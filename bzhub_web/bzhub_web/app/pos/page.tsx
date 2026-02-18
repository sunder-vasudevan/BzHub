'use client';
import { useEffect, useState } from 'react';

export default function POSPage() {
  const [data, setData] = useState<{ transactions: any[]; total_sales: number } | null>(null);

  useEffect(() => {
    fetch('https://bzhub.onrender.com/pos/transactions')
      .then(res => res.json())
      .then(setData);
  }, []);

  if (!data) return <div>Loading...</div>;

  return (
    <div>
      <h1>POS Transactions</h1>
      <p>Total Sales: ${data.total_sales}</p>
      <ul>
        {data.transactions.map(txn => (
          <li key={txn.id}>
            {txn.item} — Amount: ${txn.amount}
          </li>
        ))}
      </ul>
    </div>
  );
}
