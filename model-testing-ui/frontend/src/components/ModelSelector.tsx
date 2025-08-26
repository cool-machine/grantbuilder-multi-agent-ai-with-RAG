import React from 'react';
import { Cpu, MemoryStick, Clock, AlertCircle, CheckCircle } from 'lucide-react';

interface Model {
  id: string;
  name: string;
  size: string;
  type: string;
  description: string;
}

interface ModelSelectorProps {
  models: Record<string, Model>;
  currentModel: string | null;
  onModelChange: (modelKey: string) => void;
  apiBaseUrl: string;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({
  models,
  currentModel,
  onModelChange,
  apiBaseUrl,
  isLoading,
  setIsLoading
}) => {
  const [loadingModel, setLoadingModel] = React.useState<string | null>(null);
  const [loadError, setLoadError] = React.useState<string | null>(null);

  const handleModelSelect = async (modelKey: string) => {
    if (isLoading || modelKey === currentModel) return;

    setLoadingModel(modelKey);
    setIsLoading(true);
    setLoadError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/load_model`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ model_key: modelKey }),
      });

      const data = await response.json();

      if (response.ok) {
        onModelChange(modelKey);
      } else {
        setLoadError(data.error || 'Failed to load model');
      }
    } catch (error) {
      setLoadError('Network error: Could not connect to backend');
    } finally {
      setLoadingModel(null);
      setIsLoading(false);
    }
  };

  const getSizeColor = (size: string) => {
    if (size.includes('B')) return 'text-red-600'; // Billions
    if (size.includes('M') && parseInt(size) > 500) return 'text-yellow-600'; // Large millions
    return 'text-green-600'; // Small models
  };

  const getModelIcon = (size: string) => {
    if (size.includes('20B')) return <MemoryStick className="h-5 w-5 text-red-500" />;
    if (size.includes('7B')) return <MemoryStick className="h-5 w-5 text-yellow-500" />;
    return <Cpu className="h-5 w-5 text-green-500" />;
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Available Models
        </h3>

        {loadError && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <div className="flex items-center">
              <AlertCircle className="h-4 w-4 text-red-400 mr-2" />
              <span className="text-red-700 text-sm">{loadError}</span>
            </div>
          </div>
        )}

        <div className="space-y-3">
          {Object.entries(models).map(([key, model]) => (
            <div
              key={key}
              onClick={() => handleModelSelect(key)}
              className={`model-card ${
                currentModel === key ? 'selected' : ''
              } ${
                isLoading || loadingModel ? 'loading' : ''
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  {getModelIcon(model.size)}
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{model.name}</h4>
                    <p className="text-xs text-gray-500 mt-1">{model.description}</p>
                    
                    <div className="flex items-center space-x-4 mt-2">
                      <span className={`text-xs font-medium ${getSizeColor(model.size)}`}>
                        {model.size} parameters
                      </span>
                      <span className="text-xs text-gray-400">{model.type}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center">
                  {loadingModel === key && (
                    <div className="spinner mr-2" />
                  )}
                  {currentModel === key && !loadingModel && (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {currentModel && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
            <div className="flex items-center">
              <CheckCircle className="h-4 w-4 text-blue-500 mr-2" />
              <span className="text-blue-700 text-sm font-medium">
                {models[currentModel]?.name} is loaded and ready
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ModelSelector;