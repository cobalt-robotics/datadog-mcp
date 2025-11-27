# Datadog MCP Server

[![CI](https://github.com/hacctarr/datadog-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/hacctarr/datadog-mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/datadog-mcp)](https://pypi.org/project/datadog-mcp/)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://python.org)

MCP server that gives Claude access to Datadog monitoring: metrics, logs, pipelines, monitors, SLOs, services, and teams.

## Installation

**Requires:** [Datadog API credentials](#getting-datadog-credentials)

### Claude Code
```bash
claude mcp add datadog-mcp -e DD_API_KEY=xxx -e DD_APP_KEY=xxx
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "datadog": {
      "command": "uvx",
      "args": ["datadog-mcp"],
      "env": {
        "DD_API_KEY": "xxx",
        "DD_APP_KEY": "xxx"
      }
    }
  }
}
```

Requires [uvx](https://github.com/astral-sh/uv). Alternatively use `pipx run datadog-mcp`.

## Tools

| Tool | Description |
|------|-------------|
| `list_metrics` | Discover available metrics |
| `get_metrics` | Query metrics with filters and aggregation |
| `get_metric_fields` | Get available tags for a metric |
| `get_metric_field_values` | Get values for a metric tag |
| `get_service_logs` | Retrieve logs with filtering |
| `list_monitors` | List monitors with filtering |
| `list_slos` | List SLOs with filtering |
| `list_service_definitions` | List service catalog entries |
| `get_service_definition` | Get service details |
| `list_ci_pipelines` | List CI pipelines |
| `get_pipeline_fingerprints` | Extract pipeline fingerprints |
| `get_teams` | List teams and members |

## Examples

```
"Get error logs for user-service in the last 4 hours"
"Show metrics for aws.apigateway.count grouped by account"
"List all monitors tagged env:prod"
"What SLOs are below 99%?"
```

## Getting Datadog Credentials

1. Go to [Datadog Organization Settings](https://app.datadoghq.com/organization-settings/)
2. **API Keys** → Create/copy key → `DD_API_KEY`
3. **Application Keys** → Create/copy key → `DD_APP_KEY`

## Development

```bash
git clone https://github.com/hacctarr/datadog-mcp.git && cd datadog-mcp
pip install -e .
DD_API_KEY=xxx DD_APP_KEY=xxx datadog-mcp
```

## Credits

Originally created by [@andreidore](https://github.com/andreidore/datadog-mcp).
