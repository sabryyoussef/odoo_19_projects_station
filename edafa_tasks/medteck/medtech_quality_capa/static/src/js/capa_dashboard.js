/** @odoo-module **/

import { Component, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class CapaDashboard extends Component {
    static template = "medtech_quality_capa.CapaDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        
        this.state = {
            loading: true,
            stats: {
                totalCapas: 0,
                openCapas: 0,
                overdueCapas: 0,
                closedThisMonth: 0,
                avgTimeToClose: 0,
                effectivenessRate: 0,
            },
            capasByStage: {
                draft: 0,
                in_progress: 0,
                pending_approval: 0,
                approved: 0,
                effectiveness: 0,
                closed: 0,
            },
            overdueCAPAs: [],
            recentCAPAs: [],
            effectivenessChecksDue: [],
        };
        
        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        this.state.loading = true;
        
        try {
            // Load KPI metrics
            this.state.stats.totalCapas = await this.orm.searchCount("medtech.capa", []);
            this.state.stats.openCapas = await this.orm.searchCount("medtech.capa", [
                ["state", "not in", ["closed", "cancelled"]]
            ]);
            
            const today = new Date().toISOString().split('T')[0];
            this.state.stats.overdueCapas = await this.orm.searchCount("medtech.capa", [
                ["target_completion_date", "<", today],
                ["state", "not in", ["closed", "cancelled"]]
            ]);
            
            const firstDayOfMonth = new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0];
            this.state.stats.closedThisMonth = await this.orm.searchCount("medtech.capa", [
                ["stage", "=", "closed"],
                ["closed_date", ">=", firstDayOfMonth]
            ]);
            
            // Load stage breakdown
            this.state.capasByStage.draft = await this.orm.searchCount("medtech.capa", [["stage", "=", "draft"]]);
            this.state.capasByStage.in_progress = await this.orm.searchCount("medtech.capa", [["stage", "=", "in_progress"]]);
            this.state.capasByStage.pending_approval = await this.orm.searchCount("medtech.capa", [["stage", "=", "pending_approval"]]);
            this.state.capasByStage.approved = await this.orm.searchCount("medtech.capa", [["stage", "=", "approved"]]);
            this.state.capasByStage.effectiveness = await this.orm.searchCount("medtech.capa", [["stage", "=", "effectiveness"]]);
            this.state.capasByStage.closed = await this.orm.searchCount("medtech.capa", [["stage", "=", "closed"]]);
            
            // Load overdue CAPAs
            this.state.overdueCAPAs = await this.orm.searchRead(
                "medtech.capa",
                [
                    ["target_completion_date", "<", today],
                    ["state", "not in", ["closed", "cancelled"]]
                ],
                ["id", "name", "source", "severity", "state", "target_completion_date", "responsible_id"],
                { limit: 10, order: "target_completion_date asc" }
            );
            
            // Load recent CAPAs
            this.state.recentCAPAs = await this.orm.searchRead(
                "medtech.capa",
                [],
                ["id", "name", "source", "severity", "state", "create_date", "responsible_id"],
                { limit: 10, order: "create_date desc" }
            );
            
            // Load effectiveness checks due (CAPAs in effectiveness stage)
            this.state.effectivenessChecksDue = await this.orm.searchRead(
                "medtech.capa",
                [["stage", "=", "effectiveness"]],
                ["id", "name", "source", "effectiveness_check_date", "responsible_id"],
                { limit: 10, order: "effectiveness_check_date asc" }
            );
            
            // Calculate average time to close (simplified - would need server method for accuracy)
            this.state.stats.avgTimeToClose = 15; // Placeholder days
            this.state.stats.effectivenessRate = 92; // Placeholder percentage
            
        } catch (error) {
            console.error("Error loading CAPA dashboard data:", error);
        } finally {
            this.state.loading = false;
        }
    }

    // Action handlers
    viewAllCapas() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'medtech.capa',
            views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
            target: 'current',
        });
    }

    viewOpenCapas() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'medtech.capa',
            domain: [['state', 'not in', ['closed', 'cancelled']]],
            views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
            target: 'current',
        });
    }

    viewOverdueCapas() {
        const today = new Date().toISOString().split('T')[0];
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'medtech.capa',
            domain: [
                ['target_completion_date', '<', today],
                ['state', 'not in', ['closed', 'cancelled']]
            ],
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
        });
    }

    viewClosedThisMonth() {
        const firstDayOfMonth = new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0];
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'medtech.capa',
            domain: [
                ['state', '=', 'closed'],
                ['actual_completion_date', '>=', firstDayOfMonth]
            ],
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
        });
    }

    viewCapasByStage(stage) {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'medtech.capa',
            domain: [['state', '=', stage]],
            views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
            target: 'current',
        });
    }

    openCapa(capaId) {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'medtech.capa',
            res_id: capaId,
            views: [[false, 'form']],
            target: 'current',
        });
    }

    // Badge helper methods
    getPriorityBadgeClass(priority) {
        const priorityMap = {
            'low': 'badge-info',
            'medium': 'badge-warning',
            'high': 'badge-danger',
            'critical': 'badge-dark',
        };
        return priorityMap[priority] || 'badge-secondary';
    }

    getTypeBadgeClass(capaType) {
        const typeMap = {
            'corrective': 'badge-warning',
            'preventive': 'badge-info',
        };
        return typeMap[capaType] || 'badge-secondary';
    }

    getStateBadgeClass(state) {
        const stateMap = {
            'draft': 'badge-secondary',
            'in_progress': 'badge-primary',
            'pending_approval': 'badge-warning',
            'approved': 'badge-success',
            'effectiveness': 'badge-info',
            'closed': 'badge-success',
            'cancelled': 'badge-dark',
        };
        return stateMap[state] || 'badge-secondary';
    }

    calculateAgingDays(targetDate) {
        const today = new Date();
        const target = new Date(targetDate);
        const diffTime = today - target;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays;
    }
}

registry.category("actions").add("medtech_quality_capa.dashboard", CapaDashboard);
