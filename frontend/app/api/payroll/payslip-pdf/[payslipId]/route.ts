import { NextRequest, NextResponse } from 'next/server';

export async function POST(
    _request: NextRequest,
    { params }: { params: { payslipId: string } }
) {
    try {
        const backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000';
        const response = await fetch(`${backendUrl}/api/payroll/payslip-pdf/${params.payslipId}`, {
            method: 'POST',
        });
        if (!response.ok) {
            return NextResponse.json({ error: 'Failed to generate PDF' }, { status: response.status });
        }
        return NextResponse.json(await response.json());
    } catch (error) {
        return NextResponse.json(
            { error: error instanceof Error ? error.message : 'Failed to generate PDF' },
            { status: 500 }
        );
    }
}
