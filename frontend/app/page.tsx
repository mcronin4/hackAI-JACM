"use client";
import React, { useState, useEffect, useRef } from 'react';
import { ArrowRight, Loader2, CheckCircle, X, Send, Copy } from 'lucide-react';

// X.com Logo Component
const XLogo = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
  </svg>
);

function App() {
  const [content, setContent] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [contentBlocks, setContentBlocks] = useState<string[]>([]);
  const [expandedPost, setExpandedPost] = useState<number | null>(null);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [isStarted, setIsStarted] = useState(false);
  const [editingContent, setEditingContent] = useState('');
  const [copySuccess, setCopySuccess] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const editTextareaRef = useRef<HTMLTextAreaElement>(null);

  const sampleContentBlocks = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit.",
    "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi.",
    "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae. Itaque earum rerum hic tenetur a sapiente delectus.",
    "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus.",
    "Totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus.",
    "Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.",
    "Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur.",
    "At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti. Vel illum qui dolorem eum fugiat quo voluptas nulla pariatur? At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores.",
    "Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae.",
    "Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat.",
    "Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis."
  ];

  // Handle escape key to close expanded post
  useEffect(() => {
    const handleEscapeKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && expandedPost !== null) {
        handleCloseExpanded();
      }
    };

    document.addEventListener('keydown', handleEscapeKey);
    return () => {
      document.removeEventListener('keydown', handleEscapeKey);
    };
  }, [expandedPost]);

  // Auto-resize textarea
  useEffect(() => {
    if (editTextareaRef.current) {
      editTextareaRef.current.style.height = 'auto';
      editTextareaRef.current.style.height = editTextareaRef.current.scrollHeight + 'px';
    }
  }, [editingContent]);

  const handleStart = () => {
    setIsStarted(true);
    setIsProcessing(true);
    setContentBlocks([]);
    
    // Add content blocks gradually during processing
    const addBlocksGradually = () => {
      let blockIndex = 0;
      const interval = setInterval(() => {
        if (blockIndex < sampleContentBlocks.length) {
          setContentBlocks(prev => [...prev, sampleContentBlocks[blockIndex]]);
          blockIndex++;
        } else {
          clearInterval(interval);
        }
      }, 600); // Add a new block every 600ms

      // Complete processing after 8 seconds (to show more blocks)
      setTimeout(() => {
        setIsProcessing(false);
        setIsComplete(true);
        clearInterval(interval);
      }, 8000);
    };

    addBlocksGradually();
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setContent(e.target.value);
    
    // Keep cursor at the top after paste
    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.setSelectionRange(0, 0);
        textareaRef.current.scrollTop = 0;
      }
    }, 0);
  };

  const handlePostClick = (index: number) => {
    setIsTransitioning(true);
    setExpandedPost(index);
    setEditingContent(contentBlocks[index]);
    
    // Complete transition after animation
    setTimeout(() => {
      setIsTransitioning(false);
    }, 300);
  };

  const handleCloseExpanded = () => {
    // Save the edited content back to the content blocks
    if (expandedPost !== null) {
      const updatedBlocks = [...contentBlocks];
      updatedBlocks[expandedPost] = editingContent;
      setContentBlocks(updatedBlocks);
    }
    
    setIsTransitioning(true);
    
    // After animation, reset everything
    setTimeout(() => {
      setExpandedPost(null);
      setIsTransitioning(false);
      setEditingContent('');
    }, 300);
  };

  const handleEditingContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setEditingContent(e.target.value);
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(editingContent);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const handleSend = () => {
    // Placeholder for send functionality
    console.log('Sending content:', editingContent);
  };

  return (
    <div className="h-screen bg-white p-8 flex flex-col overflow-hidden">
      <div className="flex flex-1 min-h-0">
        {/* Content Section */}
        <div className={`transition-all duration-500 ${isStarted ? 'w-1/2' : 'w-2/3'} flex flex-col min-h-0`}>
          <div className={`transition-all duration-500 ${isStarted ? 'mb-4' : 'mt-32 mb-8'} flex-shrink-0`}>
            <div className="flex items-end justify-between mb-8">
              <h1 className={`font-bold bg-gradient-to-r from-teal-600 to-teal-400 bg-clip-text text-transparent text-left transition-all duration-500 ${
                isStarted 
                  ? 'text-lg' 
                  : 'text-5xl md:text-6xl'
              }`}>
                chameleon
              </h1>
              
              {content.trim() && !isStarted && (
                <button 
                  onClick={handleStart}
                  className="bg-gradient-to-r from-`teal-600` to-teal-400 text-white px-4 py-2 rounded-lg hover:bg-teal-400 transition-all transform hover:scale-105 flex items-center gap-2 text-sm font-semibold"
                >
                  Start
                  <ArrowRight className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
          
          <textarea
            ref={textareaRef}
            value={content}
            onChange={handleContentChange}
            placeholder="Paste your content here..."
            className="w-full flex-1 min-h-0 p-6 rounded-lg resize-none focus:outline-none shadow-lg text-sm leading-relaxed text-left bg-white text-black"
            disabled={isProcessing || isComplete}
          />
        </div>

        {/* Processing/Complete Section */}
        {isStarted && (
          <div className="w-1/2 p-8 flex flex-col min-h-0">
            <div className="text-center mb-6 flex-shrink-0">
              {isProcessing ? (
                <>
                  <div className="w-12 h-12 mx-auto mb-3 bg-teal-50 rounded-full flex items-center justify-center">
                    <Loader2 className="w-6 h-6 text-teal-500 animate-spin" />
                  </div>
                  <p className="text-gray-600 text-xs">Processing...</p>
                </>
              ) : (
                <>
                  <div className="w-12 h-12 mx-auto mb-3 bg-green-50 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  </div>
                  <p className="text-green-600 text-xs font-medium">Complete!</p>
                </>
              )}
            </div>

            {/* Tab Area */}
            <div className="flex items-center mb-4 flex-shrink-0">
              <div className="flex items-center gap-2 px-3 py-2 bg-teal-50 rounded-lg border border-teal-200">
                <XLogo className="w-4 h-4 text-teal-500" />
              </div>
            </div>

            {/* Quotes Container */}
            <div className="flex-1 min-h-0 bg-gray-50 rounded-lg border border-gray-200 p-4 relative overflow-hidden">
              {/* Normal view - scrollable content blocks */}
              <div className={`h-full transition-all duration-300 ${expandedPost !== null ? 'opacity-0 scale-95' : 'opacity-100 scale-100'}`}>
                <div className="h-full overflow-y-auto space-y-4 pr-2">
                  {contentBlocks.map((block, index) => (
                    <div
                      key={index}
                      className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm animate-fade-in flex-shrink-0 cursor-pointer transition-all duration-200 hover:scale-105 hover:shadow-md hover:border-teal-300"
                      style={{
                        animationDelay: `${index * 0.1}s`,
                        animationFillMode: 'both'
                      }}
                      onClick={() => handlePostClick(index)}
                    >
                      <p className="text-sm text-gray-700 leading-relaxed line-clamp-3">{block}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Expanded view - fills the entire quotes container */}
              {expandedPost !== null && (
                <div className={`absolute inset-0 text-sm bg-white shadow-lg border border-gray-200 rounded-lg flex transition-all duration-300 ${
                  isTransitioning ? 'opacity-0 scale-95' : 'opacity-100 scale-100'
                }`}>
                  {/* Main content area */}
                  <div className="flex-1 flex flex-col">
                    {/* Editable Content */}
                    <div className="flex-1 p-6 overflow-y-auto">
                      <textarea
                        ref={editTextareaRef}
                        value={editingContent}
                        onChange={handleEditingContentChange}
                        className="w-full min-h-full resize-none border-none outline-none text-gray-700 leading-relaxed text-sm bg-transparent"
                        placeholder="Start editing your content..."
                        style={{ minHeight: '200px' }}
                      />
                    </div>
                  </div>
                  
                  {/* Right sidebar with controls */}
                  <div className="w-12 bg-gray-50 border-l border-gray-200 flex flex-col items-center py-4 gap-4">
                    {/* Close button */}
                    <button
                      onClick={handleCloseExpanded}
                      className="p-3 hover:bg-gray-200 rounded-lg transition-colors group"
                      title="Close (ESC)"
                    >
                      <X className="w-3 h-3 text-gray-500 group-hover:text-gray-700" />
                    </button>
                    
                    {/* Send button */}
                    <button
                      onClick={handleSend}
                      className="p-3 bg-gradient-to-r from-teal-600 to-teal-400 hover:bg-teal-500 rounded-lg transition-colors group"
                      title="Send"
                    >
                      <Send className="w-3 h-3 text-white" />
                    </button>
                    
                    {/* Copy button */}
                    <button
                      onClick={handleCopy}
                      className={`p-3 rounded-lg transition-colors group ${
                        copySuccess 
                          ? 'bg-green-100 hover:bg-green-200' 
                          : 'hover:bg-gray-200'
                      }`}
                      title="Copy to clipboard"
                    >
                      <Copy className={`w-3 h-3 ${
                        copySuccess 
                          ? 'text-green-600' 
                          : 'text-gray-500 group-hover:text-gray-700'
                      }`} />
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-fade-in {
          animation: fade-in 0.5s ease-out;
        }

        .line-clamp-3 {
          display: -webkit-box;
          -webkit-line-clamp: 3;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }

        /* Custom scrollbar styling */
        .overflow-y-auto::-webkit-scrollbar {
          width: 6px;
        }
        
        .overflow-y-auto::-webkit-scrollbar-track {
          background: #f1f5f9;
          border-radius: 3px;
        }
        
        .overflow-y-auto::-webkit-scrollbar-thumb {
          background: #cbd5e1;
          border-radius: 3px;
        }
        
        .overflow-y-auto::-webkit-scrollbar-thumb:hover {
          background: #94a3b8;
        }
      `}</style>
    </div>
  );
}

export default App;