import React, { useState } from 'react';
import { Users, Award, TrendingUp, Database, Plus, Edit, Trash2, Search } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { useGrants, Grant } from '../contexts/GrantContext';
import GlobalCrawlerDashboard from '../components/admin/GlobalCrawlerDashboard';
import { Link } from 'react-router-dom';

const AdminPage: React.FC = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const { grants } = useGrants();
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');

  if (!user || user.role !== 'admin') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">{t('Unauthorized Access')}</h2>
          <p className="text-gray-600 mb-6">{t('You must be an administrator to access this page.')}</p>
          <Link
            to="/login"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            {t('Login as Admin')}
          </Link>
        </div>
      </div>
    );
  }

  const totalGrants = grants.length;
  const openGrants = grants.filter(g => g.status === 'open').length;
  const totalFunding = grants.reduce((sum, grant) => sum + grant.amount.max, 0);
  const avgRating = grants.reduce((sum, grant) => sum + grant.rating, 0) / grants.length;

  const filteredGrants = grants.filter(grant =>
    grant.title.fr.toLowerCase().includes(searchTerm.toLowerCase()) ||
    grant.funder.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">{t('Administration')}</h1>
          <p className="text-gray-600 mt-2">{t('GrantSeeker Platform Management')}</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <Database className="w-8 h-8 text-custom-red mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">{totalGrants}</p>
                <p className="text-gray-600 text-sm">{t('Total Grants')}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <Award className="w-8 h-8 text-custom-blue mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">{openGrants}</p>
                <p className="text-gray-600 text-sm">{t('Open Grants')}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <TrendingUp className="w-8 h-8 text-custom-red mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">€{(totalFunding / 1000000).toFixed(1)}M</p>
                <p className="text-gray-600 text-sm">{t('Total Funding')}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <Users className="w-8 h-8 text-custom-blue mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">{avgRating.toFixed(1)}</p>
                <p className="text-gray-600 text-sm">{t('Average Rating')}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-8">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: t('Overview') },
              { id: 'grants', label: t('Grants') },
              { id: 'crawler', label: t('Global Web Crawler') },
              { id: 'users', label: t('Users') },
              { id: 'analytics', label: 'Analytics' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-custom-red text-custom-red'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="space-y-6">
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Recent Activity */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">{t('Recent Activity')}</h2>
                <div className="space-y-4">
                  <div className="flex items-center p-3 border rounded-lg">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{t('New grant added')}</p>
                      <p className="text-xs text-gray-500">2 {t('hours ago')}</p>
                    </div>
                  </div>
                  <div className="flex items-center p-3 border rounded-lg">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{t('Data updated')}</p>
                      <p className="text-xs text-gray-500">4 {t('hours ago')}</p>
                    </div>
                  </div>
                  <div className="flex items-center p-3 border rounded-lg">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full mr-3"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{t('New user registered')}</p>
                      <p className="text-xs text-gray-500">6 {t('hours ago')}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* System Status */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">{t('System Status')}</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">{t('Database')}</span>
                    <span className="flex items-center text-green-600">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                      {t('Operational')}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">{t('External API')}</span>
                    <span className="flex items-center text-green-600">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                      {t('Operational')}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">{t('Web server')}</span>
                    <span className="flex items-center text-green-600">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                      {t('Operational')}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">{t('Automatic update')}</span>
                    <span className="flex items-center text-yellow-600">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
                      {t('In progress')}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'grants' && (
            <div className="bg-white rounded-lg shadow-md">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold text-gray-900">{t('Grant Management')}</h2>
                  <button className="bg-custom-red text-white px-4 py-2 rounded-lg hover:bg-custom-red-dark transition-colors flex items-center">
                    <Plus className="w-4 h-4 mr-2" />
                    {t('Add Grant')}
                  </button>
                </div>
                
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    placeholder={t('Search grants...')}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-custom-red focus:border-transparent"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
              </div>
              
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {t('Grant')}
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {t('Status')}
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {t('Amount')}
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {t('Deadline')}
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {t('Actions')}
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredGrants.slice(0, 10).map((grant) => (
                      <tr key={grant.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{grant.title.fr}</div>
                            <div className="text-sm text-gray-500">{grant.funder}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            grant.status === 'open' ? 'bg-green-100 text-green-800' :
                            grant.status === 'closed' ? 'bg-red-100 text-red-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {grant.status === 'open' ? t('Open') : grant.status === 'closed' ? t('Closed') : t('Upcoming')}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          €{grant.amount.max.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {new Date(grant.deadline).toLocaleDateString('fr-FR')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            <button className="text-custom-red hover:text-custom-red-dark">
                              <Edit className="w-4 h-4" />
                            </button>
                            <button className="text-custom-red hover:text-custom-red-dark">
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'crawler' && (
            <GlobalCrawlerDashboard />
          )}

          {activeTab === 'users' && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">{t('User Management')}</h2>
              <p className="text-gray-600">{t('Feature coming soon...')}</p>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">{t('Analytics')}</h2>
              <p className="text-gray-600">{t('Feature coming soon...')}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPage;