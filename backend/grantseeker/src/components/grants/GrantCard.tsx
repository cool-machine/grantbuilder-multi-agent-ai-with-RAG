import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Euro, MapPin, Star, Heart, Clock, Award } from 'lucide-react';
import { Grant } from '../../contexts/GrantContext';
import { useGrants } from '../../contexts/GrantContext';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';

interface GrantCardProps {
  grant: Grant;
}

const GrantCard: React.FC<GrantCardProps> = ({ grant }) => {
  const { favoriteGrants, addToFavorites, removeFromFavorites, createApplication } = useGrants();
  const { user } = useAuth();
  const { currentLanguage, t } = useLanguage();
  const isFavorite = favoriteGrants.includes(grant.id);

  const handleFavoriteToggle = (e: React.MouseEvent) => {
    e.preventDefault();
    if (!user) return;
    
    if (isFavorite) {
      removeFromFavorites(grant.id);
    } else {
      addToFavorites(grant.id);
    }
  };

  const handleCreateApplication = (e: React.MouseEvent) => {
    e.preventDefault();
    if (!user) return;
    createApplication(grant.id);
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
  const deadlineColor = daysLeft <= 7 ? 'text-red-600' : daysLeft <= 30 ? 'text-yellow-600' : 'text-green-600';

  const getStatusBadge = () => {
    const statusColors = {
      open: 'bg-green-100 text-green-800',
      closed: 'bg-red-100 text-red-800',
      upcoming: 'bg-blue-100 text-blue-800'
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[grant.status]}`}>
        {t(grant.status === 'open' ? 'Open' : grant.status === 'closed' ? 'Closed' : 'Upcoming')}
      </span>
    );
  };

  const getTypeBadge = () => {
    const typeColors = {
      government: 'bg-blue-100 text-blue-800',
      eu: 'bg-purple-100 text-purple-800',
      foundation: 'bg-green-100 text-green-800',
      private: 'bg-gray-100 text-gray-800'
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${typeColors[grant.type]}`}>
        {t(grant.type === 'government' ? 'Government' : grant.type === 'eu' ? 'EU' : grant.type === 'foundation' ? 'Foundation' : 'Private')}
      </span>
    );
  };

  const getDifficultyBadge = () => {
    const difficultyColors = {
      easy: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      hard: 'bg-red-100 text-red-800'
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${difficultyColors[grant.difficulty]}`}>
        {t(grant.difficulty === 'easy' ? 'Easy' : grant.difficulty === 'medium' ? 'Medium' : 'Hard')}
      </span>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 overflow-hidden">
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              {getStatusBadge()}
              {getTypeBadge()}
              {getDifficultyBadge()}
            </div>
            <Link to={`/grants/${grant.id}`}>
              <h3 className="text-xl font-semibold text-gray-900 hover:text-blue-600 transition-colors">
                {grant.title[currentLanguage]}
              </h3>
            </Link>
            <p className="text-gray-600 text-sm mt-1">{grant.funder}</p>
          </div>
          
          {user && (
            <button
              onClick={handleFavoriteToggle}
              className={`p-2 rounded-full transition-colors ${
                isFavorite 
                  ? 'text-red-500 hover:text-red-600' 
                  : 'text-gray-400 hover:text-red-500'
              }`}
            >
              <Heart className={`w-5 h-5 ${isFavorite ? 'fill-current' : ''}`} />
            </button>
          )}
        </div>

        <p className="text-gray-700 mb-4 line-clamp-3">
          {grant.description[currentLanguage]}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="flex items-center text-sm text-gray-600">
            <Euro className="w-4 h-4 mr-2 text-custom-red" />
            <span>{formatAmount(grant.amount)}</span>
          </div>
          
          <div className="flex items-center text-sm text-gray-600">
            <Calendar className="w-4 h-4 mr-2 text-custom-blue" />
            <span className={deadlineColor}>
              {daysLeft > 0 ? `${daysLeft} ${t('days left')}` : t('Expired')}
            </span>
          </div>
          
          <div className="flex items-center text-sm text-gray-600">
            <MapPin className="w-4 h-4 mr-2 text-custom-red" />
            <span className="capitalize">{grant.region}</span>
          </div>
        </div>

        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Star className="w-4 h-4 text-yellow-400 fill-current mr-1" />
            <span className="text-sm text-gray-600">
            {grant.rating.toFixed(1)} ({grant.reviews} {t('reviews')})
            </span>
          </div>
          
          <div className="flex flex-wrap gap-1">
            {grant.categories.slice(0, 3).map((category) => (
              <span
                key={category}
                className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
              >
                {category}
              </span>
            ))}
            {grant.categories.length > 3 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                +{grant.categories.length - 3}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-gray-200">
          <Link
            to={`/grants/${grant.id}`}
            className="text-custom-red hover:text-custom-red-dark font-medium text-sm transition-colors"
          >
          {t('View details')} →
          </Link>
          
          {user && (
            <button
              onClick={handleCreateApplication}
              className="bg-custom-red text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-custom-red-dark transition-colors flex items-center"
            >
              <Award className="w-4 h-4 mr-1" />
              {t('Apply')}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default GrantCard;