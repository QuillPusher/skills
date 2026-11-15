# tldr

An AI Agent skill that recaps the current chat, task by task, in as few words as possible.

## What it does

When invoked, it reads the conversation and lists every distinct task by a one-word name (e.g. `Docs`, `Tests`, `Build`), then reports on each in three groups:

- **Completed** — work finished and verified in this chat
- **Pending** — work still open, whether yours or the user's
- **Next actions** — suggestions for what could come next

Sections with nothing in them are omitted. No preamble, no closing line.

## Example output

```
**Completed**
- **Docs**: Setup guide rewritten, links checked.
- **Tests**: Unit tests fixed, all passing.

**Pending**
- **Build**: Release build not yet tested on Windows.

**Next actions**
- **Tests**: Add coverage for the error paths.
```

## Install

Copy `SKILL.md` into your skills directory