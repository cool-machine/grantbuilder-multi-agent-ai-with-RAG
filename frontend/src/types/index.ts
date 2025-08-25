// Types for the Model Testing Playground and Document Processing

export interface ExtractedDocument {
  id: string;
  fileName: string;
  fileType: string;
  extractedText: string;
  preprocessedText?: string;
  tokenizedData?: any;
  aiAnalysis?: any;
  wordCount: number;
  extractedAt: Date;
  metadata?: {
    preprocessingStats?: any;
  };
}

export interface ProcessingStatus {
  id: string;
  status: 'extracting' | 'processing' | 'completed' | 'error';
  progress: number;
  message: string;
  error?: string;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  extractedText?: string;
  promptTemplate?: string;
  finalPrompt?: string;
}

export interface NGOProfile {
  name: string;
  mission: string;
  focusAreas: string;
  targetPopulation: string;
  geographicScope: string;
  established: string;
  staff: string;
  budget: string;
}