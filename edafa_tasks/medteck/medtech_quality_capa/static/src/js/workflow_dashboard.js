/** @odoo-module **/

import { Component, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class WorkflowDashboard extends Component {
    static template = "medtech_quality_capa.WorkflowDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = {
            loading: true,
            kpi: {
                manufacturingOrders: 0,
                incomingQCOpen: 0,
                inProcessQCPending: 0,
                finalReleasePending: 0,
            },
            stages: {
                weighing: 0,
                compounding: 0,
                sterilization: 0,
                filling: 0,
                packaging: 0,
                finalRelease: 0,
            },
        };

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        this.state.loading = true;
        try {
            this.state.kpi.manufacturingOrders = await this.orm.searchCount("mrp.production", []);
            this.state.kpi.incomingQCOpen = await this.orm.searchCount("medtech.incoming.qc", [["state", "in", ["draft", "in_progress"]]]);
            this.state.kpi.inProcessQCPending = await this.orm.searchCount("medtech.inprocess.qc", [["state", "in", ["draft", "submitted"]]]);
            this.state.kpi.finalReleasePending = await this.orm.searchCount("medtech.final.release.batch", [["state", "in", ["draft", "pending_qa", "approved"]]]);

            this.state.stages.weighing = await this.orm.searchCount("medtech.weighing.batch", [["state", "not in", ["done", "cancelled"]]]);
            this.state.stages.compounding = await this.orm.searchCount("medtech.compounding.batch", [["state", "not in", ["moved", "cancelled"]]]);
            this.state.stages.sterilization = await this.orm.searchCount("medtech.sterilization.batch", [["state", "in", ["draft", "in_progress", "qc_failed", "qc_passed"]]]);
            this.state.stages.filling = await this.orm.searchCount("medtech.filling.batch", [["state", "in", ["draft", "in_progress", "qc_failed", "qc_passed"]]]);
            this.state.stages.packaging = await this.orm.searchCount("medtech.packaging.batch", [["state", "in", ["draft", "in_progress", "qc_failed", "qc_passed"]]]);
            this.state.stages.finalRelease = await this.orm.searchCount("medtech.final.release.batch", [["state", "in", ["draft", "pending_qa", "approved"]]]);
        } catch (error) {
            console.error("Workflow dashboard load error", error);
        } finally {
            this.state.loading = false;
        }
    }

    openWizard() {
        this.action.doAction("medtech_quality_capa.action_medtech_full_workflow_wizard");
    }

    openModel(model, domain = []) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: model,
            domain,
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("medtech_quality_capa.workflow_dashboard", WorkflowDashboard);
