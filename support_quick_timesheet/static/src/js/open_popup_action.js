/** @odoo-module **/

import { registry } from "@web/core/registry";

// Odoo 16 action handlers receive (env, action) or just (action) depending on caller
// We'll use a more robust way to capture the event bus.
registry.category("actions").add("action_open_support_popup", (env, action) => {
    // If env is not the first argument, action might be.
    // In most Odoo 16 contexts for client actions, env is passed.
    const targetEnv = env && env.bus ? env : (action && action.env ? action.env : null);

    if (targetEnv && targetEnv.bus) {
        targetEnv.bus.trigger("SUPPORT_POPUP:OPEN");
    } else {
        // Fallback to global odoo bus if needed, but standard env should work
        console.error("Support Popup Error: Could not find bus in environment.");
    }
});
