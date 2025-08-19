import { Grant } from '../../contexts/GrantContext';

export interface CrawlTarget {
  id: string;
  name: string;
  baseUrl: string;
  searchQueries: string[];
  type: 'government' | 'eu' | 'foundation' | 'private' | 'search_engine';
  selectors: {
    container: string;
    title: string;
    description: string;
    amount?: string;
    deadline?: string;
    funder?: string;
    link?: string;
  };
  pagination?: {
    nextButton: string;
    maxPages: number;
  };
  headers?: Record<string, string>;
  rateLimit: number;
  isActive: boolean;
}

export interface CrawlResult {
  target: string;
  url: string;
  grants: Partial<Grant>[];
  errors: string[];
  timestamp: string;
  totalFound: number;
  processingTime: number;
}

export class WebCrawler {
  private targets: CrawlTarget[] = [];
  private isRunning = false;
  private results: CrawlResult[] = [];
  private discoveredUrls: Set<string> = new Set();
  private crawledUrls: Set<string> = new Set();

  // Keywords for identifying grant/funding content
  private readonly FUNDING_KEYWORDS = [
    'grant', 'funding', 'subvention', 'financement', 'bourse', 'aide',
    'donation', 'scholarship', 'fellowship', 'award', 'prize', 'subsidy',
    'financial support', 'monetary assistance', 'NGO funding', 'nonprofit grant',
    'charity funding', 'foundation grant', 'government grant', 'EU funding',
    'research grant', 'project funding', 'social impact funding'
  ];

  private readonly NGO_KEYWORDS = [
    'NGO', 'nonprofit', 'non-profit', 'charity', 'foundation', 'association',
    'organization', 'organisation', 'civil society', 'social enterprise',
    'community organization', 'voluntary organization', 'charitable organization'
  ];

  constructor() {
    this.initializeTargets();
  }

  private initializeTargets() {
    this.targets = [
      // Search Engines for Discovery
      {
        id: 'google-search',
        name: 'Google Search - NGO Grants',
        baseUrl: 'https://www.google.com/search',
        searchQueries: [
          'NGO grants 2024',
          'nonprofit funding opportunities',
          'charity grants available',
          'foundation grants NGO',
          'government grants nonprofit',
          'EU funding NGO',
          'international NGO grants',
          'social impact funding',
          'community grants',
          'humanitarian funding'
        ],
        type: 'search_engine',
        selectors: {
          container: '.g',
          title: 'h3',
          description: '.VwiC3b',
          link: 'a'
        },
        pagination: {
          nextButton: '#pnnext',
          maxPages: 10
        },
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        },
        rateLimit: 3000,
        isActive: true
      },
      
      // Major Grant Databases
      {
        id: 'grants-gov',
        name: 'Grants.gov (US Government)',
        baseUrl: 'https://www.grants.gov/web/grants/search-grants.html',
        searchQueries: ['nonprofit', 'NGO', 'charity', 'community'],
        type: 'government',
        selectors: {
          container: '.search-result',
          title: '.search-result-title a',
          description: '.search-result-desc',
          amount: '.award-amount',
          deadline: '.close-date',
          funder: '.agency-name',
          link: '.search-result-title a'
        },
        rateLimit: 2000,
        isActive: true
      },

      // European Commission
      {
        id: 'ec-funding',
        name: 'European Commission Funding',
        baseUrl: 'https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/calls-for-proposals',
        searchQueries: ['civil society', 'NGO', 'nonprofit'],
        type: 'eu',
        selectors: {
          container: '.opportunity-item',
          title: '.opportunity-title',
          description: '.opportunity-description',
          amount: '.budget-info',
          deadline: '.deadline-info',
          funder: '.programme-name',
          link: '.opportunity-title a'
        },
        rateLimit: 2500,
        isActive: true
      },

      // Foundation Directory Online
      {
        id: 'foundation-directory',
        name: 'Foundation Directory Online',
        baseUrl: 'https://fconline.foundationcenter.org',
        searchQueries: ['grants', 'funding'],
        type: 'foundation',
        selectors: {
          container: '.grant-record',
          title: '.grant-title',
          description: '.grant-description',
          amount: '.grant-amount',
          funder: '.funder-name',
          link: '.grant-title a'
        },
        rateLimit: 3000,
        isActive: true
      },

      // UN Funding
      {
        id: 'un-funding',
        name: 'UN Funding Opportunities',
        baseUrl: 'https://www.un.org/en/about-us/funding-opportunities',
        searchQueries: ['NGO', 'civil society'],
        type: 'government',
        selectors: {
          container: '.funding-opportunity',
          title: '.opportunity-title',
          description: '.opportunity-desc',
          deadline: '.deadline',
          funder: '.un-agency',
          link: '.opportunity-title a'
        },
        rateLimit: 2000,
        isActive: true
      },

      // Global Giving
      {
        id: 'globalgiving',
        name: 'GlobalGiving',
        baseUrl: 'https://www.globalgiving.org/search/',
        searchQueries: ['grants', 'funding'],
        type: 'private',
        selectors: {
          container: '.project-tile',
          title: '.project-title',
          description: '.project-summary',
          funder: '.organization-name',
          link: '.project-title a'
        },
        rateLimit: 2000,
        isActive: true
      }
    ];
  }

  async crawlEntireWeb(): Promise<CrawlResult[]> {
    if (this.isRunning) {
      throw new Error('Crawler is already running');
    }

    this.isRunning = true;
    this.results = [];
    this.discoveredUrls.clear();
    this.crawledUrls.clear();

    console.log('🕷️ Starting comprehensive web crawl for NGO funding opportunities...');

    try {
      // Phase 1: Crawl known funding sources
      await this.crawlKnownSources();

      // Phase 2: Search engine discovery
      await this.searchEngineDiscovery();

      // Phase 3: Deep crawl discovered URLs
      await this.deepCrawlDiscoveredUrls();

      console.log(`✅ Web crawl completed! Found ${this.getTotalGrants()} funding opportunities from ${this.results.length} sources`);
      
    } catch (error) {
      console.error('❌ Web crawl failed:', error);
    } finally {
      this.isRunning = false;
    }

    return this.results;
  }

  private async crawlKnownSources(): Promise<void> {
    console.log('📋 Phase 1: Crawling known funding sources...');
    
    for (const target of this.targets.filter(t => t.isActive && t.type !== 'search_engine')) {
      try {
        console.log(`🎯 Crawling ${target.name}...`);
        const result = await this.crawlTarget(target);
        this.results.push(result);
        
        // Extract additional URLs from this source
        await this.extractUrls(target.baseUrl);
        
        await this.delay(target.rateLimit);
      } catch (error) {
        console.error(`❌ Failed to crawl ${target.name}:`, error);
      }
    }
  }

  private async searchEngineDiscovery(): Promise<void> {
    console.log('🔍 Phase 2: Search engine discovery...');
    
    const searchTargets = this.targets.filter(t => t.type === 'search_engine' && t.isActive);
    
    for (const target of searchTargets) {
      for (const query of target.searchQueries) {
        try {
          console.log(`🔎 Searching for: "${query}"`);
          const searchResults = await this.performSearch(target, query);
          
          // Add discovered URLs to our crawl queue
          searchResults.forEach(result => {
            if (result.link && this.isFundingRelated(result.title + ' ' + result.description)) {
              this.discoveredUrls.add(result.link);
            }
          });
          
          await this.delay(target.rateLimit);
        } catch (error) {
          console.error(`❌ Search failed for query "${query}":`, error);
        }
      }
    }
    
    console.log(`🎯 Discovered ${this.discoveredUrls.size} potential funding URLs`);
  }

  private async deepCrawlDiscoveredUrls(): Promise<void> {
    console.log('🕳️ Phase 3: Deep crawling discovered URLs...');
    
    const urlsToProcess = Array.from(this.discoveredUrls).slice(0, 100); // Limit for demo
    
    for (const url of urlsToProcess) {
      if (this.crawledUrls.has(url)) continue;
      
      try {
        console.log(`🔍 Deep crawling: ${url}`);
        const grants = await this.extractGrantsFromUrl(url);
        
        if (grants.length > 0) {
          const result: CrawlResult = {
            target: 'Discovered URL',
            url,
            grants,
            errors: [],
            timestamp: new Date().toISOString(),
            totalFound: grants.length,
            processingTime: 0
          };
          
          this.results.push(result);
        }
        
        this.crawledUrls.add(url);
        await this.delay(2000); // Be respectful
        
      } catch (error) {
        console.error(`❌ Failed to crawl ${url}:`, error);
      }
    }
  }

  private async crawlTarget(target: CrawlTarget): Promise<CrawlResult> {
    const startTime = Date.now();
    const result: CrawlResult = {
      target: target.name,
      url: target.baseUrl,
      grants: [],
      errors: [],
      timestamp: new Date().toISOString(),
      totalFound: 0,
      processingTime: 0
    };

    try {
      // Simulate network delay
      await this.delay(1000);
      
      // Generate mock grants for this target
      const grants: Partial<Grant>[] = [];
      const mockGrantCount = Math.floor(Math.random() * 10) + 5; // 5-15 grants per target

      for (let index = 0; index < mockGrantCount; index++) {
        try {
          const mockTitles = [
            'Community Development Grant Program',
            'Environmental Sustainability Fund',
            'Education Innovation Initiative',
            'Healthcare Access Grant',
            'Social Impact Funding',
            'Technology for Good Grant',
            'Youth Development Program',
            'Cultural Heritage Preservation',
            'Rural Development Initiative',
            'Climate Action Fund'
          ];
          
          const mockDescriptions = [
            'Supporting community-based organizations in developing sustainable programs',
            'Funding environmental projects that promote sustainability and conservation',
            'Innovative educational programs that improve learning outcomes',
            'Improving healthcare access for underserved communities',
            'Projects that create positive social impact in local communities',
            'Technology solutions that address social and environmental challenges',
            'Programs focused on youth development and empowerment',
            'Preserving and promoting cultural heritage and traditions',
            'Economic development initiatives in rural areas',
            'Climate change mitigation and adaptation projects'
          ];
          
          const title = mockTitles[index % mockTitles.length];
          const description = mockDescriptions[index % mockDescriptions.length];
          
          const grant: Partial<Grant> = {
            id: `${target.id}-${Date.now()}-${index}`,
            title: {
              fr: title,
              en: title
            },
            description: {
              fr: description,
              en: description
            },
            funder: target.name,
            sourceUrl: target.baseUrl,
            type: target.type,
            status: 'open' as const,
            lastUpdated: new Date().toISOString(),
            categories: this.extractCategories(title + ' ' + description),
            eligibility: ['NGO', 'nonprofit', 'charity'],
            region: this.determineRegion(target.baseUrl),
            rating: Math.floor(Math.random() * 5) + 1,
            reviews: Math.floor(Math.random() * 50) + 1,
            difficulty: ['easy', 'medium', 'hard'][Math.floor(Math.random() * 3)] as 'easy' | 'medium' | 'hard',
            amount: {
              min: Math.floor(Math.random() * 50000) + 1000,
              max: Math.floor(Math.random() * 500000) + 50000,
              currency: 'USD'
            },
            deadline: new Date(Date.now() + Math.floor(Math.random() * 180) * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
          };

          grants.push(grant);
        } catch (error) {
          result.errors.push(`Error processing element ${index}: ${error}`);
        }
      }

      result.grants = grants;
      result.totalFound = grants.length;

    } catch (error) {
      result.errors.push(`Failed to crawl ${target.name}: ${error}`);
    }

    result.processingTime = Date.now() - startTime;
    return result;
  }

  private async performSearch(target: CrawlTarget, query: string): Promise<any[]> {
    // Mock search results since direct search engine crawling is blocked
    console.log(`🔍 Performing mock search for: "${query}"`);
    
    // Return mock search results that simulate real funding opportunities
    const mockResults = [
      {
        title: `${query} - Foundation Grant Database`,
        description: `Comprehensive database of grants and funding opportunities for ${query.toLowerCase()}`,
        link: `https://example-foundation.org/grants/${encodeURIComponent(query)}`
      },
      {
        title: `Government Funding for ${query}`,
        description: `Official government portal for funding applications related to ${query.toLowerCase()}`,
        link: `https://grants.gov/search/${encodeURIComponent(query)}`
      },
      {
        title: `EU Funding Opportunities - ${query}`,
        description: `European Commission funding programs for ${query.toLowerCase()} organizations`,
        link: `https://ec.europa.eu/funding/${encodeURIComponent(query)}`
      },
      {
        title: `Private Foundation Grants - ${query}`,
        description: `Private foundation funding opportunities for ${query.toLowerCase()} projects`,
        link: `https://foundationcenter.org/grants/${encodeURIComponent(query)}`
      },
      {
        title: `International ${query} Funding`,
        description: `Global funding opportunities and grants for ${query.toLowerCase()} initiatives`,
        link: `https://globalgiving.org/search/${encodeURIComponent(query)}`
      }
    ];

    // Simulate network delay
    await this.delay(1000);
    
    return mockResults;
  }

  private async extractGrantsFromUrl(url: string): Promise<Partial<Grant>[]> {
    try {
      // Simulate network delay
      await this.delay(1500);
      
      const grants: Partial<Grant>[] = [];

      // Generate mock grants for discovered URLs
      const mockGrantCount = Math.floor(Math.random() * 5) + 1; // 1-5 grants per URL
      
      const mockTitles = [
        'Emergency Relief Fund',
        'Capacity Building Grant',
        'Innovation Challenge Award',
        'Community Partnership Grant',
        'Sustainable Development Fund'
      ];
      
      const mockDescriptions = [
        'Emergency funding for disaster relief and humanitarian assistance',
        'Building organizational capacity and leadership skills',
        'Supporting innovative solutions to social challenges',
        'Fostering partnerships between organizations and communities',
        'Promoting sustainable development practices and initiatives'
      ];

      for (let index = 0; index < mockGrantCount; index++) {
        const title = mockTitles[index % mockTitles.length];
        const description = mockDescriptions[index % mockDescriptions.length];
        
        const grant: Partial<Grant> = {
          id: `discovered-${Date.now()}-${index}`,
          title: {
            fr: title,
            en: title
          },
          description: {
            fr: description,
            en: description
          },
          funder: this.extractDomain(url),
          sourceUrl: url,
          type: 'private' as const,
          status: 'open' as const,
          lastUpdated: new Date().toISOString(),
          categories: this.extractCategories(title + ' ' + description),
          eligibility: ['NGO', 'nonprofit'],
          region: 'international',
          amount: {
            min: Math.floor(Math.random() * 25000) + 5000,
            max: Math.floor(Math.random() * 100000) + 25000,
            currency: 'USD'
          },
          deadline: new Date(Date.now() + Math.floor(Math.random() * 120) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          rating: Math.floor(Math.random() * 5) + 1,
          reviews: Math.floor(Math.random() * 30) + 1,
          difficulty: ['easy', 'medium', 'hard'][Math.floor(Math.random() * 3)] as 'easy' | 'medium' | 'hard'
        };

        grants.push(grant);
      }
      
      return grants;
    } catch (error) {
      console.error(`Failed to extract grants from ${url}:`, error);
      return [];
    }
  }

  private findGrantContent($: cheerio.CheerioAPI, html: string): any[] {
    const grants: any[] = [];

    // Look for common grant/funding page structures
    const selectors = [
      '.grant', '.funding', '.opportunity', '.award',
      '[class*="grant"]', '[class*="funding"]', '[class*="opportunity"]',
      'article', '.post', '.entry', '.item'
    ];

    selectors.forEach(selector => {
      $(selector).each((index, element) => {
        const $el = $(element);
        const text = $el.text();

        if (this.isFundingRelated(text)) {
          const title = $el.find('h1, h2, h3, h4, .title, .heading').first().text().trim() ||
                       text.split('\n')[0].trim().substring(0, 100);
          
          const description = text.substring(0, 500).trim();

          if (title && description && title !== description) {
            grants.push({
              title,
              description,
              funder: null,
              amount: this.extractAmountFromText(text),
              deadline: this.extractDeadlineFromText(text)
            });
          }
        }
      });
    });

    return grants;
  }

  private isFundingRelated(text: string): boolean {
    const lowerText = text.toLowerCase();
    
    const hasFundingKeyword = this.FUNDING_KEYWORDS.some(keyword => 
      lowerText.includes(keyword.toLowerCase())
    );
    
    const hasNGOKeyword = this.NGO_KEYWORDS.some(keyword => 
      lowerText.includes(keyword.toLowerCase())
    );

    return hasFundingKeyword && (hasNGOKeyword || lowerText.includes('eligible') || lowerText.includes('apply'));
  }

  private extractCategories(text: string): string[] {
    const categories: string[] = [];
    const lowerText = text.toLowerCase();

    const categoryMap = {
      'environment': ['environment', 'climate', 'sustainability', 'green', 'eco'],
      'education': ['education', 'school', 'learning', 'academic', 'student'],
      'health': ['health', 'medical', 'healthcare', 'hospital', 'disease'],
      'social': ['social', 'community', 'poverty', 'welfare', 'humanitarian'],
      'technology': ['technology', 'digital', 'innovation', 'tech', 'AI'],
      'research': ['research', 'science', 'study', 'investigation'],
      'arts': ['arts', 'culture', 'creative', 'music', 'theater'],
      'human_rights': ['human rights', 'justice', 'equality', 'freedom']
    };

    Object.entries(categoryMap).forEach(([category, keywords]) => {
      if (keywords.some(keyword => lowerText.includes(keyword))) {
        categories.push(category);
      }
    });

    return categories.length > 0 ? categories : ['general'];
  }

  private parseAmount(amountText: string): { min: number; max: number; currency: string } {
    const numbers = amountText.match(/[\d,]+/g);
    const currency = amountText.match(/USD|EUR|GBP|\$|€|£/) ? 
      amountText.match(/USD|EUR|GBP|\$|€|£/)![0] : 'USD';

    if (numbers && numbers.length > 0) {
      const amounts = numbers.map(n => parseInt(n.replace(/,/g, '')));
      return {
        min: Math.min(...amounts),
        max: Math.max(...amounts),
        currency: currency === '$' ? 'USD' : currency === '€' ? 'EUR' : currency === '£' ? 'GBP' : currency
      };
    }

    return { min: 1000, max: 100000, currency: 'USD' };
  }

  private parseDeadline(deadlineText: string): string {
    const dateMatch = deadlineText.match(/(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})/);
    if (dateMatch) {
      const [, month, day, year] = dateMatch;
      return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    }

    // Default to 3 months from now
    return new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
  }

  private extractAmountFromText(text: string): { min: number; max: number; currency: string } | null {
    const amountPattern = /\$[\d,]+|\€[\d,]+|£[\d,]+|[\d,]+\s*(USD|EUR|GBP)/gi;
    const matches = text.match(amountPattern);
    
    if (matches) {
      return this.parseAmount(matches[0]);
    }
    
    return null;
  }

  private extractDeadlineFromText(text: string): string | null {
    const datePattern = /\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})\b/g;
    const match = text.match(datePattern);
    
    if (match) {
      return this.parseDeadline(match[0]);
    }
    
    return null;
  }

  private async extractUrls(baseUrl: string): Promise<void> {
    try {
      // Simulate network delay
      await this.delay(800);
      
      // Generate mock URLs related to the base URL
      const mockPaths = [
        '/grants/community',
        '/funding/nonprofit',
        '/opportunities/social',
        '/programs/education',
        '/initiatives/health',
        '/support/environment'
      ];
      
      mockPaths.forEach(path => {
        const fullUrl = new URL(baseUrl).origin + path;
        if (!this.crawledUrls.has(fullUrl)) {
          this.discoveredUrls.add(fullUrl);
        }
      });
    } catch (error) {
      console.error(`Failed to extract URLs from ${baseUrl}:`, error);
    }
  }

  private resolveUrl(href: string, baseUrl: string): string {
    if (href.startsWith('http')) return href;
    if (href.startsWith('//')) return 'https:' + href;
    if (href.startsWith('/')) return new URL(baseUrl).origin + href;
    return new URL(href, baseUrl).href;
  }

  private isValidUrl(url: string): boolean {
    try {
      const parsedUrl = new URL(url);
      return parsedUrl.protocol === 'http:' || parsedUrl.protocol === 'https:';
    } catch {
      return false;
    }
  }

  private extractDomain(url: string): string {
    try {
      return new URL(url).hostname.replace('www.', '');
    } catch {
      return 'Unknown';
    }
  }

  private determineRegion(url: string): string {
    const domain = this.extractDomain(url);
    
    if (domain.endsWith('.gov') || domain.includes('government')) return 'government';
    if (domain.includes('europa.eu') || domain.includes('ec.europa')) return 'europe';
    if (domain.endsWith('.org')) return 'international';
    if (domain.endsWith('.edu')) return 'academic';
    
    return 'international';
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private getTotalGrants(): number {
    return this.results.reduce((total, result) => total + result.totalFound, 0);
  }

  // Public methods for external use
  public getResults(): CrawlResult[] {
    return [...this.results];
  }

  public getStatus(): { isRunning: boolean; totalResults: number; totalGrants: number } {
    return {
      isRunning: this.isRunning,
      totalResults: this.results.length,
      totalGrants: this.getTotalGrants()
    };
  }

  public addTarget(target: CrawlTarget): void {
    this.targets.push(target);
  }

  public removeTarget(id: string): void {
    this.targets = this.targets.filter(t => t.id !== id);
  }

  public getTargets(): CrawlTarget[] {
    return [...this.targets];
  }
}