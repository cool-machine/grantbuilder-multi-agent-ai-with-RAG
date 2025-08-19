/**
 * API service for crawler operations
 * Supports both mock and real crawling modes
 */

const BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-function-app.azurewebsites.net/api'
  : 'http://localhost:7071/api';

export type CrawlerMode = 'mock' | 'real';

export interface CrawlerConfig {
  request_delay?: number;
  max_concurrent_requests?: number;
  respect_robots_txt?: boolean;
}

export interface CrawlerResult {
  success: boolean;
  message: string;
  mode: CrawlerMode;
  results: {
    total_found: number;
    saved_to_database: number;
    duration_seconds: number;
    errors: string[];
  };
  opportunities: Array<{
    title: string;
    description: string;
    source: string;
    url: string;
    deadline?: string;
    amount?: string;
    eligibility?: string[];
    categories?: string[];
  }>;
}

export interface CrawlerStatus {
  success: boolean;
  status: {
    mode: CrawlerMode;
    database_connected: boolean;
    total_opportunities: number;
    sources: Record<string, number>;
    recent_additions: number;
    last_updated: string;
    config: CrawlerConfig;
  };
}

export interface CrawlerResultsResponse {
  success: boolean;
  count: number;
  limit_applied: number;
  opportunities: Array<{
    id: number;
    title: string;
    description: string;
    source: string;
    url: string;
    deadline?: string;
    amount?: string;
    eligibility: string[];
    categories: string[];
    extracted_date: string;
    created_at: string;
  }>;
}

class CrawlerAPI {
  private async makeRequest(endpoint: string, options: RequestInit = {}): Promise<any> {
    const response = await fetch(`${BASE_URL}/${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Start crawling with specified mode
   */
  async startCrawling(
    mode: CrawlerMode = 'mock', 
    config: CrawlerConfig = {}
  ): Promise<CrawlerResult> {
    return this.makeRequest(`CrawlerService?action=start&mode=${mode}`, {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }

  /**
   * Get crawler status
   */
  async getStatus(mode: CrawlerMode = 'mock'): Promise<CrawlerStatus> {
    return this.makeRequest(`CrawlerService?action=status&mode=${mode}`);
  }

  /**
   * Get crawling results from database
   */
  async getResults(params: {
    limit?: number;
    source?: string;
    query?: string;
  } = {}): Promise<CrawlerResultsResponse> {
    const queryParams = new URLSearchParams();
    queryParams.append('action', 'results');
    
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.source) queryParams.append('source', params.source);
    if (params.query) queryParams.append('query', params.query);

    return this.makeRequest(`CrawlerService?${queryParams.toString()}`);
  }

  /**
   * Update crawler configuration
   */
  async updateConfig(config: CrawlerConfig): Promise<any> {
    return this.makeRequest('CrawlerService?action=config', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }

  /**
   * Toggle between mock and real crawling modes
   */
  async toggleMode(currentMode: CrawlerMode): Promise<{
    success: boolean;
    message: string;
    previous_mode: CrawlerMode;
    current_mode: CrawlerMode;
    status: any;
  }> {
    return this.makeRequest('CrawlerService?action=toggle_mode', {
      method: 'POST',
      body: JSON.stringify({ current_mode: currentMode }),
    });
  }

  /**
   * Test connection to crawler service
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.getStatus();
      return true;
    } catch (error) {
      console.error('Crawler service connection failed:', error);
      return false;
    }
  }
}

export const crawlerAPI = new CrawlerAPI();