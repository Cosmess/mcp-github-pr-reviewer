# Architecture

## Overview

`mcp-github-pr-reviewer` is a read-only MCP Server that exposes GitHub pull
request review capabilities to MCP clients.

```txt
MCP Client
   |
   | calls tools
   v
FastMCP Server
   |
   | delegates
   v
Application Services
   |
   | validates policy and calls GitHub
   v
GitHub REST API
   |
   | returns PR metadata and files
   v
Diff Analyzer
   |
   | builds deterministic review output
   v
Structured MCP response
```

## Layers

### MCP layer

Located in `src/mcp_github_pr_reviewer/server.py`.

Responsibilities:

- Register tools.
- Receive MCP client input.
- Delegate work to services.
- Return JSON/Markdown-compatible responses.

### Configuration layer

Located in `src/mcp_github_pr_reviewer/config.py`.

Responsibilities:

- Read environment variables.
- Define API timeout and patch size limits.
- Build repository allowlist.

### Security policy layer

Located in `src/mcp_github_pr_reviewer/security/policies.py`.

Responsibilities:

- Validate repository access.
- Truncate large patches.
- Keep write actions out of the MVP.

### GitHub service layer

Located in `src/mcp_github_pr_reviewer/services/github_service.py`.

Responsibilities:

- Call GitHub REST API.
- Map API payloads to internal models.
- Handle pagination and GitHub response metadata.
- Normalize API errors.

### Analysis layer

Located in `src/mcp_github_pr_reviewer/services/diff_analyzer.py`.

Responsibilities:

- Identify important files.
- Detect common risks.
- Suggest tests.
- Generate Markdown review output.

The first version is intentionally deterministic and does not require an LLM.
This keeps tests stable and makes the baseline behavior easy to inspect.

## Future LLM integration

A future `LLMAnalyzer` should be added behind an interface instead of mixing LLM
calls into MCP tools or GitHub service code.

Suggested shape:

```txt
Analyzer
├── HeuristicAnalyzer
└── LLMAnalyzer
```

The server can then select the analyzer using environment configuration.
