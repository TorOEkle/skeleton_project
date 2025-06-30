import pandas as pd


def transform_adress(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms the 'address' column in the DataFrame by splitting it into 'street', 'city', and 'zip_code'.
    
    Args:
        df (pd.DataFrame): Input DataFrame with an 'address' column.
        
    Returns:
        pd.DataFrame: DataFrame with new column "full_adress"
    """
    "street_address", "zip_code", "location"
    street = df['street_adress'].fillna('').str.lower()
    zip_code = df['zip_code'].fillna('').astype(str)
    location = df['location'].fillna('').astype(str)
    df['full_adress'] = street + ", " + zip_code + " " + location
    
    return df

