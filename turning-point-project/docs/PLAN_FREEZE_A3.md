# Analysis plan freeze: study A3 (Add Health, human-run)

Frozen 2026-11-13T00:58Z. Written from Add Health public codebooks and the analysis guidelines only. No Add Health respondent data have been accessed by any AI tool. The run is to be performed by a human analyst outside AI tools (docs/addhealth_human_analyst_checklist.md).

```
e79ae3694a3ea7a43f8e9eaf9a247f0d033f0632a479c9cbfa246fabe01d7d9a  docs/sap_addhealth_mentor_timing.md
7d841a334830d670ebdf393525f703de204b83575eaafca2ca3fc866d75a786b  scripts/addhealth_offline/run_addhealth_mentor_timing.py
c21eccf7120eea28c05cfe7bdcd9e74ca2b25f7387f62fb97aeddf9857de05bc  docs/addhealth_human_analyst_checklist.md
```

## Amendment 1 (2026-11-13, before any run; D-030)

The PI revised the script (commit 919f052) before its first run:

- **Weight:** GSWGT134 is now required; the GSWGT4_2 fallback was removed. GSWGT4_2 is a cross-sectional Wave IV weight, which does
  not match an analysis linking Waves I, III and IV.
- **Disclosure:** a whole model, or a group's weighted BA rate, is withheld when any group × outcome cell is below 10.
- **Equivalence wording:** any non-equivalent result is reported as "equivalence not established".
- **SAS loading:** an argument was removed; it had no effect, since it repeated the reader's default.

The SAP weight row was updated to match. No estimand, model, SESOI or comparison changed. Because no Add Health data had been
analyzed, this is a pre-run amendment, not a deviation. Hashes after the amendment:

```
34df45aaddfa1be05f35994193bf35b5c5de7ef0ff88b282a0a8b4cd9d652e1c  docs/sap_addhealth_mentor_timing.md
e858bc4debc389fab6bfe794c582c13e581ed500f653753311399a58bcc440ab  scripts/addhealth_offline/run_addhealth_mentor_timing.py
```

## Run record

- **2026-11-13:** run completed locally by the PI with the script at commit 919f052. Its SHA-256 (e858bc4d…) matches amendment 1.
- **Data:** Add Health public-use Waves I, III and IV, weighted with GSWGT134.
- **Results:** kept on the PI's machine.
- **PI's interpretation (D-032):** onset at 14–17 was slightly higher than onset before 14 in adjusted BA attainment.
  - The difference was not significant at α = .05.
  - Equivalence within ±5 percentage points was supported.
