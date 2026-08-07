# Ore Blending Optimizer Version 1.2 

from models.orepile import OrePile

from config.config import VALID_ELEMENTS

class Inventory:
    def __init__(self):
        self.piles = []

    def add_pile(self, pile):
        if not isinstance(pile, OrePile):
            raise TypeError("Expected an OrePile object.")

        if pile in self.piles:
            raise ValueError(f"Pile index '{pile.index}' is already in the Inventory.")
        
        self.piles.append(pile)
        return pile

    def remove_pile(self, pile):
        if pile not in self.piles:
            raise ValueError("Pile is not in the Inventory.")
        
        self.piles.remove(pile)
        return pile

    def clear_piles(self):
        count = len(self.piles)
        self.piles.clear()

        return count

    def get_pile(self, index):
        if not isinstance(index, int):
            raise TypeError("Pile index must be an integer.")

        for pile in self.piles:
            if pile.index == index:
                return pile

        raise ValueError(f"Pile index '{index}' was not found in the Inventory.")

    def load_rows(self, rows):
        self.clear_piles()

        for record in rows.to_dict("records"):
            pile = OrePile(
                index=record["ID"],
                material=record["ORE"],
                ext_id=record["Ext ID"],
                contractor=record["Contractor"],
                stockyard=record["Stockyard"],
                pile=record["Pile"],
                wmt=record["WMT"],
                ni=record["Ni"],
                fe=record["Fe"],
                al=record["Al2O3"],
                si=record["SiO2"],
                mg=record["MgO"],
                remarks=record["Remarks"]
            )

            self.add_pile(pile)

        return len(self.piles)

    def get_by_stockyard(self, stockyard):
        return [p for p in self.piles if p.stockyard == stockyard]

    def get_by_contractor(self, contractor):
        return [p for p in self.piles if p.contractor == contractor]

    def get_by_material(self, material):
        return [p for p in self.piles if p.material == material]

    @property
    def total_wmt(self):
        return sum(p.wmt for p in self.piles)

    def average_grade(self, element):
        element = element.lower()
        
        total = self.total_wmt
        if total == 0:
            return 0.0
        
        return sum(p.contained(element) for p in self.piles) / total

    def summary(self, include_minor_elements=True):
        summary =  {
            "Total WMT": self.total_wmt,
            "Ni": self.average_grade("ni"),
            "Fe": self.average_grade("fe"),
        }

        if include_minor_elements:
            summary.update({
                "Al2O3": self.average_grade("al"),
                "SiO2": self.average_grade("si"),
                "MgO": self.average_grade("mg"),
            })

        return summary

    def __repr__(self):
        return (
            f"Inventory("
            f"piles={len(self.piles)}, "
            f"wmt={self.total_wmt:.0f}, "
            f"fe={self.average_grade('fe'):.2f}, "
            f"ni={self.average_grade('ni'):.2f})"
        )