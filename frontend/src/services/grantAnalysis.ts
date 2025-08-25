// Grant analysis service for Model Testing Playground

export class GrantAnalysisService {
  private static instance: GrantAnalysisService;

  static getInstance(): GrantAnalysisService {
    if (!GrantAnalysisService.instance) {
      GrantAnalysisService.instance = new GrantAnalysisService();
    }
    return GrantAnalysisService.instance;
  }

  async processDocument(
    text: string,
    fileName: string,
    fileType: string,
    onProgress?: (status: any) => void
  ): Promise<{ analysis: any }> {
    onProgress?.({ message: 'Analyzing document structure...' });
    
    // Simple analysis for demo
    const analysis = {
      isGrantRelated: text.toLowerCase().includes('grant') || text.toLowerCase().includes('funding'),
      documentType: fileName.toLowerCase().includes('application') ? 'grant_application' : 'grant_opportunity',
      keyEntities: ['Organization', 'Funding', 'Project'],
      confidence: 0.8,
    };
    
    return { analysis };
  }
}