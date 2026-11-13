# Add Health: checklist for the human analyst

Add Health prohibits using AI tools (including Claude, ChatGPT, Copilot, Gemini) to manage, process or analyze its data. This
checklist keeps study A3 within those terms.

1. **Get the data yourself.** Download the public-use Wave I, Wave III and Wave IV in-home files and the matching weight files from the
   Add Health Dataverse (https://dataverse.unc.edu/dataverse/addhealth) or ICPSR study 21600, after accepting the terms.
2. **Work on your own computer, with AI assistants switched off** for that session: no AI coding assistant in your editor and no
   chatbot window with the data or output.
3. **Do not upload, paste or describe** Add Health files, rows, or variable values to any AI tool, including this project's Claude
   sessions.
4. **Run the script** from a terminal:
   `python scripts/addhealth_offline/run_addhealth_mentor_timing.py --w1 <wave1 file> --w3 <wave3 file> --w4 <wave4 file> --weights <wave4 weights file> --out <folder outside the repo>`
   (`.dta`, `.sas7bdat`, `.sav`, `.csv` or `.tab` files are accepted; `.dta`/`.sas7bdat`/`.sav` need `pip install pyreadstat`.)
5. **Keep the output folder out of git** and out of AI tools. The repository's `.gitignore` already excludes `data/`. Use a folder
   outside the repository to be safe.
6. **Before sharing any results with an AI tool,** email Add Health (contact on https://addhealth.cpc.unc.edu/) and ask whether
   sharing *aggregate* estimates (the tables the script prints) is permitted. Save their written answer. Until then, interpret and
   write up the results yourself.
7. **Report** the file versions you used and the script's printed SHA-256 of the plan, so the run can be tied to the frozen plan.
