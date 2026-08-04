import sys
from pathlib import Path

import tkinter as tk
from tkinter import filedialog

import pandas as pd
import numpy as np

from config import SHEET_NAME, REQUIRED_COLUMNS, SEPARATOR

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
    
    return file

def validate_file(file):
    """
    Validates the selected inventory EXCEL file.

    Checks that the required worksheet exists and that all
    required columns are present. Exits the program if validation
    fails. Please check the REQUIREMENTS.txt for the required columns
    """

    if not file or str(file).strip() in ("", "."):
        print("\nNo file selected. Operation canceled.")
        sys.exit(0)

    filepath = Path(file)

    # Checks File existence
    if not filepath:
        print("No file selected.")
        sys.exit(1)

    # Checks Sheet existence
    try:
        df = pd.read_excel(filepath, sheet_name=SHEET_NAME, header=0)
    except ValueError:
        print(f"Sheet '{SHEET_NAME}' not found.")
        sys.exit(1)

    # Verifies file' required columns
    missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_cols:
        print("Uploaded file does not have the required columns.")
        print("Please Check REQUIREMENTS.txt")
        print(SEPARATOR)
        print(f"{filepath.name} is missing: "f"{', '.join(sorted(missing_cols))}")
        sys.exit(1)

    return df

def process_file(file):
    """
    Loads and prepares the inventory data.

    Reads the inventory worksheet, keeps only the required
    columns, adds a sequential ID column, and renames
    selected columns for easier display.

    Returns:
        pandas.DataFrame: Processed inventory data.
    """

    filepath = Path(file)
    df = validate_file(filepath)

    # Only retrieving the important columns
    df = df[REQUIRED_COLUMNS]

    # Inserts a Pile ID (different from Pile No) column to identify each pile
    df.insert(0, "ID", range(1, len(df) + 1))

    df = df.rename(columns={"Contractor":"Cont", "Stockyard": "SY"})

    return df


def create_vessel():
    return {
        "name": "",
        "capacity": 0.0,
        "fe_target": 0.0,
        "ni_target": 0.0,

        "number_piles": 0,
        "current_wmt": 0,

        "fe_actual": 0.0,
        "ni_actual": 0.0,
        "al2o3_actual": 0.0,
        "sio2_actual": 0.0,
        "mgo_actual": 0.0,
    }    

def update_vessel(vessel, selected_df):
    """
    Updates the vessel summary.

    Calculates the total selected piles, total weight (WMT),
    and weighted-average Ore grades based on the
    current pile selection.
    """

    # Catches error if the selected_df (chosen piles) is empty
    if selected_df.empty:
        vessel["number_piles"] = 0
        vessel["current_wmt"] = 0
        vessel["fe_actual"] = 0
        vessel["ni_actual"] = 0
        vessel["al2o3_actual"] = 0
        vessel["sio2_actual"] = 0
        vessel["mgo_actual"] = 0

        return None

    vessel["number_piles"] = len(selected_df)
    vessel["current_wmt"] = selected_df["WMT"].sum()

    vessel["ni_actual"] = get_weighted_average(selected_df, "Ni")
    vessel["fe_actual"] = get_weighted_average(selected_df, "Fe")
    vessel["al2o3_actual"] = get_weighted_average(selected_df, "Al2O3")
    vessel["sio2_actual"] = get_weighted_average(selected_df, "SiO2")
    vessel["mgo_actual"] = get_weighted_average(selected_df, "MgO")


def get_weighted_average(df, value_col, weight_col="WMT"):
    """
    Calculates the weighted average of a column.

    Args:
        df (pandas.DataFrame): Data containing the values.
        value_col (str): Column to average.
        weight_col (str): Column containing weights.

    Returns:
        float: Weighted average.
    """

    weights = df[weight_col]

    # Catches the error when total weights equal to 0
    if weights.sum() == 0:
        raise ValueError(f"Current {weight_col} is zero.")
    
    weighted_average = np.average(df[value_col], weights=weights)

    return weighted_average
