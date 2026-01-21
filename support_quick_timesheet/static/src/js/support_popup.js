/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

setup() {
    this.notification = useService("notification");
    this.rpc = useService("rpc");
    this.state = useState({
        isVisible: false,
        isCollapsed: false,
        isProcessing: false,
        partnerId: "",
        typeId: "",
        contactPerson: "",
    });
    this.data = useState({
        partners: [],
        types: [],
        slots: [],
    });

    onWillStart(async () => {
        try {
            await this.loadData();
        } catch (e) {
            console.error("SupportPopup: Failed to load initial data", e);
        }
    });

    // Use the bus service correctly in Odoo 16
    // Some v16 versions use addEventListener on the bus instance
    const openHandler = () => {
        console.log("SupportPopup: Handling OPEN event");
        this.openPopup();
    };

    this.env.bus.addEventListener("SUPPORT_POPUP:OPEN", openHandler);
}

    async loadData() {
    const result = await this.rpc("/web/dataset/call_kw/support.manager/get_support_data", {
        model: 'support.manager',
        method: 'get_support_data',
        args: [],
        kwargs: {},
    });
    this.data.partners = result.partners;
    this.data.types = result.types;
    this.data.slots = result.slots;
}

toggleCollapse() {
    this.state.isCollapsed = !this.state.isCollapsed;
}

closePopup() {
    this.state.isVisible = false;
}

openPopup() {
    this.state.isVisible = true;
    this.state.isCollapsed = false;
}

    async createTimesheet(slotId) {
    if (!this.state.partnerId || !this.state.typeId || !this.state.contactPerson) {
        this.notification.add("Lütfen tüm alanları doldurunuz.", { type: "danger" });
        return;
    }

    this.state.isProcessing = true;
    try {
        const result = await this.rpc("/web/dataset/call_kw/support.manager/create_timesheet", {
            model: 'support.manager',
            method: 'create_timesheet',
            args: [
                parseInt(this.state.partnerId),
                parseInt(this.state.typeId),
                this.state.contactPerson,
                parseInt(slotId)
            ],
            kwargs: {},
        });

        if (result.status === 'success') {
            this.notification.add("Timesheet başarıyla oluşturuldu.", { type: "success" });
            // Reset fields
            this.state.contactPerson = "";
        }
    } catch (error) {
        // Error handling is handled by Odoo RPC usually, but we can add specific logic here if needed
    } finally {
        this.state.isProcessing = false;
    }
}
}

SupportPopup.template = "support_quick_timesheet.SupportPopup";

// Register to systray or main components
registry.category("main_components").add("SupportPopup", {
    Component: SupportPopup,
});
