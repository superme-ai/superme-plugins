# SuperMe plugins

Official SuperMe plugin manifests for AI marketplaces. Each connects your editor to the
hosted SuperMe MCP server at `https://mcp.superme.ai` — ask people who've been there, get
multiple perspectives, and make better decisions about your work, without running a local
server.

```
.cursor-plugin/     Cursor Marketplace
.grok-plugin/       Grok Build (xAI plugin marketplace)
assets/             shared logo
```

There is no API key to paste. `https://mcp.superme.ai` is an OAuth 2.1 protected
resource: it serves `/.well-known/oauth-protected-resource` and
`/.well-known/oauth-authorization-server`, supports dynamic client registration and PKCE,
and answers unauthenticated requests with a `WWW-Authenticate` challenge — which is what
makes a compliant client open a browser to sign you in.

## Install

### Cursor

1. Open Cursor's **Customize** page, then the **Marketplace**.
2. Install **SuperMe** (or run `/add-plugin superme`).
3. The first time Cursor reaches for a SuperMe tool it opens a browser to sign in.
   Approve it.

#### If Cursor never asks you to sign in

Some Cursor builds never surface the sign-in control for a plugin-supplied MCP server:
the panel shows the connector but no **Accounts** row and no **Authenticate** button, and
no browser ever opens. Add the same server directly instead — this is the path Cursor's
own remote-MCP connectors use, and it prompts for sign-in normally:

[**Add SuperMe to Cursor**](https://cursor.com/en/install-mcp?name=SuperMe&config=eyJ0eXBlIjoiaHR0cCIsInVybCI6Imh0dHBzOi8vbWNwLnN1cGVybWUuYWkifQ==)

Nothing needs to change on your side: same server, same OAuth, still no API key. You can
leave the plugin installed or remove it.

### Grok Build

1. In Grok Build, run `/plugins`, open the **Marketplace** tab, and install **superme**.
2. The first time Grok reaches for a SuperMe tool it opens a browser to sign in. Grok
   stores the resulting tokens in `~/.grok/mcp_credentials.json`.

If the tools do not appear, check the `/plugins` and `/mcps` tabs of the same modal —
`Space` toggles an entry, and `i` starts the OAuth flow by hand.

## What these plugins ship

- **Scope:** the MCP server and nothing else — no skills, commands, agents, rules or
  hooks, and no local process.
- **Network endpoints:** `https://mcp.superme.ai` only.
- **Credentials:** a SuperMe account, authorized over OAuth. The plugins read no
  environment variables and no files on your machine.

## Development

Both catalogs clone this repo at a pinned commit and resolve manifest paths against the
plugin root, which here is the repo root — so `.cursor-plugin/plugin.json` declares
`./.cursor-plugin/mcp.json`, not `./mcp.json`.

```bash
python3 scripts/validate_manifests.py
```

CI runs this on every push. It checks that every declared path resolves, that neither
config carries a credential, and that both point at the same server. It also pins the
sign-in fallback: the Cursor manifest may use only field *names* Cursor's schema accepts,
its `description` must carry the fallback pointer somewhere past the halfway mark, and the
README deeplink must decode to the same server entry the plugin itself declares.

The fallback is a workaround for a Cursor client bug, not a permanent feature. On some
builds (reported across 3.14.x–3.18.x, no known fixed build) the panel lists a
plugin-supplied MCP server but never renders the **Accounts** row or the **Authenticate**
button, so OAuth never starts — there is no manifest field that fixes this, and inventing
one fails Cursor's own review. When a fixed build is old enough to be the floor in
`minClientVersions.cursor`, drop the description checks, the README section above, and
shorten the description again. It fails if `skills/`,
`commands/`, `agents/`, `rules/`, `hooks/`, `hooks/hooks.json`, `mcp.json`, `.mcp.json` or
`.lsp.json` appears at the repo root — both catalogs scan those locations, so anything added there publishes
as installable plugin surface.

Bump `.grok-plugin/plugin.json`'s `version` in the same commit as any change to that
directory — Grok's indexer skips a plugin whose version is unchanged. `.cursor-plugin/`
stays at `1.0.0`: Cursor gates every update on manual review, not on the version string,
so bumping it buys nothing and only invites drift between the two manifests.

## License

MIT — see [LICENSE](LICENSE).
