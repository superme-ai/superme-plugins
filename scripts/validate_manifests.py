#!/usr/bin/env python3
"""Validate the marketplace manifests the way each catalog reads them.

Both catalogs clone this repo at a pinned SHA and resolve manifest paths against
the plugin root, which here is the repo root.

Run: python3 scripts/validate_manifests.py
"""

import base64
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SERVER_URL = "https://mcp.superme.ai"

# Where a Marketplace user is sent when Cursor never offers them a sign-in. Cursor renders
# the manifest `description` in the plugin panel and nothing else we author, so the pointer
# has to survive inside that one string; the link itself lives in README.md.
FALLBACK_POINTER = "github.com/superme-ai/superme-plugins"
INSTALL_DEEPLINK = "https://cursor.com/en/install-mcp"

# cursor/plugins schemas/plugin.schema.json is `additionalProperties: false` and has no
# auth, oauth, account, connector or token property. The missing Authenticate button is a
# client bug, not a missing manifest field — adding one here would fail the catalog's own
# validation while fixing nothing, so pin the accepted set.
CURSOR_MANIFEST_FIELDS = {
    "name", "displayName", "description", "version", "minClientVersions", "author",
    "publisher", "homepage", "repository", "license", "logo", "keywords", "category",
    "tags", "commands", "agents", "skills", "rules", "hooks", "variables", "mcpServers",
}

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

cursor = load(".cursor-plugin/plugin.json")

check(
    not (set(cursor) - CURSOR_MANIFEST_FIELDS),
    f"cursor: plugin.json declares fields Cursor's schema rejects: {sorted(set(cursor) - CURSOR_MANIFEST_FIELDS)}",
)

# The sign-in fallback rides in `description`, but a listing that leads with a workaround
# reads like a bug notice — and marketplace views truncate. Keep the pointer out of the
# first sentence so the value proposition is what survives either way.
description = cursor["description"]
lead, _, rest = description.partition(". ")
check(FALLBACK_POINTER in rest, f"cursor: description must carry the sign-in fallback pointer {FALLBACK_POINTER!r} after its opening sentence")
check(FALLBACK_POINTER not in lead, "cursor: description leads with the sign-in fallback; the value proposition must come first")
check(
    cursor["repository"].endswith(FALLBACK_POINTER),
    f"cursor: description points at {FALLBACK_POINTER!r} but repository is {cursor['repository']!r}",
)

# The pointer is only worth anything if the page it names still carries a deeplink that
# installs *this* server over the remote-MCP path.
readme = (ROOT / "README.md").read_text()
deeplinks = re.findall(rf"{re.escape(INSTALL_DEEPLINK)}\?\S+?(?=[)\s])", readme)
check(bool(deeplinks), f"README.md must keep an {INSTALL_DEEPLINK} fallback link for users Cursor never prompts")
for link in deeplinks:
    encoded = parse_qs(urlsplit(link).query).get("config", [""])[0]
    padded = encoded + "=" * (-len(encoded) % 4)
    try:
        config = json.loads(base64.urlsafe_b64decode(padded))
    except Exception as exc:  # noqa: BLE001 - any decode failure is the same defect
        failures.append(f"README.md: install deeplink config is not decodable base64 JSON ({exc})")
        continue
    check(config.get("url") == SERVER_URL, f"README.md: install deeplink resolves to {config.get('url')!r}, expected {SERVER_URL}")

# Both catalogs scan these locations at the plugin root, so anything added here
# publishes as installable plugin surface at the next pinned commit.
surface = ["skills", "commands", "agents", "rules", "hooks", "hooks/hooks.json", "mcp.json", ".mcp.json", ".lsp.json"]
stray = [p for p in surface if (ROOT / p).exists()]
check(not stray, f"unexpected plugin surface at the repo root: {stray}")

if failures:
    print("\n".join(f"FAIL  {f}" for f in failures), file=sys.stderr)
    raise SystemExit(1)
print("ok — cursor and grok manifests valid")
