# Datadog MCP Server

[![CI](https://github.com/hacctarr/datadog-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/hacctarr/datadog-mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/datadog-mcp)](https://pypi.org/project/datadog-mcp/)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://python.org)

MCP server that gives Claude access to Datadog monitoring: metrics, logs, traces, pipelines, monitors, SLOs, services, and teams.

## Installation

**Requires:** [Datadog credentials](#authentication) (API keys or browser cookies)

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
| `get_logs` | Retrieve logs with filtering |
| `get_logs_field_values` | Get possible values for a log field |
| `get_traces` | Search APM traces/spans |
| `aggregate_traces` | Aggregate trace counts with grouping |
| `list_monitors` | List monitors with filtering |
| `list_slos` | List SLOs with filtering |
| `list_service_definitions` | List service catalog entries |
| `get_service_definition` | Get service details |
| `list_ci_pipelines` | List CI pipelines |
| `get_pipeline_fingerprints` | Extract pipeline fingerprints |
| `get_teams` | List teams and members |

> **Note:** `get_traces` and `aggregate_traces` require [cookie authentication](#cookie-authentication) with CSRF token.

## Examples

```
"Get error logs for user-service in the last 4 hours"
"Show metrics for aws.apigateway.count grouped by account"
"List all monitors tagged env:prod"
"What SLOs are below 99%?"
```

## Authentication

Two authentication methods are supported:

### API Keys (Recommended for most tools)

1. Go to [Datadog Organization Settings](https://app.datadoghq.com/organization-settings/)
2. **API Keys** → Create/copy key → `DD_API_KEY`
3. **Application Keys** → Create/copy key → `DD_APP_KEY`

### Cookie Authentication

Required for traces/spans API. Use browser cookies from an authenticated Datadog session.

**Setup:**
1. Log into Datadog in your browser
2. Open DevTools → Network tab → find any request to `app.datadoghq.com`
3. Copy the `Cookie` header value (needs `dogweb` and `dogwebu` cookies)
4. Copy the `x-csrf-token` header value

**Configure via environment variables:**
```bash
export DD_COOKIE="dogweb=abc123; dogwebu=xyz789"
export DD_CSRF_TOKEN="your-csrf-token"
```

**Or via files** (useful for dynamic updates without restart):
```bash
echo "dogweb=abc123; dogwebu=xyz789" > ~/.datadog_cookie
echo "your-csrf-token" > ~/.datadog_csrf
chmod 600 ~/.datadog_cookie ~/.datadog_csrf
```

**Priority:** Environment variables take precedence over files. Cookie auth takes precedence over API keys when both are configured.

## Development

```bash
git clone https://github.com/hacctarr/datadog-mcp.git && cd datadog-mcp
pip install -e .
DD_API_KEY=xxx DD_APP_KEY=xxx datadog-mcp
```

## Credits

Originally created by [@andreidore](https://github.com/andreidore/datadog-mcp).
