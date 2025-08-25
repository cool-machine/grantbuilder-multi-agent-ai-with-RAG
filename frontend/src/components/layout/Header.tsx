import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, Menu, X, User, LogOut, Settings, Globe, Brain, FileText } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';

const Header: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const { user, logout } = useAuth();
  const { currentLanguage, toggleLanguage, t } = useLanguage();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
    setIsUserMenuOpen(false);
  };

  return (
    <header className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-custom-red rounded-lg flex items-center justify-center">
              <Search className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">GrantSeeker</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-6">
            <Link to="/grants" className="text-gray-700 hover:text-custom-blue px-3 py-2 text-sm font-medium transition-colors">
              {t('Grants')}
            </Link>
            <div className="relative group">
              <button className="flex items-center space-x-1 text-gray-700 hover:text-custom-blue px-3 py-2 text-sm font-medium transition-colors">
                <Brain className="w-4 h-4" />
                <span>AI Tools</span>
              </button>
              <div className="absolute left-0 mt-2 w-56 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <div className="py-1">
                  <Link
                    to="/fill-application"
                    className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <FileText className="w-4 h-4 mr-2" />
                    AI Form Filler
                  </Link>
                  <Link
                    to="/ai-analysis"
                    className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <Brain className="w-4 h-4 mr-2" />
                    Grant Analyzer
                  </Link>
                  <Link
                    to="/document-analysis"
                    className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <FileText className="w-4 h-4 mr-2" />
                    Document Processor
                  </Link>
                  <Link
                    to="/model-testing"
                    className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <Settings className="w-4 h-4 mr-2" />
                    Model Testing Lab
                  </Link>
                </div>
              </div>
            </div>
            {user && (
              <Link to="/dashboard" className="text-gray-700 hover:text-custom-red px-3 py-2 text-sm font-medium transition-colors">
                {t('Dashboard')}
              </Link>
            )}
            {user?.role === 'admin' && (
              <Link to="/admin" className="text-gray-700 hover:text-custom-red px-3 py-2 text-sm font-medium transition-colors">
                {t('Administration')}
              </Link>
            )}
          </nav>

          {/* User Menu / Auth Buttons */}
          <div className="flex items-center space-x-4">
            {/* Language Toggle */}
            <button
              onClick={toggleLanguage}
              className="flex items-center space-x-1 text-gray-700 hover:text-custom-red focus:outline-none focus:ring-2 focus:ring-custom-red focus:ring-offset-2 rounded-md p-2"
              title={currentLanguage === 'fr' ? 'Switch to English' : 'Passer en français'}
            >
              <Globe className="w-4 h-4" />
              <span className="text-sm font-medium">{currentLanguage.toUpperCase()}</span>
            </button>

            {user ? (
              <div className="relative">
                <button
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className="flex items-center space-x-2 text-gray-700 hover:text-custom-red focus:outline-none focus:ring-2 focus:ring-custom-red focus:ring-offset-2 rounded-md p-2"
                >
                  <User className="w-5 h-5" />
                  <span className="hidden md:block text-sm font-medium">{user.name}</span>
                </button>

                {isUserMenuOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                    <div className="py-1">
                      <div className="px-4 py-2 text-sm text-gray-500 border-b">
                        {user.email}
                      </div>
                      <Link
                        to="/dashboard"
                        className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        onClick={() => setIsUserMenuOpen(false)}
                      >
                        <User className="w-4 h-4 mr-2" />
                        {t('Dashboard')}
                      </Link>
                      <button
                        className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        onClick={() => setIsUserMenuOpen(false)}
                      >
                        <Settings className="w-4 h-4 mr-2" />
                        {t('Settings')}
                      </button>
                      <button
                        onClick={handleLogout}
                        className="flex items-center w-full px-4 py-2 text-sm text-custom-red hover:bg-red-50"
                      >
                        <LogOut className="w-4 h-4 mr-2" />
                        {t('Logout')}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link
                  to="/login"
                  className="text-gray-700 hover:text-custom-red px-3 py-2 text-sm font-medium transition-colors"
                >
                  {t('Login')}
                </Link>
                <Link
                  to="/register"
                  className="bg-custom-red text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-custom-red-dark transition-colors"
                >
                  {t('Register')}
                </Link>
              </div>
            )}

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 rounded-md text-gray-700 hover:text-custom-red focus:outline-none focus:ring-2 focus:ring-custom-red"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-gray-200">
            <div className="px-2 pt-2 pb-3 space-y-1">
              <Link
                to="/grants"
                className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-custom-red hover:bg-gray-50 rounded-md"
                onClick={() => setIsMenuOpen(false)}
              >
                {t('Grants')}
              </Link>
              <div className="px-3 py-2">
                <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">AI Tools</p>
                <div className="mt-2 space-y-1">
                  <Link
                    to="/fill-application"
                    className="block px-3 py-2 text-sm text-gray-700 hover:text-custom-red hover:bg-gray-50 rounded-md"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    AI Form Filler
                  </Link>
                  <Link
                    to="/ai-analysis"
                    className="block px-3 py-2 text-sm text-gray-700 hover:text-custom-red hover:bg-gray-50 rounded-md"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Grant Analyzer
                  </Link>
                  <Link
                    to="/document-analysis"
                    className="block px-3 py-2 text-sm text-gray-700 hover:text-custom-red hover:bg-gray-50 rounded-md"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Document Processor
                  </Link>
                  <Link
                    to="/model-testing"
                    className="block px-3 py-2 text-sm text-gray-700 hover:text-custom-red hover:bg-gray-50 rounded-md"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Model Testing Lab
                  </Link>
                </div>
              </div>
              {user && (
                <Link
                  to="/dashboard"
                  className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-custom-red hover:bg-gray-50 rounded-md"
                  onClick={() => setIsMenuOpen(false)}
                >
                  {t('Dashboard')}
                </Link>
              )}
              {user?.role === 'admin' && (
                <Link
                  to="/admin"
                  className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-custom-red hover:bg-gray-50 rounded-md"
                  onClick={() => setIsMenuOpen(false)}
                >
                  {t('Administration')}
                </Link>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;