# DIGEST 2026-11-08 r1579 bm-b -- E553: six "wrote <path>" messages, and who reads them back

**Study**: `scripts/e553_render_reader.py` (card E553) · **Face**: `results/state_tilt/RENDERREADER-2026-11-08.json` (+ `renderreader_latest.json`) · **Pool card**: E551 -> done.

## What the card asked

E550 (r1577) found six sites across the six `etf_phase_*` scripts where a file-naming constant is only
**rendered into a message** -- `print("wrote", OUT_PATH, "(%.0fs total)" ...)` -- and published
`no_site_that_hands_the_constant_on_reads_it_as_a_container_one_hop_out`.  A printed output path looks like
a contract: a caller could parse it, a log scraper could key on the word, a test could assert on the line.
The card asks whether anything actually does, and whether the printed path is the only machine-visible
announcement of the face it names.

## What it found

| route | rows |
|---|---|
| the writer is spawned by a source that captures its stdout | **0** |
| the writer is spawned at all | **0** |
| the render is reachable from an in-process import | **0** |
| the writer is imported, but the render sits behind `__main__` | **4** |
| the message word is parsed, but by code that never sees this line | **2** |
| nothing in the repository names or runs the writer | **0** |

**6 messages, 0 read back by machine code, 6 human-only.**  All six renders sit inside `main()`, reachable
only from `if __name__ == "__main__": sys.exit(main())`, so the four importers (etf_book_bridge,
etf_book_cagr_reconcile, etf_book_capacity_rule, etf_book_order, etf_book_width_audit, and the phase scripts
among themselves) execute the module but never that line.  **Nobody spawns any of the six**, so no stdout
exists for a spawner to capture.

The one parser in the repository is `results/_r634bma_resolve_ring3.py:59` -- a one-off ring script that
collects the `wrote` line out of a *resolve command's* output and re-prints it inside its own message.  It is
the only code that treats `wrote` as a key, and it cannot receive any of these six lines.

Announcement half: **0 canonical pointers** (`results/state_tilt/etf_phase_*_latest.json` do not exist) and
**0 source literals** (no other code or shell names the six face paths), so **6/6 faces are announced only by
the message nobody reads**.  12 `study_reference` hits sit in `calledconsumer_latest.json` and
`filepathjoined_latest.json` -- my own family's study faces naming the parents, i.e. a mention, not an
announcement.

Verdicts: `no_repository_code_reads_back_any_of_the_six_rendered_paths` and
`every_one_of_the_six_faces_is_announced_only_by_the_message_that_nobody_reads`.

## The three errors this study made and then priced

1. **"Who parses this word" is not "who reads this message".**  The first build let the single repo-wide
   parser classify all six rows as read back.  A parser is a reader of a row only when its own source also
   spawns that writer; otherwise it parses some other command's output.  The class
   `the_message_word_is_parsed_in_the_repository_but_by_code_that_never_sees_this_line` exists so that
   residue is published instead of folded into either answer.
2. **A mention is not an announcement.**  The first build searched every JSON face for the path, so six
   unrelated study faces "announced" all six victims.  Announcements are now three disjoint kinds --
   canonical pointer / source literal / study reference -- and only the first two count.
3. **An import is not an execution.**  4 of 6 writers are imported; the render is in `main()`.  Counting
   importers as readers would have published "the message is consumed" for four rows where nothing consumes it.

Also a naming defect caught during the build (E206/E462 family): the summary field was
`renders_unreachable_from_the_main_guard` while counting the rows that *are* reachable (value 6, name says 0).
Renamed to `renders_reachable_only_from_the_main_guard` and a selftest leg now asserts the name matches what
it counts.

## Cost note

First build walked the repository once per row, over a tree with 16.8k text sources and 1.2 GB of JSON under
`results/`; the selftest produced no output for 5 minutes and was killed.  One shared corpus read plus
restricting the face scan to `*_latest.json` pointer faces brings the whole 45-leg selftest to ~6 seconds
(E442's lesson, I/O face).

## Wiring

S6 leg `render_reader` (`python scripts/e553_render_reader.py check`, rc0 4.66s) · smoke leg `# E553`
(`scripts/run_e553_smoke_leg.py`, 1/1 green, `--doctor` 1/1 red) · card E553 in
`knowledge/METHODOLOGY_ASSETS.md` (20 added lines, 0 deleted).

## Bounds, published not claimed

Static only; no script is executed.  Only in-repository consumers are measured -- an external CI that greps
stdout is outside the population.  `source_literal` scans py/ps1/bat/cmd/sh, so a `.md` naming the path is not
machine-visible.  The verdict covers E550's six rows only; the repository's other `print("wrote", ...)` sites
(grep finds 40+ in `scripts/`) are the next card, not this one's answer.