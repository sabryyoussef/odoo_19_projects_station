# -*- coding: utf-8 -*-
"""
Tests for hr_employee_document_prints
======================================

Task description
----------------
Validate the functionality and accuracy of the generated HR document.
Testing will ensure that the document correctly renders employee data and
that the PDF output is suitable for official use.

Testing tasks
-------------
1. Test with employees having complete data.
2. Test with employees having partial data.
3. Verify field mapping accuracy.
4. Validate Arabic layout and formatting.
5. Validate company header and branding.
6. Validate permissions for HR users.
7. Verify the PDF output across multiple employee records.

Expected outputs
----------------
- Verified HR document generation
- Confirmed field mapping accuracy
- Approved test version of the module
"""

from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import AccessError
from odoo.addons.mail.tests.common import mail_new_test_user


@tagged('post_install', '-at_install', 'hr_doc_prints')
class TestHrEmployeeDocumentPrints(TransactionCase):
    """
    Full validation suite for Work Commencement Notice (إشعار مباشرة عمل).

    All assertions are grouped into seven areas that mirror the task description:
        1  complete-data employees
        2  partial-data employees
        3  field-mapping accuracy
        4  Arabic layout and formatting
        5  company header and branding
        6  HR user permissions
        7  batch / multiple-employee PDF output
    """

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Saudi Arabia / Egypt for nationality tests
        cls.country_sa = cls.env.ref('base.sa')
        cls.country_eg = cls.env.ref('base.eg')

        # Dedicated test company so records don't pollute the default company
        cls.company = cls.env['res.company'].sudo().create({
            'name': 'Edafa Test Company / شركة إدافا للاختبار',
        })

        # Department and job used by the complete-data employee
        cls.department = cls.env['hr.department'].sudo().create({
            'name': 'Human Resources / الموارد البشرية',
            'company_id': cls.company.id,
        })
        cls.job = cls.env['hr.job'].sudo().create({
            'name': 'Software Engineer / مهندس برمجيات',
            'department_id': cls.department.id,
            'company_id': cls.company.id,
        })

        # ---- HR manager user ----
        # In Odoo 19, groups are assigned via mail_new_test_user with a
        # comma-separated groups string — the old groups_id M2M is gone.
        cls.hr_manager = mail_new_test_user(
            cls.env,
            login='test_hr_manager_docprints@example.com',
            name='Test HR Manager',
            email='test_hr_manager_docprints@example.com',
            password='Test@123456',
            groups='base.group_user,hr.group_hr_manager',
            company_id=cls.company.id,
        )

        # ---- HR user (officer) ----
        cls.hr_user = mail_new_test_user(
            cls.env,
            login='test_hr_officer_docprints@example.com',
            name='Test HR Officer',
            email='test_hr_officer_docprints@example.com',
            password='Test@123456',
            groups='base.group_user,hr.group_hr_user',
            company_id=cls.company.id,
        )

        # ---- Employee: complete data ----
        cls.employee_complete = cls.env['hr.employee'].sudo().create({
            'name': 'Ahmed Mohamed / أحمد محمد',
            'work_email': 'ahmed@testcompany.com',
            'mobile_phone': '+966500000001',
            'job_id': cls.job.id,
            'department_id': cls.department.id,
            'document_nationality_id': cls.country_sa.id,
            'document_id_iqama': '1234567890',
            'company_id': cls.company.id,
        })

        # ---- Employee: partial data (name only) ----
        cls.employee_partial = cls.env['hr.employee'].sudo().create({
            'name': 'Partial Employee / موظف جزئي البيانات',
            'company_id': cls.company.id,
        })

        # ---- Employee: no mobile_phone → fallback to work_phone ----
        cls.employee_phone_fallback = cls.env['hr.employee'].sudo().create({
            'name': 'Phone Fallback Employee',
            'work_phone': '+96611111111',
            'work_email': 'phone_fallback@testcompany.com',
            'company_id': cls.company.id,
        })

        # ---- Employee: Egyptian nationality ----
        cls.employee_egypt = cls.env['hr.employee'].sudo().create({
            'name': 'Sara Khaled / سارة خالد',
            'document_nationality_id': cls.country_eg.id,
            'document_id_iqama': '9876543210',
            'company_id': cls.company.id,
        })

        # Convenience reference to the report action record
        cls.report_action = cls.env.ref(
            'hr_employee_document_prints.action_report_work_commencement_notice'
        )

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def _render_html(self, employee_ids):
        """Render the QWeb HTML for the given employee id list and return a str."""
        html, _ = self.env['ir.actions.report']._render_qweb_html(
            self.report_action.report_name,
            employee_ids,
            data=None,
        )
        if isinstance(html, bytes):
            return html.decode('utf-8')
        return html

    # ==================================================================
    # 1 – Complete-data employees
    # ==================================================================

    def test_01_complete_employee_action_type(self):
        """
        Print action called on a complete-data employee must return an
        ir.actions.report response of type qweb-pdf.
        """
        action = self.employee_complete.action_print_work_commencement_notice()
        self.assertEqual(
            action.get('type'), 'ir.actions.report',
            "action type must be 'ir.actions.report'"
        )
        self.assertEqual(
            action.get('report_type'), 'qweb-pdf',
            "report_type must be 'qweb-pdf' for official PDF output"
        )

    def test_02_complete_employee_html_not_empty(self):
        """HTML rendering for a complete-data employee must not return empty content."""
        html = self._render_html([self.employee_complete.id])
        self.assertTrue(html.strip(), "Rendered HTML must not be empty")

    def test_03_complete_employee_name_in_output(self):
        """Employee name must appear verbatim in the rendered document."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn(
            self.employee_complete.name, html,
            "Employee full name must be present in the rendered output"
        )

    # ==================================================================
    # 2 – Partial-data employees
    # ==================================================================

    def test_04_partial_employee_renders_without_error(self):
        """
        Report must render without raising an exception when the employee
        has only a name and no optional fields filled in.
        """
        html = self._render_html([self.employee_partial.id])
        self.assertTrue(html.strip(), "Rendered HTML for partial-data employee must not be empty")

    def test_05_partial_employee_name_in_output(self):
        """Even a partial-data employee's name must appear in the output."""
        html = self._render_html([self.employee_partial.id])
        self.assertIn(
            self.employee_partial.name, html,
            "Partial employee name must still appear in rendered HTML"
        )

    def test_06_partial_employee_empty_fields_are_blank(self):
        """
        Absent optional fields (nationality, ID, email, mobile) must render as
        empty strings — not as 'False' or Python repr values.
        """
        html = self._render_html([self.employee_partial.id])
        self.assertNotIn('>False<', html, "'False' literal must never appear in the output")
        self.assertNotIn('>None<', html, "'None' literal must never appear in the output")

    # ==================================================================
    # 3 – Field-mapping accuracy
    # ==================================================================

    def test_07_field_map_nationality_from_document_nationality_id(self):
        """
        When version.country_id is absent, nationality must be sourced from
        hr.employee.document_nationality_id.
        """
        html = self._render_html([self.employee_complete.id])
        self.assertIn(
            self.country_sa.name, html,
            "Nationality (Saudi Arabia) must be rendered from document_nationality_id"
        )

    def test_08_field_map_nationality_different_country(self):
        """Nationality renders correctly for a different country (Egypt)."""
        html = self._render_html([self.employee_egypt.id])
        self.assertIn(
            self.country_eg.name, html,
            "Egyptian nationality must appear in the output"
        )

    def test_09_field_map_id_iqama(self):
        """document_id_iqama value must appear in the rendered output."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn(
            '1234567890', html,
            "document_id_iqama value must be rendered in the ID/Iqama field"
        )

    def test_10_field_map_id_iqama_different_employee(self):
        """ID/Iqama renders correctly for a second employee record."""
        html = self._render_html([self.employee_egypt.id])
        self.assertIn(
            '9876543210', html,
            "Second employee's ID/Iqama value must appear in the output"
        )

    def test_11_field_map_work_email_primary(self):
        """work_email is the primary email source and renders correctly."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn(
            'ahmed@testcompany.com', html,
            "work_email must be rendered as the email value"
        )

    def test_12_field_map_mobile_phone_primary(self):
        """mobile_phone is the primary mobile source and renders correctly."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn(
            '+966500000001', html,
            "mobile_phone must be rendered as the mobile value"
        )

    def test_13_field_map_mobile_fallback_to_work_phone(self):
        """
        When mobile_phone is absent, the template must fall back to work_phone.
        """
        html = self._render_html([self.employee_phone_fallback.id])
        self.assertIn(
            '+96611111111', html,
            "work_phone fallback must appear in the output when mobile_phone is absent"
        )

    def test_14_field_map_department_name(self):
        """Department name must appear in the rendered output for a complete employee."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn(
            self.department.name, html,
            "Department name must be rendered in the Department field"
        )

    def test_15_field_map_job_title(self):
        """Job name must appear in the rendered output for a complete employee."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn(
            self.job.name, html,
            "Job name must be rendered in the Job Title field"
        )

    # ==================================================================
    # 4 – Arabic layout and formatting
    # ==================================================================

    def test_16_rtl_direction_attribute(self):
        """Rendered HTML must carry dir="rtl" for correct Arabic right-to-left layout."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn(
            'dir="rtl"', html,
            'dir="rtl" attribute is required for Arabic RTL layout'
        )

    def test_17_arabic_document_title(self):
        """Arabic main title 'إشعار مباشرة عمل' must be present."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn(
            'إشعار مباشرة عمل', html,
            "Arabic main title must be present in the document"
        )

    def test_18_english_document_title(self):
        """English subtitle 'Work Commencement Notice' must be present."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn(
            'Work Commencement Notice', html,
            "English subtitle must be present in the document"
        )

    def test_19_arabic_field_label_employee_name(self):
        """Arabic field label 'اسم الموظف' must be present."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn('اسم الموظف', html)

    def test_20_arabic_field_label_nationality(self):
        """Arabic field label 'الجنسية' must be present."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn('الجنسية', html)

    def test_21_arabic_field_label_id_iqama(self):
        """Arabic field label 'رقم الهوية' must be present."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn('رقم الهوية', html)

    def test_22_arabic_field_label_email(self):
        """Arabic field label 'البريد الإلكتروني' must be present."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn('البريد الإلكتروني', html)

    def test_23_arabic_field_label_mobile(self):
        """Arabic field label 'الجوال' must be present."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn('الجوال', html)

    def test_24_arabic_field_label_job_title(self):
        """Arabic field label 'المسمى الوظيفي' must be present."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn('المسمى الوظيفي', html)

    def test_25_arabic_field_label_department(self):
        """Arabic field label 'الإدارة' must be present."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn('الإدارة', html)

    def test_26_arabic_field_label_joining_date(self):
        """Arabic field label 'تاريخ المباشرة' must be present."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn('تاريخ المباشرة', html)

    def test_27_arabic_signature_labels(self):
        """
        Arabic signature-line labels (إعداد, اعتماد, توقيع الموظف) must all
        appear in the document footer.
        """
        html = self._render_html([self.employee_complete.id])
        self.assertIn('إعداد', html, "Signature label 'إعداد' (Prepared by) must be present")
        self.assertIn('اعتماد', html, "Signature label 'اعتماد' (Approved by) must be present")
        self.assertIn('توقيع الموظف', html, "Signature label 'توقيع الموظف' must be present")

    def test_28_bilingual_field_label_employee_name(self):
        """Bilingual label 'Employee Name' must also appear alongside the Arabic."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn('Employee Name', html)

    def test_29_bilingual_field_label_nationality(self):
        """Bilingual label 'Nationality' must also appear alongside the Arabic."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn('Nationality', html)

    # ==================================================================
    # 5 – Company header and branding
    # ==================================================================

    def test_30_company_name_in_header(self):
        """Company name must appear in the document header section."""
        html = self._render_html([self.employee_complete.id])
        self.assertIn(
            self.company.name, html,
            "Company name must be present in the rendered document"
        )

    def test_31_report_record_name_expression_references_employee_name(self):
        """
        print_report_name on the ir.actions.report record must reference
        object.name so the downloaded PDF filename is dynamic.
        """
        self.assertIn(
            'object.name', self.report_action.print_report_name,
            "print_report_name must use object.name for dynamic file naming"
        )

    def test_32_report_action_binding_model(self):
        """The report action must be bound to hr.employee."""
        self.assertEqual(
            self.report_action.model, 'hr.employee',
            "Report must be bound to hr.employee model"
        )

    def test_33_report_action_type_is_qweb_pdf(self):
        """The report action record must declare qweb-pdf type for official PDF output."""
        self.assertEqual(
            self.report_action.report_type, 'qweb-pdf',
            "report_type must be 'qweb-pdf'"
        )

    # ==================================================================
    # 6 – Permissions for HR users
    # ==================================================================

    def test_34_hr_manager_can_invoke_print_action(self):
        """
        An HR manager must be able to call action_print_work_commencement_notice
        and receive a valid report action dict.
        """
        # Use sudo with the manager user so the ORM enforces their ACL
        employee = self.employee_complete.with_user(self.hr_manager)
        action = employee.action_print_work_commencement_notice()
        self.assertEqual(
            action.get('type'), 'ir.actions.report',
            "HR manager must receive a valid report action"
        )

    def test_35_hr_user_can_invoke_print_action(self):
        """
        An HR officer (group_hr_user) must be able to call
        action_print_work_commencement_notice and receive a valid report action dict.
        """
        employee = self.employee_complete.with_user(self.hr_user)
        action = employee.action_print_work_commencement_notice()
        self.assertEqual(
            action.get('type'), 'ir.actions.report',
            "HR officer must receive a valid report action"
        )

    def test_36_hr_user_can_read_document_nationality_field(self):
        """
        document_nationality_id (groups='hr.group_hr_user') must be readable by
        an HR officer without raising an AccessError.
        """
        employee = self.employee_complete.with_user(self.hr_user)
        # Reading the field must not raise; truthy or falsy value is acceptable.
        nationality = employee.document_nationality_id
        self.assertIsNotNone(
            nationality,
            "document_nationality_id must be accessible to hr.group_hr_user (may be empty)"
        )

    def test_37_hr_user_can_read_document_id_iqama_field(self):
        """
        document_id_iqama (groups='hr.group_hr_user') must be readable by an
        HR officer without raising an AccessError.
        """
        employee = self.employee_complete.with_user(self.hr_user)
        iqama = employee.document_id_iqama
        # Field access returns a string (possibly empty); must not raise.
        self.assertIsNotNone(
            iqama,
            "document_id_iqama must be accessible to hr.group_hr_user"
        )

    def test_38_report_action_record_exists(self):
        """
        The XML ID hr_employee_document_prints.action_report_work_commencement_notice
        must resolve to an ir.actions.report record.
        """
        self.assertTrue(
            self.report_action,
            "Report action record must exist in the database"
        )
        self.assertEqual(self.report_action._name, 'ir.actions.report')

    # ==================================================================
    # 7 – Multiple employee records (batch / PDF output)
    # ==================================================================

    def test_39_batch_render_two_employees(self):
        """Report must render successfully for two employees in one call."""
        html = self._render_html([self.employee_complete.id, self.employee_partial.id])
        self.assertTrue(html.strip(), "Batch HTML rendering must not return empty content")
        self.assertIn(self.employee_complete.name, html)
        self.assertIn(self.employee_partial.name, html)

    def test_40_batch_render_three_employees(self):
        """Report must render successfully for three employees in one call."""
        ids = [
            self.employee_complete.id,
            self.employee_partial.id,
            self.employee_phone_fallback.id,
        ]
        html = self._render_html(ids)
        self.assertIn(self.employee_complete.name, html)
        self.assertIn(self.employee_partial.name, html)
        self.assertIn(self.employee_phone_fallback.name, html)

    def test_41_batch_render_four_employees(self):
        """Report must render correctly for four employees with mixed data coverage."""
        ids = [
            self.employee_complete.id,
            self.employee_partial.id,
            self.employee_phone_fallback.id,
            self.employee_egypt.id,
        ]
        html = self._render_html(ids)
        # All four names must appear exactly once per record page
        for emp_id, name in [
            (self.employee_complete.id, self.employee_complete.name),
            (self.employee_partial.id, self.employee_partial.name),
            (self.employee_phone_fallback.id, self.employee_phone_fallback.name),
            (self.employee_egypt.id, self.employee_egypt.name),
        ]:
            self.assertIn(
                name, html,
                f"Employee name '{name}' must be present in batch render output"
            )

    def test_42_each_employee_page_has_rtl_attribute(self):
        """
        When rendering multiple employees, every page div must carry the RTL
        direction attribute (one occurrence per employee is expected).
        """
        ids = [self.employee_complete.id, self.employee_partial.id]
        html = self._render_html(ids)
        count = html.count('dir="rtl"')
        self.assertGreaterEqual(
            count, 2,
            f"Expected at least 2 RTL page sections for 2 employees, found {count}"
        )

    def test_43_no_false_literals_in_batch_output(self):
        """
        Batch rendering with mixed-completeness records must never produce
        '>False<' or '>None<' in the HTML.
        """
        ids = [self.employee_complete.id, self.employee_partial.id, self.employee_egypt.id]
        html = self._render_html(ids)
        self.assertNotIn('>False<', html, "'False' literal must not appear in batch output")
        self.assertNotIn('>None<', html, "'None' literal must not appear in batch output")
