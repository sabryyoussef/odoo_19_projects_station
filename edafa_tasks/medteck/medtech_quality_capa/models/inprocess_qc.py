# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MedTechInProcessQC(models.Model):
    _name = 'medtech.inprocess.qc'
    _description = 'In-Process QC'
    _inherit = ['medtech.audit.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    _audit_tracked_fields = ['state', 'result', 'checked_by_id', 'checked_at', 'check_type']

    name = fields.Char(string='QC Number', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), index=True)

    check_type = fields.Selection([
        ('weighing_dispensing', 'Weighing & Dispensing'),
        ('compounding', 'Compounding'),
        ('sterility', 'Sterility'),
        ('filling', 'Filling'),
        ('packaging', 'Packaging'),
    ], string='Check Type', required=True, default='weighing_dispensing', tracking=True)

    production_id = fields.Many2one('mrp.production', string='Manufacturing Order', required=True, tracking=True)
    weighing_batch_id = fields.Many2one('medtech.weighing.batch', string='Weighing Batch', tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ], string='State', default='draft', required=True, tracking=True, index=True)

    result = fields.Selection([
        ('pending', 'Pending'),
        ('pass', 'Pass'),
        ('fail', 'Fail'),
    ], string='Result', default='pending', required=True, tracking=True)

    checked_by_id = fields.Many2one('res.users', string='Checked By', tracking=True)
    checked_at = fields.Datetime(string='Checked At', tracking=True)
    notes = fields.Text(string='Notes', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medtech.inprocess.qc') or _('New')
        return super().create(vals_list)

    def action_pass(self):
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(_('Only draft checks can be marked passed.'))

        self.write({
            'state': 'passed',
            'result': 'pass',
            'checked_by_id': self.env.user.id,
            'checked_at': fields.Datetime.now(),
        })

        if self.weighing_batch_id:
            self.weighing_batch_id.state = 'qc_passed'
        if self.production_id:
            self.production_id.medtech_inprocess_qc_status = 'passed'
        return True

    def action_fail(self):
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(_('Only draft checks can be marked failed.'))

        self.write({
            'state': 'failed',
            'result': 'fail',
            'checked_by_id': self.env.user.id,
            'checked_at': fields.Datetime.now(),
        })

        if self.weighing_batch_id:
            self.weighing_batch_id.state = 'qc_failed'
        if self.production_id:
            self.production_id.medtech_inprocess_qc_status = 'failed'
        return True
