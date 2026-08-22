# Ore Blending Optimizer Version 1.2 

from models.orepile import OrePile

from config.config import VALID_ELEMENTS

class Vessel:

    def __init__(self, name, material, capacity_target, capacity_threshold, ni_spec, fe_spec):

        # --------------------------- VESSEL NAME ---------------------------
        if not name.strip():
            raise ValueError("Vessel name cannot be empty.")

        # ------------------------- VESSEL MATERIAL -------------------------
        if material.upper() not in ("LIMONITE", "SAPROLITE"):
            raise ValueError("Material must be either Limonite or Saprolite.")

        # ------------------------- VESSEL CAPACITY -------------------------
        if not isinstance(capacity_target, (int, float)):
            raise TypeError("Vessel capacity must be numeric.")
        if capacity_target <= 0:
            raise ValueError("Vessel capacity must be greater than zero.")

        # -------------------- VESSEL CAPACITY THRESHOLD --------------------
        if not isinstance(capacity_threshold, (int, float)):
            raise TypeError("Capacity threshold target must be numeric.")
        if capacity_threshold <= 0:
            raise ValueError("Capacity threshold target must be greater than zero.")

        # --------------------------- GRADE SPECS ---------------------------
        if not isinstance(ni_spec, (int, float)):
            raise TypeError("Ni specification must be numeric.")
        if ni_spec <= 0 or ni_spec >= 100:
            raise ValueError("Ni specification must be between 0% and 100%.\n")

        if not isinstance(fe_spec, (int, float)):
            raise TypeError("Fe specification must be numeric.")
        if fe_spec <= 0 or fe_spec >= 100:
            raise ValueError("Fe specification must be between 0% and 100%.\n")

        # Attributes
        self.name = name
        self.material = material

        self.capacity_target = float(capacity_target)
        self.capacity_threshold = float(capacity_threshold)
        self.ni_spec = float(ni_spec)
        self.fe_spec = float(fe_spec)

        self.piles = []

    def add_pile(self, pile):
        if not isinstance(pile, OrePile):
            raise TypeError("Expected an OrePile object.")

        if pile in self.piles:
            raise ValueError(f"Pile index '{pile.index}' is already selected.")
        
        self.piles.append(pile)
        return pile

    def remove_pile(self, pile):
        if pile not in self.piles:
            raise ValueError("Pile is not in the vessel.")
        
        self.piles.remove(pile)
        return pile

    def clear_piles(self):
        count = len(self.piles)
        self.piles.clear()

        return count

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
            "Vessel": self.name,
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

    def get_pile(self, index):
        if not isinstance(index, int):
            raise TypeError("Pile index must be an integer.")

        for pile in self.piles:
            if pile.index == index:
                return pile

        raise ValueError(f"Pile index '{index}' is not in the Vessel.")

    def __repr__(self):
        return (
            f"Vessel("
            f"name='{self.name}', "
            f"piles={len(self.piles)}, "
            f"wmt={self.total_wmt:.0f})"
        )
