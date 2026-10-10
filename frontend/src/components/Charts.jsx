import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { formatMoney } from './SummaryCards.jsx';

export default function Charts({ byCategory, trend }) {
  const pieData = byCategory.map((row) => ({ ...row, total: Number(row.total) }));
  const barData = trend.map((row) => ({
    month: row.month,
    income: Number(row.income),
    expenses: Number(row.expenses),
  }));

  return (
    <section className="charts">
      <div className="card">
        <h3>Spending by category</h3>
        {pieData.length === 0 ? (
          <p className="empty">No expenses this month.</p>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={pieData} dataKey="total" nameKey="category" outerRadius={90} label>
                {pieData.map((row) => (
                  <Cell key={row.category} fill={row.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => formatMoney(value)} />
            </PieChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="card">
        <h3>Last 6 months</h3>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={barData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip formatter={(value) => formatMoney(value)} />
            <Legend />
            <Bar dataKey="income" name="Income" fill="#16a34a" />
            <Bar dataKey="expenses" name="Expenses" fill="#dc2626" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
