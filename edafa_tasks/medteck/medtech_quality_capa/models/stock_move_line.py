# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.constrains('lot_id', 'move_id')
    def _check_quarantine_lot_for_mrp_consumption(self):
        for line in self:
            if not line.lot_id or not line.move_id:
                continue

            move = line.move_id
            if 'raw_material_production_id' not in move._fields:
                continue

            if not move.raw_material_production_id:
                continue

            if line.lot_id.medtech_qc_status != 'released':
                raise ValidationError(_(
                    'Lot %(lot)s cannot be consumed in manufacturing because its QC status is %(status)s. '
                    'Only QC Released lots are allowed.'
                ) % {
                    'lot': line.lot_id.name,
                    'status': dict(line.lot_id._fields['medtech_qc_status'].selection).get(line.lot_id.medtech_qc_status, 'Unknown'),
                })
