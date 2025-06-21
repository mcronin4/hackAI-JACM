"use client";

import { useState } from "react";
import Image from "next/image";

interface Topic {
  topic_id: number;
  topic_name: string;
  content_excerpt: string;
  confidence_score?: number;
}

interface TopicExtractionResponse {
  topics: Topic[];
  total_topics: number;
  processing_time: number;
}

export default function Home() {
  const [text, setText] = useState("");
  const [maxTopics, setMaxTopics] = useState(10);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<TopicExtractionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!text.trim()) {
      setError("Please enter some text to analyze");
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch("http://localhost:8000/api/v1/extract-topics", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: text.trim(),
          max_topics: maxTopics,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.detail || errorData.detail || "Failed to extract topics");
      }

      const data: TopicExtractionResponse = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setText("");
    setResults(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto pt-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🔍 Content Repurposer
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Paste your text below and we will create the required content for you.
          </p>
        </div>

        {/* Main Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Text Input */}
            <div>
              <label htmlFor="text" className="block text-sm font-semibold text-gray-700 mb-2">
                Text to Analyze
              </label>
              <textarea
                id="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste your text here... (articles, documents, conversations, etc.)"
                className="w-full h-64 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none text-gray-900 placeholder-gray-500"
                disabled={loading}
              />
              <div className="text-right mt-1">
                <span className="text-sm text-gray-500">{text.length} characters</span>
              </div>
            </div>

            {/* Max Topics Input */}
            <div>
              <label htmlFor="maxTopics" className="block text-sm font-semibold text-gray-700 mb-2">
                Maximum Topics to Extract
              </label>
              <input
                type="number"
                id="maxTopics"
                value={maxTopics}
                onChange={(e) => setMaxTopics(Math.max(1, Math.min(50, parseInt(e.target.value) || 10)))}
                min="1"
                max="50"
                className="w-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-gray-900"
                disabled={loading}
              />
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading || !text.trim()}
                className="flex-1 bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Loading...
                  </div>
                ) : (
                  "Send"
                )}
              </button>
              
              <button
                type="button"
                onClick={handleClear}
                disabled={loading}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
              >
                Clear
              </button>
            </div>
          </form>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <div className="flex items-center">
              <div className="text-red-600 mr-3">⚠️</div>
              <div>
                <h3 className="text-red-800 font-semibold">Error</h3>
                <p className="text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Results Display */}
        {results && (
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                Extracted Topics ({results.total_topics})
              </h2>
              <div className="text-sm text-gray-500">
                Processed in {results.processing_time.toFixed(2)}s
              </div>
            </div>

            <div className="space-y-4">
              {results.topics.map((topic) => (
                <div
                  key={topic.topic_id}
                  className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow duration-200"
                >
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {topic.topic_name}
                    </h3>
                    {topic.confidence_score && (
                      <div className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm font-medium">
                        {Math.round(topic.confidence_score * 100)}% confidence
                      </div>
                    )}
                  </div>
                  <p className="text-gray-700 leading-relaxed">
                    {topic.content_excerpt}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500 text-sm">
          <p>Powered by FastAPI + LangGraph • Built with Next.js</p>
        </div>
      </div>
    </div>
  );
}
