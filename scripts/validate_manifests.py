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
REPO_URL = "https://github.com/superme-ai/superme-plugins"

# Cursor renders the manifest `description` in its plugin panel and nothing else we author,
# so the sign-in fallback has to survive inside that one string. It can only carry a pointer,
# not the deeplink itself, which lives in README.md.
#
# Why the fallback exists: mcp.superme.ai currently requires authorization from the very
# first request of the MCP handshake, so a client cannot complete `initialize` or read the
# tool list before signing in. With no negotiated session there is nothing for the plugin
# panel to attach an account to, so it shows the connector with no Accounts row and no
# Authenticate button. The fix belongs in the server, not in any manifest field.
#
# Removing this: once the server lets a client finish the handshake and list tools
# unauthenticated, and challenges at call time instead, drop the two description checks
# below, the README section, and shorten the description again.
FALLBACK_POINTER = REPO_URL.removeprefix("https://")
INSTALL_DEEPLINK = re.compile(r"https://cursor\.com/(?:[a-z]{2}/)?install-mcp\?\S+?(?=[)\s])")

# Mirrors the properties of cursor/plugins schemas/plugin.schema.json, which is
# `additionalProperties: false` — checked against that schema 2026-09-12, 21/21 exact:
# https://github.com/cursor/plugins/blob/main/schemas/plugin.schema.json
# It has no auth, oauth, account, connector, credential, token or secret property; every
# "auth" substring in it is the word "author". That is the point of pinning it: a missing
# Authenticate button tempts an invented auth field, which this schema cannot accept and
# which would not help anyway — the affordance depends on the server, not the manifest.
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


cursor = load(".cursor-plugin/plugin.json")
unknown = sorted(set(cursor) - CURSOR_MANIFEST_FIELDS)
check(not unknown, f"cursor: plugin.json declares field names Cursor's schema rejects: {unknown} (if Cursor added one, re-sync CURSOR_MANIFEST_FIELDS)")

description = cursor.get("description") or ""
check(FALLBACK_POINTER in description, f"cursor: description must carry the sign-in fallback pointer {FALLBACK_POINTER!r}")
# A listing that leads with a workaround is worse than the bug it explains, and list views
# truncate the tail. Requiring the pointer past the halfway mark keeps the value proposition
# in front without pinning the prose — and unlike splitting on sentences, it cannot be
# satisfied by prefixing a short throwaway clause like "Note. " or "E.g. ".
if FALLBACK_POINTER in description:
    check(
        description.index(FALLBACK_POINTER) >= len(description) // 2,
        "cursor: description leads with the sign-in fallback; the value proposition must come first",
    )

for market, manifest_path in (
    ("cursor", ".cursor-plugin/plugin.json"),
    ("grok", ".grok-plugin/plugin.json"),
):
    manifest = load(manifest_path)

    # Report a missing key instead of tracebacking over the failures collected so far.
    missing = [f for f in ("mcpServers", "logo", "repository") if f not in manifest]
    check(not missing, f"{market}: {manifest_path} is missing {missing}")
    if missing:
        continue

    for field in ("mcpServers", "logo"):
        target = ROOT / manifest[field]
        check(target.is_file(), f"{market}: {manifest_path} -> {field} {manifest[field]!r} does not resolve from the repo root")

    check(
        manifest["repository"] == REPO_URL,
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

# The pointer is only worth anything if the page it names still carries a deeplink that
# installs the same server, over the same transport, as the plugin itself.
readme = (ROOT / "README.md").read_text()
deeplinks = INSTALL_DEEPLINK.findall(readme)
check(bool(deeplinks), "README.md must keep a cursor.com install-mcp fallback link for users Cursor never prompts")
# The loop above already reported a missing mcpServers; don't traceback over its failures.
expected = json.loads((ROOT / cursor["mcpServers"]).read_text())["mcpServers"]["superme"] if "mcpServers" in cursor else None
for link in deeplinks if expected else []:
    encoded = parse_qs(urlsplit(link).query).get("config", [""])[0]
    padded = encoded + "=" * (-len(encoded) % 4)
    try:
        config = json.loads(base64.urlsafe_b64decode(padded))
    except Exception as exc:  # noqa: BLE001 - any decode failure is the same defect
        failures.append(f"README.md: install deeplink config is not decodable base64 JSON ({exc})")
        continue
    check(config == expected, f"README.md: install deeplink installs {config}, but the plugin declares {expected}")

# Both catalogs scan these locations at the plugin root, so anything added here
# publishes as installable plugin surface at the next pinned commit.
surface = ["skills", "commands", "agents", "rules", "hooks", "hooks/hooks.json", "mcp.json", ".mcp.json", ".lsp.json"]
stray = [p for p in surface if (ROOT / p).exists()]
check(not stray, f"unexpected plugin surface at the repo root: {stray}")

if failures:
    print("\n".join(f"FAIL  {f}" for f in failures), file=sys.stderr)
    raise SystemExit(1)
print("ok — cursor and grok manifests valid")
