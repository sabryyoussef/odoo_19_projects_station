/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RecallDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            stats: {
                totalRecalls: 0,
                activeRecalls: 0,
                closedRecalls: 0,
                quarantinedStock: 0,
                affectedCustomers: 0,
                recallsByClass: {
                    class_i: 0,
                    class_ii: 0,
                    class_iii: 0,
                },
                recentRecalls: [],
                quarantineRecords: [],
            },
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        this.state.loading = true;
        try {
            // Get recall statistics
            const [totalRecalls, activeRecalls, closedRecalls] = await Promise.all([
                this.orm.searchCount("medtech.recall", []),
                this.orm.searchCount("medtech.recall", [["state", "=", "active"]]),
                this.orm.searchCount("medtech.recall", [["state", "=", "closed"]]),
            ]);

            // Get recalls by FDA class
            const classIRecalls = await this.orm.searchCount("medtech.recall", [
                ["classification", "=", "class_i"],
            ]);
            const classIIRecalls = await this.orm.searchCount("medtech.recall", [
                ["classification", "=", "class_ii"],
            ]);
            const classIIIRecalls = await this.orm.searchCount("medtech.recall", [
                ["classification", "=", "class_iii"],
            ]);

            // Get quarantined stock count
            const quarantinedStock = await this.orm.searchCount("medtech.quarantine", [
                ["state", "=", "quarantined"],
            ]);

            // Get affected customers count (from notifications)
            const affectedCustomers = await this.orm.call(
                "medtech.recall",
                "get_total_affected_customers",
                []
            ).catch(() => 0);

            // Get recent recalls
            const recentRecalls = await this.orm.searchRead(
                "medtech.recall",
                [],
                ["name", "initiation_date", "classification", "severity", "state", "total_manufactured"],
                {
                    limit: 10,
                    order: "initiation_date desc",
                }
            );

            // Get recent quarantine records
            const quarantineRecords = await this.orm.searchRead(
                "medtech.quarantine",
                [["state", "=", "quarantined"]],
                ["name", "product_id", "lot_id", "quantity", "quarantine_date", "reason"],
                {
                    limit: 10,
                    order: "quarantine_date desc",
                }
            );

            this.state.stats = {
                totalRecalls: totalRecalls,
                activeRecalls: activeRecalls,
                closedRecalls: closedRecalls,
                quarantinedStock: quarantinedStock,
                affectedCustomers: affectedCustomers,
                recallsByClass: {
                    class_i: classIRecalls,
                    class_ii: classIIRecalls,
                    class_iii: classIIIRecalls,
                },
                recentRecalls: recentRecalls,
                quarantineRecords: quarantineRecords,
            };
        } catch (error) {
            console.error("Error loading recall dashboard data:", error);
        } finally {
            this.state.loading = false;
        }
    }

    async viewAllRecalls() {
        this.action.doAction({
            name: "All Recalls",
            type: "ir.actions.act_window",
            res_model: "medtech.recall",
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });
    }

    async viewActiveRecalls() {
        this.action.doAction({
            name: "Active Recalls",
            type: "ir.actions.act_window",
            res_model: "medtech.recall",
            domain: [["state", "=", "active"]],
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });
    }

    async viewQuarantinedStock() {
        this.action.doAction({
            name: "Quarantined Stock",
            type: "ir.actions.act_window",
            res_model: "medtech.quarantine",
            domain: [["state", "=", "quarantined"]],
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });
    }

    async viewRecallsByClass(recallClass) {
        this.action.doAction({
            name: `Class ${recallClass.toUpperCase()} Recalls`,
            type: "ir.actions.act_window",
            res_model: "medtech.recall",
            domain: [["classification", "=", recallClass]],
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });
    }

    async openRecall(recallId) {
        this.action.doAction({
            name: "Recall Details",
            type: "ir.actions.act_window",
            res_model: "medtech.recall",
            res_id: recallId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    async openQuarantine(quarantineId) {
        this.action.doAction({
            name: "Quarantine Record",
            type: "ir.actions.act_window",
            res_model: "medtech.quarantine",
            res_id: quarantineId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    getSeverityBadgeClass(severity) {
        const severityMap = {
            critical: "badge-danger",
            high: "badge-warning",
            medium: "badge-info",
            low: "badge-secondary",
        };
        return severityMap[severity] || "badge-secondary";
    }

    getClassBadgeClass(fdaClass) {
        const classMap = {
            class_i: "badge-danger",
            class_ii: "badge-warning",
            class_iii: "badge-info",
        };
        return classMap[fdaClass] || "badge-secondary";
    }

    getStateBadgeClass(state) {
        const stateMap = {
            active: "badge-danger",
            monitoring: "badge-warning",
            closed: "badge-success",
        };
        return stateMap[state] || "badge-secondary";
    }
}

RecallDashboard.template = "medtech_recall.RecallDashboard";

registry.category("actions").add("medtech_recall.dashboard", RecallDashboard);
