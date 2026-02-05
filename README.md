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

## Examples

```
"Get error logs for user-service in the last 4 hours"
"Show metrics for aws.apigateway.count grouped by account"
"List all monitors tagged env:prod"
"What SLOs are below 99%?"
```

## Authentication

**Quick Start (AWS Secrets Manager - no config needed):**
```bash
aws sso login        # Login to AWS
datadog-mcp          # Start the server
```

The server uses sensible defaults - just ensure your Datadog credentials are stored in AWS Secrets Manager at the default paths.

### Default Configuration

| Setting | Default Value |
|---------|---------------|
| AWS Profile | `default` |
| AWS Region | `us-west-2` |
| API Key Secret | `/DEVELOPMENT/datadog/API_KEY` |
| App Key Secret | `/DEVELOPMENT/datadog/APP_KEY` |

**Required IAM permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ],
    "Resource": [
      "arn:aws:secretsmanager:*:*:secret:/DEVELOPMENT/datadog/*"
    ]
  }]
}
```

### Override Defaults (Optional)

Set environment variables only if you need different values:

| Variable | Default | Description |
|----------|---------|-------------|
| `AWS_PROFILE` | `default` | AWS profile to use |
| `AWS_REGION` | `us-west-2` | AWS region for Secrets Manager |
| `AWS_SECRET_API_KEY` | `/DEVELOPMENT/datadog/API_KEY` | Secret path for API key |
| `AWS_SECRET_APP_KEY` | `/DEVELOPMENT/datadog/APP_KEY` | Secret path for App key |
| `AWS_ROLE_ARN` | None | IAM role to assume (optional) |
| `SECRET_CACHE_TTL` | `3000` | Cache TTL in seconds |

### Alternative: Cookie Authentication

Cookie auth takes priority when configured. Use this for development/testing.

**Via environment variables:**
```bash
export DD_COOKIE="dogweb=abc123; dogwebu=xyz789"
export DD_CSRF_TOKEN="your-csrf-token"
```

**Via files** (can be updated without restarting the server):
```bash
echo "dogweb=abc123; dogwebu=xyz789" > ~/.datadog_cookie
echo "your-csrf-token" > ~/.datadog_csrf
chmod 600 ~/.datadog_cookie ~/.datadog_csrf
```

To get your cookie and CSRF token:
1. Log into [app.datadoghq.com](https://app.datadoghq.com)
2. Open DevTools (F12) → Network tab
3. Copy `Cookie` and `x-csrf-token` headers from any request

## Development

```bash
git clone https://github.com/hacctarr/datadog-mcp.git && cd datadog-mcp
pip install -e .
DD_API_KEY=xxx DD_APP_KEY=xxx datadog-mcp
```

## Credits

Originally created by [@andreidore](https://github.com/andreidore/datadog-mcp).
