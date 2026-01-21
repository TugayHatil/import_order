/** @odoo-module **/

import { registry } from "@web/core/registry";
import { env } from "@web/env";

/**
 * Client action to trigger the support popup.
 * In Odoo 16, function actions receive (action, options).
 * We use the global env to trigger the bus event.
 */
function openSupportPopupAction(action, options) {
    console.log("Support Quick Timesheet: Menu action triggered");

    // Trigger the event on the global bus
    if (env && env.bus) {
        env.bus.trigger("SUPPORT_POPUP:OPEN");
    }

    // Return an action that closes the current operation and remains on the same page
    return {
        type: "ir.actions.act_window_close",
    };
}

registry.category("actions").add("action_open_support_popup", openSupportPopupAction);
