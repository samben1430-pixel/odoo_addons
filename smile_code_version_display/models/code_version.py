from odoo import api, models


class CodeVersionDisplay(models.AbstractModel):
    """Model to retrieve and display code version in systray"""

    _name = "code.version.display"
    _description = "Code Version Display"

    @api.model
    def get_version_info(self):
        """
        Get code version and display settings

        Returns:
            dict: {
                'version': str - code version or 'N/A' if not set,
                'display': bool - whether to display in systray
            }
        """
        IrConfigParam = self.env["ir.config_parameter"].sudo()

        # Check if display is enabled
        display_enabled = IrConfigParam.get_param(
            "code.version.display",
            default="False"
        ) == "True"

        # Get version from ir.config_parameter
        version = IrConfigParam.get_param("code.version", default=False)

        # If no version found, try to get it from environment variable
        # or return a default value
        if not version:
            import os
            version = os.environ.get("CODE_VERSION", "N/A")

        return {
            "version": version,
            "display": display_enabled,
        }
