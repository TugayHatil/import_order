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
        // Common function to setup the external window (PiP or standard)
        const setupExternalWindow = (win) => {
            // 1. Copy ALL style elements (Link and Style tags)
            const allStyleNodes = document.querySelectorAll('link[rel="stylesheet"], style');
            allStyleNodes.forEach(node => {
                win.document.head.appendChild(node.cloneNode(true));
            });

            // 2. Setup Body - Inherit classes from main window
            win.document.body.className = document.body.className;
            win.document.body.classList.add('o_web_client', 'o_web_backend');
            win.document.body.style.background = "#fff";
            win.document.body.style.margin = "0";
            win.document.body.style.display = "block";
            win.document.body.style.height = "100vh";
            win.document.body.style.overflow = "auto"; // Ensure scrolling

            // 3. Move the component element
            // Accessing the root element. In OWL 2, we might not have 'this.el'.
            // Using the internal reference as seen in the previous code, or fallback to direct DOM query if needed.
            const element = this.__owl__.bdom ? this.__owl__.bdom.el : (this.__owl__.me ? this.__owl__.me.el : null);
            
            if (!element) {
                console.error("SupportPopup: Could not find component element to move.");
                return;
            }

            win.document.body.appendChild(element);

            // Apply PiP specific styles
            element.classList.add('o_in_pip');
            element.classList.remove('o_hidden');
            this.state.isVisible = true;

            // 4. Handle closing - Restore element to main window
            const onExternalClose = () => {
                element.classList.remove('o_in_pip');
                // We need to put it back where it belongs. 
                // Since we don't know the exact parent, appending to body is a safe bet for a direct child of 'main_components'.
                // Ideally, OWL framework handles this if we didn't break the VDOM connection too badly.
                // Re-appending to the document body of the main window:
                document.body.appendChild(element); 
                this.render(); // Trigger re-render to ensure state consistency
            };

            win.addEventListener("pagehide", onExternalClose);
            // Also listen to 'unload' just in case
            win.addEventListener("unload", () => {
                 // Check if already restored to avoid double execution if pagehide fires too
                 if (element.ownerDocument !== document) {
                     onExternalClose();
                 }
            });
            
            console.log("SupportPopup: External Window initialized successfully");
        };

        try {
            // Try Document Picture-in-Picture API first
            if (window.documentPictureInPicture) {
                const pipWindow = await window.documentPictureInPicture.requestWindow({
                    width: 350,
                    height: 520,
                });
                setupExternalWindow(pipWindow);
                return;
            }
        } catch (err) {
            console.warn("SupportPopup: PiP API failed or not supported, falling back to window.open", err);
        }

        // Fallback: standard window.open
        try {
            const width = 350;
            const height = 520;
            const left = window.screen.width - width - 50;
            // Open specifically 'about:blank' to ensure we can write to it immediately
            const popWin = window.open('about:blank', 'SupportPopOut', `width=${width},height=${height},left=${left},top=50,popup=yes`);
            
            if (!popWin) {
                this.notification.add("Popup blocked. Please allow popups.", { type: "warning" });
                return;
            }

            // Small delay to ensure window is ready? Usually about:blank is synchronous.
            setupExternalWindow(popWin);
            
            // Focus the new window
            popWin.focus();

        } catch (e) {
             console.error("SupportPopup: Fallback window.open failed", e);
             this.notification.add("Failed to open popup window.", { type: "danger" });
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
