import React, { useState, useEffect } from 'react';
import { Play, Pause, Settings, Database, AlertCircle, CheckCircle, Clock, Globe } from 'lucide-react';
import { GrantCrawler, CrawlSource, CrawlResult } from '../../services/crawler/GrantCrawler';

const CrawlerDashboard: React.FC = () => {
  const [crawler] = useState(() => new GrantCrawler());
  const [crawlStatus, setCrawlStatus] = useState(crawler.getStatus());
  const [sources, setSources] = useState<CrawlSource[]>(crawler.getSources());
  const [crawlHistory, setCrawlHistory] = useState<CrawlResult[]>(crawler.getCrawlHistory());
  const [isRunning, setIsRunning] = useState(false);
  const [selectedSource, setSelectedSource] = useState<string>('');

  useEffect(() => {
    const interval = setInterval(() => {
      setCrawlStatus(crawler.getStatus());
      setSources(crawler.getSources());
      setCrawlHistory(crawler.getCrawlHistory());
    }, 1000);

    return () => clearInterval(interval);
  }, [crawler]);

  const handleStartCrawl = async () => {
    setIsRunning(true);
    try {
      const results = await crawler.crawlAllSources();
      console.log('Crawl completed:', results);
    } catch (error) {
      console.error('Crawl failed:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const handleToggleSource = (sourceId: string) => {
    const source = sources.find(s => s.id === sourceId);
    if (source) {
      crawler.updateSource(sourceId, { isActive: !source.isActive });
      setSources(crawler.getSources());
    }
  };

  const getStatusIcon = (isActive: boolean, lastCrawled?: string) => {
    if (!isActive) return <Pause className="w-4 h-4 text-gray-400" />;
    if (!lastCrawled) return <Clock className="w-4 h-4 text-yellow-500" />;
    
    const lastCrawlDate = new Date(lastCrawled);
    const hoursSinceLastCrawl = (Date.now() - lastCrawlDate.getTime()) / (1000 * 60 * 60);
    
    if (hoursSinceLastCrawl < 24) return <CheckCircle className="w-4 h-4 text-green-500" />;
    if (hoursSinceLastCrawl < 72) return <AlertCircle className="w-4 h-4 text-yellow-500" />;
    return <AlertCircle className="w-4 h-4 text-red-500" />;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Web Crawler Dashboard</h2>
            <p className="text-gray-600">Manage automated grant data collection</p>
          </div>
          
          <button
            onClick={handleStartCrawl}
            disabled={isRunning || crawlStatus.isRunning}
            className="bg-custom-red text-white px-6 py-3 rounded-lg hover:bg-custom-red-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {isRunning || crawlStatus.isRunning ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Crawling...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Start Crawl
              </>
            )}
          </button>
        </div>

        {/* Status Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Database className="w-6 h-6 text-custom-blue mr-3" />
              <div>
                <p className="text-sm text-gray-600">Total Sources</p>
                <p className="text-xl font-bold text-custom-blue">{crawlStatus.totalSources}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center">
              <CheckCircle className="w-6 h-6 text-green-600 mr-3" />
              <div>
                <p className="text-sm text-gray-600">Active Sources</p>
                <p className="text-xl font-bold text-green-600">{crawlStatus.activeSources}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Clock className="w-6 h-6 text-yellow-600 mr-3" />
              <div>
                <p className="text-sm text-gray-600">Last Crawl</p>
                <p className="text-sm font-medium text-yellow-600">
                  {crawlStatus.lastCrawl 
                    ? new Date(crawlStatus.lastCrawl).toLocaleDateString('fr-FR')
                    : 'Never'
                  }
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-red-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Globe className="w-6 h-6 text-custom-red mr-3" />
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <p className="text-sm font-medium text-custom-red">
                  {crawlStatus.isRunning ? 'Running' : 'Idle'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Sources Management */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Crawl Sources</h3>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Source
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Crawled
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rate Limit
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sources.map((source) => (
                <tr key={source.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{source.name}</div>
                      <div className="text-sm text-gray-500">{source.baseUrl}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      source.type === 'government' ? 'bg-blue-100 text-blue-800' :
                      source.type === 'eu' ? 'bg-purple-100 text-purple-800' :
                      source.type === 'foundation' ? 'bg-green-100 text-green-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {source.type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getStatusIcon(source.isActive, source.lastCrawled)}
                      <span className="ml-2 text-sm text-gray-900">
                        {source.isActive ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {source.lastCrawled 
                      ? new Date(source.lastCrawled).toLocaleDateString('fr-FR')
                      : 'Never'
                    }
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {source.rateLimit}ms
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleToggleSource(source.id)}
                        className={`${
                          source.isActive 
                            ? 'text-red-600 hover:text-red-900' 
                            : 'text-green-600 hover:text-green-900'
                        }`}
                      >
                        {source.isActive ? 'Disable' : 'Enable'}
                      </button>
                      <button className="text-custom-blue hover:text-custom-blue-light">
                        <Settings className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Crawl History */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Recent Crawl Results</h3>
        
        {crawlHistory.length === 0 ? (
          <p className="text-gray-600">No crawl history available. Start your first crawl to see results.</p>
        ) : (
          <div className="space-y-4">
            {crawlHistory.slice(-5).reverse().map((result, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{result.source}</h4>
                  <span className="text-sm text-gray-500">
                    {new Date(result.timestamp).toLocaleString('fr-FR')}
                  </span>
                </div>
                
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Found: </span>
                    <span className="font-medium text-green-600">{result.totalFound}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">New: </span>
                    <span className="font-medium text-blue-600">{result.newGrants}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Errors: </span>
                    <span className="font-medium text-red-600">{result.errors.length}</span>
                  </div>
                </div>
                
                {result.errors.length > 0 && (
                  <div className="mt-2">
                    <details className="text-sm">
                      <summary className="text-red-600 cursor-pointer">View Errors</summary>
                      <ul className="mt-1 text-red-600 list-disc list-inside">
                        {result.errors.map((error, errorIndex) => (
                          <li key={errorIndex}>{error}</li>
                        ))}
                      </ul>
                    </details>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CrawlerDashboard;