/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("actions").add("action_open_support_popup", (env, action) => {
    console.log("Client Action action_open_support_popup: Triggered");

    // Attempt to find the bus on env or recursively on action
    const targetEnv = env && env.bus ? env : (action && action.env ? action.env : null);

    if (targetEnv && targetEnv.bus) {
        console.log("Client Action: Bus found, triggering SUPPORT_POPUP:OPEN");
        targetEnv.bus.trigger("SUPPORT_POPUP:OPEN");
    } else {
        console.error("Support Popup Error: Could not find bus in environment. Printing args for debug:", { env, action });
        // Emergency fallback to searching the DOM for the root component env if possible
        // but typically env should be here.
    }
});
