SHEET_NAME = "INVENTORY (DATA)"
REQUIRED_COLUMNS = [
    "ORE",
    "Ext ID",
    "Contractor",
    "Stockyard",
    "Pile",
    "WMT",
    "Ni",
    "Fe",
    "Al2O3",
    "SiO2",
    "MgO",
    "Remarks"
]
VALID_ELEMENTS = frozenset({
    "ni", "fe", "al", "si", "mg"
})
ROUND_COLUMNS = {
    "Ni": 2,
    "Fe": 2,
    "Al2O3": 2,
    "SiO2": 2,
    "MgO": 2,
    "WMT": 0
}
LABEL_WIDTH = 18
SEPARATOR = "-" * 80

VESSEL_CAPACITY_THRESHOLD = 6000