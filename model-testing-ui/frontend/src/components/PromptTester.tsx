import React, { useState, useEffect } from 'react';
import { Send, RefreshCw, FileText, Lightbulb, Code, TrendingUp, BookOpen } from 'lucide-react';

interface Model {
  id: string;
  name: string;
  size: string;
  type: string;
  description: string;
}

interface TestResult {
  success: boolean;
  response: string;
  model_name: string;
  generation_time: number;
  response_length: number;
  system_info: any;
  error?: string;
}

interface PromptTesterProps {
  currentModel: string | null;
  models: Record<string, Model>;
  apiBaseUrl: string;
  onTestResult: (result: TestResult) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

interface Prompt {
  name: string;
  prompt: string;
}

const PromptTester: React.FC<PromptTesterProps> = ({
  currentModel,
  models,
  apiBaseUrl,
  onTestResult,
  isLoading,
  setIsLoading
}) => {
  const [prompt, setPrompt] = useState('');
  const [predefinedPrompts, setPredefinedPrompts] = useState<Record<string, Prompt>>({});
  const [maxTokens, setMaxTokens] = useState(100);
  const [temperature, setTemperature] = useState(0.7);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    fetchPrompts();
  }, []);

  const fetchPrompts = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/prompts`);
      const data = await response.json();
      setPredefinedPrompts(data.prompts);
    } catch (error) {
      console.error('Error fetching prompts:', error);
    }
  };

  const handleGenerate = async () => {
    if (!currentModel || !prompt.trim() || isGenerating) return;

    setIsGenerating(true);
    setIsLoading(true);

    try {
      const response = await fetch(`${apiBaseUrl}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt.trim(),
          max_tokens: maxTokens,
          temperature: temperature,
        }),
      });

      const data = await response.json();
      onTestResult(data);

    } catch (error) {
      const errorResult: TestResult = {
        success: false,
        response: '',
        model_name: models[currentModel]?.name || 'Unknown',
        generation_time: 0,
        response_length: 0,
        system_info: null,
        error: 'Network error: Could not connect to backend'
      };
      onTestResult(errorResult);
    } finally {
      setIsGenerating(false);
      setIsLoading(false);
    }
  };

  const handlePromptSelect = (promptKey: string) => {
    const selectedPrompt = predefinedPrompts[promptKey];
    if (selectedPrompt) {
      setPrompt(selectedPrompt.prompt);
    }
  };

  const getPromptIcon = (key: string) => {
    const iconMap: Record<string, React.ReactElement> = {
      grant_writing: <FileText className="h-4 w-4" />,
      creative_writing: <Lightbulb className="h-4 w-4" />,
      code_generation: <Code className="h-4 w-4" />,
      business_plan: <TrendingUp className="h-4 w-4" />,
      technical_explanation: <BookOpen className="h-4 w-4" />,
    };
    return iconMap[key] || <FileText className="h-4 w-4" />;
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Prompt Testing
        </h3>

        {/* Predefined Prompts */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            Quick Test Prompts
          </h4>
          <div className="grid grid-cols-1 gap-2">
            {Object.entries(predefinedPrompts).map(([key, promptObj]) => (
              <button
                key={key}
                onClick={() => handlePromptSelect(key)}
                className="flex items-center space-x-2 p-2 text-left text-sm bg-gray-50 hover:bg-gray-100 rounded-md transition-colors"
                disabled={isGenerating}
              >
                {getPromptIcon(key)}
                <span>{promptObj.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Custom Prompt Input */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Custom Prompt
          </label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter your prompt here..."
            className="prompt-textarea"
            disabled={isGenerating}
          />
        </div>

        {/* Settings */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Tokens: {maxTokens}
            </label>
            <input
              type="range"
              min="10"
              max="500"
              value={maxTokens}
              onChange={(e) => setMaxTokens(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              disabled={isGenerating}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Temperature: {temperature}
            </label>
            <input
              type="range"
              min="0.1"
              max="1.5"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              disabled={isGenerating}
            />
          </div>
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={!currentModel || !prompt.trim() || isGenerating}
          className={`w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-md font-medium transition-colors ${
            !currentModel || !prompt.trim() || isGenerating
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {isGenerating ? (
            <>
              <div className="spinner" />
              <span>Generating...</span>
            </>
          ) : (
            <>
              <Send className="h-4 w-4" />
              <span>Generate Response</span>
            </>
          )}
        </button>

        {!currentModel && (
          <p className="text-sm text-gray-500 text-center mt-3">
            Select a model to start testing
          </p>
        )}
      </div>
    </div>
  );
};

export default PromptTester;