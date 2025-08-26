import React, { useState } from 'react';

interface ProcessingOption {
  id: string;
  name: string;
  description: string;
  estimatedTime: string;
  estimatedCost: string;
  confidence: string;
  available: boolean;
}

interface DocumentProcessorSelectorProps {
  onProcessingModeChange: (mode: string) => void;
  selectedMode: string;
}

const DocumentProcessorSelector: React.FC<DocumentProcessorSelectorProps> = ({
  onProcessingModeChange,
  selectedMode
}) => {
  const processingOptions: ProcessingOption[] = [
    {
      id: 'quick-fill',
      name: '⚡ Quick Fill (Current)',
      description: 'Fast field-by-field filling with GPT-OSS-120B',
      estimatedTime: '~35 seconds',
      estimatedCost: '$0.25-0.70',
      confidence: '80%',
      available: true
    },
    {
      id: 'azure-deepseek',
      name: '🔧 Azure Services + DeepSeek R1',
      description: 'Advanced document extraction + 6-agent reasoning system',
      estimatedTime: '~60-90 seconds',
      estimatedCost: '$0.50-1.35',
      confidence: '95%',
      available: true
    },
    {
      id: 'o3-multimodal',
      name: '🧠 o3 Multimodal (Future)',
      description: 'Direct PDF processing with multimodal reasoning',
      estimatedTime: '~30 seconds',
      estimatedCost: '$2.00 (est.)',
      confidence: '98% (est.)',
      available: false
    }
  ];

  const [showDetails, setShowDetails] = useState(false);

  return (
    <div className=\"bg-white rounded-lg shadow-md p-6 mb-6\">
      <div className=\"flex items-center justify-between mb-4\">
        <h3 className=\"text-lg font-semibold text-gray-800\">
          AI Processing Method
        </h3>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className=\"text-sm text-blue-600 hover:text-blue-800\"
        >
          {showDetails ? 'Hide Details' : 'Show Details'}
        </button>
      </div>

      <div className=\"space-y-3\">
        {processingOptions.map((option) => (
          <div
            key={option.id}
            className={`relative border-2 rounded-lg p-4 cursor-pointer transition-all ${
              selectedMode === option.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            } ${!option.available ? 'opacity-60 cursor-not-allowed' : ''}`}
            onClick={() => option.available && onProcessingModeChange(option.id)}
          >
            <div className=\"flex items-start justify-between\">
              <div className=\"flex items-center space-x-3\">
                <input
                  type=\"radio\"
                  name=\"processing-mode\"
                  value={option.id}
                  checked={selectedMode === option.id}
                  onChange={() => option.available && onProcessingModeChange(option.id)}
                  disabled={!option.available}
                  className=\"mt-1\"
                />
                <div>
                  <div className=\"flex items-center space-x-2\">
                    <h4 className=\"font-medium text-gray-900\">{option.name}</h4>
                    {!option.available && (
                      <span className=\"px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded\">
                        Coming Soon
                      </span>
                    )}
                  </div>
                  <p className=\"text-sm text-gray-600 mt-1\">{option.description}</p>
                  
                  {showDetails && (
                    <div className=\"mt-3 grid grid-cols-3 gap-4 text-sm\">
                      <div>
                        <span className=\"font-medium text-gray-700\">Time:</span>
                        <div className=\"text-gray-600\">{option.estimatedTime}</div>
                      </div>
                      <div>
                        <span className=\"font-medium text-gray-700\">Cost:</span>
                        <div className=\"text-gray-600\">{option.estimatedCost}</div>
                      </div>
                      <div>
                        <span className=\"font-medium text-gray-700\">Quality:</span>
                        <div className=\"text-gray-600\">{option.confidence}</div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Feature highlights */}
            {showDetails && option.id === 'azure-deepseek' && (
              <div className=\"mt-4 pt-3 border-t border-gray-200\">
                <h5 className=\"font-medium text-gray-700 mb-2\">Features:</h5>
                <div className=\"grid grid-cols-2 gap-2 text-sm text-gray-600\">
                  <div>✅ Advanced PDF extraction</div>
                  <div>✅ Table & chart analysis</div>
                  <div>✅ 6 specialized AI agents</div>
                  <div>✅ 671B parameter reasoning</div>
                  <div>✅ Comprehensive strategy</div>
                  <div>✅ Inter-agent collaboration</div>
                </div>
              </div>
            )}

            {showDetails && option.id === 'o3-multimodal' && (
              <div className=\"mt-4 pt-3 border-t border-gray-200\">
                <h5 className=\"font-medium text-gray-700 mb-2\">When Available:</h5>
                <div className=\"text-sm text-gray-600\">
                  <div>🔮 Direct multimodal PDF understanding</div>
                  <div>🔮 Single model does everything</div>
                  <div>🔮 Superior visual reasoning</div>
                  <div>🔮 Fastest processing time</div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Current selection summary */}
      <div className=\"mt-4 p-3 bg-gray-50 rounded-lg\">
        <div className=\"text-sm text-gray-700\">
          <strong>Selected:</strong> {processingOptions.find(opt => opt.id === selectedMode)?.name}
        </div>
        <div className=\"text-xs text-gray-600 mt-1\">
          {processingOptions.find(opt => opt.id === selectedMode)?.description}
        </div>
      </div>
    </div>
  );
};

export default DocumentProcessorSelector;