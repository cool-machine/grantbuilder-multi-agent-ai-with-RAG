import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Calendar, Euro, MapPin, Star, Heart, Award, ExternalLink, Download, Users, Clock } from 'lucide-react';
import { useGrants } from '../contexts/GrantContext';
import { useAuth } from '../contexts/AuthContext';

const GrantDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { getGrantById, favoriteGrants, addToFavorites, removeFromFavorites, createApplication } = useGrants();
  const { user } = useAuth();

  const grant = id ? getGrantById(id) : undefined;

  if (!grant) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Subvention non trouvée</h2>
          <p className="text-gray-600 mb-6">La subvention que vous recherchez n'existe pas ou a été supprimée.</p>
          <button
            onClick={() => navigate('/grants')}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retour aux subventions
          </button>
        </div>
      </div>
    );
  }

  const isFavorite = favoriteGrants.includes(grant.id);

  const handleFavoriteToggle = () => {
    if (!user) return;
    
    if (isFavorite) {
      removeFromFavorites(grant.id);
    } else {
      addToFavorites(grant.id);
    }
  };

  const handleCreateApplication = () => {
    if (!user) return;
    createApplication(grant.id);
    // Show success message or redirect
  };

  const formatAmount = (amount: { min: number; max: number; currency: string }) => {
    if (amount.min === amount.max) {
      return `${amount.max.toLocaleString()} ${amount.currency}`;
    }
    return `${amount.min.toLocaleString()} - ${amount.max.toLocaleString()} ${amount.currency}`;
  };

  const getDaysUntilDeadline = () => {
    const deadline = new Date(grant.deadline);
    const today = new Date();
    const diffTime = deadline.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const daysLeft = getDaysUntilDeadline();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <button
          onClick={() => navigate('/grants')}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6 transition-colors"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Retour aux subventions
        </button>

        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  grant.status === 'open' ? 'bg-green-100 text-green-800' :
                  grant.status === 'closed' ? 'bg-red-100 text-red-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {grant.status === 'open' ? 'Ouvert' : grant.status === 'closed' ? 'Fermé' : 'À venir'}
                </span>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  grant.type === 'government' ? 'bg-blue-100 text-blue-800' :
                  grant.type === 'eu' ? 'bg-purple-100 text-purple-800' :
                  grant.type === 'foundation' ? 'bg-green-100 text-green-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {grant.type === 'government' ? 'Gouvernement' :
                   grant.type === 'eu' ? 'UE' :
                   grant.type === 'foundation' ? 'Fondation' : 'Privé'}
                </span>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  grant.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
                  grant.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {grant.difficulty === 'easy' ? 'Facile' :
                   grant.difficulty === 'medium' ? 'Moyen' : 'Difficile'}
                </span>
              </div>
              
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{grant.title.fr}</h1>
              <p className="text-xl text-gray-600">{grant.funder}</p>
            </div>
            
            {user && (
              <button
                onClick={handleFavoriteToggle}
                className={`p-3 rounded-full transition-colors ${
                  isFavorite 
                    ? 'text-red-500 hover:text-red-600 bg-red-50' 
                    : 'text-gray-400 hover:text-red-500 hover:bg-red-50'
                }`}
              >
                <Heart className={`w-6 h-6 ${isFavorite ? 'fill-current' : ''}`} />
              </button>
            )}
          </div>

          {/* Key Information */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="flex items-center">
              <Euro className="w-6 h-6 text-custom-red mr-3" />
              <div>
                <p className="text-sm text-gray-600">Montant</p>
                <p className="font-semibold">{formatAmount(grant.amount)}</p>
              </div>
            </div>
            
            <div className="flex items-center">
              <Calendar className="w-6 h-6 text-custom-blue mr-3" />
              <div>
                <p className="text-sm text-gray-600">Date limite</p>
                <p className={`font-semibold ${daysLeft <= 7 ? 'text-red-600' : daysLeft <= 30 ? 'text-yellow-600' : 'text-green-600'}`}>
                  {daysLeft > 0 ? `${daysLeft} jours` : 'Expiré'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center">
              <MapPin className="w-6 h-6 text-custom-red mr-3" />
              <div>
                <p className="text-sm text-gray-600">Région</p>
                <p className="font-semibold capitalize">{grant.region}</p>
              </div>
            </div>
            
            <div className="flex items-center">
              <Star className="w-6 h-6 text-yellow-500 mr-3" />
              <div>
                <p className="text-sm text-gray-600">Note</p>
                <p className="font-semibold">{grant.rating.toFixed(1)} ({grant.reviews} avis)</p>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          {user && (
            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={handleCreateApplication}
               className="bg-custom-red text-white px-8 py-3 rounded-lg font-semibold hover:bg-custom-red-dark transition-colors flex items-center justify-center"
              >
                <Award className="w-5 h-5 mr-2" />
                Créer une candidature
              </button>
              <a
                href={grant.sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-gray-100 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-200 transition-colors flex items-center justify-center"
              >
                <ExternalLink className="w-5 h-5 mr-2" />
                Voir la source
              </a>
            </div>
          )}
        </div>

        {/* Content Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Description */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Description</h2>
              <div className="prose max-w-none">
                <p className="text-gray-700 leading-relaxed">{grant.description.fr}</p>
              </div>
            </div>

            {/* Eligibility */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Critères d'éligibilité</h2>
              <ul className="space-y-2">
                {grant.eligibility.map((criterion, index) => (
                  <li key={index} className="flex items-center text-gray-700">
                    <div className="w-2 h-2 bg-custom-blue rounded-full mr-3"></div>
                    <span className="capitalize">{criterion.replace(/_/g, ' ')}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Categories */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Catégories</h2>
              <div className="flex flex-wrap gap-2">
                {grant.categories.map((category) => (
                  <span
                    key={category}
                    className="px-3 py-1 bg-red-50 text-custom-red text-sm rounded-full font-medium capitalize"
                  >
                    {category}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Info */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Informations rapides</h3>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-600">Date de publication</p>
                  <p className="font-medium">{new Date(grant.lastUpdated).toLocaleDateString('fr-FR')}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Date limite</p>
                  <p className="font-medium">{new Date(grant.deadline).toLocaleDateString('fr-FR')}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Dernière mise à jour</p>
                  <p className="font-medium">{new Date(grant.lastUpdated).toLocaleDateString('fr-FR')}</p>
                </div>
              </div>
            </div>

            {/* Community Stats */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Statistiques communauté</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Avis</span>
                  <span className="font-medium">{grant.reviews}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Note moyenne</span>
                  <span className="font-medium">{grant.rating.toFixed(1)}/5</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Candidatures estimées</span>
                  <span className="font-medium">~{Math.floor(grant.reviews * 2.5)}</span>
                </div>
              </div>
            </div>

            {/* Tips */}
            <div className="bg-red-25 rounded-lg p-6 border border-red-100">
              <h3 className="text-lg font-semibold text-custom-red mb-3">💡 {t('Tips')}</h3>
              <ul className="space-y-2 text-sm text-custom-red">
                <li>• {t('Prepare your documents in advance')}</li>
                <li>• {t('Read all criteria carefully')}</li>
                <li>• {t('Contact the funder if you have questions')}</li>
                <li>• {t('Submit your application before the deadline')}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GrantDetailPage;