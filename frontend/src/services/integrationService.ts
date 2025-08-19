/**
 * Integration service that combines crawler API with grant management
 * Provides unified interface for managing both mock and real data
 */

import { crawlerAPI, CrawlerMode, CrawlerResult } from './api/crawlerAPI';
import { Grant } from '../contexts/GrantContext';

export interface IntegratedCrawlResult {
  success: boolean;
  mode: CrawlerMode;
  grants: Grant[];
  statistics: {
    totalFound: number;
    totalSaved: number;
    duplicatesSkipped: number;
    errors: string[];
    duration: number;
  };
  message: string;
}

class IntegrationService {
  /**
   * Start crawling and integrate results with grant system
   */
  async crawlAndIntegrate(
    mode: CrawlerMode = 'mock',
    config: any = {}
  ): Promise<IntegratedCrawlResult> {
    try {
      // Start crawling
      const crawlResult = await crawlerAPI.startCrawling(mode, config);
      
      if (!crawlResult.success) {
        return {
          success: false,
          mode,
          grants: [],
          statistics: {
            totalFound: 0,
            totalSaved: 0,
            duplicatesSkipped: 0,
            errors: crawlResult.results.errors,
            duration: crawlResult.results.duration_seconds
          },
          message: crawlResult.message
        };
      }

      // Convert opportunities to Grant format
      const grants: Grant[] = this.convertOpportunitiesToGrants(crawlResult.opportunities);

      return {
        success: true,
        mode: crawlResult.mode as CrawlerMode,
        grants,
        statistics: {
          totalFound: crawlResult.results.total_found,
          totalSaved: crawlResult.results.saved_to_database,
          duplicatesSkipped: Math.max(0, crawlResult.results.total_found - crawlResult.results.saved_to_database),
          errors: crawlResult.results.errors,
          duration: crawlResult.results.duration_seconds
        },
        message: crawlResult.message
      };

    } catch (error) {
      return {
        success: false,
        mode,
        grants: [],
        statistics: {
          totalFound: 0,
          totalSaved: 0,
          duplicatesSkipped: 0,
          errors: [error instanceof Error ? error.message : String(error)],
          duration: 0
        },
        message: 'Integration failed'
      };
    }
  }

  /**
   * Get stored results and convert to Grant format
   */
  async getStoredGrants(params: {
    limit?: number;
    source?: string;
    query?: string;
  } = {}): Promise<Grant[]> {
    try {
      const response = await crawlerAPI.getResults(params);
      
      if (!response.success || !response.opportunities) {
        return [];
      }

      return this.convertStoredOpportunitiesToGrants(response.opportunities);
      
    } catch (error) {
      console.error('Failed to get stored grants:', error);
      return [];
    }
  }

  /**
   * Convert crawler opportunities to Grant objects
   */
  private convertOpportunitiesToGrants(opportunities: any[]): Grant[] {
    return opportunities.map((opp, index) => this.createGrantFromOpportunity(opp, index));
  }

  /**
   * Convert stored opportunities to Grant objects
   */
  private convertStoredOpportunitiesToGrants(opportunities: any[]): Grant[] {
    return opportunities.map(opp => this.createGrantFromStoredOpportunity(opp));
  }

  /**
   * Create Grant object from fresh crawl opportunity
   */
  private createGrantFromOpportunity(opp: any, index: number): Grant {
    const now = new Date().toISOString();
    
    return {
      id: `crawl-${Date.now()}-${index}`,
      title: {
        fr: opp.title,
        en: opp.title
      },
      description: {
        fr: opp.description || 'Description à venir',
        en: opp.description || 'Description to come'
      },
      funder: opp.source || 'Unknown Funder',
      amount: this.parseAmount(opp.amount),
      deadline: opp.deadline || new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      categories: opp.categories || ['general'],
      eligibility: opp.eligibility || ['association_loi_1901'],
      region: 'national',
      type: this.mapSourceToType(opp.source),
      status: 'open' as const,
      applicationProcess: {
        fr: 'Processus de candidature disponible sur le site du financeur',
        en: 'Application process available on funder\'s website'
      },
      requiredDocuments: ['project_description', 'budget', 'organization_info'],
      contactInfo: {
        email: 'info@funder.org',
        phone: '+33 1 XX XX XX XX',
        website: opp.url
      },
      sourceUrl: opp.url,
      lastUpdated: now,
      rating: 4.0,
      reviews: Math.floor(Math.random() * 20) + 5,
      difficulty: this.assignDifficulty(),
      tags: opp.categories || []
    };
  }

  /**
   * Create Grant object from stored opportunity
   */
  private createGrantFromStoredOpportunity(opp: any): Grant {
    return {
      id: `stored-${opp.id}`,
      title: {
        fr: opp.title,
        en: opp.title
      },
      description: {
        fr: opp.description || 'Description à venir',
        en: opp.description || 'Description to come'
      },
      funder: opp.source || 'Unknown Funder',
      amount: this.parseAmount(opp.amount),
      deadline: opp.deadline || new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      categories: opp.categories || ['general'],
      eligibility: opp.eligibility || ['association_loi_1901'],
      region: 'national',
      type: this.mapSourceToType(opp.source),
      status: 'open' as const,
      applicationProcess: {
        fr: 'Processus de candidature disponible sur le site du financeur',
        en: 'Application process available on funder\'s website'
      },
      requiredDocuments: ['project_description', 'budget', 'organization_info'],
      contactInfo: {
        email: 'info@funder.org',
        phone: '+33 1 XX XX XX XX',
        website: opp.url
      },
      sourceUrl: opp.url,
      lastUpdated: opp.extracted_date || new Date().toISOString(),
      rating: 4.0,
      reviews: Math.floor(Math.random() * 20) + 5,
      difficulty: this.assignDifficulty(),
      tags: opp.categories || []
    };
  }

  /**
   * Parse amount string to amount object
   */
  private parseAmount(amountStr?: string): { min: number; max: number; currency: string } {
    if (!amountStr) {
      return { min: 5000, max: 50000, currency: 'EUR' };
    }

    // Extract numbers from string like "€5,000 - €50,000"
    const matches = amountStr.match(/[\d,]+/g);
    if (matches && matches.length >= 2) {
      const min = parseInt(matches[0].replace(/,/g, ''));
      const max = parseInt(matches[1].replace(/,/g, ''));
      return { min, max, currency: 'EUR' };
    } else if (matches && matches.length === 1) {
      const amount = parseInt(matches[0].replace(/,/g, ''));
      return { min: amount * 0.5, max: amount, currency: 'EUR' };
    }

    return { min: 5000, max: 50000, currency: 'EUR' };
  }

  /**
   * Map source to grant type
   */
  private mapSourceToType(source?: string): 'government' | 'eu' | 'foundation' | 'private' {
    if (!source) return 'private';
    
    const lowerSource = source.toLowerCase();
    if (lowerSource.includes('european') || lowerSource.includes('eu') || lowerSource.includes('europe')) {
      return 'eu';
    } else if (lowerSource.includes('government') || lowerSource.includes('ministry') || lowerSource.includes('gouv')) {
      return 'government';
    } else if (lowerSource.includes('foundation') || lowerSource.includes('fondation')) {
      return 'foundation';
    }
    
    return 'private';
  }

  /**
   * Assign difficulty randomly
   */
  private assignDifficulty(): 'easy' | 'medium' | 'hard' {
    const difficulties: Array<'easy' | 'medium' | 'hard'> = ['easy', 'medium', 'hard'];
    return difficulties[Math.floor(Math.random() * difficulties.length)];
  }

  /**
   * Get comprehensive status including both crawler and integration info
   */
  async getIntegratedStatus(mode: CrawlerMode = 'mock'): Promise<{
    crawler: any;
    integration: {
      connected: boolean;
      lastSync: string;
      totalIntegratedGrants: number;
    };
  }> {
    try {
      const crawlerStatus = await crawlerAPI.getStatus(mode);
      
      // Get count of integrated grants (this could be stored separately)
      const storedGrants = await this.getStoredGrants({ limit: 1000 });
      
      return {
        crawler: crawlerStatus.status,
        integration: {
          connected: crawlerStatus.success,
          lastSync: new Date().toISOString(),
          totalIntegratedGrants: storedGrants.length
        }
      };
      
    } catch (error) {
      return {
        crawler: null,
        integration: {
          connected: false,
          lastSync: 'Never',
          totalIntegratedGrants: 0
        }
      };
    }
  }

  /**
   * Toggle crawler mode and return new status
   */
  async toggleCrawlerMode(currentMode: CrawlerMode): Promise<{
    success: boolean;
    newMode: CrawlerMode;
    status: any;
  }> {
    try {
      const response = await crawlerAPI.toggleMode(currentMode);
      return {
        success: response.success,
        newMode: response.current_mode,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        newMode: currentMode,
        status: null
      };
    }
  }

  /**
   * Export grants data
   */
  async exportGrants(format: 'json' | 'csv'): Promise<string> {
    // This could call a backend API to generate exports
    const grants = await this.getStoredGrants({ limit: 10000 });
    
    if (format === 'json') {
      return JSON.stringify(grants, null, 2);
    } else {
      // Simple CSV conversion
      const headers = ['Title', 'Funder', 'Amount Min', 'Amount Max', 'Deadline', 'Source URL'];
      const csv = [
        headers.join(','),
        ...grants.map(grant => [
          `"${grant.title.fr}"`,
          `"${grant.funder}"`,
          grant.amount.min,
          grant.amount.max,
          grant.deadline,
          `"${grant.sourceUrl}"`
        ].join(','))
      ].join('\n');
      
      return csv;
    }
  }
}

export const integrationService = new IntegrationService();