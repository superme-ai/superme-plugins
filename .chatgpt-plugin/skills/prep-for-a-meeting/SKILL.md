---
name: prep-for-a-meeting
description: Use whenever the user asks to prep for a meeting, call, pitch, interview or negotiation with named people, or asks who someone they are about to meet or work with is, even a plain 'I'm meeting X tomorrow', and when such a meeting comes up even if they have not asked. Looks them up on SuperMe instead of answering from memory or the web (people_search, people_profile_read) — they get a brief on each person from their own profile, who they are, what they have done, what they care about and where they stand on the topic — and says who is not on it instead of guessing.
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
- For what the profiles do not answer, call ask with the person's id (or several) and the user's question verbatim, then a "Context:" line with what it depends on: what "it", "this" or "they" refer to, and the specifics given earlier in this session.
- Poll ask_read with wait_for_next_update; the summary field says who has replied, and the ask card is live for the user.

## Routine
- A meeting that repeats with the same people fits a run on the morning of each one, on the meeting's own cadence (weekly for a weekly meeting). If the user wants this regularly, offer a scheduled task on this host after the brief: fill the template below from this session and show it to the user before creating it.
- Standing question: "What will {attendees} push on about {topic} at {meeting}, and what should I have ready?", then a "Context:" line with what stays true from run to run.
- What to lead with: what is new in their profiles since the last brief, and the one thing to have ready.
- In the template, first call people_profile_read for the attendees' user_ids, then call ask with those user_ids in place of the work group.
- Template. The task text carries everything, so it works without memory on this host:
  ```
  Schedule: {cadence}, at {time in the user's time zone}.
  Call SuperMe's ask tool (load it if this host defers tools) with work_group_id "{work_group_id}" (the work group "{work group name}"), or the same user_ids when this session's ask went to people, and this question and its Context: line, word for word: {question}
  Poll ask_read with wait_for_next_update until the status is no longer in progress or everyone has replied. If SuperMe's tools are not there, say so and stop.
  Give a short synthesis, each point with who said it. Lead with what changed since the last answer, then {what to lead with}. Last answer: {the answer from this session, in brief}.
  ```
