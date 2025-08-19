import React, { createContext, useContext, useState, useEffect } from 'react';

export interface Grant {
  id: string;
  title: {
    fr: string;
    en: string;
  };
  description: {
    fr: string;
    en: string;
  };
  funder: string;
  amount: {
    min: number;
    max: number;
    currency: string;
  };
  deadline: string;
  categories: string[];
  eligibility: string[];
  region: string;
  type: 'government' | 'eu' | 'foundation' | 'private';
  status: 'open' | 'closed' | 'upcoming';
  sourceUrl: string;
  lastUpdated: string;
  rating: number;
  reviews: number;
  difficulty: 'easy' | 'medium' | 'hard';
}

interface GrantApplication {
  id: string;
  grantId: string;
  status: 'saved' | 'in_progress' | 'submitted' | 'awarded' | 'rejected';
  notes: string;
  documents: string[];
  deadline: string;
  createdAt: string;
  updatedAt: string;
}

interface GrantContextType {
  grants: Grant[];
  applications: GrantApplication[];
  favoriteGrants: string[];
  loading: boolean;
  searchGrants: (query: string, filters: GrantFilters) => Grant[];
  getGrantById: (id: string) => Grant | undefined;
  addToFavorites: (grantId: string) => void;
  removeFromFavorites: (grantId: string) => void;
  createApplication: (grantId: string) => void;
  updateApplication: (id: string, updates: Partial<GrantApplication>) => void;
  filters: GrantFilters;
  updateFilters: (filters: Partial<GrantFilters>) => void;
}

export interface GrantFilters {
  search: string;
  categories: string[];
  region: string;
  type: string;
  status: string;
  amountMin: number;
  amountMax: number;
  difficulty: string;
  deadlineRange: string;
}

const GrantContext = createContext<GrantContextType | undefined>(undefined);

export const useGrants = () => {
  const context = useContext(GrantContext);
  if (context === undefined) {
    throw new Error('useGrants must be used within a GrantProvider');
  }
  return context;
};

// Mock data
const mockGrants: Grant[] = [
  {
    id: '1',
    title: {
      fr: 'Subvention pour l\'Innovation Environnementale',
      en: 'Environmental Innovation Grant'
    },
    description: {
      fr: 'Financement pour les projets innovants en matière d\'environnement et de développement durable.',
      en: 'Funding for innovative environmental and sustainable development projects.'
    },
    funder: 'Ministère de la Transition Écologique',
    amount: { min: 10000, max: 100000, currency: 'EUR' },
    deadline: '2024-06-30',
    categories: ['environment', 'innovation', 'sustainability'],
    eligibility: ['association_loi_1901', 'fondation'],
    region: 'national',
    type: 'government',
    status: 'open',
    sourceUrl: 'https://www.ecologie.gouv.fr',
    lastUpdated: '2024-01-15',
    rating: 4.2,
    reviews: 18,
    difficulty: 'medium'
  },
  {
    id: '2',
    title: {
      fr: 'Programme Horizon Europe - Action Climatique',
      en: 'Horizon Europe Programme - Climate Action'
    },
    description: {
      fr: 'Financement européen pour la recherche et l\'innovation en action climatique.',
      en: 'European funding for climate action research and innovation.'
    },
    funder: 'Commission Européenne',
    amount: { min: 50000, max: 500000, currency: 'EUR' },
    deadline: '2024-09-15',
    categories: ['climate', 'research', 'innovation'],
    eligibility: ['all_nonprofits'],
    region: 'europe',
    type: 'eu',
    status: 'open',
    sourceUrl: 'https://ec.europa.eu/horizon-europe',
    lastUpdated: '2024-01-10',
    rating: 4.7,
    reviews: 42,
    difficulty: 'hard'
  },
  {
    id: '3',
    title: {
      fr: 'Fondation de France - Solidarité Sociale',
      en: 'Foundation of France - Social Solidarity'
    },
    description: {
      fr: 'Soutien aux initiatives de solidarité sociale et d\'aide aux plus démunis.',
      en: 'Support for social solidarity initiatives and assistance to the underprivileged.'
    },
    funder: 'Fondation de France',
    amount: { min: 5000, max: 50000, currency: 'EUR' },
    deadline: '2024-04-30',
    categories: ['social', 'solidarity', 'community'],
    eligibility: ['association_loi_1901'],
    region: 'national',
    type: 'foundation',
    status: 'open',
    sourceUrl: 'https://www.fondationdefrance.org',
    lastUpdated: '2024-01-12',
    rating: 4.5,
    reviews: 31,
    difficulty: 'easy'
  }
];

export const GrantProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [grants] = useState<Grant[]>(mockGrants);
  const [applications, setApplications] = useState<GrantApplication[]>([]);
  const [favoriteGrants, setFavoriteGrants] = useState<string[]>([]);
  const [loading] = useState(false);
  const [filters, setFilters] = useState<GrantFilters>({
    search: '',
    categories: [],
    region: '',
    type: '',
    status: '',
    amountMin: 0,
    amountMax: 1000000,
    difficulty: '',
    deadlineRange: ''
  });

  useEffect(() => {
    // Load favorites from localStorage
    const storedFavorites = localStorage.getItem('favoriteGrants');
    if (storedFavorites) {
      setFavoriteGrants(JSON.parse(storedFavorites));
    }

    // Load applications from localStorage
    const storedApplications = localStorage.getItem('grantApplications');
    if (storedApplications) {
      setApplications(JSON.parse(storedApplications));
    }
  }, []);

  const searchGrants = (query: string, searchFilters: GrantFilters): Grant[] => {
    return grants.filter(grant => {
      const matchesSearch = !query || 
        grant.title.fr.toLowerCase().includes(query.toLowerCase()) ||
        grant.title.en.toLowerCase().includes(query.toLowerCase()) ||
        grant.description.fr.toLowerCase().includes(query.toLowerCase()) ||
        grant.funder.toLowerCase().includes(query.toLowerCase());

      const matchesCategories = searchFilters.categories.length === 0 ||
        searchFilters.categories.some(cat => grant.categories.includes(cat));

      const matchesType = !searchFilters.type || grant.type === searchFilters.type;
      const matchesStatus = !searchFilters.status || grant.status === searchFilters.status;
      const matchesDifficulty = !searchFilters.difficulty || grant.difficulty === searchFilters.difficulty;
      
      const matchesAmount = grant.amount.min >= searchFilters.amountMin && 
        grant.amount.max <= searchFilters.amountMax;

      return matchesSearch && matchesCategories && matchesType && 
        matchesStatus && matchesDifficulty && matchesAmount;
    });
  };

  const getGrantById = (id: string): Grant | undefined => {
    return grants.find(grant => grant.id === id);
  };

  const addToFavorites = (grantId: string) => {
    const newFavorites = [...favoriteGrants, grantId];
    setFavoriteGrants(newFavorites);
    localStorage.setItem('favoriteGrants', JSON.stringify(newFavorites));
  };

  const removeFromFavorites = (grantId: string) => {
    const newFavorites = favoriteGrants.filter(id => id !== grantId);
    setFavoriteGrants(newFavorites);
    localStorage.setItem('favoriteGrants', JSON.stringify(newFavorites));
  };

  const createApplication = (grantId: string) => {
    const grant = getGrantById(grantId);
    if (!grant) return;

    const newApplication: GrantApplication = {
      id: Date.now().toString(),
      grantId,
      status: 'saved',
      notes: '',
      documents: [],
      deadline: grant.deadline,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    const newApplications = [...applications, newApplication];
    setApplications(newApplications);
    localStorage.setItem('grantApplications', JSON.stringify(newApplications));
  };

  const updateApplication = (id: string, updates: Partial<GrantApplication>) => {
    const newApplications = applications.map(app => 
      app.id === id ? { ...app, ...updates, updatedAt: new Date().toISOString() } : app
    );
    setApplications(newApplications);
    localStorage.setItem('grantApplications', JSON.stringify(newApplications));
  };

  const updateFilters = (newFilters: Partial<GrantFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  const value = {
    grants,
    applications,
    favoriteGrants,
    loading,
    searchGrants,
    getGrantById,
    addToFavorites,
    removeFromFavorites,
    createApplication,
    updateApplication,
    filters,
    updateFilters
  };

  return <GrantContext.Provider value={value}>{children}</GrantContext.Provider>;
};