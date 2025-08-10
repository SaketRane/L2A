from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
from typing import List
import json
import asyncio
import traceback
import logging
import threading
from .rag import RAGEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Scriptoria RAG API", 
    version="1.0.0",
    description="AI-powered textbook Q&A system with RAG"
)

# Configure CORS with environment variables
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
cors_origins = [origin.strip() for origin in cors_origins]  # Clean whitespace

# Production CORS settings
allow_origins = cors_origins if os.getenv("ENVIRONMENT") == "production" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialize RAG engine
rag_engine = RAGEngine()

class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class Question(BaseModel):
    question: str
    history: List[Message] = []

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Basic health checks
        health_status = {
            "status": "healthy", 
            "service": "Scriptoria RAG API",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "rag_engine_initialized": rag_engine is not None
        }
        
        # Check if uploads directory exists
        health_status["uploads_dir_exists"] = os.path.exists("uploads")
        
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/upload-stream")
async def upload_pdf_stream(file: UploadFile = File(...)):
    """Upload a PDF file with streaming progress updates."""
    
    # Validate file extension first
    if not file.filename.endswith('.pdf'):
        return StreamingResponse(
            iter([f"data: {json.dumps({'status': 'error', 'message': 'Only PDF files are allowed'})}\n\n"]),
            media_type="text/plain"
        )
    
    # Read file content immediately to avoid stream closure issues
    try:
        file_content = await file.read()
    except Exception as e:
        return StreamingResponse(
            iter([f"data: {json.dumps({'status': 'error', 'message': f'Error reading file: {str(e)}'})}\n\n"]),
            media_type="text/plain"
        )
    
    file_path = None
    
    async def generate_progress():
        nonlocal file_path
        try:
            # Step 1: Validate file
            yield f"data: {json.dumps({'status': 'validating', 'message': '📋 Validating PDF file...', 'progress': 10})}\n\n"
            await asyncio.sleep(0.1)
            
            # Step 2: Create directory and save file
            os.makedirs("uploads", exist_ok=True)
            file_path = f"uploads/{file.filename}"
            
            yield f"data: {json.dumps({'status': 'uploading', 'message': '📤 Saving PDF file...', 'progress': 20})}\n\n"
            await asyncio.sleep(0.1)
            
            # Save file content to disk
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
            
            # Ensure file is completely written
            await asyncio.sleep(0.2)
            
            yield f"data: {json.dumps({'status': 'uploaded', 'message': '✅ File saved successfully', 'progress': 30})}\n\n"
            await asyncio.sleep(0.1)
            
            # Step 3: Process PDF with progress updates
            yield f"data: {json.dumps({'status': 'processing', 'message': '📄 Extracting text from PDF...', 'progress': 40})}\n\n"
            await asyncio.sleep(0.1)
            
            # Step 4: Text extraction
            yield f"data: {json.dumps({'status': 'extracting', 'message': '📖 Reading PDF pages...', 'progress': 50})}\n\n"
            await asyncio.sleep(0.1)
            
            # Step 5: Chunking
            yield f"data: {json.dumps({'status': 'chunking', 'message': '✂️ Breaking text into chunks...', 'progress': 60})}\n\n"
            await asyncio.sleep(0.1)
            
            # Step 6: Embedding
            yield f"data: {json.dumps({'status': 'embedding', 'message': '🧠 Generating embeddings...', 'progress': 70})}\n\n"
            await asyncio.sleep(0.1)
            
            # Step 7: Building index
            yield f"data: {json.dumps({'status': 'indexing', 'message': '🏗️ Building search index...', 'progress': 85})}\n\n"
            await asyncio.sleep(0.1)
            
            # Create a progress callback to relay batch processing progress
            def progress_callback(progress, message):
                # This will be called synchronously from the RAG engine
                # We need to store the progress to be yielded in the async generator
                progress_callback.last_progress = progress
                progress_callback.last_message = message
            
            progress_callback.last_progress = 85
            progress_callback.last_message = '🏗️ Building search index...'
            
            # Actually process the PDF
            try:
                # Process PDF with progress callback
                # Run PDF processing in a separate thread
                processing_complete = threading.Event()
                processing_error = None
                
                def process_pdf_thread():
                    nonlocal processing_error
                    try:
                        rag_engine.process_pdf(file_path, progress_callback)
                    except Exception as e:
                        processing_error = e
                    finally:
                        processing_complete.set()
                
                # Start processing thread
                thread = threading.Thread(target=process_pdf_thread)
                thread.start()
                
                # Monitor progress and yield updates
                last_yielded_progress = 85
                while not processing_complete.is_set():
                    await asyncio.sleep(0.5)  # Check every 500ms
                    
                    # Check if progress has changed
                    current_progress = getattr(progress_callback, 'last_progress', 85)
                    current_message = getattr(progress_callback, 'last_message', '🏗️ Building search index...')
                    
                    if current_progress > last_yielded_progress:
                        yield f"data: {json.dumps({'status': 'indexing', 'message': current_message, 'progress': current_progress})}\n\n"
                        last_yielded_progress = current_progress
                
                # Wait for thread to complete
                thread.join()
                
                # Check if there was an error
                if processing_error:
                    raise processing_error
                
                # Step 8: Saving
                yield f"data: {json.dumps({'status': 'saving', 'message': '💾 Saving index to disk...', 'progress': 95})}\n\n"
                await asyncio.sleep(0.1)
                
                # Step 9: Complete
                yield f"data: {json.dumps({'status': 'complete', 'message': '🎉 PDF processed successfully!', 'progress': 100, 'filename': file.filename})}\n\n"
                
            except Exception as pdf_error:
                error_msg = f"Failed to process PDF content. Please ensure the PDF is not corrupted or password-protected."
                logger.error(f"PDF Processing Error: {str(pdf_error)}")
                logger.error(traceback.format_exc())
                yield f"data: {json.dumps({'status': 'error', 'message': error_msg})}\n\n"
                return
            
        except Exception as e:
            error_msg = "An unexpected error occurred during upload. Please try again."
            logger.error(f"Upload Error: {str(e)}")
            logger.error(traceback.format_exc())
            yield f"data: {json.dumps({'status': 'error', 'message': error_msg})}\n\n"
        finally:
            # Clean up the uploaded file with a small delay
            if file_path and os.path.exists(file_path):
                try:
                    await asyncio.sleep(0.5)  # Give time for any lingering file operations
                    os.remove(file_path)
                    print(f"🗑️ Cleaned up temporary file: {file_path}")
                except Exception as cleanup_error:
                    print(f"⚠️ Warning: Could not clean up file {file_path}: {cleanup_error}")
    
    return StreamingResponse(
        generate_progress(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@app.post("/ask")
async def ask_question(question: Question):
    """Ask a question and get an answer with citations."""
    print(f"Received question: {question.question}")  # Debug log
    
    if not question.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )
    
    try:
        answer = rag_engine.answer_question(question.question, history=question.history)
        return {
            "answer": answer
        }
    except ValueError as e:
        # Handle specific error for when no PDF is processed
        print(f"ValueError: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        error_msg = f"Error answering question: {str(e)}"
        print(f"Error: {error_msg}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )

@app.post("/ask-stream")
async def ask_question_stream(question: Question):
    """Ask a question and get streaming progress updates."""
    print(f"Received streaming question: {question.question}")
    
    if not question.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    async def generate_progress():
        try:
            # Step 1: Processing question
            progress_data = {
                'status': 'processing_question', 
                'message': '🤔 Processing your question...'
            }
            yield f"data: {json.dumps(progress_data)}\n\n"
            await asyncio.sleep(0.1)  # Small delay for UI update
            
            # Step 2: Refining question
            progress_data = {
                'status': 'refining_question', 
                'message': '🎯 Refining question for better retrieval...'
            }
            yield f"data: {json.dumps(progress_data)}\n\n"
            await asyncio.sleep(0.2)  # Allow UI to update
            refined_question = rag_engine._refine_question(question.question, question.history or [])
            
            # Step 3: Retrieving chunks
            progress_data = {
                'status': 'retrieving_chunks', 
                'message': '🔍 Searching knowledge base...'
            }
            yield f"data: {json.dumps(progress_data)}\n\n"
            await asyncio.sleep(0.2)  # Allow UI to update
            contexts, window_indices, pages_used = rag_engine._get_contexts(refined_question, k=20, window_size=5)
            
            # Step 4: Processing chunks
            progress_data = {
                'status': 'processing_chunks', 
                'message': f'📚 Processing {len(contexts)} relevant passages from pages {", ".join(map(str, pages_used)) if pages_used else "N/A"}...'
            }
            yield f"data: {json.dumps(progress_data)}\n\n"
            await asyncio.sleep(0.3)  # Longer delay for this step
            
            # Step 5: Generating answer
            progress_data = {
                'status': 'generating_answer', 
                'message': '✨ Generating your answer...'
            }
            yield f"data: {json.dumps(progress_data)}\n\n"
            await asyncio.sleep(0.2)  # Allow UI to update
            answer = rag_engine._generate_answer(question.question, refined_question, contexts, question.history or [], pages_used)
            
            # Step 6: Complete
            final_data = {
                'status': 'complete', 
                'answer': answer
            }
            yield f"data: {json.dumps(final_data)}\n\n"
            
        except ValueError as e:
            # Handle specific error for when no PDF is processed
            error_data = {
                'status': 'error', 
                'message': str(e)
            }
            yield f"data: {json.dumps(error_data)}\n\n"
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"Streaming error: {error_msg}")
            print(traceback.format_exc())
            error_data = {
                'status': 'error', 
                'message': error_msg
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        generate_progress(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )