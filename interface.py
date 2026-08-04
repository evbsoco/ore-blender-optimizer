import os
import pandas as pd

from tabulate import tabulate

from data import create_vessel, get_float, update_vessel, ROUND_COLUMNS

LABEL_WIDTH = 18
SEPARATOR = "-" * 80


def clear_screen():
    """
    Clears the console screen.
    """

    os.system("cls" if os.name == "nt" else "clear")


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


def add_pile(all_df, selected_df, vessel):
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

