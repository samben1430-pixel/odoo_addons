# Changelog

All notable changes to this module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [17.0.1.0.0] - 2025-10-22

### Added
- Initial release for Odoo 17.0
- Display code version in systray (top navigation bar)
- Configurable display via system parameter `code.version.display`
- Beautiful gradient badge with hover effects
- OWL component for modern Odoo frontend
- Support for `code.version` system parameter
- Fallback to `CODE_VERSION` environment variable
- Python model `code.version.display` with RPC method `get_version_info()`
- Complete documentation (README.rst, INSTALL.md, INTEGRATION_GUIDE.md)
- Quick start guide (QUICK_START.md)
- Example scripts for environment setup
- Docker Compose examples
- Integration examples with ribbon modules

### Features
- **Single RPC call** at page load (no polling)
- **Minimal DOM footprint** for performance
- **Customizable styling** via XML template
- **Environment-aware** configuration support
- **Works standalone** or with `smile_upgrade` module
- **Easy CI/CD integration** with examples for GitLab CI, GitHub Actions, and Kubernetes

### Technical Details
- Model: `code.version.display` (AbstractModel)
- JS Component: OWL component registered in systray
- Assets: Bundled in `web.assets_backend`
- Dependencies: Only `web` module
- License: AGPL-3

### Documentation
- Comprehensive README with features and configuration
- Installation guide with multiple deployment scenarios
- Integration guide for ribbon modules and CI/CD pipelines
- Quick start guide for 5-minute setup
- Examples for Docker, Kubernetes, Git hooks
- Troubleshooting section

### Examples Provided
- Environment setup script (`examples/environment_setup.sh`)
- Docker Compose configuration (`examples/docker-compose.yml`)
- Git hooks for automatic version updates
- CI/CD pipeline examples (GitLab CI, GitHub Actions)
- Kubernetes ConfigMap and Deployment examples

---

## Roadmap

### [17.0.1.1.0] - Future
- [ ] Add user group restriction option
- [ ] Add notification dialog with detailed version info on click
- [ ] Add automatic color coding based on environment
- [ ] Add support for additional metadata (git commit, deploy date)
- [ ] Add integration with Sentry/error tracking

### [17.0.2.0.0] - Future
- [ ] Add REST API endpoint for version info
- [ ] Add version history tracking
- [ ] Add rollback detection
- [ ] Add version comparison tool
- [ ] Add changelog integration

---

## Migration Notes

### From smile_upgrade < 17.0
If you were using the built-in version display from `smile_upgrade`:
- This module extracts that functionality into a standalone module
- The version display in `smile_upgrade` remains available
- You can use both or choose one
- No breaking changes - fully compatible

### Upgrading to 17.0.1.0.0
First installation, no upgrade needed.

---

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Support

For issues, questions, or contributions:
- **GitHub Issues**: https://github.com/Smile-SA/odoo_addons/issues
- **Documentation**: See README.rst and other .md files in this module

---

## Authors

- **Smile SA** - *Initial work* - [Smile-SA](https://github.com/Smile-SA)

## License

This project is licensed under the AGPL-3 License - see the LICENSE file for details.

---

**Maintained by Smile SA** - European expert in open source solutions since 1991.
