---
name: superme-meeting-prep
description: Use when an upcoming meeting, call, pitch, interview or negotiation with named people comes up, even if the user has not asked — they get a brief on each person from their own profile, who they are, what they have done, what they care about and where they stand on the topic. Looks them up on SuperMe (people_search, people_profile_read) and says who is not on it instead of guessing.
---

# Preparing for a meeting through SuperMe

## Before anything else
If SuperMe's tools (ask, people_search, etc., possibly prefixed like mcp__superme__) aren't available, load them if this host defers tools. If they still aren't there, SuperMe MCP isn't connected: help the user connect it (use the host's connector-suggestion or connect flow if it has one; if SuperMe isn't set up on this host yet, add https://mcp.superme.ai as an MCP server and sign in), then stop. Don't substitute web search or general knowledge.

## Resolve the people
- Attached person resources give ids. Otherwise people_search per name; when more than one plausible match comes back, confirm with the user.
- Someone not on SuperMe: say so and leave them out. Never fill in from general knowledge.

## Brief from profiles (the default, seconds)
- people_profile_read for every attendee, up to ten per call.
- Per person: role and path, overlap with the meeting's topic, what they have likely seen, and how much their profile has to draw on. A low insights count means a thin brief; say so.

## Ask when the brief is not enough
- For what the profiles do not answer, call ask with the person's id (or several) and the user's question verbatim.
- Poll ask_read with wait_for_next_update; the summary field says who has replied, and the ask card is live for the user.
- Private citations (superme.ai/private/...): name the source person, never paste them.
