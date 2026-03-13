/**
 * customFields.ts — Custom field definitions for extensible entities.
 * Field schemas are stored in localStorage (per-org config, no DB required).
 * Field values are stored in Supabase `custom_data` table via db.ts.
 */

export type FieldType = 'text' | 'number' | 'date' | 'boolean' | 'dropdown' | 'email' | 'phone' | 'url'

export type EntityType = 'employee' | 'contact' | 'lead' | 'product'

export interface CustomField {
  id: string          // snake_case key, e.g. 'blood_type'
  label: string       // display name, e.g. 'Blood Type'
  type: FieldType
  required: boolean
  options?: string[]  // only for 'dropdown' type
}

export interface CustomFieldSchema {
  employee: CustomField[]
  contact: CustomField[]
  lead: CustomField[]
  product: CustomField[]
}

const STORAGE_KEY = 'bzhub_custom_fields'
const EMPTY: CustomFieldSchema = { employee: [], contact: [], lead: [], product: [] }

export function loadCustomFields(): CustomFieldSchema {
  if (typeof window === 'undefined') return EMPTY
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? { ...EMPTY, ...JSON.parse(raw) } : EMPTY
  } catch {
    return EMPTY
  }
}

export function saveCustomFields(schema: CustomFieldSchema) {
  if (typeof window === 'undefined') return
  localStorage.setItem(STORAGE_KEY, JSON.stringify(schema))
}

export function getEntityFields(entity: EntityType): CustomField[] {
  return loadCustomFields()[entity] ?? []
}

export const ENTITY_LABELS: Record<EntityType, string> = {
  employee: 'Employee',
  contact: 'Contact',
  lead: 'Lead',
  product: 'Product',
}

export const FIELD_TYPE_LABELS: Record<FieldType, string> = {
  text: 'Text',
  number: 'Number',
  date: 'Date',
  boolean: 'Yes / No',
  dropdown: 'Dropdown',
  email: 'Email',
  phone: 'Phone',
  url: 'URL',
}

/** Convert a human label to a safe snake_case id */
export function labelToId(label: string): string {
  return label
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_|_$/g, '')
    .slice(0, 40)
}
