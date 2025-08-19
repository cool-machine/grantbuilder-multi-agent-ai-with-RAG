import React from 'react';
import { useGrants } from '../../contexts/GrantContext';

const GrantFilters: React.FC = () => {
  const { filters, updateFilters } = useGrants();

  const categories = [
    'environment', 'education', 'social', 'health', 'culture', 'sport',
    'innovation', 'research', 'technology', 'community', 'sustainability'
  ];

  const regions = [
    'national', 'europe', 'ile_de_france', 'provence_alpes_cote_azur',
    'auvergne_rhone_alpes', 'nouvelle_aquitaine', 'occitanie', 'hauts_de_france'
  ];

  const types = ['government', 'eu', 'foundation', 'private'];
  const statuses = ['open', 'upcoming'];
  const difficulties = ['easy', 'medium', 'hard'];

  const handleCategoryChange = (category: string) => {
    const newCategories = filters.categories.includes(category)
      ? filters.categories.filter(c => c !== category)
      : [...filters.categories, category];
    updateFilters({ categories: newCategories });
  };

  return (
    <div className="space-y-6">
      {/* Amount Range */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">Montant (€)</h3>
        <div className="space-y-2">
          <div>
            <label className="block text-xs text-gray-600 mb-1">Minimum</label>
            <input
              type="number"
              value={filters.amountMin}
              onChange={(e) => updateFilters({ amountMin: parseInt(e.target.value) || 0 })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-custom-red focus:border-transparent"
              placeholder="0"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-600 mb-1">Maximum</label>
            <input
              type="number"
              value={filters.amountMax}
              onChange={(e) => updateFilters({ amountMax: parseInt(e.target.value) || 1000000 })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-custom-red focus:border-transparent"
              placeholder="1000000"
            />
          </div>
        </div>
      </div>

      {/* Categories */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">Catégories</h3>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {categories.map((category) => (
            <label key={category} className="flex items-center">
              <input
                type="checkbox"
                checked={filters.categories.includes(category)}
                onChange={() => handleCategoryChange(category)}
                className="rounded border-gray-300 text-custom-red focus:ring-custom-red"
              />
              <span className="ml-2 text-sm text-gray-700 capitalize">{category}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Region */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">Région</h3>
        <select
          value={filters.region}
          onChange={(e) => updateFilters({ region: e.target.value })}
          className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-custom-red focus:border-transparent"
        >
          <option value="">Toutes les régions</option>
          {regions.map((region) => (
            <option key={region} value={region} className="capitalize">
              {region.replace(/_/g, ' ')}
            </option>
          ))}
        </select>
      </div>

      {/* Type */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">Type de financeur</h3>
        <select
          value={filters.type}
          onChange={(e) => updateFilters({ type: e.target.value })}
          className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-custom-red focus:border-transparent"
        >
          <option value="">Tous les types</option>
          <option value="government">Gouvernement</option>
          <option value="eu">Union Européenne</option>
          <option value="foundation">Fondation</option>
          <option value="private">Privé</option>
        </select>
      </div>

      {/* Status */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">Statut</h3>
        <select
          value={filters.status}
          onChange={(e) => updateFilters({ status: e.target.value })}
          className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-custom-red focus:border-transparent"
        >
          <option value="">Tous les statuts</option>
          <option value="open">Ouvert</option>
          <option value="upcoming">À venir</option>
        </select>
      </div>

      {/* Difficulty */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">Difficulté</h3>
        <select
          value={filters.difficulty}
          onChange={(e) => updateFilters({ difficulty: e.target.value })}
          className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-custom-red focus:border-transparent"
        >
          <option value="">Toutes les difficultés</option>
          <option value="easy">Facile</option>
          <option value="medium">Moyen</option>
          <option value="hard">Difficile</option>
        </select>
      </div>

      {/* Reset Button */}
      <button
        onClick={() => updateFilters({
          search: '',
          categories: [],
          region: '',
          type: '',
          status: '',
          amountMin: 0,
          amountMax: 1000000,
          difficulty: '',
          deadlineRange: ''
        })}
        className="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-200 transition-colors"
      >
        Réinitialiser les filtres
      </button>
    </div>
  );
};

export default GrantFilters;