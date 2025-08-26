import React from 'react';
import { MemoryStick, Cpu, HardDrive, Activity, AlertTriangle } from 'lucide-react';

interface SystemInfoData {
  ram_total_gb: number;
  ram_available_gb: number;
  ram_used_percent: number;
  disk_free_gb: number;
  cpu_percent: number;
  timestamp: string;
}

interface SystemInfoProps {
  systemInfo: SystemInfoData | null;
}

const SystemInfo: React.FC<SystemInfoProps> = ({ systemInfo }) => {
  if (!systemInfo) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            System Status
          </h3>
          <div className="text-center py-4">
            <div className="spinner mx-auto mb-2" />
            <p className="text-gray-500 text-sm">Loading system information...</p>
          </div>
        </div>
      </div>
    );
  }

  const getStatusColor = (percentage: number, reverse: boolean = false) => {
    if (reverse) {
      // For available resources (more = better)
      if (percentage > 70) return 'text-green-600';
      if (percentage > 30) return 'text-yellow-600';
      return 'text-red-600';
    } else {
      // For used resources (less = better)
      if (percentage < 50) return 'text-green-600';
      if (percentage < 80) return 'text-yellow-600';
      return 'text-red-600';
    }
  };

  const getProgressBarColor = (percentage: number) => {
    if (percentage < 50) return 'bg-green-500';
    if (percentage < 80) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const formatUptime = (timestamp: string) => {
    try {
      const time = new Date(timestamp);
      return time.toLocaleTimeString();
    } catch {
      return 'Unknown';
    }
  };

  const ramUsedGb = systemInfo.ram_total_gb - systemInfo.ram_available_gb;
  const ramAvailablePercent = (systemInfo.ram_available_gb / systemInfo.ram_total_gb) * 100;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            System Status
          </h3>
          <Activity className="h-5 w-5 text-green-500" />
        </div>

        <div className="space-y-4">
          {/* RAM Usage */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <MemoryStick className="h-4 w-4 text-blue-500" />
                <span className="text-sm font-medium text-gray-700">Memory</span>
              </div>
              <span className={`text-sm font-medium ${getStatusColor(systemInfo.ram_used_percent)}`}>
                {systemInfo.ram_used_percent.toFixed(1)}%
              </span>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${getProgressBarColor(systemInfo.ram_used_percent)}`}
                style={{ width: `${systemInfo.ram_used_percent}%` }}
              />
            </div>
            
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Used: {ramUsedGb.toFixed(1)} GB</span>
              <span>Available: {systemInfo.ram_available_gb.toFixed(1)} GB</span>
              <span>Total: {systemInfo.ram_total_gb.toFixed(1)} GB</span>
            </div>

            {systemInfo.ram_used_percent > 90 && (
              <div className="flex items-center space-x-2 mt-2 p-2 bg-red-50 rounded-md">
                <AlertTriangle className="h-4 w-4 text-red-500" />
                <span className="text-red-700 text-xs">Critical: Very low memory available</span>
              </div>
            )}
          </div>

          {/* CPU Usage */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Cpu className="h-4 w-4 text-green-500" />
                <span className="text-sm font-medium text-gray-700">CPU</span>
              </div>
              <span className={`text-sm font-medium ${getStatusColor(systemInfo.cpu_percent)}`}>
                {systemInfo.cpu_percent.toFixed(1)}%
              </span>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${getProgressBarColor(systemInfo.cpu_percent)}`}
                style={{ width: `${systemInfo.cpu_percent}%` }}
              />
            </div>
          </div>

          {/* Disk Space */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <HardDrive className="h-4 w-4 text-purple-500" />
                <span className="text-sm font-medium text-gray-700">Storage</span>
              </div>
              <span className="text-sm font-medium text-green-600">
                {systemInfo.disk_free_gb.toFixed(1)} GB free
              </span>
            </div>
          </div>

          {/* Last Updated */}
          <div className="pt-3 border-t border-gray-100">
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>Last updated</span>
              <span>{formatUptime(systemInfo.timestamp)}</span>
            </div>
          </div>
        </div>

        {/* Health Summary */}
        <div className="mt-4 p-3 bg-gray-50 rounded-md">
          <div className="text-xs text-gray-600">
            <strong>System Health:</strong>{' '}
            {systemInfo.ram_used_percent < 70 && systemInfo.cpu_percent < 70 && (
              <span className="text-green-600">Good</span>
            )}
            {(systemInfo.ram_used_percent >= 70 || systemInfo.cpu_percent >= 70) && 
             (systemInfo.ram_used_percent < 90 && systemInfo.cpu_percent < 90) && (
              <span className="text-yellow-600">Moderate Load</span>
            )}
            {(systemInfo.ram_used_percent >= 90 || systemInfo.cpu_percent >= 90) && (
              <span className="text-red-600">High Load</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemInfo;