import pandas as pd
import re
import sys

def clean_text(text):
    """Clean messy free-form text."""
    if pd.isna(text):
        return ""
    text = re.sub(r'(?i)note:.*', '', text)
    text = re.sub(r'(?i)please.*', '', text)
    text = re.sub(r'(?i)jira.*', '', text)
    text = re.sub(r'(?i)contact.*', '', text)
    text = re.sub(r'[^a-zA-Z0-9_.,=()<>+\-*/\'" ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def build_edh_logic_dynamic(edh_df):
    """
    Build SQL join logic dynamically based on edh_ref sheet.
    Returns a string like:
    INNER JOIN edh_ref r ON src.name = tgt.first_name AND src.id = tgt.emp_id
    """
    if edh_df.empty:
        return ""
    join_conditions = []
    for _, row in edh_df.iterrows():
        src = row.get("source_field", "")
        tgt = row.get("target_field", "")
        if src and tgt:
            join_conditions.append(f"src.{src} = tgt.{tgt}")
    if join_conditions:
        return "INNER JOIN edh_ref r ON " + " AND ".join(join_conditions)
    return ""

def process_excel(filename):
    # Read sheets
    mapping_df = pd.read_excel(filename, sheet_name="field source to target mapping")
    rules_df = pd.read_excel(filename, sheet_name="transformation rules")
    edh_df = pd.read_excel(filename, sheet_name="edh_ref")

    # Clean mapping free-form text
    mapping_df["Cleaned_Transformation"] = mapping_df.get(
        "transformation rule auto populate (free form text)", pd.Series([""]*len(mapping_df))
    ).apply(clean_text)

    # Clean rules description
    rules_df["Cleaned_Description"] = rules_df.get("description", pd.Series([""]*len(rules_df))).apply(clean_text)

    # Merge rules into mapping sheet
    if "transformation rule #" in mapping_df.columns and "transformation rule #" in rules_df.columns:
        mapping_df = mapping_df.merge(
            rules_df[["transformation rule #", "Cleaned_Description"]],
            on="transformation rule #",
            how="left"
        )

    # Apply dynamic EDH logic for EDH-derived rows
    edh_logic_list = []
    for _, row in mapping_df.iterrows():
        if "EDH derived" in str(row.get("source table", "")) or \
           "EDH derived" in str(row.get("source column", "")) or \
           "EDH derived" in str(row.get("transformation rule auto populate (free form text)", "")):
            edh_logic_list.append(build_edh_logic_dynamic(edh_df))
        else:
            edh_logic_list.append("")
    mapping_df["EDH_Derived_Logic"] = edh_logic_list

    # Save cleaned Excel
    output_file = filename.replace(".xlsx", "_cleaned.xlsx")
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        mapping_df.to_excel(writer, sheet_name="field source to target mapping", index=False)
        rules_df.to_excel(writer, sheet_name="transformation rules", index=False)
        edh_df.to_excel(writer, sheet_name="edh_ref", index=False)

    print(f"✅ Cleaned file with EDH logic saved as {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_sql_rules.py <input_excel_file>")
    else:
        process_excel(sys.argv[1])
