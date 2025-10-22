========================
Code Version Display
========================

.. |badge1| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

.. |badge2| image:: https://img.shields.io/badge/github-Smile--SA%2Fodoo_addons-lightgray.png?logo=github
    :target: https://github.com/Smile-SA/odoo_addons/tree/17.0/smile_code_version_display
    :alt: Smile-SA/odoo_addons

|badge1| |badge2|

This module displays the code version in the Odoo systray (top navigation bar).
It's particularly useful for environments like DEV, QA, or STAGING where you want
to quickly identify which version of code is running.

**Table of contents**

.. contents::
   :local:

Features
========

* Displays code version as a badge in the systray
* Configurable via system parameter ``code.version.display``
* Beautiful gradient badge with hover effects
* Works standalone or with ``smile_upgrade`` module
* Can be integrated with environment ribbon modules
* Minimal performance impact (single RPC call at page load)

Configuration
=============

Enable Display
--------------

Go to **Settings → Technical → Parameters → System Parameters** and set:

* **Key**: ``code.version.display``
* **Value**: ``True``

Or via SQL::

    UPDATE ir_config_parameter
    SET value = 'True'
    WHERE key = 'code.version.display';

Set Code Version
----------------

The module reads the version from the system parameter ``code.version``.

**If you use smile_upgrade:**
The version is automatically managed by ``smile_upgrade`` module.

**If you don't use smile_upgrade:**
You can set it manually:

1. Via System Parameters::

    Key: code.version
    Value: 1.2.3

2. Via environment variable::

    export CODE_VERSION="1.2.3"
    odoo-bin -c odoo.conf

3. Via SQL at deployment::

    INSERT INTO ir_config_parameter (key, value)
    VALUES ('code.version', '1.2.3')
    ON CONFLICT (key) DO UPDATE SET value = '1.2.3';

Usage
=====

Once installed and enabled:

1. Install the module
2. Set ``code.version.display`` to ``True``
3. Set ``code.version`` to your version number
4. Refresh your browser
5. You'll see a purple badge with your version in the top bar

Integration with Environment Ribbon
====================================

This module works great alongside environment ribbon modules (like ``web_environment_ribbon``).
They complement each other:

* **Ribbon**: Shows which environment (DEV/QA/PROD)
* **Version Badge**: Shows which code version is running

Example Setup for DEV/QA Environments
--------------------------------------

**odoo-dev.conf**::

    [options]
    # ... other options ...
    ribbon.name = DEV
    ribbon.color = #FF0000

**odoo-qa.conf**::

    [options]
    # ... other options ...
    ribbon.name = QA
    ribbon.color = #FFA500

For both environments, enable version display::

    UPDATE ir_config_parameter
    SET value = 'True'
    WHERE key = 'code.version.display';

Customization
=============

Badge Styling
-------------

You can customize the badge appearance by modifying the template in
``static/src/xml/code_version_systray.xml``.

Current style uses a purple gradient. You can change colors:

* **Green theme**: ``#11998e`` to ``#38ef7d``
* **Blue theme**: ``#4facfe`` to ``#00f2fe``
* **Red theme**: ``#eb3349`` to ``#f45c43``

Example for environment-based colors::

    <!-- DEV: Red -->
    background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);

    <!-- QA: Orange -->
    background: linear-gradient(135deg, #f46b45 0%, #eea849 100%);

    <!-- STAGING: Blue -->
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);

Click Action
------------

By default, clicking the badge logs the version to console.
You can customize the ``onClick()`` method in ``static/src/js/code_version_systray.js``
to show a notification or dialog with more information.

Integration with Your Module
=============================

If you have your own ribbon module and want to integrate this functionality:

**Option 1: Add as dependency**

In your module's ``__manifest__.py``::

    {
        'depends': ['smile_code_version_display', ...],
    }

**Option 2: Copy the functionality**

You can copy these files to your module:

1. ``models/code_version.py`` → Your module's models
2. ``static/src/js/code_version_systray.js`` → Your module's JS
3. ``static/src/xml/code_version_systray.xml`` → Your module's XML

Then customize as needed (e.g., integrate into your ribbon component).

Technical Details
=================

* **Model**: ``code.version.display`` (AbstractModel)
* **RPC Method**: ``get_version_info()`` - Returns version and display flag
* **JS Component**: OWL component registered in systray
* **Sequence**: 1 (appears on the left side of systray)

Performance
-----------

* Single RPC call per page load
* No polling or periodic updates
* Minimal DOM footprint
* Uses Odoo's native caching mechanisms

Known Issues
============

None at this time.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Smile-SA/odoo_addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.

Credits
=======

Contributors
------------

* Smile SA

Maintainer
----------

This module is maintained by Smile SA.

Since 1991 Smile has been a pioneer of technology and also the European expert in open source solutions.
