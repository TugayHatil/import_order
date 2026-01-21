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
        if (window.documentPictureInPicture) {
            console.log("SupportPopup: Using Document Picture-in-Picture API");
            try {
                const pipWindow = await window.documentPictureInPicture.requestWindow({
                    width: 350,
                    height: 500,
                });

                // Copy styles to the new window
                [...document.styleSheets].forEach((styleSheet) => {
                    try {
                        if (styleSheet.href) {
                            const link = pipWindow.document.createElement('link');
                            link.rel = 'stylesheet';
                            link.href = styleSheet.href;
                            pipWindow.document.head.appendChild(link);
                        } else {
                            const cssRules = [...styleSheet.cssRules].map((rule) => rule.cssText).join('');
                            const style = pipWindow.document.createElement('style');
                            style.textContent = cssRules;
                            pipWindow.document.head.appendChild(style);
                        }
                    } catch (e) {
                        console.warn("Could not copy styleSheet", styleSheet, e);
                    }
                });

                // Move our element to the PIP window
                const container = this.__owl__.me.el;
                pipWindow.document.body.append(container);

                // Add class for PiP styling
                container.classList.add('o_in_pip');
                this.state.isVisible = true;

                // When the PIP window closes, move the element back
                pipWindow.addEventListener("pagehide", (event) => {
                    container.classList.remove('o_in_pip');
                    document.body.append(container);
                    this.state.isVisible = false;
                });

                return;
            } catch (err) {
                console.error("SupportPopup: PiP Request failed, falling back to window.open", err);
            }
        }

        // Fallback for older browsers
        const width = 350;
        const height = 500;
        const left = window.screen.width - width - 50;
        const top = 50;
        window.open(
            '/support/quick_form',
            'SupportQuickTimesheet',
            `width=${width},height=${height},left=${left},top=${top},status=no,menubar=no,toolbar=no,scrollbars=yes`
        );
        this.closePopup();
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
