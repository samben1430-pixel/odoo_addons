{
    "name": "Code Version Display",
    "version": "17.0.1.0.0",
    "depends": ["web"],
    "author": "Smile",
    "license": "AGPL-3",
    "description": """
Display Code Version in Systray
================================

This module displays the code version in the Odoo systray.
It can be enabled/disabled via the system parameter 'code.version.display'.

Features:
---------
* Displays code version in systray (top bar)
* Configurable via system parameter
* Works with or without smile_upgrade module
* Can be integrated with environment ribbon modules

Configuration:
--------------
Set the system parameter 'code.version.display' to True to enable the display.
    """,
    "summary": "Display code version in systray",
    "website": "https://github.com/Smile-SA/odoo_addons",
    "category": "Tools",
    "sequence": 20,
    "auto_install": False,
    "installable": True,
    "application": False,
    "data": [
        "data/ir_config_parameter.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "smile_code_version_display/static/src/js/**/*",
            "smile_code_version_display/static/src/xml/**/*",
        ],
    },
}
