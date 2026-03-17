Role: You are an Odoo 19 Technical Consultant.
Objective: Create a "Lazy/Lean" Prototype for an Elevator Lifecycle Management module. The goal is a 10-minute demo to get stakeholder approval. Do not write complex logic; use Odoo's native inheritance and standard flows.

Module Name: elevator_pro_demo

Task 1: Data Model & CRM (The Lead)

    Inherit crm.lead.

    Add a "Technical Specs" notebook tab with these fields: shaft_width, shaft_depth, pit_depth, overhead_height, floors_count (Integer).

    Add a button: "Create Site Inspection".

Task 2: Site Inspection (The Field Service)

    Link to project.task or a new simplified model elevator.inspection.

    Include a checklist for: [Measurements Taken, Photos Uploaded, Wiring Checked].

    State: Draft -> Scheduled -> Completed.

Task 3: Sales & Engineering (The Quote)

    Inherit sale.order.

    Add a field engineering_approved (Boolean).

    Logic: If engineering_approved is False, show a "Warning Ribbon" on the Quotation.

    The Sales Price should be a simple "Cost + Margin" calculation (Manual for now).

Task 4: Manufacturing & Project (The Execution)

    Use Odoo’s standard MTO (Make to Order) flow.

    Define one generic BoM (Bill of Materials) for a "Standard 3-Floor Passenger Elevator".

    When the Sale Order is confirmed, it must automatically create a Manufacturing Order and a Project Task for "Installation".

Task 5: Quality & Maintenance (The Handover)

    In the Project Task, add a "Quality Pass" checkbox.

    Once checked, change the stage to "Delivered".

    Trigger a simple Maintenance Equipment record creation in the maintenance module.

UI Requirements:

    Create a single "Elevator Dashboard" (Action Window) that shows a Kanban view of all active elevator projects grouped by "State": [New, Inspection, Manufacturing, Installation, QC, Live].

    Use standard Odoo 19 purple/dark mode compatible icons.

Constraints:

    No external API integrations.

    No complex Python constraints.

    Use Odoo Studio-like simplicity in the XML.

Why this "Lazy Plan" works for a Demo:

    Speed: By inheriting crm.lead and sale.order, you don't have to build a database from scratch.

    Visual Impact: Using the Kanban view for the "State Machine" (from New to Maintenance) is the most "sellable" part of a demo.

    The "Wow" Factor: Showing that a Sale Order automatically creates a Manufacturing Order and a Maintenance Contract proves the "Integrated" value of Odoo without you having to code the background math.

Would you like me to generate the basic Python/XML manifest for this "Lazy" module so you can drop it into an Odoo instance?