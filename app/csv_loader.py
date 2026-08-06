from pathlib import Path

import tkinter as tk
from tkinter import filedialog

import pandas as pd

from config.config import SHEET_NAME, REQUIRED_COLUMNS, SEPARATOR

def select_file():
    """
    Opens a file dialog for the user to select an inventory EXCEL 
    file. Edit if actual Inventory is a CSV file.

    Returns:
        str: Path to the selected file.
    """

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    file = filedialog.askopenfilename(
        title="Select File",
        filetypes=[("Excel Files", "*.xlsx;*.xls")],
    )
    root.destroy()
    
    return Path(file)

def validate_file(filepath):
    """
    Validates the selected inventory EXCEL file.

    Checks that the required worksheet exists and that all
    required columns are present. Exits the program if validation
    fails. Please check the REQUIREMENTS.txt for the required columns
    """

    # validates file path
    if not filepath or str(filepath).strip() in ("", "."):
        raise ValueError("No file selected.")

    # validates file existence
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # validates sheet existence
    try:
        df = pd.read_excel(filepath, sheet_name=SHEET_NAME, header=0)
    except ValueError:
        raise ValueError(f"Sheet '{SHEET_NAME}' not found.")

    # verifies file's required columns
    missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_cols:
        raise ValueError(f"{filepath.name} is missing: "f"{', '.join(sorted(missing_cols))}")
    
    return df

def process_dataframe(df):
    """
    Loads and prepares the inventory data.

    Reads the inventory worksheet, keeps only the required
    columns, adds a sequential ID column, and renames
    selected columns for easier display.

    Returns:
        pandas.DataFrame: Processed inventory data.
    """
    
    # Only retrieving the important columns
    df = df[REQUIRED_COLUMNS]

    # Inserts a Pile ID (different from Pile No) column to identify each pile
    df.insert(0, "ID", range(1, len(df) + 1))

    return df

def load_inventory():
    
    # select_file
    filepath = select_file()

    # validates file
    df = validate_file(filepath)

    # process_file
    processed_df = process_dataframe(df)

    return processed_df
