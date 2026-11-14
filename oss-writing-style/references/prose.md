# Prose

Sentence-level rules. They apply to a button label as much as to a deployment guide. Each rule includes its fidelity limit: the point past which applying it would change a fact.

Tables show each rule as a before and an after. They illustrate the rule. They are not phrases to find and replace.

## Cut words, not facts

Every word should do work.

| Cut this | Write this |
| --- | --- |
| in order to | to |
| has the ability to, is able to | can |
| provides the capability to | lets you |
| used for the purpose of | used for |
| owing to the fact that, due to the fact that | because |
| in spite of the fact that | although |
| in the event that | if |
| prior to | before |
| at this point in time | now |
| the question as to whether | whether |
| in a timely manner | promptly |
| a number of | several, or the number if the source gives it |

| Before | After |
| --- | --- |
| The system provides the capability to assign tasks to teammates who are currently available. | Assign tasks to available teammates. |
| Click here to save your changes | Save |

**Limit.** A qualifier that states real behavior is a fact, not filler. _May, up to, at least, typically, only when_ describe how the product behaves. Keep them.

## Say what is, not what isn't

State things in positive form when the positive form means exactly the same thing.

| Before | After |
| --- | --- |
| The report does not include test accounts. | The report excludes test accounts. |
| Notifications are not turned on. | Notifications are off. |

**Limit.** Don't convert a prohibition ("Do not restart the service during a deployment") or a scope exclusion ("This setting does not apply to archived projects"). The negative is the fact. Don't infer a positive the source didn't state: "isn't signed out for 8 hours" doesn't mean "stays signed in for 8 hours."

## Flag vague claims, don't sharpen them

Vague phrases hide a missing fact: an interval, a count, a limit, a condition. You can't supply it.

| Vague phrase | Flag as |
| --- | --- |
| Updates in near real time. | State the refresh interval. |
| Shows key events. | Which events, and how many? |
| Scales to meet enterprise needs. | State the limit, or cut the sentence. |

Rewrite only when the specific value appears elsewhere in the source. Then use it.

## Use nouns and verbs

Nouns and verbs carry a sentence. Most adjectives and adverbs are padding.

| Before | After |
| --- | --- |
| The backlog was very quickly cleared out. | The backlog cleared. |
| Significantly reduces overall build time. | Reduces build time. |

The words to cut are in the Words table in `terminology.md`.

## Keep parallel ideas parallel

Items in a list, headings at one level, and steps in a procedure take the same grammatical form.

| Before | After |
| --- | --- |
| Create a project, members should be added, and then the access rule needs setting. | Create a project. Add members. Set the access rule. |
| Pending, Being processed, Done | Pending, Processing, Done |

## Keep modifiers next to what they modify

| Before | After |
| --- | --- |
| Archived projects are only exported on request. | Archived projects are exported only on request. |
| After failing three health checks, the system marks the server as Offline. | A server that fails three health checks is marked Offline. |

In the second before, the system didn't fail the health checks. The opening phrase attaches to the wrong subject.

**Limit.** Move a modifier only when the intended meaning is clear from the source. If _only_ could attach to two words and change the meaning either way, flag it.

## Lead with the point

Readers scan. Put the key word first in a heading, a label, a list item, and the first sentence of a paragraph. Inside a sentence, don't let the point trail off into a weak closing clause.

| Before | After |
| --- | --- |
| An error occurred when the system attempted to export, which may be related to the file path. | Export failed. Check the file path. |
| Settings for the project | Project settings |

## Use present tense

_Opens,_ not _will open._ Present tense describes how the product behaves now.

**Limit.** A sentence about the future ("will be available in the next release") is a fact about timing. Don't move it to the present. Flag it under Claims.

## Use active voice

The subject does the action ("The connector retries the request").

**Limit.** Convert passive to active only when the actor is named or obvious. "The file is deleted" has no actor. Leave it, or flag it. Passive is also right when it keeps blame off the reader ("The password wasn't recognized") or when the receiver is the point ("Requests are sent to the first available server").

## Write facts as statements and steps as commands

"The dashboard refreshes every 15 seconds." "Select **Save**." Don't phrase advice as a wish. "Back up the database before you upgrade," not "It is recommended that you consider backing up the database."

## Use contractions

Use common contractions: _it's, you're, don't, can't, isn't._ Avoid unusual ones (_it'd, should've, there're_) and contractions of nouns ("the project's been archived").

**Limit.** Legal text keeps its exact wording.

## Make the meaning of _-ing_ words clear

A heading like "Scheduling reports" can mean how to schedule a report or reports about scheduling. If the source makes the meaning clear, rewrite to that meaning ("Schedule a report"). If it doesn't, flag it.

## Keep chains of prepositions short

More than two prepositional phrases in a row are hard to follow.

| Before | After |
| --- | --- |
| the status of the sync of the files in the folder of the project | the sync status for files in the project folder |

## Write for global readers

- One idea per sentence.
- Keep _that_ when it helps parsing: "Make sure that the sync finished."
- Replace idioms and sports metaphors when the plain meaning is clear: "out of the box" becomes "by default." If it isn't clear, flag it.
- Replace Latin abbreviations (list in `terminology.md`).
- A season used as a date ("the spring release") is ambiguous across hemispheres. Flag it. Don't guess the month.

## Documentation only

**One topic per paragraph, stated in the first sentence.** A reader who reads only the first sentence of each paragraph should still follow the argument. Reorder sentences to get there. Don't cut one that carries a fact.

**Don't explain twice.** If the same fact appears twice in different words, keep the clearer copy and delete the other. If the two copies differ in substance, flag the conflict.
