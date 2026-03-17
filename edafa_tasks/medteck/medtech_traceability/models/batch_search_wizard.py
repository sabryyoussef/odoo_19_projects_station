# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MedTechBatchSearchWizard(models.TransientModel):
    _name = 'medtech.batch.search.wizard'
    _description = 'Batch Search Wizard'

    search_lot_id = fields.Many2one('stock.lot', string='Lot to Search', required=True)

    mode = fields.Selection([
        ('backward', 'Backward (Finished Lot -> Raw Materials)'),
        ('forward', 'Forward (Raw/Finished Lot -> Customers)'),
    ], string='Traceability Mode', required=True, default='backward')

    result_text = fields.Text(string='Result', readonly=True)

    def action_run_search(self):
        self.ensure_one()
        service = self.env['medtech.traceability.query']

        if self.mode == 'backward':
            data = service.get_batch_backward_trace(self.search_lot_id.id)
            lines = [
                _('Lot: %s') % data.get('lot', '-'),
                _('Product: %s') % data.get('product', '-'),
                _('Manufacturing Order: %s') % data.get('manufacturing_order', '-'),
                _('Stage Records: %s') % ', '.join(data.get('stage_records', [])) if data.get('stage_records') else _('Stage Records: -'),
                _('Consumed Lots:'),
            ]
            consumed = data.get('consumed_lots', [])
            if consumed:
                lines.extend([f"- {item}" for item in consumed])
            else:
                lines.append('- -')
            self.result_text = '\n'.join(lines)
        else:
            data = service.get_batch_forward_trace(self.search_lot_id.id)
            lines = [
                _('Lot: %s') % data.get('lot', '-'),
                _('Product: %s') % data.get('product', '-'),
                _('Produced Lots:'),
            ]
            produced = data.get('produced_lots', [])
            if produced:
                lines.extend([f"- {item}" for item in produced])
            else:
                lines.append('- -')

            lines.append(_('Customers:'))
            customers = data.get('customers', [])
            if customers:
                lines.extend([f"- {item}" for item in customers])
            else:
                lines.append('- -')

            self.result_text = '\n'.join(lines)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Batch Search'),
            'res_model': 'medtech.batch.search.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
