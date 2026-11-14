# Tests

Manual test cases for the skill. Each sample is seeded with known problems. Run the skill on a sample, then compare its output with the expected results.

| File | Mode | What it checks |
| --- | --- | --- |
| `docs-sample.md` | Documentation | Headings, fluff, machine tells, procedures, lists, claims flags, code and credentials |
| `ui-sample.json` | UI text | Buttons, dialogs, errors, form fields, toasts, empty states, tooltips, links, tokens, badges |
| `expected-results.md` | Both | What must change, what must be flagged, and what must stay as it is |

## Run a test

1. Copy the sample to a scratch folder. Don't run the skill on the copy in this repository, or the sample stops being a test.
2. Ask the agent to apply the skill. In Claude Code: `/oss-writing-style-skill docs` for the document, `/oss-writing-style-skill ui` for the strings, with the file attached or its path in the request. In other harnesses, ask for the writing style pass and name the mode.
3. Compare the result with `expected-results.md`.

## Pass criteria

A run passes when all four hold:

- Every item under **Must change** is changed to one of the accepted forms.
- Every item under **Must flag** appears in the flags.
- Nothing under **Must not change** is altered.
- No fact was added: no invented limit, interval, action, example value, or definition.

A **Must change** item that was flagged instead of changed is a miss. A **Must flag** item that was changed instead of flagged is a worse miss, because the agent supplied a fact.

## Report a result

Open an issue with:

- The harness and model you used
- The sample and the mode
- Which items missed, and what the agent did instead
- The first line of the report (the mode line)

Run the tests again after any change to a rule, and add a case when you add a rule.
