import { useState } from 'react';
import { api } from '../api.js';

export default function AuthForm({ onLoggedIn }) {
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      if (mode === 'register') await api.register(form);
      await api.login(form.username, form.password);
      onLoggedIn();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="card auth" onSubmit={handleSubmit}>
      <h2>{mode === 'login' ? 'Log in' : 'Create account'}</h2>
      <input placeholder="Username" value={form.username} onChange={update('username')} required />
      {mode === 'register' && (
        <input type="email" placeholder="Email" value={form.email} onChange={update('email')} />
      )}
      <input
        type="password"
        placeholder="Password"
        value={form.password}
        onChange={update('password')}
        required
      />
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? 'Please wait...' : mode === 'login' ? 'Log in' : 'Sign up'}
      </button>
      <button
        type="button"
        className="link"
        onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
      >
        {mode === 'login' ? "Don't have an account? Sign up" : 'Already have an account? Log in'}
      </button>
    </form>
  );
}
