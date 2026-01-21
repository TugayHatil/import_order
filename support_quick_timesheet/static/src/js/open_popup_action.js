/** @odoo-module **/

import { Component, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";

/**
 * Empty component that triggers the support popup when activated as a client action.
 */
class OpenSupportPopupAction extends Component {
    setup() {
        onMounted(() => {
            console.log("OpenSupportPopupAction: Mounted, triggering event");
            this.env.bus.trigger("SUPPORT_POPUP:OPEN");
            // Also try dispatching standard event if trigger fails for some reason
            this.env.bus.dispatchEvent(new CustomEvent("SUPPORT_POPUP:OPEN"));

            // Go back in history or close the current action if possible
            // But usually we just want to stay on the current page while the popup opens
            if (this.env.services.action) {
                this.env.services.action.restore();
            }
        });
    }
}
OpenSupportPopupAction.template = "support_quick_timesheet.OpenSupportPopupAction";

registry.category("actions").add("action_open_support_popup", OpenSupportPopupAction);
