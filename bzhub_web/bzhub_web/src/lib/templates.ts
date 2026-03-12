export type TemplateId = 'general' | 'retail' | 'clinic' | 'restaurant' | 'distributor'

export interface IndustryTemplate {
  id: TemplateId
  name: string
  description: string
  color: string
  defaultHiddenKPIs: string[]
  highlights: string[]
}

export const TEMPLATES: IndustryTemplate[] = [
  {
    id: 'general',
    name: 'General Business',
    description: 'A balanced setup for any SMB. All modules enabled with standard KPIs.',
    color: '#6D28D9',
    defaultHiddenKPIs: [],
    highlights: ['All modules active', 'Standard KPIs', 'Full CRM pipeline', 'HR & Payroll'],
  },
  {
    id: 'retail',
    name: 'Retail Store',
    description: 'Optimised for retail and e-commerce with inventory and sales focus.',
    color: '#0891B2',
    defaultHiddenKPIs: ['pipeline_value'],
    highlights: ['Inventory & POS focus', 'Sales reports', 'Supplier management', 'Low-stock alerts'],
  },
  {
    id: 'clinic',
    name: 'Medical Clinic',
    description: 'Built for small clinics managing staff, leave, and operations.',
    color: '#059669',
    defaultHiddenKPIs: ['pipeline_value', 'low_stock'],
    highlights: ['Staff & HR focus', 'Leave management', 'Employee self-service', 'Appraisals'],
  },
  {
    id: 'restaurant',
    name: 'Restaurant / F&B',
    description: 'Designed for food service with daily revenue and POS operations.',
    color: '#DC2626',
    defaultHiddenKPIs: ['pipeline_value'],
    highlights: ['Daily revenue KPIs', 'POS transactions', 'Inventory & suppliers', 'Staff scheduling'],
  },
  {
    id: 'distributor',
    name: 'Wholesale Distributor',
    description: 'For distributors managing customer pipelines and bulk orders.',
    color: '#D97706',
    defaultHiddenKPIs: [],
    highlights: ['CRM pipeline primary', 'Purchase orders', 'Supplier network', 'Sales analytics'],
  },
]

export function getActiveTemplate(): IndustryTemplate {
  if (typeof window === 'undefined') return TEMPLATES[0]
  const stored = localStorage.getItem('bzhub_template') as TemplateId | null
  return TEMPLATES.find(t => t.id === stored) ?? TEMPLATES[0]
}

export function applyTemplate(template: IndustryTemplate): void {
  localStorage.setItem('bzhub_template', template.id)
  // Build new dashboard prefs from template defaults
  const visibleKPIs = {
    today_sales: true,
    inventory_value: true,
    low_stock: true,
    avg_daily_sales: true,
    pipeline_value: true,
    growth: true,
  }
  for (const key of template.defaultHiddenKPIs) {
    if (key in visibleKPIs) {
      (visibleKPIs as Record<string, boolean>)[key] = false
    }
  }
  localStorage.setItem('bzhub_dashboard_prefs', JSON.stringify({ visibleKPIs, trendDays: 30 }))
}
