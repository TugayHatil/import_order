/** @odoo-module **/

import { registry } from "@web/core/registry";

function openSupportPopup(parent, action) {
    const bus = parent.env.bus;
    bus.trigger("SUPPORT_POPUP:OPEN");
}

registry.category("actions").add("action_open_support_popup", openSupportPopup);
