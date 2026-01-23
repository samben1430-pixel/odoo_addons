# Smile FS Attachment Fix

## Description

This module fixes the `FileNotFoundError` that can occur when using the `fs_attachment` module with external storage systems (S3, GCS, NFS, etc.).

## Problem

When files are missing from external storage but references still exist in Odoo, the application crashes with:

```
FileNotFoundError: bucket3/de11391c322e01e0e94c6ab4bf930d363b687e56
```

This can happen when:
- Files are manually deleted from external storage
- Storage synchronization issues occur
- Migration or backup restore operations are incomplete
- Network issues prevent access to storage systems

## Solution

This module adds robust error handling by:

1. **Catching FileNotFoundError**: Intercepts the error before it crashes the application
2. **Logging detailed information**: Records the missing file path and full stack trace for debugging
3. **Graceful degradation**: Returns empty content instead of crashing
4. **OSError handling**: Also catches network and permission-related storage errors

## Technical Details

The module overrides two key methods in `ir.attachment`:

- `_file_read(fname)`: Main file reading method
- `_storage_file_read(fname)`: External storage file reading method (used by fs_attachment)

Both methods now wrap the parent call in try-except blocks to catch and handle:
- `FileNotFoundError`: When files don't exist in storage
- `OSError`: When network or permission issues occur
- `AttributeError`: When fs_attachment is not installed (graceful fallback)

## Installation

1. Copy this module to your Odoo addons directory
2. Update the app list
3. Install "Smile FS Attachment Fix"

## Configuration

No configuration needed. The module automatically protects all attachment read operations.

## Logging

When a file is not found, you'll see log entries like:

```
ERROR: File not found in external storage: bucket3/de11391c322e01e0e94c6ab4bf930d363b687e56.
Storage path that failed: bucket3/de11391c322e01e0e94c6ab4bf930d363b687e56.
Returning empty content to prevent application crash.
```

## Compatibility

- Odoo 17.0
- Works with or without fs_attachment module
- Compatible with all fsspec-based storage backends (S3, GCS, Azure, etc.)

## License

AGPL-3.0 or later

## Author

Smile - http://www.smile.eu
