# -*- coding: utf-8 -*-
# (C) 2026 Smile (<http://www.smile.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Smile FS Attachment Fix",
    "version": "17.0.1.0.0",
    "category": "Tools",
    "author": "Smile",
    "license": "AGPL-3",
    "description": """
Fix for FileNotFoundError in fs_attachment
==========================================

This module adds robust error handling for missing files in external storage systems.

Features:
---------
* Catches FileNotFoundError when reading files from external storage (S3, GCS, etc.)
* Logs detailed error information for debugging
* Returns empty content instead of crashing
* Prevents application crashes when files are missing from storage

This fix is particularly useful when:
* Files are deleted from external storage but references remain in Odoo
* Storage configuration issues cause file access problems
* Network issues prevent access to storage systems
    """,
    "depends": [
        "base",
    ],
    "data": [],
    "installable": True,
    "auto_install": False,
}
