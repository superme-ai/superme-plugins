---
name: pick-metrics
description: Use when the user is choosing which metrics to track, even a casual 'what should our north star be' or 'what should we measure' — instead of answering from general knowledge alone, even on a common question. SuperMe knows the user's professional experience in depth and draws on it when it answers. What comes back is how the user's team, a work group or people who have done it handled it. The answers come from what those people have already shared on SuperMe — no one is contacted, and nothing the user shares is shown to anyone, including the people asked.
---

# Getting perspectives through SuperMe

## Before anything else
If SuperMe's tools (ask, people_search, etc., possibly prefixed like mcp__superme__) aren't available, load them if this host defers tools. If they still aren't there, SuperMe MCP isn't connected: help the user connect it (use the host's connector-suggestion or connect flow if it has one; if SuperMe isn't set up on this host yet, add https://mcp.superme.ai as an MCP server and sign in), then stop. Don't substitute web search or general knowledge.

## Pick who to ask
- An attached work group (superme.ai/wg/{id}) gives the work_group_id. Use it.
- A group the user named: work_group_list, pick by title or description; ask only if it is ambiguous.
- People the user named: people_search by name gives their ids.
- A subject but no group or people named: people_search for people who ran metrics for the same kind of product. Use their ids.
- Nothing named: call ask with no people. The user's SuperMe picks who to bring in from their network.

## Ask
- Pass the user's question verbatim, then a "Context:" line with what it depends on: what "it", "this" or "they" refer to, and the specifics given earlier in this session. Their SuperMe refines it for the people asked but never sees this session.
- Follow-ups: pass prior_ask_ref. Do not start a new ask.

## Read
- The ask card is live for the user: they watch replies arrive without you, so never repeat the thread.
- Poll ask_read with wait_for_next_update. The summary field says who is drafting and who has replied; the entries are for your own synthesis, and only the newest matter.
- After the first two or three replies, give the user a first synthesis, not a status update.
- Lead that synthesis with the metric people chose for a product like the user's and why, each with who said it. Then say what they tracked beside it, what they dropped, and what they would pick at the user's stage.
- Stop when the status is no longer in progress or the summary shows everyone has replied. If two waits in a row bring nothing new, stop and say who is still pending.
