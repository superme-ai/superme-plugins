# SuperMe plugins

Official SuperMe plugin manifests for AI marketplaces. Each one connects your
editor to the hosted SuperMe MCP server at `https://mcp.superme.ai`, so you can
ask people who've been there, get multiple perspectives, and make better
decisions about your work — without running a local server.

```
.cursor-plugin/     Cursor Marketplace
.grok-plugin/       Grok Build (xAI plugin marketplace)
assets/             shared logo
```

There is **no API key to paste** in either. `mcp.superme.ai` is an OAuth 2.1
protected resource: it advertises `/.well-known/oauth-protected-resource` and
`/.well-known/oauth-authorization-server`, supports dynamic client registration
and PKCE, and answers unauthenticated requests with a `WWW-Authenticate`
challenge. That challenge is what makes a compliant client open a browser to
sign you in.

## Install

### Cursor

1. Open Cursor's **Customize** page, then the **Marketplace**.
2. Install **SuperMe** (or run `/add-plugin superme`).
3. The first time Cursor reaches for a SuperMe tool it opens a browser to sign
   in. Approve it.

If the plugin connects but never offers to sign you in, add the server directly
— it runs the same flow:
[**Add SuperMe to Cursor**](https://cursor.com/en/install-mcp?name=SuperMe&config=eyJ1cmwiOiJodHRwczovL21jcC5zdXBlcm1lLmFpIn0=)

### Grok Build

1. In Grok Build, run `/plugins`, open the **Marketplace** tab, and install
   **superme**.
2. The first time Grok reaches for a SuperMe tool it opens a browser to sign in.
   Grok stores the resulting tokens in `~/.grok/mcp_credentials.json`.

If the tools do not appear, check the `/plugins` and `/mcps` tabs of the same
modal — `Space` toggles an entry, and `i` starts the OAuth flow by hand.

## What these plugins ship

- **Scope:** the MCP server and nothing else — no skills, commands, agents,
  rules or hooks, and no local process.
- **Network endpoints:** `https://mcp.superme.ai` only.
- **Credentials:** a SuperMe account, authorized over OAuth. The plugins read no
  environment variables and no files on your machine.

> **Note on token lifetime.** SuperMe currently issues the same long-lived
> unscoped token over the OAuth path as it does for a manually created API key,
> and does not yet support refresh or per-client revocation. OAuth removes the
> copy-paste and the shared team-wide key; shortening and scoping the credential
> is tracked separately.

## Layout

Both catalogs clone this repo at a pinned commit and resolve manifest paths
against the **plugin root**, which here is the repo root — so
`.cursor-plugin/plugin.json` declares `./.cursor-plugin/mcp.json`, not
`./mcp.json`. `scripts/validate_manifests.py` checks that every declared path
resolves from the repo root, that neither config carries a credential, and that
both point at the same server. CI runs it on every push.

Keep the repo root free of `skills/`, `commands/`, `agents/`, `rules/`,
`hooks/`, `mcp.json` and `.mcp.json` — both catalogs scan those locations
unconditionally, so anything added there publishes as installable plugin
surface at the next commit bump. The validator fails if one appears.

## Shipping an update

**Cursor** does not auto-update a listing from source — every plugin update is
manually reviewed before it goes live. Submit changes at
[cursor.com/marketplace/publish](https://cursor.com/marketplace/publish).

**Grok Build** re-pins only when `.grok-plugin/plugin.json`'s `version` changes
— xAI's `bump-plugin-shas.py` skips a plugin whose version is unchanged
("commits moved, release did not").

Either way, bump the relevant `plugin.json` `version` in the same commit as any
change to that plugin's directory, or the change sits on `main` and reaches no
installed user.

## License

MIT — see [LICENSE](LICENSE).
