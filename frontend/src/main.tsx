import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

// Handle browser extension errors that don't affect our app
window.addEventListener('error', (event) => {
  if (event.message?.includes('message channel closed') || 
      event.message?.includes('listener indicated an asynchronous response')) {
    event.preventDefault();
    return true;
  }
}, true);

window.addEventListener('unhandledrejection', (event) => {
  if (event.reason?.message?.includes('message channel closed') ||
      event.reason?.message?.includes('listener indicated an asynchronous response')) {
    event.preventDefault();
  }
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
