import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        // Call backend payroll service
        const backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000';

        const response = await fetch(`${backendUrl}/api/payroll/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            return NextResponse.json(
                { error: 'Backend calculation failed' },
                { status: response.status }
            );
        }

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        return NextResponse.json(
            { error: error instanceof Error ? error.message : 'Calculation failed' },
            { status: 500 }
        );
    }
}
