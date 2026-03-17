# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

class TestAuditTrail(TransactionCase):

    def setUp(self):
        super(TestAuditTrail, self).setUp()
        # We need a model to test the mixin. medtech.audit.event itself is a regular model.
        self.audit_model = self.env['medtech.audit.event']

    def test_00_audit_event_creation(self):
        """Test manual creation of audit events"""
        event = self.audit_model._create_audit_event(
            model='res.partner',
            res_id=1,
            operation='write',
            old_vals={'name': 'Old Name'},
            new_vals={'name': 'New Name'},
            context_info='Manual audit'
        )
        self.assertEqual(event.model, 'res.partner')
        self.assertEqual(event.res_id, 1)
        self.assertEqual(event.operation, 'write')
        self.assertIn('name', event.old_values)
        self.assertIn('New Name', event.new_values)
        self.assertEqual(event.context_info, 'Manual audit')

    def test_01_audit_summary_computation(self):
        """Test the computation of change summary"""
        event = self.audit_model.create({
            'model': 'res.partner',
            'res_id': 1,
            'operation': 'create',
        })
        self.assertEqual(event.change_summary, 'Record created')

        event_write = self.audit_model._create_audit_event(
            model='res.partner',
            res_id=1,
            operation='write',
            new_vals={'name': 'Test Partner', 'email': 'test@example.com'}
        )
        self.assertIn('name: Test Partner', event_write.change_summary)
        self.assertIn('email: test@example.com', event_write.change_summary)
