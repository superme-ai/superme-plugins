---
name: superme-meeting-prep
description: Use when the user is preparing to meet people and wants a brief on who they are and where they stand.
---

# Preparing for a meeting through SuperMe

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
