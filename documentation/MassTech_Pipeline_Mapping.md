# MassTech APMaldi Sales Pipeline → BzHub Stage Mapping

> **Source:** Masstech Lead Process Flow v1.92 (April 20, 2022)
> **BzHub version referenced:** v5.0.0

---

## Overview

MassTech's Zoho CRM pipeline for APMaldi Sales consists of **10 stages** spanning the full lead-to-fulfillment lifecycle. BzHub's CRM currently uses **6 generic stages**. This document maps the two systems, identifies coverage gaps, and notes which transitions are automatic vs. manual.

---

## Pipeline Stage Mapping

| # | MassTech Stage | BzHub Equivalent | Transition Type | Responsible Team(s) | Key Actions / Notes |
|---|---|---|---|---|---|
| 1 | **Deal** | **New** | Auto | Marketing | Entry point. Deal created, quote created and sent for approval. |
| 2 | **Qualification** | **Contacted** | Auto | Marketing / Mgmt | Stage auto-changes after quote approval. |
| 3 | **Proposal / User Quote / Negotiation** | **Qualified** | Auto | Marketing / Mgmt | Stage auto-changes when quote is sent to customer. |
| 4 | **Review / Final Quote / RFQ / Bid** | **Proposal** | Manual | Mgmt / Finance / Customer | Quote accepted; Zoho Desk support ticket created; email sent to customer with support info. |
| 5 | **PO / WO Received** | **Proposal** *(sub-phase)* | Manual | Customer / Finance | Customer delivers Purchase Order or Work Order. |
| 6 | **Sales Order Confirmation by MTI** | *(No BzHub equivalent)* | Auto | Finance / Mgmt | Accepted quote auto-converts to Draft Sales Order in Zoho Books. Zoho Project + tasks created. Production & Shipping modules created. |
| 7 | **In Production** | *(No BzHub equivalent)* | Auto | Production | Stage auto-changes based on status in CRM Production Module. |
| 8 | **Production Complete** | *(No BzHub equivalent)* | Auto | Production / Shipping | Factory Checklist must be submitted before advancing to Shipping. |
| 9 | **Shipped** | *(No BzHub equivalent)* | Auto | Shipping / Support | Packing checklist attached in Shipping Module. MassTech Support team takes over. |
| 10 | **Closed Won** | **Won** | Auto | Support / Mgmt | Deal closed. |
| — | *(Implicit — deal not won)* | **Lost** | Manual | — | No explicit MassTech stage; assumed as off-ramp at any point. |

---

## Automatic vs. Manual Transitions

| Transition | Type | Trigger |
|---|---|---|
| Deal → Qualification | **Auto** | Deal entry |
| Qualification → Proposal/Negotiation | **Auto** | Quote approval |
| Proposal/Negotiation → Review/Final Quote | **Auto** | Quote sent to customer |
| Review/Final Quote → PO/WO Received | **Manual** | Customer delivers PO or WO |
| PO/WO Received → Sales Order Confirmation | **Manual** | MTI confirms and creates SO |
| Sales Order Confirmation → In Production | **Auto** | Production Module status |
| In Production → Production Complete | **Auto** | Production Module status |
| Production Complete → Shipped | **Auto** | Factory Checklist submitted |
| Shipped → Closed Won | **Auto** | Shipment marked as Delivered |

---

## Zoho App Touchpoints per Stage

| MassTech Stage | Zoho Apps Involved |
|---|---|
| Deal → Qualification | CRM |
| Qualification → Proposal/Negotiation | CRM, Books |
| Review/Final Quote/RFQ/Bid | CRM, Books, Desk |
| Sales Order Confirmation | CRM, Books, Projects |
| In Production | CRM, Projects |
| Production Complete | CRM, Projects |
| Shipped | CRM, Inventory |
| Closed Won | CRM, Inventory |

---

## Gap Analysis

### BzHub stages with no direct MassTech equivalent

| BzHub Stage | Status |
|---|---|
| **Contacted** | Partially maps to MassTech's "Qualification" (stage 2). MassTech has no distinct first-contact stage — qualification begins at deal entry. |

### MassTech stages with no BzHub equivalent (stages 6–9)

These four stages cover the **post-sale fulfillment lifecycle**, which BzHub currently collapses entirely into "Won":

| MassTech Stage | Gap Description |
|---|---|
| Sales Order Confirmation by MTI | BzHub has no SO creation or project scaffolding step |
| In Production | BzHub has no production tracking stage |
| Production Complete | BzHub has no factory checklist gate or production-complete stage |
| Shipped | BzHub has no shipping/fulfillment stage |

To fully replicate MassTech's pipeline in BzHub, four new post-sale stages would need to be added between "Won" and "Closed Won", turning "Won" into an intermediate production stage rather than a terminal state.

---

## Team Legend

| Code | Team |
|---|---|
| Mtkt | Marketing |
| Mgmt | Management |
| Prod | Production |
| Shipping | Shipping |
| Finance | Finance |
| Support | Customer Support |
| Customer | External customer |

---

## Recommended BzHub Stage Expansion (if code changes are later desired)

To fully represent MassTech's pipeline, BzHub's stage list would expand from 6 to 10 active stages:

```
New → Qualified → Proposal → PO Received → In Production → Production Complete → Shipped → Won | Lost
```

Mapping back to MassTech:

| Proposed BzHub Stage | Maps To |
|---|---|
| New | Deal + Qualification |
| Qualified | Proposal/User Quote/Negotiation |
| Proposal | Review/Final Quote/RFQ/Bid |
| PO Received | PO/WO Received + Sales Order Confirmation by MTI |
| In Production | In Production |
| Production Complete | Production Complete |
| Shipped | Shipped |
| Won | Closed Won |
| Lost | *(implicit off-ramp)* |
