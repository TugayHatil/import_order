/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("actions").add("action_open_support_popup", (env, action) => {
    console.log("Client Action action_open_support_popup: Triggered");

    // In Odoo 16 client actions, 'env' is the first argument if it's a raw function action
    const targetBus = env && env.bus ? env.bus : null;

    if (targetBus) {
        console.log("Client Action: Global bus found, triggering SUPPORT_POPUP:OPEN");
        targetBus.trigger("SUPPORT_POPUP:OPEN");
    } else {
        console.error("Support Popup Error: Could not find bus in environment.");
        // Last resort: try to find it via global odoo object
        if (window.odoo && window.odoo.__WOWL_DEBUG__ && window.odoo.__WOWL_DEBUG__.root && window.odoo.__WOWL_DEBUG__.root.env) {
            console.log("Client Action: Found bus via WOWL_DEBUG fallback");
            window.odoo.__WOWL_DEBUG__.root.env.bus.trigger("SUPPORT_POPUP:OPEN");
        }
    }
});
