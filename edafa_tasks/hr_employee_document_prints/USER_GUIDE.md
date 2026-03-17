# User Guide - HR Employee Document Prints

## Purpose
This guide explains how HR users can print the Work Commencement Notice for employees.

## Who Can Use It
- HR Officer (`hr.group_hr_user`)
- HR Manager (`hr.group_hr_manager`)

## Before You Start
- The module `HR Employee Document Prints` must be installed.
- Employee record should exist and be saved.

## Employee Data Used in the Document
The report reads:
- Employee name
- Nationality
- ID or Iqama
- Email
- Mobile
- Job title
- Department
- Joining date
- Company header/logo

## Recommended Data Entry
On each employee record, fill these fields when available:
- `Document Nationality`
- `Document ID / Iqama`
- `Work Email`
- `Mobile`
- `Job Position`
- `Department`
- `Contract Start Date`

## How To Print (Single Employee)
1. Open `Employees` and select an employee.
2. Click the button for Work Commencement Notice in the header.
3. Or open the `Print` menu and select Work Commencement Notice.
4. The PDF is generated and downloaded/opened by your browser.

## How To Print (Multiple Employees)
1. Open `Employees` list view.
2. Select multiple employee records.
3. Open `Action` or `Print` menu (depending on view) and choose Work Commencement Notice.
4. Odoo generates a multi-page PDF (one section/page per employee).

## Field Fallback Behavior
If a value is missing, the system uses fallback sources:
- Nationality: contract/version nationality then employee `Document Nationality`
- ID/Iqama: contract/version ID then employee `Document ID / Iqama`
- Email: work email then other employee email fields
- Mobile: mobile phone then work phone then phone

## Troubleshooting
- Button not visible:
  - Check user has HR Officer/Manager access.
  - Confirm employee record is saved.
- PDF missing expected values:
  - Verify employee fields are filled.
  - Verify employee contract/version data if your flow uses version-based fields.
- Wrong company header/logo:
  - Check employee company assignment and company logo configuration.
- Action not found in Print menu:
  - Confirm module installation is complete and app list is updated.

## Best Practices
- Keep employee core data complete before printing official documents.
- Use batch print only after validating data consistency.
- Reprint after any employee profile corrections.
