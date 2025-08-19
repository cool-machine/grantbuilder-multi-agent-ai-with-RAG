import { Grant } from '../contexts/GrantContext';

export interface CrawlSource {
  id: string;
  name: string;
  baseUrl: string;
  type: 'government' | 'eu' | 'foundation' | 'private';
  selectors: {
    grantList: string;
    title: string;
    description: string;
    amount: string;
    deadline: string;
    funder: string;
    detailsLink?: string;
  };
  pagination?: {
    nextButton: string;
    maxPages: number;
  };
  rateLimit: number; // milliseconds between requests
  lastCrawled?: string;
  isActive: boolean;
}

export interface CrawlResult {
  source: string;
  grants: Partial<Grant>[];
  errors: string[];
  timestamp: string;
  totalFound: number;
  newGrants: number;
  updatedGrants: number;
}

export class GrantCrawler {
  private sources: CrawlSource[] = [];
  private crawlHistory: CrawlResult[] = [];
  private isRunning = false;

  constructor() {
    this.initializeDefaultSources();
  }

  private initializeDefaultSources() {
    this.sources = [
      {
        id: 'data-gouv-fr',
        name: 'Data.gouv.fr',
        baseUrl: 'https://www.data.gouv.fr',
        type: 'government',
        selectors: {
          grantList: '.dataset-card',
          title: '.dataset-card__title',
          description: '.dataset-card__description',
          amount: '.dataset-card__amount',
          deadline: '.dataset-card__deadline',
          funder: '.dataset-card__organization'
        },
        rateLimit: 2000,
        isActive: true
      },
      {
        id: 'ec-europa-funding',
        name: 'European Commission Funding',
        baseUrl: 'https://ec.europa.eu/info/funding-tenders',
        type: 'eu',
        selectors: {
          grantList: '.funding-opportunity',
          title: '.opportunity-title',
          description: '.opportunity-description',
          amount: '.opportunity-budget',
          deadline: '.opportunity-deadline',
          funder: '.opportunity-programme'
        },
        rateLimit: 3000,
        isActive: true
      },
      {
        id: 'fondation-de-france',
        name: 'Fondation de France',
        baseUrl: 'https://www.fondationdefrance.org',
        type: 'foundation',
        selectors: {
          grantList: '.grant-item',
          title: '.grant-title',
          description: '.grant-description',
          amount: '.grant-amount',
          deadline: '.grant-deadline',
          funder: '.grant-funder'
        },
        rateLimit: 2500,
        isActive: true
      }
    ];
  }

  async crawlAllSources(): Promise<CrawlResult[]> {
    if (this.isRunning) {
      throw new Error('Crawling is already in progress');
    }

    this.isRunning = true;
    const results: CrawlResult[] = [];

    try {
      for (const source of this.sources.filter(s => s.isActive)) {
        console.log(`Starting crawl for ${source.name}...`);
        const result = await this.crawlSource(source);
        results.push(result);
        
        // Rate limiting between sources
        await this.delay(source.rateLimit);
      }
    } finally {
      this.isRunning = false;
    }

    this.crawlHistory.push(...results);
    return results;
  }

  async crawlSource(source: CrawlSource): Promise<CrawlResult> {
    const result: CrawlResult = {
      source: source.name,
      grants: [],
      errors: [],
      timestamp: new Date().toISOString(),
      totalFound: 0,
      newGrants: 0,
      updatedGrants: 0
    };

    try {
      // In a real implementation, you would use a headless browser like Puppeteer
      // For this demo, we'll simulate the crawling process
      const grants = await this.simulateCrawling(source);
      
      result.grants = grants;
      result.totalFound = grants.length;
      result.newGrants = grants.length; // In real implementation, compare with existing data
      
      // Update last crawled timestamp
      source.lastCrawled = new Date().toISOString();
      
    } catch (error) {
      result.errors.push(`Failed to crawl ${source.name}: ${error}`);
    }

    return result;
  }

  private async simulateCrawling(source: CrawlSource): Promise<Partial<Grant>[]> {
    // Simulate network delay
    await this.delay(1000);

    // Return mock data based on source type
    const mockGrants: Partial<Grant>[] = [];
    const grantCount = Math.floor(Math.random() * 10) + 5;

    for (let i = 0; i < grantCount; i++) {
      mockGrants.push({
        id: `${source.id}-${Date.now()}-${i}`,
        title: {
          fr: `Subvention ${source.name} ${i + 1}`,
          en: `${source.name} Grant ${i + 1}`
        },
        description: {
          fr: `Description de la subvention découverte sur ${source.name}`,
          en: `Grant description discovered from ${source.name}`
        },
        funder: source.name,
        amount: {
          min: Math.floor(Math.random() * 50000) + 5000,
          max: Math.floor(Math.random() * 500000) + 50000,
          currency: 'EUR'
        },
        deadline: new Date(Date.now() + Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        categories: this.getRandomCategories(),
        eligibility: ['association_loi_1901'],
        region: 'national',
        type: source.type,
        status: 'open' as const,
        sourceUrl: `${source.baseUrl}/grant-${i}`,
        lastUpdated: new Date().toISOString(),
        rating: Math.random() * 2 + 3,
        reviews: Math.floor(Math.random() * 50) + 5,
        difficulty: ['easy', 'medium', 'hard'][Math.floor(Math.random() * 3)] as 'easy' | 'medium' | 'hard'
      });
    }

    return mockGrants;
  }

  private getRandomCategories(): string[] {
    const allCategories = [
      'environment', 'education', 'social', 'health', 'culture', 
      'sport', 'innovation', 'research', 'technology', 'community'
    ];
    const count = Math.floor(Math.random() * 3) + 1;
    return allCategories.sort(() => 0.5 - Math.random()).slice(0, count);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Configuration methods
  addSource(source: CrawlSource): void {
    this.sources.push(source);
  }

  updateSource(id: string, updates: Partial<CrawlSource>): void {
    const index = this.sources.findIndex(s => s.id === id);
    if (index !== -1) {
      this.sources[index] = { ...this.sources[index], ...updates };
    }
  }

  removeSource(id: string): void {
    this.sources = this.sources.filter(s => s.id !== id);
  }

  getSources(): CrawlSource[] {
    return [...this.sources];
  }

  getCrawlHistory(): CrawlResult[] {
    return [...this.crawlHistory];
  }

  getStatus(): { isRunning: boolean; lastCrawl?: string; totalSources: number; activeSources: number } {
    return {
      isRunning: this.isRunning,
      lastCrawl: this.crawlHistory.length > 0 ? this.crawlHistory[this.crawlHistory.length - 1].timestamp : undefined,
      totalSources: this.sources.length,
      activeSources: this.sources.filter(s => s.isActive).length
    };
  }
}