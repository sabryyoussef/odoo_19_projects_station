# HR Employee Document Prints

## Overview
`hr_employee_document_prints` adds HR document printing to the employee profile.
Current scope includes one official document:
- Work Commencement Notice (QWeb PDF)

The module is intentionally structured for future HR templates.

## Features
- Adds two fallback fields on `hr.employee`:
  - `document_nationality_id`
  - `document_id_iqama`
- Adds a print button on employee form header:
  - `action_print_work_commencement_notice`
- Adds a report action in the Print menu for employees.
- Generates bilingual (Arabic/English) RTL PDF layout.
- Supports batch printing for multiple employees.
- Uses fallback logic for key values:
  - Nationality: employee version country then fallback employee document nationality
  - ID/Iqama: version identification then fallback employee document ID
  - Email: `work_email`, then `email`, then `private_email`
  - Mobile: `mobile_phone`, then `work_phone`, then `phone`

## Module Structure
- `models/hr_employee.py`: employee field extensions and print action method.
- `views/hr_employee_views.xml`: form button and fallback fields placement.
- `reports/hr_employee_documents_report.xml`: report action and QWeb template.
- `tests/test_hr_employee_document_prints.py`: functional coverage and layout checks.

## Dependencies
- Odoo module: `hr`

## Installation
1. Add the addon path containing this module to your Odoo `addons_path`.
2. Update app list.
3. Install `HR Employee Document Prints`.

## Security and Access
- New fields are visible for HR users/managers (`hr.group_hr_user`, `hr.group_hr_manager`).
- Print action is available from the employee form/report menu for HR users.

## How It Works
1. Open an employee profile.
2. Click the Work Commencement print action from the header or Print menu.
3. Odoo runs `action_print_work_commencement_notice`.
4. The report `hr_employee_document_prints.report_work_commencement_notice` renders PDF.

## Testing
The module includes post-install tests under:
- `tests/test_hr_employee_document_prints.py`

Example run:
```bash
python odoo-bin -d <db_name> --test-tags hr_doc_prints --stop-after-init -u hr_employee_document_prints
```

## Roadmap
- Add more HR document templates using the same scaffold.
- Add configurable template variants by company/legal entity.
- Add optional digital signature integration.
