import React, { useState, useEffect } from 'react';
import { Search, Filter, MapPin, Calendar, Euro, Star, ChevronDown } from 'lucide-react';
import { useGrants } from '../contexts/GrantContext';
import GrantCard from '../components/grants/GrantCard';
import GrantFilters from '../components/grants/GrantFilters';

const GrantsPage: React.FC = () => {
  const { grants, searchGrants, filters, updateFilters } = useGrants();
  const [filteredGrants, setFilteredGrants] = useState(grants);
  const [showFilters, setShowFilters] = useState(false);
  const [sortBy, setSortBy] = useState('deadline');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  useEffect(() => {
    const results = searchGrants(filters.search, filters);
    
    // Sort results
    const sorted = [...results].sort((a, b) => {
      let aValue: any, bValue: any;
      
      switch (sortBy) {
        case 'deadline':
          aValue = new Date(a.deadline);
          bValue = new Date(b.deadline);
          break;
        case 'amount':
          aValue = a.amount.max;
          bValue = b.amount.max;
          break;
        case 'rating':
          aValue = a.rating;
          bValue = b.rating;
          break;
        case 'title':
          aValue = a.title.fr;
          bValue = b.title.fr;
          break;
        default:
          return 0;
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
    
    setFilteredGrants(sorted);
  }, [filters, grants, searchGrants, sortBy, sortOrder]);

  const handleSearch = (query: string) => {
    updateFilters({ search: query });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Découvrir les subventions</h1>
              <p className="mt-2 text-gray-600">
                {filteredGrants.length} subventions disponibles
              </p>
            </div>
            
            {/* Search Bar */}
            <div className="mt-6 lg:mt-0 lg:w-96">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Rechercher des subventions..."
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-custom-red focus:border-transparent"
                  value={filters.search}
                  onChange={(e) => handleSearch(e.target.value)}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters Sidebar */}
          <div className="lg:w-80">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-gray-900">Filtres</h2>
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className="lg:hidden p-2 text-gray-500 hover:text-gray-700"
                >
                  <Filter className="w-5 h-5" />
                </button>
              </div>
              
              <div className={`${showFilters ? 'block' : 'hidden'} lg:block`}>
                <GrantFilters />
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {/* Sort Controls */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">Trier par:</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:ring-2 focus:ring-custom-red focus:border-transparent"
                >
                  <option value="deadline">Date limite</option>
                  <option value="amount">Montant</option>
                  <option value="rating">Note</option>
                  <option value="title">Titre</option>
                </select>
                <button
                  onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                  className="p-1 text-gray-500 hover:text-gray-700"
                >
                  <ChevronDown className={`w-4 h-4 transform ${sortOrder === 'desc' ? 'rotate-180' : ''}`} />
                </button>
              </div>
            </div>

            {/* Results */}
            {filteredGrants.length === 0 ? (
              <div className="bg-white rounded-lg shadow-md p-12 text-center">
                <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucune subvention trouvée</h3>
                <p className="text-gray-600">
                  Essayez de modifier vos critères de recherche ou d'élargir vos filtres.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-6">
                {filteredGrants.map((grant) => (
                  <GrantCard key={grant.id} grant={grant} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default GrantsPage;