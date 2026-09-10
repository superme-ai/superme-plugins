#!/usr/bin/env python3
"""Validate the marketplace manifests the way each catalog reads them.

Both catalogs clone this repo at a pinned SHA and resolve manifest paths against
the plugin root, which here is the repo root.

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

    # A `variables` schema turns the credential into an install-time prompt, and
    # the `${VAR}` header it feeds silences mcp.superme.ai's WWW-Authenticate
    # challenge — so the client never runs its OAuth flow.
    check("variables" not in manifest, f"{market}: manifest declares `variables`; the plugin must authenticate over OAuth")

    raw = (ROOT / manifest["mcpServers"]).read_text()
    check("${" not in raw, f"{market}: {manifest['mcpServers']} contains an unresolved ${{VAR}} placeholder")

    servers = json.loads(raw)["mcpServers"]
    check(list(servers) == ["superme"], f"{market}: expected exactly one server named 'superme', got {list(servers)}")
    server = servers["superme"]
    check("headers" not in server, f"{market}: {manifest['mcpServers']} sends headers; OAuth requires no credential")
    check(server["type"] == "http", f"{market}: expected transport 'http', got {server['type']!r}")
    check(server["url"] == SERVER_URL, f"{market}: expected {SERVER_URL}, got {server['url']!r}")

# Both catalogs scan these locations at the plugin root, so anything added here
# publishes as installable plugin surface at the next pinned commit.
surface = ["skills", "commands", "agents", "rules", "hooks", "hooks/hooks.json", "mcp.json", ".mcp.json", ".lsp.json"]
stray = [p for p in surface if (ROOT / p).exists()]
check(not stray, f"unexpected plugin surface at the repo root: {stray}")

if failures:
    print("\n".join(f"FAIL  {f}" for f in failures), file=sys.stderr)
    raise SystemExit(1)
print("ok — cursor and grok manifests valid")
