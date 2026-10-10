import { formatMoney } from './SummaryCards.jsx';

export default function TransactionList({ transactions, onDelete }) {
  return (
    <div className="card list">
      <h3>Transactions</h3>
      {transactions.length === 0 ? (
        <p className="empty">No transactions for this period.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Category</th>
              <th>Description</th>
              <th className="right">Amount</th>
              <th aria-label="Actions" />
            </tr>
          </thead>
          <tbody>
            {transactions.map((tx) => (
              <tr key={tx.id}>
                <td>{tx.date}</td>
                <td>{tx.category_name}</td>
                <td>{tx.description}</td>
                <td className={`right ${tx.kind}`}>
                  {tx.kind === 'expense' ? '-' : '+'}
                  {formatMoney(tx.amount)}
                </td>
                <td>
                  <button type="button" className="danger small" onClick={() => onDelete(tx.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
