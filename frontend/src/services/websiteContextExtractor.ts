// Website Context Extractor for Grant Applications
// Extracts contextual information from funder and applicant websites

export interface WebsiteContext {
  url: string;
  accessible: boolean;
  lastUpdated?: string;
  title: string;
  mission?: string;
  description?: string;
  keyInfo: string[];
  // Structured funder information
  funderInfo?: {
    about?: {
      missionStatement?: string;
      organizationalGoals?: string[];
      strategicObjectives?: string[];
    };
    pastFundings?: {
      recentRecipients?: string[];
      fundedProjects?: string[];
      awardAmounts?: string[];
    };
    fundingPriorities?: {
      currentCalls?: string[];
      priorityThemes?: string[];
      evaluationCriteria?: string[];
      strategicFocus?: string[];
    };
  };
  // Structured applicant information
  applicantInfo?: {
    researchCapabilities?: {
      expertiseAreas?: string[];
      researchCenters?: string[];
      keyFaculty?: string[];
      academicDepartments?: string[];
    };
    trackRecord?: {
      previousGrants?: string[];
      notableProjects?: string[];
      publications?: string[];
      awards?: string[];
    };
    resources?: {
      facilities?: string[];
      equipment?: string[];
      collaborations?: string[];
      supportServices?: string[];
    };
  };
  contactInfo?: {
    email?: string;
    phone?: string;
    address?: string;
  };
  warnings: string[];
  extractedAt: Date;
  confidence: number;
}

export interface ExtractedContexts {
  funder: WebsiteContext | null;
  applicant: WebsiteContext | null;
}

export class WebsiteContextExtractor {
  private static instance: WebsiteContextExtractor;

  static getInstance(): WebsiteContextExtractor {
    if (!WebsiteContextExtractor.instance) {
      WebsiteContextExtractor.instance = new WebsiteContextExtractor();
    }
    return WebsiteContextExtractor.instance;
  }

  async extractWebsiteContext(url: string, type: 'funder' | 'applicant'): Promise<WebsiteContext> {
    console.log(`Extracting context from ${type} website: ${url}`);

    try {
      // For local development, we'll use a CORS proxy or mock the extraction
      // In production, this would go through your backend crawler service
      const response = await this.fetchWithFallback(url);
      
      if (!response.ok) {
        throw new Error(`Website not accessible: ${response.status}`);
      }

      const html = await response.text();
      const context = this.parseWebsiteContent(html, url, type);
      
      return context;

    } catch (error) {
      console.warn(`Failed to extract from ${url}:`, error);
      return this.createFallbackContext(url, type, error instanceof Error ? error.message : 'Unknown error');
    }
  }

  private async fetchWithFallback(url: string): Promise<Response> {
    console.log(`Attempting to fetch: ${url}`);
    
    // Try direct fetch first (will work for CORS-enabled sites)
    try {
      console.log('Trying direct fetch...');
      const response = await fetch(url);
      console.log(`Direct fetch response: ${response.status} ${response.statusText}`);
      return response;
    } catch (corsError) {
      console.log('Direct fetch failed, trying CORS proxy...', corsError);
      
      // Try multiple CORS proxies for better reliability
      const proxies = [
        `https://api.allorigins.win/get?url=${encodeURIComponent(url)}`,
        `https://corsproxy.io/?${encodeURIComponent(url)}`,
        `https://api.codetabs.com/v1/proxy?quest=${encodeURIComponent(url)}`
      ];

      let lastError;
      for (let i = 0; i < proxies.length; i++) {
        const proxyUrl = proxies[i];
        console.log(`Trying proxy ${i + 1}/3: ${proxyUrl}`);
        
        try {
          const response = await fetch(proxyUrl);
          console.log(`Proxy ${i + 1} response: ${response.status} ${response.statusText}`);
          
          if (response.ok) {
            if (proxyUrl.includes('allorigins.win')) {
              const data = await response.json();
              console.log('Proxy data received, status:', data.status);
              return new Response(data.contents, {
                status: data.status?.http_code || 200,
                statusText: 'OK'
              });
            } else if (proxyUrl.includes('corsproxy.io')) {
              const html = await response.text();
              return new Response(html, {
                status: 200,
                statusText: 'OK'
              });
            } else if (proxyUrl.includes('codetabs.com')) {
              const data = await response.json();
              return new Response(data.contents, {
                status: 200,
                statusText: 'OK'
              });
            }
          } else {
            throw new Error(`Proxy ${i + 1} failed: ${response.status} ${response.statusText}`);
          }
        } catch (proxyError) {
          console.log(`Proxy ${i + 1} failed:`, proxyError);
          lastError = proxyError;
          continue; // Try next proxy
        }
      }
      
      console.error('All proxies failed');
      throw new Error(`All methods failed. Direct: ${corsError.message}, Proxies: ${lastError?.message}`);
    }
  }

  private parseWebsiteContent(html: string, url: string, type: 'funder' | 'applicant'): WebsiteContext {
    // Create a DOM parser
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    // Extract basic information
    const title = doc.querySelector('title')?.textContent?.trim() || 'Untitled';
    
    // Extract meta description
    const metaDescription = doc.querySelector('meta[name="description"]')?.getAttribute('content')?.trim();
    
    // Extract mission/about information
    const mission = this.extractMission(doc, type);
    
    // Extract key information based on type
    const keyInfo = this.extractKeyInfo(doc, type);
    
    // Extract structured funder information if this is a funder
    const funderInfo = type === 'funder' ? this.extractStructuredFunderInfo(doc) : undefined;
    
    // Extract structured applicant information if this is an applicant
    const applicantInfo = type === 'applicant' ? this.extractStructuredApplicantInfo(doc) : undefined;
    
    // Extract contact information
    const contactInfo = this.extractContactInfo(doc);
    
    // Check for website age indicators
    const warnings = this.detectWebsiteWarnings(doc, html);
    
    // Calculate confidence score
    const confidence = this.calculateConfidence(title, mission, keyInfo, warnings, funderInfo, applicantInfo);

    return {
      url,
      accessible: true,
      title,
      mission: mission || metaDescription,
      description: metaDescription,
      keyInfo,
      funderInfo,
      applicantInfo,
      contactInfo,
      warnings,
      extractedAt: new Date(),
      confidence
    };
  }

  private extractMission(doc: Document, type: 'funder' | 'applicant'): string | undefined {
    // Look for mission-related content
    const missionSelectors = [
      '[class*="mission"]',
      '[class*="about"]',
      '[id*="mission"]',
      '[id*="about"]',
      'h1, h2, h3',
      '.mission-statement',
      '.about-us'
    ];

    for (const selector of missionSelectors) {
      const elements = doc.querySelectorAll(selector);
      for (const element of elements) {
        const text = element.textContent?.trim();
        if (text && text.length > 50 && text.length < 500) {
          // Filter for mission-like content
          if (text.toLowerCase().includes('mission') || 
              text.toLowerCase().includes('purpose') ||
              text.toLowerCase().includes('dedicated') ||
              text.toLowerCase().includes('committed')) {
            return text;
          }
        }
      }
    }

    // Fallback: get first substantial paragraph
    const paragraphs = doc.querySelectorAll('p');
    for (const p of paragraphs) {
      const text = p.textContent?.trim();
      if (text && text.length > 100 && text.length < 400) {
        return text;
      }
    }

    return undefined;
  }

  private extractKeyInfo(doc: Document, type: 'funder' | 'applicant'): string[] {
    const keyInfo: string[] = [];

    if (type === 'funder') {
      // Look for funding-specific information (keeping for backward compatibility)
      const fundingKeywords = ['grant', 'funding', 'award', 'program', 'eligibility', 'deadline'];
      const elements = doc.querySelectorAll('h1, h2, h3, h4, li, strong');
      
      elements.forEach(element => {
        const text = element.textContent?.trim();
        if (text && fundingKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
          if (text.length < 200 && !keyInfo.includes(text)) {
            keyInfo.push(text);
          }
        }
      });
    } else {
      // Look for organization-specific information
      const orgKeywords = ['program', 'service', 'community', 'impact', 'founded', 'established', 'serving'];
      const elements = doc.querySelectorAll('h1, h2, h3, h4, li, strong');
      
      elements.forEach(element => {
        const text = element.textContent?.trim();
        if (text && orgKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
          if (text.length < 200 && !keyInfo.includes(text)) {
            keyInfo.push(text);
          }
        }
      });
    }

    return keyInfo.slice(0, 10); // Limit to top 10 items
  }

  private extractStructuredFunderInfo(doc: Document): WebsiteContext['funderInfo'] {
    return {
      about: this.extractAboutSection(doc),
      pastFundings: this.extractPastFundings(doc),
      fundingPriorities: this.extractFundingPriorities(doc)
    };
  }

  private extractAboutSection(doc: Document) {
    const about = {
      missionStatement: undefined as string | undefined,
      organizationalGoals: [] as string[],
      strategicObjectives: [] as string[]
    };

    // Extract mission statement
    const missionSelectors = [
      '[class*="mission"]', '[id*="mission"]',
      '[class*="about"]', '[id*="about"]'
    ];

    // Try CSS selectors first
    for (const selector of missionSelectors) {
      try {
        const elements = doc.querySelectorAll(selector);
        for (const element of elements) {
          const text = element.textContent?.trim();
          if (text && text.length > 50 && text.length < 500) {
            if (text.toLowerCase().includes('mission') || 
                text.toLowerCase().includes('purpose') ||
                text.toLowerCase().includes('dedicated')) {
              about.missionStatement = text;
              break;
            }
          }
        }
        if (about.missionStatement) break;
      } catch (error) {
        console.warn(`Invalid selector: ${selector}`, error);
        continue;
      }
    }

    // If no mission found with CSS selectors, search through heading elements
    if (!about.missionStatement) {
      const headings = doc.querySelectorAll('h1, h2, h3, h4, h5, h6');
      for (const heading of headings) {
        const text = heading.textContent?.trim();
        if (text && text.length > 50 && text.length < 500) {
          if (text.toLowerCase().includes('mission') || 
              text.toLowerCase().includes('purpose') ||
              text.toLowerCase().includes('dedicated')) {
            about.missionStatement = text;
            break;
          }
        }
      }
    }

    // Extract organizational goals
    const goalKeywords = ['goal', 'objective', 'aim', 'priority', 'focus', 'commitment'];
    const elements = doc.querySelectorAll('h1, h2, h3, h4, li, p');
    
    elements.forEach(element => {
      const text = element.textContent?.trim();
      if (text && goalKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        if (text.length > 20 && text.length < 300) {
          if (text.toLowerCase().includes('goal') || text.toLowerCase().includes('objective')) {
            about.organizationalGoals.push(text);
          } else if (text.toLowerCase().includes('strategic') || text.toLowerCase().includes('priority')) {
            about.strategicObjectives.push(text);
          }
        }
      }
    });

    // Limit arrays
    about.organizationalGoals = about.organizationalGoals.slice(0, 5);
    about.strategicObjectives = about.strategicObjectives.slice(0, 5);

    return about;
  }

  private extractPastFundings(doc: Document) {
    const pastFundings = {
      recentRecipients: [] as string[],
      fundedProjects: [] as string[],
      awardAmounts: [] as string[]
    };

    // Look for recipient information
    const recipientKeywords = ['recipient', 'winner', 'awarded to', 'granted to', 'university', 'institution'];
    const projectKeywords = ['project', 'research', 'initiative', 'program', 'study'];
    const amountKeywords = ['€', '$', 'million', 'billion', 'funding', 'grant', 'award'];

    const elements = doc.querySelectorAll('p, li, div, span');
    
    elements.forEach(element => {
      const text = element.textContent?.trim();
      if (!text || text.length < 10) return;

      // Skip JSON, technical content, and code-like strings
      if (text.includes('{') || text.includes('}') || 
          text.includes('"service":') || text.includes('"version":') ||
          text.includes('{"') || text.includes('"}') ||
          text.startsWith('[{') || text.endsWith('}]')) {
        return; // Skip this element
      }

      // Extract recipients
      if (recipientKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        if (text.length < 200) {
          pastFundings.recentRecipients.push(text);
        }
      }

      // Extract projects
      if (projectKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        if (text.length < 300 && text.length > 20) {
          pastFundings.fundedProjects.push(text);
        }
      }

      // Extract amounts
      if (amountKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        const amountMatch = text.match(/(€|$|\£)[\d,.]+(?: ?(million|billion|k|thousand))?/gi);
        if (amountMatch) {
          pastFundings.awardAmounts.push(...amountMatch);
        }
      }
    });

    // Limit arrays and remove duplicates
    pastFundings.recentRecipients = [...new Set(pastFundings.recentRecipients)].slice(0, 10);
    pastFundings.fundedProjects = [...new Set(pastFundings.fundedProjects)].slice(0, 10);
    pastFundings.awardAmounts = [...new Set(pastFundings.awardAmounts)].slice(0, 10);

    return pastFundings;
  }

  private extractFundingPriorities(doc: Document) {
    const priorities = {
      currentCalls: [] as string[],
      priorityThemes: [] as string[],
      evaluationCriteria: [] as string[],
      strategicFocus: [] as string[]
    };

    // Extract current calls
    const callKeywords = ['call for', 'open call', 'application', 'deadline', 'submit', 'apply'];
    const themeKeywords = ['theme', 'priority', 'focus area', 'pillar', 'cluster', 'challenge'];
    const criteriaKeywords = ['criteria', 'evaluation', 'assessment', 'scoring', 'review'];
    const focusKeywords = ['strategic', 'innovation', 'research', 'climate', 'digital', 'health'];

    const elements = doc.querySelectorAll('h1, h2, h3, h4, li, p, strong');
    
    elements.forEach(element => {
      const text = element.textContent?.trim();
      if (!text || text.length < 10) return;

      // Extract current calls
      if (callKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        if (text.length < 250) {
          priorities.currentCalls.push(text);
        }
      }

      // Extract priority themes
      if (themeKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        if (text.length < 200 && text.length > 15) {
          priorities.priorityThemes.push(text);
        }
      }

      // Extract evaluation criteria
      if (criteriaKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        if (text.length < 300 && text.length > 20) {
          priorities.evaluationCriteria.push(text);
        }
      }

      // Extract strategic focus
      if (focusKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        if (text.length < 200 && text.length > 15) {
          priorities.strategicFocus.push(text);
        }
      }
    });

    // Limit arrays and remove duplicates
    priorities.currentCalls = [...new Set(priorities.currentCalls)].slice(0, 8);
    priorities.priorityThemes = [...new Set(priorities.priorityThemes)].slice(0, 8);
    priorities.evaluationCriteria = [...new Set(priorities.evaluationCriteria)].slice(0, 6);
    priorities.strategicFocus = [...new Set(priorities.strategicFocus)].slice(0, 8);

    return priorities;
  }

  private extractStructuredApplicantInfo(doc: Document): WebsiteContext['applicantInfo'] {
    return {
      researchCapabilities: this.extractResearchCapabilities(doc),
      trackRecord: this.extractTrackRecord(doc),
      resources: this.extractResources(doc)
    };
  }

  private extractResearchCapabilities(doc: Document) {
    const capabilities = {
      expertiseAreas: [] as string[],
      researchCenters: [] as string[],
      keyFaculty: [] as string[],
      academicDepartments: [] as string[]
    };

    // Extract expertise areas
    const expertiseKeywords = ['research', 'expertise', 'specializ', 'focus', 'field', 'discipline', 'study'];
    const centerKeywords = ['center', 'centre', 'institute', 'laboratory', 'lab', 'school', 'faculty'];
    const facultyKeywords = ['professor', 'dr.', 'phd', 'researcher', 'scientist', 'academic'];
    const deptKeywords = ['department', 'division', 'school of', 'faculty of'];

    const elements = doc.querySelectorAll('h1, h2, h3, h4, li, p, strong, a');
    
    elements.forEach(element => {
      const text = element.textContent?.trim();
      if (!text || text.length < 5) return;

      // Extract expertise areas
      if (expertiseKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        if (text.length < 150 && text.length > 10) {
          capabilities.expertiseAreas.push(text);
        }
      }

      // Extract research centers
      if (centerKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        if (text.length < 100 && text.length > 10) {
          capabilities.researchCenters.push(text);
        }
      }

      // Extract key faculty (look for academic titles)
      if (facultyKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        if (text.length < 80 && text.length > 8) {
          capabilities.keyFaculty.push(text);
        }
      }

      // Extract departments
      if (deptKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        if (text.length < 80 && text.length > 10) {
          capabilities.academicDepartments.push(text);
        }
      }
    });

    // Remove duplicates and limit
    capabilities.expertiseAreas = [...new Set(capabilities.expertiseAreas)].slice(0, 8);
    capabilities.researchCenters = [...new Set(capabilities.researchCenters)].slice(0, 10);
    capabilities.keyFaculty = [...new Set(capabilities.keyFaculty)].slice(0, 8);
    capabilities.academicDepartments = [...new Set(capabilities.academicDepartments)].slice(0, 8);

    return capabilities;
  }

  private extractTrackRecord(doc: Document) {
    const trackRecord = {
      previousGrants: [] as string[],
      notableProjects: [] as string[],
      publications: [] as string[],
      awards: [] as string[]
    };

    const grantKeywords = ['grant', 'funding', 'awarded', 'received', 'sponsored'];
    const projectKeywords = ['project', 'research', 'initiative', 'collaboration', 'study'];
    const publicationKeywords = ['publication', 'journal', 'paper', 'article', 'book', 'published'];
    const awardKeywords = ['award', 'prize', 'recognition', 'honor', 'distinction', 'medal'];

    const elements = doc.querySelectorAll('p, li, div, span, strong');
    
    elements.forEach(element => {
      const text = element.textContent?.trim();
      if (!text || text.length < 10) return;

      // Extract grants
      if (grantKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        if (text.length < 200 && text.includes('€') || text.includes('$') || text.includes('£')) {
          trackRecord.previousGrants.push(text);
        }
      }

      // Extract projects
      if (projectKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        if (text.length < 250 && text.length > 20) {
          trackRecord.notableProjects.push(text);
        }
      }

      // Extract publications
      if (publicationKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        if (text.length < 200 && text.length > 15) {
          trackRecord.publications.push(text);
        }
      }

      // Extract awards
      if (awardKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        if (text.length < 150 && text.length > 10) {
          trackRecord.awards.push(text);
        }
      }
    });

    // Remove duplicates and limit
    trackRecord.previousGrants = [...new Set(trackRecord.previousGrants)].slice(0, 8);
    trackRecord.notableProjects = [...new Set(trackRecord.notableProjects)].slice(0, 8);
    trackRecord.publications = [...new Set(trackRecord.publications)].slice(0, 8);
    trackRecord.awards = [...new Set(trackRecord.awards)].slice(0, 8);

    return trackRecord;
  }

  private extractResources(doc: Document) {
    const resources = {
      facilities: [] as string[],
      equipment: [] as string[],
      collaborations: [] as string[],
      supportServices: [] as string[]
    };

    const facilityKeywords = ['facility', 'building', 'campus', 'library', 'laboratory', 'lab', 'space'];
    const equipmentKeywords = ['equipment', 'instrument', 'technology', 'infrastructure', 'resource'];
    const collaborationKeywords = ['partnership', 'collaboration', 'network', 'alliance', 'consortium'];
    const serviceKeywords = ['service', 'support', 'office', 'center', 'help', 'assistance'];

    const elements = doc.querySelectorAll('h1, h2, h3, h4, li, p, strong');
    
    elements.forEach(element => {
      const text = element.textContent?.trim();
      if (!text || text.length < 8) return;

      // Extract facilities
      if (facilityKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        if (text.length < 120 && text.length > 10) {
          resources.facilities.push(text);
        }
      }

      // Extract equipment
      if (equipmentKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        if (text.length < 150 && text.length > 10) {
          resources.equipment.push(text);
        }
      }

      // Extract collaborations
      if (collaborationKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        if (text.length < 120 && text.length > 15) {
          resources.collaborations.push(text);
        }
      }

      // Extract support services
      if (serviceKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
        if (text.length < 100 && text.length > 12) {
          resources.supportServices.push(text);
        }
      }
    });

    // Remove duplicates and limit
    resources.facilities = [...new Set(resources.facilities)].slice(0, 8);
    resources.equipment = [...new Set(resources.equipment)].slice(0, 8);
    resources.collaborations = [...new Set(resources.collaborations)].slice(0, 8);
    resources.supportServices = [...new Set(resources.supportServices)].slice(0, 8);

    return resources;
  }

  private extractContactInfo(doc: Document): WebsiteContext['contactInfo'] {
    const contactInfo: WebsiteContext['contactInfo'] = {};

    // Extract email
    const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/;
    const bodyText = doc.body.textContent || '';
    const emailMatch = bodyText.match(emailRegex);
    if (emailMatch) {
      contactInfo.email = emailMatch[0];
    }

    // Extract phone (basic US format)
    const phoneRegex = /\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})/;
    const phoneMatch = bodyText.match(phoneRegex);
    if (phoneMatch) {
      contactInfo.phone = phoneMatch[0];
    }

    return Object.keys(contactInfo).length > 0 ? contactInfo : undefined;
  }

  private detectWebsiteWarnings(doc: Document, html: string): string[] {
    const warnings: string[] = [];

    // Check for copyright year to estimate age
    const copyrightRegex = /copyright.*?(\d{4})/i;
    const copyrightMatch = html.match(copyrightRegex);
    if (copyrightMatch) {
      const copyrightYear = parseInt(copyrightMatch[1]);
      const currentYear = new Date().getFullYear();
      if (currentYear - copyrightYear > 3) {
        warnings.push(`Website appears to be from ${copyrightYear} (${currentYear - copyrightYear} years old)`);
      }
    }

    // Check for other age indicators
    const lastUpdatedRegex = /last updated.*?(\d{4})/i;
    const updateMatch = html.match(lastUpdatedRegex);
    if (updateMatch) {
      const updateYear = parseInt(updateMatch[1]);
      const currentYear = new Date().getFullYear();
      if (currentYear - updateYear > 2) {
        warnings.push(`Last updated in ${updateYear}`);
      }
    }

    // Check for broken images or links (basic check)
    const brokenImages = doc.querySelectorAll('img[src=""], img:not([src])').length;
    if (brokenImages > 2) {
      warnings.push('Website may have maintenance issues (broken images detected)');
    }

    return warnings;
  }

  private calculateConfidence(title: string, mission?: string, keyInfo: string[] = [], warnings: string[] = [], funderInfo?: WebsiteContext['funderInfo'], applicantInfo?: WebsiteContext['applicantInfo']): number {
    let confidence = 0.5; // Base confidence

    // Increase confidence for good content
    if (title && title !== 'Untitled') confidence += 0.1;
    if (mission && mission.length > 50) confidence += 0.2;
    if (keyInfo.length > 3) confidence += 0.1;
    
    // Increase confidence for structured funder information
    if (funderInfo) {
      if (funderInfo.about?.missionStatement) confidence += 0.1;
      if (funderInfo.about?.organizationalGoals?.length > 0) confidence += 0.05;
      if (funderInfo.pastFundings?.recentRecipients?.length > 0) confidence += 0.1;
      if (funderInfo.pastFundings?.awardAmounts?.length > 0) confidence += 0.05;
      if (funderInfo.fundingPriorities?.currentCalls?.length > 0) confidence += 0.1;
      if (funderInfo.fundingPriorities?.priorityThemes?.length > 0) confidence += 0.05;
    }
    
    // Increase confidence for structured applicant information
    if (applicantInfo) {
      if (applicantInfo.researchCapabilities?.expertiseAreas?.length > 0) confidence += 0.1;
      if (applicantInfo.researchCapabilities?.researchCenters?.length > 0) confidence += 0.05;
      if (applicantInfo.trackRecord?.previousGrants?.length > 0) confidence += 0.1;
      if (applicantInfo.trackRecord?.notableProjects?.length > 0) confidence += 0.05;
      if (applicantInfo.resources?.facilities?.length > 0) confidence += 0.05;
      if (applicantInfo.resources?.collaborations?.length > 0) confidence += 0.05;
    }
    
    // Decrease confidence for warnings
    confidence -= warnings.length * 0.1;

    // Ensure confidence stays within bounds
    return Math.max(0.1, Math.min(1.0, confidence));
  }

  private createFallbackContext(url: string, type: 'funder' | 'applicant', error: string): WebsiteContext {
    return {
      url,
      accessible: false,
      title: `${type} website not accessible`,
      mission: undefined,
      description: undefined,
      keyInfo: [],
      funderInfo: undefined,
      applicantInfo: undefined,
      contactInfo: undefined,
      warnings: [`Website not accessible: ${error}`],
      extractedAt: new Date(),
      confidence: 0.1
    };
  }

  async extractBothContexts(funderUrl: string, applicantUrl: string): Promise<ExtractedContexts> {
    console.log('Extracting contexts from both websites...');

    const [funderContext, applicantContext] = await Promise.allSettled([
      this.extractWebsiteContext(funderUrl, 'funder'),
      this.extractWebsiteContext(applicantUrl, 'applicant')
    ]);

    return {
      funder: funderContext.status === 'fulfilled' ? funderContext.value : null,
      applicant: applicantContext.status === 'fulfilled' ? applicantContext.value : null
    };
  }
}