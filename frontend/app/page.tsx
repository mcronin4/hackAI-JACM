"use client";
import React, { useState, useEffect, useRef } from 'react';
import { ArrowRight, Loader2, CheckCircle, X, Send, Copy, FileText, Youtube, Video, FileText as Transcript } from 'lucide-react';
import { useAuthStore } from '@/lib/auth-store';
import { ProfileDropdown } from '@/components/ProfileDropdown';
import { useSearchParams } from 'next/navigation';
import AuthModal from '@/components/auth/AuthModal';

// X.com Logo Component
const XLogo = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
  </svg>
);

const API_URL = 'http://localhost:8000';

// Function to extract YouTube video ID from URL
const extractYouTubeId = (url: string): string | null => {
  const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/;
  const match = url.match(regex);
  return match ? match[1] : null;
};

function App() {
  const { user, isLoggedIn, isLoading, logout, checkAuthStatus, resetAuthState } = useAuthStore();
  const searchParams = useSearchParams();
  const [content, setContent] = useState('');
  const [contentType, setContentType] = useState<'text' | 'youtube'>('text');
  const [youtubeViewType, setYoutubeViewType] = useState<'video' | 'transcript'>('video');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [isTranscriptLoading, setIsTranscriptLoading] = useState(false);
  const [contentBlocks, setContentBlocks] = useState<string[]>([]);
  const [expandedPost, setExpandedPost] = useState<number | null>(null);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [isStarted, setIsStarted] = useState(false);
  const [editingContent, setEditingContent] = useState('');
  const [copySuccess, setCopySuccess] = useState(false);
  const [isContentTransitioning, setIsContentTransitioning] = useState(false);
  const [isYoutubeViewTransitioning, setIsYoutubeViewTransitioning] = useState(false);
  const [actualTranscript, setActualTranscript] = useState<string>('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const editTextareaRef = useRef<HTMLTextAreaElement>(null);
  const youtubeInputRef = useRef<HTMLInputElement>(null);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  // Check authentication status on component mount
  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  // Handle auth errors from URL parameters
  useEffect(() => {
    const error = searchParams.get('error');
    if (error) {
      console.error('Authentication error:', error);
      // You can add a toast notification here if you want
      // For now, we'll just log it
    }
  }, [searchParams]);

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

  // Clear content when switching content type with fade transition
  useEffect(() => {
    if (content.trim()) {
      setIsContentTransitioning(true);
      setTimeout(() => {
        setContent('');
        setIsContentTransitioning(false);
      }, 150);
    }
  }, [contentType, content]);

  // Helper function to start post generation (used after transcript is ready)
  const startPostGeneration = (transcriptText?: string, youtubeUrl?: string) => {
    setIsProcessing(true);
    setContentBlocks([]);

    // Use transcript text if provided, otherwise use the content from the text box
    const textToProcess = transcriptText || content;
    
    // Build request body
    const body: {
      text: string;
      target_platforms: string[];
      original_url?: string;
    } = {
      text: textToProcess,
      target_platforms: ['twitter']
    };
    
    // Add original_url if we have a YouTube URL
    if (youtubeUrl) {
      body.original_url = youtubeUrl;
    }
    
    console.log('Sending post generation request:', body);
    
    // Send the content to the API
    fetch(API_URL + '/api/v1/generate-posts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Post generation API response:', data);
        
        if (data.success && data.generated_posts) {
          // Set the actual generated posts from the API
          setContentBlocks(data.generated_posts);
          setIsProcessing(false);
          setIsComplete(true);
        } else {
          // Handle API errors
          console.error('API returned error:', data.error);
          setContentBlocks(['Error: Failed to generate posts. Please try again.']);
          setIsProcessing(false);
          setIsComplete(false);
        }
      })
      .catch(error => {
        console.error('Error generating posts:', error);
        setContentBlocks(['Error: Unable to connect to the server. Please check if the backend is running.']);
        setIsProcessing(false);
        setIsComplete(false);
      });
  };

  const handleStart = () => {
    setIsStarted(true);

    if (contentType === 'youtube') {
      // Validate YouTube URL first
      if (!content.trim() || !extractYouTubeId(content)) {
        setContentBlocks(['Error: Please enter a valid YouTube URL.']);
        setIsProcessing(false);
        setIsComplete(false);
        return;
      }
      
      // For YouTube content, first get transcript, then generate posts
      setIsTranscriptLoading(true);
      
      const youtubeBody = {
        url: content
      };
      
      console.log('Calling YouTube API:', youtubeBody);
      
      // Step 1: Call YouTube transcription API
      fetch(API_URL + '/api/v1/youtube/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(youtubeBody)
      })
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          console.log('YouTube API response:', data);
          
          if (data.success) {
            if (data.transcript) {
              // Store the actual transcript
              setActualTranscript(data.transcript);
              setIsTranscriptLoading(false);
              // Step 2: Use transcript to generate posts
              startPostGeneration(data.transcript, content);
            } else {
              // Video was processed but transcription failed
              console.warn('Video processed but transcription failed');
              setActualTranscript('Transcription failed. This might be due to a large file size or API timeout.');
              setIsTranscriptLoading(false);
              setContentBlocks(['Error: Video was downloaded successfully, but transcription failed. This might be due to a large file size or API timeout. Please try with a shorter video.']);
              setIsProcessing(false);
              setIsComplete(false);
            }
          } else {
            // Handle YouTube API errors
            console.error('YouTube API error:', data.error_message);
            setIsTranscriptLoading(false);
            setContentBlocks([`Error: Failed to process YouTube video. ${data.error_message || 'Please try again.'}`]);
            setIsProcessing(false);
            setIsComplete(false);
          }
        })
        .catch(error => {
          console.error('Error calling YouTube API:', error);
          setIsTranscriptLoading(false);
          setContentBlocks(['Error: Unable to process YouTube video. Please check the URL and try again.']);
          setIsProcessing(false);
          setIsComplete(false);
        });
    } else {
      // Validate text content
      if (!content.trim()) {
        setContentBlocks(['Error: Please enter some text to generate posts from.']);
        setIsProcessing(false);
        setIsComplete(false);
        return;
      }
      
      // For text content, start post generation immediately
      startPostGeneration();
    }
  };

  const handleReset = () => {
    // Reset all state to initial values
    setContent('');
    setContentType('text');
    setYoutubeViewType('video');
    setIsProcessing(false);
    setIsComplete(false);
    setIsTranscriptLoading(false);
    setContentBlocks([]);
    setExpandedPost(null);
    setIsTransitioning(false);
    setIsStarted(false);
    setEditingContent('');
    setCopySuccess(false);
    setIsContentTransitioning(false);
    setIsYoutubeViewTransitioning(false);
    setActualTranscript('');
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setContent(e.target.value);
  };

  const handleYouTubeInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setContent(e.target.value);
  };

  const handleContentTypeChange = (newType: 'text' | 'youtube') => {
    if (newType !== contentType) {
      setIsContentTransitioning(true);
      setTimeout(() => {
        setContentType(newType);
        setTimeout(() => {
          setIsContentTransitioning(false);
          // Focus the appropriate input field after transition completes
          if (newType === 'text') {
            textareaRef.current?.focus();
          } else if (newType === 'youtube') {
            youtubeInputRef.current?.focus();
          }
        }, 50);
      }, 150);
    }
  };

  const handleYoutubeViewTypeChange = (newViewType: 'video' | 'transcript') => {
    if (newViewType !== youtubeViewType) {
      setIsYoutubeViewTransitioning(true);
      setTimeout(() => {
        setYoutubeViewType(newViewType);
        setTimeout(() => {
          setIsYoutubeViewTransitioning(false);
        }, 50);
      }, 150);
    }
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

  const getPlaceholderText = () => {
    return contentType === 'text' 
      ? 'Paste your content here...' 
      : 'Paste YouTube link here...';
  };

  // Get YouTube video ID for embedding
  const youtubeVideoId = contentType === 'youtube' && content ? extractYouTubeId(content) : null;
  const hasValidYouTubeUrl = youtubeVideoId !== null;

  return (
    <div className="h-screen bg-white p-8 flex flex-col overflow-hidden relative">
      {/* Fixed Profile/Login Button - Top Right */}
      <div className="fixed top-4 right-4 z-50">
        {isLoggedIn && user ? (
          <ProfileDropdown 
            user={user} 
            isLoading={isLoading} 
            onLogout={logout} 
          />
        ) : (
          <button 
            onClick={() => setIsAuthModalOpen(true)}
            className="bg-gradient-to-r from-teal-600 to-teal-400 text-white px-4 py-2 rounded-lg hover:from-teal-500 hover:to-teal-300 transition-all transform hover:scale-105 flex items-center gap-2 text-sm font-semibold shadow-lg"
          >
            Sign Up / Login
          </button>
        )}
      </div>

      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
      />

      <div className="flex flex-1 min-h-0">
        {/* Content Section */}
        <div className={`transition-all duration-500 ${isStarted ? 'w-1/2' : 'w-2/3'} flex flex-col min-h-0`}>
          {/* Header - moves up when YouTube video is present or when started */}
          <div className={`transition-all duration-500 ${
            isStarted || (contentType === 'youtube' && hasValidYouTubeUrl)
              ? 'mb-4' 
              : 'mt-32 mb-8'
          } flex-shrink-0`}>
            <div className="flex items-end justify-between mb-8">
              <div className="flex items-fi">
                <img 
                  src="/chameleon_logo.png" 
                  alt="Chameleon Logo" 
                  className={`transition-all duration-500 mr-4 ${
                    isStarted || (contentType === 'youtube' && hasValidYouTubeUrl)
                      ? 'w-8 h-8' 
                      : 'w-16 h-16 md:w-20 md:h-20'
                  }`}
                />
                <div className="flex flex-col">
                  <h1 
                    onClick={handleReset}
                    className={`font-bold bg-gradient-to-r from-teal-600 to-teal-400 bg-clip-text text-transparent text-left transition-all duration-500 cursor-pointer hover:from-teal-500 hover:to-teal-300 ${
                      isStarted || (contentType === 'youtube' && hasValidYouTubeUrl)
                        ? 'text-lg' 
                        : 'text-5xl md:text-6xl'
                    }`}
                  >
                    chameleon
                  </h1>
                  {!isStarted && !(contentType === 'youtube' && hasValidYouTubeUrl) && (
                  <p className="text-teal-500 font-bold text-left transition-all duration-500 text-lg mt-2">
                    adapt your content to any platform
                  </p>
                )}
                </div>
              </div>
              
              {/* Start Button */}
              {content.trim() && !isStarted && (
                <button 
                  onClick={handleStart}
                  className="bg-gradient-to-r from-teal-600 to-teal-400 text-white px-4 py-2 rounded-lg hover:bg-teal-400 transition-all transform hover:scale-105 flex items-center gap-2 text-sm font-semibold"
                >
                  Start
                  <ArrowRight className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
          
          {/* Content Type Toggle - Hide unused option when started */}
          <div className="mb-3 flex-shrink-0 flex items-center gap-4">
            <div className="flex bg-gray-100 rounded-md p-0.5 w-fit">
              {/* Text button - hide when started and contentType is youtube */}
              {!(isStarted && contentType === 'youtube') && (
                <button
                  onClick={() => handleContentTypeChange('text')}
                  className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-medium transition-all ${
                    contentType === 'text'
                      ? 'bg-white text-teal-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                  disabled={isProcessing || isComplete}
                >
                  <FileText className="w-3 h-3" />
                  Text
                </button>
              )}
              
              {/* YouTube button - hide when started and contentType is text */}
              {!(isStarted && contentType === 'text') && (
                <button
                  onClick={() => handleContentTypeChange('youtube')}
                  className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-medium transition-all ${
                    contentType === 'youtube'
                      ? 'bg-white text-red-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                  disabled={isProcessing || isComplete}
                >
                  <Youtube className="w-3 h-3" />
                  YouTube Link
                </button>
              )}
            </div>

            {/* Video/Transcript Toggle - Only show when YouTube is selected, started, and has valid URL */}
            {isStarted && contentType === 'youtube' && hasValidYouTubeUrl && (
              <div className="flex bg-gray-100 rounded-md p-0.5 w-fit">
                <button
                  onClick={() => handleYoutubeViewTypeChange('video')}
                  className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-medium transition-all ${
                    youtubeViewType === 'video'
                      ? 'bg-white text-blue-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                  disabled={isTranscriptLoading}
                >
                  <Video className="w-3 h-3" />
                  Video
                </button>
                <button
                  onClick={() => handleYoutubeViewTypeChange('transcript')}
                  className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-medium transition-all ${
                    youtubeViewType === 'transcript'
                      ? 'bg-white text-purple-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                  disabled={isTranscriptLoading}
                >
                  <Transcript className="w-3 h-3" />
                  Transcript
                </button>
              </div>
            )}
          </div>
          
          {/* Content Input Area with fade transitions */}
          <div className="flex-1 min-h-0 flex flex-col relative">
            {contentType === 'text' ? (
              <textarea
                ref={textareaRef}
                value={content}
                onChange={handleContentChange}
                placeholder={getPlaceholderText()}
                className={`w-full flex-1 min-h-0 p-6 rounded-lg resize-none focus:outline-none shadow-lg text-sm leading-relaxed text-left bg-white text-black transition-all duration-300 ${
                  isContentTransitioning ? 'opacity-0' : 'opacity-100'
                }`}
                disabled={isProcessing || isComplete}
              />
            ) : (
              <div className={`flex-1 min-h-0 flex flex-col transition-all duration-300 ${
                isContentTransitioning ? 'opacity-0' : 'opacity-100'
              }`}>
                {/* YouTube URL Input */}
                <input
                  ref={youtubeInputRef}
                  type="text"
                  value={content}
                  onChange={handleYouTubeInputChange}
                  placeholder={getPlaceholderText()}
                  className="w-full p-4 rounded-lg focus:outline-none shadow-lg text-sm bg-white text-black flex-shrink-0 h-16"
                  disabled={isProcessing || isComplete}
                />
                
                {/* YouTube Content Area - Video or Transcript */}
                {hasValidYouTubeUrl && (
                  <div className="flex-1 min-h-0 mt-4 relative">
                    {/* Video View */}
                    {youtubeViewType === 'video' && (
                      <div className={`absolute inset-0 bg-gray-100 rounded-lg overflow-hidden shadow-lg transition-all duration-300 ${
                        isYoutubeViewTransitioning ? 'opacity-0' : 'opacity-100'
                      }`}>
                        <iframe
                          src={`https://www.youtube.com/embed/${youtubeVideoId}`}
                          title="YouTube video player"
                          frameBorder="0"
                          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                          allowFullScreen
                          className="w-full h-full"
                        />
                      </div>
                    )}
                    
                    {/* Transcript View */}
                    {youtubeViewType === 'transcript' && (
                      <div className={`flex-1 bg-white rounded-lg shadow-lg relative transition-all duration-300 ${
                        isYoutubeViewTransitioning ? 'opacity-0' : 'opacity-100'
                      }`}>
                        {/* Transcript Loading Overlay */}
                        {isTranscriptLoading && (
                          <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center z-10 rounded-lg">
                            <div className="flex flex-col items-center gap-3">
                              <Loader2 className="w-8 h-8 text-teal-500 animate-spin" />
                              <p className="text-sm text-gray-600">Loading transcript...</p>
                            </div>
                          </div>
                        )}
                        
                        {/* Transcript Content - Simple scrollable div */}
                        <div className={`h-full p-6 overflow-y-auto rounded-lg transition-all duration-300 ${
                          isTranscriptLoading ? 'opacity-50 pointer-events-none' : 'opacity-100'
                        }`}>
                          <div className="text-sm leading-relaxed text-gray-700 whitespace-pre-line overflow-y-auto">
                            {actualTranscript || 'Enter a YouTube URL and click Start to see the transcript here.'}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
                
                {/* Invalid URL message */}
                {contentType === 'youtube' && content && !hasValidYouTubeUrl && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-600">
                      Please enter a valid YouTube URL
                    </p>
                    <p className="text-xs text-red-400 mt-1">
                      Supported formats: youtube.com/watch?v=... or youtu.be/...
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Processing/Complete Section */}
        {isStarted && (
          <div className="w-1/2 p-8 flex flex-col min-h-0">
            <div className="text-center mb-6 flex-shrink-0">
              {isTranscriptLoading ? (
                <>
                  <div className="w-12 h-12 mx-auto mb-3 bg-purple-50 rounded-full flex items-center justify-center">
                    <Loader2 className="w-6 h-6 text-purple-500 animate-spin" />
                  </div>
                  <p className="text-purple-600 text-xs">Loading transcript...</p>
                </>
              ) : isProcessing ? (
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

            {/* Tab Area with Post Count */}
            <div className="flex items-center justify-between mb-4 flex-shrink-0">
              <div className="flex items-center gap-2 px-3 py-2 bg-teal-50 rounded-lg border border-teal-200">
                <XLogo className="w-4 h-4 text-teal-500" />
                <span className="text-sm text-teal-700 font-medium">Generated Posts</span>
              </div>
              {contentBlocks.length > 0 && !isProcessing && (
                <div className="text-xs text-gray-500">
                  {contentBlocks.length} post{contentBlocks.length !== 1 ? 's' : ''} generated
                </div>
              )}
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
                      <p className="text-sm text-gray-700 leading-relaxed">{block}</p>
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