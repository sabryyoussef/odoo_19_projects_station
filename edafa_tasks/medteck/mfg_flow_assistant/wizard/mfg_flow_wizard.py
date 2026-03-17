from odoo import Command, api, fields, models, _
from odoo.exceptions import UserError


class MfgFlowWizard(models.TransientModel):
    _name = "mfg.flow.wizard"
    _description = "Manufacturing Flow Assistant"

    product_id = fields.Many2one("product.product", string="Final Product", domain="[('type','in',('consu','product'))]")
    bom_id = fields.Many2one("mrp.bom", string="Bill of Materials", readonly=True)
    production_id = fields.Many2one("mrp.production", string="Manufacturing Order", readonly=True)
    step_state = fields.Selection([
        ("components", "Step 1: Components"), ("bom", "Step 2: BoM"), ("mo", "Step 3: Manufacturing Order"),
        ("workorders", "Step 4: Work Orders"), ("quality", "Step 5: Quality"), ("produce", "Step 6: Produce"),
        ("stock_review", "Step 7: Stock Review"), ("traceability", "Step 8: Traceability"),
        ("capa", "Step 9: CAPA"), ("recall_field", "Step 10: Recall & Field"),
    ], default="components", required=True)

    instruction_html = fields.Html(compute="_compute_instruction_html")
    component_status = fields.Selection([("no_product", "No Product"), ("no_bom", "No BoM"), ("no_components", "No Components"), ("missing_stock", "Missing Stock"), ("ready", "Ready")], compute="_compute_status_fields")
    bom_status = fields.Selection([("no_product", "No Product"), ("no_bom", "No BoM"), ("bom_found", "BoM Found")], compute="_compute_status_fields")
    mo_status = fields.Selection([("no_product", "No Product"), ("no_bom", "No BoM"), ("no_mo", "No MO"), ("mo_found", "MO Found")], compute="_compute_status_fields")
    workorder_status = fields.Selection([("no_mo", "No MO"), ("no_workorders", "No WOs"), ("wo_ready", "WO Ready"), ("wo_in_progress", "WO In Progress"), ("wo_done", "WO Done")], compute="_compute_status_fields")
    quality_status = fields.Selection([("no_mo", "No MO"), ("no_checks", "No Checks"), ("checks_pending", "Pending"), ("checks_passed", "Passed"), ("checks_failed", "Failed")], compute="_compute_status_fields")
    produce_status = fields.Selection([("no_mo", "No MO"), ("not_started", "Not Started"), ("in_progress", "In Progress"), ("ready_to_close", "Ready To Close"), ("done", "Done")], compute="_compute_status_fields")
    stock_review_status = fields.Selection([("no_mo", "No MO"), ("no_moves", "No Moves"), ("waiting_transfer", "Waiting"), ("completed", "Completed")], compute="_compute_status_fields")
    traceability_status = fields.Selection([("no_mo", "No MO"), ("no_serials", "No Serials"), ("no_dhr", "No DHR"), ("dhr_ready", "DHR Ready")], compute="_compute_status_fields")
    capa_status = fields.Selection([("no_records", "No Records"), ("nonconformance_open", "NC Open"), ("capa_open", "CAPA Open"), ("closed", "Closed")], compute="_compute_status_fields")
    recall_status = fields.Selection([("no_recall", "No Recall"), ("candidate", "Candidate"), ("active", "Active"), ("closed", "Closed")], compute="_compute_status_fields")
    field_service_status = fields.Selection([("no_service", "No Service"), ("visits_open", "Open Visits"), ("visits_done", "Visits Done")], compute="_compute_status_fields")

    component_line_ids = fields.One2many("mfg.flow.wizard.line", "wizard_id")
    workorder_ids = fields.Many2many("mrp.workorder", compute="_compute_status_fields")
    quality_check_ids = fields.Many2many("quality.check", compute="_compute_status_fields")
    raw_move_ids = fields.Many2many("stock.move", compute="_compute_status_fields")
    finished_move_ids = fields.Many2many("stock.move", compute="_compute_status_fields")
    serial_lot_ids = fields.Many2many("stock.lot", compute="_compute_status_fields")
    dhr_ids = fields.Many2many("medtech.dhr", compute="_compute_status_fields")
    nonconformance_ids = fields.Many2many("medtech.nonconformance", compute="_compute_status_fields")
    capa_ids = fields.Many2many("medtech.capa", compute="_compute_status_fields")
    recall_ids = fields.Many2many("medtech.recall", compute="_compute_status_fields")
    service_visit_ids = fields.Many2many("medtech.service.visit", compute="_compute_status_fields")

    component_count = fields.Integer(compute="_compute_status_fields")
    operation_count = fields.Integer(compute="_compute_status_fields")
    workorder_count = fields.Integer(compute="_compute_status_fields")
    quality_check_count = fields.Integer(compute="_compute_status_fields")
    raw_move_count = fields.Integer(compute="_compute_status_fields")
    finished_move_count = fields.Integer(compute="_compute_status_fields")
    serial_lot_count = fields.Integer(compute="_compute_status_fields")
    dhr_count = fields.Integer(compute="_compute_status_fields")
    nonconformance_count = fields.Integer(compute="_compute_status_fields")
    capa_count = fields.Integer(compute="_compute_status_fields")
    recall_count = fields.Integer(compute="_compute_status_fields")
    service_visit_count = fields.Integer(compute="_compute_status_fields")
    is_ready_for_next_step = fields.Boolean(compute="_compute_status_fields")
    is_first_step = fields.Boolean(compute="_compute_navigation_flags")
    is_last_step = fields.Boolean(compute="_compute_navigation_flags")
    current_stage_status = fields.Char(compute="_compute_current_stage_status")

    def _step_sequence(self):
        return [
            "components",
            "bom",
            "mo",
            "workorders",
            "quality",
            "produce",
            "stock_review",
            "traceability",
            "capa",
            "recall_field",
        ]

    @api.depends("step_state")
    def _compute_instruction_html(self):
        m = {
            "components": "Step 1: Validate components from BoM.",
            "bom": "Step 2: Open/Create BoM.",
            "mo": "Step 3: Open/Create MO.",
            "workorders": "Step 4: Execute work orders.",
            "quality": "Step 5: Process quality checks.",
            "produce": "Step 6: Produce and close MO.",
            "stock_review": "Step 7: Review stock moves.",
            "traceability": "Step 8: Review/create DHR.",
            "capa": "Step 9: Create/open NC and CAPA.",
            "recall_field": "Step 10: Recall candidates and field history.",
        }
        for r in self:
            r.instruction_html = "<p><strong>%s</strong></p>" % m.get(r.step_state, "")

    @api.depends("step_state")
    def _compute_navigation_flags(self):
        seq = self._step_sequence()
        first = seq[0]
        last = seq[-1]
        for rec in self:
            rec.is_first_step = rec.step_state == first
            rec.is_last_step = rec.step_state == last

    @api.depends(
        "step_state",
        "component_status",
        "bom_status",
        "mo_status",
        "workorder_status",
        "quality_status",
        "produce_status",
        "stock_review_status",
        "traceability_status",
        "capa_status",
        "recall_status",
        "field_service_status",
    )
    def _compute_current_stage_status(self):
        field_by_step = {
            "components": "component_status",
            "bom": "bom_status",
            "mo": "mo_status",
            "workorders": "workorder_status",
            "quality": "quality_status",
            "produce": "produce_status",
            "stock_review": "stock_review_status",
            "traceability": "traceability_status",
            "capa": "capa_status",
            "recall_field": "recall_status",
        }
        for rec in self:
            status_field = field_by_step.get(rec.step_state)
            if not status_field:
                rec.current_stage_status = "-"
                continue
            value = rec[status_field]
            selection = dict(rec._fields[status_field].selection)
            rec.current_stage_status = selection.get(value, "-")

    @api.depends("product_id", "bom_id", "production_id", "production_id.state", "production_id.workorder_ids.state", "production_id.move_raw_ids.state", "production_id.move_finished_ids.state")
    def _compute_status_fields(self):
        for r in self:
            # Always initialize computed fields to avoid missing assignment errors.
            r.component_status = "no_product"
            r.bom_status = "no_product"
            r.mo_status = "no_product"
            r.workorder_status = "no_mo"
            r.quality_status = "no_mo"
            r.produce_status = "no_mo"
            r.stock_review_status = "no_mo"
            r.traceability_status = "no_mo"
            r.capa_status = "no_records"
            r.recall_status = "no_recall"
            r.field_service_status = "no_service"
            r.is_ready_for_next_step = False

            r.component_count = len(r.component_line_ids)
            r.operation_count = len(r.bom_id.operation_ids)
            r.workorder_ids = r.production_id.workorder_ids
            r.workorder_count = len(r.workorder_ids)
            mo_checks = r.production_id.check_ids.filtered(lambda c: not c.workorder_id)
            wo_checks = r.production_id.workorder_ids.mapped("check_ids")
            r.quality_check_ids = mo_checks | wo_checks
            r.quality_check_count = len(r.quality_check_ids)
            r.raw_move_ids = r.production_id.move_raw_ids
            r.finished_move_ids = r.production_id.move_finished_ids
            r.raw_move_count = len(r.raw_move_ids)
            r.finished_move_count = len(r.finished_move_ids)
            r.serial_lot_ids = (r.production_id.move_finished_ids.move_line_ids.mapped("lot_id") | r.production_id.lot_producing_ids) if r.production_id else self.env["stock.lot"]
            r.serial_lot_count = len(r.serial_lot_ids)
            r.dhr_ids = self.env["medtech.dhr"].search([("serial_lot_id", "in", r.serial_lot_ids.ids)]) if r.serial_lot_ids else self.env["medtech.dhr"]
            r.nonconformance_ids = self.env["medtech.nonconformance"].search([("affected_product_ids", "in", r.product_id.ids)]) if r.product_id else self.env["medtech.nonconformance"]
            r.capa_ids = self.env["medtech.capa"].search([("affected_product_ids", "in", r.product_id.ids)]) if r.product_id else self.env["medtech.capa"]
            r.recall_ids = self.env["medtech.recall"].search([("affected_product_ids", "in", r.product_id.ids)]) if r.product_id else self.env["medtech.recall"]
            r.service_visit_ids = self.env["medtech.service.visit"].search([("device_serial_id", "in", r.serial_lot_ids.ids)]) if r.serial_lot_ids else self.env["medtech.service.visit"]
            r.dhr_count = len(r.dhr_ids); r.nonconformance_count = len(r.nonconformance_ids); r.capa_count = len(r.capa_ids); r.recall_count = len(r.recall_ids); r.service_visit_count = len(r.service_visit_ids)

            if not r.product_id:
                continue
            if not r.bom_id:
                r.component_status = "no_bom"; r.bom_status = "no_bom"; r.mo_status = "no_bom"
                r.workorder_status = "no_mo"; r.quality_status = "no_mo"; r.produce_status = "no_mo"; r.stock_review_status = "no_mo"; r.traceability_status = "no_mo"
                r.is_ready_for_next_step = False
            else:
                r.bom_status = "bom_found"; r.mo_status = "mo_found" if r.production_id else "no_mo"
                r.component_status = "no_components" if not r.component_line_ids else ("missing_stock" if any(l.short_qty > 0 for l in r.component_line_ids) else "ready")
                r.is_ready_for_next_step = r.component_status == "ready"
                if not r.workorder_ids: r.workorder_status = "no_workorders"
                elif any(w.state == "progress" for w in r.workorder_ids): r.workorder_status = "wo_in_progress"
                elif any(w.state in ("ready", "blocked") for w in r.workorder_ids): r.workorder_status = "wo_ready"
                else: r.workorder_status = "wo_done"
                if not r.quality_check_ids: r.quality_status = "no_checks"
                elif any(q.quality_state == "none" for q in r.quality_check_ids): r.quality_status = "checks_pending"
                elif any(q.quality_state == "fail" for q in r.quality_check_ids): r.quality_status = "checks_failed"
                else: r.quality_status = "checks_passed"
                if not r.production_id: r.produce_status = "no_mo"
                elif r.production_id.state == "done": r.produce_status = "done"
                elif r.production_id.state in ("draft", "confirmed", "cancel"): r.produce_status = "not_started"
                elif r.production_id.state == "to_close": r.produce_status = "ready_to_close"
                else: r.produce_status = "in_progress"
                all_moves = r.raw_move_ids | r.finished_move_ids
                if not all_moves: r.stock_review_status = "no_moves"
                elif any(m.state not in ("done", "cancel") for m in all_moves): r.stock_review_status = "waiting_transfer"
                else: r.stock_review_status = "completed"
                r.traceability_status = "no_serials" if not r.serial_lot_ids else ("no_dhr" if not r.dhr_ids else "dhr_ready")
                if not r.nonconformance_ids and not r.capa_ids: r.capa_status = "no_records"
                elif r.capa_ids and any(c.stage not in ("closed", "cancelled") for c in r.capa_ids): r.capa_status = "capa_open"
                elif r.nonconformance_ids and not r.capa_ids: r.capa_status = "nonconformance_open"
                else: r.capa_status = "closed"
                if not r.recall_ids: r.recall_status = "candidate" if r.capa_ids else "no_recall"
                elif any(rc.state == "active" for rc in r.recall_ids): r.recall_status = "active"
                elif all(rc.state in ("closed", "cancelled") for rc in r.recall_ids): r.recall_status = "closed"
                else: r.recall_status = "candidate"
                if not r.service_visit_ids: r.field_service_status = "no_service"
                elif any(v.state not in ("completed", "cancelled") for v in r.service_visit_ids): r.field_service_status = "visits_open"
                else: r.field_service_status = "visits_done"

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for r in self:
            r._sync_selected_product_data()

    def _sync_selected_product_data(self):
        self.ensure_one()
        if not self.product_id:
            self.update({"bom_id": False, "production_id": False, "component_line_ids": [Command.clear()]})
            return
        bom = self.env["mrp.bom"].search([("product_id", "=", self.product_id.id)], limit=1) or self.env["mrp.bom"].search([("product_tmpl_id", "=", self.product_id.product_tmpl_id.id), ("product_id", "=", False)], limit=1)
        self.bom_id = bom
        self.production_id = self.env["mrp.production"].search([("product_id", "=", self.product_id.id), ("state", "not in", ("done", "cancel"))], order="id desc", limit=1)
        lines = [Command.clear()]
        if bom:
            for l in bom.bom_line_ids:
                avail = l.product_id.qty_available
                lines.append(Command.create({"product_id": l.product_id.id, "product_uom_id": l.product_uom_id.id, "required_qty": l.product_qty, "on_hand_qty": avail, "short_qty": max(l.product_qty - avail, 0.0), "is_available": avail >= l.product_qty}))
        self.component_line_ids = lines

    def _open_self(self, step=None):
        self.ensure_one()
        if step:
            self.step_state = step
        return {"type": "ir.actions.act_window", "name": _("Manufacturing Flow Assistant"), "res_model": "mfg.flow.wizard", "view_mode": "form", "res_id": self.id, "target": "current"}

    def action_go_to_components(self): return self._open_self("components")
    def action_go_to_bom(self): return self._open_self("bom")
    def action_go_to_mo(self): return self._open_self("mo")
    def action_go_to_workorders(self): return self._open_self("workorders")
    def action_go_to_quality(self): return self._open_self("quality")
    def action_go_to_produce(self): return self._open_self("produce")
    def action_go_to_stock_review(self): return self._open_self("stock_review")
    def action_go_to_traceability(self): return self._open_self("traceability")
    def action_go_to_capa(self): return self._open_self("capa")
    def action_go_to_recall_field(self): return self._open_self("recall_field")

    def action_previous_step(self):
        self.ensure_one()
        seq = self._step_sequence()
        idx = seq.index(self.step_state)
        if idx == 0:
            return self._open_self(seq[0])
        return self._open_self(seq[idx - 1])

    def action_next_step(self):
        self.ensure_one()
        seq = self._step_sequence()
        idx = seq.index(self.step_state)
        if idx >= len(seq) - 1:
            return self._open_self(seq[-1])
        return self._open_self(seq[idx + 1])

    def action_open_bom(self):
        self.ensure_one()
        if not self.bom_id: raise UserError(_("No BoM found."))
        return {"type": "ir.actions.act_window", "res_model": "mrp.bom", "view_mode": "form", "res_id": self.bom_id.id, "target": "current"}

    def action_open_product(self):
        self.ensure_one()
        if not self.product_id:
            raise UserError(_("Select a final product first."))
        return {"type": "ir.actions.act_window", "res_model": "product.product", "view_mode": "form", "res_id": self.product_id.id, "target": "current"}

    def action_create_final_product(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.product",
            "view_mode": "form",
            "target": "current",
            "context": {"default_type": "product", "default_sale_ok": False, "default_purchase_ok": True},
        }

    def action_create_bom(self):
        self.ensure_one()
        if not self.product_id: raise UserError(_("Select product first."))
        return {"type": "ir.actions.act_window", "res_model": "mrp.bom", "view_mode": "form", "target": "current", "context": {"default_product_tmpl_id": self.product_id.product_tmpl_id.id, "default_product_id": self.product_id.id, "default_product_qty": 1.0}}

    def action_create_component_product(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.product",
            "view_mode": "form",
            "target": "current",
            "context": {"default_type": "product", "default_sale_ok": False, "default_purchase_ok": True},
        }

    def action_refresh_components(self):
        self.ensure_one()
        self._sync_selected_product_data()
        return self._open_self("components")

    def action_open_mo(self):
        self.ensure_one()
        if not self.production_id: raise UserError(_("No MO found."))
        return {"type": "ir.actions.act_window", "res_model": "mrp.production", "view_mode": "form", "res_id": self.production_id.id, "target": "current"}

    def action_create_mo(self):
        self.ensure_one()
        if not self.product_id or not self.bom_id: raise UserError(_("Select product and BoM first."))
        mo = self.env["mrp.production"].create({"product_id": self.product_id.id, "product_uom_id": self.product_id.uom_id.id, "product_qty": 1.0, "bom_id": self.bom_id.id, "origin": _("Created from Manufacturing Flow Assistant")})
        self.production_id = mo
        return self.action_open_mo()

    def action_open_mo_workorders(self): return {"type": "ir.actions.act_window", "res_model": "mrp.workorder", "view_mode": "list,form", "domain": [("id", "in", self.workorder_ids.ids)] if self.workorder_ids else [("id", "=", 0)], "target": "current"}
    def action_open_quality_checks(self): return {"type": "ir.actions.act_window", "res_model": "quality.check", "view_mode": "list,form", "domain": [("id", "in", self.quality_check_ids.ids)] if self.quality_check_ids else [("id", "=", 0)], "target": "current"}
    def action_open_raw_moves(self): return {"type": "ir.actions.act_window", "res_model": "stock.move", "view_mode": "list,form", "domain": [("id", "in", self.raw_move_ids.ids)] if self.raw_move_ids else [("id", "=", 0)], "target": "current"}
    def action_open_finished_moves(self): return {"type": "ir.actions.act_window", "res_model": "stock.move", "view_mode": "list,form", "domain": [("id", "in", self.finished_move_ids.ids)] if self.finished_move_ids else [("id", "=", 0)], "target": "current"}
    def action_open_dhr_records(self): return {"type": "ir.actions.act_window", "res_model": "medtech.dhr", "view_mode": "list,form", "domain": [("id", "in", self.dhr_ids.ids)] if self.dhr_ids else [("id", "=", 0)], "target": "current"}
    def action_open_nonconformances(self): return {"type": "ir.actions.act_window", "res_model": "medtech.nonconformance", "view_mode": "list,form", "domain": [("id", "in", self.nonconformance_ids.ids)] if self.nonconformance_ids else [("id", "=", 0)], "target": "current"}
    def action_open_capas(self): return {"type": "ir.actions.act_window", "res_model": "medtech.capa", "view_mode": "list,form", "domain": [("id", "in", self.capa_ids.ids)] if self.capa_ids else [("id", "=", 0)], "target": "current"}
    def action_open_recalls(self): return {"type": "ir.actions.act_window", "res_model": "medtech.recall", "view_mode": "list,form", "domain": [("id", "in", self.recall_ids.ids)] if self.recall_ids else [("id", "=", 0)], "target": "current"}
    def action_open_service_visits(self): return {"type": "ir.actions.act_window", "res_model": "medtech.service.visit", "view_mode": "list,form", "domain": [("id", "in", self.service_visit_ids.ids)] if self.service_visit_ids else [("id", "=", 0)], "target": "current"}

    def action_validate_components(self):
        self.ensure_one()
        msg = _("Components are ready.") if self.component_status == "ready" else _("Component validation completed.")
        return {"type": "ir.actions.client", "tag": "display_notification", "params": {"title": _("Validation"), "message": msg, "type": "success" if self.component_status == "ready" else "warning", "sticky": False}}

    def action_start_first_workorder(self):
        self.ensure_one()
        candidate = self.workorder_ids.filtered(lambda w: w.state == "ready")[:1] or self.workorder_ids.filtered(lambda w: w.state == "blocked")[:1]
        if not candidate:
            raise UserError(_("No startable work order found."))
        candidate.button_start()
        return {"type": "ir.actions.act_window", "res_model": "mrp.workorder", "view_mode": "form", "res_id": candidate.id, "target": "current"}

    def action_pass_first_pending_quality_check(self):
        self.ensure_one()
        check = self.quality_check_ids.filtered(lambda c: c.quality_state == "none")[:1]
        if not check:
            raise UserError(_("No pending quality checks found."))
        check.do_pass()
        return {"type": "ir.actions.act_window", "res_model": "quality.check", "view_mode": "form", "res_id": check.id, "target": "current"}

    def action_open_produce_mo(self):
        return self.action_open_mo()

    def action_set_qty_to_produce(self):
        self.ensure_one()
        if not self.production_id:
            raise UserError(_("Create or select a Manufacturing Order first."))
        remaining = max(self.production_id.product_qty - self.production_id.qty_produced, 0.0)
        self.production_id.qty_producing = remaining
        return self._open_self("produce")

    def action_mark_mo_done(self):
        self.ensure_one()
        if not self.production_id:
            raise UserError(_("Create or select a Manufacturing Order first."))
        return self.production_id.button_mark_done()

    def action_create_dhr_from_mo(self):
        self.ensure_one()
        if not self.production_id:
            raise UserError(_("Create or select a Manufacturing Order first."))
        lot = self.serial_lot_ids[:1]
        if not lot:
            raise UserError(_("No produced serial/lot found on this MO."))
        dhr = self.env["medtech.dhr"].search([("serial_lot_id", "=", lot.id), ("production_order_id", "=", self.production_id.id)], limit=1)
        if not dhr:
            dhr = self.env["medtech.dhr"].create({"serial_lot_id": lot.id, "production_order_id": self.production_id.id, "device_master_id": self.product_id.product_tmpl_id.id})
        return {"type": "ir.actions.act_window", "res_model": "medtech.dhr", "view_mode": "form", "res_id": dhr.id, "target": "current"}

    def action_create_nonconformance_from_mo(self):
        self.ensure_one()
        if not self.product_id:
            raise UserError(_("Select a product first."))
        nc = self.env["medtech.nonconformance"].create({
            "source": "manufacturing",
            "severity": "medium",
            "description": _("Nonconformance created from Manufacturing Flow Assistant for %s") % self.product_id.display_name,
            "affected_product_ids": [(6, 0, [self.product_id.id])],
            "affected_lot_ids": [(6, 0, self.serial_lot_ids.ids)] if self.serial_lot_ids else False,
        })
        return {"type": "ir.actions.act_window", "res_model": "medtech.nonconformance", "view_mode": "form", "res_id": nc.id, "target": "current"}

    def action_create_capa_from_nonconformance(self):
        self.ensure_one()
        nc = self.nonconformance_ids[:1]
        if not nc:
            raise UserError(_("Create/open a nonconformance first."))
        capa = self.env["medtech.capa"].create({
            "source": "nonconformance",
            "description": _("CAPA generated from NC %s") % nc.name,
            "nonconformance_ids": [(4, nc.id)],
            "affected_product_ids": [(6, 0, [self.product_id.id])] if self.product_id else False,
            "affected_serial_lot_ids": [(6, 0, self.serial_lot_ids.ids)] if self.serial_lot_ids else False,
            "action_plan": _("Investigate root cause and implement corrective/preventive actions."),
            "target_completion_date": fields.Date.today(),
            "responsible_id": self.env.user.id,
        })
        return {"type": "ir.actions.act_window", "res_model": "medtech.capa", "view_mode": "form", "res_id": capa.id, "target": "current"}

    def action_create_recall_candidate(self):
        self.ensure_one()
        if not self.product_id:
            raise UserError(_("Select a product first."))
        vals = {
            "classification": "class_ii",
            "severity": "high",
            "recall_type": "quality",
            "trigger_source": "capa",
            "description": _("Recall candidate from Manufacturing Flow Assistant for %s") % self.product_id.display_name,
            "affected_determination": "by_lot" if self.serial_lot_ids else "by_product",
            "affected_product_ids": [(6, 0, [self.product_id.id])],
        }
        if self.serial_lot_ids:
            vals["affected_lot_ids"] = [(6, 0, self.serial_lot_ids.ids)]
        recall = self.env["medtech.recall"].create(vals)
        return {"type": "ir.actions.act_window", "res_model": "medtech.recall", "view_mode": "form", "res_id": recall.id, "target": "current"}


class MfgFlowWizardLine(models.TransientModel):
    _name = "mfg.flow.wizard.line"
    _description = "Manufacturing Flow Assistant Line"

    wizard_id = fields.Many2one("mfg.flow.wizard", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.product", string="Component", readonly=True)
    product_uom_id = fields.Many2one("uom.uom", string="UoM", readonly=True)
    required_qty = fields.Float(string="Required Qty", readonly=True)
    on_hand_qty = fields.Float(string="On Hand", readonly=True)
    short_qty = fields.Float(string="Short Qty", readonly=True)
    is_available = fields.Boolean(string="Available", readonly=True)

    def action_open_component(self):
        self.ensure_one()
        return {"type": "ir.actions.act_window", "res_model": "product.product", "view_mode": "form", "res_id": self.product_id.id, "target": "current"}
