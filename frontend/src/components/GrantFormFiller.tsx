import React, { useState, useEffect } from 'react';
import { FileText, Upload, Wand2, Download, AlertCircle, CheckCircle, Globe, FileUp, Eye } from 'lucide-react';
import { useGrants } from '../contexts/GrantContext';
import DocumentProcessorSelector from './DocumentProcessorSelector';
import MultiAgentChatWindow from './MultiAgentChatWindow';

interface NGOProfile {
  organization_name: string;
  mission: string;
  years_active: number;
  focus_areas: string[];
  annual_budget: number;
}

interface NGODataSources {
  basic_info: {
    organization_name: string;
    contact_email?: string;
    phone?: string;
  };
  profile_pdf?: File;
  website_url?: string;
  manual_details?: {
    mission: string;
    years_active: number;
    focus_areas: string[];
    annual_budget: number;
    recent_projects?: string;
  };
}

interface GrantContext {
  funder_name: string;
  focus_area: string;
  max_amount: number;
  requirements: string;
}

interface FilledFormResponse {
  success: boolean;
  original_fields: any[];
  classified_fields: any;
  filled_responses: Record<string, string>;
  filled_pdf?: {
    data: string;
    filename: string;
    content_type: string;
    encoding: string;
  };
  pdf_analysis?: {
    total_pages: number;
    has_form_fields: boolean;
    form_fields: string[];
  };
  processing_summary?: {
    total_fields: number;
    filled_fields: number;
    fill_rate: number;
    pdf_generation?: {
      success: boolean;
      method: string;
    };
  };
  // Multi-Agent Framework Response
  result?: string;
  chat_history?: any[];
  tasks?: any[];
  deliverables?: any[];
}

interface GrantFormFillerProps {
  grantId?: string;
}

export const GrantFormFiller: React.FC<GrantFormFillerProps> = ({ grantId }) => {
  const { getGrantById } = useGrants();
  const selectedGrant = grantId ? getGrantById(grantId) : undefined;
  
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<FilledFormResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [processingMode, setProcessingMode] = useState<string>('multi-agent-framework'); // Default to new system
  
  // Multi-Agent Chat State
  const [showChatWindow, setShowChatWindow] = useState(false);
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  
  // New multi-source NGO data - Demo-ready defaults (Teach for America)
  const [ngoDataSources, setNgoDataSources] = useState<NGODataSources>({
    basic_info: {
      organization_name: "Teach for America Appalachia",
      contact_email: "info@teachforamerica.org",
      phone: "(212) 279-2080"
    },
    website_url: "https://www.teachforamerica.org/",
    manual_details: {
      mission: "Find, develop, and support equity-oriented leaders to transform education and expand opportunity for all children",
      years_active: 35,
      focus_areas: ["education", "teacher training", "rural education", "equity"],
      annual_budget: 245000000,
      recent_projects: "Strengthening teacher pipelines in rural Appalachian communities, placing 3,500+ new teachers annually in high-need schools, developing leadership development programs for educators in underserved areas"
    }
  });
  
  // UI state for data source selection - Demo-ready with website and manual enabled
  const [activeDataSources, setActiveDataSources] = useState({
    pdf: false,
    website: true,
    manual: true
  });
  
  // Legacy NGO profile for backward compatibility - now derived from ngoDataSources
  const ngoProfile: NGOProfile = {
    organization_name: ngoDataSources.basic_info.organization_name,
    mission: ngoDataSources.manual_details?.mission || "",
    years_active: ngoDataSources.manual_details?.years_active || 0,
    focus_areas: ngoDataSources.manual_details?.focus_areas || [],
    annual_budget: ngoDataSources.manual_details?.annual_budget || 0
  };

  // Demo grant context - Ready for Teach for America scenario
  const [grantContext, setGrantContext] = useState<GrantContext>({
    funder_name: "Appalachian Regional Commission",
    focus_area: "rural education and teacher training",
    max_amount: 500000,
    requirements: "Must serve rural Appalachian communities with measurable teacher placement outcomes"
  });

  // Auto-populate grant context when a specific grant is selected
  useEffect(() => {
    if (selectedGrant) {
      setGrantContext({
        funder_name: selectedGrant.funder,
        focus_area: selectedGrant.categories.join(', '),
        max_amount: selectedGrant.amount.max,
        requirements: selectedGrant.description.en // Use description as requirements context
      });
    }
  }, [selectedGrant]);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setError(null);
    } else {
      setError('Please select a PDF file');
    }
  };

  const handleNGOProfileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setNgoDataSources({
        ...ngoDataSources,
        profile_pdf: file
      });
      setActiveDataSources({
        ...activeDataSources,
        pdf: true
      });
      setError(null);
    } else {
      setError('Please select a PDF file for NGO profile');
    }
  };

  const handleWebsiteChange = (url: string) => {
    setNgoDataSources({
      ...ngoDataSources,
      website_url: url
    });
    setActiveDataSources({
      ...activeDataSources,
      website: url.length > 0
    });
  };

  const toggleDataSource = (source: 'pdf' | 'website' | 'manual') => {
    setActiveDataSources({
      ...activeDataSources,
      [source]: !activeDataSources[source]
    });
  };

  const convertFileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const base64String = reader.result as string;
        // Remove data URL prefix
        const base64Data = base64String.split(',')[1];
        resolve(base64Data);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const fillGrantForm = async () => {
    if (!selectedFile) {
      setError('Please select a PDF file first');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      // Convert PDF to base64
      const pdfData = await convertFileToBase64(selectedFile);

      // Call Azure Function
      // Prepare NGO profile data from multiple sources
      let ngoProfileData = {
        organization_name: ngoDataSources.basic_info.organization_name,
        contact_email: ngoDataSources.basic_info.contact_email,
        phone: ngoDataSources.basic_info.phone,
      };

      // Add manual details if enabled
      if (activeDataSources.manual && ngoDataSources.manual_details) {
        ngoProfileData = {
          ...ngoProfileData,
          ...ngoDataSources.manual_details
        };
      }

      // Prepare request body
      const requestBody: any = {
        pdf_data: pdfData,
        ngo_profile: ngoProfileData,
        grant_context: grantContext,
        processing_mode: processingMode, // Add processing mode selection
        data_sources: {
          has_profile_pdf: activeDataSources.pdf && ngoDataSources.profile_pdf,
          has_website: activeDataSources.website && ngoDataSources.website_url,
          website_url: ngoDataSources.website_url || null
        }
      };

      // Add NGO profile PDF if provided
      if (activeDataSources.pdf && ngoDataSources.profile_pdf) {
        const profilePdfData = await convertFileToBase64(ngoDataSources.profile_pdf);
        requestBody.ngo_profile_pdf = profilePdfData;
      }

      // Call Azure Functions backend - NO FALLBACKS
      const response = await fetch('https://ocp10-grant-functions.azurewebsites.net/api/FillGrantForm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Azure Functions error:', errorText);
        throw new Error(`Azure Functions error (${response.status}): ${errorText || response.statusText}`);
      }

      const data: FilledFormResponse = await response.json();
      setResult(data);
      
      // Extract chat history for multi-agent framework
      if (processingMode === 'multi-agent-framework' && data.chat_history) {
        setChatHistory(data.chat_history);
        setShowChatWindow(true);
      }

    } catch (err) {
      console.error('Grant form filling error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fill grant form');
    } finally {
      setIsProcessing(false);
    }
  };

  const downloadFilledPDF = () => {
    if (!result?.filled_pdf) return;

    try {
      // Convert base64 to blob
      const pdfData = result.filled_pdf.data;
      
      // Validate base64 data
      if (!pdfData || pdfData.length === 0) {
        throw new Error('PDF data is empty');
      }
      
      // Use more efficient base64 to blob conversion
      const binaryString = atob(pdfData);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      // Create blob with explicit PDF MIME type
      const blob = new Blob([bytes], { 
        type: 'application/pdf'
      });
      
      // Validate blob size
      if (blob.size === 0) {
        throw new Error('Generated PDF blob is empty');
      }
      
      // Create download link with better attributes
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = result.filled_pdf.filename || 'filled_grant_application.pdf';
      a.rel = 'noopener'; // Security best practice
      a.target = '_self'; // Prevent opening in new tab
      
      // Force download behavior (prevent auto-open)
      a.style.display = 'none';
      document.body.appendChild(a);
      
      // Trigger download
      a.click();
      
      // Clean up after a short delay to ensure download starts
      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }, 100);
      
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Failed to download PDF: ' + (error instanceof Error ? error.message : 'Unknown error'));
      // NO FALLBACKS - let the user know PDF download failed explicitly
    }
  };

  const openPDFInNewTab = () => {
    if (!result?.filled_pdf) return;

    try {
      // Convert base64 to blob
      const pdfData = result.filled_pdf.data;
      const binaryString = atob(pdfData);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      const blob = new Blob([bytes], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      
      // Open in new tab instead of downloading
      const newWindow = window.open(url, '_blank');
      if (!newWindow) {
        alert('Popup blocked. Please allow popups and try again, or use the Download PDF button instead.');
      }
      
      // Clean up URL after 1 minute
      setTimeout(() => {
        URL.revokeObjectURL(url);
      }, 60000);
      
    } catch (error) {
      console.error('Error opening PDF:', error);
      alert('Failed to open PDF. Try downloading instead.');
    }
  };

  const downloadFilledText = () => {
    if (!result?.filled_responses) return;

    const content = Object.entries(result.filled_responses)
      .map(([field, response]) => `${field.replace(/_/g, ' ').toUpperCase()}:\n${response}\n\n`)
      .join('');

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'filled_grant_form.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Wand2 className="w-6 h-6 text-purple-600" />
          <h2 className="text-2xl font-bold text-gray-900">AI Grant Form Filler (Enhanced Multi-Agent)</h2>
        </div>

        {/* Processing Mode Selector */}
        <div className="mb-6">
          <DocumentProcessorSelector
            selectedMode={processingMode}
            onModeChange={setProcessingMode}
          />
        </div>

        {/* NGO Profile Section - Multi-Source */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">NGO Profile</h3>
          
          {/* Basic Info (Always Required) */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <h4 className="font-medium text-blue-900 mb-3">Basic Information (Required)</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Organization Name*</label>
                <input
                  type="text"
                  value={ngoDataSources.basic_info.organization_name}
                  onChange={(e) => setNgoDataSources({
                    ...ngoDataSources,
                    basic_info: { ...ngoDataSources.basic_info, organization_name: e.target.value }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Contact Email</label>
                <input
                  type="email"
                  value={ngoDataSources.basic_info.contact_email || ""}
                  onChange={(e) => setNgoDataSources({
                    ...ngoDataSources,
                    basic_info: { ...ngoDataSources.basic_info, contact_email: e.target.value }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                <input
                  type="tel"
                  value={ngoDataSources.basic_info.phone || ""}
                  onChange={(e) => setNgoDataSources({
                    ...ngoDataSources,
                    basic_info: { ...ngoDataSources.basic_info, phone: e.target.value }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                />
              </div>
            </div>
          </div>

          {/* Additional Data Sources */}
          <div className="space-y-4">
            <h4 className="font-medium text-gray-800">Additional Sources (Choose any to enhance the application)</h4>
            
            {/* NGO Profile PDF Upload */}
            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="pdf-source"
                    checked={activeDataSources.pdf}
                    onChange={() => toggleDataSource('pdf')}
                    className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                  />
                  <label htmlFor="pdf-source" className="flex items-center space-x-2 font-medium text-gray-700">
                    <FileUp className="w-4 h-4" />
                    <span>Upload NGO Profile PDF</span>
                  </label>
                </div>
                <span className="text-xs text-gray-500">Annual reports, organizational documents</span>
              </div>
              
              {activeDataSources.pdf && (
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleNGOProfileUpload}
                    className="hidden"
                    id="ngo-profile-upload"
                  />
                  <label htmlFor="ngo-profile-upload" className="cursor-pointer">
                    <FileText className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm font-medium text-gray-900">
                      {ngoDataSources.profile_pdf ? ngoDataSources.profile_pdf.name : 'Choose NGO profile PDF'}
                    </p>
                    <p className="text-xs text-gray-500">
                      Upload annual report, project summary, or organizational document
                    </p>
                  </label>
                </div>
              )}
            </div>

            {/* Website URL */}
            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="website-source"
                    checked={activeDataSources.website}
                    onChange={() => toggleDataSource('website')}
                    className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                  />
                  <label htmlFor="website-source" className="flex items-center space-x-2 font-medium text-gray-700">
                    <Globe className="w-4 h-4" />
                    <span>Organization Website (Optional)</span>
                  </label>
                </div>
                <span className="text-xs text-gray-500">For additional context</span>
              </div>
              
              {activeDataSources.website && (
                <div>
                  <input
                    type="url"
                    placeholder="https://your-organization.org"
                    value={ngoDataSources.website_url || ""}
                    onChange={(e) => handleWebsiteChange(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    AI will extract mission, projects, and other relevant information
                  </p>
                </div>
              )}
            </div>

            {/* Manual Entry */}
            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="manual-source"
                    checked={activeDataSources.manual}
                    onChange={() => toggleDataSource('manual')}
                    className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                  />
                  <label htmlFor="manual-source" className="flex items-center space-x-2 font-medium text-gray-700">
                    <FileText className="w-4 h-4" />
                    <span>Manual Entry</span>
                  </label>
                </div>
                <span className="text-xs text-gray-500">Type details directly</span>
              </div>
              
              {activeDataSources.manual && ngoDataSources.manual_details && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Mission Statement</label>
                    <textarea
                      value={ngoDataSources.manual_details.mission}
                      onChange={(e) => setNgoDataSources({
                        ...ngoDataSources,
                        manual_details: { ...ngoDataSources.manual_details!, mission: e.target.value }
                      })}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Years Active</label>
                    <input
                      type="number"
                      value={ngoDataSources.manual_details.years_active}
                      onChange={(e) => setNgoDataSources({
                        ...ngoDataSources,
                        manual_details: { ...ngoDataSources.manual_details!, years_active: parseInt(e.target.value) || 0 }
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Annual Budget ($)</label>
                    <input
                      type="number"
                      value={ngoDataSources.manual_details.annual_budget}
                      onChange={(e) => setNgoDataSources({
                        ...ngoDataSources,
                        manual_details: { ...ngoDataSources.manual_details!, annual_budget: parseInt(e.target.value) || 0 }
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Focus Areas (comma-separated)</label>
                    <input
                      type="text"
                      value={ngoDataSources.manual_details.focus_areas.join(", ")}
                      onChange={(e) => setNgoDataSources({
                        ...ngoDataSources,
                        manual_details: { 
                          ...ngoDataSources.manual_details!, 
                          focus_areas: e.target.value.split(",").map(area => area.trim()).filter(area => area.length > 0)
                        }
                      })}
                      placeholder="education, health, environment"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Recent Projects (Optional)</label>
                    <textarea
                      value={ngoDataSources.manual_details.recent_projects || ""}
                      onChange={(e) => setNgoDataSources({
                        ...ngoDataSources,
                        manual_details: { ...ngoDataSources.manual_details!, recent_projects: e.target.value }
                      })}
                      rows={2}
                      placeholder="Brief description of recent successful projects..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Grant Context Section */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-800">Grant Context</h3>
            {selectedGrant && (
              <div className="flex items-center text-sm text-green-600 bg-green-50 px-3 py-1 rounded-full">
                <CheckCircle className="w-4 h-4 mr-1" />
                Pre-filled from selected grant
              </div>
            )}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Funder Name</label>
              <input
                type="text"
                value={grantContext.funder_name}
                onChange={(e) => setGrantContext({...grantContext, funder_name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Focus Area</label>
              <input
                type="text"
                value={grantContext.focus_area}
                onChange={(e) => setGrantContext({...grantContext, focus_area: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Max Amount ($)</label>
              <input
                type="number"
                value={grantContext.max_amount}
                onChange={(e) => setGrantContext({...grantContext, max_amount: parseInt(e.target.value) || 0})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              />
            </div>
          </div>
        </div>

        {/* File Upload Section */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Upload Grant Form (PDF)</h3>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              className="hidden"
              id="grant-form-upload"
            />
            <label htmlFor="grant-form-upload" className="cursor-pointer">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-lg font-medium text-gray-900 mb-2">
                {selectedFile ? selectedFile.name : 'Choose PDF grant form'}
              </p>
              <p className="text-sm text-gray-500">
                Upload a grant application form in PDF format
              </p>
            </label>
          </div>
        </div>

        {/* Fill Form Button */}
        <div className="flex justify-center mb-6">
          <button
            onClick={fillGrantForm}
            disabled={!selectedFile || isProcessing}
            className={`px-6 py-3 rounded-lg font-medium flex items-center space-x-2 ${
              !selectedFile || isProcessing
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-purple-600 text-white hover:bg-purple-700'
            }`}
          >
            <Wand2 className="w-5 h-5" />
            <span>{isProcessing ? 'Filling Form...' : 'Fill Grant Form with Azure ML'}</span>
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="flex items-center space-x-2 p-4 bg-red-50 border border-red-200 rounded-lg">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <span className="text-red-700">{error}</span>
          </div>
        )}

        {/* Results Display */}
        {result && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-6 h-6 text-green-500" />
                <h3 className="text-xl font-semibold text-gray-900">Form Filled Successfully</h3>
              </div>
              <div className="flex items-center space-x-3">
                {result.filled_pdf && (
                  <div className="flex space-x-2">
                    <button
                      onClick={downloadFilledPDF}
                      className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      <Download className="w-4 h-4" />
                      <span>Download PDF</span>
                    </button>
                    <button
                      onClick={openPDFInNewTab}
                      className="flex items-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                      title="Preview PDF in new tab"
                    >
                      <Eye className="w-4 h-4" />
                      <span>Preview</span>
                    </button>
                  </div>
                )}
                <button
                  onClick={downloadFilledText}
                  className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                >
                  <Download className="w-4 h-4" />
                  <span>Download Text</span>
                </button>
              </div>
            </div>

            {/* Processing Summary */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-medium text-green-900 mb-2">Processing Summary</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-green-700">Total Fields:</span>
                  <span className="font-medium ml-2">{result.processing_summary.total_fields}</span>
                </div>
                <div>
                  <span className="text-green-700">Filled Fields:</span>
                  <span className="font-medium ml-2">{result.processing_summary.filled_fields}</span>
                </div>
                <div>
                  <span className="text-green-700">Success Rate:</span>
                  <span className="font-medium ml-2">{Math.round(result.processing_summary.fill_rate)}%</span>
                </div>
                {result.processing_summary.pdf_generation && (
                  <div>
                    <span className="text-green-700">PDF Method:</span>
                    <span className="font-medium ml-2 capitalize">
                      {result.processing_summary.pdf_generation.method.replace('_', ' ')}
                    </span>
                  </div>
                )}
              </div>
              
              {/* PDF Analysis Info */}
              {result.pdf_analysis && (
                <div className="mt-4 pt-3 border-t border-green-200">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-green-700">Original PDF Pages:</span>
                      <span className="font-medium ml-2">{result.pdf_analysis.total_pages}</span>
                    </div>
                    <div>
                      <span className="text-green-700">Has Form Fields:</span>
                      <span className="font-medium ml-2">{result.pdf_analysis.has_form_fields ? 'Yes' : 'No'}</span>
                    </div>
                    {result.pdf_analysis.form_fields.length > 0 && (
                      <div>
                        <span className="text-green-700">Form Fields Found:</span>
                        <span className="font-medium ml-2">{result.pdf_analysis.form_fields.length}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Filled Responses */}
            <div className="space-y-4">
              <h4 className="text-lg font-semibold text-gray-900">Filled Form Fields</h4>
              {Object.entries(result.filled_responses).map(([field, response]) => (
                <div key={field} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h5 className="font-medium text-gray-900 mb-2 capitalize">
                    {field.replace(/_/g, ' ')}
                  </h5>
                  <p className="text-gray-700 whitespace-pre-wrap">{response}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Multi-Agent Chat Window */}
      {(processingMode === 'multi-agent-framework' && (isProcessing || chatHistory.length > 0)) && (
        <MultiAgentChatWindow
          isProcessing={isProcessing}
          chatHistory={chatHistory}
          onClose={() => setChatHistory([])}
        />
      )}
    </div>
  );
};

export default GrantFormFiller;