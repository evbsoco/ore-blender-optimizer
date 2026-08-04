from data import select_file, process_file

from interface import clear_screen, get_target_specs, display_summary, display_screen
from interface import add_pile, remove_pile, view_available, view_selection

import pandas as pd
pd.set_option("display.max_rows", None)

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