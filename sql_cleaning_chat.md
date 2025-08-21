# ChatGPT Discussion: SQL Transformation Logic Automation

This document captures the conversation on automating the cleaning and generation of SQL transformation logic from free-form STM (Source-to-Target Mapping) documents.  

---

## Problem Statement

- You have **source-to-target mapping Excel/CSV files** with multiple sheets:
  - **Sheet 1 (Field Source to Target Mapping):**
    - Contains mapping of source schema/table/column to target schema/table/column.
    - Has a `transformation rule auto populate` column with *free-form text* (mix of SQL logic, notes, comments, special characters).
    - Has references to `transformation rule #`.

  - **Sheet 2 (Transformation Rules):**
    - Contains `rule_id`, `rule_logic`, and `rule_logic_definition`.

  - **Sheet 3 (EDH Reference):**
    - Contains mappings for EDH-derived sources.

- Current pain point:
  - Transformation logic column contains messy notes and SQL-like fragments.
  - Manual effort is needed to clean it up and generate runnable SQL.

---

## Desired Outcome

- **Automated Python script** that:
  1. Reads Excel file (all sheets).
  2. Cleans transformation logic column (remove comments, irrelevant notes, Jira references, dates, etc.).
  3. Merges referenced rules from the `Transformation Rules` sheet.
  4. Incorporates EDH Reference mappings where applicable.
  5. Produces a new column `Cleaned_Transformation` in Sheet 1 with proper SQL-ready logic.

---

## Initial Script (Prototype)

```python
import re
import pandas as pd

def clean_transformation_text(text: str) -> str:
    if pd.isna(text):
        return ""
    # Remove Notes, Comments, Jira tickets, Dates
    text = re.sub(r'(?i)note:.*', '', text)
    text = re.sub(r'(?i)comments?:.*', '', text)
    text = re.sub(r'jira[^\s]*', '', text)
    text = re.sub(r'\d{1,2}[\-/][A-Za-z]{3}[\-/]\d{2,4}', '', text)
    # Keep only SQL-like tokens
    text = re.sub(r'[^a-zA-Z0-9_.,=<>\'"()\s\*+/-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def process_excel(filename: str, output_filename: str = "cleaned_output.xlsx"):
    # Read sheets
    stm_df = pd.read_excel(filename, sheet_name="field source to target mapping")
    rules_df = pd.read_excel(filename, sheet_name="transformation rules")
    edh_df = pd.read_excel(filename, sheet_name="EDH reference")

    # Rule mapping dictionary
    rule_dict = dict(zip(rules_df["rule id"], rules_df["rule logic"]))

    cleaned = []
    for _, row in stm_df.iterrows():
        logic = str(row.get("transformation rule auto populate", "")).strip()

        # Replace rule id with logic if present
        rule_id = str(row.get("transformation rule #", "")).strip()
        if rule_id in rule_dict:
            logic = rule_dict[rule_id] + " " + logic

        # If EDH derived
        if "edh derived" in logic.lower():
            src_table = str(row.get("source table", ""))
            src_column = str(row.get("source column", ""))
            edh_match = edh_df[
                (edh_df["Source table"] == src_table) & 
                (edh_df["Source column"] == src_column)
            ]
            if not edh_match.empty:
                logic += " -- EDH Mapping: " + ", ".join(
                    edh_match["Target column"].astype(str).tolist()
                )

        cleaned.append(clean_transformation_text(logic))

    stm_df["Cleaned_Transformation"] = cleaned
    with pd.ExcelWriter(output_filename, engine="openpyxl") as writer:
        stm_df.to_excel(writer, sheet_name="field source to target mapping", index=False)
        rules_df.to_excel(writer, sheet_name="transformation rules", index=False)
        edh_df.to_excel(writer, sheet_name="EDH reference", index=False)

    print(f"✅ Cleaned file written to {output_filename}")
```

- Run with:
  ```bash
  python transform_cleaner.py input_file.xlsx
  ```

---

## Future Enhancements

- Validate cleaned SQL using `sqlparse` or `sqlglot`.
- Handle multiple transformation rules per column.
- Use Copilot/LLMs to **auto-rewrite free text** into valid SQL.
- Generate full SELECT statements for target tables automatically.

---

## Industry Context

- Similar solutions exist in ETL tools (Informatica, Talend, Ab Initio) but require structured rules.  
- Data governance tools (Collibra, Alation) track lineage but don’t auto-clean free-text SQL.  
- Most companies solve this using **custom Python scripts** like the one above.  
- Some teams are starting to use **LLMs (GPT-4/4o, etc.)** to parse messy notes into SQL.

---

## Next Steps

1. Test the prototype script with your Excel file.  
2. Inspect the `Cleaned_Transformation` column.  
3. Iterate rules/regex patterns for your dataset.  
4. Later: integrate with GitHub Copilot in VS Code for edge-case cleanups and SQL generation.

---
