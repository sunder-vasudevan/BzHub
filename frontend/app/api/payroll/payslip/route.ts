import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000';
        const response = await fetch(`${backendUrl}/api/payroll/payslip`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (!response.ok) {
            return NextResponse.json({ error: 'Failed to generate payslip' }, { status: response.status });
        }
        return NextResponse.json(await response.json());
    } catch (error) {
        return NextResponse.json(
            { error: error instanceof Error ? error.message : 'Failed to generate payslip' },
            { status: 500 }
        );
    }
}
