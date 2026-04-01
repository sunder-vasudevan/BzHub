'use client';

import React, { useState, useEffect } from 'react';

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
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        calculatePayroll();
    }, [baseSalary, allowances, config]);

    const calculatePayroll = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch('/api/payroll/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    employee_id: 'USER_001',
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
                <h1 className="text-4xl font-bold text-gray-800 mb-1">Payroll Calculator</h1>
                <p className="text-gray-600 mb-8">Calculate gross, deductions, and net salary in real-time</p>

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
                            </div>
                        ) : null}
                    </div>
                </div>
            </div>
        </div>
    );
}
