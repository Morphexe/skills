---
name: mine-session-skills
description: Looks back over recent Codex, Claude, Pi, memory, and optional Chronicle evidence to identify repeated manual workflows worth packaging as skills, subagents, or automations. Use when the user asks to review recent work, mine sessions/history/memories, find repeatable workflows, or create missing skills/agents/automations from recurring work.
---

# Mine Session Skills

## Goal

Review the last 30 days of available work history, or all available history if shorter, to find repeated manual workflows that are worth packaging. Prefer extending existing skills, agents, or automations over creating duplicates.

## Evidence order

1. **Recent Codex sessions and task summaries** — primary evidence.
2. **Codex Memories and rollout summaries** — use to find patterns repeated across sessions.
3. **Chronicle, if enabled** — discovery only. Confirm important details in the relevant source system when possible.
4. **Existing skills, custom agents, and automations** — prior art to reuse or extend.

Use the helper for local agent logs when useful:

```bash
python skills/productivity/mine-session-skills/scripts/extract_user_requests.py --limit 80
```

It scans common Claude, Codex, and Pi JSONL logs. If it misses a format, inspect recent files manually and summarize only what is needed.

## Candidate criteria

Only act on a candidate when it meets all of these:

- occurred at least twice, or is clearly likely to recur and costly to repeat;
- has stable inputs, a repeatable procedure, and a clear output or stopping condition;
- would materially improve speed, quality, consistency, or reliability;
- is not already adequately covered by an existing skill, agent, script, or automation.

Look broadly across coding, research, writing, planning, communication, operations, analysis, and personal administration. Favor work that is repeated, time-consuming, error-prone, context-heavy, or benefits from a consistent process.

## Choose the smallest form

- **Skill** — reusable workflow or playbook.
- **Custom subagent** — bounded specialist role or investigation task suitable for delegation.
- **Automation** — scheduled or recurring check, report, reminder, or monitor.
- **Extend existing** — current asset is close but incomplete.
- **Skip** — too one-off, ambiguous, sensitive, poorly evidenced, or already covered.

## Workflow

1. Define the time window: last 30 days, or all available history if shorter.
2. Gather evidence in the order above. Record source, date, and a short sanitized summary.
3. Cluster repeated workflows by intent, not wording or tool.
4. Compare each cluster against existing skills, custom agents, scripts, cron jobs, and docs.
5. Produce a compact shortlist first. Do not create anything until the high-confidence missing items are clear.
6. Create only high-confidence missing items, keeping them narrow, practical, source-aware, and easy to validate.
7. Update the relevant indexes/configs when adding repo-managed skills or agents.

## Shortlist format

```md
## Workflow packaging shortlist

- **Repeated workflow:** ...
  - Evidence and dates: ...
  - Frequency / confidence: ...
  - Recommended form: skill | subagent | automation | extend existing | skip
  - Why worth creating or skipping: ...
```

## Final response format

End with:

```md
## Created or extended
- ...

## Deliberately skipped
- ...

## Needs more evidence
- ...
```

## Guardrails

- Do not quote sensitive content; summarize it.
- Treat Chronicle as discovery only unless details are confirmed elsewhere.
- Do not package speculative, overlapping, or overly broad assets.
- Prefer extending existing assets over duplicating them.
- If evidence is thin, output the shortlist and ask before creating anything.
