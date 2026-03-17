# Elevator Workflow – User Guide

This guide explains how to use the **Elevator Workflow** module for elevator sales and implementation in Odoo 19.

---

## 1. Overview

The module adds:

| Area | What it does |
|------|----------------|
| **CRM Lead / Opportunity** | Extra fields for technical survey: Number of Floors, Shaft Dimensions (H/W/D), Passenger Capacity. |
| **CRM Pipeline** | Four stages: New Lead → Technical Survey (Breakdown) → Quotation → Won. |
| **Project Task** | Link to Sale Order, assigned Vehicle (Fleet), and Final site measurements (shaft H/W/D). |
| **Sale Order** | Button to open linked Implementation Tasks. |

Automation (e.g. “create task when quotation is confirmed”) is done via **Settings → Technical → Automation → Automated Actions**, not inside the module.

---

## 2. Where to Find Everything

- **CRM:** **Sales → CRM → Leads** (or Opportunities). Open any lead/opportunity to see the **Technical survey data** block.
- **Pipeline stages:** **Sales → Configuration → Pipeline Stages** (or edit stages from the lead kanban).
- **Projects / Tasks:** **Project → Tasks**. On a task form you will see **Sale Order**, **Vehicle**, and **Installation → Final site measurements**.
- **Sale Order:** **Sales → Orders → Quotations**. On a confirmed order, use the **Task(s)** stat button to open implementation tasks.
- **Fleet:** **Fleet → Vehicles** to manage vehicles; assign one on the task form.

---

## 3. Use Case Example: From Lead to Installation Sign-off

### Scenario

**ABC Tower** needs a new passenger elevator. You will:

1. Create a lead and move it through the pipeline.
2. Capture technical survey data (floors, shaft, capacity).
3. Create a quotation and confirm the order.
4. Create an implementation task, assign a vehicle, and record final site measurements.

---

### Step 1: New Lead

1. Go to **Sales → CRM → Leads**.
2. Click **New**.
3. Fill:
   - **Contact** (e.g. John Smith, ABC Tower).
   - **Expected Revenue** (optional).
   - **Salesperson** (optional).
4. Set the stage to **New Lead** (or leave default if it is already this).
5. Save.

---

### Step 2: Technical Survey (Breakdown)

1. Move the lead to the **Technical Survey (Breakdown)** stage (drag on kanban or change stage in form).
2. Schedule a **Meeting** activity (or another activity type) for the site visit: use **Schedule Activity** on the lead and assign the technician(s). Use **Calendar** to see and assign site visits.
3. After the breakdown visit, open the lead and scroll to **Technical survey data**:
   - **Number of Floors:** 12  
   - **Shaft Height (m):** 3.20  
   - **Shaft Width (m):** 1.80  
   - **Shaft Depth (m):** 2.10  
   - **Passenger Capacity:** 10  
4. Save.

---

### Step 3: Quotation and Won

1. Move the lead to **Quotation**.
2. Click **Create Quotation** (or **New Quotation**) to create a Sale Order from the opportunity.
3. On the quotation, add the **Elevator** product (and options if any), set quantity and price, then send the quotation to the customer.
4. When the customer accepts, click **Confirm** to confirm the order.
5. Move the lead to **Won** (or use your normal won process).

---

### Step 4: Implementation Task (after order is confirmed)

If you have an **Automated Action** that creates a project task when the Sale Order is confirmed:

- A task is created automatically and linked to the order (**Sale Order** field on the task).

If not:

1. Go to **Project → Tasks** (or your “Elevator installation” project).
2. **New**.
3. Set **Project**, **Task title** (e.g. “ABC Tower – Elevator installation”), **Assignees**.
4. In **Sale Order**, select the confirmed order (e.g. “S00042 – ABC Tower”). Save.

---

### Step 5: Vehicle and Final Site Measurements

1. Open the implementation task.
2. **Vehicle:** In the top area (after Project), set **Vehicle** to the truck/van used to transport components (e.g. “Service Van 01”). Use **Fleet → Vehicles** if you need to create one.
3. When the technician finishes the installation, they fill **Installation → Final site measurements**:
   - **Final Shaft Height (m):** 3.18  
   - **Final Shaft Width (m):** 1.82  
   - **Final Shaft Depth (m):** 2.12  
   (These can differ slightly from the survey; they are the as-built values.)
4. Complete any **checklists** or **Quality Control** steps you use for installation sign-off.
5. Mark the task as **Done** (or move it to your “Done” stage).

---

### Step 6: From Sale Order to Task

1. Go to **Sales → Orders** and open the confirmed order (e.g. S00042).
2. In the top right, use the **Task(s)** stat button (shows the count of linked tasks).
3. Click it to open the list of implementation tasks for this order. Open the task to see vehicle and final measurements.

---

## 4. Summary Flow

```
New Lead → Technical Survey (Breakdown) → Quotation → Won
                ↓
        [Technical survey data: floors, shaft H/W/D, capacity]
                ↓
        Quotation created & confirmed
                ↓
        Implementation Task created (manual or automated)
                ↓
        [Vehicle assigned, Final site measurements filled]
                ↓
        Task marked Done (optional: recurring task / maintenance for monthly inspections)
```

---

## 5. Optional: Automations

- **Create task when order is confirmed**  
  **Settings → Technical → Automation → Automated Actions → Create**  
  - Model: **Sale Order**  
  - Trigger: **On update** (or **On create** if you confirm at creation)  
  - Condition: **State** = **Sale** (or equivalent)  
  - Action: **Create a record** → Model **Project Task**, set **Project**, **Sale Order** (map to **x_sale_order_id** if your form shows it), and any default assignee or title.

- **Recurring task or maintenance on sign-off**  
  Create another Automated Action on **Project Task**: when **Stage** = Done (and optionally **Task type** = Installation), then create a **Recurring Task** or **Maintenance Request** for monthly safety inspections.

---

## 6. CRM Stages Provided by the Module

The module adds four **CRM stages** (in addition to any existing ones):

| Stage | Use |
|-------|-----|
| **New Lead** | Initial contact. |
| **Technical Survey (Breakdown)** | Site visit and technical survey; fill **Technical survey data** here. |
| **Quotation** | Quotation sent; create and confirm SO from here. |
| **Won** | Deal won; order confirmed. |

To use only these four in your pipeline, configure your **Sales Team** so its pipeline uses these stages, or hide/archive the default stages you do not need.

---

## 7. Troubleshooting

| Issue | What to check |
|------|----------------|
| No “Technical survey data” on lead | Confirm **Elevator Workflow** is installed; refresh the page or clear cache. |
| No “Sale Order” or “Vehicle” on task | Open a **Project Task** (not a different model); confirm module is installed. |
| “Task(s)” button missing on SO | Confirm the module is installed and the view is not overridden by another app. |
| Stages not visible | Go to **Configuration → Pipeline Stages** and ensure the four stages are assigned to your Sales Team / pipeline. |

For more setup details (e.g. MRP, Quality, Fleet), see the main **Elevator Workflow** configuration plan or your internal implementation docs.
