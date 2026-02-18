'use client';
import { useEffect, useState } from 'react';

export default function VisitorsPage() {
  const [data, setData] = useState<{ visitors: any[]; total_visitors: number } | null>(null);

  useEffect(() => {
    fetch('https://bzhub.onrender.com/visitors')
      .then(res => res.json())
      .then(setData);
  }, []);

  if (!data) return <div>Loading...</div>;

  return (
    <div>
      <h1>Visitors</h1>
      <p>Total Visitors: {data.total_visitors}</p>
      <ul>
        {data.visitors.map(visitor => (
          <li key={visitor.id}>
            {visitor.name} — Purpose: {visitor.purpose}
          </li>
        ))}
      </ul>
    </div>
  );
}
