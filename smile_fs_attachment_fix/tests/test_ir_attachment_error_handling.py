# -*- coding: utf-8 -*-
# (C) 2026 Smile (<http://www.smile.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch
from odoo.tests.common import TransactionCase


class TestIrAttachmentErrorHandling(TransactionCase):
    """Test error handling for missing files in external storage."""

    def setUp(self):
        super(TestIrAttachmentErrorHandling, self).setUp()
        self.attachment_model = self.env["ir.attachment"]

    def test_file_read_with_file_not_found_error(self):
        """Test that _file_read handles FileNotFoundError gracefully."""
        with patch.object(
            type(self.attachment_model),
            "_file_read",
            side_effect=FileNotFoundError("Test file not found")
        ):
            # This should not raise an exception, but return empty bytes
            result = self.attachment_model._file_read("test_file.txt")
            self.assertEqual(result, b"", "Should return empty bytes on FileNotFoundError")

    def test_file_read_with_os_error(self):
        """Test that _file_read handles OSError gracefully."""
        with patch.object(
            type(self.attachment_model),
            "_file_read",
            side_effect=OSError("Test OS error")
        ):
            # This should not raise an exception, but return empty bytes
            result = self.attachment_model._file_read("test_file.txt")
            self.assertEqual(result, b"", "Should return empty bytes on OSError")

    def test_storage_file_read_with_file_not_found_error(self):
        """Test that _storage_file_read handles FileNotFoundError gracefully."""
        # Check if _storage_file_read exists (requires fs_attachment module)
        if not hasattr(self.attachment_model, "_storage_file_read"):
            self.skipTest("_storage_file_read not available (fs_attachment not installed)")

        with patch.object(
            type(self.attachment_model),
            "_storage_file_read",
            side_effect=FileNotFoundError("Test file not found in storage")
        ):
            # This should not raise an exception, but return empty bytes
            result = self.attachment_model._storage_file_read("test_file.txt")
            self.assertEqual(
                result, b"", "Should return empty bytes on FileNotFoundError"
            )

    def test_storage_file_read_without_fs_attachment(self):
        """Test that _storage_file_read handles missing fs_attachment module."""
        # Simulate fs_attachment not being installed by raising AttributeError
        with patch.object(
            type(self.attachment_model),
            "_storage_file_read",
            side_effect=AttributeError("_storage_file_read not found")
        ):
            # This should not raise an exception, but return empty bytes
            result = self.attachment_model._storage_file_read("test_file.txt")
            self.assertEqual(
                result, b"",
                "Should return empty bytes when fs_attachment is not installed"
            )

    def test_normal_file_read_still_works(self):
        """Test that normal file reading still works correctly."""
        # Create a test attachment
        attachment = self.attachment_model.create({
            "name": "Test File",
            "datas": b"VGVzdCBjb250ZW50",  # Base64 of "Test content"
        })

        # Read the file - should work normally
        self.assertTrue(attachment.datas, "Should be able to read attachment normally")
