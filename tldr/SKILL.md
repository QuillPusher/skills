---
name: tldr
description: Give an extreme summary of the current chat, task by task, in three groups - completed, pending, and suggested next actions. Use when the user says "tldr", "TL;DR", "/tldr", "sum up", "where are we", "recap this chat", or asks for a quick overview of what happened, what's left, or what to do next.
---

# TL;DR

Summarize this whole conversation in as few words as possible, grouped by task.

## Steps

1. Read the chat from the start and list the distinct tasks. Name each one with a single word, for example `Docs`, `Tests`, `Build`, `Config`, `Deploy`.
2. For each task, decide what's done, what's still open, and what you'd suggest next.
3. Write the three sections below. Leave out a section only if it has nothing in it.

## Format

Use three bold section labels, each followed by a flat bullet list. Don't use headings, tables or sub-bullets.

Each bullet starts with the task's category word in bold, then a colon and a space, then the point:

```
**Completed**
- **Docs**: Setup guide rewritten, links checked.
- **Tests**: Unit tests fixed, all passing.

**Pending**
- **Docs**: Owner to answer open question on limits.
- **Build**: Release build not yet tested on Windows.

**Next actions**
- **Tests**: Add coverage for the error paths.
- **Docs**: Update screenshots after the UI changes.
```

## Rules

- **Completed:** work that's finished and verified in this chat.
- **Pending:** work still open, whether yours or the user's: unanswered questions, unverified steps, decisions waiting on someone.
- **Next actions:** your own suggestions for what could come next. They aren't restatements of pending items.
- Keep each bullet to about 10 words or fewer. Use fragments, not sentences.
- One bullet per point. A task can appear in several sections.
- Use the category word exactly as the first word, in bold: one word, then a colon and a space, with the colon outside the bold (`**Docs**: `). Never put it in a heading.
- Report only what the chat shows. Don't invent status, and say "unverified" when something wasn't checked.
- Name files and links briefly and only when they help, for example `test report`.
- Nothing before or after the three sections: no introduction, no closing line.
