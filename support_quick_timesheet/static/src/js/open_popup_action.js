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

            // Trigger the event to open the main popup component
            this.env.bus.trigger("SUPPORT_POPUP:OPEN");

            // Critical: Avoid 'No controller to restore' error.
            // Instead of restore(), we use act_window_close to silently 'close' this action.
            // Odoo 16 will then stay on the previous view.
            if (this.env.services.action) {
                this.env.services.action.doAction("ir.actions.act_window_close");
            }
        });
    }
}
OpenSupportPopupAction.template = "support_quick_timesheet.OpenSupportPopupAction";

registry.category("actions").add("action_open_support_popup", OpenSupportPopupAction);
