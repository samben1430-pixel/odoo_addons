/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

/**
 * Code Version Systray Component
 *
 * Displays the code version in the systray (top bar) if enabled via
 * the system parameter 'code.version.display'
 */
class CodeVersionSystray extends Component {
    static template = "smile_code_version_display.CodeVersionSystray";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            version: "",
            display: false,
        });

        onWillStart(async () => {
            await this.loadVersion();
        });
    }

    /**
     * Load version information from backend
     */
    async loadVersion() {
        try {
            const data = await this.orm.call(
                "code.version.display",
                "get_version_info",
                []
            );
            Object.assign(this.state, {
                version: data.version,
                display: data.display,
            });
        } catch (error) {
            console.error("Failed to load code version:", error);
            this.state.display = false;
        }
    }

    /**
     * Handle click on version badge
     * You can customize this to show more information
     */
    onClick() {
        // Optional: Add notification or dialog with more info
        console.log("Code Version:", this.state.version);
    }
}

export const systrayItem = {
    Component: CodeVersionSystray,
};

// Register in systray with low sequence to appear on the left
registry
    .category("systray")
    .add("CodeVersionSystray", systrayItem, { sequence: 1 });
