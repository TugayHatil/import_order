/** @odoo-module **/

import { registry } from "@web/core/registry";

function openSupportPopup(env, action) {
    env.bus.trigger("SUPPORT_POPUP:OPEN");
}

registry.category("actions").add("action_open_support_popup", openSupportPopup);
