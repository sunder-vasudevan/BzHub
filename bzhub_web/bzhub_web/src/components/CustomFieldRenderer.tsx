"use client"

/**
 * CustomFieldRenderer — renders form inputs for custom fields defined by a schema.
 * Used in Employee, Contact, Lead, and Product forms.
 */
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import type { CustomField } from "@/lib/customFields"

interface Props {
  fields: CustomField[]
  values: Record<string, unknown>
  onChange: (id: string, value: unknown) => void
  disabled?: boolean
}

export default function CustomFieldRenderer({ fields, values, onChange, disabled }: Props) {
  if (fields.length === 0) return null

  return (
    <div className="space-y-3">
      {fields.map((field) => {
        const value = values[field.id] ?? ""

        if (field.type === 'boolean') {
          return (
            <div key={field.id} className="flex items-center gap-3">
              <input
                type="checkbox"
                id={`cf_${field.id}`}
                checked={!!value}
                onChange={(e) => onChange(field.id, e.target.checked)}
                disabled={disabled}
                className="h-4 w-4 rounded border-input"
              />
              <Label htmlFor={`cf_${field.id}`} className="cursor-pointer">
                {field.label}
                {field.required && <span className="text-destructive ml-1">*</span>}
              </Label>
            </div>
          )
        }

        if (field.type === 'dropdown' && field.options?.length) {
          return (
            <div key={field.id} className="space-y-1.5">
              <Label htmlFor={`cf_${field.id}`}>
                {field.label}
                {field.required && <span className="text-destructive ml-1">*</span>}
              </Label>
              <select
                id={`cf_${field.id}`}
                value={String(value)}
                onChange={(e) => onChange(field.id, e.target.value)}
                disabled={disabled}
                required={field.required}
                className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              >
                <option value="">— Select —</option>
                {field.options.map((opt) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            </div>
          )
        }

        const inputType =
          field.type === 'number' ? 'number' :
          field.type === 'date' ? 'date' :
          field.type === 'email' ? 'email' :
          field.type === 'url' ? 'url' :
          'text'

        return (
          <div key={field.id} className="space-y-1.5">
            <Label htmlFor={`cf_${field.id}`}>
              {field.label}
              {field.required && <span className="text-destructive ml-1">*</span>}
            </Label>
            <Input
              id={`cf_${field.id}`}
              type={inputType}
              value={String(value)}
              onChange={(e) => onChange(field.id, e.target.value)}
              disabled={disabled}
              required={field.required}
              placeholder={field.type === 'phone' ? '+1 555 000 0000' : undefined}
            />
          </div>
        )
      })}
    </div>
  )
}
