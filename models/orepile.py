from config.config import VALID_ELEMENTS

class OrePile:

    def __init__(self, index, material, ext_id, contractor, stockyard, pile, wmt, ni, fe, al, si, mg, remarks):

        # Index Validator
        if not isinstance(index, int):
            raise TypeError("Index must be an integer.")
        if index < 0:
            raise ValueError("Index cannot be negative.")

        # String (Material, Ext ID, Contractor, Stockyard, Pile) validator
        for name, value in {
            "Material": material,
            "Ext ID": ext_id,
            "Contractor": contractor,
            "Stockyard": stockyard,
            "Pile": pile,
        }.items():
            if not value.strip():
                raise ValueError(f"{name} cannot be empty.")

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
        self.material = material
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
        self.remarks = remarks

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