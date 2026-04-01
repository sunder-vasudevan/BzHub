import PayrollCalculator from '@/components/PayrollCalculator';
import { Metadata } from 'next';

export const metadata: Metadata = {
    title: 'Payroll Calculator | BzHub',
    description: 'Calculate payroll with real-time gross, deductions, and net salary computation.',
};

export default function PayrollPage() {
    return (
        <main className="min-h-screen bg-gray-50">
            <PayrollCalculator />
        </main>
    );
}
