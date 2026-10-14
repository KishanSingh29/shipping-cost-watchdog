
import shutil
from pathlib import Path

import pandas as pd

path = Path("eval/labeled_cases.csv")
backup = Path("eval/labeled_cases.csv.bak")

# Original CSV ka backup, sirf pehli baar.
if not backup.exists():
    shutil.copy2(path, backup)

df = pd.read_csv(path, dtype=str).fillna("")

justified = {
    "C002": "N002",
    "C003": "N001",
    "C030": "N002",
}

unexplained = {"C001", "C004", "C005", "C020"}
missing_data = {"C016", "C017"}

for i, row in df.iterrows():
    case_id = row["case_id"]

    if case_id in missing_data:
        df.loc[i, ["expected_flagged", "expected_verdict",
                   "expected_note_id"]] = ""

    elif case_id in justified:
        df.loc[i, "expected_flagged"] = "1"
        df.loc[i, "expected_verdict"] = "justified"
        df.loc[i, "expected_note_id"] = justified[case_id]

    elif case_id in unexplained:
        df.loc[i, "expected_flagged"] = "1"
        df.loc[i, "expected_verdict"] = "unexplained"
        df.loc[i, "expected_note_id"] = ""

    else:
        df.loc[i, "expected_flagged"] = "0"
        df.loc[i, "expected_verdict"] = "not_flagged"
        df.loc[i, "expected_note_id"] = ""

df.to_csv(path, index=False)

print("Labels updated:", path)
print("Backup:", backup)
print(df[[
    "case_id", "expected_flagged",
    "expected_verdict", "expected_note_id"
]].to_string(index=False))
