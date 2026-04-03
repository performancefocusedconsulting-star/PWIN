/**
 * PWIN Platform — Server Entry Point
 *
 * Dual interface:
 *   1. Data API (HTTP, localhost:3456) — serves HTML product apps
 *   2. MCP Server (stdio) — serves Claude with typed tool functions
 *
 * Usage:
 *   node src/server.js              — start Data API only (default)
 *   node src/server.js --mcp        — start MCP server only (stdio, for Claude)
 *   node src/server.js --both       — start both (API on HTTP, MCP on stdio)
 */

import { startAPI } from './api.js';
import { startMCP } from './mcp.js';

const args = process.argv.slice(2);
const mcpOnly = args.includes('--mcp');
const both = args.includes('--both');

async function main() {
  if (mcpOnly) {
    await startMCP();
  } else if (both) {
    await startAPI();
    await startMCP();
  } else {
    // Default: Data API only
    await startAPI();
    console.log('[PWIN Platform] Run with --mcp for MCP server, --both for both interfaces');
  }
}

main().catch((err) => {
  console.error('[PWIN Platform] Fatal error:', err);
  process.exit(1);
});
