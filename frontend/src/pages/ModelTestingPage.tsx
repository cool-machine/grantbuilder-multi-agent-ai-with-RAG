import React, { useState, useRef } from 'react';
import { Upload, Send, Copy, Trash2, Settings, MessageSquare, Eye, Play, Globe, Download } from 'lucide-react';
import { ChatMessage, NGOProfile } from '../types';
import { WebsiteContextExtractor, WebsiteContext, ExtractedContexts } from '../services/websiteContextExtractor';

// Model Testing Playground - Interactive chat interface for prompt engineering

export default function ModelTestingPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      type: 'system',
      content: '🎉 Welcome to the Model Testing Playground!\n\nThis demo is pre-populated with Teach for America information and a sample Appalachian Regional Commission grant. You can:\n\n✅ Test different prompts in the chat below\n✅ Modify the NGO profile or grant context as needed\n✅ Customize the prompt template on the left\n✅ View the exact prompts sent to GPT-OSS-120B\n\nTry asking: "Write an executive summary for this grant application" or "What are our key strengths for this funding opportunity?"',
      timestamp: new Date()
    }
  ]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [ngoProfile, setNGOProfile] = useState<NGOProfile>({
    name: '',
    mission: '',
    focusAreas: '',
    targetPopulation: '',
    geographicScope: '',
    established: '',
    staff: '',
    budget: ''
  });
  // Website context extraction
  const [funderUrl, setFunderUrl] = useState('https://research-and-innovation.ec.europa.eu/funding/funding-opportunities/funding-programmes-and-open-calls/horizon-europe_en');
  const [applicantUrl, setApplicantUrl] = useState('https://www.ox.ac.uk/');
  const [extractedContexts, setExtractedContexts] = useState<ExtractedContexts | null>(null);
  const [isExtractingContext, setIsExtractingContext] = useState(false);
  
  // Model selection
  const [selectedModel, setSelectedModel] = useState('gpt-oss-120b');

  const [grantDocument, setGrantDocument] = useState('');
  const [extractedText, setExtractedText] = useState('');
  const [uploadedPDFFile, setUploadedPDFFile] = useState<File | null>(null);
  const [promptTemplate, setPromptTemplate] = useState(`You are a professional grant writer helping to complete a grant application.

====================================================================
GRANT APPLICATION SCENARIO
====================================================================
The organization "{ngo_name}" is applying for funding from the grant provider.
Your task is to write compelling, accurate content that demonstrates alignment 
between the applicant's capabilities and the funder's priorities.

====================================================================
SECTION 1: GRANT PROVIDER INFORMATION (Who is giving the money)
====================================================================
{funder_context}

====================================================================
SECTION 2: APPLYING ORGANIZATION INFORMATION (Who wants the money)
====================================================================
Organization Profile:
- Name: {ngo_name}
- Mission: {ngo_mission}
- Focus Areas: {ngo_focus_areas}
- Target Population: {ngo_target_population}
- Geographic Scope: {ngo_geographic_scope}
- Established: {ngo_established}
- Staff Size: {ngo_staff}
- Annual Budget: {ngo_budget}

Detailed Organization Context (from website analysis):
{applicant_context}

====================================================================
SECTION 3: GRANT APPLICATION FORM CONTEXT
====================================================================
EXAMPLE FORMAT - Here's how grant applications are typically structured:

EXAMPLE GRANT APPLICATION STRUCTURE:
- Executive Summary: [Brief overview of project and impact]
- Project Description: [Detailed explanation of objectives and methodology]  
- Budget Justification: [Breakdown of costs and resource allocation]
- Timeline: [Project milestones and deliverables]
- Team Qualifications: [Expertise and experience of key personnel]
- Impact Statement: [Expected outcomes and benefits]

ACTUAL GRANT FORM TO COMPLETE:
{grant_context}

Note: Use the above structure as guidance, but focus on the specific fields and requirements in the actual grant form below.

====================================================================
SECTION 4: SPECIFIC WRITING REQUEST
====================================================================
Task: {user_request}

====================================================================
INSTRUCTIONS FOR RESPONSE
====================================================================
Please provide a professional, detailed response that:
1. Demonstrates clear alignment between the applicant's capabilities and funder's priorities
2. Incorporates specific evidence from the organization's track record and resources
3. Addresses the funder's evaluation criteria and strategic focus areas
4. Uses measurable, specific language that shows impact potential
5. Maintains the appropriate tone and format for the grant application context

Write as if you are the applying organization addressing the grant provider.`);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [toastMessage, setToastMessage] = useState<{title: string, description: string, variant?: string} | null>(null);

  const showToast = (toast: {title: string, description: string, variant?: string}) => {
    setToastMessage(toast);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      showToast({
        title: "Invalid file type",
        description: "Please upload a PDF file.",
        variant: "destructive"
      });
      return;
    }

    // Store the PDF file for direct agent processing
    setUploadedPDFFile(file);

    // Check if API base URL is configured
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'https://ocp10-grant-functions.azurewebsites.net/api';
    console.log('Using API Base URL:', apiBaseUrl);

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Use client-side PDF extraction to replicate Azure Function behavior
      const { DocumentExtractor } = await import('../services/textExtraction');
      const extractor = DocumentExtractor.getInstance();
      
      // Extract text using the same approach as Azure Functions would
      const extractedResult = await extractor.extractText(file, (status) => {
        console.log('PDF Extraction Progress:', status);
      });
      
      // Use the actual extracted text (this is what Azure Function would see)
      const azureFunctionExtractedText = extractedResult.extractedText;
      
      setExtractedText(azureFunctionExtractedText);
      showToast({
        title: "PDF Uploaded Successfully",
        description: `PDF ready for direct agent processing. Extracted ${azureFunctionExtractedText.length} characters as preview.`
      });
    } catch (error) {
      console.error('Error extracting PDF:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to extract PDF text';
      showToast({
        title: "PDF extraction failed",
        description: errorMessage + " Please try a different PDF or use manual text input.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const buildFinalPrompt = (userRequest: string): string => {
    // Build funder context from extracted website data
    let funderContext = '[No funder context extracted]';
    if (extractedContexts?.funder) {
      const funder = extractedContexts.funder;
      let contextParts = [`FUNDER: ${funder.title}`];
      
      // About Section
      if (funder.funderInfo?.about) {
        contextParts.push('\n📋 ABOUT:');
        if (funder.funderInfo.about.missionStatement) {
          contextParts.push(`Mission: ${funder.funderInfo.about.missionStatement}`);
        }
        if (funder.funderInfo.about.organizationalGoals?.length > 0) {
          contextParts.push(`Goals: ${funder.funderInfo.about.organizationalGoals.slice(0, 3).join('; ')}`);
        }
        if (funder.funderInfo.about.strategicObjectives?.length > 0) {
          contextParts.push(`Objectives: ${funder.funderInfo.about.strategicObjectives.slice(0, 3).join('; ')}`);
        }
      }
      
      // Past Fundings Section
      if (funder.funderInfo?.pastFundings) {
        const pf = funder.funderInfo.pastFundings;
        if (pf.recentRecipients?.length > 0 || pf.fundedProjects?.length > 0 || pf.awardAmounts?.length > 0) {
          contextParts.push('\n💰 PAST FUNDINGS:');
          if (pf.recentRecipients?.length > 0) {
            contextParts.push(`Recent Recipients: ${pf.recentRecipients.slice(0, 3).join('; ')}`);
          }
          if (pf.fundedProjects?.length > 0) {
            contextParts.push(`Funded Projects: ${pf.fundedProjects.slice(0, 2).join('; ')}`);
          }
          if (pf.awardAmounts?.length > 0) {
            contextParts.push(`Award Amounts: ${pf.awardAmounts.slice(0, 3).join('; ')}`);
          }
        }
      }
      
      // Funding Priorities Section
      if (funder.funderInfo?.fundingPriorities) {
        const fp = funder.funderInfo.fundingPriorities;
        if (fp.currentCalls?.length > 0 || fp.priorityThemes?.length > 0 || fp.evaluationCriteria?.length > 0) {
          contextParts.push('\n🎯 FUNDING PRIORITIES:');
          if (fp.currentCalls?.length > 0) {
            contextParts.push(`Current Calls: ${fp.currentCalls.slice(0, 2).join('; ')}`);
          }
          if (fp.priorityThemes?.length > 0) {
            contextParts.push(`Priority Themes: ${fp.priorityThemes.slice(0, 3).join('; ')}`);
          }
          if (fp.evaluationCriteria?.length > 0) {
            contextParts.push(`Evaluation Criteria: ${fp.evaluationCriteria.slice(0, 2).join('; ')}`);
          }
          if (fp.strategicFocus?.length > 0) {
            contextParts.push(`Strategic Focus: ${fp.strategicFocus.slice(0, 3).join('; ')}`);
          }
        }
      }
      
      // Fallback to basic info if no structured data
      if (!funder.funderInfo?.about && !funder.funderInfo?.pastFundings && !funder.funderInfo?.fundingPriorities) {
        if (funder.mission) contextParts.push(`Mission: ${funder.mission}`);
        if (funder.keyInfo.length > 0) contextParts.push(`Key Info: ${funder.keyInfo.slice(0, 3).join('; ')}`);
      }
      
      // Add warnings and confidence
      if (funder.warnings.length > 0) {
        contextParts.push(`\n⚠️ Notes: ${funder.warnings.join('; ')}`);
      }
      contextParts.push(`\n📊 Confidence: ${Math.round(funder.confidence * 100)}%`);
      
      funderContext = contextParts.join('\n');
    }

    // Build applicant context from extracted website data
    let applicantContext = '[No applicant context extracted]';
    if (extractedContexts?.applicant) {
      const applicant = extractedContexts.applicant;
      let contextParts = [`APPLICANT: ${applicant.title}`];
      
      // Research Capabilities Section
      if (applicant.applicantInfo?.researchCapabilities) {
        const rc = applicant.applicantInfo.researchCapabilities;
        if (rc.expertiseAreas?.length > 0 || rc.researchCenters?.length > 0 || rc.academicDepartments?.length > 0) {
          contextParts.push('\n🔬 RESEARCH CAPABILITIES:');
          if (rc.expertiseAreas?.length > 0) {
            contextParts.push(`Expertise Areas: ${rc.expertiseAreas.slice(0, 3).join('; ')}`);
          }
          if (rc.researchCenters?.length > 0) {
            contextParts.push(`Research Centers: ${rc.researchCenters.slice(0, 3).join('; ')}`);
          }
          if (rc.academicDepartments?.length > 0) {
            contextParts.push(`Departments: ${rc.academicDepartments.slice(0, 3).join('; ')}`);
          }
          if (rc.keyFaculty?.length > 0) {
            contextParts.push(`Key Faculty: ${rc.keyFaculty.slice(0, 2).join('; ')}`);
          }
        }
      }
      
      // Track Record Section
      if (applicant.applicantInfo?.trackRecord) {
        const tr = applicant.applicantInfo.trackRecord;
        if (tr.previousGrants?.length > 0 || tr.notableProjects?.length > 0 || tr.awards?.length > 0) {
          contextParts.push('\n🏆 TRACK RECORD:');
          if (tr.previousGrants?.length > 0) {
            contextParts.push(`Previous Grants: ${tr.previousGrants.slice(0, 2).join('; ')}`);
          }
          if (tr.notableProjects?.length > 0) {
            contextParts.push(`Notable Projects: ${tr.notableProjects.slice(0, 2).join('; ')}`);
          }
          if (tr.awards?.length > 0) {
            contextParts.push(`Awards: ${tr.awards.slice(0, 2).join('; ')}`);
          }
          if (tr.publications?.length > 0) {
            contextParts.push(`Publications: ${tr.publications.slice(0, 2).join('; ')}`);
          }
        }
      }
      
      // Resources Section
      if (applicant.applicantInfo?.resources) {
        const res = applicant.applicantInfo.resources;
        if (res.facilities?.length > 0 || res.equipment?.length > 0 || res.collaborations?.length > 0) {
          contextParts.push('\n🏛️ RESOURCES:');
          if (res.facilities?.length > 0) {
            contextParts.push(`Facilities: ${res.facilities.slice(0, 3).join('; ')}`);
          }
          if (res.equipment?.length > 0) {
            contextParts.push(`Equipment: ${res.equipment.slice(0, 2).join('; ')}`);
          }
          if (res.collaborations?.length > 0) {
            contextParts.push(`Collaborations: ${res.collaborations.slice(0, 2).join('; ')}`);
          }
          if (res.supportServices?.length > 0) {
            contextParts.push(`Support Services: ${res.supportServices.slice(0, 2).join('; ')}`);
          }
        }
      }
      
      // Fallback to basic info if no structured data
      if (!applicant.applicantInfo?.researchCapabilities && !applicant.applicantInfo?.trackRecord && !applicant.applicantInfo?.resources) {
        if (applicant.mission) contextParts.push(`Mission: ${applicant.mission}`);
        if (applicant.keyInfo.length > 0) contextParts.push(`Key Programs: ${applicant.keyInfo.slice(0, 3).join('; ')}`);
        if (applicant.contactInfo?.email) contextParts.push(`Contact: ${applicant.contactInfo.email}`);
      }
      
      // Add warnings and confidence
      if (applicant.warnings.length > 0) {
        contextParts.push(`\n⚠️ Notes: ${applicant.warnings.join('; ')}`);
      }
      contextParts.push(`\n📊 Confidence: ${Math.round(applicant.confidence * 100)}%`);
      
      applicantContext = contextParts.join('\n');
    }

    return promptTemplate
      .replace('{ngo_name}', ngoProfile.name || 'University of Oxford')
      .replace('{ngo_mission}', ngoProfile.mission || 'Leading university dedicated to research excellence and education')
      .replace('{ngo_focus_areas}', ngoProfile.focusAreas || 'Research, Education, Innovation')
      .replace('{ngo_target_population}', ngoProfile.targetPopulation || 'Students, Researchers, Academic Community')
      .replace('{ngo_geographic_scope}', ngoProfile.geographicScope || 'Global, with focus on UK and Europe')
      .replace('{ngo_established}', ngoProfile.established || '1096')
      .replace('{ngo_staff}', ngoProfile.staff || '12,000+ academic and support staff')
      .replace('{ngo_budget}', ngoProfile.budget || '£2.5 billion annually')
      .replace('{funder_context}', funderContext)
      .replace('{applicant_context}', applicantContext)
      .replace('{grant_context}', extractedText || grantDocument || '[No grant context provided]')
      .replace('{user_request}', userRequest);
  };

  const sendMessage = async () => {
    if (!currentMessage.trim()) return;

    const finalPrompt = buildFinalPrompt(currentMessage);
    
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: currentMessage,
      timestamp: new Date(),
      extractedText: extractedText || grantDocument,
      promptTemplate: promptTemplate,
      finalPrompt: finalPrompt
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);

    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'https://ocp10-grant-functions.azurewebsites.net/api';
      
      // Prepare request body with PDF file if available
      const requestBody: any = {
        prompt: finalPrompt,
        task_type: 'full_grant',
        max_tokens: 2000,
        temperature: 0.7,
        model: selectedModel,
        context: {
          funder: funderContext,
          applicant: applicantContext,
          extracted_data: extractedData
        }
      };

      // Include PDF file data if available
      if (uploadedPDFFile) {
        const base64Data = await new Promise<string>((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result as string);
          reader.onerror = reject;
          reader.readAsDataURL(uploadedPDFFile);
        });
        
        requestBody.pdf_file = {
          name: uploadedPDFFile.name,
          base64: base64Data,
          type: uploadedPDFFile.type
        };
      }

      const response = await fetch(`${apiBaseUrl}/AgentOrchestrator`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('AI model service is currently unavailable. Please try again later or contact support.');
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: result.choices?.[0]?.message?.content || result.response || 'No response received',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'system',
        content: `Error: ${error instanceof Error ? error.message : 'Failed to get response from model'}\n\nNote: This is a demo environment. The AI model service may be temporarily unavailable.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      
      const errorMsg = error instanceof Error ? error.message : 'Failed to get response from model';
      showToast({
        title: "Request failed",
        description: errorMsg.includes('404') ? 'AI service temporarily unavailable' : 'Network error - please try again',
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      showToast({
        title: "Copied to clipboard",
        description: "Content has been copied to your clipboard."
      });
    } catch (error) {
      showToast({
        title: "Copy failed",
        description: "Failed to copy content to clipboard.",
        variant: "destructive"
      });
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const extractWebsiteContexts = async () => {
    if (!funderUrl.trim() || !applicantUrl.trim()) {
      showToast({
        title: "Missing URLs",
        description: "Please enter both funder and applicant website URLs.",
        variant: "destructive"
      });
      return;
    }

    setIsExtractingContext(true);

    try {
      const extractor = WebsiteContextExtractor.getInstance();
      const contexts = await extractor.extractBothContexts(funderUrl.trim(), applicantUrl.trim());
      
      setExtractedContexts(contexts);
      
      const funderStatus = contexts.funder?.accessible ? '✅' : '❌';
      const applicantStatus = contexts.applicant?.accessible ? '✅' : '❌';
      
      showToast({
        title: "Website contexts extracted",
        description: `Funder: ${funderStatus} | Applicant: ${applicantStatus}. Check the contexts below.`
      });

    } catch (error) {
      console.error('Error extracting website contexts:', error);
      showToast({
        title: "Extraction failed",
        description: "Failed to extract website contexts. Please check the URLs and try again.",
        variant: "destructive"
      });
    } finally {
      setIsExtractingContext(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Toast Notification */}
      {toastMessage && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
          toastMessage.variant === 'destructive' ? 'bg-red-100 border border-red-400 text-red-800' : 'bg-green-100 border border-green-400 text-green-800'
        }`}>
          <div className="font-semibold">{toastMessage.title}</div>
          <div className="text-sm">{toastMessage.description}</div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Model Testing Playground</h1>
          <p className="text-gray-600">Test and fine-tune prompts for the GPT-OSS-120B model with your NGO profile and grant context.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Configuration */}
          <div className="lg:col-span-1 space-y-6">
            {/* NGO Profile */}
            <div className="bg-white rounded-lg shadow-md border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center gap-2 mb-2">
                  <Settings className="h-5 w-5" />
                  <h3 className="text-lg font-semibold">NGO Profile</h3>
                </div>
                <p className="text-gray-600 text-sm">Configure your organization's information for context.</p>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <label htmlFor="ngo-name" className="block text-sm font-medium text-gray-700 mb-1">Organization Name</label>
                  <input
                    type="text"
                    id="ngo-name"
                    value={ngoProfile.name}
                    onChange={(e) => setNGOProfile(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Enter NGO name"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label htmlFor="ngo-mission" className="block text-sm font-medium text-gray-700 mb-1">Mission Statement</label>
                  <textarea
                    id="ngo-mission"
                    value={ngoProfile.mission}
                    onChange={(e) => setNGOProfile(prev => ({ ...prev, mission: e.target.value }))}
                    placeholder="Describe your mission"
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
                  />
                </div>
                <div>
                  <label htmlFor="ngo-focus" className="block text-sm font-medium text-gray-700 mb-1">Focus Areas</label>
                  <input
                    type="text"
                    id="ngo-focus"
                    value={ngoProfile.focusAreas}
                    onChange={(e) => setNGOProfile(prev => ({ ...prev, focusAreas: e.target.value }))}
                    placeholder="e.g., Education, Healthcare, Environment"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label htmlFor="ngo-population" className="block text-sm font-medium text-gray-700 mb-1">Target Population</label>
                  <input
                    type="text"
                    id="ngo-population"
                    value={ngoProfile.targetPopulation}
                    onChange={(e) => setNGOProfile(prev => ({ ...prev, targetPopulation: e.target.value }))}
                    placeholder="Who you serve"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label htmlFor="ngo-scope" className="block text-sm font-medium text-gray-700 mb-1">Geographic Scope</label>
                  <input
                    type="text"
                    id="ngo-scope"
                    value={ngoProfile.geographicScope}
                    onChange={(e) => setNGOProfile(prev => ({ ...prev, geographicScope: e.target.value }))}
                    placeholder="Local, Regional, National, International"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label htmlFor="ngo-established" className="block text-sm font-medium text-gray-700 mb-1">Established</label>
                    <input
                      type="text"
                      id="ngo-established"
                      value={ngoProfile.established}
                      onChange={(e) => setNGOProfile(prev => ({ ...prev, established: e.target.value }))}
                      placeholder="Year"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label htmlFor="ngo-staff" className="block text-sm font-medium text-gray-700 mb-1">Staff Size</label>
                    <input
                      type="text"
                      id="ngo-staff"
                      value={ngoProfile.staff}
                      onChange={(e) => setNGOProfile(prev => ({ ...prev, staff: e.target.value }))}
                      placeholder="Number"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <div>
                  <label htmlFor="ngo-budget" className="block text-sm font-medium text-gray-700 mb-1">Annual Budget</label>
                  <input
                    type="text"
                    id="ngo-budget"
                    value={ngoProfile.budget}
                    onChange={(e) => setNGOProfile(prev => ({ ...prev, budget: e.target.value }))}
                    placeholder="$100,000"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* Grant Context */}
            <div className="bg-white rounded-lg shadow-md border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold mb-2">Grant Context</h3>
                <p className="text-gray-600 text-sm">Upload a grant PDF or paste requirements manually.</p>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileUpload}
                    accept=".pdf"
                    className="hidden"
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      disabled={isLoading}
                      className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed ${
                        uploadedPDFFile 
                          ? 'border-green-300 bg-green-50 text-green-700 hover:bg-green-100' 
                          : 'border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <Upload className="h-4 w-4" />
                      {isLoading ? 'Processing PDF...' : uploadedPDFFile ? `✅ PDF Ready: ${uploadedPDFFile.name}` : 'Upload PDF for Direct Agent Processing'}
                    </button>
                    {uploadedPDFFile && (
                      <button
                        onClick={() => {
                          setUploadedPDFFile(null);
                          setExtractedText('');
                          showToast({
                            title: "PDF Cleared",
                            description: "PDF file has been removed. You can upload a new one."
                          });
                        }}
                        className="px-3 py-2 text-red-600 hover:bg-red-50 border border-red-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                        title="Clear PDF"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </div>
                <div className="text-center text-gray-500">OR</div>
                <div>
                  <label htmlFor="grant-text" className="block text-sm font-medium text-gray-700 mb-1">Paste Grant Requirements</label>
                  <textarea
                    id="grant-text"
                    value={grantDocument}
                    onChange={(e) => setGrantDocument(e.target.value)}
                    placeholder="Paste grant requirements, application guidelines, or specific questions here..."
                    rows={6}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
                  />
                </div>
                {extractedText && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Extracted Text ({extractedText.length} characters)</label>
                    <div className="bg-gray-50 p-3 rounded-md text-sm max-h-32 overflow-y-auto">
                      {extractedText.substring(0, 200)}...
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Website Context Extraction */}
            <div className="bg-white rounded-lg shadow-md border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center gap-2 mb-2">
                  <Globe className="h-5 w-5" />
                  <h3 className="text-lg font-semibold">Website Context Extraction</h3>
                </div>
                <p className="text-gray-600 text-sm">Extract contextual information from funder and applicant websites.</p>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <label htmlFor="funder-url" className="block text-sm font-medium text-gray-700 mb-1">Funder Website URL</label>
                  <input
                    type="url"
                    id="funder-url"
                    value={funderUrl}
                    onChange={(e) => setFunderUrl(e.target.value)}
                    placeholder="https://www.funder.org"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label htmlFor="applicant-url" className="block text-sm font-medium text-gray-700 mb-1">Applicant Website URL</label>
                  <input
                    type="url"
                    id="applicant-url"
                    value={applicantUrl}
                    onChange={(e) => setApplicantUrl(e.target.value)}
                    placeholder="https://www.organization.org"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <button
                  onClick={extractWebsiteContexts}
                  disabled={isExtractingContext}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Download className="h-4 w-4" />
                  {isExtractingContext ? 'Extracting Contexts...' : 'Extract Website Contexts'}
                </button>

                {/* Display extracted contexts */}
                {extractedContexts && (
                  <div className="mt-6 space-y-4">
                    {/* Funder Context */}
                    {extractedContexts.funder && (
                      <div className="border rounded-md p-4 bg-blue-50">
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`w-3 h-3 rounded-full ${extractedContexts.funder.accessible ? 'bg-green-500' : 'bg-red-500'}`}></span>
                          <h4 className="font-semibold text-blue-800">Funder Context</h4>
                          <span className="text-sm text-blue-600">
                            Confidence: {Math.round(extractedContexts.funder.confidence * 100)}%
                          </span>
                        </div>
                        <div className="text-sm space-y-3">
                          <div>
                            <p><strong>Title:</strong> {extractedContexts.funder.title}</p>
                            <p><strong>URL:</strong> <a href={extractedContexts.funder.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{extractedContexts.funder.url}</a></p>
                          </div>
                          
                          {/* Structured Funder Information */}
                          {extractedContexts.funder.funderInfo && (
                            <div className="space-y-3">
                              {/* About Section */}
                              {extractedContexts.funder.funderInfo.about && (
                                <div className="bg-blue-100 p-3 rounded">
                                  <strong className="text-blue-800">📋 ABOUT:</strong>
                                  {extractedContexts.funder.funderInfo.about.missionStatement && (
                                    <p className="mt-1"><span className="font-medium">Mission:</span> {extractedContexts.funder.funderInfo.about.missionStatement.substring(0, 300)}...</p>
                                  )}
                                  {extractedContexts.funder.funderInfo.about.organizationalGoals && extractedContexts.funder.funderInfo.about.organizationalGoals.length > 0 && (
                                    <div className="mt-2">
                                      <span className="font-medium">Goals:</span>
                                      <ul className="ml-4 list-disc">
                                        {extractedContexts.funder.funderInfo.about.organizationalGoals.slice(0, 3).map((goal, idx) => (
                                          <li key={idx} className="text-xs">{goal.substring(0, 150)}...</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                  {extractedContexts.funder.funderInfo.about.strategicObjectives && extractedContexts.funder.funderInfo.about.strategicObjectives.length > 0 && (
                                    <div className="mt-2">
                                      <span className="font-medium">Objectives:</span>
                                      <ul className="ml-4 list-disc">
                                        {extractedContexts.funder.funderInfo.about.strategicObjectives.slice(0, 3).map((obj, idx) => (
                                          <li key={idx} className="text-xs">{obj.substring(0, 150)}...</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                </div>
                              )}
                              
                              {/* Past Fundings Section */}
                              {extractedContexts.funder.funderInfo.pastFundings && (
                                <div className="bg-blue-100 p-3 rounded">
                                  <strong className="text-blue-800">💰 PAST FUNDINGS:</strong>
                                  {extractedContexts.funder.funderInfo.pastFundings.recentRecipients && extractedContexts.funder.funderInfo.pastFundings.recentRecipients.length > 0 && (
                                    <div className="mt-1">
                                      <span className="font-medium">Recipients:</span> {extractedContexts.funder.funderInfo.pastFundings.recentRecipients.slice(0, 3).join('; ')}
                                    </div>
                                  )}
                                  {extractedContexts.funder.funderInfo.pastFundings.awardAmounts && extractedContexts.funder.funderInfo.pastFundings.awardAmounts.length > 0 && (
                                    <div className="mt-1">
                                      <span className="font-medium">Amounts:</span> {extractedContexts.funder.funderInfo.pastFundings.awardAmounts.slice(0, 5).join('; ')}
                                    </div>
                                  )}
                                  {extractedContexts.funder.funderInfo.pastFundings.fundedProjects && extractedContexts.funder.funderInfo.pastFundings.fundedProjects.length > 0 && (
                                    <div className="mt-1">
                                      <span className="font-medium">Projects:</span>
                                      <ul className="ml-4 list-disc">
                                        {extractedContexts.funder.funderInfo.pastFundings.fundedProjects.slice(0, 2).map((project, idx) => (
                                          <li key={idx} className="text-xs">{project.substring(0, 100)}...</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                </div>
                              )}
                              
                              {/* Funding Priorities Section */}
                              {extractedContexts.funder.funderInfo.fundingPriorities && (
                                <div className="bg-blue-100 p-3 rounded">
                                  <strong className="text-blue-800">🎯 FUNDING PRIORITIES:</strong>
                                  {extractedContexts.funder.funderInfo.fundingPriorities.priorityThemes && extractedContexts.funder.funderInfo.fundingPriorities.priorityThemes.length > 0 && (
                                    <div className="mt-1">
                                      <span className="font-medium">Themes:</span> {extractedContexts.funder.funderInfo.fundingPriorities.priorityThemes.slice(0, 4).join('; ')}
                                    </div>
                                  )}
                                  {extractedContexts.funder.funderInfo.fundingPriorities.currentCalls && extractedContexts.funder.funderInfo.fundingPriorities.currentCalls.length > 0 && (
                                    <div className="mt-1">
                                      <span className="font-medium">Current Calls:</span>
                                      <ul className="ml-4 list-disc">
                                        {extractedContexts.funder.funderInfo.fundingPriorities.currentCalls.slice(0, 2).map((call, idx) => (
                                          <li key={idx} className="text-xs">{call.substring(0, 120)}...</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                  {extractedContexts.funder.funderInfo.fundingPriorities.evaluationCriteria && extractedContexts.funder.funderInfo.fundingPriorities.evaluationCriteria.length > 0 && (
                                    <div className="mt-1">
                                      <span className="font-medium">Criteria:</span> {extractedContexts.funder.funderInfo.fundingPriorities.evaluationCriteria.slice(0, 2).join('; ')}
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          )}
                          
                          {/* Fallback to basic info if no structured data */}
                          {!extractedContexts.funder.funderInfo && extractedContexts.funder.mission && (
                            <p><strong>Mission:</strong> {extractedContexts.funder.mission.substring(0, 200)}...</p>
                          )}
                          {!extractedContexts.funder.funderInfo && extractedContexts.funder.keyInfo.length > 0 && (
                            <div>
                              <strong>Key Information:</strong>
                              <ul className="ml-4 list-disc">
                                {extractedContexts.funder.keyInfo.slice(0, 3).map((info, idx) => (
                                  <li key={idx} className="text-xs">{info.substring(0, 100)}...</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          {extractedContexts.funder.warnings.length > 0 && (
                            <div className="mt-2">
                              <strong>⚠️ Warnings:</strong>
                              {extractedContexts.funder.warnings.map((warning, idx) => (
                                <p key={idx} className="text-orange-600 text-xs">{warning}</p>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Applicant Context */}
                    {extractedContexts.applicant && (
                      <div className="border rounded-md p-4 bg-green-50">
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`w-3 h-3 rounded-full ${extractedContexts.applicant.accessible ? 'bg-green-500' : 'bg-red-500'}`}></span>
                          <h4 className="font-semibold text-green-800">Applicant Context</h4>
                          <span className="text-sm text-green-600">
                            Confidence: {Math.round(extractedContexts.applicant.confidence * 100)}%
                          </span>
                        </div>
                        <div className="text-sm space-y-3">
                          <div>
                            <p><strong>Title:</strong> {extractedContexts.applicant.title}</p>
                            <p><strong>URL:</strong> <a href={extractedContexts.applicant.url} target="_blank" rel="noopener noreferrer" className="text-green-600 hover:underline">{extractedContexts.applicant.url}</a></p>
                          </div>
                          
                          {/* Structured Applicant Information */}
                          {extractedContexts.applicant.applicantInfo && (
                            <div className="space-y-3">
                              {/* Research Capabilities Section */}
                              {extractedContexts.applicant.applicantInfo.researchCapabilities && (
                                <div className="bg-green-100 p-3 rounded">
                                  <strong className="text-green-800">🔬 RESEARCH CAPABILITIES:</strong>
                                  {extractedContexts.applicant.applicantInfo.researchCapabilities.expertiseAreas && extractedContexts.applicant.applicantInfo.researchCapabilities.expertiseAreas.length > 0 && (
                                    <div className="mt-1">
                                      <span className="font-medium">Expertise:</span> {extractedContexts.applicant.applicantInfo.researchCapabilities.expertiseAreas.slice(0, 4).join('; ')}
                                    </div>
                                  )}
                                  {extractedContexts.applicant.applicantInfo.researchCapabilities.researchCenters && extractedContexts.applicant.applicantInfo.researchCapabilities.researchCenters.length > 0 && (
                                    <div className="mt-1">
                                      <span className="font-medium">Centers:</span>
                                      <ul className="ml-4 list-disc">
                                        {extractedContexts.applicant.applicantInfo.researchCapabilities.researchCenters.slice(0, 3).map((center, idx) => (
                                          <li key={idx} className="text-xs">{center.substring(0, 100)}...</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                  {extractedContexts.applicant.applicantInfo.researchCapabilities.academicDepartments && extractedContexts.applicant.applicantInfo.researchCapabilities.academicDepartments.length > 0 && (
                                    <div className="mt-1">
                                      <span className="font-medium">Departments:</span> {extractedContexts.applicant.applicantInfo.researchCapabilities.academicDepartments.slice(0, 4).join('; ')}
                                    </div>
                                  )}
                                </div>
                              )}
                              
                              {/* Track Record Section */}
                              {extractedContexts.applicant.applicantInfo.trackRecord && (
                                <div className="bg-green-100 p-3 rounded">
                                  <strong className="text-green-800">🏆 TRACK RECORD:</strong>
                                  {extractedContexts.applicant.applicantInfo.trackRecord.previousGrants && extractedContexts.applicant.applicantInfo.trackRecord.previousGrants.length > 0 && (
                                    <div className="mt-1">
                                      <span className="font-medium">Previous Grants:</span>
                                      <ul className="ml-4 list-disc">
                                        {extractedContexts.applicant.applicantInfo.trackRecord.previousGrants.slice(0, 2).map((grant, idx) => (
                                          <li key={idx} className="text-xs">{grant.substring(0, 120)}...</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                  {extractedContexts.applicant.applicantInfo.trackRecord.awards && extractedContexts.applicant.applicantInfo.trackRecord.awards.length > 0 && (
                                    <div className="mt-1">
                                      <span className="font-medium">Awards:</span> {extractedContexts.applicant.applicantInfo.trackRecord.awards.slice(0, 3).join('; ')}
                                    </div>
                                  )}
                                  {extractedContexts.applicant.applicantInfo.trackRecord.notableProjects && extractedContexts.applicant.applicantInfo.trackRecord.notableProjects.length > 0 && (
                                    <div className="mt-1">
                                      <span className="font-medium">Notable Projects:</span>
                                      <ul className="ml-4 list-disc">
                                        {extractedContexts.applicant.applicantInfo.trackRecord.notableProjects.slice(0, 2).map((project, idx) => (
                                          <li key={idx} className="text-xs">{project.substring(0, 100)}...</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                </div>
                              )}
                              
                              {/* Resources Section */}
                              {extractedContexts.applicant.applicantInfo.resources && (
                                <div className="bg-green-100 p-3 rounded">
                                  <strong className="text-green-800">🏛️ RESOURCES:</strong>
                                  {extractedContexts.applicant.applicantInfo.resources.facilities && extractedContexts.applicant.applicantInfo.resources.facilities.length > 0 && (
                                    <div className="mt-1">
                                      <span className="font-medium">Facilities:</span> {extractedContexts.applicant.applicantInfo.resources.facilities.slice(0, 3).join('; ')}
                                    </div>
                                  )}
                                  {extractedContexts.applicant.applicantInfo.resources.equipment && extractedContexts.applicant.applicantInfo.resources.equipment.length > 0 && (
                                    <div className="mt-1">
                                      <span className="font-medium">Equipment:</span> {extractedContexts.applicant.applicantInfo.resources.equipment.slice(0, 3).join('; ')}
                                    </div>
                                  )}
                                  {extractedContexts.applicant.applicantInfo.resources.collaborations && extractedContexts.applicant.applicantInfo.resources.collaborations.length > 0 && (
                                    <div className="mt-1">
                                      <span className="font-medium">Collaborations:</span>
                                      <ul className="ml-4 list-disc">
                                        {extractedContexts.applicant.applicantInfo.resources.collaborations.slice(0, 2).map((collab, idx) => (
                                          <li key={idx} className="text-xs">{collab.substring(0, 100)}...</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          )}
                          
                          {/* Fallback to basic info if no structured data */}
                          {!extractedContexts.applicant.applicantInfo && extractedContexts.applicant.mission && (
                            <p><strong>Mission:</strong> {extractedContexts.applicant.mission.substring(0, 200)}...</p>
                          )}
                          {!extractedContexts.applicant.applicantInfo && extractedContexts.applicant.keyInfo.length > 0 && (
                            <div>
                              <strong>Key Information:</strong>
                              <ul className="ml-4 list-disc">
                                {extractedContexts.applicant.keyInfo.slice(0, 3).map((info, idx) => (
                                  <li key={idx} className="text-xs">{info.substring(0, 100)}...</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          {extractedContexts.applicant.warnings.length > 0 && (
                            <div className="mt-2">
                              <strong>⚠️ Warnings:</strong>
                              {extractedContexts.applicant.warnings.map((warning, idx) => (
                                <p key={idx} className="text-orange-600 text-xs">{warning}</p>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Prompt Template */}
            <div className="bg-white rounded-lg shadow-md border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold mb-2">Step 2: Prompt Template</h3>
                <p className="text-gray-600 text-sm">Customize the system prompt sent to the model.</p>
              </div>
              <div className="p-6">
                <textarea
                  value={promptTemplate}
                  onChange={(e) => setPromptTemplate(e.target.value)}
                  placeholder="Enter your prompt template..."
                  rows={10}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm resize-vertical"
                />
              </div>
            </div>

            {/* Final Prompt Preview */}
            {(extractedText || grantDocument) && (
              <div className="bg-white rounded-lg shadow-md border border-gray-200">
                <div className="p-6 border-b border-gray-200">
                  <div className="flex items-center gap-2 mb-2">
                    <Eye className="h-5 w-5" />
                    <h3 className="text-lg font-semibold">Step 3: Final Prompt Preview</h3>
                  </div>
                  <p className="text-gray-600 text-sm">This is exactly what will be sent to GPT-OSS-120B.</p>
                </div>
                <div className="p-6">
                  <div className="bg-gray-50 p-4 rounded-md font-mono text-sm max-h-64 overflow-y-auto border">
                    <pre className="whitespace-pre-wrap">
                      {buildFinalPrompt('Write an executive summary for this grant application')}
                    </pre>
                  </div>
                  <button
                    onClick={() => copyToClipboard(buildFinalPrompt('Write an executive summary for this grant application'))}
                    className="mt-3 flex items-center gap-2 px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <Copy className="h-3 w-3" />
                    Copy Final Prompt
                  </button>
                </div>
              </div>
            )}

            {/* Send to Model Button */}
            {(extractedText || grantDocument) && (
              <div className="bg-white rounded-lg shadow-md border border-gray-200">
                <div className="p-6 border-b border-gray-200">
                  <div className="flex items-center gap-2 mb-2">
                    <Play className="h-5 w-5" />
                    <h3 className="text-lg font-semibold">Step 4: Send to Model</h3>
                  </div>
                  <p className="text-gray-600 text-sm">Manually send the prompt to GPT-OSS-120B when ready.</p>
                </div>
                <div className="p-6">
                  <div className="grid grid-cols-1 gap-3">
                    <button
                      onClick={() => {
                        setCurrentMessage('Write an executive summary for this grant application');
                        sendMessage();
                      }}
                      disabled={isLoading}
                      className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Send className="h-4 w-4" />
                      Send "Executive Summary" to Model
                    </button>
                    <button
                      onClick={() => {
                        setCurrentMessage('What are our key strengths for this funding opportunity?');
                        sendMessage();
                      }}
                      disabled={isLoading}
                      className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Send className="h-4 w-4" />
                      Send "Key Strengths" to Model
                    </button>
                    <button
                      onClick={() => {
                        setCurrentMessage('Draft a project description highlighting our impact in rural education');
                        sendMessage();
                      }}
                      disabled={isLoading}
                      className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Send className="h-4 w-4" />
                      Send "Project Description" to Model
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Chat Interface */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md border border-gray-200 h-[800px] flex flex-col">
              <div className="p-6 border-b border-gray-200 flex-shrink-0">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <MessageSquare className="h-5 w-5" />
                      <h3 className="text-lg font-semibold">Model Chat Interface</h3>
                    </div>
                    <p className="text-gray-600 text-sm">Test your prompts and see model responses in real-time.</p>
                  </div>
                  <button
                    onClick={clearChat}
                    className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <Trash2 className="h-4 w-4" />
                    Clear Chat
                  </button>
                </div>
                <div className="flex items-center gap-4 mt-4">
                  <div className="flex items-center gap-2">
                    <label htmlFor="model-select" className="text-sm font-medium text-gray-700">Model:</label>
                    <select
                      id="model-select"
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      disabled={isLoading}
                      className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <option value="gpt-oss-120b">GPT-OSS-120B (120B params)</option>
                      <option value="gpt-35-turbo-instruct">GPT-3.5-Turbo-Instruct</option>
                    </select>
                  </div>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    isLoading ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                  }`}>
                    {isLoading ? 'Processing...' : 'Ready'}
                  </span>
                </div>
              </div>

              <div className="flex-1 flex flex-col gap-4 p-6">
                {/* Messages Area */}
                <div className="flex-1 overflow-y-auto pr-4">
                  <div className="space-y-4">
                    {messages.length === 0 && (
                      <div className="text-center text-gray-500 py-8">
                        <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>Start a conversation to test your prompts...</p>
                      </div>
                    )}
                    
                    {messages.map((message) => (
                      <div key={message.id} className="space-y-2">
                        <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                          <div className={`max-w-[80%] rounded-lg px-4 py-2 ${
                            message.type === 'user' 
                              ? 'bg-blue-600 text-white' 
                              : message.type === 'system'
                              ? 'bg-red-100 text-red-800 border border-red-200'
                              : 'bg-gray-100 text-gray-900'
                          }`}>
                            <div className="flex items-center gap-2 mb-2">
                              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                                message.type === 'user' ? 'bg-blue-700 text-blue-100' : 'bg-gray-200 text-gray-800'
                              }`}>
                                {message.type === 'user' ? 'You' : message.type === 'system' ? 'System' : 'Assistant'}
                              </span>
                              <span className="text-xs opacity-70">
                                {message.timestamp.toLocaleTimeString()}
                              </span>
                            </div>
                            <div className="whitespace-pre-wrap">{message.content}</div>
                            <button
                              onClick={() => copyToClipboard(message.content)}
                              className="mt-2 p-1 rounded hover:bg-black/10 focus:outline-none"
                            >
                              <Copy className="h-3 w-3" />
                            </button>
                          </div>
                        </div>

                        {/* Show prompt details for user messages */}
                        {message.type === 'user' && message.finalPrompt && (
                          <details className="text-sm">
                            <summary className="cursor-pointer text-gray-600 hover:text-gray-800">
                              View Final Prompt Sent to Model
                            </summary>
                            <div className="mt-2 p-3 bg-gray-50 rounded-md font-mono text-xs overflow-x-auto">
                              <button
                                onClick={() => copyToClipboard(message.finalPrompt!)}
                                className="float-right p-1 rounded hover:bg-gray-200 focus:outline-none"
                              >
                                <Copy className="h-3 w-3" />
                              </button>
                              <pre className="whitespace-pre-wrap">{message.finalPrompt}</pre>
                            </div>
                          </details>
                        )}
                        
                        <hr className="border-gray-200" />
                      </div>
                    ))}
                  </div>
                </div>

                {/* Input Area */}
                <div className="flex gap-2">
                  <textarea
                    value={currentMessage}
                    onChange={(e) => setCurrentMessage(e.target.value)}
                    placeholder="Enter your prompt or question here..."
                    rows={3}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && e.ctrlKey) {
                        sendMessage();
                      }
                    }}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={isLoading || !currentMessage.trim()}
                    className="self-end px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </div>
                <p className="text-xs text-gray-500">
                  Press Ctrl+Enter to send • Model: GPT-OSS-120B • ~7 seconds response time
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}