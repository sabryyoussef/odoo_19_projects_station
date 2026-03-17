# Elevator Pro Demo User Guide

## Overview
`elevator_pro_demo` adds a guided flow for elevator opportunities from CRM to live handover:
- CRM opportunity tracking by elevator stage
- Site inspection task creation
- Sales order linkage to the opportunity
- Installation task creation on sales confirmation
- Quality pass and maintenance equipment creation

## Prerequisites
- Module installed: `elevator_pro_demo`
- User has access to CRM, Sales, Project, and Maintenance apps

## Main Menu
- CRM -> `Elevator Flow`

This dashboard opens opportunities grouped by `Elevator Flow Stage`.

## Elevator Opportunity Setup
1. Open an opportunity in CRM.
2. Fill the elevator fields in `Elevator Demo Flow`:
- Shaft Height / Width / Depth
- Floors
- Passengers Capacity
- Speed
- Machine Room Required
3. Confirm `Elevator Flow Stage` starts at `New`.

## Create Site Inspection
1. From the opportunity, click `Create Site Inspection`.
2. Odoo creates (or reuses) project `Elevator Operations`.
3. A project task is created:
- Task type: `Inspection`
- Inspection status: `Draft`
- Linked to the opportunity
4. Opportunity stage becomes `Inspection`.

## Manage Inspection Task
From the inspection task form, use header buttons:
- `Inspection Draft`
- `Inspection Scheduled`
- `Inspection Completed`

When set to `Inspection Completed`, the linked opportunity stage moves to `Manufacturing`.

## Sales Order Flow
1. Create a quotation/sales order.
2. Set `Elevator Lead` to link it with the CRM opportunity.
3. `Engineering Approved` is available as a control field.
4. Confirm the sales order.

On confirmation:
- Installation task is auto-created in `Elevator Operations`
- Opportunity stage moves to `Installation` (after task creation)

## Quality and Go-Live
1. Open the installation task.
2. Click `Quality Pass`.

Result:
- Task marked as quality passed
- Opportunity stage becomes `Live`
- Maintenance equipment is auto-created and linked to the sales order

## Expected Auto-Created Records
- Project: `Elevator Operations` (if missing)
- Site inspection task from opportunity action
- Installation task from sales confirmation
- Maintenance equipment after quality pass

## Troubleshooting
- If `Create Site Inspection` does not create a new task, check if `Site Inspection Task` is already linked.
- If no installation task appears after confirming sale order, verify `Elevator Lead` is set.
- If no equipment is created after `Quality Pass`, ensure task is linked to a sales order.
