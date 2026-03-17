/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";

class ErrorReportSystray extends Component {
    static template = "error_reporter_enterprise.ErrorReportSystray";

    setup() {
        this.action = useService("action");
    }

    onClick() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "error.report",
            name: "Error Reports",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            target: "current",
            context: {
                search_default_filter_new: 1,
            },
        });
    }
}

registry.category("systray").add(
    "error_reporter_enterprise.ErrorReportSystray",
    {
        Component: ErrorReportSystray,
        sequence: 50,
    }
);

