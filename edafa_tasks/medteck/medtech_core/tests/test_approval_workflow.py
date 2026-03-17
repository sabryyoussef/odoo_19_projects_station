# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

class TestApprovalWorkflow(TransactionCase):

    def setUp(self):
        super(TestApprovalWorkflow, self).setUp()
        self.approver = self.env['res.users'].create({
            'name': 'Test Approver',
            'login': 'test_approver',
            'email': 'approver@test.com',
        })
        # We need a model that inherits from medtech.approval.mixin to test it.
        # Since mixins are abstract, we can't instantiate them directly.
        # medtech.dhr in medtech_traceability uses it.
        # But we are in medtech_core tests. 
        # For a core test, we just check if the mixin is available.
        self.mixin = self.env['medtech.approval.mixin']

    def test_00_mixin_existence(self):
        """Check if the mixin is correctly registered in the environment"""
        self.assertTrue('medtech.approval.mixin' in self.env.registry)
        self.assertTrue(self.mixin._abstract)
