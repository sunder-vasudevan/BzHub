import { NextRequest, NextResponse } from 'next/server';

export async function GET(
    _request: NextRequest,
    { params }: { params: { employeeId: string; payslipId: string } }
) {
    try {
        const backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000';
        const response = await fetch(
            `${backendUrl}/api/payroll/payslips/${params.employeeId}/${params.payslipId}`
        );
        if (!response.ok) {
            return NextResponse.json({ error: 'Payslip not found' }, { status: response.status });
        }
        return NextResponse.json(await response.json());
    } catch (error) {
        return NextResponse.json(
            { error: error instanceof Error ? error.message : 'Failed to retrieve payslip' },
            { status: 500 }
        );
    }
}
