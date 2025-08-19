import { WebCrawler, CrawlResult } from './WebCrawler';
import { DataProcessor } from './DataProcessor';
import { Grant } from '../../contexts/GrantContext';

export interface CrawlerConfig {
  maxConcurrentCrawls: number;
  respectRobotsTxt: boolean;
  userAgent: string;
  defaultRateLimit: number;
  maxPagesPerSite: number;
  enableDeepCrawling: boolean;
}

export class CrawlerManager {
  private crawler: WebCrawler;
  private processor: DataProcessor;
  private config: CrawlerConfig;
  private crawlHistory: CrawlResult[] = [];
  private isScheduled = false;

  constructor(config: Partial<CrawlerConfig> = {}) {
    this.config = {
      maxConcurrentCrawls: 5,
      respectRobotsTxt: true,
      userAgent: 'GrantSeeker-Bot/1.0 (https://grantseeker.fr; Educational Purpose)',
      defaultRateLimit: 2000,
      maxPagesPerSite: 50,
      enableDeepCrawling: true,
      ...config
    };

    this.crawler = new WebCrawler();
    this.processor = new DataProcessor();
  }

  async startGlobalCrawl(): Promise<{
    success: boolean;
    totalGrants: number;
    processedGrants: Grant[];
    errors: string[];
    summary: string;
  }> {
    console.log('🚀 Starting Global NGO Funding Crawler...');
    console.log('📊 This will search the entire web for funding opportunities!');

    try {
      // Start the comprehensive web crawl
      const results = await this.crawler.crawlEntireWeb();
      this.crawlHistory.push(...results);

      // Process and validate all discovered grants
      const allRawGrants = results.flatMap(result => result.grants);
      const processedGrants: Grant[] = [];
      const errors: string[] = [];

      console.log(`🔄 Processing ${allRawGrants.length} discovered funding opportunities...`);

      for (const rawGrant of allRawGrants) {
        try {
          const processed = this.processor.processRawData(rawGrant, 'web_crawl');
          const validation = this.processor.validateGrant(processed);

          if (validation.isValid && processed.title && processed.description) {
            processedGrants.push(processed as Grant);
          } else {
            errors.push(`Invalid grant: ${validation.errors.join(', ')}`);
          }
        } catch (error) {
          errors.push(`Processing error: ${error}`);
        }
      }

      // Remove duplicates
      const { unique: uniqueGrants } = this.processor.findDuplicates(processedGrants);

      const summary = this.generateCrawlSummary(results, uniqueGrants.length, errors.length);
      console.log(summary);

      return {
        success: true,
        totalGrants: uniqueGrants.length,
        processedGrants: uniqueGrants as Grant[],
        errors,
        summary
      };

    } catch (error) {
      console.error('❌ Global crawl failed:', error);
      return {
        success: false,
        totalGrants: 0,
        processedGrants: [],
        errors: [error instanceof Error ? error.message : String(error)],
        summary: 'Crawl failed due to technical error'
      };
    }
  }

  async scheduleRegularCrawls(): Promise<void> {
    if (this.isScheduled) {
      console.log('⏰ Crawler is already scheduled');
      return;
    }

    this.isScheduled = true;
    console.log('⏰ Starting scheduled crawling...');

    // Schedule daily crawls at 2 AM
    const scheduleDaily = () => {
      const now = new Date();
      const tomorrow2AM = new Date(now);
      tomorrow2AM.setDate(tomorrow2AM.getDate() + 1);
      tomorrow2AM.setHours(2, 0, 0, 0);

      const msUntil2AM = tomorrow2AM.getTime() - now.getTime();

      setTimeout(async () => {
        console.log('🕐 Running scheduled daily crawl...');
        await this.startGlobalCrawl();
        
        // Schedule next crawl
        setInterval(async () => {
          console.log('🕐 Running scheduled daily crawl...');
          await this.startGlobalCrawl();
        }, 24 * 60 * 60 * 1000); // Every 24 hours
        
      }, msUntil2AM);
    };

    scheduleDaily();
  }

  stopScheduledCrawls(): void {
    this.isScheduled = false;
    console.log('⏹️ Scheduled crawling stopped');
  }

  private generateCrawlSummary(results: CrawlResult[], totalGrants: number, errorCount: number): string {
    const sourcesSummary = results.map(r => `${r.target}: ${r.totalFound} grants`).join('\n');
    
    return `
🎯 GLOBAL NGO FUNDING CRAWL COMPLETE
=====================================
📊 Sources Crawled: ${results.length}
💰 Total Grants Found: ${totalGrants}
❌ Processing Errors: ${errorCount}
⏱️ Crawl Duration: ${this.getCrawlDuration(results)}

📋 Sources Summary:
${sourcesSummary}

🌍 Coverage: Global (Government, EU, Foundations, Private)
🎯 Target: NGOs, Nonprofits, Charities, Civil Society
✅ Status: Ready for use in Grant Seeker platform
    `;
  }

  private getCrawlDuration(results: CrawlResult[]): string {
    if (results.length === 0) return '0 seconds';
    
    const totalTime = results.reduce((sum, result) => sum + result.processingTime, 0);
    const minutes = Math.floor(totalTime / 60000);
    const seconds = Math.floor((totalTime % 60000) / 1000);
    
    return `${minutes}m ${seconds}s`;
  }

  // Public API methods
  getCrawlHistory(): CrawlResult[] {
    return [...this.crawlHistory];
  }

  getCrawlerStatus(): {
    isRunning: boolean;
    isScheduled: boolean;
    totalCrawls: number;
    lastCrawl?: string;
  } {
    const status = this.crawler.getStatus();
    return {
      isRunning: status.isRunning,
      isScheduled: this.isScheduled,
      totalCrawls: this.crawlHistory.length,
      lastCrawl: this.crawlHistory.length > 0 ? 
        this.crawlHistory[this.crawlHistory.length - 1].timestamp : undefined
    };
  }

  addCustomSource(name: string, url: string, selectors: any): void {
    this.crawler.addTarget({
      id: `custom-${Date.now()}`,
      name,
      baseUrl: url,
      searchQueries: ['grants', 'funding'],
      type: 'private',
      selectors,
      rateLimit: this.config.defaultRateLimit,
      isActive: true
    });
  }

  getDiscoveredSources(): string[] {
    return this.crawler.getTargets().map(t => t.name);
  }
}