import React, { useState, useEffect } from 'react';
import { 
  Globe, Play, Pause, Calendar, Database, TrendingUp, AlertCircle, 
  CheckCircle, Settings, ToggleLeft, ToggleRight, Zap, Cloud 
} from 'lucide-react';
import { crawlerAPI, CrawlerMode, CrawlerResult, CrawlerStatus } from '../../services/api/crawlerAPI';
import { useLanguage } from '../../contexts/LanguageContext';

const EnhancedCrawlerDashboard: React.FC = () => {
  const { t } = useLanguage();
  const [mode, setMode] = useState<CrawlerMode>('mock');
  const [isRunning, setIsRunning] = useState(false);
  const [crawlResults, setCrawlResults] = useState<CrawlerResult | null>(null);
  const [status, setStatus] = useState<CrawlerStatus | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);

  useEffect(() => {
    // Test connection and get initial status
    const initializeDashboard = async () => {
      try {
        const connected = await crawlerAPI.testConnection();
        setIsConnected(connected);
        
        if (connected) {
          const statusResult = await crawlerAPI.getStatus(mode);
          setStatus(statusResult);
        }
      } catch (error) {
        console.error('Failed to initialize dashboard:', error);
        setLogs(prev => [...prev, `❌ Connection failed: ${error}`]);
      }
    };

    initializeDashboard();
  }, [mode]);

  const handleStartCrawling = async () => {
    setIsRunning(true);
    setLogs(prev => [...prev, `🚀 Starting ${mode} crawler...`]);
    
    try {
      const config = {
        request_delay: 2.0,
        max_concurrent_requests: 5,
        respect_robots_txt: true
      };

      const results = await crawlerAPI.startCrawling(mode, config);
      setCrawlResults(results);
      
      setLogs(prev => [...prev, results.message]);
      setLogs(prev => [...prev, `📊 Found: ${results.results.total_found} opportunities`]);
      setLogs(prev => [...prev, `💾 Saved: ${results.results.saved_to_database} to database`]);
      setLogs(prev => [...prev, `⏱️ Duration: ${results.results.duration_seconds.toFixed(2)}s`]);
      
      if (results.results.errors.length > 0) {
        setLogs(prev => [...prev, `⚠️ Errors: ${results.results.errors.length}`]);
      }

      // Refresh status after crawling
      const statusResult = await crawlerAPI.getStatus(mode);
      setStatus(statusResult);
      
    } catch (error) {
      setLogs(prev => [...prev, `❌ Crawl failed: ${error}`]);
    } finally {
      setIsRunning(false);
    }
  };

  const handleToggleMode = async () => {
    try {
      const response = await crawlerAPI.toggleMode(mode);
      const newMode = response.current_mode;
      
      setMode(newMode);
      setLogs(prev => [...prev, response.message]);
      
      // Get status for new mode
      const statusResult = await crawlerAPI.getStatus(newMode);
      setStatus(statusResult);
      
    } catch (error) {
      setLogs(prev => [...prev, `❌ Failed to toggle mode: ${error}`]);
    }
  };

  const ModeToggle = () => (
    <div className="flex items-center space-x-3 bg-gray-50 rounded-lg p-4">
      <div className="flex items-center space-x-2">
        <Zap className={`w-5 h-5 ${mode === 'mock' ? 'text-blue-600' : 'text-gray-400'}`} />
        <span className={`font-medium ${mode === 'mock' ? 'text-blue-900' : 'text-gray-500'}`}>
          Mock Mode
        </span>
      </div>
      
      <button
        onClick={handleToggleMode}
        className="relative inline-flex items-center cursor-pointer"
        disabled={isRunning}
      >
        {mode === 'mock' ? (
          <ToggleLeft className="w-8 h-8 text-blue-600 hover:text-blue-700" />
        ) : (
          <ToggleRight className="w-8 h-8 text-green-600 hover:text-green-700" />
        )}
      </button>
      
      <div className="flex items-center space-x-2">
        <Cloud className={`w-5 h-5 ${mode === 'real' ? 'text-green-600' : 'text-gray-400'}`} />
        <span className={`font-medium ${mode === 'real' ? 'text-green-900' : 'text-gray-500'}`}>
          Real Mode
        </span>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-custom-blue to-blue-800 text-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center">
              <Globe className="w-8 h-8 mr-3" />
              {t('Enhanced Crawler Dashboard')}
            </h1>
            <p className="text-blue-200 mt-2">
              Choose between mock simulation and real web crawling
            </p>
            <div className="mt-3">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                isConnected 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                <div className={`w-2 h-2 rounded-full mr-2 ${
                  isConnected ? 'bg-green-400' : 'bg-red-400'
                }`}></div>
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-2xl font-bold">
              {status?.status.total_opportunities?.toLocaleString() || '0'}
            </div>
            <div className="text-blue-200">Total Opportunities</div>
            <div className="text-lg font-medium mt-1">
              {crawlResults?.results.total_found || 0} Recently Found
            </div>
          </div>
        </div>
      </div>

      {/* Mode Toggle */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Crawler Mode</h3>
        <ModeToggle />
        <div className="mt-4 text-sm text-gray-600">
          <p>
            <strong>Mock Mode:</strong> Uses simulated data for testing and development. 
            Fast execution with realistic sample grants.
          </p>
          <p className="mt-2">
            <strong>Real Mode:</strong> Crawls actual funding websites. 
            Takes longer but provides real, up-to-date opportunities.
          </p>
        </div>
      </div>

      {/* Control Panel */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {mode === 'mock' ? 'Mock Crawl' : 'Real Crawl'}
          </h3>
          <p className="text-gray-600 mb-4">
            {mode === 'mock' 
              ? 'Generate realistic sample funding opportunities for testing'
              : 'Crawl actual funding websites for real opportunities'
            }
          </p>
          <button
            onClick={handleStartCrawling}
            disabled={isRunning || !isConnected}
            className="w-full bg-custom-red text-white px-4 py-3 rounded-lg hover:bg-custom-red-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isRunning ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                {mode === 'mock' ? 'Generating...' : 'Crawling...'}
              </>
            ) : (
              <>
                <Play className="w-5 h-5 mr-2" />
                {mode === 'mock' ? 'Start Mock Crawl' : 'Start Real Crawl'}
              </>
            )}
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Status & Statistics</h3>
          {status ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Current Mode</span>
                <span className={`font-medium ${
                  status.status.mode === 'mock' ? 'text-blue-600' : 'text-green-600'
                }`}>
                  {status.status.mode.toUpperCase()}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Database</span>
                <span className={`flex items-center ${
                  status.status.database_connected ? 'text-green-600' : 'text-red-600'
                }`}>
                  {status.status.database_connected ? (
                    <CheckCircle className="w-4 h-4 mr-1" />
                  ) : (
                    <AlertCircle className="w-4 h-4 mr-1" />
                  )}
                  {status.status.database_connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Recent Additions</span>
                <span className="font-medium">{status.status.recent_additions}</span>
              </div>
            </div>
          ) : (
            <div className="text-gray-500">Loading status...</div>
          )}
        </div>
      </div>

      {/* Results Summary */}
      {crawlResults && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            Latest Crawl Results ({crawlResults.mode} mode)
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="flex items-center">
                <CheckCircle className="w-6 h-6 text-green-600 mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Success</p>
                  <p className="text-xl font-bold text-green-600">
                    {crawlResults.success ? 'Yes' : 'No'}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="flex items-center">
                <Database className="w-6 h-6 text-custom-blue mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Found</p>
                  <p className="text-xl font-bold text-custom-blue">
                    {crawlResults.results.total_found}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="flex items-center">
                <TrendingUp className="w-6 h-6 text-purple-600 mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Saved</p>
                  <p className="text-xl font-bold text-purple-600">
                    {crawlResults.results.saved_to_database}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-yellow-50 p-4 rounded-lg">
              <div className="flex items-center">
                <AlertCircle className="w-6 h-6 text-yellow-600 mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Errors</p>
                  <p className="text-xl font-bold text-yellow-600">
                    {crawlResults.results.errors.length}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {crawlResults.opportunities.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Sample Opportunities</h4>
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {crawlResults.opportunities.slice(0, 5).map((opportunity, index) => (
                  <div key={index} className="border rounded-lg p-3">
                    <h5 className="font-medium text-gray-900">{opportunity.title}</h5>
                    <p className="text-sm text-gray-600 mt-1">{opportunity.source}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {opportunity.amount || 'Amount TBD'}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Live Logs */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Crawler Logs</h3>
        <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm max-h-64 overflow-y-auto">
          {logs.length === 0 ? (
            <p>No logs yet. Start a crawl to see activity...</p>
          ) : (
            logs.map((log, index) => (
              <div key={index} className="mb-1">
                <span className="text-gray-500">[{new Date().toLocaleTimeString()}]</span> {log}
              </div>
            ))
          )}
        </div>
        <button
          onClick={() => setLogs([])}
          className="mt-2 text-sm text-gray-500 hover:text-gray-700"
        >
          Clear Logs
        </button>
      </div>
    </div>
  );
};

export default EnhancedCrawlerDashboard;