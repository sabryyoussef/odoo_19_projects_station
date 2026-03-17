Elevator Workflow
================

Odoo 19 module for end-to-end Elevator Sales and Implementation workflow.
Provides views, data, and minimal code only (no business logic); use
Settings and Automated Actions for automation.

Contents
--------
* **CRM Lead:** Technical survey fields (Number of Floors, Shaft H/W/D, Passenger Capacity).
* **Project Task:** Sale Order link, Fleet vehicle, Final site measurements (shaft H/W/D).
* **Sale Order:** Button to open linked Implementation Tasks.
* **Data:** CRM stages: New Lead, Technical Survey (Breakdown), Quotation, Won.

Setup
-----
1. Install the module (Apps → Elevator Workflow).
2. To use the 4 stages as your main pipeline: CRM → Configuration → Pipeline Stages;
   assign "New Lead", "Technical Survey (Breakdown)", "Quotation", "Won" to your
   Sales Team, or rename the default stages manually to match.
3. Create an Automated Action: SO confirmed → Create project task, set
   x_sale_order_id to the order.
4. Optional: Automated Action on task sign-off → Create recurring task or
   maintenance request for monthly inspections.

Depends: crm, sale_management, project, fleet, stock, mrp.
