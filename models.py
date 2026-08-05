VALID_ELEMENTS = frozenset({"ni", "fe", "al", "si", "mg"})

class OrePile:

    def __init__(self, ext_id, contractor, stockyard, pile, wmt, ni, fe, al, si, mg):
        self.ext_id = ext_id
        self.contractor = contractor
        self.stockyard = stockyard
        self.pile = pile

        self.wmt = wmt

        self.ni = ni
        self.fe = fe
        self.al = al
        self.si = si
        self.mg = mg

    def contained(self, element):
        element = element.lower()
        if element not in VALID_ELEMENTS:
            raise ValueError(f"Unknown: {element}. Please enter a valid element.")
        
        return self.wmt * getattr(self, element.lower())



class Vessel:

    def __init__(self, name, material, capacity_target, ni_spec, fe_spec):
        self.name = name
        self.material = material

        self.capacity_target = capacity_target
        self.ni_spec = ni_spec
        self.fe_spec = fe_spec

        self.piles = []
        
    def add_pile(self, pile):
        self.piles.append(pile)

    def remove_pile(self, pile):
        self.piles.remove(pile)

    def clear_piles(self):
        self.piles.clear()

    @property
    def total_wmt(self):
        return sum(p.wmt for p in self.piles)

    def average_grade(self, element):
        element = element.lower()
        if element not in VALID_ELEMENTS:
            raise ValueError(f"Unknown: {element}. Please enter a valid element.")
    
        if self.total_wmt == 0:
            return 0.0
        
        return sum(p.contained(element) for p in self.piles) / self.total_wmt

    def summary(self, include=True):
        summary =  {
            "Vessel": self.name,
            "Total WMT": self.total_wmt,
            "Ni": self.average_grade("ni"),
            "Fe": self.average_grade("fe"),
            "Al2O3": self.average_grade("al"),
            "SiO2": self.average_grade("si"),
            "MgO": self.average_grade("mg")
        }

        if include:
            summary.update({
                "Al2O3": self.average_grade("al"),
                "SiO2": self.average_grade("si"),
                "MgO": self.average_grade("mg"),
            })

        return summary