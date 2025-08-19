import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
  organization: string;
  role: 'admin' | 'editor' | 'member' | 'guest';
  preferences: {
    language: 'fr' | 'en';
    notifications: boolean;
  };
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (userData: RegisterData) => Promise<void>;
  loading: boolean;
}

interface RegisterData {
  email: string;
  password: string;
  name: string;
  organization: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for stored user session
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Check if admin login
      const isAdmin = email.toLowerCase().includes('admin') || 
                     email.toLowerCase() === 'admin@example.com' ||
                     email.toLowerCase() === 'admin@grantseeker.fr' ||
                     email.toLowerCase() === 'admin@admin.com' ||
                     email.toLowerCase() === 'test@admin.com';
      
      // Mock user data
      const userData: User = {
        id: '1',
        email,
        name: isAdmin ? 'Administrator' : 'Marie Dubois',
        organization: isAdmin ? 'GrantSeeker Admin' : 'Association Environnement France',
        role: isAdmin ? 'admin' : 'member',
        preferences: {
          language: 'fr',
          notifications: true
        }
      };
      
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
    } catch (error) {
      throw new Error('Échec de la connexion');
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData: RegisterData) => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const newUser: User = {
        id: Date.now().toString(),
        email: userData.email,
        name: userData.name,
        organization: userData.organization,
        role: 'member',
        preferences: {
          language: 'fr',
          notifications: true
        }
      };
      
      setUser(newUser);
      localStorage.setItem('user', JSON.stringify(newUser));
    } catch (error) {
      throw new Error('Échec de l\'inscription');
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  const value = {
    user,
    login,
    logout,
    register,
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};