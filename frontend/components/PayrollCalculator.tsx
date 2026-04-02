'use client';

import React, { useState, useEffect, useRef } from 'react';

interface DeductionsConfig {
    tax_rate: number;
    insurance: number;
    loan_emi: number;
    professional_tax: number;
}

interface PayrollResult {
    gross_salary: number;
    deductions: Record<string, number>;
    net_salary: number;
    period: string;
}

interface Payslip {
    id: string;
    employee_id: string;
    period: string;
    gross_salary: number;
    deductions: Record<string, number>;
    net_salary: number;
    created_at: string;
}

type Tab = 'calculator' | 'history';

export default function PayrollCalculator() {
    const [baseSalary, setBaseSalary] = useState<number>(50000);
    const [allowances, setAllowances] = useState<Record<string, number>>({
        dearness: 5000,
        house_rent: 10000,
    });
    const [config, setConfig] = useState<DeductionsConfig>({
        tax_rate: 0.10,
        insurance: 500,
        loan_emi: 0,
        professional_tax: 200,
    });
    const [result, setResult] = useState<PayrollResult | null>(null);
    const [history, setHistory] = useState<Payslip[]>([]);
    const [loading, setLoading] = useState(false);
    const [historyLoading, setHistoryLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<Tab>('calculator');
    const [employeeId, setEmployeeId] = useState<string>('');
    const debounceTimer = useRef<NodeJS.Timeout | null>(null);

    // Debounced calculation (300ms delay)
    useEffect(() => {
        if (debounceTimer.current) clearTimeout(debounceTimer.current);

        debounceTimer.current = setTimeout(() => {
            calculatePayroll();
        }, 300);

        return () => {
            if (debounceTimer.current) clearTimeout(debounceTimer.current);
        };
    }, [baseSalary, allowances, config]);

    // Load history when tab changes
    useEffect(() => {
        if (activeTab === 'history') {
            loadPayslipHistory();
        }
    }, [activeTab, employeeId]);

    const calculatePayroll = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch('/api/payroll/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    employee_id: employeeId,
                    base_salary: baseSalary,
                    allowances: allowances,
                    deductions_config: config,
                }),
            });

            if (!response.ok) throw new Error('Failed to calculate payroll');
            const data = await response.json();
            setResult(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Calculation failed');
        } finally {
            setLoading(false);
        }
    };

    const generatePayslip = async () => {
        if (!result) return;
        setLoading(true);
        try {
            const response = await fetch('/api/payroll/payslip', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    employee_id: employeeId,
                    base_salary: baseSalary,
                    allowances: allowances,
                    deductions_config: config,
                }),
            });

            if (!response.ok) throw new Error('Failed to generate payslip');
            const data = await response.json();
            alert(`Payslip generated successfully (ID: ${data.id})`);
            // Refresh history
            await loadPayslipHistory();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to generate payslip');
        } finally {
            setLoading(false);
        }
    };

    const loadPayslipHistory = async () => {
        setHistoryLoading(true);
        try {
            const response = await fetch(`/api/payroll/payslips/${employeeId}`);
            if (!response.ok) throw new Error('Failed to load history');
            const data = await response.json();
            setHistory(data.payslips || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load history');
        } finally {
            setHistoryLoading(false);
        }
    };

    const downloadPayslipPDF = async (payslipId: string) => {
        try {
            const response = await fetch(`/api/payroll/payslip-pdf/${payslipId}`, {
                method: 'POST',
            });
            if (!response.ok) throw new Error('Failed to generate payslip');
            const data = await response.json();

            // Open as HTML in new tab — user can print/save as PDF from browser
            const html = atob(data.html_base64);
            const blob = new Blob([html], { type: 'text/html' });
            const url = window.URL.createObjectURL(blob);
            window.open(url, '_blank');
            setTimeout(() => window.URL.revokeObjectURL(url), 10000);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to generate payslip');
        }
    };

    const handleAllowanceChange = (key: string, value: number) => {
        setAllowances(prev => ({ ...prev, [key]: value }));
    };

    const handleConfigChange = (key: string, value: number) => {
        setConfig(prev => ({ ...prev, [key]: value }));
    };

    const addAllowance = (name: string) => {
        const newKey = name.toLowerCase().replace(/\s+/g, '_');
        setAllowances(prev => ({ ...prev, [newKey]: 0 }));
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
            <div className="max-w-6xl mx-auto">
                <h1 className="text-4xl font-bold text-gray-800 mb-1">Payroll System</h1>
                <p className="text-gray-600 mb-8">Calculate, generate, and manage employee payslips</p>

                {/* Tab Navigation */}
                <div className="flex gap-4 mb-6">
                    <button
                        onClick={() => setActiveTab('calculator')}
                        className={`px-6 py-3 font-semibold rounded-lg transition ${activeTab === 'calculator'
                                ? 'bg-blue-600 text-white'
                                : 'bg-white text-gray-700 hover:bg-gray-50'
                            }`}
                    >
                        Calculator
                    </button>
                    <button
                        onClick={() => setActiveTab('history')}
                        className={`px-6 py-3 font-semibold rounded-lg transition ${activeTab === 'history'
                                ? 'bg-blue-600 text-white'
                                : 'bg-white text-gray-700 hover:bg-gray-50'
                            }`}
                    >
                        Payslip History
                    </button>
                </div>

                {/* Employee ID Input */}
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <label className="block text-sm font-medium text-gray-600 mb-2">Employee ID <span className="text-gray-400 font-normal">(numeric)</span></label>
                    <input
                        type="number"
                        value={employeeId}
                        onChange={(e) => setEmployeeId(e.target.value)}
                        placeholder="e.g. 1"
                        className="w-full max-w-sm px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                </div>

                {activeTab === 'calculator' ? (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Input Section */}
                        <div className="lg:col-span-2 space-y-6">
                            {/* Base Salary */}
                            <div className="bg-white rounded-lg shadow p-6">
                                <h2 className="text-xl font-semibold text-gray-700 mb-4">Base Salary & Allowances</h2>
                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-600 mb-2">Base Salary</label>
                                        <input
                                            type="number"
                                            value={baseSalary}
                                            onChange={(e) => setBaseSalary(Number(e.target.value))}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        />
                                        <p className="text-xs text-gray-500 mt-1">₹{baseSalary.toLocaleString()}</p>
                                    </div>

                                    <div className="border-t pt-4">
                                        <h3 className="text-sm font-semibold text-gray-700 mb-3">Allowances</h3>
                                        <div className="space-y-3">
                                            {Object.entries(allowances).map(([key, value]) => (
                                                <div key={key}>
                                                    <label className="block text-sm text-gray-600 mb-1">
                                                        {key.replace(/_/g, ' ').toUpperCase()}
                                                    </label>
                                                    <input
                                                        type="number"
                                                        value={value}
                                                        onChange={(e) => handleAllowanceChange(key, Number(e.target.value))}
                                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
                                                    />
                                                </div>
                                            ))}
                                        </div>
                                        <button
                                            onClick={() => addAllowance('other')}
                                            className="mt-3 text-sm text-blue-600 hover:text-blue-700 font-medium"
                                        >
                                            + Add Allowance
                                        </button>
                                    </div>
                                </div>
                            </div>

                            {/* Deductions Configuration */}
                            <div className="bg-white rounded-lg shadow p-6">
                                <h2 className="text-xl font-semibold text-gray-700 mb-4">Deduction Configuration</h2>
                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-600 mb-2">
                                            Tax Rate (%)
                                        </label>
                                        <input
                                            type="number"
                                            step="0.01"
                                            value={config.tax_rate * 100}
                                            onChange={(e) => handleConfigChange('tax_rate', Number(e.target.value) / 100)}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-600 mb-2">Insurance</label>
                                        <input
                                            type="number"
                                            value={config.insurance}
                                            onChange={(e) => handleConfigChange('insurance', Number(e.target.value))}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-600 mb-2">Loan EMI</label>
                                        <input
                                            type="number"
                                            value={config.loan_emi}
                                            onChange={(e) => handleConfigChange('loan_emi', Number(e.target.value))}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-600 mb-2">
                                            Professional Tax
                                        </label>
                                        <input
                                            type="number"
                                            value={config.professional_tax}
                                            onChange={(e) => handleConfigChange('professional_tax', Number(e.target.value))}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Results Section */}
                        <div className="lg:col-span-1">
                            {error && (
                                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                                    <p className="text-sm text-red-700">{error}</p>
                                </div>
                            )}

                            {loading ? (
                                <div className="bg-white rounded-lg shadow p-6 flex items-center justify-center h-64">
                                    <p className="text-gray-500">Calculating...</p>
                                </div>
                            ) : result ? (
                                <div className="space-y-4">
                                    {/* Gross Salary Card */}
                                    <div className="bg-white rounded-lg shadow p-6">
                                        <h3 className="text-sm font-semibold text-gray-600 mb-2">GROSS SALARY</h3>
                                        <p className="text-3xl font-bold text-blue-600">
                                            ₹{result.gross_salary.toLocaleString()}
                                        </p>
                                    </div>

                                    {/* Deductions Card */}
                                    <div className="bg-white rounded-lg shadow p-6">
                                        <h3 className="text-sm font-semibold text-gray-600 mb-4">DEDUCTIONS</h3>
                                        <div className="space-y-2">
                                            {Object.entries(result.deductions).map(([key, value]) => (
                                                <div key={key} className="flex justify-between text-sm">
                                                    <span className="text-gray-600">{key.replace(/_/g, ' ')}</span>
                                                    <span className="font-medium text-gray-800">
                                                        -₹{value.toLocaleString()}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                        <div className="border-t mt-4 pt-4 flex justify-between">
                                            <span className="font-semibold text-gray-700">Total Deductions</span>
                                            <span className="font-bold text-red-600">
                                                -₹{Object.values(result.deductions).reduce((a, b) => a + b, 0).toLocaleString()}
                                            </span>
                                        </div>
                                    </div>

                                    {/* Net Salary Card */}
                                    <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-lg p-6">
                                        <h3 className="text-sm font-semibold text-green-700 mb-2">NET SALARY</h3>
                                        <p className="text-3xl font-bold text-green-600">
                                            ₹{result.net_salary.toLocaleString()}
                                        </p>
                                        <p className="text-xs text-green-600 mt-2">{result.period}</p>
                                    </div>

                                    {/* Summary */}
                                    <div className="bg-gray-50 rounded-lg p-4">
                                        <p className="text-xs text-gray-600">
                                            <span className="font-semibold">Deduction %:</span>{' '}
                                            {(
                                                ((result.gross_salary - result.net_salary) / result.gross_salary) *
                                                100
                                            ).toFixed(2)}
                                            %
                                        </p>
                                    </div>

                                    {/* Generate Payslip Button */}
                                    <button
                                        onClick={generatePayslip}
                                        disabled={loading}
                                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50"
                                    >
                                        {loading ? 'Generating...' : '📄 Generate Payslip'}
                                    </button>
                                </div>
                            ) : null}
                        </div>
                    </div>
                ) : (
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Payslip History</h2>

                        {historyLoading ? (
                            <p className="text-gray-500">Loading payslips...</p>
                        ) : history.length > 0 ? (
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                    <thead className="bg-gray-100">
                                        <tr>
                                            <th className="px-4 py-3 text-left font-semibold text-gray-700">Period</th>
                                            <th className="px-4 py-3 text-right font-semibold text-gray-700">Gross</th>
                                            <th className="px-4 py-3 text-right font-semibold text-gray-700">Deductions</th>
                                            <th className="px-4 py-3 text-right font-semibold text-gray-700">Net</th>
                                            <th className="px-4 py-3 text-center font-semibold text-gray-700">Action</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {history.map((slip) => (
                                            <tr key={slip.id} className="border-t hover:bg-gray-50">
                                                <td className="px-4 py-3">{slip.period}</td>
                                                <td className="px-4 py-3 text-right">₹{slip.gross_salary.toLocaleString()}</td>
                                                <td className="px-4 py-3 text-right">
                                                    ₹{Object.values(slip.deductions || {}).reduce((a, b) => a + b, 0).toLocaleString()}
                                                </td>
                                                <td className="px-4 py-3 text-right font-semibold text-green-600">
                                                    ₹{slip.net_salary.toLocaleString()}
                                                </td>
                                                <td className="px-4 py-3 text-center">
                                                    <button
                                                        onClick={() => downloadPayslipPDF(slip.id)}
                                                        className="text-blue-600 hover:text-blue-700 font-medium"
                                                    >
                                                        📥 Download
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        ) : (
                            <p className="text-gray-500">No payslips found for this employee.</p>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
