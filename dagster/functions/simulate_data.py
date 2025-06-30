import random

from faker import Faker
import numpy as np
import pandas as pd


def generate_norwegian_addresses(n_addresses: int = 1000) -> pd.DataFrame:
    """
    Generate a DataFrame with exactly n_addresses unique Norwegian addresses.
    
    Parameters:
        n_addresses (int): Number of unique addresses to generate (default 1000).
    
    Returns:
        pd.DataFrame: DataFrame with columns [street_address, zip_code, location]
    """
    fake = Faker('no_NO')
    Faker.seed(42)
    random.seed(42)

    zip_locations = [
        ("0155", "Oslo"), ("5003", "Bergen"), ("7013", "Trondheim"),
        ("9008", "Tromsø"), ("2317", "Hamar"), ("6413", "Molde"),
        ("8006", "Bodø"), ("2609", "Lillehammer"), ("1723", "Sarpsborg"),
        ("7630", "Aasen"), ("1607", "Fredrikstad"), ("4370", "Egersund"),
        ("4878", "Grimstad"), ("3616", "Kongsberg"), ("8656", "Mosjøen")
    ]

    unique_addresses = set()

    while len(unique_addresses) < n_addresses:
        street = fake.street_address()
        zip_code, location = random.choice(zip_locations)
        unique_addresses.add((street, zip_code, location))
    id_list = random.sample(range(10000, 99999), n_addresses)
    df = pd.DataFrame(list(unique_addresses), columns=["street_address", "zip_code", "location"])
    df.insert(0, "household_id", id_list)
    
    return df



def simulate_person_data(id_adress: pd.Series) -> pd.DataFrame:
    """
    Simulates person data with two persons per address.
    Age gap between co-residents is <= 5 years. Each person has a unique 6-digit ID.
    
    Parameters:
        id_adress (pd.Series): Series of address IDs.
    
    Returns:
        pd.DataFrame: DataFrame with columns [person_id, address_id, name, year_of_birth, income]
    """
    Faker.seed(105)
    fake = Faker('no_NO')
    random.seed(105)
    np.random.seed(105)

    n_addresses = len(id_adress)

    # Generate base year of birth for each address
    base_yobs = np.random.randint(1950, 1996, size=n_addresses)

    # For each address, generate 2 persons with <= 5 year age gap
    person_rows = []
    used_person_ids = set()
    
    for i in range(n_addresses):
        address_id = id_adress.iloc[i]
        yob1 = base_yobs[i]
        yob2 = yob1 + random.randint(-5, 5)
        yob2 = np.clip(yob2, 1950, 1995)

        for yob in [yob1, yob2]:
            # Generate unique 6-digit person ID
            while True:
                person_id = random.randint(100000, 999999)
                if person_id not in used_person_ids:
                    used_person_ids.add(person_id)
                    break
            
            normal_noise = np.random.normal(loc=1.2, scale=0.1)
            income = round((2025 - yob) * normal_noise * 10000)
            person_rows.append({
                "person_id": person_id,
                "household_id": address_id,
                "name": fake.name(),
                "year_of_birth": yob,
                "income": int(income)
            })

    return pd.DataFrame(person_rows)
