import React, { useState, useRef } from 'react';
import { Upload, Send, Copy, Trash2, Settings, MessageSquare } from 'lucide-react';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  extractedText?: string;
  promptTemplate?: string;
  finalPrompt?: string;
}

interface NGOProfile {
  name: string;
  mission: string;
  focusAreas: string;
  targetPopulation: string;
  geographicScope: string;
  established: string;
  staff: string;
  budget: string;
}

export default function ModelTestingPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [ngoProfile, setNGOProfile] = useState<NGOProfile>({
    name: '',
    mission: '',
    focusAreas: '',
    targetPopulation: '',
    geographicScope: '',
    established: '',
    staff: '',
    budget: ''
  });
  const [grantDocument, setGrantDocument] = useState('');
  const [extractedText, setExtractedText] = useState('');
  const [promptTemplate, setPromptTemplate] = useState(`You are a professional grant writer helping an NGO fill out grant applications. 

NGO Information:
- Name: {ngo_name}
- Mission: {ngo_mission}
- Focus Areas: {ngo_focus_areas}
- Target Population: {ngo_target_population}
- Geographic Scope: {ngo_geographic_scope}
- Established: {ngo_established}
- Staff Size: {ngo_staff}
- Annual Budget: {ngo_budget}

Grant Context:
{grant_context}

User Request: {user_request}

Please provide a professional, detailed response that aligns with the NGO's profile and addresses the grant requirements. Focus on being specific, measurable, and compelling.`);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [toastMessage, setToastMessage] = useState<{title: string, description: string, variant?: string} | null>(null);

  const showToast = (toast: {title: string, description: string, variant?: string}) => {
    setToastMessage(toast);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      showToast({
        title: "Invalid file type",
        description: "Please upload a PDF file.",
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/ProcessDocument`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setExtractedText(result.extracted_text || 'No text extracted from PDF');
      
      showToast({
        title: "Document processed",
        description: `Extracted ${result.extracted_text?.length || 0} characters from PDF.`
      });
    } catch (error) {
      console.error('Error processing document:', error);
      showToast({
        title: "Upload failed",
        description: "Failed to process PDF document. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const buildFinalPrompt = (userRequest: string): string => {
    return promptTemplate
      .replace('{ngo_name}', ngoProfile.name || '[Not specified]')
      .replace('{ngo_mission}', ngoProfile.mission || '[Not specified]')
      .replace('{ngo_focus_areas}', ngoProfile.focusAreas || '[Not specified]')
      .replace('{ngo_target_population}', ngoProfile.targetPopulation || '[Not specified]')
      .replace('{ngo_geographic_scope}', ngoProfile.geographicScope || '[Not specified]')
      .replace('{ngo_established}', ngoProfile.established || '[Not specified]')
      .replace('{ngo_staff}', ngoProfile.staff || '[Not specified]')
      .replace('{ngo_budget}', ngoProfile.budget || '[Not specified]')
      .replace('{grant_context}', extractedText || grantDocument || '[No grant context provided]')
      .replace('{user_request}', userRequest);
  };

  const sendMessage = async () => {
    if (!currentMessage.trim()) return;

    const finalPrompt = buildFinalPrompt(currentMessage);
    
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: currentMessage,
      timestamp: new Date(),
      extractedText: extractedText || grantDocument,
      promptTemplate: promptTemplate,
      finalPrompt: finalPrompt
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/GemmaProxy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [
            {
              role: 'user',
              content: finalPrompt
            }
          ],
          max_tokens: 2000,
          temperature: 0.7
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: result.choices?.[0]?.message?.content || result.response || 'No response received',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'system',
        content: `Error: ${error instanceof Error ? error.message : 'Failed to get response from model'}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      
      showToast({
        title: "Request failed",
        description: "Failed to get response from the model. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      showToast({
        title: "Copied to clipboard",
        description: "Content has been copied to your clipboard."
      });
    } catch (error) {
      showToast({
        title: "Copy failed",
        description: "Failed to copy content to clipboard.",
        variant: "destructive"
      });
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Toast Notification */}
      {toastMessage && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
          toastMessage.variant === 'destructive' ? 'bg-red-100 border border-red-400 text-red-800' : 'bg-green-100 border border-green-400 text-green-800'
        }`}>
          <div className="font-semibold">{toastMessage.title}</div>
          <div className="text-sm">{toastMessage.description}</div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Model Testing Playground</h1>
          <p className="text-gray-600">Test and fine-tune prompts for the GPT-OSS-120B model with your NGO profile and grant context.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Configuration */}
          <div className="lg:col-span-1 space-y-6">
            {/* NGO Profile */}
            <div className="bg-white rounded-lg shadow-md border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center gap-2 mb-2">
                  <Settings className="h-5 w-5" />
                  <h3 className="text-lg font-semibold">NGO Profile</h3>
                </div>
                <p className="text-gray-600 text-sm">Configure your organization's information for context.</p>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <label htmlFor="ngo-name" className="block text-sm font-medium text-gray-700 mb-1">Organization Name</label>
                  <input
                    type="text"
                    id="ngo-name"
                    value={ngoProfile.name}
                    onChange={(e) => setNGOProfile(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Enter NGO name"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label htmlFor="ngo-mission" className="block text-sm font-medium text-gray-700 mb-1">Mission Statement</label>
                  <textarea
                    id="ngo-mission"
                    value={ngoProfile.mission}
                    onChange={(e) => setNGOProfile(prev => ({ ...prev, mission: e.target.value }))}
                    placeholder="Describe your mission"
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
                  />
                </div>
                <div>
                  <label htmlFor="ngo-focus" className="block text-sm font-medium text-gray-700 mb-1">Focus Areas</label>
                  <input
                    type="text"
                    id="ngo-focus"
                    value={ngoProfile.focusAreas}
                    onChange={(e) => setNGOProfile(prev => ({ ...prev, focusAreas: e.target.value }))}
                    placeholder="e.g., Education, Healthcare, Environment"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label htmlFor="ngo-population" className="block text-sm font-medium text-gray-700 mb-1">Target Population</label>
                  <input
                    type="text"
                    id="ngo-population"
                    value={ngoProfile.targetPopulation}
                    onChange={(e) => setNGOProfile(prev => ({ ...prev, targetPopulation: e.target.value }))}
                    placeholder="Who you serve"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label htmlFor="ngo-scope" className="block text-sm font-medium text-gray-700 mb-1">Geographic Scope</label>
                  <input
                    type="text"
                    id="ngo-scope"
                    value={ngoProfile.geographicScope}
                    onChange={(e) => setNGOProfile(prev => ({ ...prev, geographicScope: e.target.value }))}
                    placeholder="Local, Regional, National, International"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label htmlFor="ngo-established" className="block text-sm font-medium text-gray-700 mb-1">Established</label>
                    <input
                      type="text"
                      id="ngo-established"
                      value={ngoProfile.established}
                      onChange={(e) => setNGOProfile(prev => ({ ...prev, established: e.target.value }))}
                      placeholder="Year"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label htmlFor="ngo-staff" className="block text-sm font-medium text-gray-700 mb-1">Staff Size</label>
                    <input
                      type="text"
                      id="ngo-staff"
                      value={ngoProfile.staff}
                      onChange={(e) => setNGOProfile(prev => ({ ...prev, staff: e.target.value }))}
                      placeholder="Number"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <div>
                  <label htmlFor="ngo-budget" className="block text-sm font-medium text-gray-700 mb-1">Annual Budget</label>
                  <input
                    type="text"
                    id="ngo-budget"
                    value={ngoProfile.budget}
                    onChange={(e) => setNGOProfile(prev => ({ ...prev, budget: e.target.value }))}
                    placeholder="$100,000"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* Grant Context */}
            <div className="bg-white rounded-lg shadow-md border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold mb-2">Grant Context</h3>
                <p className="text-gray-600 text-sm">Upload a grant PDF or paste requirements manually.</p>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileUpload}
                    accept=".pdf"
                    className="hidden"
                  />
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isLoading}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Upload className="h-4 w-4" />
                    {isLoading ? 'Processing...' : 'Upload Grant PDF'}
                  </button>
                </div>
                <div className="text-center text-gray-500">OR</div>
                <div>
                  <label htmlFor="grant-text" className="block text-sm font-medium text-gray-700 mb-1">Paste Grant Requirements</label>
                  <textarea
                    id="grant-text"
                    value={grantDocument}
                    onChange={(e) => setGrantDocument(e.target.value)}
                    placeholder="Paste grant requirements, application guidelines, or specific questions here..."
                    rows={6}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
                  />
                </div>
                {extractedText && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Extracted Text ({extractedText.length} characters)</label>
                    <div className="bg-gray-50 p-3 rounded-md text-sm max-h-32 overflow-y-auto">
                      {extractedText.substring(0, 200)}...
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Prompt Template */}
            <div className="bg-white rounded-lg shadow-md border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold mb-2">Prompt Template</h3>
                <p className="text-gray-600 text-sm">Customize the system prompt sent to the model.</p>
              </div>
              <div className="p-6">
                <textarea
                  value={promptTemplate}
                  onChange={(e) => setPromptTemplate(e.target.value)}
                  placeholder="Enter your prompt template..."
                  rows={10}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm resize-vertical"
                />
              </div>
            </div>
          </div>

          {/* Right Column - Chat Interface */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md border border-gray-200 h-[800px] flex flex-col">
              <div className="p-6 border-b border-gray-200 flex-shrink-0">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <MessageSquare className="h-5 w-5" />
                      <h3 className="text-lg font-semibold">Model Chat Interface</h3>
                    </div>
                    <p className="text-gray-600 text-sm">Test your prompts and see model responses in real-time.</p>
                  </div>
                  <button
                    onClick={clearChat}
                    className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <Trash2 className="h-4 w-4" />
                    Clear Chat
                  </button>
                </div>
                <div className="flex items-center gap-2 mt-4">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    GPT-OSS-120B
                  </span>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    isLoading ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                  }`}>
                    {isLoading ? 'Processing...' : 'Ready'}
                  </span>
                </div>
              </div>

              <div className="flex-1 flex flex-col gap-4 p-6">
                {/* Messages Area */}
                <div className="flex-1 overflow-y-auto pr-4">
                  <div className="space-y-4">
                    {messages.length === 0 && (
                      <div className="text-center text-gray-500 py-8">
                        <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>Start a conversation to test your prompts...</p>
                      </div>
                    )}
                    
                    {messages.map((message) => (
                      <div key={message.id} className="space-y-2">
                        <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                          <div className={`max-w-[80%] rounded-lg px-4 py-2 ${
                            message.type === 'user' 
                              ? 'bg-blue-600 text-white' 
                              : message.type === 'system'
                              ? 'bg-red-100 text-red-800 border border-red-200'
                              : 'bg-gray-100 text-gray-900'
                          }`}>
                            <div className="flex items-center gap-2 mb-2">
                              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                                message.type === 'user' ? 'bg-blue-700 text-blue-100' : 'bg-gray-200 text-gray-800'
                              }`}>
                                {message.type === 'user' ? 'You' : message.type === 'system' ? 'System' : 'Assistant'}
                              </span>
                              <span className="text-xs opacity-70">
                                {message.timestamp.toLocaleTimeString()}
                              </span>
                            </div>
                            <div className="whitespace-pre-wrap">{message.content}</div>
                            <button
                              onClick={() => copyToClipboard(message.content)}
                              className="mt-2 p-1 rounded hover:bg-black/10 focus:outline-none"
                            >
                              <Copy className="h-3 w-3" />
                            </button>
                          </div>
                        </div>

                        {/* Show prompt details for user messages */}
                        {message.type === 'user' && message.finalPrompt && (
                          <details className="text-sm">
                            <summary className="cursor-pointer text-gray-600 hover:text-gray-800">
                              View Final Prompt Sent to Model
                            </summary>
                            <div className="mt-2 p-3 bg-gray-50 rounded-md font-mono text-xs overflow-x-auto">
                              <button
                                onClick={() => copyToClipboard(message.finalPrompt!)}
                                className="float-right p-1 rounded hover:bg-gray-200 focus:outline-none"
                              >
                                <Copy className="h-3 w-3" />
                              </button>
                              <pre className="whitespace-pre-wrap">{message.finalPrompt}</pre>
                            </div>
                          </details>
                        )}
                        
                        <hr className="border-gray-200" />
                      </div>
                    ))}
                  </div>
                </div>

                {/* Input Area */}
                <div className="flex gap-2">
                  <textarea
                    value={currentMessage}
                    onChange={(e) => setCurrentMessage(e.target.value)}
                    placeholder="Enter your prompt or question here..."
                    rows={3}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && e.ctrlKey) {
                        sendMessage();
                      }
                    }}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={isLoading || !currentMessage.trim()}
                    className="self-end px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </div>
                <p className="text-xs text-gray-500">
                  Press Ctrl+Enter to send • Model: GPT-OSS-120B • ~7 seconds response time
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}