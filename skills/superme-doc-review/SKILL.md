---
name: superme-doc-review
description: Use when the user wants feedback on a doc, draft or plan.
---

# Getting feedback on a doc through SuperMe

## Pick who to ask
- An attached work group (superme.ai/wg/{id}) gives the work_group_id. Use it.
- A group the user named: work_group_list, pick by title or description; ask only if it is ambiguous.
- People the user named: people_search by name gives their ids.
- A subject but no group or people named: people_search finds people who've worked on it. Use their ids.
- Nothing named: call ask with no people. SuperMe brings in the people whose experience fits.

## Get the doc in
- Attach it through file_upload and pass the file id to ask. The doc goes to the profiles you ask, not to the people behind them.
- No doc yet: ask for a link or the text. Never invent what the doc says.

## Ask
- Pass the user's request verbatim with the doc attached. The user's SuperMe frames it for the people asked.
- Follow-ups: pass prior_ask_ref. Do not start a new ask.

## Read
- The ask card is live for the user: they watch replies arrive without you, so never repeat the thread.
- Poll ask_read with wait_for_next_update. The summary field says who is drafting and who has replied; the entries are for your own synthesis, and only the newest matter.
- After the first two or three replies, give the user a first synthesis, not a status update.
- Stop when the status is no longer in progress or the summary shows everyone has replied. If two waits in a row bring nothing new, stop and say who is still pending.
- Private citations (superme.ai/private/...): say they exist, never paste them.
