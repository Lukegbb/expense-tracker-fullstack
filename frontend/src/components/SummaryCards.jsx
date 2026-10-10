const euro = new Intl.NumberFormat('en-IE', { style: 'currency', currency: 'EUR' });

export const formatMoney = (value) => euro.format(Number(value || 0));

export default function SummaryCards({ summary }) {
  const balance = Number(summary.balance);
  return (
    <section className="cards">
      <div className="card stat">
        <span>Income</span>
        <strong className="income">{formatMoney(summary.income)}</strong>
      </div>
      <div className="card stat">
        <span>Expenses</span>
        <strong className="expense">{formatMoney(summary.expenses)}</strong>
      </div>
      <div className="card stat">
        <span>Balance</span>
        <strong className={balance >= 0 ? 'income' : 'expense'}>{formatMoney(balance)}</strong>
      </div>
    </section>
  );
}
