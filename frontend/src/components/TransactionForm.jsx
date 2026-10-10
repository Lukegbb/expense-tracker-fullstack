import { useState } from 'react';

const today = () => new Date().toISOString().slice(0, 10);

export default function TransactionForm({ categories, onSubmit }) {
  const [form, setForm] = useState({ category: '', amount: '', date: today(), description: '' });
  const [error, setError] = useState('');

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await onSubmit({ ...form, category: Number(form.category) });
      setForm({ ...form, amount: '', description: '' });
      setError('');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form className="card form" onSubmit={handleSubmit}>
      <h3>Add transaction</h3>
      <select value={form.category} onChange={update('category')} required>
        <option value="">Select a category</option>
        {categories.map((cat) => (
          <option key={cat.id} value={cat.id}>
            {cat.name} ({cat.kind})
          </option>
        ))}
      </select>
      <input
        type="number"
        min="0.01"
        step="0.01"
        placeholder="Amount (€)"
        value={form.amount}
        onChange={update('amount')}
        required
      />
      <input type="date" value={form.date} onChange={update('date')} required />
      <input placeholder="Description" value={form.description} onChange={update('description')} />
      {error && <p className="error">{error}</p>}
      <button type="submit">Add</button>
    </form>
  );
}
