---
name: fix-simple-issue
description: Launch and supervise a subagent that immediately implements a triaged low-complexity issue. Use only after triage-issue returns immediate_fix_eligible yes.
---

# Fix a simple issue

Use this skill only when `triage-issue` completed successfully and returned
`immediate_fix_eligible: yes`. Never broaden eligibility beyond that result.

## Delegate the implementation

Launch one implementation subagent with the `agent` tool. Give it:

- the issue number, title, body, and acceptance criteria;
- the triage evidence and proposed solution;
- the relevant repository path and files, when known;
- the requirement to make the smallest complete change;
- the requirement to follow repository instructions and existing conventions;
- the requirement to add or update focused tests when appropriate;
- the requirement to run the repository's existing relevant validation;
- the requirement not to change unrelated code or expose secrets;
- a request to return changed files, validation results, and any blockers.

Tell the subagent to implement the fix now rather than merely describe it. Do
not ask it to repeat labeling, complexity estimation, or the triage comment.

## Supervise

1. Wait for the subagent with `read_agent`.
2. Confirm that it changed only issue-relevant files and reports successful
   relevant validation.
3. If it reports a blocker or the work is no longer clearly Low complexity,
   stop rather than improvising a larger change.
4. Return a concise implementation and validation summary to the caller.

The skill is complete only after the subagent has finished or has returned a
clear blocker.
