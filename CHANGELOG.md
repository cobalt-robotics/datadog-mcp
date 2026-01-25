# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.5](https://github.com/hacctarr/datadog-mcp/compare/v0.2.4...v0.2.5) (2026-01-25)


### Bug Fixes

* logs int subscript error and fix test suite ([ff96ae8](https://github.com/hacctarr/datadog-mcp/commit/ff96ae858228772578f160fcf6943284471c0718))

## [0.2.4](https://github.com/hacctarr/datadog-mcp/compare/v0.2.3...v0.2.4) (2026-01-23)


### Bug Fixes

* support cookie auth for logs endpoint ([ee53b06](https://github.com/hacctarr/datadog-mcp/commit/ee53b0644cafc46cd583d878ac23f1d73e1ab145))

## [0.2.3](https://github.com/hacctarr/datadog-mcp/compare/v0.2.2...v0.2.3) (2026-01-20)


### Documentation

* clarify authentication methods - API keys OR cookie+CSRF ([68a3aa9](https://github.com/hacctarr/datadog-mcp/commit/68a3aa936657243a6faa95cdd357ae8c3b9375d4))

## [0.2.2](https://github.com/hacctarr/datadog-mcp/compare/v0.2.1...v0.2.2) (2026-01-19)


### Documentation

* add cookie authentication documentation ([fc2bcd8](https://github.com/hacctarr/datadog-mcp/commit/fc2bcd8a697dbe756f608fb1a1fb43a564443476))

## [0.2.1](https://github.com/hacctarr/datadog-mcp/compare/v0.2.0...v0.2.1) (2026-01-19)


### Bug Fixes

* update test to expect warning instead of ValueError for missing credentials ([92bb5d8](https://github.com/hacctarr/datadog-mcp/commit/92bb5d88e958f86358aec5aacf2d782be94d5190))


### Documentation

* add v0.2.0 release notes to CHANGELOG ([0366140](https://github.com/hacctarr/datadog-mcp/commit/03661403e358f9664c097f84f903e58ac834a3eb))

## [v0.2.0] - 2026-01-19

### Added
- **Cookie-Based Authentication** - Alternative to API keys using browser session cookies
  - Dynamic credential loading (update without restarting server)
  - File-based storage (`~/.datadog_cookie`, `~/.datadog_csrf`)
  - `save_cookie()` and `save_csrf_token()` helper functions
- **CSRF Token Support** - Required for protected endpoints (traces, spans) with cookie auth
- **Auth Tests** - 13 new tests covering cookie/CSRF authentication
- **Configuration Documentation** - Added `.env.example` with all config options

### Changed
- `get_auth_headers()` now supports optional `include_csrf` parameter
- `fetch_traces()` and `aggregate_traces()` include CSRF token when using cookie auth
- Updated test fixtures and mock paths for better isolation

### Technical
- Cookie priority: `DD_COOKIE` env var > `~/.datadog_cookie` file
- CSRF priority: `DD_CSRF_TOKEN` env var > `~/.datadog_csrf` file
- Credentials read fresh on each API call (no restart needed)
- File permissions set to 600 for security

## [v0.0.7] - 2025-11-26

### Added
- **PyPI Publishing** - Package now available on PyPI for simple installation with `uvx datadog-mcp`
- **GitHub Actions CI/CD** - Replaced CircleCI with GitHub Actions for testing and automated releases

### Changed
- **Simplified Installation** - Users can now install with just `uvx datadog-mcp` instead of long git URLs
- **Repository Migration** - Updated all references to hacctarr/datadog-mcp fork
- **Fixed Server Path** - Corrected server path from `ddmcp/server.py` to `datadog_mcp/server.py`

### Technical
- Added PyPI badge to README
- Streamlined README from ~150 lines to ~40 lines for installation section
- Auto-release workflow triggers on CHANGELOG.md updates

## [v0.0.6] - 2025-07-14

### Added
- **Enhanced Log Processing**
  - Enhanced log extraction to support new content format with additional attributes
  - Added new tool for retrieving field values from Datadog APIs
  - Improved log parsing capabilities for better data extraction

### Changed
- **Dependency Updates**
  - Upgraded to proper official Datadog SDK client
  - Updated Datadog API client dependencies
  - Improved MCP server self-referencing configuration

### Technical
- Merged PR #3 for enhanced error pattern detection
- Enhanced log content format handling
- Added support for additional log attributes extraction

## [v0.0.5] - 2025-06-27

### Added
- **Monitoring & Alerting Tools**
  - `list_monitors` - List all Datadog monitors with filtering by name, tags, and monitor tags
  - `list_slos` - List Service Level Objectives with filtering by name, tags, and query support
  - Comprehensive filtering options for both monitors and SLOs
  - Multiple output formats (table, json, summary) for monitoring tools

### Enhanced
- Extended tool registry in server.py with new monitoring capabilities
- Updated README with monitoring tools documentation
- Added examples for monitor and SLO management usage

### Technical
- New API endpoints: `/api/v1/monitor` and `/api/v1/slo`
- Enhanced Datadog API client with monitor and SLO support
- Improved pagination handling for large monitor/SLO datasets

## [v0.0.4] - 2025-06-18

### Added
- **CircleCI CI/CD Pipeline**
  - Comprehensive test suite for pull requests (syntax check, package structure, UVX installation, lint check, configuration validation, documentation check)
  - Manual release workflow with semver validation, changelog validation, package building, and GitHub release creation
  - Automatic release detection when changelog contains new versions not yet tagged in GitHub
- UVX support for direct installation from GitHub
- Comprehensive versioning documentation
- Console script entry points for CLI usage
- Proper Python package structure

### Changed
- **Package renamed from "ddmcp" to "datadog-mcp"**
- **Console script renamed from "ddmcp" to "datadog-mcp"**
- **UVX is now the recommended installation method**
- Restructured project as proper Python package in `ddmcp/` directory
- Updated all imports to use relative imports
- Enhanced README with UVX installation methods and versioning examples
- Simplified installation documentation (removed Docker Hub/Compose as primary options)

### Fixed
- Fixed regex pattern in auto-release version detection for reliable changelog parsing
- Corrected semver validation for CircleCI environment compatibility

### Technical
- Added `[project.scripts]` entry point in pyproject.toml
- Created sync wrapper function for async main
- Multi-architecture Docker builds (AMD64/ARM64)
- Comprehensive CI/CD configuration with both manual and automatic release triggers
- Changelog-driven release automation with version detection and GitHub integration 

## [v0.0.3] - 2025-06-16

### Added
- **Service Definitions Management**
  - `list_service_definitions` - List all service definitions with pagination and filtering
  - `get_service_definition` - Retrieve detailed service definition by name
  - Support for schema versions (v1, v2, v2.1, v2.2) with v2.2 as default
  - Multiple output formats (table, json, yaml, formatted)
- Service definition API client functions in `utils/datadog_client.py`

### Enhanced
- Updated README with service definition tools documentation
- Added examples for service definition usage
- Extended tool registry in server.py

### Technical
- New API endpoints: `/api/v2/services/definitions` and `/api/v2/services/definitions/{service_name}`
- Comprehensive service metadata parsing (team, contacts, links, integrations)

## [v0.0.2] - 2025-06-16

### Added
- **Enhanced Metrics System**
  - `list_metrics` - Discover available metrics with filtering
  - `get_metric_fields` - Get available fields/tags for metrics
  - `get_metric_field_values` - Get all values for specific metric fields
  - Dynamic field discovery and validation
- **Improved Logging**
  - `get_logs` - Flexible log retrieval with comprehensive filtering
  - Support for multiple environments, log levels, and time ranges
  - Enhanced log formatting options

### Changed
- Replaced `get_service_logs` and `get_service_metrics` with more flexible generic tools
- Improved error handling and user feedback
- Enhanced API client with better field discovery
- Reorganized tests into dedicated `tests/` directory

### Fixed
- Multi-environment query building with proper OR logic
- Zero-result handling with field suggestions
- Metric aggregation field validation

### Technical
- Added `/api/v2/metrics` endpoint for metric discovery
- Implemented `/api/v2/metrics/{metric_name}/all-tags` for field discovery
- Backward compatibility maintained through wrapper functions

## [v0.0.1] - 2025-06-14 (Initial Release)

### Added
- **Core MCP Server Framework**
  - Async MCP server with stdio transport
  - Tool registration and routing system
  - Comprehensive error handling and logging

- **CI/CD Pipeline Management**
  - `list_ci_pipelines` - List and filter CI pipelines
  - `get_pipeline_fingerprints` - Extract fingerprints for Terraform integration
  - Repository and pipeline name filtering

- **Service Monitoring**
  - `get_service_logs` - Retrieve service logs with environment filtering
  - `get_service_metrics` - Query service metrics with aggregation
  - Multi-environment support (prod, staging, backoffice)
  - Time range filtering (1h to 30d)

- **Team Management**
  - `get_teams` - List teams and member details
  - Team filtering and membership information

- **Data Formatting & Analysis**
  - Multiple output formats (table, json, summary, timeseries)
  - Statistical analysis for metrics (min, max, avg, latest)
  - Configurable data presentation

- **Datadog Integration**
  - Complete API client for Datadog v1 and v2 APIs
  - Authentication via DD_API_KEY and DD_APP_KEY
  - Support for CI pipelines, logs, metrics, and teams endpoints

- **Docker Support**
  - Multi-platform Docker support (AMD64/ARM64)
  - Docker Compose configuration
  - Multi-stage builds with UV package manager
  - Comprehensive installation methods

### Technical Details
- **Architecture**: Modular tool-based pattern with centralized registration
- **Dependencies**: MCP 1.9.4+, httpx, datadog-api-client
- **Python**: Requires Python 3.13+
- **Environment**: Configurable via environment variables
- **Testing**: Comprehensive test suite for all major components

### Documentation
- Complete README with installation, configuration, and usage examples
- Tool-specific documentation with parameter descriptions
- Claude Desktop integration examples
- API credential setup instructions
- Method comparison table for different deployment approaches

---

## Version History Summary

- **v0.2.0**: Cookie-Based Authentication with CSRF Support
- **v0.0.7**: PyPI Publishing & GitHub Actions
- **v0.0.5**: Monitoring & Alerting Tools (Monitors & SLOs)
- **v0.0.4**: CI/CD Pipeline & UVX Support
- **v0.0.3**: Service Definitions Management
- **v0.0.2**: Enhanced Metrics & Logging System
- **v0.0.1**: Initial Release with Core MCP Server, Docker Support

## Migration Notes

### From v0.0.2 to v0.0.3
- No breaking changes
- New service definition tools available alongside existing tools

### From v0.0.1 to v0.0.2
- **Breaking Changes**: 
  - `get_service_logs` → `get_logs` (more flexible filtering)
  - `get_service_metrics` → `get_metrics` (supports any metric, not just service metrics)
- **Migration**: Update tool names in integrations, new tools have enhanced capabilities
