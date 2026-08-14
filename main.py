# Ore Blending Optimizer Version 1.2 

from models.inventory import Inventory
from app.loader import load_inventory
from models.vessel import Vessel
from optimizer.optimizer import OreBlenderOptimizer

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

    clear_screen()
    
    print("\nPlease do not exit. Starting optimizer...")

    # -----------------------------
    # Optimize
    # -----------------------------

    optimizer = OreBlenderOptimizer(
        inventory=inventory,
        vessel=vessel
    )    

    result = optimizer.solve()

    # -----------------------------
    # Display result
    # -----------------------------

    waiting = input("\n\nPlease press enter to continue...")

    clear_screen()

    print("=== OPTIMIZATION RESULT ===")

    print(
        f"Vessel capacity: "
        f"{vessel.capacity_target:,.0f} WMT"
    )

    print(
        f"Allowed maximum: "
        f"{vessel.capacity_target + vessel.capacity_threshold:,.0f} WMT"
    )

    print(
        f"Required Ni: "
        f"{vessel.ni_spec:.3f}"
    )

    print(
        f"Required Fe: "
        f"{vessel.fe_spec:.3f}"
    )

    print("\nSelected piles:")

    print("\nIndex\tOre\tExt ID\tStockyard\tContractor\tPile\t\tWMT\tNi\tFe\tAl2O3\tSiO2\tMgO\tRemarks")

    for pile in result["selected_piles"]:
        print(
            f"{pile.index}\t"
            f"{pile.material}\t"
            f"{pile.ext_id}\t"
            f"{pile.stockyard}\t\t"
            f"{pile.contractor}\t\t"
            f"{pile.pile}\t\t"
            f"{pile.wmt:,.0f}\t"
            f"{pile.ni:.2f}\t"
            f"{pile.fe:.2f}\t"
            f"{pile.al:.2f}\t"
            f"{pile.si:.2f}\t"
            f"{pile.mg:.2f}\t"
            f"{pile.remarks}"
        )

    print(
        "\nTotal WMT:",
        f"{result['total_wmt']:,.0f}"
    )

    print(
        "Blended Ni:",
        f"{result['ni']:.2f}"
    )

    print(
        "Blended Fe:",
        f"{result['fe']:.2f}"
    )

if __name__ == "__main__":
    main()