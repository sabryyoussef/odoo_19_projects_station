/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class TraceabilityDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            stats: {
                totalDevices: 0,
                totalUDIs: 0,
                totalDHRs: 0,
                devicesWithSerial: 0,
                devicesWithoutSerial: 0,
                recentTraceability: [],
            },
            selectedDHR: null,
            genealogyData: null,
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        this.state.loading = true;
        try {
            // Get statistics
            const [deviceCount, udiCount, dhrCount] = await Promise.all([
                this.orm.searchCount("product.template", [["is_medical_device", "=", true]]),
                this.orm.searchCount("medtech.udi", []),
                this.orm.searchCount("medtech.dhr", []),
            ]);

            // Get devices with and without serials
            const devicesWithSerial = await this.orm.searchCount("medtech.dhr", [
                ["serial_number", "!=", false],
            ]);
            const devicesWithoutSerial = dhrCount - devicesWithSerial;

            // Get recent DHRs for traceability
            const recentDHRs = await this.orm.searchRead(
                "medtech.dhr",
                [],
                ["name", "serial_number", "lot_number", "product_id", "manufacturing_date", "device_master_id"],
                {
                    limit: 10,
                    order: "create_date desc",
                }
            );

            this.state.stats = {
                totalDevices: deviceCount,
                totalUDIs: udiCount,
                totalDHRs: dhrCount,
                devicesWithSerial: devicesWithSerial,
                devicesWithoutSerial: devicesWithoutSerial,
                recentTraceability: recentDHRs,
            };
        } catch (error) {
            console.error("Error loading dashboard data:", error);
        } finally {
            this.state.loading = false;
        }
    }

    async viewDeviceMaster() {
        this.action.doAction({
            name: "Device Master Records",
            type: "ir.actions.act_window",
            res_model: "product.template",
            domain: [["is_medical_device", "=", true]],
            context: {default_is_medical_device: true},
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });
    }

    async viewUDIs() {
        this.action.doAction({
            name: "UDI Records",
            type: "ir.actions.act_window",
            res_model: "medtech.udi",
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });
    }

    async viewDHRs() {
        this.action.doAction({
            name: "Device History Records",
            type: "ir.actions.act_window",
            res_model: "medtech.dhr",
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });
    }

    async openDHR(dhrId) {
        this.action.doAction({
            name: "Device History Record",
            type: "ir.actions.act_window",
            res_model: "medtech.dhr",
            res_id: dhrId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    async traceGenealogy(dhrId) {
        this.state.selectedDHR = dhrId;
        try {
            // Call compute_genealogy_tree method on the DHR
            const genealogyData = await this.orm.call(
                "medtech.dhr",
                "compute_genealogy_tree",
                [dhrId]
            );
            this.state.genealogyData = genealogyData;
        } catch (error) {
            console.error("Error computing genealogy:", error);
            this.state.genealogyData = { error: "Failed to compute genealogy tree" };
        }
    }

    closeGenealogy() {
        this.state.selectedDHR = null;
        this.state.genealogyData = null;
    }

    renderGenealogyTree(data, level = 0) {
        if (!data || data.error) {
            return `<div class="text-danger">Error: ${data?.error || "Unknown error"}</div>`;
        }

        const indent = "&nbsp;&nbsp;&nbsp;&nbsp;".repeat(level);
        let html = `
            <div class="genealogy-node" style="margin-left: ${level * 20}px;">
                <i class="fa fa-microchip"></i>
                <strong>${data.name || "Unknown"}</strong>
                ${data.serial_number ? `(S/N: ${data.serial_number})` : ""}
                ${data.lot_number ? `(LOT: ${data.lot_number})` : ""}
            </div>
        `;

        if (data.components && data.components.length > 0) {
            data.components.forEach(component => {
                html += this.renderGenealogyTree(component, level + 1);
            });
        }

        return html;
    }
}

TraceabilityDashboard.template = "medtech_traceability.TraceabilityDashboard";

registry.category("actions").add("medtech_traceability.dashboard", TraceabilityDashboard);
