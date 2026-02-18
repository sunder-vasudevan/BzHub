'use client';
import { useEffect, useState } from 'react';

export default function InventoryPage() {
  const [data, setData] = useState<{ items: any[]; total_value: number } | null>(null);

  useEffect(() => {
    fetch('https://bzhub.onrender.com/inventory')
      .then(res => res.json())
      .then(setData);
  }, []);

  if (!data) return <div>Loading...</div>;

  return (
    <div>
      <h1>Inventory</h1>
      <p>Total Inventory Value: ${data.total_value}</p>
      <ul>
        {data.items.map(item => (
          <li key={item.id}>
            {item.name} — Qty: {item.quantity} — Unit Price: ${item.unit_price}
          </li>
        ))}
      </ul>
    </div>
  );
}
