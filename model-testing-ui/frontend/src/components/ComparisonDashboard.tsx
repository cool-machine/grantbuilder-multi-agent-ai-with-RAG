import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Clock, FileText, Zap } from 'lucide-react';

interface TestResult {
  success: boolean;
  response: string;
  model_name: string;
  generation_time: number;
  response_length: number;
  system_info: any;
  error?: string;
}

interface Model {
  id: string;
  name: string;
  size: string;
  type: string;
  description: string;
}

interface ComparisonDashboardProps {
  results: TestResult[];
  models: Record<string, Model>;
  apiBaseUrl: string;
}

const ComparisonDashboard: React.FC<ComparisonDashboardProps> = ({
  results,
  models
}) => {
  const [selectedMetric, setSelectedMetric] = useState<'time' | 'length' | 'success'>('time');

  // Process results for visualization
  const processedResults = React.useMemo(() => {
    const modelStats: Record<string, {
      name: string;
      totalTests: number;
      successfulTests: number;
      avgTime: number;
      avgLength: number;
      successRate: number;
      times: number[];
      lengths: number[];
    }> = {};

    results.forEach(result => {
      if (!modelStats[result.model_name]) {
        modelStats[result.model_name] = {
          name: result.model_name,
          totalTests: 0,
          successfulTests: 0,
          avgTime: 0,
          avgLength: 0,
          successRate: 0,
          times: [],
          lengths: []
        };
      }

      const stats = modelStats[result.model_name];
      stats.totalTests++;

      if (result.success) {
        stats.successfulTests++;
        stats.times.push(result.generation_time);
        stats.lengths.push(result.response_length);
      }
    });

    // Calculate averages
    Object.values(modelStats).forEach(stats => {
      stats.avgTime = stats.times.length > 0 
        ? stats.times.reduce((a, b) => a + b, 0) / stats.times.length 
        : 0;
      stats.avgLength = stats.lengths.length > 0 
        ? stats.lengths.reduce((a, b) => a + b, 0) / stats.lengths.length 
        : 0;
      stats.successRate = stats.totalTests > 0 
        ? (stats.successfulTests / stats.totalTests) * 100 
        : 0;
    });

    return Object.values(modelStats);
  }, [results]);

  const chartData = processedResults.map(stats => ({
    name: stats.name.replace(/\s+/g, '\n'), // Break long names
    time: Number(stats.avgTime.toFixed(2)),
    length: Math.round(stats.avgLength),
    success: Number(stats.successRate.toFixed(1)),
    tests: stats.totalTests
  }));

  const pieData = processedResults.map(stats => ({
    name: stats.name,
    value: stats.successfulTests,
    total: stats.totalTests
  }));

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  if (results.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div className="text-center">
          <TrendingUp className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            No Comparison Data Yet
          </h3>
          <p className="text-gray-600">
            Run tests with different models to see performance comparisons here.
          </p>
        </div>
      </div>
    );
  }

  const getMetricTitle = () => {
    switch (selectedMetric) {
      case 'time': return 'Average Generation Time (seconds)';
      case 'length': return 'Average Response Length (characters)';
      case 'success': return 'Success Rate (%)';
      default: return '';
    }
  };

  const getMetricColor = () => {
    switch (selectedMetric) {
      case 'time': return '#8884d8';
      case 'length': return '#82ca9d';
      case 'success': return '#ffc658';
      default: return '#8884d8';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-2">Model Performance Comparison</h2>
        <p className="text-gray-600">
          Analyzing {results.length} test results across {processedResults.length} models
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-blue-500 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">Fastest Model</p>
              <p className="text-lg font-semibold text-gray-900">
                {processedResults.length > 0 
                  ? processedResults.reduce((prev, curr) => 
                      prev.avgTime < curr.avgTime ? prev : curr
                    ).name.split(' ')[0]
                  : 'N/A'
                }
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <FileText className="h-8 w-8 text-green-500 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">Most Verbose</p>
              <p className="text-lg font-semibold text-gray-900">
                {processedResults.length > 0 
                  ? processedResults.reduce((prev, curr) => 
                      prev.avgLength > curr.avgLength ? prev : curr
                    ).name.split(' ')[0]
                  : 'N/A'
                }
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <Zap className="h-8 w-8 text-yellow-500 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">Most Reliable</p>
              <p className="text-lg font-semibold text-gray-900">
                {processedResults.length > 0 
                  ? processedResults.reduce((prev, curr) => 
                      prev.successRate > curr.successRate ? prev : curr
                    ).name.split(' ')[0]
                  : 'N/A'
                }
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-purple-500 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">Total Tests</p>
              <p className="text-lg font-semibold text-gray-900">
                {results.length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Performance Metrics</h3>
            <select
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value as 'time' | 'length' | 'success')}
              className="text-sm border border-gray-300 rounded-md px-2 py-1"
            >
              <option value="time">Generation Time</option>
              <option value="length">Response Length</option>
              <option value="success">Success Rate</option>
            </select>
          </div>
          
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="name" 
                fontSize={12}
                interval={0}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis fontSize={12} />
              <Tooltip />
              <Bar 
                dataKey={selectedMetric} 
                fill={getMetricColor()} 
                name={getMetricTitle()}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Success Rate Pie Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Success Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({name, value}) => `${name.split(' ')[0]}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value, name, props) => [
                `${value} successful tests out of ${props.payload.total}`,
                props.payload.name
              ]} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Detailed Statistics</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Model
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tests
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Success Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Length
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {processedResults.map((stats, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {stats.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {stats.successfulTests} / {stats.totalTests}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      stats.successRate >= 90 ? 'bg-green-100 text-green-800' :
                      stats.successRate >= 70 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {stats.successRate.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {stats.avgTime.toFixed(2)}s
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {Math.round(stats.avgLength)} chars
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ComparisonDashboard;