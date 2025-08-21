import pandas as pd
import re
import sys

def clean_text(text):
    """Basic cleaning: remove notes, special chars, redundant whitespace"""
    if pd.isna(text):
        return ""
    # Remove notes/comments patterns
    text = re.sub(r'(?i)note:.*', '', text)
    text = re.sub(r'(?i)please.*', '', text)
    text = re.sub(r'(?i)jira.*', '', text)
    text = re.sub(r'(?i)contact.*', '', text)
    # Remove extra special characters except SQL symbols
    text = re.sub(r'[^a-zA-Z0-9_.,=()<>+\-*/\'" ]', ' ', text)
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def process_excel(filename):
    # Read sheets
    mapping_df = pd.read_excel(filename, sheet_name="field source to target mapping")
    rules_df = pd.read_excel(filename, sheet_name="transformation rules")
    edh_df = pd.read_excel(filename, sheet_name="edh_ref")

    # Clean free-form text in mapping sheet
    if "transformation rule auto populate (free form text)" in mapping_df.columns:
        mapping_df["Cleaned_Transformation"] = mapping_df["transformation rule auto populate (free form text)"].apply(clean_text)
    else:
        mapping_df["Cleaned_Transformation"] = ""

    # Clean free-form text in rules sheet (description column)
    if "description" in rules_df.columns:
        rules_df["Cleaned_Description"] = rules_df["description"].apply(clean_text)

    # Merge transformation rules into mapping sheet
    if "transformation rule #" in mapping_df.columns and "transformation rule #" in rules_df.columns:
        mapping_df = mapping_df.merge(
            rules_df[["transformation rule #", "Cleaned_Description"]],
            on="transformation rule #",
            how="left"
        )

    # Save cleaned output
    output_file = filename.replace(".xlsx", "_cleaned.xlsx")
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        mapping_df.to_excel(writer, sheet_name="field source to target mapping", index=False)
        rules_df.to_excel(writer, sheet_name="transformation rules", index=False)
        edh_df.to_excel(writer, sheet_name="edh_ref", index=False)

    print(f"✅ Cleaned file saved as {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_sql_rules.py <input_excel_file>")
    else:
        process_excel(sys.argv[1])
