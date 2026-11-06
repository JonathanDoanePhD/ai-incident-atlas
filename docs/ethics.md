# Ethics & privacy notes

**Focus on systems, not people.** The atlas is about AI systems, the organizations that build and deploy them, and
categories of harm. It is not a catalog of victims.

**Private individuals.** AIID entity lists sometimes name people who were harmed (or individual defendants). Every
one of the 5,934 entities linked to an incident was classified (`prompts/entity_kind_v1.md`) into organization,
government, product, group, generic placeholder, public figure, or private individual. The privacy-protective
default is *private individual* when in doubt. Then:
- private individuals never appear in entity lists, filters or search fields of the public app;
- their names are redacted (`[name withheld]`) from AIID titles, descriptions and report headlines in the bundle;
- extraction prompts forbid private names in summaries, and quotes containing them are downgraded to *inferred*
  (the quote is dropped);
- the committed `data/enrich/entity_kinds.csv` is keyed by a hash of the entity id, so the file itself does not
  list names. (The hash is unsalted, so it obscures rather than secures; the underlying AIID data is public.)
- tests (`tests/test_export.py`) assert that no private individual's name appears in exported summaries or entity
  lists.

Public figures (politicians, celebrities, executives) remain visible because incidents involving them (e.g.,
deepfakes) are matters of public interest, and AIID names them.

**Third-party content.** Report texts belong to their publishers and are excluded from the AIID CC license. They are
used only locally. The public app shows our own summaries, quotes of at most 25 words with source links, and
headlines truncated to 25 words.

**Untrusted input.** Report text was treated as data. Extraction instructions explicitly tell the model to ignore
instructions found in articles, and every output is validated by code.

**Tone.** Harms are described factually and without sensationalism. Organizations are named as *alleged*
developers/deployers, following AIID. Allegations in lawsuits are not presented as established facts.

**Limits of the privacy filter.** Classification of names is imperfect: a private person mistaken for a public
figure would remain visible, and redaction matches names literally (nicknames or misspellings can slip through).
Issues can be reported via the repository's issue tracker.
