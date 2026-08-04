import os
import sys
from pathlib import Path

import tkinter as tk
from tkinter import filedialog
from tabulate import tabulate

import numpy as np
import pandas as pd

pd.set_option("display.max_rows", None)

SHEET_NAME = "INVENTORY (DATA)"
REQUIRED_COLUMNS = [
    "Ext ID",
    "Contractor",
    "Stockyard",
    "Pile",
    "WMT",
    "Ni",
    "Fe",
    "Al2O3",
    "SiO2",
    "MgO",
    "Remarks"
]
ROUND_COLUMNS = {
    "Ni": 2,
    "Fe": 2,
    "Al2O3": 2,
    "SiO2": 2,
    "MgO": 2,
    "WMT": 0
}
LABEL_WIDTH = 18
SEPARATOR = "-" * 80


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


def get_float(prompt):
    """
    Repeatedly prompts the user until a valid
    floating-point number is entered.

    Returns:
        float: User input.
    """

    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")

def clear_screen():
    """
    Clears the console screen.
    """

    os.system("cls" if os.name == "nt" else "clear")

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


def get_target_specs():
    """
    Prompts the user for the vessel's target specifications.

    Returns:
        dict: Vessel information and initialized statistics.
    """

    clear_screen()
    print("Vessel Specifications\n")

    vessel = create_vessel()
    vessel["name"] = input("Vessel Name: ").strip().upper()
    vessel["capacity"] = get_float("Vessel Capacity (WMT): ")
    vessel["fe_target"] = get_float("Vessel Fe Requirement: ")
    vessel["ni_target"] = get_float("Vessel Ni Requirement: ")

    return vessel

def display_summary(vessel, show_remaining=True):
    """
    Displays the current vessel summary,
    including capacity, target grades,
    and current blend statistics.
    """

    fe_diff = vessel["fe_actual"] - vessel["fe_target"]
    ni_diff = vessel["ni_actual"] - vessel["ni_target"]
    remaining_wmt = vessel["capacity"] - vessel["current_wmt"]

    print("Vessel Specifications\n")

    print(f"{'Vessel Name:':<{LABEL_WIDTH}}{vessel['name']}")
    print(f"{'Capacity:':<{LABEL_WIDTH}}{vessel['capacity']:,.0f} WMT")
    print(f"{'Target Specs:':<{LABEL_WIDTH}}{vessel['fe_target']:.2f}% Fe / {vessel['ni_target']:.2f}% Ni\n")
    print(f"{'Selected Piles:':<{LABEL_WIDTH}}{vessel['number_piles']}")

    if show_remaining:
        print(f"{'Current WMT:':<{LABEL_WIDTH}}{vessel['current_wmt']:,.0f} WMT (Remaining: {remaining_wmt:,.0f} WMT)")
    else:
        print(f"{'Current WMT:':<{LABEL_WIDTH}}{vessel['current_wmt']:>,.0f} WMT")

    print(f"{'Current Fe:':<{LABEL_WIDTH}}{vessel['fe_actual']:.2f}% ({fe_diff:+.2f}%)")
    print(f"{'Current Ni:':<{LABEL_WIDTH}}{vessel['ni_actual']:.2f}% ({ni_diff:+.2f}%)")

def display_screen(vessel, show_remaining=True):
    """Clears the console and displays the vessel summary."""

    clear_screen()
    display_summary(vessel, show_remaining)
    print(SEPARATOR)


def  add_pile(all_df, selected_df, vessel):
    """
    Adds a pile to the current blend.

    Updates the vessel statistics after a
    successful addition.

    Returns:
        tuple: Updated selected DataFrame and vessel dictionary.
    """

    # Catches a non-number input
    try:
        pile_id = int(input("Pile to add: "))
    except ValueError:
        print("Please enter a valid ID.")
        return selected_df, vessel

    # Catches an already-chosen pile
    if pile_id in selected_df["ID"].values:
        print("Pile already selected.")
        return selected_df, vessel

    row = all_df[all_df["ID"] == pile_id]

    # Catches an empty row
    if row.empty:
        print("Invalid pile.")
        return selected_df, vessel

    selected_df = pd.concat([selected_df, row], ignore_index=True)
    update_vessel(vessel, selected_df)

    return selected_df, vessel

def remove_pile(selected_df, vessel):
    """
    Removes a pile from the current blend.

    Updates the vessel statistics after a
    successful removal.

    Returns:
        tuple: Updated selected DataFrame and vessel dictionary.
    """

    # Catches a non-number input
    try:
        pile_id = int(input("ID to remove: "))
    except ValueError:
        print("Please enter a valid ID.")
        return selected_df, vessel

    # Catches piles not present in the selected piles
    if pile_id not in selected_df["ID"].values:
        print("Pile not currently selected.")
        return selected_df, vessel

    selected_df = selected_df[selected_df["ID"] != pile_id]
    update_vessel(vessel, selected_df)
    
    return selected_df, vessel

def view_selection(selected_df):
    """
    Displays the currently selected piles
    in a formatted table.
    """

    selected_df = selected_df.round(ROUND_COLUMNS)

    if selected_df.empty:   
        print("No Pile selected")
        return

    print(
        tabulate(
            selected_df,
            headers="keys",
            tablefmt="grid",
            showindex=False,
            colalign=("center",) * len(selected_df.columns),
            numalign="center",
            stralign="center"
        )
    )

def view_available(all_df, selected_df):
    """
    Displays all available piles that have
    not yet been selected.
    """

    available_df = all_df[~all_df["ID"].isin(selected_df["ID"])]
    available_df = available_df.round(ROUND_COLUMNS)

    print(
        tabulate(
            available_df,
            headers="keys",
            tablefmt="grid",
            showindex=False,
            colalign=("center",) * len(available_df.columns),
            numalign="center",
            stralign="center"
        )
    )    



def main():
    """
    Runs the Ore Blender Optimizer.

    Handles user interaction, menu navigation,
    and the overall blending workflow.
    """

    vessel = get_target_specs()
    file = select_file()
    df = process_file(file)

    selected_df = df.iloc[0:0].copy()
    while True:
        display_screen(vessel)

        print("Action:\n1. View Available Piles")
        print("2. Add Pile")
        print("3. Remove Pile")
        print("4. View Selected Piles")
        print("5. Exit")

        choice = input("\nChoice: ").strip()

        display_screen(vessel)

        match choice:
            case "1":
                view_available(df, selected_df)
            
            case "2":
                selected_df, vessel = add_pile(df, selected_df, vessel)

            case "3":
                selected_df, vessel = remove_pile(selected_df, vessel)

            case "4":
                view_selection(selected_df)

            case "5":
                clear_screen()
                display_summary(vessel, show_remaining= False)
                print("\nThank you!\n")
                break

            case _:
                print("Not included in Actions. Please choose a correct Action.")

        input("\nPress Enter to proceed...")


if __name__ == "__main__":
    main()