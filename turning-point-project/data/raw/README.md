# data/raw

Put downloaded survey extracts here. **Everything in this folder except this README is git-ignored.**

Do not commit microdata, even public-use files: their licences restrict redistribution, and
Add Health / NCES / BLS terms prohibit attempts to re-identify respondents.

Expected layout (one sub-folder per study):

```
data/raw/
  nlsy97/       NLS Investigator CSV extract + the .NLSY97 tagset used to create it
  addhealth/    Add Health public-use files (from ICPSR study 21600, after accepting the terms)
  els2002/      NCES public-use files
  hsls09/       NCES public-use files
```

Record in `docs/research_decision_log.md` which release/version of each file was used.
`tpp validate <dataset> <file>` writes a provenance manifest (SHA-256, size, mapping) to
`data/processed/` so results can be tied to an exact input file.
