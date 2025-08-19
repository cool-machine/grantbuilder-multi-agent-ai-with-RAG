import React from 'react';
import DocumentProcessor from '../components/DocumentProcessor';

const DocumentAnalysisPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <DocumentProcessor />
    </div>
  );
};

export default DocumentAnalysisPage;