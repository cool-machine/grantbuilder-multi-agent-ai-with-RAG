import React from 'react';
import { Link } from 'react-router-dom';
import { Search, Target, Users, Award, TrendingUp, Shield, Clock } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';

const HomePage: React.FC = () => {
  const { user } = useAuth();
  const { t } = useLanguage();

  return (
    <div>
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-custom-blue via-custom-blue to-black text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              {t('Find perfect funding for your')}{' '}
              <span className="text-custom-red">{t('association')}</span>
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-blue-200 max-w-3xl mx-auto">
              {t('The French platform that connects associations with the best grant opportunities')}. {' '}
              {t('More than 10,000 grants referenced and updated daily')}.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/grants"
                className="bg-custom-red text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-custom-red-dark transition-colors inline-flex items-center justify-center"
              >
                <Search className="w-5 h-5 mr-2" />
                {t('Explore grants')}
              </Link>
              {!user && (
                <Link
                  to="/register"
                  className="bg-transparent border-2 border-white text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-white hover:text-custom-blue transition-colors inline-flex items-center justify-center"
                >
                  {t('Create free account')}
                </Link>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              {t('Why choose GrantSeeker?')}
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              {t('More than')} 5,000 {t('associations already use GrantSeeker')}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="text-center p-6 rounded-lg hover:shadow-lg transition-shadow">
              <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <Target className="w-8 h-8 text-custom-blue" />
              </div>
              <h3 className="text-xl font-semibold mb-3">{t('Smart Matching')}</h3>
              <p className="text-gray-600">
                {t('Our algorithm analyzes your profile and recommends the most suitable grants')}.
              </p>
            </div>

            <div className="text-center p-6 rounded-lg hover:shadow-lg transition-shadow">
              <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <Clock className="w-8 h-8 text-custom-red" />
              </div>
              <h3 className="text-xl font-semibold mb-3">{t('Real-time Alerts')}</h3>
              <p className="text-gray-600">
                {t('Receive notifications for new grants and important deadlines')}.
              </p>
            </div>

            <div className="text-center p-6 rounded-lg hover:shadow-lg transition-shadow">
              <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-custom-blue" />
              </div>
              <h3 className="text-xl font-semibold mb-3">{t('Verified Data')}</h3>
              <p className="text-gray-600">
                {t('All our data is verified daily to ensure accuracy and timeliness')}.
              </p>
            </div>

            <div className="text-center p-6 rounded-lg hover:shadow-lg transition-shadow">
              <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-custom-red" />
              </div>
              <h3 className="text-xl font-semibold mb-3">{t('Active Community')}</h3>
              <p className="text-gray-600">
                {t('Exchange with other associations, share experiences and learn from others\' successes')}.
              </p>
            </div>

            <div className="text-center p-6 rounded-lg hover:shadow-lg transition-shadow">
              <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <Award className="w-8 h-8 text-custom-blue" />
              </div>
              <h3 className="text-xl font-semibold mb-3">{t('Application Tracking')}</h3>
              <p className="text-gray-600">
                {t('Manage all your applications from a central dashboard with automatic reminders')}.
              </p>
            </div>

            <div className="text-center p-6 rounded-lg hover:shadow-lg transition-shadow">
              <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-8 h-8 text-custom-red" />
              </div>
              <h3 className="text-xl font-semibold mb-3">{t('Advanced Analytics')}</h3>
              <p className="text-gray-600">
                {t('Analyze your success rates and optimize future applications with detailed reports')}.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-custom-blue mb-2">10,000+</div>
              <div className="text-gray-600">{t('Referenced grants')}</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-custom-red mb-2">5,000+</div>
              <div className="text-gray-600">{t('User associations')}</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-custom-red mb-2">€50M+</div>
              <div className="text-gray-600">{t('Funding obtained')}</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-custom-blue mb-2">85%</div>
              <div className="text-gray-600">{t('Satisfaction rate')}</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-custom-blue">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-white">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            {t('Ready to transform your funding search?')}
          </h2>
          <p className="text-xl mb-8 text-blue-200 max-w-3xl mx-auto">
            {t('The French platform that connects associations with the best grant opportunities')}. {t('More than 10,000 grants referenced and updated daily')}.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="bg-custom-red text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-custom-red-dark transition-colors inline-flex items-center justify-center"
            >
              {t('Start for free')}
            </Link>
            <Link
              to="/grants"
              className="bg-transparent border-2 border-white text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-white hover:text-custom-blue transition-colors inline-flex items-center justify-center"
            >
              {t('View grants')}
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;