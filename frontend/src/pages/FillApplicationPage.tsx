import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import GrantFormFiller from '../components/GrantFormFiller';
import { useGrants } from '../contexts/GrantContext';

const FillApplicationPage: React.FC = () => {
  const { grantId } = useParams<{ grantId: string }>();
  const { getGrantById } = useGrants();
  const selectedGrant = grantId ? getGrantById(grantId) : undefined;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          {selectedGrant && (
            <div className="mb-4">
              <Link 
                to={`/grants/${grantId}`}
                className="inline-flex items-center text-custom-red hover:text-custom-red-dark transition-colors"
              >
                <ArrowLeft className="w-4 h-4 mr-1" />
                Back to {selectedGrant.title.en}
              </Link>
            </div>
          )}
          
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AI Grant Application Filler
          </h1>
          <p className="text-gray-600">
            Upload your grant form and let AI fill it out professionally using your organization's information.
          </p>
          
          {selectedGrant && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-blue-800 font-medium">
                    Filling application for: {selectedGrant.title.en}
                  </p>
                  <p className="text-blue-600 text-sm mt-1">
                    Funder: {selectedGrant.funder} • Amount: €{selectedGrant.amount.max.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
        
        <GrantFormFiller grantId={grantId} />
      </div>
    </div>
  );
};

export default FillApplicationPage;