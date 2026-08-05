VALID_ELEMENTS = frozenset({"ni", "fe", "al", "si", "mg"})

class OrePile:

    def __init__(self, index, ext_id, contractor, stockyard, pile, wmt, ni, fe, al, si, mg):

        # Index Validator
        if not isinstance(index, int):
            raise TypeError("Index must be an integer.")
        if index < 0:
            raise ValueError("Index cannot be negative.")

        # WMT Validator
        if not isinstance(wmt, (int, float)):
            raise TypeError("WMT must be numeric.")
        if wmt <= 0:
            raise ValueError("WMT must be greater than zero.")

        # Grade Validator
        for name, value in {
            "Ni": ni,
            "Fe": fe,
            "Al": al,
            "Si": si,
            "Mg": mg,
        }.items():
            if not isinstance(value, (int, float)):
                raise TypeError(f"{name} grade must be numeric.")

        # Attributes
        self.index = index
        self.ext_id = ext_id
        self.contractor = contractor
        self.stockyard = stockyard
        self.pile = pile

        self.wmt = float(wmt)
        self.ni = float(ni)
        self.fe = float(fe)
        self.al = float(al)
        self.si = float(si)
        self.mg = float(mg)

    # Methods
    def contained(self, element):
        element = element.lower()
        if element not in VALID_ELEMENTS:
            raise ValueError(f"Unknown: {element}. Please enter a valid element.")
        
        return self.wmt * getattr(self, element)

    def __repr__(self) -> str:
        return (
            f"OrePile(index={self.index}, ext_id='{self.ext_id}', "
            f"contractor='{self.contractor}', stockyard='{self.stockyard}', "
            f"pile='{self.pile}', wmt={self.wmt}, ni={self.ni}, fe={self.fe}"
        )



class Vessel:

    def __init__(self, name, material, capacity_target, ni_spec, fe_spec):

        # Name validator
        if not name.strip():
            raise ValueError("Vessel name cannot be empty.")

        # Material validator
        if not material.strip():
            raise ValueError("Material cannot be empty.")

        # Capacity validator
        if not isinstance(capacity_target, (int, float)):
            raise TypeError("Capacity target must be numeric.")
        if capacity_target <= 0:
            raise ValueError("Capacity target must be greater than zero.")

        # Grade Specs validator
        if not isinstance(ni_spec, (int, float)):
            raise TypeError("Ni specification must be numeric.")
        if not isinstance(fe_spec, (int, float)):
            raise TypeError("Fe specification must be numeric.")

        # Attributes
        self.name = name
        self.material = material

        self.capacity_target = float(capacity_target)
        self.ni_spec = float(ni_spec)
        self.fe_spec = float(fe_spec)

        self.piles = []

    # Methods
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
        if element not in VALID_ELEMENTS:
            raise ValueError(f"Unknown: {element}. Please enter a valid element.")

        total = self.total_wmt
        if total == 0:
            return 0.0
        
        return sum(p.contained(element) for p in self.piles) / total

    def summary(self, include=True):
        summary =  {
            "Vessel": self.name,
            "Total WMT": self.total_wmt,
            "Ni": self.average_grade("ni"),
            "Fe": self.average_grade("fe"),
        }

        if include:
            summary.update({
                "Al2O3": self.average_grade("al"),
                "SiO2": self.average_grade("si"),
                "MgO": self.average_grade("mg"),
            })

        return summary

    def __repr__(self):
        return (
            f"Vessel("
            f"name='{self.name}', "
            f"piles={len(self.piles)}, "
            f"wmt={self.total_wmt:.0f})"
        )