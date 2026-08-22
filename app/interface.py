# Ore Blending Optimizer Version 1.2 

import os
import pandas as pd

from tabulate import tabulate

from config.config import SEPARATOR, LABEL_WIDTH, ROUND_COLUMNS

def clear_screen():
    """
    Clears the console screen.
    """

    os.system("cls" if os.name == "nt" else "clear")

def input_float(prompt):
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

def get_vessel_specs():
    """
    Prompt the user to enter vessel specifications.

    Validates all inputs before returning the vessel data.
    The material must be either LIMONITE or SAPROLITE.
    Numeric vessel specifications must satisfy their respective
    minimum and non-negative constraints.

    Returns:
        dict: Validated vessel specifications containing:
            - name: Vessel name
            - material: LIMONITE or SAPROLITE
            - capacity_target: Target vessel capacity in WMT
            - capacity_threshold: Maximum allowable capacity excess in WMT
            - fe_spec: Required Fe grade
            - ni_spec: Required Ni grade
    """

    print("Vessel Specifications\n")

    while True:

        # --------------------------- VESSEL NAME ---------------------------
        name = input("Vessel Name: ").strip().upper()
        if not name:
            print("Vessel name cannot be empty.\n")
            continue

        # ------------------------- VESSEL MATERIAL -------------------------
        material = input("Material (Limonite/Saprolite): ").strip().upper()
        if material not in ("LIMONITE", "SAPROLITE"):
            print("Invalid material. Please enter Limonite or Saprolite.\n")
            continue

        # ------------------------- VESSEL CAPACITY -------------------------
        capacity_target = input_float("Vessel Capacity (WMT): ")
        if capacity_target <= 0:
            print("Vessel capacity must be greater than 0.\n")
            continue

        # ------------------------- VESSEL FE GRADE -------------------------
        fe_spec = input_float("Vessel Fe Requirement: ")
        if fe_spec <= 0 or fe_spec >= 100:
            print("Fe specification must be between 0% and 100%.\n")
            continue

        # ------------------------- VESSEL NI GRADE -------------------------
        ni_spec = input_float("Vessel Ni Requirement: ")
        if ni_spec <= 0 or ni_spec >= 100:
            print("Ni specification must be between 0% and 100%.\n")
            continue

        # ----------------------- ALL INPUTS ARE VALID -----------------------
        break

    vessel_data = {
        "name": name,
        "material": material,
        "capacity_threshold": 5000,
        "capacity_target": capacity_target,
        "fe_spec": fe_spec,
        "ni_spec": ni_spec
    }

    return vessel_data

def display_summary(vessel, show_remaining_capacity=True):
    """
    Displays the current vessel summary,
    including capacity, target grades,
    and current blend statistics.
    """

    current_wmt = vessel.total_wmt
    current_fe = vessel.average_grade("fe")
    current_ni = vessel.average_grade("ni")

    remaining_wmt = vessel.capacity_target - current_wmt
    fe_diff = current_fe - vessel.fe_spec
    ni_diff = current_ni - vessel.ni_spec

    print("Vessel Specifications\n")

    print(f"{'Vessel Name:':<{LABEL_WIDTH}}{vessel.name}")
    print(f"{'Capacity:':<{LABEL_WIDTH}}{vessel.capacity_target:,.0f} WMT")
    print(
        f"{'Target Specs:':<{LABEL_WIDTH}}"
        f"{vessel.fe_spec:.2f}% Fe / {vessel.ni_spec:.2f}% Ni\n"
    )

    print(f"{'Selected Piles:':<{LABEL_WIDTH}}{len(vessel.piles)}")

    if show_remaining_capacity:
        print(
            f"{'Current WMT:':<{LABEL_WIDTH}}"
            f"{current_wmt:,.0f} WMT "
            f"(Remaining: {remaining_wmt:,.0f} WMT)"
        )
    else:
        print(f"{'Current WMT:':<{LABEL_WIDTH}}{current_wmt:,.0f} WMT")

    print(f"{'Current Fe:':<{LABEL_WIDTH}}{current_fe:.2f}% ({fe_diff:+.2f}%)")
    print(f"{'Current Ni:':<{LABEL_WIDTH}}{current_ni:.2f}% ({ni_diff:+.2f}%)")

def display_screen(vessel, show_remaining=True):
    """Clears the console and displays the vessel summary."""

    clear_screen()
    display_summary(vessel, show_remaining)
    print(SEPARATOR)

def add_pile(inventory, vessel):

    try:
        pile_id = int(input("Pile to add: "))
    except ValueError:
        print("Please enter a valid ID.")
        return

    try:
        pile = inventory.get_pile(pile_id)

        inventory.remove_pile(pile)
        vessel.add_pile(pile)

        print("Pile added.")

    except (TypeError, ValueError) as e:
        print(e)

def remove_pile(inventory, vessel):
    if not vessel.piles:
        print("No piles currently selected in the vessel.")
        return

    try:
        pile_id = int(input("Pile to remove: "))
    except ValueError:
        print("Please enter a valid ID.")
        return

    try:
        pile = vessel.get_pile(pile_id)

        vessel.remove_pile(pile)
        inventory.add_pile(pile)

        print("Pile removed.")

    except (TypeError, ValueError) as e:
        print(e)

def view_selection(vessel):
    display_piles(vessel.piles)

def view_available(inventory):
    display_piles(inventory.piles)

def display_piles(piles):

    rows = []

    if not piles:
        print("No piles to display.")
        return

    for p in piles:
        rows.append({
            "Pile Index": p.index,
            "Ext ID": p.ext_id,
            "Contractor": p.contractor,
            "Stockyard": p.stockyard,
            "Pile No": p.pile,
            "WMT": p.wmt,
            "Fe": p.fe,
            "Ni": p.ni
        })

    df = pd.DataFrame(rows).round(ROUND_COLUMNS)

    print(
        tabulate(
            df,
            headers="keys",
            tablefmt="grid",
            showindex=False,
            colalign=("center",) * len(df.columns),
            numalign="center",
            stralign="center"
        )
    )

def exit_function(vessel):
    clear_screen()
    display_summary(vessel, show_remaining_capacity= False)
    print("\nThank you!\n")