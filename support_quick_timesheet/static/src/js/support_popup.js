/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class SupportPopup extends Component {
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
        this.openHandler = () => {
            console.log("SupportPopup: Handling OPEN event");
            this.openPopup();
        };

        this.env.bus.addEventListener("SUPPORT_POPUP:OPEN", this.openHandler);
    }

    destroy() {
        if (this.openHandler) {
            this.env.bus.removeEventListener("SUPPORT_POPUP:OPEN", this.openHandler);
        }
        super.destroy();
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

    async popOut() {
        if (!window.documentPictureInPicture) {
            this.notification.add("Tarayıcınız 'Her Zaman Üstte' (PiP) özelliğini desteklemiyor.", { type: "warning" });
            return;
        }

        try {
            const pipWindow = await window.documentPictureInPicture.requestWindow({
                width: 350,
                height: 520,
            });

            // 1. Copy ALL style elements (Link and Style tags) - Most robust method
            const allStyleNodes = document.querySelectorAll('link[rel="stylesheet"], style');
            allStyleNodes.forEach(node => {
                pipWindow.document.head.appendChild(node.cloneNode(true));
            });

            // 2. Setup Body - Inherit classes from main window
            pipWindow.document.body.className = document.body.className;
            pipWindow.document.body.classList.add('o_web_client', 'o_web_backend');
            pipWindow.document.body.style.background = "#fff";
            pipWindow.document.body.style.margin = "0";
            pipWindow.document.body.style.display = "block";
            pipWindow.document.body.style.height = "100vh";

            // 3. Move the component element
            const element = this.__owl__.me.el;
            pipWindow.document.body.appendChild(element);

            // Apply PiP specific styles
            element.classList.add('o_in_pip');
            element.classList.remove('o_hidden');
            this.state.isVisible = true;

            // 4. Handle closing
            pipWindow.addEventListener("pagehide", () => {
                element.classList.remove('o_in_pip');
                document.body.appendChild(element);
                this.render();
            });

            console.log("SupportPopup: PiP Window initialized successfully");

        } catch (err) {
            console.error("SupportPopup: PiP Error", err);
            // Last resort: standard window.open
            const width = 350;
            const height = 520;
            const left = window.screen.width - width - 50;
            window.open('/support/quick_form', 'SupportPopOut', `width=${width},height=${height},left=${left},top=50`);
        }
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
                this.state.contactPerson = "";
            }
        } catch (error) {
            console.error("SupportPopup: Error creating timesheet", error);
        } finally {
            this.state.isProcessing = false;
        }
    }
}

SupportPopup.template = "support_quick_timesheet.SupportPopup";

// Register to main components
registry.category("main_components").add("SupportPopup", {
    Component: SupportPopup,
});
