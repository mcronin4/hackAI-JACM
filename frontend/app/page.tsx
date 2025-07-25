"use client";
import React, { useState, useEffect, useRef, Suspense } from 'react';
import Image from 'next/image';
import { ArrowRight, Loader2, CheckCircle, X, Copy, FileText, Youtube, Video, FileText as Transcript } from 'lucide-react';
import { useAuthStore } from '@/lib/auth-store';
import { ProfileDropdown } from '@/components/ProfileDropdown';
import { useSearchParams } from 'next/navigation';
import AuthModal from '@/components/auth/AuthModal';

// X.com Logo Component
const XLogo = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 20 20" className={className} fill="currentColor">
    <path d="M15.5 2h2.5l-5.5 6.3L18.5 18h-5l-4-5.2L5.5 18H3l6-6.8L3 2h5l3.5 4.7L15.5 2zm-1 14h1.4L6.5 3.5H5L14.5 16z"/>
  </svg>
);

// LinkedIn Logo Component
const LinkedInLogo = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor">
    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
  </svg>
);

const API_URL = 'http://localhost:8000';

// Function to extract YouTube video ID from URL
const extractYouTubeId = (url: string): string | null => {
  const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/;
  const match = url.match(regex);
  return match ? match[1] : null;
};

// Platform types
type Platform = 'twitter' | 'linkedin';

// Updated response types
interface PlatformPost {
  post_content: string;
  topic_id: number;
  topic_name: string;
  primary_emotion: string;
  content_strategy: string;
  processing_time: number;
}

interface PlatformPosts {
  twitter: PlatformPost[];
  linkedin: PlatformPost[];
}

interface APIResponse {
  success: boolean;
  platform_posts: PlatformPosts;
  generated_posts: string[]; // Legacy compatibility
  total_topics: number;
  successful_generations: number;
  processing_time: number;
  error?: string;
}

function AppContent() {
  const { user, isLoggedIn, isLoading, logout, checkAuthStatus } = useAuthStore();
  const searchParams = useSearchParams();
  const [content, setContent] = useState('');
  const [contentType, setContentType] = useState<'text' | 'youtube'>('text');
  const [youtubeViewType, setYoutubeViewType] = useState<'video' | 'transcript'>('video');
  const [selectedPlatforms, setSelectedPlatforms] = useState<Platform[]>(['twitter']);
  const [activePlatformTab, setActivePlatformTab] = useState<Platform>('twitter');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isTranscriptLoading, setIsTranscriptLoading] = useState(false);
  const [platformPosts, setPlatformPosts] = useState<PlatformPosts>({ twitter: [], linkedin: [] });
  const [contentBlocks, setContentBlocks] = useState<string[]>([]); // Legacy support
  const [expandedPost, setExpandedPost] = useState<{ platform: Platform; index: number } | null>(null);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [isStarted, setIsStarted] = useState(false);
  const [editingContent, setEditingContent] = useState('');
  const [copySuccess, setCopySuccess] = useState(false);
  const [isContentTransitioning, setIsContentTransitioning] = useState(false);
  const [isYoutubeViewTransitioning, setIsYoutubeViewTransitioning] = useState(false);
  const [actualTranscript, setActualTranscript] = useState<string>('');

  const [pipelineProgress, setPipelineProgress] = useState<number>(0);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const editTextareaRef = useRef<HTMLTextAreaElement>(null);
  const youtubeInputRef = useRef<HTMLInputElement>(null);

  const [isPlatformSelectionStep, setIsPlatformSelectionStep] = useState(false);
  const [isPlatformSelectionVisible, setPlatformSelectionVisible] = useState(false);
  const [isConfirmButtonVisible, setConfirmButtonVisible] = useState(false);
  const [showAnimations, setShowAnimations] = useState(false);
  const [isLayoutTransitioning, setIsLayoutTransitioning] = useState(false);
  console.log(`showAnimations (for build error): ${showAnimations}`);
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [expandedPost]); // handleCloseExpanded intentionally omitted to avoid re-creating listener

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
    } else {
      // If there's no content, don't show transition
      setIsContentTransitioning(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [contentType]); // content intentionally omitted to prevent infinite loop

  // Platform selection handlers
  const handlePlatformToggle = (platform: Platform) => {
    setSelectedPlatforms(prev => {
      const isSelected = prev.includes(platform);
      if (isSelected) {
        // Don't allow deselecting all platforms
        if (prev.length === 1) return prev;
        const newPlatforms = prev.filter(p => p !== platform);
        // If we're removing the active tab, switch to the first remaining platform
        if (platform === activePlatformTab && newPlatforms.length > 0) {
          setActivePlatformTab(newPlatforms[0]);
        }
        return newPlatforms;
      } else {
        const newPlatforms = [...prev, platform];
        // If this is the first platform being added, make it active
        if (prev.length === 0) {
          setActivePlatformTab(platform);
        }
        return newPlatforms;
      }
    });
  };

  const handlePlatformTabChange = (platform: Platform) => {
    if (selectedPlatforms.includes(platform)) {
      setActivePlatformTab(platform);
    }
  };

  // Helper function to start post generation (used after transcript is ready)
  const startPostGeneration = (transcriptText?: string, youtubeUrl?: string) => {
    setIsProcessing(true);
    setPlatformPosts({ twitter: [], linkedin: [] });
    setContentBlocks([]); // Clear legacy blocks

    // Use transcript text if provided, otherwise use the content from the text box
    const textToProcess = transcriptText || content;
    
    console.log('USERUSERUSERUSERUSERUSER User:', user);

    // Build request body with selected platforms
    const body: {
      text: string;
      target_platforms: string[];
      x_handle?: string;
      original_url?: string;
    } = {
      text: textToProcess,
      target_platforms: selectedPlatforms,
      x_handle: user?.x_handle || undefined,
    };
    
    // Add original_url if we have a YouTube URL
    if (youtubeUrl) {
      body.original_url = youtubeUrl;
    }
    
    console.log('Sending streaming post generation request:', body);
    
    // Use streaming API for better user experience
    startStreamingPostGeneration(body);
  };

  // New streaming post generation function
  const startStreamingPostGeneration = (body: { text: string; target_platforms: string[]; original_url?: string }) => {
    // Reset state before starting
    setPlatformPosts({ twitter: [], linkedin: [] });
    setPipelineProgress(0);
    
    // Use fetch for streaming POST requests (EventSource only supports GET)
    fetch(API_URL + '/api/v1/stream-posts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
        'Cache-Control': 'no-cache'
      },
      body: JSON.stringify(body)
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body reader available');
        }
        
        return reader;
      })
      .then(reader => {
        const decoder = new TextDecoder();
        let buffer = '';
        
        const processChunk = async (): Promise<void> => {
          const { done, value } = await reader.read();
          
          if (done) {
            setIsProcessing(false);
            return;
          }
          
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep the last incomplete line in buffer
          
          for (const line of lines) {
            if (line.startsWith('event: ') || line.startsWith('data: ')) {
              handleStreamingEvent(line);
            }
          }
          
          // Continue processing
          return processChunk();
        };
        
        return processChunk();
      })
      .catch(error => {
        console.error('Streaming error:', error);
        setPlatformPosts({ twitter: [], linkedin: [] });
        setContentBlocks(['Error: Failed to establish streaming connection. Falling back to regular API...']);
        
        // Fallback to regular API
        fallbackToRegularAPI(body);
      });
  };

  // Handle streaming events
  const handleStreamingEvent = (line: string) => {
    try {
      console.log('Raw streaming line:', line); // Debug log
      
      if (line.startsWith('event: ')) {
        const eventType = line.substring(7); // Remove 'event: '
        console.log('Event type:', eventType); // Debug log
        return;
      }
      
      if (line.startsWith('data: ')) {
        const jsonData = line.substring(6); // Remove 'data: '
        console.log('Raw JSON data:', jsonData); // Debug log
        
        const eventData = JSON.parse(jsonData);
        console.log('Parsed event data:', eventData); // Debug log
        
        // Check for post content - the backend sends data directly, not nested in 'data' field
        if (eventData.post_content) {
          console.log('Found post content, adding to UI'); // Debug log
          
          // New post received
          const newPost: PlatformPost = {
            post_content: eventData.post_content,
            topic_id: eventData.topic_id || 0,
            topic_name: eventData.topic_name || '',
            primary_emotion: eventData.primary_emotion || '',
            content_strategy: eventData.content_strategy || '',
            processing_time: eventData.processing_time || 0
          };
          
          const platform = (eventData.platform || 'twitter') as Platform;
          console.log('Adding post to platform:', platform, 'Current state:', platformPosts); // Debug log
          
          setPlatformPosts(prev => {
            // Ensure the platform array exists before spreading
            const currentPlatformPosts = prev[platform] || [];
            const updated = {
              ...prev,
              [platform]: [...currentPlatformPosts, newPost]
            };
            console.log('Updated platform posts:', updated); // Debug log
            return updated;
          });
          
          // Update pipeline progress (from backend)
          if (typeof eventData.progress === 'number') {
            setPipelineProgress(eventData.progress);
          }
          
          // Update post progress for status display
          if (eventData.post_progress) {
            // Post progress is now shown via pipeline progress
          }
        } else if (eventData.message) {
          // Status update
          console.log('Status update:', eventData.message);
          
          // Update pipeline progress
          if (typeof eventData.progress === 'number') {
            setPipelineProgress(eventData.progress);
          }
          
          // Set expected total when we know it (no longer needed with pipeline progress)
          // if (eventData.total_posts_expected) {
          //   // This was for individual post progress, now using pipeline progress
          // }
        } else if (eventData.error) {
          // Error occurred
          console.error('Streaming error:', eventData.error);
          setContentBlocks([`Error: ${eventData.error}`]);
          setIsProcessing(false);
        } else if (eventData.total_processing_time !== undefined) {
          // Completion event
          console.log('Streaming complete');
          setPipelineProgress(100);
          setIsProcessing(false);
        } else {
          console.log('Unhandled event data:', eventData); // Debug log
        }
      }
    } catch (error) {
      console.error('Error parsing streaming event:', error, 'Line:', line);
    }
  };

  // Fallback to regular API if streaming fails
  const fallbackToRegularAPI = (body: { text: string; target_platforms: string[]; original_url?: string }) => {
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
      .then((data: APIResponse) => {
        if (data.success && data.platform_posts) {
          setPlatformPosts(data.platform_posts);
          
          const allPosts: string[] = [];
          selectedPlatforms.forEach(platform => {
            const posts = data.platform_posts[platform] || [];
            posts.forEach(post => allPosts.push(post.post_content));
          });
          setContentBlocks(allPosts);
        } else {
          setContentBlocks(['Error: Failed to generate posts using fallback API.']);
        }
        setIsProcessing(false);
      })
      .catch(error => {
        console.error('Fallback API error:', error);
        setContentBlocks(['Error: Both streaming and fallback APIs failed.']);
        setIsProcessing(false);
      });
  };

  // New handleStart function
  const handleStart = () => {
    // Validate input first
    if (contentType === 'youtube') {
      if (!content.trim() || !extractYouTubeId(content)) {
        setContentBlocks(['Error: Please enter a valid YouTube URL.']);
        return; // Don't proceed
      }
    } else {
       if (!content.trim()) {
        setContentBlocks(['Error: Please enter some text to generate posts from.']);
        return;
      }
    }
    
    // If validation passes, show platform selection UI
    setIsPlatformSelectionStep(true);
    
    // Animate platform selection in after a brief delay
    setTimeout(() => {
      setPlatformSelectionVisible(true);
      setConfirmButtonVisible(true);
    }, 50);
  };

  // Add this entire new function
  const handleConfirm   = () => {
    // Animate platform selection and confirm button out
    setPlatformSelectionVisible(false);
    setConfirmButtonVisible(false);
    
    // Start layout transition immediately
    setIsLayoutTransitioning(true);
    
    // Wait for animation to complete before proceeding
    setTimeout(() => {
      // Now we start the actual processing
      setIsPlatformSelectionStep(false);
      setIsStarted(true);
      setShowAnimations(true); // Enable animations for new posts
      
      // This part is the logic from your original handleStart function
      if (contentType === 'youtube') {
        setIsTranscriptLoading(true);
        const youtubeBody = { url: content };
        fetch(API_URL + '/api/v1/youtube/process', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(youtubeBody)
        })
          .then(response => response.json())
          .then(data => {
            if (data.success && data.transcript) {
              setActualTranscript(data.transcript);
              setIsTranscriptLoading(false);
              startPostGeneration(data.transcript, content); // Call your existing function
            } else {
              // ... error handling
              setIsTranscriptLoading(false);
              setContentBlocks([`Error: ${data.error_message || 'Transcription failed.'}`]);
              setIsProcessing(false);
            }
          })
          .catch(() => {
            // ... error handling
            setIsTranscriptLoading(false);
            setContentBlocks(['Error: Unable to process YouTube video.']);
            setIsProcessing(false);
          });
      } else {
        // For text content, start post generation immediately
        startPostGeneration(); // Call your existing function
      }
    }, 300); // Wait for fade-out animation
  };

  const handleReset = () => {
    setIsStarted(false);
    setIsProcessing(false);
    setIsTranscriptLoading(false);
    setPlatformPosts({ twitter: [], linkedin: [] });
    setContentBlocks([]);
    setContent('');
    setExpandedPost(null);
    setEditingContent('');
    setCopySuccess(false);
    setActualTranscript('');
    setPipelineProgress(0);
    setActivePlatformTab(selectedPlatforms[0] || 'twitter');
    setPlatformSelectionVisible(false);
    setConfirmButtonVisible(false);
    setIsLayoutTransitioning(false);
    setIsPlatformSelectionStep(false);
    setShowAnimations(false);
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setContent(e.target.value);
  };

  const handleYouTubeInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setContent(e.target.value);
  };

  const handleContentTypeChange = (newType: 'text' | 'youtube') => {
    if (newType !== contentType) {
      console.log('Switching content type from', contentType, 'to', newType);
      setContentType(newType);
      
      // Focus the appropriate input after a brief delay to ensure DOM is updated
      setTimeout(() => {
        if (newType === 'text' && textareaRef.current) {
          textareaRef.current.focus();
          console.log('Focused text area');
        } else if (newType === 'youtube' && youtubeInputRef.current) {
          youtubeInputRef.current.focus();
          console.log('Focused YouTube input');
        }
      }, 100);
    }
  };

  const handleYoutubeViewTypeChange = (newViewType: 'video' | 'transcript') => {
    if (newViewType !== youtubeViewType) {
      setIsYoutubeViewTransitioning(true);
      setTimeout(() => {
        setYoutubeViewType(newViewType);
        setIsYoutubeViewTransitioning(false);
      }, 150);
    }
  };

  const handlePostClick = (platform: Platform, index: number) => {
    setIsTransitioning(true);
    setExpandedPost({ platform, index });
    
    // Get the content from the specific platform
    const posts = platformPosts[platform];
    if (posts && posts[index]) {
      setEditingContent(posts[index].post_content);
    }
    
    setTimeout(() => {
      setIsTransitioning(false);
      if (editTextareaRef.current) {
        editTextareaRef.current.focus();
      }
    }, 300);
  };

  const handleCloseExpanded = () => {
    setIsTransitioning(true);
    
    // Update the platform posts with edited content
    if (expandedPost !== null) {
      const { platform, index } = expandedPost;
      const updatedPlatformPosts = { ...platformPosts };
      if (updatedPlatformPosts[platform] && updatedPlatformPosts[platform][index]) {
        updatedPlatformPosts[platform][index].post_content = editingContent;
        setPlatformPosts(updatedPlatformPosts);
        
        // Also update legacy contentBlocks
        const allPosts: string[] = [];
        selectedPlatforms.forEach(p => {
          const posts = updatedPlatformPosts[p] || [];
          posts.forEach(post => allPosts.push(post.post_content));
        });
        setContentBlocks(allPosts);
      }
    }
    
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
        <div className={`transition-all duration-500 ${isLayoutTransitioning || isStarted ? 'w-1/2' : 'w-2/3'} flex flex-col min-h-0`}>
          {/* Header - moves up when YouTube video is present or when started */}
          <div className={`transition-all duration-500 ${ isStarted || isPlatformSelectionStep || (contentType === 'youtube' && hasValidYouTubeUrl) ? 'mb-4' : 'mt-32 mb-8' } flex-shrink-0`}>
            <div className="flex items-end justify-between mb-8">
              <div className="flex items-fi">
                <Image 
                  src="/chameleon_logo.png" 
                  alt="Chameleon Logo" 
                  width={80}
                  height={80}
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
              
              {/* Start Button - Only show when not in platform selection step */}
              {content.trim() && !isStarted && !isPlatformSelectionStep && (
                <button
                  onClick={handleStart}
                  className="cursor-pointer bg-gradient-to-r from-teal-600 to-teal-400 text-white px-4 py-2 rounded-lg hover:bg-teal-400 transition-all transform hover:scale-105 flex items-center gap-2 text-sm font-semibold"
                >
                  Start
                  <ArrowRight className="w-4 h-4" />
                </button>
              )}

              {/* Platform Selection - Only show in platform selection step */}
                  {isPlatformSelectionStep && (
                    <div className={`flex items-center gap-4 transition-all duration-300 ${
                      isPlatformSelectionVisible ? 'opacity-100 transform translate-y-0' : 'opacity-0 transform -translate-y-4'
                    }`}>
                      {isPlatformSelectionStep && (
                    <div className={`flex justify-end items-center transition-all duration-300 ${
                      isConfirmButtonVisible ? 'opacity-100 transform translate-y-0' : 'opacity-0 transform translate-y-4'
                    }`}>
                      <button
                        onClick={handleConfirm}
                        className="cursor-pointer bg-white border-2 border-teal-500 text-teal-500 px-4 py-2 rounded-lg hover:bg-teal-50 transition-all transform hover:scale-105 flex items-center gap-2 text-sm font-semibold"
                      >
                        Confirm
                        {/* <ArrowRight className="w-4 h-4" /> */}
                      </button>
                    </div>
                  )}
                  <p className="text-xs text-gray-500">Select platforms:</p>
                  <div className="flex items-center gap-3">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" checked={selectedPlatforms.includes('twitter')} onChange={() => handlePlatformToggle('twitter')} className="sr-only"/>
                      <div className={`w-8 h-8 rounded-md flex items-center justify-center transition-all ${selectedPlatforms.includes('twitter') ? 'bg-black text-white' : 'bg-gray-100 text-gray-400 hover:bg-gray-200'}`}>
                        <XLogo className="w-4 h-4" />
                      </div>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" checked={selectedPlatforms.includes('linkedin')} onChange={() => handlePlatformToggle('linkedin')} className="sr-only"/>
                      <div className={`w-8 h-8 rounded-md flex items-center justify-center transition-all ${selectedPlatforms.includes('linkedin') ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-400 hover:bg-gray-200'}`}>
                        <LinkedInLogo className="w-4 h-4" />
                      </div>
                    </label>
                  </div>
                </div>
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
                  className={`cursor-pointer flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-medium transition-all ${
                    contentType === 'text'
                      ? 'bg-white text-teal-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                  disabled={isProcessing || isPlatformSelectionStep}
                >
                  <FileText className="w-3 h-3" />
                  Text
                </button>
              )}
              
              {/* YouTube button - hide when started and contentType is text */}
              {!(isStarted && contentType === 'text') && (
                <button
                  onClick={() => handleContentTypeChange('youtube')}
                  className={`cursor-pointer flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-medium transition-all ${
                    contentType === 'youtube'
                      ? 'bg-white text-red-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                  disabled={isProcessing}
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
                  className={`cursor-pointer flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-medium transition-all ${
                    youtubeViewType === 'video'
                      ? 'bg-white text-teal-700 shadow-sm'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                  disabled={isTranscriptLoading}
                >
                  <Video className="w-3 h-3" />
                  Video
                </button>
                <button
                  onClick={() => handleYoutubeViewTypeChange('transcript')}
                  className={`cursor-pointer flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-medium transition-all ${
                    youtubeViewType === 'transcript'
                      ? 'bg-white text-teal-700 shadow-sm'
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
                className={`w-full flex-1 min-h-0 p-6 rounded-lg resize-none focus:outline-none shadow-[0_0_15px_rgba(0,0,0,0.1)] text-sm leading-relaxed text-left bg-white text-black transition-all duration-300 ${
                  isContentTransitioning ? 'opacity-0' : 'opacity-100'
                }`}
                disabled={isProcessing || isPlatformSelectionStep}
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
                  className="w-full p-4 rounded-lg focus:outline-none shadow-[0_0_15px_rgba(0,0,0,0.1)] text-sm bg-white text-black flex-shrink-0 h-16"
                  disabled={isProcessing || isPlatformSelectionStep}
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
                      <div className={`absolute inset-0 bg-white rounded-lg shadow-lg border border-gray-200 transition-all duration-300 ${
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
                          <div className="text-sm leading-relaxed text-gray-700 whitespace-pre-line">
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
                  <div className="text-gray-600 text-xs space-y-2">
                    {/* Pipeline progress bar (0-100%) */}
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-teal-500 h-2 rounded-full transition-all duration-500" 
                        style={{ 
                          width: `${pipelineProgress}%` 
                        }}
                      />
                    </div>
                    <p className="text-xs text-gray-500">
                      {pipelineProgress < 25 ? 'Extracting topics...' : 
                       pipelineProgress < 50 ? 'Analyzing emotions...' : 
                       pipelineProgress < 100 ? 'Generating posts...' : 
                       'Complete!'}
                    </p>
                  </div>
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

            {/* Platform Tabs and Posts */}
            <div className="flex flex-col flex-1 min-h-0">
              {/* Platform Tab Headers */}
              <div className="flex items-center justify-between mb-4 flex-shrink-0">
                <div className="flex bg-gray-100 rounded-md p-0.5 w-fit">
                  {selectedPlatforms
                    .sort((a, b) => {
                      // Ensure Twitter comes first
                      if (a === 'twitter') return -1;
                      if (b === 'twitter') return 1;
                      return 0;
                    })
                    .map(platform => {
                      const Icon = platform === 'twitter' ? XLogo : LinkedInLogo;
                      const platformColor = platform === 'twitter' ? 'text-black' : 'text-blue-600';
                      
                      return (
                        <button
                          key={platform}
                          onClick={() => handlePlatformTabChange(platform)}
                          className={`cursor-pointer flex items-center justify-center gap-1.5 px-4 py-1.5 rounded text-xs font-medium transition-all min-w-[80px] ${
                            activePlatformTab === platform
                              ? `bg-white ${platformColor} shadow-sm`
                              : 'text-gray-600 hover:text-gray-800'
                          }`}
                        >
                          <Icon className="w-4 h-4" />
                        </button>
                      );
                    })}
                </div>
              </div>

              {/* Active Platform Posts Container */}
              {(() => {
                const activePosts = platformPosts[activePlatformTab] || [];
                return (
                  <div className={`flex-1 min-h-0 bg-gray-50 border-gray-200 rounded-lg border p-4 relative overflow-hidden`}>
                    {/* Normal view - scrollable platform posts */}
                    <div className={`h-full transition-all duration-300 ${
                      expandedPost?.platform === activePlatformTab ? 'opacity-0 scale-95' : 'opacity-100 scale-100'
                    }`}>
                      <div className="h-full space-y-3 pr-2 overflow-y-auto">
                        {activePosts.map((post, index) => (
                          <div
                            key={index}
                            className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm animate-fade-in flex-shrink-0 cursor-pointer transition-all duration-200 hover:scale-103 hover:shadow-md hover:border-teal-300"
                            style={{
                              animationDelay: `${index * 0.1}s`,
                              animationFillMode: 'both'
                            }}
                            onClick={() => handlePostClick(activePlatformTab, index)}
                          >
                            <p className="text-sm text-gray-700 leading-relaxed line-clamp-6">
                              {post.post_content}
                            </p>
                            <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
                              <span>Topic {post.topic_id}</span>
                            </div>
                          </div>
                        ))}

                        {/* Show legacy posts only for Twitter if no platform posts */}
                        {activePlatformTab === 'twitter' && activePosts.length === 0 && contentBlocks.length > 0 && (
                          contentBlocks.map((block, index) => (
                            <div
                              key={`legacy-${index}`}
                              className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm animate-fade-in flex-shrink-0 cursor-pointer transition-all duration-200 hover:scale-102 hover:shadow-md hover:border-teal-300"
                              style={{
                                animationDelay: `${index * 0.1}s`,
                                animationFillMode: 'both'
                              }}
                              onClick={() => {
                                // Legacy support for old posts
                                setIsTransitioning(true);
                                setExpandedPost({ platform: 'twitter', index });
                                setEditingContent(block);
                                setTimeout(() => {
                                  setIsTransitioning(false);
                                  if (editTextareaRef.current) {
                                    editTextareaRef.current.focus();
                                  }
                                }, 300);
                              }}
                            >
                              <p className="text-sm text-gray-700 leading-relaxed">{block}</p>
                            </div>
                          ))
                        )}
                      </div>
                    </div>

                    {/* Expanded view - fills the entire platform container */}
                    {expandedPost?.platform === activePlatformTab && (
                      <div className={`absolute inset-0 text-sm bg-white shadow-lg border border-gray-200 rounded-lg flex transition-all duration-300 overflow-hidden ${
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
                            className="cursor-pointer p-3 hover:bg-gray-200 rounded-lg transition-colors group"
                            title="Close (ESC)"
                          >
                            <X className="w-3 h-3 text-gray-500 group-hover:text-gray-700" />
                          </button>
                          
                          {/* Copy button */}
                          <button
                            onClick={handleCopy}
                            className={`cursor-pointer p-3 rounded-lg transition-colors group ${
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
                );
              })()}
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

        .line-clamp-6 {
          display: -webkit-box;
          -webkit-line-clamp: 6;
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

function App() {
  return (
    <Suspense fallback={<div className="h-screen bg-white flex items-center justify-center">
      <div className="flex flex-col items-center gap-3">
        <Loader2 className="w-8 h-8 text-teal-500 animate-spin" />
        <p className="text-sm text-gray-600">Loading...</p>
      </div>
    </div>}>
      <AppContent />
    </Suspense>
  );
}

export default App;