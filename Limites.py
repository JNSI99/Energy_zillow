"""
LL97 Emission Factors by ESPM Property Type
Source: 1 RCNY §103-14 - NYC Department of Buildings
https://www.nyc.gov/assets/buildings/rules/1_RCNY_103-14.pdf

Units: tCO2e per square foot per year
Periods: 2024-2029, 2030-2034, 2035-2039, 2040-2049, 2050+
"""

from typing import Optional

# -----------------------------------------------------------------------
# Master lookup table — all 62 ESPM property types (1 RCNY §103-14)
# Keys match exactly the "Primary Property Type - Self Selected" field in LL84
# -----------------------------------------------------------------------
EMISSION_FACTORS: dict[str, dict[str, float]] = {
    "Adult Education":                              {"2024": 0.00758,  "2030": 0.003565528, "2035": 0.002674146, "2040": 0.001782764, "2050": 0.0},
    "Ambulatory Surgical Center":                   {"2024": 0.01181,  "2030": 0.008980612, "2035": 0.006735459, "2040": 0.004490306, "2050": 0.0},
    "Automobile Dealership":                        {"2024": 0.00675,  "2030": 0.002824097, "2035": 0.002118072, "2040": 0.001412048, "2050": 0.0},
    "Bank Branch":                                  {"2024": 0.00987,  "2030": 0.004036172, "2035": 0.003027129, "2040": 0.002018086, "2050": 0.0},
    "Bowling Alley":                                {"2024": 0.00574,  "2030": 0.003103815, "2035": 0.002327861, "2040": 0.001551907, "2050": 0.0},
    "College/University":                           {"2024": 0.00987,  "2030": 0.002099748, "2035": 0.001236322, "2040": 0.000180818, "2050": 0.0},
    "Convenience Store without Gas Station":        {"2024": 0.00675,  "2030": 0.003540032, "2035": 0.002655024, "2040": 0.001770016, "2050": 0.0},
    "Courthouse":                                   {"2024": 0.00426,  "2030": 0.001480533, "2035": 0.001110400, "2040": 0.000740266, "2050": 0.0},
    "Data Center":                                  {"2024": 0.02381,  "2030": 0.014791131, "2035": 0.011093348, "2040": 0.007395565, "2050": 0.0},
    "Distribution Center":                          {"2024": 0.00574,  "2030": 0.000991600, "2035": 0.000549637, "2040": 0.000123568, "2050": 0.0},
    "Enclosed Mall":                                {"2024": 0.01074,  "2030": 0.003983803, "2035": 0.002987852, "2040": 0.001991901, "2050": 0.0},
    "Financial Office":                             {"2024": 0.00846,  "2030": 0.003697004, "2035": 0.002772753, "2040": 0.001848502, "2050": 0.0},
    "Fitness Center/Health Club/Gym":               {"2024": 0.00987,  "2030": 0.003946728, "2035": 0.002960046, "2040": 0.001973364, "2050": 0.0},
    "Food Sales":                                   {"2024": 0.01181,  "2030": 0.005208880, "2035": 0.003906660, "2040": 0.002604440, "2050": 0.0},
    "Food Service":                                 {"2024": 0.01181,  "2030": 0.007749414, "2035": 0.005812060, "2040": 0.003874707, "2050": 0.0},
    "Hospital (General Medical & Surgical)":        {"2024": 0.02381,  "2030": 0.007335204, "2035": 0.004654044, "2040": 0.002997851, "2050": 0.0},
    "Hotel":                                        {"2024": 0.00987,  "2030": 0.003850668, "2035": 0.002640017, "2040": 0.001465772, "2050": 0.0},
    "K-12 School":                                  {"2024": 0.00675,  "2030": 0.002230588, "2035": 0.001488109, "2040": 0.000809607, "2050": 0.0},
    "Laboratory":                                   {"2024": 0.02381,  "2030": 0.026029868, "2035": 0.019522401, "2040": 0.013014934, "2050": 0.0},
    "Library":                                      {"2024": 0.00675,  "2030": 0.002218412, "2035": 0.001663809, "2040": 0.001109206, "2050": 0.0},
    "Lifestyle Center":                             {"2024": 0.00846,  "2030": 0.004705850, "2035": 0.003529387, "2040": 0.002352925, "2050": 0.0},
    "Mailing Center/Post Office":                   {"2024": 0.00426,  "2030": 0.001980440, "2035": 0.001485330, "2040": 0.000990220, "2050": 0.0},
    "Manufacturing/Industrial Plant":               {"2024": 0.00758,  "2030": 0.001417030, "2035": 0.000975993, "2040": 0.000508346, "2050": 0.0},
    "Medical Office":                               {"2024": 0.01074,  "2030": 0.002912778, "2035": 0.001683565, "2040": 0.000407851, "2050": 0.0},
    "Movie Theater":                                {"2024": 0.01181,  "2030": 0.005395268, "2035": 0.004046451, "2040": 0.002697634, "2050": 0.0},
    "Multifamily Housing":                          {"2024": 0.00675,  "2030": 0.003346640, "2035": 0.002692183, "2040": 0.002052731, "2050": 0.0},
    "Museum":                                       {"2024": 0.01181,  "2030": 0.005395800, "2035": 0.004046850, "2040": 0.002697900, "2050": 0.0},
    "Non-Refrigerated Warehouse":                   {"2024": 0.00426,  "2030": 0.000883187, "2035": 0.000568051, "2040": 0.000163152, "2050": 0.0},
    "Office":                                       {"2024": 0.00758,  "2030": 0.002690852, "2035": 0.001652340, "2040": 0.000581893, "2050": 0.0},
    "Other - Education":                            {"2024": 0.00846,  "2030": 0.002934006, "2035": 0.001867699, "2040": 0.000839571, "2050": 0.0},
    "Other - Entertainment/Public Assembly":        {"2024": 0.00987,  "2030": 0.002956738, "2035": 0.002250122, "2040": 0.001355610, "2050": 0.0},
    "Other - Lodging/Residential":                  {"2024": 0.00758,  "2030": 0.001901982, "2035": 0.001329089, "2040": 0.000762093, "2050": 0.0},
    "Other - Mall":                                 {"2024": 0.01074,  "2030": 0.001928226, "2035": 0.001006426, "2040": 0.000067983, "2050": 0.0},
    "Other - Public Services":                      {"2024": 0.00758,  "2030": 0.003808033, "2035": 0.002856025, "2040": 0.001904017, "2050": 0.0},
    "Other - Recreation":                           {"2024": 0.00987,  "2030": 0.004479570, "2035": 0.003359678, "2040": 0.002239785, "2050": 0.0},
    "Other - Restaurant/Bar":                       {"2024": 0.02381,  "2030": 0.008505075, "2035": 0.006378806, "2040": 0.004252537, "2050": 0.0},
    "Other - Services":                             {"2024": 0.01074,  "2030": 0.001823381, "2035": 0.001367536, "2040": 0.000911691, "2050": 0.0},
    "Other - Specialty Hospital":                   {"2024": 0.02381,  "2030": 0.006321819, "2035": 0.004741365, "2040": 0.003160910, "2050": 0.0},
    "Other - Technology/Science":                   {"2024": 0.02381,  "2030": 0.010446456, "2035": 0.007834842, "2040": 0.005223228, "2050": 0.0},
    "Outpatient Rehabilitation/Physical Therapy":   {"2024": 0.01181,  "2030": 0.006018323, "2035": 0.004513742, "2040": 0.003009161, "2050": 0.0},
    "Parking":                                      {"2024": 0.00426,  "2030": 0.000214421, "2035": 0.000104943, "2040": 0.000000000, "2050": 0.0},
    "Performing Arts":                              {"2024": 0.00846,  "2030": 0.002472539, "2035": 0.001399345, "2040": 0.000000000, "2050": 0.0},
    "Personal Services (Health/Beauty, Dry Cleaning, etc.)": {"2024": 0.00574, "2030": 0.004843037, "2035": 0.003632278, "2040": 0.002421519, "2050": 0.0},
    "Pre-school/Daycare":                           {"2024": 0.00675,  "2030": 0.002362874, "2035": 0.001772155, "2040": 0.001181437, "2050": 0.0},
    "Refrigerated Warehouse":                       {"2024": 0.00987,  "2030": 0.002852131, "2035": 0.002139098, "2040": 0.001426066, "2050": 0.0},
    "Repair Services (Vehicle, Shoe, Locksmith, etc.)": {"2024": 0.00426, "2030": 0.002210699, "2035": 0.001658024, "2040": 0.001105349, "2050": 0.0},
    "Residence Hall/Dormitory":                     {"2024": 0.00758,  "2030": 0.002464089, "2035": 0.001332459, "2040": 0.000528616, "2050": 0.0},
    "Residential Care Facility":                    {"2024": 0.01138,  "2030": 0.004893124, "2035": 0.004027812, "2040": 0.002272629, "2050": 0.0},
    "Restaurant":                                   {"2024": 0.01181,  "2030": 0.004038374, "2035": 0.003028780, "2040": 0.002019187, "2050": 0.0},
    "Retail Store":                                 {"2024": 0.00758,  "2030": 0.002104490, "2035": 0.001216050, "2040": 0.000176040, "2050": 0.0},
    "Self-Storage Facility":                        {"2024": 0.00426,  "2030": 0.000611830, "2035": 0.000404901, "2040": 0.000132282, "2050": 0.0},
    "Senior Care Community":                        {"2024": 0.01138,  "2030": 0.004410123, "2035": 0.003336443, "2040": 0.002277912, "2050": 0.0},
    "Social/Meeting Hall":                          {"2024": 0.00987,  "2030": 0.003833108, "2035": 0.002874831, "2040": 0.001916554, "2050": 0.0},
    "Strip Mall":                                   {"2024": 0.01181,  "2030": 0.001361842, "2035": 0.000600493, "2040": 0.000038512, "2050": 0.0},
    "Supermarket/Grocery Store":                    {"2024": 0.02381,  "2030": 0.006755190, "2035": 0.004256103, "2040": 0.002030027, "2050": 0.0},
    "Transportation Terminal/Station":              {"2024": 0.00426,  "2030": 0.000571669, "2035": 0.000428752, "2040": 0.000285834, "2050": 0.0},
    "Urgent Care/Clinic/Other Outpatient":          {"2024": 0.01181,  "2030": 0.005772375, "2035": 0.004329281, "2040": 0.002886187, "2050": 0.0},
    "Vocational School":                            {"2024": 0.00574,  "2030": 0.004613122, "2035": 0.003459842, "2040": 0.002306561, "2050": 0.0},
    "Wholesale Club/Supercenter":                   {"2024": 0.01138,  "2030": 0.004264962, "2035": 0.003198721, "2040": 0.002132481, "2050": 0.0},
    "Worship Facility":                             {"2024": 0.00574,  "2030": 0.001230602, "2035": 0.000866921, "2040": 0.000549306, "2050": 0.0},
}

# Compliance period boundaries
PERIODS = [
    (2050, "2050"),
    (2040, "2040"),
    (2035, "2035"),
    (2030, "2030"),
    (2024, "2024"),
]


def _get_period_key(year: int) -> str:
    """Map a calendar year to the correct compliance period key."""
    for threshold, key in PERIODS:
        if year >= threshold:
            return key
    raise ValueError(f"Year {year} is before LL97 compliance started (2024).")


def get_emission_factor(
    primary_property_type: str,
    year: int,
    fuzzy: bool = True,
) -> Optional[float]:
    """
    Return the LL97 emission factor (tCO2e/sqft/year) for a given
    ESPM property type and calendar year.

    Args:
        primary_property_type: Value from LL84 column
                               "Primary Property Type - Self Selected".
                               Must match exactly one of the 62 ESPM types
                               in 1 RCNY §103-14, unless fuzzy=True.
        year:                  Calendar year (2024-2050+).
        fuzzy:                 If True, attempt case-insensitive / partial
                               match when exact key is not found.

    Returns:
        float  — emission factor in tCO2e per sqft per year, or
        None   — if property type is not found and fuzzy match fails.

    Examples:
        >>> get_emission_factor("Multifamily Housing", 2024)
        0.00675
        >>> get_emission_factor("multifamily housing", 2030)   # fuzzy
        0.003346640
        >>> get_emission_factor("Office", 2035)
        0.001652340
        >>> get_emission_factor("Office", 2050)
        0.0
    """
    period_key = _get_period_key(year)

    # 1. Exact match
    if primary_property_type in EMISSION_FACTORS:
        return EMISSION_FACTORS[primary_property_type][period_key]

    if not fuzzy:
        return None

    # 2. Case-insensitive match
    lower = primary_property_type.strip().lower()
    for key, factors in EMISSION_FACTORS.items():
        if key.lower() == lower:
            return factors[period_key]

    # 3. Partial / substring match (returns first hit)
    for key, factors in EMISSION_FACTORS.items():
        if lower in key.lower() or key.lower() in lower:
            return factors[period_key]

    return None


def get_emission_factor_all_periods(
    primary_property_type: str,
    fuzzy: bool = True,
) -> Optional[dict[str, float]]:
    """
    Return emission factors for ALL compliance periods for a given
    ESPM property type.

    Returns:
        dict with keys "2024", "2030", "2035", "2040", "2050", or None.

    Example:
        >>> get_emission_factor_all_periods("Multifamily Housing")
        {
            "2024": 0.00675,
            "2030": 0.003346640,
            "2035": 0.002692183,
            "2040": 0.002052731,
            "2050": 0.0,
        }
    """
    if primary_property_type in EMISSION_FACTORS:
        return dict(EMISSION_FACTORS[primary_property_type])

    if not fuzzy:
        return None

    lower = primary_property_type.strip().lower()
    for key, factors in EMISSION_FACTORS.items():
        if key.lower() == lower:
            return dict(factors)

    for key, factors in EMISSION_FACTORS.items():
        if lower in key.lower() or key.lower() in lower:
            return dict(factors)

    return None


def calculate_emissions_limit(
    primary_property_type: str,
    gross_floor_area_sqft: float,
    year: int,
) -> Optional[float]:
    """
    Calculate the total annual GHG emissions LIMIT for a building.

    Formula (1 RCNY §103-14 Equation 103-14.1):
        Limit (tCO2e) = gross_floor_area_sqft × emission_factor

    Args:
        primary_property_type: LL84 "Primary Property Type - Self Selected"
        gross_floor_area_sqft: From LL84 "Largest Property Use - Gross Floor Area (ft²)"
                               or PLUTO BldgArea
        year:                  Calendar year

    Returns:
        float — annual emissions limit in tCO2e, or None if type not found.
    """
    factor = get_emission_factor(primary_property_type, year)
    if factor is None:
        return None
    return gross_floor_area_sqft * factor


def calculate_penalty(
    actual_emissions_tco2e: float,
    primary_property_type: str,
    gross_floor_area_sqft: float,
    year: int,
    penalty_rate_usd: float = 268.0,
) -> dict:
    """
    Calculate the LL97 annual penalty for a building.

    Args:
        actual_emissions_tco2e: From LL84 "Total GHG Emissions (Metric Tons CO2e)"
                                or calculated from fuel use × GHG coefficients
        primary_property_type:  LL84 "Primary Property Type - Self Selected"
        gross_floor_area_sqft:  Building gross floor area in sqft
        year:                   Calendar year
        penalty_rate_usd:       $/tCO2e (default $268, per LL97)

    Returns:
        dict with keys:
            "year", "period", "emissions_limit_tco2e", "actual_emissions_tco2e",
            "excess_tco2e", "annual_penalty_usd", "compliant"
    """
    limit = calculate_emissions_limit(primary_property_type, gross_floor_area_sqft, year)
    period_key = _get_period_key(year)
    excess = max(0.0, actual_emissions_tco2e - limit) if limit is not None else None
    penalty = excess * penalty_rate_usd if excess is not None else None

    return {
        "year":                    year,
        "period":                  f"{period_key}–{'2029' if period_key=='2024' else '2034' if period_key=='2030' else '2039' if period_key=='2035' else '2049' if period_key=='2040' else '∞'}",
        "emission_factor":         get_emission_factor(primary_property_type, year),
        "emissions_limit_tco2e":   round(limit, 4) if limit else None,
        "actual_emissions_tco2e":  round(actual_emissions_tco2e, 4),
        "excess_tco2e":            round(excess, 4) if excess is not None else None,
        "annual_penalty_usd":      round(penalty, 2) if penalty is not None else None,
        "compliant":               excess == 0.0 if excess is not None else None,
    }


# -----------------------------------------------------------------------
# Quick smoke test
# -----------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("LL97 Emission Factor Lookup — Quick Test")
    print("=" * 60)

    # Test 1: single factor
    prop = "Multifamily Housing"
    for yr in [2024, 2030, 2035, 2040, 2050]:
        f = get_emission_factor(prop, yr)
        print(f"  {prop} | {yr}: {f} tCO2e/sqft")

    print()

    # Test 2: all periods at once
    print("All periods — Office:")
    print(" ", get_emission_factor_all_periods("Office"))

    print()

    # Test 3: fuzzy match
    print("Fuzzy match 'multifamily' 2030:", get_emission_factor("multifamily", 2030))
    print("Fuzzy match 'grocery' 2030:    ", get_emission_factor("grocery", 2030))

    print()

    # Test 4: full penalty calc
    print("Penalty calc — 100k sqft Office, 950 tCO2e actual, 2024:")
    result = calculate_penalty(
        actual_emissions_tco2e=950,
        primary_property_type="Office",
        gross_floor_area_sqft=100_000,
        year=2024,
    )
    for k, v in result.items():
        print(f"  {k}: {v}")

    print()
    print("Same building in 2030 (no changes):")
    result2 = calculate_penalty(
        actual_emissions_tco2e=950,
        primary_property_type="Office",
        gross_floor_area_sqft=100_000,
        year=2030,
    )
    for k, v in result2.items():
        print(f"  {k}: {v}")
