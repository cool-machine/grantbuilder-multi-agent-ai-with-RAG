import React, { useState } from 'react';
import { Calendar, Award, Heart, TrendingUp, Clock, CheckCircle, AlertCircle, XCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useGrants } from '../contexts/GrantContext';
import { Link } from 'react-router-dom';

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const { grants, applications, favoriteGrants, getGrantById } = useGrants();
  const [activeTab, setActiveTab] = useState('overview');

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Accès non autorisé</h2>
          <p className="text-gray-600 mb-6">Vous devez être connecté pour accéder au tableau de bord.</p>
          <Link
            to="/login"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Se connecter
          </Link>
        </div>
      </div>
    );
  }

  const getApplicationStatusIcon = (status: string) => {
    switch (status) {
      case 'saved':
        return <Clock className="w-5 h-5 text-gray-500" />;
      case 'in_progress':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'submitted':
        return <CheckCircle className="w-5 h-5 text-blue-500" />;
      case 'awarded':
        return <Award className="w-5 h-5 text-green-500" />;
      case 'rejected':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getApplicationStatusLabel = (status: string) => {
    const labels = {
      saved: 'Sauvegardé',
      in_progress: 'En cours',
      submitted: 'Soumis',
      awarded: 'Accordé',
      rejected: 'Rejeté'
    };
    return labels[status as keyof typeof labels] || status;
  };

  const favoriteGrantsList = favoriteGrants.map(id => getGrantById(id)).filter(Boolean);

  const upcomingDeadlines = applications
    .filter(app => {
      const deadline = new Date(app.deadline);
      const today = new Date();
      const diffTime = deadline.getTime() - today.getTime();
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      return diffDays <= 30 && diffDays > 0;
    })
    .sort((a, b) => new Date(a.deadline).getTime() - new Date(b.deadline).getTime());

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Tableau de bord</h1>
          <p className="text-gray-600 mt-2">Bienvenue, {user.name}</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <Award className="w-8 h-8 text-custom-red mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">{applications.length}</p>
                <p className="text-gray-600 text-sm">Candidatures</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <Heart className="w-8 h-8 text-custom-red mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">{favoriteGrants.length}</p>
                <p className="text-gray-600 text-sm">Favoris</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <CheckCircle className="w-8 h-8 text-custom-blue mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {applications.filter(app => app.status === 'awarded').length}
                </p>
                <p className="text-gray-600 text-sm">Subventions obtenues</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <TrendingUp className="w-8 h-8 text-custom-red mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {applications.length > 0 ? Math.round((applications.filter(app => app.status === 'awarded').length / applications.length) * 100) : 0}%
                </p>
                <p className="text-gray-600 text-sm">Taux de succès</p>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-8">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: 'Vue d\'ensemble' },
              { id: 'applications', label: 'Mes candidatures' },
              { id: 'favorites', label: 'Mes favoris' },
              { id: 'deadlines', label: 'Échéances' }
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
              {/* Recent Applications */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Candidatures récentes</h2>
                {applications.length === 0 ? (
                  <p className="text-gray-600">Aucune candidature pour le moment.</p>
                ) : (
                  <div className="space-y-4">
                    {applications.slice(0, 5).map((app) => {
                      const grant = getGrantById(app.grantId);
                      if (!grant) return null;
                      return (
                        <div key={app.id} className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex-1">
                            <h3 className="font-medium text-gray-900">{grant.title.fr}</h3>
                            <p className="text-sm text-gray-600">{grant.funder}</p>
                          </div>
                          <div className="flex items-center space-x-2">
                            {getApplicationStatusIcon(app.status)}
                            <span className="text-sm text-gray-600">
                              {getApplicationStatusLabel(app.status)}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Upcoming Deadlines */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Échéances à venir</h2>
                {upcomingDeadlines.length === 0 ? (
                  <p className="text-gray-600">Aucune échéance dans les 30 prochains jours.</p>
                ) : (
                  <div className="space-y-4">
                    {upcomingDeadlines.slice(0, 5).map((app) => {
                      const grant = getGrantById(app.grantId);
                      const daysLeft = Math.ceil((new Date(app.deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
                      if (!grant) return null;
                      return (
                        <div key={app.id} className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex-1">
                            <h3 className="font-medium text-gray-900">{grant.title.fr}</h3>
                            <p className="text-sm text-gray-600">{new Date(app.deadline).toLocaleDateString('fr-FR')}</p>
                          </div>
                          <span className={`text-sm font-medium ${
                            daysLeft <= 7 ? 'text-red-600' : daysLeft <= 14 ? 'text-yellow-600' : 'text-green-600'
                          }`}>
                            {daysLeft} jour{daysLeft > 1 ? 's' : ''}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'applications' && (
            <div className="bg-white rounded-lg shadow-md">
              <div className="p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Toutes mes candidatures</h2>
                {applications.length === 0 ? (
                  <div className="text-center py-8">
                    <Award className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune candidature</h3>
                    <p className="text-gray-600 mb-6">Commencez par explorer les subventions disponibles.</p>
                    <Link
                      to="/grants"
                      className="bg-custom-blue text-white px-6 py-3 rounded-lg hover:bg-custom-blue-light transition-colors"
                    >
                      Explorer les subventions
                    </Link>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Subvention
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Statut
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Date limite
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Créé le
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {applications.map((app) => {
                          const grant = getGrantById(app.grantId);
                          if (!grant) return null;
                          return (
                            <tr key={app.id} className="hover:bg-gray-50">
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div>
                                  <div className="text-sm font-medium text-gray-900">{grant.title.fr}</div>
                                  <div className="text-sm text-gray-500">{grant.funder}</div>
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="flex items-center">
                                  {getApplicationStatusIcon(app.status)}
                                  <span className="ml-2 text-sm text-gray-900">
                                    {getApplicationStatusLabel(app.status)}
                                  </span>
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {new Date(app.deadline).toLocaleDateString('fr-FR')}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {new Date(app.createdAt).toLocaleDateString('fr-FR')}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'favorites' && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Mes subventions favorites</h2>
              {favoriteGrantsList.length === 0 ? (
                <div className="text-center py-8">
                  <Heart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun favori</h3>
                  <p className="text-gray-600 mb-6">Ajoutez des subventions à vos favoris pour les retrouver facilement.</p>
                  <Link
                    to="/grants"
                    className="bg-custom-red text-white px-6 py-3 rounded-lg hover:bg-custom-red-dark transition-colors"
                  >
                    Explorer les subventions
                  </Link>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {favoriteGrantsList.map((grant) => (
                    <div key={grant?.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <h3 className="font-semibold text-gray-900 mb-2">{grant?.title.fr}</h3>
                      <p className="text-sm text-gray-600 mb-3">{grant?.funder}</p>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-500">
                          {grant ? new Date(grant.deadline).toLocaleDateString('fr-FR') : ''}
                        </span>
                        <Link
                          to={`/grants/${grant?.id}`}
                          className="text-custom-red hover:text-custom-red-dark text-sm font-medium"
                        >
                          Voir détails →
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'deadlines' && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Calendrier des échéances</h2>
              {upcomingDeadlines.length === 0 ? (
                <div className="text-center py-8">
                  <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune échéance</h3>
                  <p className="text-gray-600">Toutes vos candidatures sont à jour !</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {upcomingDeadlines.map((app) => {
                    const grant = getGrantById(app.grantId);
                    const daysLeft = Math.ceil((new Date(app.deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
                    if (!grant) return null;
                    return (
                      <div key={app.id} className={`p-4 rounded-lg border-l-4 ${
                        daysLeft <= 7 ? 'border-red-500 bg-red-50' :
                        daysLeft <= 14 ? 'border-yellow-500 bg-yellow-50' :
                        'border-green-500 bg-green-50'
                      }`}>
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900">{grant.title.fr}</h3>
                            <p className="text-sm text-gray-600">{grant.funder}</p>
                            <p className="text-sm text-gray-500 mt-1">
                              Statut: {getApplicationStatusLabel(app.status)}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm text-gray-600">
                              {new Date(app.deadline).toLocaleDateString('fr-FR')}
                            </p>
                            <p className={`text-sm font-medium ${
                              daysLeft <= 7 ? 'text-red-600' :
                              daysLeft <= 14 ? 'text-yellow-600' :
                              'text-green-600'
                            }`}>
                              {daysLeft} jour{daysLeft > 1 ? 's' : ''} restant{daysLeft > 1 ? 's' : ''}
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;