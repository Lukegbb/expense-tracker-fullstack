import { useCallback, useEffect, useState } from 'react';
import { api } from '../api.js';
import SummaryCards from './SummaryCards.jsx';
import Charts from './Charts.jsx';
import TransactionForm from './TransactionForm.jsx';
import TransactionList from './TransactionList.jsx';

const currentMonth = () => new Date().toISOString().slice(0, 7);

function monthRange(month) {
  const [year, m] = month.split('-').map(Number);
  const lastDay = new Date(year, m, 0).getDate();
  return { date_from: `${month}-01`, date_to: `${month}-${String(lastDay).padStart(2, '0')}` };
}

export default function Dashboard() {
  const [month, setMonth] = useState(currentMonth());
  const [kind, setKind] = useState('');
  const [categories, setCategories] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [trend, setTrend] = useState([]);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      const [cats, txs, sum, monthly] = await Promise.all([
        api.categories(),
        api.transactions({ ...monthRange(month), kind }),
        api.summary(month),
        api.monthly(6),
      ]);
      setCategories(cats);
      setTransactions(txs.results);
      setSummary(sum);
      setTrend(monthly);
      setError('');
    } catch (err) {
      setError(err.message);
    }
  }, [month, kind]);

  useEffect(() => {
    load();
  }, [load]);

  const handleCreate = async (payload) => {
    await api.createTransaction(payload);
    await load();
  };

  const handleDelete = async (id) => {
    await api.deleteTransaction(id);
    await load();
  };

  return (
    <main>
      <div className="toolbar">
        <label>
          Month
          <input type="month" value={month} onChange={(e) => setMonth(e.target.value)} />
        </label>
        <label>
          Show
          <select value={kind} onChange={(e) => setKind(e.target.value)}>
            <option value="">All</option>
            <option value="income">Income</option>
            <option value="expense">Expenses</option>
          </select>
        </label>
      </div>

      {error && <p className="error">{error}</p>}

      {summary && <SummaryCards summary={summary} />}
      <Charts byCategory={summary?.by_category || []} trend={trend} />

      <div className="grid">
        <TransactionForm categories={categories} onSubmit={handleCreate} />
        <TransactionList transactions={transactions} onDelete={handleDelete} />
      </div>
    </main>
  );
}
