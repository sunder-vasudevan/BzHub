import { fetchLeaveRequests, fetchPurchaseOrders, fetchAppraisals, fetchInventory } from './db'

export interface AppNotification {
  id: string
  type: 'leave' | 'purchase_order' | 'appraisal' | 'low_stock'
  title: string
  body: string
  href: string
  severity: 'info' | 'warning' | 'urgent'
}

export async function fetchNotifications(): Promise<AppNotification[]> {
  const [leaves, pos, appraisals, inventory] = await Promise.all([
    fetchLeaveRequests(),
    fetchPurchaseOrders(),
    fetchAppraisals(),
    fetchInventory(),
  ])

  const notifications: AppNotification[] = []

  const pendingLeaves = leaves.filter(l => l.status === 'Pending')
  if (pendingLeaves.length > 0) {
    notifications.push({
      id: 'leave-pending',
      type: 'leave',
      title: `${pendingLeaves.length} Leave Request${pendingLeaves.length > 1 ? 's' : ''} Pending`,
      body: 'Awaiting your approval in HR → Leave',
      href: '/hr',
      severity: 'urgent',
    })
  }

  const pendingPOs = pos.filter(p => p.status === 'Pending')
  if (pendingPOs.length > 0) {
    notifications.push({
      id: 'po-pending',
      type: 'purchase_order',
      title: `${pendingPOs.length} Purchase Order${pendingPOs.length > 1 ? 's' : ''} Pending`,
      body: 'Awaiting approval in Operations → Purchase Orders',
      href: '/operations',
      severity: 'urgent',
    })
  }

  const pendingAppraisals = appraisals.filter(a => a.status === 'Pending' || a.status === 'In Progress')
  if (pendingAppraisals.length > 0) {
    notifications.push({
      id: 'appraisal-pending',
      type: 'appraisal',
      title: `${pendingAppraisals.length} Appraisal${pendingAppraisals.length > 1 ? 's' : ''} to Review`,
      body: 'Pending sign-off in HR → Appraisals',
      href: '/hr',
      severity: 'info',
    })
  }

  const lowStock = (inventory as Array<{quantity: number, threshold: number, item_name: string}>).filter(
    i => (i.threshold ?? 0) > 0 && i.quantity <= i.threshold
  )
  if (lowStock.length > 0) {
    notifications.push({
      id: 'low-stock',
      type: 'low_stock',
      title: `${lowStock.length} Low Stock Item${lowStock.length > 1 ? 's' : ''}`,
      body: `Items running low: ${lowStock.slice(0, 3).map(i => i.item_name).join(', ')}${lowStock.length > 3 ? '…' : ''}`,
      href: '/operations',
      severity: 'warning',
    })
  }

  return notifications
}
