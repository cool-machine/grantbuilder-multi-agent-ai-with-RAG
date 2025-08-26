import React, { useState, useEffect } from 'react';
import { Activity, Cpu, HardDrive, MemoryStick, Zap, Clock, BarChart3 } from 'lucide-react';
import ModelSelector from './components/ModelSelector';
import PromptTester from './components/PromptTester';
import ResultsPanel from './components/ResultsPanel';
import SystemInfo from './components/SystemInfo';
import ComparisonDashboard from './components/ComparisonDashboard';

interface SystemInfo {
  ram_total_gb: number;
  ram_available_gb: number;
  ram_used_percent: number;
  disk_free_gb: number;
  cpu_percent: number;
  timestamp: string;
}

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

function App() {
  const [currentView, setCurrentView] = useState('testing'); // 'testing' | 'comparison'
  const [models, setModels] = useState<Record<string, Model>>({});
  const [currentModel, setCurrentModel] = useState<string | null>(null);
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

  useEffect(() => {
    fetchModels();
    fetchSystemInfo();
    
    // Refresh system info every 30 seconds
    const interval = setInterval(fetchSystemInfo, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchModels = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/models`);
      const data = await response.json();
      setModels(data.models);
      setCurrentModel(data.current_model);
    } catch (error) {
      console.error('Error fetching models:', error);
    }
  };

  const fetchSystemInfo = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      const data = await response.json();
      setSystemInfo(data.system_info);
    } catch (error) {
      console.error('Error fetching system info:', error);
    }
  };

  const handleTestResult = (result: TestResult) => {
    setTestResults(prev => [result, ...prev.slice(0, 9)]); // Keep last 10 results
  };

  const getSystemHealthColor = () => {
    if (!systemInfo) return 'gray';
    if (systemInfo.ram_used_percent > 90) return 'red';
    if (systemInfo.ram_used_percent > 70) return 'yellow';
    return 'green';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Activity className="h-8 w-8 text-blue-600 mr-3" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">AI Model Testing Lab</h1>
                <p className="text-gray-600">Compare and evaluate language models</p>
              </div>
            </div>
            
            {/* System Status */}
            {systemInfo && (
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2">
                  <MemoryStick className={`h-5 w-5 text-${getSystemHealthColor()}-500`} />
                  <span className="text-sm font-medium">
                    RAM: {systemInfo.ram_available_gb.toFixed(1)}GB / {systemInfo.ram_total_gb}GB
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <Cpu className="h-5 w-5 text-blue-500" />
                  <span className="text-sm font-medium">CPU: {systemInfo.cpu_percent}%</span>
                </div>
              </div>
            )}
          </div>
          
          {/* Navigation */}
          <div className="flex space-x-1 mb-6">
            <button
              onClick={() => setCurrentView('testing')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                currentView === 'testing'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Zap className="h-4 w-4 inline mr-2" />
              Model Testing
            </button>
            <button
              onClick={() => setCurrentView('comparison')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                currentView === 'comparison'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <BarChart3 className="h-4 w-4 inline mr-2" />
              Comparison Dashboard
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'testing' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column - Model Selection */}
            <div className="lg:col-span-1">
              <ModelSelector
                models={models}
                currentModel={currentModel}
                onModelChange={setCurrentModel}
                apiBaseUrl={API_BASE_URL}
                isLoading={isLoading}
                setIsLoading={setIsLoading}
              />
              
              <div className="mt-6">
                <SystemInfo systemInfo={systemInfo} />
              </div>
            </div>

            {/* Middle Column - Testing Interface */}
            <div className="lg:col-span-1">
              <PromptTester
                currentModel={currentModel}
                models={models}
                apiBaseUrl={API_BASE_URL}
                onTestResult={handleTestResult}
                isLoading={isLoading}
                setIsLoading={setIsLoading}
              />
            </div>

            {/* Right Column - Results */}
            <div className="lg:col-span-1">
              <ResultsPanel results={testResults} />
            </div>
          </div>
        ) : (
          <ComparisonDashboard 
            results={testResults}
            models={models}
            apiBaseUrl={API_BASE_URL}
          />
        )}
      </div>
    </div>
  );
}

export default App;