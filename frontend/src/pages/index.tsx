import { useState, useRef, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { ClipLoader } from 'react-spinners';
import AlternativeLatexRenderer from '../components/AlternativeLatexRenderer';

// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState('');
  const [uploadMessage, setUploadMessage] = useState('');
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pdfUploaded, setPdfUploaded] = useState(false);
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; content: string }[]>([]);
  const [progressStatus, setProgressStatus] = useState('');
  const [progressMessage, setProgressMessage] = useState('');
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom on new message
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    onDrop: acceptedFiles => {
      setFile(acceptedFiles[0]);
      setError('');
      setPdfUploaded(false);
    }
  });

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError('');
    setPdfUploaded(false);
    setUploadProgress(0);
    setUploadStatus('');
    setUploadMessage('');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      if (process.env.NODE_ENV === 'development') {
        console.log('Uploading to:', `${API_BASE_URL}/upload-stream`);
      }
      
      const response = await fetch(`${API_BASE_URL}/upload-stream`, {
        method: 'POST',
        body: formData,
      });

      if (!response.body) {
        throw new Error('No response body');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (process.env.NODE_ENV === 'development') {
                console.log('Upload progress:', data);
              }
              
              setUploadStatus(data.status);
              setUploadMessage(data.message || '');
              setUploadProgress(data.progress || 0);
              
              if (data.status === 'complete') {
                setPdfUploaded(true);
                setMessages([]);
                setUploading(false);
                return;
              } else if (data.status === 'error') {
                throw new Error(data.message);
              }
            } catch (parseError) {
              console.error('Error parsing SSE data:', parseError);
            }
          }
        }
      }
    } catch (err) {
      console.error('Upload error:', err);
      setError('Error uploading file. Please try again.');
      setUploading(false);
      setPdfUploaded(false);
      setUploadProgress(0);
      setUploadStatus('');
      setUploadMessage('');
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError('');
    setProgressStatus('');
    setProgressMessage('');
    
    const newMessages = [...messages, { role: 'user' as const, content: question.trim() }];
    setMessages(newMessages);
    const currentQuestion = question.trim();
    setQuestion('');

    try {
      // Map messages to ensure role is 'user' | 'assistant' for backend
      const history = newMessages.slice(0, -1).map(m => ({ role: m.role, content: m.content }));
      
      const response = await fetch(`${API_BASE_URL}/ask-stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: currentQuestion,
          history
        })
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(errorData || 'Failed to get response');
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let finalAnswer = '';
      let buffer = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          // Add new chunk to buffer
          buffer += decoder.decode(value, { stream: true });
          
          // Process complete lines
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const jsonStr = line.substring(6).trim();
                if (jsonStr) {
                  const data = JSON.parse(jsonStr);
                  
                  if (data.status === 'complete') {
                    finalAnswer = data.answer;
                    setProgressStatus('');
                    setProgressMessage('');
                  } else if (data.status === 'error') {
                    throw new Error(data.message);
                  } else {
                    setProgressStatus(data.status);
                    setProgressMessage(data.message);
                  }
                }
              } catch (parseError) {
                console.error('Error parsing SSE data:', parseError, 'Line:', line);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }

      if (finalAnswer) {
        setMessages([...newMessages, { role: 'assistant' as const, content: finalAnswer }]);
      } else {
        throw new Error('No answer received from server');
      }
    } catch (err: any) {
      console.error('Full error:', err);
      setError(err.message || 'Error getting answer. Please try again.');
      // Remove the user's question if error
      setMessages(messages);
    } finally {
      setLoading(false);
      setProgressStatus('');
      setProgressMessage('');
    }
  };

  // Chat bubble component
  const ChatBubble = ({ role, content }: { role: 'user' | 'assistant'; content: string }) => (
    <div className={`flex ${role === 'user' ? 'justify-end' : 'justify-start'} mb-4 w-full`}>
      <div
        className={
          role === 'user'
            ? 'max-w-xl px-4 py-3 rounded-2xl shadow-lg whitespace-pre-line break-words bg-purple-600 text-white rounded-br-sm'
            : 'w-full max-w-none px-5 py-4 rounded-2xl shadow-lg bg-[#1a1a1c] text-gray-100 rounded-bl-sm border border-purple-800/50'
        }
        style={role === 'assistant' ? { maxWidth: '100%' } : {}}
      >
        <AlternativeLatexRenderer text={content} />
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white flex flex-col">
      {/* Header */}
      <div className="flex justify-center py-8">
        <div className="bg-white rounded-3xl shadow-xl px-2 py-2 flex flex-col items-center max-w-md w-full">
          <h1 className="text-5xl font-bold text-purple-600 mb-1">
            Scriptoria
          </h1>
          <p className="text-gray-600 text-lg mt-0">
            Making textbooks easy to understand
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col relative">
        {/* Upload & Question Area - Centered before upload */}
        {!pdfUploaded && (
          <div className="flex-1 flex flex-col items-center justify-center px-4 space-y-6">
            <div className="w-full max-w-md">
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-xl p-3 text-center cursor-pointer transition-all duration-300 ${
                  isDragActive 
                    ? 'border-purple-500 bg-purple-500/10' 
                    : 'border-gray-700 hover:border-purple-500 hover:bg-purple-500/5'
                }`}
              >
                <input {...getInputProps()} />
                {file ? (
                  <p className="text-purple-400">{file.name}</p>
                ) : (
                  <div className="space-y-2">
                    <p className="text-gray-400">Drag and drop a PDF file here, or click to select</p>
                    <p className="text-sm text-gray-500">Supports .pdf files</p>
                  </div>
                )}
              </div>
              {file && !pdfUploaded && (
                <div className="mt-4 w-full">
                  <button
                    onClick={handleUpload}
                    disabled={uploading}
                    className="w-full bg-purple-400 hover:bg-purple-500 text-white font-semibold py-2 px-4 rounded-xl shadow-lg transition-all duration-300 disabled:opacity-50"
                  >
                    {uploading ? <ClipLoader size={20} color="#fff" /> : 'Upload PDF'}
                  </button>
                  
                  {/* Progress Bar and Status */}
                  {uploading && (
                    <div className="mt-4 space-y-2">
                      {/* Progress Bar */}
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-purple-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${uploadProgress}%` }}
                        ></div>
                      </div>
                      
                      {/* Progress Text */}
                      <div className="text-center">
                        <p className="text-sm text-purple-400 font-medium">
                          {uploadProgress}%
                        </p>
                        {uploadMessage && (
                          <p className="text-xs text-gray-400 mt-1">
                            {uploadMessage}
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
            {/* Centered Question Bar under drop file bar */}
            <div className="w-full max-w-2xl flex items-center space-x-4 justify-center">
              <input
                type="text"
                value={question}
                onChange={e => setQuestion(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter' && !loading && question.trim() && file) {
                    handleAsk();
                  }
                }}
                placeholder="Talk to your textbook..."
                className="flex-1 bg-[#2A2A2A] text-white placeholder-gray-500 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-400"
                disabled={!file}
              />
              <button
                onClick={handleAsk}
                disabled={loading || !question.trim() || !file}
                className="bg-purple-400 hover:bg-purple-500 text-white font-semibold py-3 px-6 rounded-xl shadow-lg transition-all duration-300 disabled:opacity-50"
              >
                {loading ? <ClipLoader size={20} color="#fff" /> : 'Ask'}
              </button>
            </div>
          </div>
        )}

        {/* Chat Area - Only shown when PDF is uploaded */}
        {pdfUploaded && (
          <div className="flex-1 overflow-y-auto px-4 py-6" style={{ paddingBottom: '180px', paddingTop: '0px' }}>
            {error && (
              <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 mb-4 w-full">{error}</div>
            )}
            {messages.length === 0 && !error && (
              <div className="h-screen flex items-center justify-center text-gray-500 w-full">
                <p>Start chatting with your textbook...</p>
              </div>
            )}
            {messages.map((msg, idx) => (
              <ChatBubble key={idx} role={msg.role} content={msg.content} />
            ))}
            {loading && (
              <div className="flex justify-start mb-4">
                <div className="max-w-xl px-5 py-4 rounded-2xl shadow-lg bg-[#1a1a1c] text-gray-100 border border-purple-800/50">
                  <div className="flex items-center space-x-3">
                    <ClipLoader size={18} color="#a78bfa" />
                    <div className="flex flex-col">
                      <span className="text-purple-300 font-medium">
                        {progressMessage || 'Processing...'}
                      </span>
                      {progressStatus && (
                        <span className="text-gray-400 text-sm">
                          {progressStatus === 'processing_question' && '🤔 Analyzing your question'}
                          {progressStatus === 'refining_question' && '🔍 Optimizing search query'}
                          {progressStatus === 'retrieving_chunks' && '📚 Searching knowledge base'}
                          {progressStatus === 'processing_chunks' && '⚙️ Processing relevant content'}
                          {progressStatus === 'generating_answer' && '✨ Generating response'}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={chatBottomRef} />
          </div>
        )}

        {/* Chat Input - Fixed at bottom when PDF is uploaded */}
        {pdfUploaded && (
          <div className="fixed bottom-6 left-0 w-full flex justify-center z-50 pointer-events-none">
            <div className="bg-[#0A0A0A] rounded-2xl shadow-2xl max-w-2xl w-full px-6 py-4 flex flex-col items-center pointer-events-auto">
              <div className="w-full mb-2 flex items-center justify-between">
                <p className="text-purple-400 text-sm text-left">Currently loaded: {file?.name}</p>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => {
                      setPdfUploaded(false);
                      setFile(null);
                      setMessages([]);
                      setQuestion('');
                      setError('');
                    }}
                    className="ml-4 bg-purple-900 hover:bg-purple-700 text-white text-xs font-semibold py-1 px-3 rounded-xl shadow transition-all duration-200"
                  >
                    Change PDF
                  </button>
                  <button
                    onClick={() => {
                      setMessages([]);
                      setQuestion('');
                      setError('');
                    }}
                    className="ml-2 bg-gray-700 hover:bg-gray-600 text-white text-xs font-semibold py-1 px-3 rounded-xl shadow transition-all duration-200"
                  >
                    New Chat
                  </button>
                </div>
              </div>
              <div className="flex items-center w-full space-x-4">
                <input
                  type="text"
                  value={question}
                  onChange={e => setQuestion(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' && !loading && question.trim() && pdfUploaded) {
                      handleAsk();
                    }
                  }}
                  placeholder="Talk to your textbook..."
                  className="flex-1 bg-[#2A2A2A] text-white placeholder-gray-500 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-400"
                  disabled={!pdfUploaded}
                />
                <button
                  onClick={handleAsk}
                  disabled={loading || !question.trim() || !pdfUploaded}
                  className="bg-purple-400 hover:bg-purple-500 text-white font-semibold py-3 px-6 rounded-xl shadow-lg transition-all duration-300 disabled:opacity-50"
                >
                  {loading ? <ClipLoader size={20} color="#fff" /> : 'Ask'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 