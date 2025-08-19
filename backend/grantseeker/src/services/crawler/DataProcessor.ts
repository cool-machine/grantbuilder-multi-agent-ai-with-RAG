import { Grant } from '../../contexts/GrantContext';

export interface ProcessingRule {
  field: keyof Grant;
  pattern: RegExp;
  transform: (value: string) => any;
}

export class DataProcessor {
  private rules: ProcessingRule[] = [];

  constructor() {
    this.initializeDefaultRules();
  }

  private initializeDefaultRules() {
    this.rules = [
      // Amount processing
      {
        field: 'amount' as keyof Grant,
        pattern: /(\d+(?:\.\d+)?)\s*(?:€|EUR|euros?)/i,
        transform: (value: string) => {
          const matches = value.match(/(\d+(?:\.\d+)?)/g);
          if (matches) {
            const amounts = matches.map(m => parseFloat(m.replace(/\s/g, '')));
            return {
              min: Math.min(...amounts),
              max: Math.max(...amounts),
              currency: 'EUR'
            };
          }
          return { min: 0, max: 0, currency: 'EUR' };
        }
      },
      
      // Date processing
      {
        field: 'deadline' as keyof Grant,
        pattern: /(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})/,
        transform: (value: string) => {
          const match = value.match(/(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})/);
          if (match) {
            const [, day, month, year] = match;
            return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
          }
          return new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        }
      }
    ];
  }

  processRawData(rawData: any, sourceType: string): Partial<Grant> {
    const processed: Partial<Grant> = {
      id: this.generateId(rawData.title, sourceType),
      title: {
        fr: this.cleanText(rawData.title),
        en: this.cleanText(rawData.title) // In production, use translation service
      },
      description: {
        fr: this.cleanText(rawData.description),
        en: this.cleanText(rawData.description)
      },
      funder: this.cleanText(rawData.funder),
      sourceUrl: rawData.link || rawData.sourceUrl,
      lastUpdated: new Date().toISOString(),
      type: this.determineType(sourceType),
      status: 'open' as const,
      region: this.determineRegion(rawData),
      categories: this.extractCategories(rawData.title + ' ' + rawData.description),
      eligibility: this.determineEligibility(rawData),
      rating: 0,
      reviews: 0,
      difficulty: this.determineDifficulty(rawData)
    };

    // Apply processing rules
    for (const rule of this.rules) {
      const fieldValue = rawData[rule.field as string];
      if (fieldValue && rule.pattern.test(fieldValue)) {
        (processed as any)[rule.field] = rule.transform(fieldValue);
      }
    }

    return processed;
  }

  private generateId(title: string, source: string): string {
    const cleanTitle = title.toLowerCase().replace(/[^a-z0-9]/g, '-');
    const timestamp = Date.now();
    return `${source}-${cleanTitle.substring(0, 30)}-${timestamp}`;
  }

  private cleanText(text: string): string {
    if (!text) return '';
    return text
      .replace(/\s+/g, ' ')
      .replace(/[^\w\s\-.,!?()]/g, '')
      .trim();
  }

  private determineType(sourceType: string): 'government' | 'eu' | 'foundation' | 'private' {
    const typeMap: Record<string, 'government' | 'eu' | 'foundation' | 'private'> = {
      'government': 'government',
      'eu': 'eu',
      'foundation': 'foundation',
      'private': 'private'
    };
    return typeMap[sourceType] || 'private';
  }

  private determineRegion(rawData: any): string {
    // Simple region detection based on keywords
    const text = (rawData.title + ' ' + rawData.description).toLowerCase();
    
    if (text.includes('europe') || text.includes('eu')) return 'europe';
    if (text.includes('national') || text.includes('france')) return 'national';
    if (text.includes('île-de-france') || text.includes('paris')) return 'ile_de_france';
    
    return 'national';
  }

  private extractCategories(text: string): string[] {
    const categoryKeywords = {
      'environment': ['environnement', 'écologie', 'climat', 'biodiversité'],
      'education': ['éducation', 'formation', 'enseignement', 'école'],
      'social': ['social', 'solidarité', 'aide', 'assistance'],
      'health': ['santé', 'médical', 'soins', 'hôpital'],
      'culture': ['culture', 'art', 'patrimoine', 'musée'],
      'sport': ['sport', 'activité physique', 'loisir'],
      'innovation': ['innovation', 'technologie', 'numérique'],
      'research': ['recherche', 'science', 'étude'],
      'community': ['communauté', 'local', 'territoire']
    };

    const categories: string[] = [];
    const lowerText = text.toLowerCase();

    for (const [category, keywords] of Object.entries(categoryKeywords)) {
      if (keywords.some(keyword => lowerText.includes(keyword))) {
        categories.push(category);
      }
    }

    return categories.length > 0 ? categories : ['general'];
  }

  private determineEligibility(rawData: any): string[] {
    // Default eligibility - in production, extract from grant details
    return ['association_loi_1901'];
  }

  private determineDifficulty(rawData: any): 'easy' | 'medium' | 'hard' {
    const text = (rawData.title + ' ' + rawData.description).toLowerCase();
    
    if (text.includes('simple') || text.includes('facile')) return 'easy';
    if (text.includes('complexe') || text.includes('difficile')) return 'hard';
    
    return 'medium';
  }

  // Validation methods
  validateGrant(grant: Partial<Grant>): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!grant.title?.fr) errors.push('Title is required');
    if (!grant.description?.fr) errors.push('Description is required');
    if (!grant.funder) errors.push('Funder is required');
    if (!grant.amount || grant.amount.max <= 0) errors.push('Valid amount is required');
    if (!grant.deadline) errors.push('Deadline is required');

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Deduplication
  findDuplicates(grants: Partial<Grant>[]): { duplicates: string[][]; unique: Partial<Grant>[] } {
    const duplicates: string[][] = [];
    const unique: Partial<Grant>[] = [];
    const seen = new Map<string, number>();

    for (const grant of grants) {
      const signature = this.createSignature(grant);
      
      if (seen.has(signature)) {
        const existingIndex = seen.get(signature)!;
        const existingGroup = duplicates.find(group => group.includes(unique[existingIndex].id!));
        
        if (existingGroup) {
          existingGroup.push(grant.id!);
        } else {
          duplicates.push([unique[existingIndex].id!, grant.id!]);
        }
      } else {
        seen.set(signature, unique.length);
        unique.push(grant);
      }
    }

    return { duplicates, unique };
  }

  private createSignature(grant: Partial<Grant>): string {
    const title = grant.title?.fr?.toLowerCase().replace(/\s+/g, '') || '';
    const funder = grant.funder?.toLowerCase().replace(/\s+/g, '') || '';
    const amount = grant.amount?.max || 0;
    
    return `${title}-${funder}-${amount}`;
  }
}