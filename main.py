# Ore Blending Optimizer Version 1.2 

from models.inventory import Inventory
from app.loader import load_inventory
from models.vessel import Vessel

from app.interface import (
    clear_screen,
    get_vessel_specs,
    display_screen,
    view_available,
    view_selection,
    add_pile,
    remove_pile,
    exit_function,
)

def main():
    """
    Runs the Ore Blender Optimizer.

    Handles user interaction, menu navigation,
    and the overall blending workflow.
    """

    clear_screen()

    vessel_data = get_vessel_specs()
    vessel = Vessel(**vessel_data)

    inventory = Inventory()

    try:
        rows = load_inventory()    
        count = inventory.load_rows(rows)
        print(f"\nSuccessfully loaded {count} piles.")
    except Exception as e:
        print(f"\nError loading inventory: {e}")
        return

    input("\nPress Enter to continue...")

    while True:

        display_screen(vessel)

        print("Action:")
        print("1. View Available Piles")
        print("2. Add Pile")
        print("3. Remove Pile")
        print("4. View Selected Piles")
        print("5. Exit")

        choice = input("\nChoice: ").strip()

        display_screen(vessel)

        match choice:

            case "1":
                view_available(inventory)

            case "2":
                add_pile(inventory, vessel)

            case "3":
                remove_pile(inventory, vessel)

            case "4":
                view_selection(vessel)

            case "5":
                exit_function(vessel)
                break

            case _:
                print("Not included in Actions. Please choose a correct Action.")

        input("\nPress Enter to proceed...")

if __name__ == "__main__":
    main()