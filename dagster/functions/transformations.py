import pandas as pd


def transform_adress(df: pd.DataFrame) -> pd.DataFrame:
    street = df["street_address"].fillna("").str.strip().str.lower()
    zip_code = df["zip_code"].fillna("").astype(str).str.strip()
    location = df["location"].fillna("").astype(str).str.strip().str.lower()

    # Build zip+location (no extra space if one is missing)
    zip_loc = (zip_code + " " + location).str.strip()
    zip_loc = zip_loc.replace("", pd.NA)

    # Only add comma if street is present
    full = (
        street.where(street != "", pd.NA)
        + ", "
        + zip_loc.where(zip_loc.notna(), "")
    ).fillna(zip_loc).str.strip(", ").replace("", pd.NA)

    df["full_adress"] = full
    return df


