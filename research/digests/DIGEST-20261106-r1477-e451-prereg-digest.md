# E451 -- a study's claim to follow a prereg is prose unless a face carries its digest

Round r1477 bm-b, 2026-11-06. Card `E451-WHICH-STUDY-THAT-CITES-ITS-PREREG-NOTE-CARRIES-NO-DIGEST-OF-IT`.

## What was asked

E449 (r1468) published seven `research/*.md` notes that a study script names through a `PREREG`
constant, that code text cites by filename, and that **no opener in the corpus opens** -- the
constant is assigned once and never read again. The card asks the obvious next question: if the note
constrains the study, does any artifact the study publishes carry a digest of it?

## What was measured

Population = E449's seven rows, re-derived rather than inherited:

| step | count |
| --- | --- |
| `.py` files walked | 12,210 |
| naming sites (file names the note basename) | 32 over 31 distinct files |
| naming files that publish any `results/` face | 28 |
| of those, the study's **own** producer (basename carries the study slug) | 11 |
| faces probed from own producers | 24 |
| faces probed from every naming producer | 84 |
| face targets absent from disk | 10 |
| naming files that publish no face (published as residue) | 4 |

Digest evidence, per face that exists today: a value equal to the note's current sha256 (full, or a
hex prefix of at least 12 chars), or a keyed ISO as-of date on a prereg/note field.

## The reading

**Zero.** 0 faces carry a full sha256, 0 a hex prefix, 0 a keyed as-of. Verdict:

```
no_study_publishes_a_digest_of_the_prereg_note_it_names
```

All seven studies land in `note_named_but_no_digest`; none falls back to
`note_not_named_by_its_own_producer`, so the zero is about missing digests, not missing producers.

## The near miss, which is the actual finding

65 faces name a prereg field or the study stem and carry no digest; 23 of them are written by an own
producer. Two of the seven studies record their freeze in prose, and they disagree about the same
document:

- `results/fund_divlowvol_p1/probe.json` →
  `prereg_state = "FROZEN v1.0 (2026-10-03 bm-b r610 five-condition freeze window)"`
- `results/_fund_divlowvol_p1_transfer_probe.json` →
  `prereg = "research/FUND-DIVLOWVOL-P1.md (DRAFT-NOT-FROZEN)"`

Same note (`research/FUND-DIVLOWVOL-P1.md`), a frozen state in one face and an unfrozen state in the
other, and neither string is checkable: a date inside a sentence cannot be keyed on, it does not name
bytes, and the note may have been edited since either face was written. That is the concrete cost of
a claim without a digest -- two artifacts of one study contradict each other about the document that
is supposed to bind the study, and no machine can adjudicate.

## The law

A "frozen prereg" is machine-checkable only if the producer's own face carries `prereg_sha256` (the
note's bytes, or a prefix of at least 12 hex chars) or a keyed ISO `prereg_as_of`. A date inside a
sentence is not a pin. Publish prose freeze strings as claims; never count them as pins.

## Wiring and verification

- producer `scripts/e451_prereg_digest.py` — `selftest 30/30`, `run` rc0, `check problems=[]`,
  `verify problems=[]`
- face `results/state_tilt/prereghash_latest.json` + `PREREGHASH-2026-11-06.json`
- smoke leg `e451 which study that names a prereg note publishes a digest of it` — 1/1 green
  standalone, 1/1 red on a doctored class promotion, face restored byte-identically
  (`sha in == sha out`, `714ec867...`)
- S6 leg `prereg_digest` (`verify`, one corpus walk, 3.8 s)
- card `knowledge/METHODOLOGY_ASSETS.md` E451 (numstat 45/0)