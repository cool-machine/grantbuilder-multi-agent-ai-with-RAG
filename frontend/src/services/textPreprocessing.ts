// Text preprocessing service for Model Testing Playground

export class TextPreprocessor {
  private static instance: TextPreprocessor;

  static getInstance(): TextPreprocessor {
    if (!TextPreprocessor.instance) {
      TextPreprocessor.instance = new TextPreprocessor();
    }
    return TextPreprocessor.instance;
  }

  preprocessText(text: string): string {
    // Basic text preprocessing
    return text
      .replace(/\s+/g, ' ') // Normalize whitespace
      .replace(/\n\s*\n/g, '\n\n') // Clean up excessive newlines
      .trim();
  }

  getPreprocessingStats(originalText: string, preprocessedText: string) {
    return {
      originalLength: originalText.length,
      preprocessedLength: preprocessedText.length,
      reductionPercent: Math.round(((originalText.length - preprocessedText.length) / originalText.length) * 100)
    };
  }
}