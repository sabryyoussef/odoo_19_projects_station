# Elevator Pro Demo Use Cases

## Use Case 1: New Elevator Opportunity to Site Inspection
### Actor
Sales Engineer

### Goal
Capture project specs and dispatch site inspection.

### Steps
1. Create an opportunity in CRM.
2. Enter shaft dimensions, floors, speed, and capacity.
3. Click `Create Site Inspection`.

### Expected Result
- A project task is created in `Elevator Operations`.
- Inspection task is linked to the opportunity.
- Flow stage becomes `Inspection`.

## Use Case 2: Inspection Completion Unlocks Manufacturing Stage
### Actor
Project Coordinator

### Goal
Move opportunity based on inspection completion.

### Steps
1. Open the linked inspection task.
2. Set status to `Inspection Scheduled`.
3. Set status to `Inspection Completed`.

### Expected Result
- Inspection status is stored as `Completed`.
- Opportunity flow stage updates to `Manufacturing`.

## Use Case 3: Sales Confirmation Creates Installation Task
### Actor
Sales Operations

### Goal
Start execution after commercial confirmation.

### Steps
1. Create quotation for the customer.
2. Link `Elevator Lead` on sales order.
3. Confirm sales order.

### Expected Result
- Installation task is auto-created in `Elevator Operations`.
- Installation task is linked to both sales order and opportunity.
- Opportunity flow stage is set to `Installation`.

## Use Case 4: Quality Pass Moves Deal to Live
### Actor
QA Engineer

### Goal
Complete the final quality gate and hand over.

### Steps
1. Open installation task.
2. Click `Quality Pass`.

### Expected Result
- Task flag `Quality Passed` is enabled.
- Opportunity flow stage becomes `Live`.
- Maintenance equipment record is created and linked to sales order.

## Use Case 5: Dashboard Monitoring by Stage
### Actor
Sales Manager

### Goal
Track opportunities by operational stage.

### Steps
1. Open CRM -> `Elevator Flow`.
2. Review kanban columns grouped by flow stage.
3. Filter/search by `Elevator Flow Stage`.

### Expected Result
- Opportunities are visible by `New`, `Inspection`, `Manufacturing`, `Installation`, `QC`, and `Live`.
- Manager can quickly identify bottlenecks and next actions.
