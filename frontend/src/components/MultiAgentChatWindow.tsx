import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Users, Vote, CheckCircle, Clock, AlertTriangle, Copy, Check } from 'lucide-react';

interface ChatMessage {
  timestamp: string;
  agent: string;
  message_type: string;
  content: string;
  task_id?: string;
  vote_result?: string;
}

interface MultiAgentChatWindowProps {
  isProcessing: boolean;
  chatHistory: ChatMessage[];
  onClose?: () => void;
}

const MultiAgentChatWindow: React.FC<MultiAgentChatWindowProps> = ({ 
  isProcessing, 
  chatHistory, 
  onClose 
}) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [copied, setCopied] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatHistory]);

  const copyAllChat = async () => {
    const chatText = chatHistory.map(message => {
      const timestamp = formatTimestamp(message.timestamp);
      const agentName = getAgentName(message.agent);
      const icon = getMessageIcon(message.message_type);
      const taskId = message.task_id ? `#${message.task_id}` : '';
      const voteResult = message.vote_result ? `[${message.vote_result.toUpperCase()}]` : '';
      
      return `${icon} ${agentName} ${taskId}\n${timestamp}\n${message.content}${voteResult ? ' ' + voteResult : ''}\n\n`;
    }).join('---\n\n');

    try {
      await navigator.clipboard.writeText(chatText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = chatText;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getAgentColor = (agent: string) => {
    const colors = {
      'general_manager': 'bg-purple-100 text-purple-800 border-purple-300',
      'research_agent': 'bg-blue-100 text-blue-800 border-blue-300',
      'budget_agent': 'bg-green-100 text-green-800 border-green-300', 
      'writing_agent': 'bg-orange-100 text-orange-800 border-orange-300',
      'impact_agent': 'bg-red-100 text-red-800 border-red-300',
      'networking_agent': 'bg-cyan-100 text-cyan-800 border-cyan-300',
      'system': 'bg-gray-100 text-gray-800 border-gray-300'
    };
    return colors[agent] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getMessageIcon = (messageType: string) => {
    switch (messageType) {
      case 'plan': return '📋';
      case 'action': return '⚡';
      case 'evaluation': return '🔍';
      case 'vote': return '🗳️';
      case 'result': return '✅';
      case 'error': return '❌';
      case 'system': return '🤖';
      default: return '💬';
    }
  };

  const getAgentName = (agent: string) => {
    const names = {
      'general_manager': 'General Manager',
      'research_agent': 'Research Agent',
      'budget_agent': 'Budget Agent',
      'writing_agent': 'Writing Agent', 
      'impact_agent': 'Impact Agent',
      'networking_agent': 'Networking Agent',
      'system': 'System'
    };
    return names[agent] || agent;
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  if (!isExpanded) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={() => setIsExpanded(true)}
          className="bg-purple-600 text-white p-3 rounded-full shadow-lg hover:bg-purple-700 transition-colors"
        >
          <MessageCircle className="w-6 h-6" />
          {chatHistory.length > 0 && (
            <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
              {chatHistory.length}
            </span>
          )}
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 w-96 h-[600px] bg-white rounded-lg shadow-2xl border border-gray-200 z-50 flex flex-col">
      {/* Header */}
      <div className="bg-purple-600 text-white p-4 rounded-t-lg flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Users className="w-5 h-5" />
          <h3 className="font-semibold">Multi-Agent Chat</h3>
          {isProcessing && (
            <div className="flex items-center space-x-1">
              <Clock className="w-4 h-4 animate-pulse" />
              <span className="text-sm">Processing...</span>
            </div>
          )}
        </div>
        <div className="flex items-center space-x-2">
          {chatHistory.length > 0 && (
            <button
              onClick={copyAllChat}
              className={`flex items-center space-x-1 px-2 py-1 text-xs font-medium rounded transition-colors ${
                copied 
                  ? 'bg-green-500 text-white' 
                  : 'bg-purple-500 hover:bg-purple-400 text-white'
              }`}
              title="Copy entire chat conversation"
            >
              {copied ? (
                <>
                  <Check className="w-3 h-3" />
                  <span>Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3" />
                  <span>Copy All</span>
                </>
              )}
            </button>
          )}
          <button
            onClick={() => setIsExpanded(false)}
            className="text-white hover:text-gray-200 p-1"
          >
            _
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 p-1"
            >
              ×
            </button>
          )}
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {chatHistory.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <MessageCircle className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>Agent discussions will appear here...</p>
          </div>
        ) : (
          chatHistory.map((message, index) => (
            <div key={index} className="space-y-2">
              {/* Agent Header */}
              <div className="flex items-center justify-between">
                <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-medium border ${getAgentColor(message.agent)}`}>
                  <span>{getMessageIcon(message.message_type)}</span>
                  <span>{getAgentName(message.agent)}</span>
                  {message.task_id && (
                    <span className="text-xs opacity-75">#{message.task_id}</span>
                  )}
                </div>
                <span className="text-xs text-gray-500">{formatTimestamp(message.timestamp)}</span>
              </div>

              {/* Message Content */}
              <div className="bg-gray-50 p-3 rounded-lg border-l-4 border-l-purple-400">
                <div className="text-sm text-gray-800 whitespace-pre-wrap">
                  {message.content}
                </div>
                {message.vote_result && (
                  <div className="mt-2 flex items-center space-x-2">
                    <Vote className="w-4 h-4 text-blue-600" />
                    <span className={`text-xs px-2 py-1 rounded ${
                      message.vote_result === 'approve' 
                        ? 'bg-green-100 text-green-800' 
                        : message.vote_result === 'reject'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {message.vote_result.toUpperCase()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Footer Stats */}
      <div className="border-t border-gray-200 p-3 bg-gray-50 rounded-b-lg">
        <div className="flex items-center justify-between text-xs text-gray-600">
          <span>Messages: {chatHistory.length}</span>
          <div className="flex items-center space-x-4">
            <span className="flex items-center space-x-1">
              <CheckCircle className="w-3 h-3 text-green-500" />
              <span>Tasks: {chatHistory.filter(m => m.message_type === 'result').length}</span>
            </span>
            <span className="flex items-center space-x-1">
              <Vote className="w-3 h-3 text-blue-500" />
              <span>Votes: {chatHistory.filter(m => m.vote_result).length}</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MultiAgentChatWindow;