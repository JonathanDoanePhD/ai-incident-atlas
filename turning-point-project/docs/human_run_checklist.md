# Checklist for human-run analyses (PSID, FFCWS, Add Health)

These datasets' terms prohibit, or require prior permission for, processing with AI tools. The plans and scripts were written by
Claude from public documentation only. A person runs them, outside AI tools.

1. **Download the data yourself** under the provider's terms (PSID Data Center; ICPSR/OPR for FFCWS; Add Health Dataverse or ICPSR 21600).
2. **Switch off AI assistants** for the session: no AI coding assistant in the editor, and no chatbot holding the data or output.
3. **Do not upload, paste or describe** data files, rows or values to any AI tool, including this project's Claude sessions.
4. **Run the script** from a terminal (commands below), writing output to a folder **outside** the repository.
5. **Before sharing even aggregate results with an AI tool**, get written permission from the data provider. Until then, interpret and
   write up results yourself.
6. **Record** the data release, the date, and the plan SHA-256 that each script prints.

| Study | Plan | Script and command |
|---|---|---|
| A3 Add Health mentor onset | `docs/sap_addhealth_mentor_timing.md` | see `docs/addhealth_human_analyst_checklist.md` — **run completed locally by the PI 2026-11-13 (D-032); results kept local** |
| R1 PSID closeness 8–11 vs 12–15 | `docs/sap_psid_childhood_replication.md` | `python scripts/psid_offline/run_psid_closeness_timing.py --data <PSID Data Center CSV/Stata export> --edu ER34548 [more education vars] --sex <sex var> --birthyear <year-born var> --out <folder>` — **run completed locally by the PI 2026-11-13; all three timing comparisons inconclusive (D-035); results kept local** |
| R2 FFCWS age 9 vs 15 | `docs/sap_ffcws_age9_age15.md` | `python scripts/ffcws_offline/run_ffcws_age9_age15.py --files <baseline file> <year-9 file> <year-15 file> <year-22 file> --out <folder>` — **run completed locally by the PI 2026-11-13; primary timing comparison inconclusive (D-034); results kept local** |

**PSID Data Center cart (one individual-level file):** `ER30001`, `ER30002`, sex and year born (individual file), the "YEARS
COMPLETED EDUCATION" variables for 2015 onward (e.g. `ER34548`), `ER16462`, `ER15928`, and from the CDS child files `Q23H5A`,
`Q23H5G`, `Q23H5H`, `Q33H5A`, `Q33H5G`, `Q33H5H`, `CH07PRWT`. Export as CSV or Stata.
