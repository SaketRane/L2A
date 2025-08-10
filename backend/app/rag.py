import os
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from FlagEmbedding import FlagReranker
import faiss
import numpy as np
from transformers import AutoTokenizer
import fitz
import google.generativeai as genai
from typing import Tuple, List, Dict
import json
from dotenv import load_dotenv
import nltk
import hashlib
import re
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
from nltk.tokenize import sent_tokenize

class RAGEngine:
    def __init__(self):
        print("\n🚀 Initializing RAG Engine...")
        load_dotenv()
        
        # Use BGE-large-en-v1.5 for both embedding and tokenization
        model_name = "BAAI/bge-large-en-v1.5"
        try:
            self.embedder = SentenceTransformer(model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            print(f"✅ Loaded embedding model: {model_name}")
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model: {str(e)}")
        
        # Initialize reranker
        try:
            print("🔄 Loading BGE reranker...")
            self.reranker = FlagReranker('BAAI/bge-reranker-large', use_fp16=True)
            print("✅ Loaded BGE reranker")
        except Exception as e:
            raise RuntimeError(f"Failed to load reranker: {str(e)}")
        
        self.index = None
        self.chunks = []
        self.model = None
        self._setup_gemini()
        print("📚 Checking for existing processed data...")
        self._load_existing_index()
        print("✅ RAG Engine initialization complete\n")
    
    def _setup_gemini(self):
        """Configure the Gemini model."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
        try:
            self.model_name = "gemini-2.0-flash"
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini model: {str(e)}")
    
    def _load_pdf_text(self, path: str) -> Tuple[str, List[int]]:
        """Load and parse PDF text, returning text and page mapping."""
        try:
            doc = fitz.open(path)
            pages_text = []
            page_numbers = []
            
            for page_num, page in enumerate(doc, 1):
                page_text = page.get_text()
                pages_text.append(page_text)
                # Track which page each character belongs to
                page_numbers.extend([page_num] * len(page_text))
                # Add page break markers for easier tracking
                if page_num < len(doc):
                    pages_text.append(f"\n\n--- PAGE {page_num} END ---\n\n")
                    page_numbers.extend([page_num] * len(f"\n\n--- PAGE {page_num} END ---\n\n"))
            
            text = "".join(pages_text)
            print(f"✅ Loaded with PyMuPDF: {len(doc)} pages.")
            return text, page_numbers
        except Exception as e:
            print(f"⚠️ PyMuPDF failed ({e}), falling back to PyPDF2...")
            reader = PdfReader(path)
            pages_text = []
            page_numbers = []
            
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text() or ""
                pages_text.append(page_text)
                # Track which page each character belongs to
                page_numbers.extend([page_num] * len(page_text))
                # Add page break markers for easier tracking
                if page_num < len(reader.pages):
                    pages_text.append(f"\n\n--- PAGE {page_num} END ---\n\n")
                    page_numbers.extend([page_num] * len(f"\n\n--- PAGE {page_num} END ---\n\n"))
            
            text = "".join(pages_text)
            print(f"✅ Loaded with PyPDF2: {len(reader.pages)} pages.")
            return text, page_numbers

    def _chunk_text_with_pages(self, text: str, page_numbers: List[int], max_tokens: int = 200, overlap_ratio: float = 0.2) -> List[Dict]:
        """Semantically chunk text into overlapping segments with page tracking."""
        try:
            sentences = sent_tokenize(text)
            chunks = []
            current_chunk = []
            current_token_count = 0
            token_buffer = []
            overlap_tokens = int(overlap_ratio * max_tokens)
            current_char_pos = 0
            chunk_pages = set()

            for sentence in sentences:
                tokens = self.tokenizer.encode(sentence, add_special_tokens=False)
                token_len = len(tokens)
                
                # Find which pages this sentence spans
                sentence_start = text.find(sentence, current_char_pos)
                sentence_end = sentence_start + len(sentence)
                sentence_pages = set()
                
                if sentence_start != -1:
                    for pos in range(sentence_start, min(sentence_end, len(page_numbers))):
                        sentence_pages.add(page_numbers[pos])
                    current_char_pos = sentence_end
                
                chunk_pages.update(sentence_pages)

                if current_token_count + token_len <= max_tokens:
                    current_chunk.append(sentence)
                    token_buffer.extend(tokens)
                    current_token_count += token_len
                else:
                    if current_chunk:  # Only add non-empty chunks
                        chunk_text = " ".join(current_chunk).strip()
                        # Remove page markers from final text but keep page info
                        clean_text = chunk_text
                        for page_num in sorted(chunk_pages):
                            clean_text = clean_text.replace(f"--- PAGE {page_num} END ---", "")
                        clean_text = clean_text.strip()
                        
                        if clean_text:  # Only add non-empty chunks
                            chunks.append({
                                'text': clean_text,
                                'pages': sorted(list(chunk_pages))
                            })

                    if overlap_tokens > 0 and token_buffer:
                        overlap_tokens_ids = token_buffer[-overlap_tokens:]
                        overlap_text = self.tokenizer.decode(overlap_tokens_ids, clean_up_tokenization_spaces=True)
                        current_chunk = [overlap_text]
                        token_buffer = self.tokenizer.encode(overlap_text, add_special_tokens=False)
                        current_token_count = len(token_buffer)
                        # Keep some page info for overlap
                        chunk_pages = sentence_pages.copy()
                    else:
                        current_chunk = []
                        token_buffer = []
                        current_token_count = 0
                        chunk_pages = set()

                    if token_len <= max_tokens:
                        current_chunk.append(sentence)
                        token_buffer.extend(tokens)
                        current_token_count += token_len
                        chunk_pages.update(sentence_pages)
                    else:
                        # Split very long sentences into smaller chunks
                        for i in range(0, token_len, max_tokens):
                            sub_tokens = tokens[i:i + max_tokens]
                            sub_chunk = self.tokenizer.decode(sub_tokens, clean_up_tokenization_spaces=True)
                            if sub_chunk.strip():  # Only add non-empty chunks
                                chunks.append({
                                    'text': sub_chunk.strip(),
                                    'pages': sorted(list(sentence_pages))
                                })
                        current_chunk = []
                        token_buffer = []
                        current_token_count = 0
                        chunk_pages = set()

            if current_chunk:
                chunk_text = " ".join(current_chunk).strip()
                # Remove page markers from final text but keep page info
                clean_text = chunk_text
                for page_num in sorted(chunk_pages):
                    clean_text = clean_text.replace(f"--- PAGE {page_num} END ---", "")
                clean_text = clean_text.strip()
                
                if clean_text:  # Only add non-empty chunks
                    chunks.append({
                        'text': clean_text,
                        'pages': sorted(list(chunk_pages))
                    })

            return chunks
        except Exception as e:
            raise RuntimeError(f"Failed to chunk text: {str(e)}")
    
    def _load_existing_index(self):
        """Load existing index and chunks if they exist."""
        try:
            index_path = "large_context_index.faiss"
            chunks_path = "chunks.json"
            
            if os.path.exists(index_path) and os.path.exists(chunks_path):
                print("📚 Found existing index and chunks files")
                self.index = faiss.read_index(index_path)
                with open(chunks_path, 'r') as f:
                    self.chunks = json.load(f)
                print(f"✅ Loaded existing index with {self.index.ntotal} vectors and {len(self.chunks)} chunks")
                return True
            else:
                print("⚠️ No existing index found")
                return False
        except Exception as e:
            print(f"⚠️ Error loading existing index: {str(e)}")
            return False
    
    def _build_index(self, chunks: List[Dict], progress_callback=None):
        """Build FAISS index from chunks with page metadata."""
        try:
            # Extract text for embedding while preserving metadata
            chunk_texts = []
            safe_chunks = []
            
            for chunk_data in chunks:
                chunk_text = chunk_data['text']
                # Additional safety check: truncate any chunks that are still too long
                # Since we're using BGE-large-en-v1.5 with max_tokens=300, be more conservative
                # Roughly 4 characters per token for English text
                max_chars = 1200  # Conservative estimate for 300 tokens
                if len(chunk_text) > max_chars:
                    # Truncate to safe length
                    truncated = chunk_text[:max_chars]
                    # Try to end at a sentence boundary
                    last_period = truncated.rfind('.')
                    if last_period > 800:  # Only truncate at sentence if we have enough content
                        truncated = truncated[:last_period + 1]
                    chunk_texts.append(truncated)
                    # Update the chunk data with truncated text for embedding but keep original for storage
                    safe_chunks.append({
                        'text': chunk_data['text'],  # Keep original text
                        'pages': chunk_data['pages'],
                        'embedding_text': truncated  # Track what was used for embedding
                    })
                else:
                    chunk_texts.append(chunk_text)
                    safe_chunks.append({
                        'text': chunk_text,
                        'pages': chunk_data['pages'],
                        'embedding_text': chunk_text
                    })
            
            print(f"🔍 Processing {len(chunk_texts)} chunks for embedding...")
            
            # Process chunks in batches to show progress
            batch_size = 32  # Adjust based on your memory constraints
            all_embeddings = []
            total_chunks = len(chunk_texts)
            
            for i in range(0, total_chunks, batch_size):
                batch_texts = chunk_texts[i:i + batch_size]
                batch_embeddings = self.embedder.encode(batch_texts, convert_to_numpy=True, show_progress_bar=False)
                all_embeddings.append(batch_embeddings)
                
                # Update progress
                processed = min(i + batch_size, total_chunks)
                progress = 85 + int((processed / total_chunks) * 10)  # Progress from 85% to 95%
                if progress_callback:
                    progress_callback(progress, f"🧠 Processing batch {i//batch_size + 1}/{(total_chunks + batch_size - 1)//batch_size}...")
                
                print(f"✅ Processed batch {i//batch_size + 1}/{(total_chunks + batch_size - 1)//batch_size}")
            
            # Combine all embeddings
            embeddings = all_embeddings[0] if len(all_embeddings) == 1 else None
            if embeddings is None:
                embeddings = np.vstack(all_embeddings)
            
            embeddings = embeddings.astype('float32')
            
            if embeddings.ndim == 1:
                embeddings = embeddings.reshape(1, -1)
            
            faiss.normalize_L2(embeddings)
            
            d = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(d)
            self.index.add(embeddings)
            
            # Save both index and chunks with page metadata
            faiss.write_index(self.index, "large_context_index.faiss")
            with open("chunks.json", 'w') as f:
                json.dump(safe_chunks, f)  # Save chunks with page metadata
            print("✅ FAISS index and chunks saved")
        except Exception as e:
            raise RuntimeError(f"Failed to build FAISS index: {str(e)}")
    
    def _get_pdf_hash(self, pdf_path: str) -> str:
        """Generate a hash for the PDF file."""
        with open(pdf_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _check_existing_processing(self, pdf_path: str) -> bool:
        """Check if this PDF has already been processed."""
        try:
            pdf_hash = self._get_pdf_hash(pdf_path)
            hash_path = "pdf_hash.txt"
            
            if os.path.exists(hash_path):
                with open(hash_path, 'r') as f:
                    stored_hash = f.read().strip()
                print(f"🔍 Comparing PDF hashes - Current: {pdf_hash}, Stored: {stored_hash}")
                if stored_hash == pdf_hash:
                    print("✅ Found existing processing for this PDF")
                    return True
            print("⚠️ No matching hash found")
            return False
        except Exception as e:
            print(f"⚠️ Error checking existing processing: {str(e)}")
            return False
    
    def process_pdf(self, pdf_path: str, progress_callback=None):
        """Process PDF and build the RAG index."""
        try:
            # Check if this PDF has already been processed
            if self._check_existing_processing(pdf_path):
                print("🔄 Loading existing index and chunks...")
                if self._load_existing_index():
                    print("✅ Successfully loaded existing index and chunks")
                    return
                else:
                    print("⚠️ Failed to load existing index, will process PDF again")
            
            print("📄 Processing new PDF...")
            # Load and parse PDF with page tracking
            text, page_numbers = self._load_pdf_text(pdf_path)
            
            # Chunk the text with page metadata
            self.chunks = self._chunk_text_with_pages(text, page_numbers)
            print(f"🔖 Split into {len(self.chunks)} chunks with page metadata")
            
            # Build the index with progress callback
            self._build_index(self.chunks, progress_callback)
            print("✅ FAISS index built successfully")
            
            # Save the PDF hash
            pdf_hash = self._get_pdf_hash(pdf_path)
            with open("pdf_hash.txt", 'w') as f:
                f.write(pdf_hash)
            print(f"💾 Saved PDF hash: {pdf_hash}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to process PDF: {str(e)}")

    def _refine_question(self, question: str, history: list) -> str:
        """Refine the user's question using retrieved context to guide reformulation."""
        try:
            print(f"🔍 Starting question refinement for: {question[:100]}...")
            
            # Step 1: Take the raw user query and do a rough retrieval (truncate if too long)
            query_text = question
            if len(query_text) > 1200:  # Safety truncation for BGE-large-en-v1.5
                query_text = query_text[:1200]
            q_emb = self.embedder.encode([query_text], convert_to_numpy=True)
            
            # Step 2: Run rough retrieval to get top-k contexts (even with vague query)
            k_rough = 3  # Get top 3 hits for reformulation
            D, I = self.index.search(q_emb, k_rough)
            
            # Step 3: Gather the retrieved contexts
            rough_contexts = []
            for idx in I[0]:
                if idx < len(self.chunks):  # Safety check
                    chunk_data = self.chunks[idx]
                    # Handle both old format (strings) and new format (dicts)
                    chunk_text = chunk_data if isinstance(chunk_data, str) else chunk_data['text']
                    rough_contexts.append(chunk_text)
            
            # Combine contexts for reformulation
            combined_context = "\n\n".join(rough_contexts)
            
            # Format history using the same logic as in _generate_answer
            history_str = ""
            print(f"🔍 Processing history with {len(history)} messages")

            # Only keep the last 6 messages (3 exchanges) to prevent prompt from becoming too large
            recent_history = history[-6:] if len(history) > 6 else history

            for i, msg in enumerate(recent_history):
                print(f"🔍 Message {i}: type={type(msg)}, hasattr role={hasattr(msg, 'role') if hasattr(msg, '__dict__') else 'N/A'}")
                try:
                    # For Pydantic Message objects, access attributes directly
                    role = msg.role
                    content = msg.content
                    
                    # Truncate very long messages to prevent prompt bloat
                    if len(content) > 3000:
                        content = content[:3000] + "... [truncated]"

                    print(f"✅ Successfully accessed message {i}: role={role}, content length={len(content)}")
                    
                    if role == 'user':
                        history_str += f"User: {content}\n"
                    elif role == 'assistant':
                        history_str += f"Assistant: {content}\n"
                except AttributeError as e:
                    # If it's a dict format, handle it differently
                    print(f"⚠️ Warning: Unexpected message format: {type(msg)}, {e}")
                    if isinstance(msg, dict):
                        role = msg.get('role', '')
                        content = msg.get('content', '')
                        if role == 'user':
                            history_str += f"User: {content}\n"
                        elif role == 'assistant':
                            history_str += f"Assistant: {content}\n"
                    continue
            if history_str:
                history_str = f"Previous conversation:\n{history_str}\n"
            
            # Step 4: Feed both raw query and retrieved contexts to LLM for reformulation
            prompt = (
                "You are an expert at query reformulation. Your task is to take a raw user question and rewrite it to be more specific and effective for retrieving relevant information from a technical document.\n\n"
                "Instructions:\n"
                "1. Use the retrieved content below to understand the domain, terminology, and style\n"
                "2. Rewrite the user's question using the technical language and concepts from the retrieved content\n"
                "3. Keep the core intent of the original question\n"
                "4. Try to assume as little as possible about the user's knowledge level and what he is asking, but aim for clarity and precision\n"
                "5. Do NOT answer the question or mention specific parts of the text - only reformulate it for better retrieval\n"
                "6. If the user is asking for a derivation or proof, reformulate the query to all the relevant steps and concepts involved\n"
                "7. If the user is asking for a definition or explanation, provide an informative reformulation\n\n"
                f"Retrieved content (for context and terminology):\n{combined_context}\n\n"
                f"Past conversation history for context:\n{history_str}\n\n"
                f"Original user question: \"{question}\"\n\n"
                "Reformulated question:"
            )
            
            print(f"🤖 Calling Gemini for question refinement...")
            response = self.model.generate_content(prompt)
            if not response or not response.text:
                print("⚠️ Warning: Failed to refine question, using original.")
                return question
            
            refined_question = response.text.strip()
            # Clean up quotes if present
            if refined_question.startswith('"') and refined_question.endswith('"'):
                refined_question = refined_question[1:-1]
            
            print(f"🔍 Original: {question}")
            print(f"🎯 Refined: {refined_question}")
            
            return refined_question
            
        except Exception as e:
            print(f"⚠️ Warning: Error during question refinement: {str(e)}. Using original question.")
            return question

    def _post_process_latex(self, text: str) -> str:
        """Minimal post-processing to clean up text without interfering with LaTeX."""
        # Just clean up any obvious issues without heavy LaTeX manipulation
        # The frontend AlternativeLatexRenderer already handles LaTeX properly
        
        # Fix any double-escaped backslashes that might cause issues
        text = re.sub(r'\\\\([a-zA-Z]+)', r'\\\1', text)
        
        return text

    def _rerank_chunks(self, query: str, chunk_indices: List[int], top_k: int = None) -> List[int]:
        """
        Rerank retrieved chunks using FlagReranker for better relevance.
        
        Args:
            query: The search query
            chunk_indices: List of chunk indices to rerank
            top_k: Number of top chunks to return (if None, returns all reranked)
        
        Returns:
            List of reranked chunk indices
        """
        if not chunk_indices:
            return chunk_indices
            
        print(f"🔄 Reranking {len(chunk_indices)} chunks using BGE FlagReranker...")
        
        # Prepare query-chunk pairs for FlagReranker
        passages = []
        valid_indices = []
        
        for idx in chunk_indices:
            if idx < len(self.chunks):
                chunk_data = self.chunks[idx]
                # Handle both old format (strings) and new format (dicts)
                chunk_text = chunk_data if isinstance(chunk_data, str) else chunk_data['text']
                
                # Truncate very long chunks for efficient reranking
                if len(chunk_text) > 1000:
                    chunk_text = chunk_text[:1000] + "..."
                
                passages.append(chunk_text)
                valid_indices.append(idx)
        
        if not passages:
            return chunk_indices
        
        # Get reranking scores using FlagReranker
        scores = self.reranker.compute_score([[query, passage] for passage in passages])
        
        # Handle both single score and list of scores
        if not isinstance(scores, list):
            scores = [scores]
        
        # Sort indices by scores (descending)
        scored_indices = list(zip(valid_indices, scores))
        scored_indices.sort(key=lambda x: x[1], reverse=True)
        
        # Extract reranked indices
        reranked_indices = [idx for idx, score in scored_indices]
        
        # Return top_k if specified
        if top_k and top_k < len(reranked_indices):
            reranked_indices = reranked_indices[:top_k]
        
        print(f"✅ Reranking complete. Top scores: {[f'{score:.3f}' for _, score in scored_indices[:5]]}")
        return reranked_indices

    def _get_contexts(self, refined_question: str, k: int = 10, window_size: int = 5):
        """Get relevant contexts from the vector database with reranking."""
        print(f"🔍 Getting contexts for refined question: {refined_question[:100]}...")
        
        # Embed the refined question (truncate if too long)
        query_text = refined_question
        if len(query_text) > 1200:  # Safety truncation for long queries with BGE-large-en-v1.5
            query_text = query_text[:1200]
        
        print(f"🔮 Encoding query for embedding search...")
        q_emb = self.embedder.encode([query_text], convert_to_numpy=True)
        
        # Search FAISS for more chunks initially (for reranking)
        initial_k = min(k * 3, 30)  # Get 3x more chunks for reranking, but cap at 50
        print(f"🔍 Searching FAISS index for top {initial_k} chunks for reranking...")
        D, I = self.index.search(q_emb, initial_k)
        
        # Rerank the retrieved chunks to improve relevance
        initial_indices = I[0].tolist()
        reranked_indices = self._rerank_chunks(query_text, initial_indices, top_k=k)
        
        # Gather context using a window around each reranked chunk
        window_indices = set()
        for idx in reranked_indices:
            start = max(0, idx - window_size)
            end = min(len(self.chunks), idx + window_size + 1)
            for i in range(start, end):
                window_indices.add(i)
        
        # Sort indices to maintain original order of chunks
        sorted_indices = sorted(list(window_indices))
        
        # Gather contexts and track pages
        contexts = []
        all_pages_used = set()
        
        for idx in sorted_indices:
            chunk_data = self.chunks[idx]
            # Handle both old format (strings) and new format (dicts)
            if isinstance(chunk_data, str):
                contexts.append(chunk_data)
            else:
                contexts.append(chunk_data['text'])
                all_pages_used.update(chunk_data['pages'])
        
        print(f"✅ Retrieved {len(contexts)} context chunks from pages: {sorted(list(all_pages_used))}")
        return contexts, window_indices, sorted(list(all_pages_used))

    def _generate_answer(self, original_question: str, refined_question: str, contexts: list, history: list, pages_used: list = None):
        """Generate the final answer using the LLM."""
        print(f"✨ Generating answer for question: {original_question[:100]}...")
        if pages_used:
            print(f"📄 Using content from pages: {pages_used}")

        # Build the conversation history string (limit to last 6 exchanges to prevent prompt bloat)
        history_str = ""
        print(f"🔍 Processing history with {len(history)} messages")

        # Only keep the last 6 messages (3 exchanges) to prevent prompt from becoming too large
        recent_history = history[-6:] if len(history) > 6 else history

        for i, msg in enumerate(recent_history):
            print(f"🔍 Message {i}: type={type(msg)}, hasattr role={hasattr(msg, 'role') if hasattr(msg, '__dict__') else 'N/A'}")
            try:
                # For Pydantic Message objects, access attributes directly
                role = msg.role
                content = msg.content
                
                # Truncate very long messages to prevent prompt bloat
                if len(content) > 3000:
                    content = content[:3000] + "... [truncated]"

                print(f"✅ Successfully accessed message {i}: role={role}, content length={len(content)}")
                
                if role == 'user':
                    history_str += f"User: {content}\n"
                elif role == 'assistant':
                    history_str += f"Assistant: {content}\n"
            except AttributeError as e:
                # If it's a dict format, handle it differently
                print(f"⚠️ Warning: Unexpected message format: {type(msg)}, {e}")
                if isinstance(msg, dict):
                    role = msg.get('role', '')
                    content = msg.get('content', '')
                    if role == 'user':
                        history_str += f"User: {content}\n"
                    elif role == 'assistant':
                        history_str += f"Assistant: {content}\n"
                continue
        if history_str:
            history_str = f"Previous conversation:\n{history_str}\n"
            
        # Build the prompt
        context = "\n\n".join(contexts)
        
        history_length = len(history_str)
        question_length = len(refined_question)
        
        # Build source pages string separately to avoid f-string backslash issue
        source_pages_str = "**Source Pages:** " + ", ".join(map(str, pages_used)) + "\n\n" if pages_used else ""

        prompt = (
            f"You are a helpful assistant and a good teacher trying to explain concepts to someone new to the subject. Use the following context along with your abilities and knowledge to answer the question and explain the concepts clearly. Format your response according to these rules:\n\n"
            "FORMATTING GUIDELINES:\n"
            "1. **Structure**: Organize your answer with clear sections using ## for main topics (e.g., ## Wave-Particle Duality)\n"
            "2. **Key Concepts**: Present important concepts as **bold statements** without bullet points, followed by explanatory paragraphs\n"
            "3. **Mathematical Expressions**: CRITICAL - ALL math must be wrapped in LaTeX delimiters:\n"
            "   - Use $...$ for inline math: $\\psi(x,t)$, $E=mc^2$, $\\hbar$, $\\partial$, $\\alpha$, etc.\n"
            "   - Use $$...$$ for block equations: $$\\frac{\\partial \\Psi}{\\partial t} = \\hat{H}\\Psi$$\n"
            "   - Every mathematical symbol must be wrapped: $\\psi$, $\\Psi$, $\\phi$, $\\hbar$, $\\partial$, $\\alpha$, etc.\n"
            "4. **Minimal Bullets**: Use bullet points (- ) ONLY for lists of 3+ related items, not for main explanations\n"
            "5. **Flow**: Write in flowing paragraphs rather than choppy bullet points\n"
            "6. **Examples**: Use clear examples to illustrate concepts\n\n"
            "ANSWER STRUCTURE:\n"
            "- Start with a brief conceptual overview\n"
            "- Organize into logical sections with ## headers\n"
            "- Use **bold** for key terms and concepts\n"
            "- Provide step-by-step derivations when needed\n"
            "- Explain concepts in a way that builds understanding, using analogies and physical interpretations where appropriate\n"
            "- Include practical applications or limitations\n\n"
            "EXAMPLE FORMAT:\n"
            "## Wave-Particle Duality\n"
            "**Quantum objects exhibit both wave and particle properties.** This fundamental principle means that particles like electrons can show interference patterns (wave behavior) while also having discrete, localized impacts (particle behavior).\n\n"
            "The **de Broglie wavelength** $\\lambda = \\frac{h}{p}$ relates a particle's momentum $p$ to its wavelength $\\lambda$, where $h$ is Planck's constant. This relationship shows that all matter has an associated wavelength.\n\n"
            f"Past conversation:\n{history_str} \n\n Context:\n{context}\n\n"
            f"Source pages:\n{source_pages_str}\n\n"
            f"Question: {refined_question}\n\n"
            "Answer:\n"
        )

        print(f"📊 Prompt stats - Total: {len(prompt)} chars, History: {history_length}, Context: {len(context)}, Question: {question_length}")
        print(f"🤖 Calling Gemini for answer generation...")
        
        # Generate the answer with timeout protection
        try:
            start_time = time.time()
            
            # Use a thread executor with timeout for the Gemini call
            with ThreadPoolExecutor() as executor:
                future = executor.submit(self.model.generate_content, prompt)
                try:
                    response = future.result(timeout=40)  # 40 second timeout
                except FuturesTimeoutError:
                    future.cancel()
                    raise TimeoutError("Gemini API call timed out after 40 seconds")

            end_time = time.time()
            print(f"⏱️ Gemini call took {end_time - start_time:.2f} seconds")
            
            if not response or not response.text:
                raise RuntimeError(f"Failed to generate response from {self.model_name} model")
                
        except Exception as e:
            print(f"❌ Gemini API error: {str(e)}")
            # Return a fallback response instead of crashing
            return f"I apologize, but I encountered an issue generating a response. This might be due to the conversation becoming too long or a timeout. Please try asking your question again, and I'll do my best to help. Error details: {str(e)}"
        
        # Clean up excessive spacing in the response
        answer = response.text.strip()
        
        # Post-process to ensure LaTeX expressions are properly wrapped
        answer = self._post_process_latex(answer)
        
        # Add page reference information if available
        pages_used = pages_used[:10] if pages_used else []
        if pages_used:
            page_info = f"\n\n---\n**📄 Source Pages:** {', '.join(map(str, pages_used))}"
            answer += page_info
        
        print(f"✅ Generated answer with {len(answer)} characters")
        return answer

    def answer_question(self, question: str, k: int = 10, window_size: int = 5, history: list = None) -> str:
        """Answer a question using the RAG pipeline with a sentence window and conversation history."""
        if not self.index or not self.chunks:
            raise ValueError("No PDF has been processed yet. Please upload a PDF first.")
        if history is None:
            history = []
        try:
            # Step 1: Refine the question for better retrieval
            refined_question = self._refine_question(question, history)
            
            # Step 2: Get relevant contexts
            contexts, window_indices, pages_used = self._get_contexts(refined_question, k, window_size)
            
            # Step 3: Generate the answer
            print(f"🔍 Generating answer for question")
            answer = self._generate_answer(question, refined_question, contexts, history, pages_used)
            
            return answer
        except Exception as e:
            raise RuntimeError(f"Failed to answer question: {str(e)}")

