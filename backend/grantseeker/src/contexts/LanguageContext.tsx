import React, { createContext, useContext, useState, useEffect } from 'react';

export type Language = 'fr' | 'en';

interface LanguageContextType {
  currentLanguage: Language;
  toggleLanguage: () => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

// Translation dictionary
const translations = {
  fr: {
    // Navigation
    'Grants': 'Subventions',
    'Dashboard': 'Tableau de bord',
    'Administration': 'Administration',
    'Login': 'Connexion',
    'Register': 'S\'inscrire',
    'Logout': 'Déconnexion',
    'Settings': 'Paramètres',
    
    // Home Page
    'Find perfect funding for your': 'Trouvez le financement parfait pour votre',
    'association': 'association',
    'The French platform that connects associations with the best grant opportunities': 'La plateforme française qui connecte les associations aux meilleures opportunités de subventions',
    'More than 10,000 grants referenced and updated daily': 'Plus de 10,000 subventions référencées et mises à jour quotidiennement',
    'Explore grants': 'Explorer les subventions',
    'Create free account': 'Créer un compte gratuit',
    'Why choose GrantSeeker?': 'Pourquoi choisir GrantSeeker ?',
    'We simplify funding search to allow associations to focus on their mission': 'Nous simplifions la recherche de financement pour permettre aux associations de se concentrer sur leur mission',
    
    // Features
    'Smart Matching': 'Matching Intelligent',
    'Our algorithm analyzes your profile and recommends the most suitable grants': 'Notre algorithme analyse votre profil et vous recommande les subventions les plus adaptées',
    'Real-time Alerts': 'Alertes en Temps Réel',
    'Receive notifications for new grants and important deadlines': 'Recevez des notifications pour les nouvelles subventions et les dates limites importantes',
    'Verified Data': 'Données Vérifiées',
    'All our data is verified daily to ensure accuracy and timeliness': 'Toutes nos données sont vérifiées quotidiennement pour garantir leur exactitude et leur actualité',
    'Active Community': 'Communauté Active',
    'Exchange with other associations, share experiences and learn from others\' successes': 'Échangez avec d\'autres associations, partagez vos expériences et apprenez des succès des autres',
    'Application Tracking': 'Suivi des Candidatures',
    'Manage all your applications from a central dashboard with automatic reminders': 'Gérez toutes vos candidatures depuis un tableau de bord central avec des rappels automatiques',
    'Advanced Analytics': 'Analytics Avancées',
    'Analyze your success rates and optimize future applications with detailed reports': 'Analysez vos taux de succès et optimisez vos futures candidatures grâce à nos rapports détaillés',
    
    // Stats
    'Referenced grants': 'Subventions référencées',
    'User associations': 'Associations utilisatrices',
    'Funding obtained': 'Financements obtenus',
    'Satisfaction rate': 'Taux de satisfaction',
    
    // CTA
    'Ready to transform your funding search?': 'Prêt à transformer votre recherche de financement ?',
    'Join thousands of associations that have already found their funding thanks to GrantSeeker': 'Rejoignez des milliers d\'associations qui ont déjà trouvé leur financement grâce à GrantSeeker',
    'Start for free': 'Commencer gratuitement',
    'View grants': 'Voir les subventions',
    
    // Grant Details
    'Amount': 'Montant',
    'Deadline': 'Date limite',
    'Region': 'Région',
    'Rating': 'Note',
    'reviews': 'avis',
    'Create application': 'Créer une candidature',
    'View source': 'Voir la source',
    'Description': 'Description',
    'Eligibility criteria': 'Critères d\'éligibilité',
    'Categories': 'Catégories',
    'Quick info': 'Informations rapides',
    'Publication date': 'Date de publication',
    'Last updated': 'Dernière mise à jour',
    'Community stats': 'Statistiques communauté',
    'Reviews': 'Avis',
    'Average rating': 'Note moyenne',
    'Estimated applications': 'Candidatures estimées',
    'Tips': 'Conseils',
    
    // Common
    'Open': 'Ouvert',
    'Closed': 'Fermé',
    'Upcoming': 'À venir',
    'Government': 'Gouvernement',
    'EU': 'UE',
    'Foundation': 'Fondation',
    'Private': 'Privé',
    'Easy': 'Facile',
    'Medium': 'Moyen',
    'Hard': 'Difficile',
    'days left': 'jours restants',
    'Expired': 'Expiré',
    'Apply': 'Candidater',
    'View details': 'Voir les détails',
    'Add to favorites': 'Ajouter aux favoris',
    'Remove from favorites': 'Retirer des favoris',
    
    // Admin
    'Global Web Crawler': 'Crawler Web Global',
    'Start Global Crawl': 'Démarrer le Crawl Global',
    'Schedule Daily': 'Programmer Quotidien',
    'Crawling Web...': 'Crawl en cours...',
    'Total Sources': 'Sources Totales',
    'Active Sources': 'Sources Actives',
    'Last Crawl': 'Dernier Crawl',
    'Status': 'Statut',
    'Running': 'En cours',
    'Idle': 'Inactif',
    'Never': 'Jamais',
    
    // Login/Register
    'Login to your account': 'Connexion à votre compte',
    'Don\'t have an account?': 'Pas encore de compte ?',
    'Create one for free': 'Créez-en un gratuitement',
    'Email address': 'Adresse email',
    'Password': 'Mot de passe',
    'Remember me': 'Se souvenir de moi',
    'Forgot password?': 'Mot de passe oublié ?',
    'Sign in': 'Se connecter',
    'Create your account': 'Créer votre compte',
    'Already have an account?': 'Déjà un compte ?',
    'Sign in here': 'Connectez-vous',
    'Full name': 'Nom complet',
    'Organization': 'Organisation',
    'Confirm password': 'Confirmer le mot de passe',
    'I accept the': 'J\'accepte les',
    'terms of service': 'conditions d\'utilisation',
    'and': 'et la',
    'privacy policy': 'politique de confidentialité',
    'Create my account': 'Créer mon compte',
    
    // Admin
    'Admin Access': 'Accès Admin',
    'Any password': 'N\'importe quel mot de passe',
    'By signing in, you accept our': 'En vous connectant, vous acceptez nos',
    'and our': 'et notre',
    'Unauthorized Access': 'Accès non autorisé',
    'You must be an administrator to access this page.': 'Vous devez être administrateur pour accéder à cette page.',
    'Login as Admin': 'Se connecter en tant qu\'admin',
    'GrantSeeker Platform Management': 'Gestion de la plateforme GrantSeeker',
    'Total Grants': 'Total des subventions',
    'Open Grants': 'Subventions ouvertes',
    'Total Funding': 'Financement total',
    'Average Rating': 'Note moyenne',
    'Overview': 'Vue d\'ensemble',
    'Users': 'Utilisateurs',
    
    // Admin Page Content
    'GrantSeeker Platform Management': 'Gestion de la plateforme GrantSeeker',
    'Total Grants': 'Total des subventions',
    'Open Grants': 'Subventions ouvertes',
    'Total Funding': 'Financement total',
    'Average Rating': 'Note moyenne',
    'Recent Activity': 'Activité récente',
    'System Status': 'État du système',
    'New grant added': 'Nouvelle subvention ajoutée',
    'Data updated': 'Données mises à jour',
    'New user registered': 'Nouvel utilisateur inscrit',
    'hours ago': 'heures',
    'Database': 'Base de données',
    'External API': 'API externe',
    'Web server': 'Serveur web',
    'Automatic update': 'Mise à jour automatique',
    'Operational': 'Opérationnel',
    'In progress': 'En cours',
    'Grant Management': 'Gestion des subventions',
    'Add Grant': 'Ajouter une subvention',
    'Search grants...': 'Rechercher des subventions...',
    'Grant': 'Subvention',
    'Amount': 'Montant',
    'Deadline': 'Date limite',
    'Actions': 'Actions',
    'User Management': 'Gestion des utilisateurs',
    'Feature coming soon...': 'Fonctionnalité à venir...',
    'Analytics': 'Analytics',
    
    // Additional HomePage translations
    'Discover and manage grant opportunities for French nonprofits': 'Discover and manage grant opportunities for French nonprofits',
    'Prepare your documents in advance': 'Prepare your documents in advance',
    'Read all criteria carefully': 'Read all criteria carefully',
    'Contact the funder if you have questions': 'Contact the funder if you have questions',
    'Submit your application before the deadline': 'Submit your application before the deadline',
    'More than': 'More than',
    'associations already use GrantSeeker': 'associations already use GrantSeeker',
    
    // Footer and additional translations
    'The reference platform for discovering and managing your grant applications': 'La plateforme de référence pour découvrir et gérer vos demandes de subventions',
    'We help French associations find the funding they need': 'Nous aidons les associations françaises à trouver le financement dont elles ont besoin',
    'Quick Links': 'Liens rapides',
    'User Guide': 'Guide d\'utilisation',
    'FAQ': 'FAQ',
    'Support': 'Support',
    'Help Center': 'Centre d\'aide',
    'Contact Us': 'Nous contacter',
    'Report an Issue': 'Signaler un problème',
    'Community': 'Communauté',
    'All rights reserved': 'Tous droits réservés',
    'Privacy Policy': 'Politique de confidentialité',
    'Terms of Service': 'Conditions d\'utilisation',
    'GDPR': 'RGPD',
  },
  en: {
    // Navigation
    'Grants': 'Grants',
    'Dashboard': 'Dashboard',
    'Administration': 'Administration',
    'Login': 'Login',
    'Register': 'Register',
    'Logout': 'Logout',
    'Settings': 'Settings',
    
    // Home Page
    'Find perfect funding for your': 'Find perfect funding for your',
    'association': 'organization',
    'The French platform that connects associations with the best grant opportunities': 'The French platform that connects organizations with the best grant opportunities',
    'More than 10,000 grants referenced and updated daily': 'More than 10,000 grants referenced and updated daily',
    'Explore grants': 'Explore grants',
    'Create free account': 'Create free account',
    'Why choose GrantSeeker?': 'Why choose GrantSeeker?',
    'We simplify funding search to allow associations to focus on their mission': 'We simplify funding search to allow organizations to focus on their mission',
    
    // Features
    'Smart Matching': 'Smart Matching',
    'Our algorithm analyzes your profile and recommends the most suitable grants': 'Our algorithm analyzes your profile and recommends the most suitable grants',
    'Real-time Alerts': 'Real-time Alerts',
    'Receive notifications for new grants and important deadlines': 'Receive notifications for new grants and important deadlines',
    'Verified Data': 'Verified Data',
    'All our data is verified daily to ensure accuracy and timeliness': 'All our data is verified daily to ensure accuracy and timeliness',
    'Active Community': 'Active Community',
    'Exchange with other associations, share experiences and learn from others\' successes': 'Exchange with other organizations, share experiences and learn from others\' successes',
    'Application Tracking': 'Application Tracking',
    'Manage all your applications from a central dashboard with automatic reminders': 'Manage all your applications from a central dashboard with automatic reminders',
    'Advanced Analytics': 'Advanced Analytics',
    'Analyze your success rates and optimize future applications with detailed reports': 'Analyze your success rates and optimize future applications with detailed reports',
    
    // Stats
    'Referenced grants': 'Referenced grants',
    'User associations': 'User organizations',
    'Funding obtained': 'Funding obtained',
    'Satisfaction rate': 'Satisfaction rate',
    
    // CTA
    'Ready to transform your funding search?': 'Ready to transform your funding search?',
    'Join thousands of associations that have already found their funding thanks to GrantSeeker': 'Join thousands of organizations that have already found their funding thanks to GrantSeeker',
    'Start for free': 'Start for free',
    'View grants': 'View grants',
    
    // Grant Details
    'Amount': 'Amount',
    'Deadline': 'Deadline',
    'Region': 'Region',
    'Rating': 'Rating',
    'reviews': 'reviews',
    'Create application': 'Create application',
    'View source': 'View source',
    'Description': 'Description',
    'Eligibility criteria': 'Eligibility criteria',
    'Categories': 'Categories',
    'Quick info': 'Quick info',
    'Publication date': 'Publication date',
    'Last updated': 'Last updated',
    'Community stats': 'Community stats',
    'Reviews': 'Reviews',
    'Average rating': 'Average rating',
    'Estimated applications': 'Estimated applications',
    'Tips': 'Tips',
    
    // Common
    'Open': 'Open',
    'Closed': 'Closed',
    'Upcoming': 'Upcoming',
    'Government': 'Government',
    'EU': 'EU',
    'Foundation': 'Foundation',
    'Private': 'Private',
    'Easy': 'Easy',
    'Medium': 'Medium',
    'Hard': 'Hard',
    'days left': 'days left',
    'Expired': 'Expired',
    'Apply': 'Apply',
    'View details': 'View details',
    'Add to favorites': 'Add to favorites',
    'Remove from favorites': 'Remove from favorites',
    
    // Admin
    'Global Web Crawler': 'Global Web Crawler',
    'Start Global Crawl': 'Start Global Crawl',
    'Schedule Daily': 'Schedule Daily',
    'Crawling Web...': 'Crawling Web...',
    'Total Sources': 'Total Sources',
    'Active Sources': 'Active Sources',
    'Last Crawl': 'Last Crawl',
    'Status': 'Status',
    'Running': 'Running',
    'Idle': 'Idle',
    'Never': 'Never',
    
    // Login/Register
    'Login to your account': 'Login to your account',
    'Don\'t have an account?': 'Don\'t have an account?',
    'Create one for free': 'Create one for free',
    'Email address': 'Email address',
    'Password': 'Password',
    'Remember me': 'Remember me',
    'Forgot password?': 'Forgot password?',
    'Sign in': 'Sign in',
    'Create your account': 'Create your account',
    'Already have an account?': 'Already have an account?',
    'Sign in here': 'Sign in here',
    'Full name': 'Full name',
    'Organization': 'Organization',
    'Confirm password': 'Confirm password',
    'I accept the': 'I accept the',
    'terms of service': 'terms of service',
    'and': 'and',
    'privacy policy': 'privacy policy',
    'Create my account': 'Create my account',
    
    // Admin
    'Admin Access': 'Admin Access',
    'Any password': 'Any password',
    'By signing in, you accept our': 'By signing in, you accept our',
    'and our': 'and our',
    'Unauthorized Access': 'Unauthorized Access',
    'You must be an administrator to access this page.': 'You must be an administrator to access this page.',
    'Login as Admin': 'Login as Admin',
    'GrantSeeker Platform Management': 'GrantSeeker Platform Management',
    'Total Grants': 'Total Grants',
    'Open Grants': 'Open Grants',
    'Total Funding': 'Total Funding',
    'Average Rating': 'Average Rating',
    'Overview': 'Overview',
    'Users': 'Users',
    
    // Admin Page Content
    'GrantSeeker Platform Management': 'GrantSeeker Platform Management',
    'Total Grants': 'Total Grants',
    'Open Grants': 'Open Grants',
    'Total Funding': 'Total Funding',
    'Average Rating': 'Average Rating',
    'Recent Activity': 'Recent Activity',
    'System Status': 'System Status',
    'New grant added': 'New grant added',
    'Data updated': 'Data updated',
    'New user registered': 'New user registered',
    'hours ago': 'hours ago',
    'Database': 'Database',
    'External API': 'External API',
    'Web server': 'Web server',
    'Automatic update': 'Automatic update',
    'Operational': 'Operational',
    'In progress': 'In progress',
    'Grant Management': 'Grant Management',
    'Add Grant': 'Add Grant',
    'Search grants...': 'Search grants...',
    'Grant': 'Grant',
    'Amount': 'Amount',
    'Deadline': 'Deadline',
    'Actions': 'Actions',
    'User Management': 'User Management',
    'Feature coming soon...': 'Feature coming soon...',
    'Analytics': 'Analytics',
    
    // Additional HomePage translations
    'Discover and manage grant opportunities for French nonprofits': 'Discover and manage grant opportunities for French nonprofits',
    'Prepare your documents in advance': 'Prepare your documents in advance',
    'Read all criteria carefully': 'Read all criteria carefully',
    'Contact the funder if you have questions': 'Contact the funder if you have questions',
    'Submit your application before the deadline': 'Submit your application before the deadline',
    'More than': 'More than',
    'associations already use GrantSeeker': 'organizations already use GrantSeeker',
    
    // Footer and additional translations
    'The reference platform for discovering and managing your grant applications': 'The reference platform for discovering and managing your grant applications',
    'We help French associations find the funding they need': 'We help French organizations find the funding they need',
    'Quick Links': 'Quick Links',
    'User Guide': 'User Guide',
    'FAQ': 'FAQ',
    'Support': 'Support',
    'Help Center': 'Help Center',
    'Contact Us': 'Contact Us',
    'Report an Issue': 'Report an Issue',
    'Community': 'Community',
    'All rights reserved': 'All rights reserved',
    'Privacy Policy': 'Privacy Policy',
    'Terms of Service': 'Terms of Service',
    'GDPR': 'GDPR',
  }
};

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState<Language>(() => {
    const stored = localStorage.getItem('language');
    return (stored === 'en' || stored === 'fr') ? stored : 'fr';
  });

  useEffect(() => {
    localStorage.setItem('language', currentLanguage);
  }, [currentLanguage]);

  const toggleLanguage = () => {
    setCurrentLanguage(prev => prev === 'fr' ? 'en' : 'fr');
  };

  const t = (key: string): string => {
    return translations[currentLanguage][key] || key;
  };

  const value = {
    currentLanguage,
    toggleLanguage,
    t
  };

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
};