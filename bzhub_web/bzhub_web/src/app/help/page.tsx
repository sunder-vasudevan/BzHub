"use client"

import { useState } from "react"
import AppLayout from "@/components/layout/AppLayout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  LayoutDashboard,
  ShoppingCart,
  Briefcase,
  Users,
  BarChart3,
  Settings,
  ChevronDown,
  ChevronRight,
  HelpCircle,
  Package,
  CreditCard,
  Truck,
  Target,
  Star,
  Zap,
  DollarSign,
  TrendingUp,
  Building2,
  CalendarDays,
  ClipboardList,
  CheckCircle2,
  UserCheck,
  Bell,
  Settings2,
  Download,
  Search,
  ClipboardCheck,
} from "lucide-react"

interface Section {
  id: string
  icon: React.ReactNode
  title: string
  badge?: string
  content: { heading: string; text: string }[]
}

const sections: Section[] = [
  {
    id: "dashboard",
    icon: <LayoutDashboard className="h-5 w-5" />,
    title: "Dashboard",
    content: [
      {
        heading: "KPI Cards",
        text: "The top row shows today's sales revenue, total inventory value, number of low-stock items, and active employees. These update every time you refresh.",
      },
      {
        heading: "Sales Trend Chart",
        text: "The line chart shows daily revenue for the past 30 days. Hover over any point to see the exact figure for that day.",
      },
      {
        heading: "Product Velocity",
        text: "Fast Movers and Slow Movers show which inventory items are selling quickly or sitting idle, helping you make restocking decisions.",
      },
    ],
  },
  {
    id: "operations-inventory",
    icon: <Package className="h-5 w-5" />,
    title: "Operations — Inventory",
    badge: "Operations",
    content: [
      {
        heading: "Adding an Item",
        text: "Click 'Add Item' in the Inventory tab. Fill in the name, category, quantity, cost price, and sale price. Upload a product image if needed.",
      },
      {
        heading: "Editing / Deleting",
        text: "Click the Edit button on any row to update details. Click Delete to remove the item — this cannot be undone.",
      },
      {
        heading: "Low Stock Alerts",
        text: "Items with quantity below 10 are flagged with a Low Stock badge. You can filter by low-stock items using the search bar.",
      },
      {
        heading: "Sorting",
        text: "Click any column header to sort the inventory table by that column. Click again to reverse the sort order.",
      },
    ],
  },
  {
    id: "operations-pos",
    icon: <CreditCard className="h-5 w-5" />,
    title: "Operations — Point of Sale",
    badge: "Operations",
    content: [
      {
        heading: "Making a Sale",
        text: "In the POS tab, click any product card to add it to the cart. Adjust quantities in the cart using the + / − buttons.",
      },
      {
        heading: "Completing a Sale",
        text: "Once items are in the cart, enter the customer name (optional) and click 'Complete Sale'. The inventory quantities update automatically.",
      },
      {
        heading: "Bills History",
        text: "All completed sales appear in the Bills section below the POS. Click 'Print' on any bill to open a print-friendly view.",
      },
    ],
  },
  {
    id: "operations-suppliers",
    icon: <Truck className="h-5 w-5" />,
    title: "Operations — Suppliers",
    badge: "Operations",
    content: [
      {
        heading: "Adding a Supplier",
        text: "In the Suppliers tab, click 'Add Supplier'. Enter the company name, contact person, phone, email, and any notes.",
      },
      {
        heading: "Managing Suppliers",
        text: "Edit or delete suppliers using the buttons in the Actions column. Supplier records help you track where your stock comes from.",
      },
    ],
  },
  {
    id: "crm",
    icon: <Briefcase className="h-5 w-5" />,
    title: "CRM Pipeline",
    content: [
      {
        heading: "Pipeline Stages",
        text: "Leads move through six stages: New → Contacted → Qualified → Proposal → Won → Lost. Each column on the Kanban board represents one stage.",
      },
      {
        heading: "Adding a Lead",
        text: "Click the + button on any column header to add a lead directly into that stage. Fill in the title, value, probability, and assign an owner.",
      },
      {
        heading: "Moving a Lead",
        text: "Click the 'Move' button on a lead card to advance it to the next stage. Or click the card to open it and change the stage manually.",
      },
      {
        heading: "Pipeline Value",
        text: "The stats bar at the top shows total pipeline value (excluding Lost), conversion rate (Won / closed), and total lead count.",
      },
    ],
  },
  {
    id: "hr-employees",
    icon: <Users className="h-5 w-5" />,
    title: "HR — Employees",
    badge: "HR",
    content: [
      {
        heading: "Adding an Employee",
        text: "Click 'Add Employee' and fill in their name, designation, department, email, and phone. The employee is marked Active by default.",
      },
      {
        heading: "Editing Records",
        text: "Click Edit on any employee row to update their details. Changes take effect immediately.",
      },
    ],
  },
  {
    id: "hr-payroll",
    icon: <DollarSign className="h-5 w-5" />,
    title: "HR — Payroll",
    badge: "HR",
    content: [
      {
        heading: "Viewing Payroll",
        text: "The Payroll tab shows all payroll records with employee name, pay period, gross pay, net pay, and status (Draft / Paid).",
      },
      {
        heading: "Monthly Summary",
        text: "The card at the top of the Payroll tab shows the total gross payroll for the current month and how many records it includes.",
      },
    ],
  },
  {
    id: "hr-goals",
    icon: <Target className="h-5 w-5" />,
    title: "HR — Goals",
    badge: "HR",
    content: [
      {
        heading: "Creating a Goal",
        text: "Click 'Add Goal', select the employee, enter a title, description, and due date. Set the initial status to Active.",
      },
      {
        heading: "Check-ins",
        text: "Click 'Check-in' on any goal to log progress. Enter the percentage complete (0–100) and a note explaining the update.",
      },
      {
        heading: "Goal Statuses",
        text: "Goals can be: Draft (not started), Active (in progress), Completed (done), or Cancelled. Update status via the Edit dialog.",
      },
    ],
  },
  {
    id: "hr-appraisals",
    icon: <Star className="h-5 w-5" />,
    title: "HR — Appraisals",
    badge: "HR",
    content: [
      {
        heading: "Creating an Appraisal",
        text: "Click 'New Appraisal', select the employee and enter the period (e.g. 'Q1 2026'). Both self-rating and manager rating are on a 1–5 scale.",
      },
      {
        heading: "Overall Score",
        text: "The overall score is the average of the self-rating and manager rating, displayed in the table for quick comparison.",
      },
      {
        heading: "Appraisal Statuses",
        text: "Statuses flow: Pending → In Progress → Completed. Update via the Edit dialog after both parties have submitted their ratings.",
      },
    ],
  },
  {
    id: "hr-skills",
    icon: <Zap className="h-5 w-5" />,
    title: "HR — Skills Matrix",
    badge: "HR",
    content: [
      {
        heading: "Skills Library",
        text: "The left panel lists all skills grouped by category: Software, Hardware, Soft Skills, Domain Knowledge. Add new skills to the library with the Add button.",
      },
      {
        heading: "Assigning Skills to Employees",
        text: "Select an employee from the dropdown in the right panel. Click 'Add Skill', choose from the library, and set their proficiency: Beginner, Intermediate, Advanced, or Expert.",
      },
      {
        heading: "Updating Proficiency",
        text: "Click Edit on an employee's skill card to update their proficiency level as they grow.",
      },
    ],
  },
  {
    id: "leave-requests",
    icon: <CalendarDays className="h-5 w-5" />,
    title: "HR — Leave Requests",
    badge: "HR",
    content: [
      {
        heading: "Submitting a Leave Request",
        text: "In the HR → Leave tab, click 'New Request'. Select the employee, leave type (Annual, Sick, Unpaid, Other), date range, and an optional reason. Click 'Submit Request'.",
      },
      {
        heading: "Approving or Rejecting Leave",
        text: "Pending leave requests show green Approve and red Reject buttons. Click Approve to grant the leave or Reject to decline it. The status updates immediately.",
      },
      {
        heading: "Leave Types",
        text: "Annual — planned paid leave. Sick — medical leave. Unpaid — leave without pay. Other — any other reason.",
      },
    ],
  },
  {
    id: "purchase-orders",
    icon: <ClipboardList className="h-5 w-5" />,
    title: "Operations — Purchase Orders",
    badge: "Operations",
    content: [
      {
        heading: "Creating a Purchase Order",
        text: "In Operations → Purchase Orders, click 'New PO'. Select a supplier, enter the order date, expected delivery date, total amount, and a description of items being ordered.",
      },
      {
        heading: "Approval Workflow",
        text: "New POs are created with a Pending status. A manager reviews and clicks Approve or Reject. Approved orders can then be marked as Ordered once placed with the supplier, and Delivered once received.",
      },
      {
        heading: "PO Status Flow",
        text: "Pending → Approved → Ordered → Delivered. Rejected POs are closed. You can track where each order is in the pipeline at a glance.",
      },
    ],
  },
  {
    id: "appraisal-approval",
    icon: <CheckCircle2 className="h-5 w-5" />,
    title: "HR — Appraisal Sign-Off",
    badge: "HR",
    content: [
      {
        heading: "Manager Sign-Off",
        text: "Pending and In Progress appraisals show Approve and Reject buttons directly on the appraisals list. Click Approve to formally close the appraisal cycle, or Reject to send it back.",
      },
      {
        heading: "Appraisal Statuses",
        text: "Pending → In Progress → Approved (or Rejected). Approved appraisals are locked from further editing unless changed back via the Edit dialog.",
      },
    ],
  },
  {
    id: "reports",
    icon: <BarChart3 className="h-5 w-5" />,
    title: "Reports",
    content: [
      {
        heading: "Sales Report",
        text: "Shows a monthly breakdown of revenue, number of transactions, and average order value. Use this to spot seasonal trends.",
      },
      {
        heading: "Top Sellers",
        text: "Bar chart of your top 10 products by units sold. The table below ranks all products by quantity. Useful for reorder planning.",
      },
      {
        heading: "Inventory Report",
        text: "Full stock list with each item's quantity, unit price, and total value (qty × price). Low-stock items are flagged with a badge.",
      },
    ],
  },
  {
    id: "employee-portal",
    icon: <Users className="h-5 w-5" />,
    title: "Employee Self-Service Portal",
    badge: "My Portal",
    content: [
      {
        heading: "Selecting Yourself",
        text: "Open 'My Portal' from the sidebar. Select your name from the dropdown to load your personal data. Login will replace this step in a future update.",
      },
      {
        heading: "My Goals",
        text: "View all goals assigned to you by your manager, including their status (Draft, In Progress, Completed) and due dates.",
      },
      {
        heading: "My Appraisals — Self-Assessment",
        text: "View appraisal cycles for your current or past periods. For Pending or In Progress appraisals, click 'Edit Self-Assessment' to submit your self-rating (0–5) and comments. This notifies your manager that your self-assessment is ready.",
      },
      {
        heading: "My Leave",
        text: "Submit new leave requests by selecting the leave type (Annual, Sick, Unpaid, Other), entering start and end dates, and an optional reason. Your request will appear as Pending until a manager approves or rejects it.",
      },
      {
        heading: "My Skills",
        text: "View your skills profile as set by your manager — grouped by category (Software, Hardware, Soft Skills, Domain Knowledge) with your proficiency level for each skill.",
      },
    ],
  },
  {
    id: "settings",
    icon: <Settings className="h-5 w-5" />,
    title: "Settings",
    content: [
      {
        heading: "Company Info",
        text: "Set your company name, address, phone, and email. This information appears on printed bills.",
      },
      {
        heading: "Currency",
        text: "Change the currency symbol displayed throughout the app (e.g. $, £, ₹). This is cosmetic only — it does not convert values.",
      },
    ],
  },
  {
    id: "notification-center",
    icon: <Bell className="h-5 w-5" />,
    title: "Notification Center",
    badge: "New",
    content: [
      {
        heading: "Bell Icon",
        text: "Click the bell icon in the top-right bar (desktop) or the mobile header to open your notification panel. A red badge shows the count of active notifications.",
      },
      {
        heading: "What Triggers Notifications",
        text: "BzHub automatically surfaces: pending leave requests, pending purchase orders awaiting approval, appraisals that need sign-off, and inventory items that have fallen below their stock threshold.",
      },
      {
        heading: "Navigating from a Notification",
        text: "Click any notification to jump directly to the relevant module. The panel closes automatically after you click.",
      },
    ],
  },
  {
    id: "dashboard-customization",
    icon: <Settings2 className="h-5 w-5" />,
    title: "Dashboard Customization",
    badge: "New",
    content: [
      {
        heading: "Customize Button",
        text: "Click the 'Customize' button (gear icon) in the top-right of the Dashboard header to open the customization panel.",
      },
      {
        heading: "Show / Hide KPI Cards",
        text: "Toggle the checkboxes next to each card name (Today's Sales, Inventory Value, Low Stock, Avg Daily Sales, Pipeline Value, Growth) to show or hide them. Your preferences are saved automatically.",
      },
      {
        heading: "Saved Preferences",
        text: "Your dashboard layout is saved to your browser's local storage under the key 'bzhub_dashboard_prefs'. It persists across page refreshes.",
      },
    ],
  },
  {
    id: "csv-export",
    icon: <Download className="h-5 w-5" />,
    title: "CSV Export",
    badge: "New",
    content: [
      {
        heading: "Export Inventory",
        text: "In Operations → Inventory tab, click 'Export CSV' to download the current visible inventory table including item name, quantity, prices and stock status.",
      },
      {
        heading: "Export Employees",
        text: "In HR → Employees tab, click 'Export CSV' to download a spreadsheet of all employees with their name, designation, team, email and phone.",
      },
      {
        heading: "Export Reports",
        text: "In the Reports page, each tab (Sales Report, Top Sellers, Inventory Report) has an 'Export CSV' button that downloads the data currently shown in that tab.",
      },
    ],
  },
  {
    id: "global-search",
    icon: <Search className="h-5 w-5" />,
    title: "Global Search",
    badge: "New",
    content: [
      {
        heading: "Opening the Search",
        text: "Press Cmd+K (Mac) or Ctrl+K (Windows/Linux) from any page to open the global search modal. You can also click the 'Search…' button in the top bar on desktop.",
      },
      {
        heading: "What It Searches",
        text: "The search queries four data sources simultaneously: Inventory (by item name), Employees (by name), CRM Contacts (by name), and CRM Leads (by title or company).",
      },
      {
        heading: "Using Results",
        text: "Results are grouped by category with colour-coded labels. Click any result to navigate directly to the relevant module page. The modal closes automatically.",
      },
      {
        heading: "Keyboard Navigation",
        text: "Press Escape to close the search modal at any time.",
      },
    ],
  },
  {
    id: "audit-log",
    icon: <ClipboardCheck className="h-5 w-5" />,
    title: "Audit Log",
    badge: "New",
    content: [
      {
        heading: "What is Logged",
        text: "BzHub automatically records create, update, and delete actions for: Employees, Leave Requests, Purchase Orders, and Goals. Each entry includes the table, record ID, action type, summary, and timestamp.",
      },
      {
        heading: "Viewing the Audit Log",
        text: "Go to 'Audit Log' in the sidebar (ClipboardCheck icon). The table shows the most recent 200 entries in reverse chronological order.",
      },
      {
        heading: "Filtering",
        text: "Filter by action type (Create / Update / Delete) or by module (table name) using the dropdowns at the top. Click 'Clear filters' to reset.",
      },
      {
        heading: "Database Setup",
        text: "The audit log requires the audit_logs table in Supabase. Run the SQL in documentation/supabase_schema_v3.sql to create it.",
      },
    ],
  },
]

function SectionCard({ section }: { section: Section }) {
  const [open, setOpen] = useState(false)

  return (
    <Card className="overflow-hidden">
      <button
        className="w-full text-left"
        onClick={() => setOpen(!open)}
      >
        <CardHeader className="py-4 px-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-[#6D28D9]">{section.icon}</span>
              <CardTitle className="text-base font-semibold">{section.title}</CardTitle>
              {section.badge && (
                <Badge variant="secondary" className="text-xs">{section.badge}</Badge>
              )}
            </div>
            {open
              ? <ChevronDown className="h-4 w-4 text-muted-foreground" />
              : <ChevronRight className="h-4 w-4 text-muted-foreground" />
            }
          </div>
        </CardHeader>
      </button>
      {open && (
        <CardContent className="px-5 pb-5 pt-0 space-y-4 border-t border-border">
          {section.content.map((item) => (
            <div key={item.heading}>
              <p className="text-sm font-semibold text-foreground mb-1">{item.heading}</p>
              <p className="text-sm text-muted-foreground leading-relaxed">{item.text}</p>
            </div>
          ))}
        </CardContent>
      )}
    </Card>
  )
}

export default function HelpPage() {
  return (
    <AppLayout activePage="help">
      <div className="px-4 py-4 md:px-6 md:py-8 max-w-3xl">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div
            className="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{ backgroundColor: "#6D28D920" }}
          >
            <HelpCircle className="h-5 w-5" style={{ color: "#6D28D9" }} />
          </div>
          <div>
            <h1 className="text-2xl font-bold">User Guide</h1>
            <p className="text-sm text-muted-foreground">How to use BzHub — click any section to expand</p>
          </div>
        </div>

        {/* Quick nav badges */}
        <div className="flex flex-wrap gap-2 mb-6">
          {["Dashboard", "Operations", "CRM", "HR", "Reports", "Settings", "New in v4.6"].map((label) => (
            <Badge key={label} variant="outline" className="cursor-default">{label}</Badge>
          ))}
        </div>

        {/* Sections */}
        <div className="space-y-3">
          {sections.map((section) => (
            <SectionCard key={section.id} section={section} />
          ))}
        </div>

        <p className="text-xs text-muted-foreground text-center mt-8">
          BzHub v4.6 · For support, contact your system administrator
        </p>
      </div>
    </AppLayout>
  )
}
