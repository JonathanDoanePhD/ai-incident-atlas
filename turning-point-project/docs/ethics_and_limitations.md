# Ethics and limitations

Status: draft v0.1.

## Data use

- **Secondary data only, public-use first.** Paper 1 is designed to use de-identified public-use
  files. Restricted-use files (e.g. geocodes, full Add Health samples) would require the data
  steward's licence, a security plan, and institutional approval; none are requested yet.
- **No microdata in the repository.** `.gitignore` excludes `data/raw/` and `data/processed/`
  and common survey file formats; `tpp check-repo` and a unit test fail if any are tracked.
- **No re-identification.** Data-use terms for these studies prohibit attempts to identify
  respondents. We will not link files to outside data at the individual level, and the website
  will show only model estimates and aggregate tabulations with small-cell suppression
  (minimum cell size 10 by default; follow stricter steward rules where they exist).
- **IRB status.** Whether analysis of public-use, de-identified secondary data is "not human
  subjects research", exempt, or requires review is an institutional determination. It must be
  obtained from the researcher's institution (or an independent IRB) and recorded in
  `research_decision_log.md` before outcome analyses begin. Do not assume either answer.

## Framing and harms

- No model in this project is intended or validated to classify individual young people.
  Predictive models (Study A) are used to understand which factors carry information, and are
  audited for calibration across groups only in aggregate.
- Family circumstances (household structure, caregiver substance use, poverty) are contexts.
  Reporting will avoid deficit language and will not present household structure as a cause
  without a design that supports that.
- Demographic and equity variables are analysed only in aggregate.
- Misclassification risk: if findings were ever used to target services, false negatives would
  deny support and false positives could stigmatise. Any future targeting should favour
  universal or self-referral access over prediction-based gatekeeping.

## Independence from the motivating narrative

The researcher's goal of founding a mentoring organisation creates a conflict of interest toward
finding that mentoring matters and that a particular window (e.g. freshman year) matters. Safeguards:
preregistration of the primary contrast before outcome data are examined; reporting all
preregistered results regardless of direction; an explicit smallest effect size of interest so
that nulls are informative; and disclosure of the motivation in any paper.

## Future primary data collection (not part of this phase)

School- or community-based research with minors would need, at minimum: IRB review; parental or
guardian permission and child assent; district research approval; FERPA-compliant handling of
education records; a data management and security plan; mandated-reporter protocols for mentors and
researchers; mentor screening (background checks) and training; and procedures for withdrawal and
data destruction. A trial of a mentoring programme should be registered (e.g. on a public registry)
before enrolment.

## Known limitations of the overall design

1. Adolescent-start cohorts cannot compare middle childhood with adolescence.
2. Single-cohort age contrasts are confounded with cohort, grade and calendar period.
3. Observational associations between support and attainment are vulnerable to selection of
   more engaged youth into supportive relationships.
4. Public-use files sometimes omit variables or subsamples available in restricted files.
5. The cohorts studied (born 1980s–1990s) grew up in different institutional contexts than
   young people today; transportability to current programme populations is uncertain.
