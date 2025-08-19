import React from 'react';
import { Mail, Phone, MapPin, Globe } from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';

const Footer: React.FC = () => {
  const { t } = useLanguage();
  
  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="col-span-1 md:col-span-2">
            <h3 className="text-xl font-bold mb-4">GrantSeeker</h3>
            <p className="text-gray-300 mb-6 max-w-md">
              {t('The reference platform for discovering and managing your grant applications')}. 
              {t('We help French associations find the funding they need')}.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-300 hover:text-white transition-colors">
                <Globe className="w-5 h-5" />
              </a>
              <a href="mailto:contact@grantseeker.fr" className="text-gray-300 hover:text-white transition-colors">
                <Mail className="w-5 h-5" />
              </a>
              <a href="tel:+33123456789" className="text-gray-300 hover:text-white transition-colors">
                <Phone className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-semibold mb-4">{t('Quick Links')}</h4>
            <ul className="space-y-2">
              <li><a href="/grants" className="text-gray-300 hover:text-white transition-colors">{t('Grants')}</a></li>
              <li><a href="/dashboard" className="text-gray-300 hover:text-white transition-colors">{t('Dashboard')}</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors">{t('User Guide')}</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors">{t('FAQ')}</a></li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h4 className="text-lg font-semibold mb-4">{t('Support')}</h4>
            <ul className="space-y-2">
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors">{t('Help Center')}</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors">{t('Contact Us')}</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors">{t('Report an Issue')}</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors">{t('Community')}</a></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-300 text-sm">
            © 2024 GrantSeeker. {t('All rights reserved')}.
          </p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a href="#" className="text-gray-300 hover:text-white text-sm transition-colors">
              {t('Privacy Policy')}
            </a>
            <a href="#" className="text-gray-300 hover:text-white text-sm transition-colors">
              {t('Terms of Service')}
            </a>
            <a href="#" className="text-gray-300 hover:text-white text-sm transition-colors">
              {t('GDPR')}
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;