import React, { useState, useEffect } from 'react';
import { Globe, Play, Pause, Calendar, Database, TrendingUp, AlertCircle, CheckCircle, Search, Settings } from 'lucide-react';
import { CrawlerManager } from '../../services/crawler/CrawlerManager';
import { useLanguage } from '../../contexts/LanguageContext';

const GlobalCrawlerDashboard: React.FC = () => {
  const { t } = useLanguage();
  const [crawlerManager] = useState(() => new CrawlerManager());
  const [isRunning, setIsRunning] = useState(false);
  const [crawlResults, setCrawlResults] = useState<any>(null);
  const [status, setStatus] = useState(crawlerManager.getCrawlerStatus());
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      setStatus(crawlerManager.getCrawlerStatus());
    }, 1000);

    return () => clearInterval(interval);
  }, [crawlerManager]);

  const handleStartGlobalCrawl = async () => {
    setIsRunning(true);
    setLogs(['🚀 Starting Global NGO Funding Crawler...']);
    
    try {
      const results = await crawlerManager.startGlobalCrawl();
      setCrawlResults(results);
      setLogs(prev => [...prev, results.summary]);
      
      if (results.success) {
        setLogs(prev => [...prev, `✅ Successfully found ${results.totalGrants} funding opportunities!`]);
      } else {
        setLogs(prev => [...prev, `❌ Crawl completed with errors: ${results.errors.length} issues`]);
      }
    } catch (error) {
      setLogs(prev => [...prev, `❌ Crawl failed: ${error}`]);
    } finally {
      setIsRunning(false);
    }
  };

  const handleScheduleCrawls = async () => {
    await crawlerManager.scheduleRegularCrawls();
    setLogs(prev => [...prev, '⏰ Scheduled daily crawls at 2 AM']);
  };

  const handleStopSchedule = () => {
    crawlerManager.stopScheduledCrawls();
    setLogs(prev => [...prev, '⏹️ Stopped scheduled crawls']);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-custom-blue to-blue-800 text-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center">
              <Globe className="w-8 h-8 mr-3" />
              {t('Global Web Crawler')}
            </h1>
            <p className="text-blue-200 mt-2">
              Crawl the entire web to discover NGO funding opportunities worldwide
            </p>
          </div>
          
          <div className="text-right">
            <div className="text-2xl font-bold">
              {crawlResults ? crawlResults.totalGrants.toLocaleString() : '0'}
            </div>
            <div className="text-blue-200">Grants Discovered</div>
          </div>
        </div>
      </div>

      {/* Control Panel */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Manual Crawl</h3>
          <p className="text-gray-600 mb-4">
            Start a comprehensive crawl of the entire web for NGO funding opportunities
          </p>
          <button
            onClick={handleStartGlobalCrawl}
            disabled={isRunning}
            className="w-full bg-custom-red text-white px-4 py-3 rounded-lg hover:bg-custom-red-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isRunning ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                {t('Crawling Web...')}
              </>
            ) : (
              <>
                <Play className="w-5 h-5 mr-2" />
                {t('Start Global Crawl')}
              </>
            )}
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Scheduled Crawls</h3>
          <p className="text-gray-600 mb-4">
            Automatically crawl for new funding opportunities daily
          </p>
          <div className="space-y-2">
            <button
              onClick={handleScheduleCrawls}
              disabled={status.isScheduled}
              className="w-full bg-custom-blue text-white px-4 py-2 rounded-lg hover:bg-custom-blue-light transition-colors disabled:opacity-50"
            >
              <Calendar className="w-4 h-4 mr-2 inline" />
              {status.isScheduled ? 'Scheduled' : t('Schedule Daily')}
            </button>
            {status.isScheduled && (
              <button
                onClick={handleStopSchedule}
                className="w-full bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition-colors"
              >
                <Pause className="w-4 h-4 mr-2 inline" />
                Stop Schedule
              </button>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Crawler Status</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">{t('Status')}</span>
              <span className={`flex items-center ${status.isRunning ? 'text-green-600' : 'text-gray-500'}`}>
                {status.isRunning ? <CheckCircle className="w-4 h-4 mr-1" /> : <AlertCircle className="w-4 h-4 mr-1" />}
                {status.isRunning ? t('Running') : t('Idle')}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Scheduled</span>
              <span className={status.isScheduled ? 'text-green-600' : 'text-gray-500'}>
                {status.isScheduled ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Total Crawls</span>
              <span className="font-medium">{status.totalCrawls}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Results Summary */}
      {crawlResults && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Latest Crawl Results</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="flex items-center">
                <CheckCircle className="w-6 h-6 text-green-600 mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Success Rate</p>
                  <p className="text-xl font-bold text-green-600">
                    {crawlResults.success ? '100%' : '0%'}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="flex items-center">
                <Database className="w-6 h-6 text-custom-blue mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Grants Found</p>
                  <p className="text-xl font-bold text-custom-blue">
                    {crawlResults.totalGrants.toLocaleString()}
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
                    {crawlResults.errors.length}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="flex items-center">
                <TrendingUp className="w-6 h-6 text-purple-600 mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Sources</p>
                  <p className="text-xl font-bold text-purple-600">Global</p>
                </div>
              </div>
            </div>
          </div>

          {crawlResults.processedGrants.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Sample Discovered Grants</h4>
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {crawlResults.processedGrants.slice(0, 5).map((grant: any, index: number) => (
                  <div key={index} className="border rounded-lg p-3">
                    <h5 className="font-medium text-gray-900">{grant.title.fr}</h5>
                    <p className="text-sm text-gray-600 mt-1">{grant.funder}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {grant.amount ? `${grant.amount.min.toLocaleString()} - ${grant.amount.max.toLocaleString()} ${grant.amount.currency}` : 'Amount TBD'}
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
      </div>

      {/* How to Use Guide */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-custom-blue mb-4">How to Use the Global Crawler</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">🚀 Manual Crawling</h4>
            <ul className="text-sm text-gray-700 space-y-1">
              <li>• Click "Start Global Crawl" to begin</li>
              <li>• Crawler searches major funding databases</li>
              <li>• Uses search engines to discover new sources</li>
              <li>• Processes and validates all found grants</li>
              <li>• Results are automatically integrated</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">⏰ Scheduled Crawling</h4>
            <ul className="text-sm text-gray-700 space-y-1">
              <li>• Enable daily automatic crawls</li>
              <li>• Runs at 2 AM to avoid peak hours</li>
              <li>• Keeps your database updated</li>
              <li>• Discovers new funding sources</li>
              <li>• Can be stopped/started anytime</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GlobalCrawlerDashboard;