import React from 'react';
import { Clock, Type, CheckCircle, XCircle, TrendingUp, MemoryStick } from 'lucide-react';

interface TestResult {
  success: boolean;
  response: string;
  model_name: string;
  generation_time: number;
  response_length: number;
  system_info: any;
  error?: string;
}

interface ResultsPanelProps {
  results: TestResult[];
}

const ResultsPanel: React.FC<ResultsPanelProps> = ({ results }) => {
  const formatTime = (seconds: number) => {
    return `${seconds.toFixed(2)}s`;
  };

  const formatLength = (length: number) => {
    return `${length} chars`;
  };

  const getResultClass = (success: boolean) => {
    return `result-card ${success ? 'success' : 'error'}`;
  };

  const truncateResponse = (text: string, maxLength: number = 200) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  if (results.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Test Results
          </h3>
          <div className="text-center py-8">
            <TrendingUp className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No test results yet</p>
            <p className="text-sm text-gray-400">
              Generate some responses to see results here
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Test Results ({results.length})
        </h3>

        <div className="space-y-4 max-h-96 overflow-y-auto">
          {results.map((result, index) => (
            <div key={index} className={getResultClass(result.success)}>
              {/* Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  {result.success ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-500" />
                  )}
                  <span className="font-medium text-gray-900">
                    {result.model_name}
                  </span>
                </div>
                <span className="text-xs text-gray-500">
                  {new Date().toLocaleTimeString()}
                </span>
              </div>

              {/* Metrics */}
              {result.success && (
                <div className="metrics-grid mb-4">
                  <div className="metric-item">
                    <div className="metric-value">
                      {formatTime(result.generation_time)}
                    </div>
                    <div className="metric-label">Generation Time</div>
                  </div>
                  <div className="metric-item">
                    <div className="metric-value">
                      {formatLength(result.response_length)}
                    </div>
                    <div className="metric-label">Response Length</div>
                  </div>
                </div>
              )}

              {/* Response or Error */}
              {result.success ? (
                <div className="bg-gray-50 rounded-md p-3">
                  <p className="response-text text-sm">
                    {truncateResponse(result.response)}
                  </p>
                  {result.response.length > 200 && (
                    <button className="text-blue-600 hover:text-blue-800 text-xs mt-2">
                      Show full response
                    </button>
                  )}
                </div>
              ) : (
                <div className="bg-red-50 rounded-md p-3">
                  <p className="text-red-700 text-sm">
                    Error: {result.error}
                  </p>
                </div>
              )}

              {/* System Info */}
              {result.success && result.system_info && (
                <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
                  <div className="flex items-center space-x-4">
                    <span className="flex items-center space-x-1">
                      <MemoryStick className="h-3 w-3" />
                      <span>
                        RAM: {result.system_info.final?.ram_used_percent?.toFixed(1)}%
                      </span>
                    </span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Summary Stats */}
        {results.length > 0 && (
          <div className="mt-6 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-lg font-semibold text-green-600">
                  {results.filter(r => r.success).length}
                </div>
                <div className="text-xs text-gray-500">Successful</div>
              </div>
              <div>
                <div className="text-lg font-semibold text-red-600">
                  {results.filter(r => !r.success).length}
                </div>
                <div className="text-xs text-gray-500">Failed</div>
              </div>
              <div>
                <div className="text-lg font-semibold text-blue-600">
                  {results.filter(r => r.success).length > 0 
                    ? formatTime(
                        results.filter(r => r.success)
                          .reduce((acc, r) => acc + r.generation_time, 0) / 
                        results.filter(r => r.success).length
                      )
                    : '0s'
                  }
                </div>
                <div className="text-xs text-gray-500">Avg Time</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsPanel;