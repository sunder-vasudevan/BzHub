'use client';
import { useEffect, useState } from 'react';

export default function HRPage() {
  const [data, setData] = useState<{ employees: any[]; total_employees: number } | null>(null);

  useEffect(() => {
    fetch('https://bzhub.onrender.com/hr/employees')
      .then(res => res.json())
      .then(setData);
  }, []);

  if (!data) return <div>Loading...</div>;

  return (
    <div>
      <h1>Employees</h1>
      <p>Total Employees: {data.total_employees}</p>
      <ul>
        {data.employees.map(emp => (
          <li key={emp.id}>
            {emp.name} — Role: {emp.role}
          </li>
        ))}
      </ul>
    </div>
  );
}
