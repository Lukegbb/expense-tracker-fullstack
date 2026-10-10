import { useState } from 'react';
import { isLoggedIn, logout } from './api.js';
import AuthForm from './components/AuthForm.jsx';
import Dashboard from './components/Dashboard.jsx';

export default function App() {
  const [loggedIn, setLoggedIn] = useState(isLoggedIn());

  const handleLogout = () => {
    logout();
    setLoggedIn(false);
  };

  return (
    <div className="container">
      <header className="header">
        <h1>Expense Tracker</h1>
        {loggedIn && (
          <button type="button" className="secondary" onClick={handleLogout}>
            Log out
          </button>
        )}
      </header>
      {loggedIn ? <Dashboard /> : <AuthForm onLoggedIn={() => setLoggedIn(true)} />}
    </div>
  );
}
