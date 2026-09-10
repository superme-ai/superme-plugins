#!/usr/bin/env python3
"""Validate the marketplace manifests the way each catalog reads them.

Both catalogs clone this repo at a pinned SHA and resolve every path the
manifest declares against the *plugin root* — which, because `.cursor-plugin/`
and `.grok-plugin/` sit at the top level, is the repo root. A path that is
right in an editor and wrong in their clone fails in their CI, not ours, so
these checks run here first.

Run: python3 scripts/validate_manifests.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER_URL = "https://mcp.superme.ai"

failures: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text())


for market, manifest_path in (
    ("cursor", ".cursor-plugin/plugin.json"),
    ("grok", ".grok-plugin/plugin.json"),
):
    manifest = load(manifest_path)

    for field in ("mcpServers", "logo"):
        target = ROOT / manifest[field]
        check(target.is_file(), f"{market}: {manifest_path} -> {field} {manifest[field]!r} does not resolve from the repo root")

    check(
        manifest["repository"] == "https://github.com/superme-ai/superme-plugins",
        f"{market}: repository must point at this repo, got {manifest['repository']!r}",
    )

    # The regression this repo exists to prevent. A `variables` schema turns the
    # credential into an install-time prompt, and the `${VAR}` header it feeds
    # silences mcp.superme.ai's WWW-Authenticate challenge — so the client never
    # runs its OAuth flow and the user is back to pasting a ten-year API key.
    check("variables" not in manifest, f"{market}: manifest declares `variables`; the plugin must authenticate over OAuth")

    raw = (ROOT / manifest["mcpServers"]).read_text()
    check("${" not in raw, f"{market}: {manifest['mcpServers']} contains an unresolved ${{VAR}} placeholder")

    servers = json.loads(raw)["mcpServers"]
    check(list(servers) == ["superme"], f"{market}: expected exactly one server named 'superme', got {list(servers)}")
    server = servers["superme"]
    check("headers" not in server, f"{market}: {manifest['mcpServers']} sends headers; OAuth requires no credential")
    check(server["type"] == "http", f"{market}: expected transport 'http', got {server['type']!r}")
    check(server["url"] == SERVER_URL, f"{market}: expected {SERVER_URL}, got {server['url']!r}")

# Each catalog treats the repo root as the plugin root and walks these
# locations unconditionally. Anything added here for an unrelated reason would
# silently publish as installable plugin surface at the next SHA bump.
surface = ["skills", "commands", "agents", "rules", "hooks", "hooks/hooks.json", "mcp.json", ".mcp.json", ".lsp.json"]
stray = [p for p in surface if (ROOT / p).exists()]
check(not stray, f"unexpected plugin surface at the repo root: {stray}")

if failures:
    print("\n".join(f"FAIL  {f}" for f in failures), file=sys.stderr)
    raise SystemExit(1)
print("ok — cursor and grok manifests valid")
