# -*- coding: utf-8 -*-
# (C) 2026 Smile (<http://www.smile.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from odoo import models, api

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.model
    def _file_read(self, fname):
        """
        Override _file_read to add robust error handling for FileNotFoundError.

        This method wraps the parent _file_read method and catches FileNotFoundError
        that can occur when files are missing from external storage systems (S3, GCS, etc.).

        When a FileNotFoundError occurs:
        - The error is logged with full details for debugging
        - An empty bytes object is returned instead of crashing
        - The application continues to function

        Args:
            fname: The filename/path to read

        Returns:
            bytes: The file content, or empty bytes if the file is not found
        """
        try:
            return super(IrAttachment, self)._file_read(fname)
        except FileNotFoundError as e:
            _logger.error(
                "File not found in storage: %s. "
                "This may indicate a missing file in external storage (S3, GCS, etc.). "
                "Returning empty content to prevent application crash.",
                fname,
                exc_info=True
            )
            # Return empty bytes to prevent application crash
            return b""
        except OSError as e:
            # Catch other OS-related errors (network issues, permission problems, etc.)
            _logger.error(
                "OS error while reading file from storage: %s. Error: %s. "
                "Returning empty content to prevent application crash.",
                fname,
                str(e),
                exc_info=True
            )
            return b""

    @api.model
    def _storage_file_read(self, fname):
        """
        Override _storage_file_read to add robust error handling.

        This method is called by fs_attachment module when reading files from
        external storage. We add additional error handling here to catch
        FileNotFoundError that can occur during file opening.

        Args:
            fname: The filename/path to read

        Returns:
            bytes: The file content, or empty bytes if the file is not found
        """
        try:
            return super(IrAttachment, self)._storage_file_read(fname)
        except FileNotFoundError as e:
            _logger.error(
                "File not found in external storage: %s. "
                "Storage path that failed: %s. "
                "Returning empty content to prevent application crash.",
                fname,
                str(e),
                exc_info=True
            )
            return b""
        except OSError as e:
            _logger.error(
                "OS error while reading file from external storage: %s. Error: %s. "
                "Returning empty content to prevent application crash.",
                fname,
                str(e),
                exc_info=True
            )
            return b""
        except AttributeError:
            # _storage_file_read might not exist if fs_attachment is not installed
            # In this case, fall back to normal behavior
            _logger.debug(
                "_storage_file_read method not found in parent. "
                "This is normal if fs_attachment module is not installed."
            )
            return b""
