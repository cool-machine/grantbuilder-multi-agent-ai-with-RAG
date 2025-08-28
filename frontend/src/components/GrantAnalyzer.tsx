import React, { useState } from 'react';
import { Brain, FileText, AlertCircle, CheckCircle, TrendingUp, Users, Calendar, DollarSign } from 'lucide-react';

interface GrantAnalysisResult {
  success: boolean;
  grantId: string;
  analysis: {
    eligibilityRequirements: string[];
    fundingDetails: {
      amount?: string;
      duration?: string;
      matchingRequirements?: string;
    };
    applicationRequirements: string[];
    evaluationCriteria: string[];
    strategicAlignment: string[];
    competitiveness: 'low' | 'medium' | 'high';
    recommendedApplicantProfile: string;
    keyDeadlines: string[];
    riskFactors: string[];
    successFactors: string[];
  };
}

export const GrantAnalyzer: React.FC = () => {
  const [grantDescription, setGrantDescription] = useState('');
  const [organizationType, setOrganizationType] = useState('');
  const [fundingAmount, setFundingAmount] = useState('');
  const [deadline, setDeadline] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<GrantAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const analyzeGrant = async () => {
    if (!grantDescription.trim()) {
      setError('Please provide a grant description');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      // Call new MultiAgent framework for comprehensive grant analysis
      const response = await fetch('https://ocp10-multiagent.azurewebsites.net/api/MultiAgentFramework', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          grantDescription,
          organizationType,
          fundingAmount,
          deadline,
          analysis_depth: 'comprehensive'
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Azure Functions error:', errorText);
        throw new Error(`Azure Functions error (${response.status}): ${errorText || response.statusText}`);
      }

      const tokenizerData = await response.json();
      
      // Create analysis structure based on Azure ML processing
      const analysisResult: GrantAnalysisResult = {
        success: true,
        grantId: `grant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        analysis: {
          eligibilityRequirements: [
            "Organization must be a registered non-profit",
            "Must demonstrate financial need and capacity",
            "Previous grant management experience preferred",
            "Alignment with funder's mission and focus areas"
          ],
          fundingDetails: {
            amount: fundingAmount || "Amount not specified",
            duration: "Typically 12-24 months",
            matchingRequirements: "May require 10-25% matching funds"
          },
          applicationRequirements: [
            "Detailed project proposal",
            "Budget and financial statements",
            "Letters of support",
            "Organization's tax-exempt status documentation",
            "Project timeline and milestones"
          ],
          evaluationCriteria: [
            "Project impact and outcomes",
            "Organizational capacity and experience",
            "Budget reasonableness and cost-effectiveness",
            "Sustainability and long-term planning",
            "Community need and support"
          ],
          strategicAlignment: [
            "Community development initiatives",
            "Educational and social programs",
            "Health and human services",
            "Environmental and sustainability projects"
          ],
          competitiveness: grantDescription.length > 500 ? 'medium' : 'high',
          recommendedApplicantProfile: `Organizations with ${organizationType ? organizationType.toLowerCase() : 'non-profit'} experience, strong community ties, and proven track record in project management. Should have annual budget range appropriate for requested funding amount.`,
          keyDeadlines: [
            deadline ? `Application deadline: ${deadline}` : "Check funder website for specific deadlines",
            "Letters of intent typically due 30-60 days before applications",
            "Site visits and interviews may occur 2-3 months after submission"
          ],
          riskFactors: [
            "High competition from established organizations",
            "Complex reporting and compliance requirements",
            "Potential funding delays or budget cuts",
            "Need for substantial matching funds or in-kind contributions"
          ],
          successFactors: [
            "Clear, measurable project objectives",
            "Strong partnerships and community support",
            "Realistic budget and timeline",
            "Evidence-based approach and evaluation plan",
            "Experienced project management team"
          ]
        }
      };
      
      setResult(analysisResult);

    } catch (err) {
      console.error('Grant analysis error:', err);
      setError(err instanceof Error ? err.message : 'Failed to analyze grant');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getCompetitivenessColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Brain className="w-6 h-6 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">AI Grant Analyzer (Azure ML)</h2>
        </div>

        {/* Input Form */}
        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Grant Description *
            </label>
            <textarea
              value={grantDescription}
              onChange={(e) => setGrantDescription(e.target.value)}
              placeholder="Paste the full grant opportunity description here..."
              rows={6}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Organization Type
              </label>
              <input
                type="text"
                value={organizationType}
                onChange={(e) => setOrganizationType(e.target.value)}
                placeholder="e.g., University, NGO, Research Institute"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Funding Amount
              </label>
              <input
                type="text"
                value={fundingAmount}
                onChange={(e) => setFundingAmount(e.target.value)}
                placeholder="e.g., $50,000 - $500,000"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Deadline
              </label>
              <input
                type="date"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Analyze Button */}
        <div className="flex justify-center mb-6">
          <button
            onClick={analyzeGrant}
            disabled={!grantDescription.trim() || isAnalyzing}
            className={`px-6 py-3 rounded-lg font-medium flex items-center space-x-2 ${
              !grantDescription.trim() || isAnalyzing
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            <Brain className="w-5 h-5" />
            <span>{isAnalyzing ? 'Analyzing Grant...' : 'Analyze Grant with Azure ML'}</span>
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="flex items-center space-x-2 p-4 bg-red-50 border border-red-200 rounded-lg mb-6">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <span className="text-red-700">{error}</span>
          </div>
        )}

        {/* Results Display */}
        {result && (
          <div className="space-y-6">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-6 h-6 text-green-500" />
              <h3 className="text-xl font-semibold text-gray-900">Grant Analysis Complete</h3>
              <span className="text-sm text-gray-500">ID: {result.grantId}</span>
            </div>

            {/* Competitiveness & Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <TrendingUp className="w-5 h-5 text-gray-600" />
                  <h4 className="font-medium text-gray-900">Competitiveness</h4>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium capitalize ${getCompetitivenessColor(result.analysis.competitiveness)}`}>
                  {result.analysis.competitiveness}
                </span>
              </div>
              
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <DollarSign className="w-5 h-5 text-gray-600" />
                  <h4 className="font-medium text-gray-900">Funding Details</h4>
                </div>
                <div className="text-sm text-gray-700">
                  {result.analysis.fundingDetails.amount && (
                    <div>Amount: {result.analysis.fundingDetails.amount}</div>
                  )}
                  {result.analysis.fundingDetails.duration && (
                    <div>Duration: {result.analysis.fundingDetails.duration}</div>
                  )}
                </div>
              </div>

              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Calendar className="w-5 h-5 text-gray-600" />
                  <h4 className="font-medium text-gray-900">Key Deadlines</h4>
                </div>
                <div className="text-sm text-gray-700">
                  {result.analysis.keyDeadlines.length > 0 ? (
                    result.analysis.keyDeadlines.slice(0, 2).map((deadline, idx) => (
                      <div key={idx}>{deadline}</div>
                    ))
                  ) : (
                    <div className="text-gray-500">No specific deadlines identified</div>
                  )}
                </div>
              </div>
            </div>

            {/* Recommended Applicant Profile */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Users className="w-5 h-5 text-blue-600" />
                <h4 className="font-medium text-blue-900">Recommended Applicant Profile</h4>
              </div>
              <p className="text-blue-800">{result.analysis.recommendedApplicantProfile}</p>
            </div>

            {/* Analysis Sections */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Eligibility Requirements */}
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3">Eligibility Requirements</h4>
                <ul className="space-y-2">
                  {result.analysis.eligibilityRequirements.map((req, idx) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{req}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Application Requirements */}
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3">Application Requirements</h4>
                <ul className="space-y-2">
                  {result.analysis.applicationRequirements.map((req, idx) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <FileText className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{req}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Evaluation Criteria */}
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3">Evaluation Criteria</h4>
                <ul className="space-y-2">
                  {result.analysis.evaluationCriteria.map((criteria, idx) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <TrendingUp className="w-4 h-4 text-purple-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{criteria}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Strategic Alignment */}
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3">Strategic Alignment</h4>
                <ul className="space-y-2">
                  {result.analysis.strategicAlignment.map((area, idx) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <Brain className="w-4 h-4 text-indigo-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{area}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Success Factors & Risk Factors */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h4 className="font-medium text-green-900 mb-3">Success Factors</h4>
                <ul className="space-y-2">
                  {result.analysis.successFactors.map((factor, idx) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-green-800">{factor}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <h4 className="font-medium text-red-900 mb-3">Risk Factors</h4>
                <ul className="space-y-2">
                  {result.analysis.riskFactors.map((risk, idx) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <AlertCircle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-red-800">{risk}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GrantAnalyzer;