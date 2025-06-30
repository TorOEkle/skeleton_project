import pandas as pd
from pandas.testing import assert_frame_equal
import pytest
from functions.transformations import transform_adress

@pytest.fixture
def raw_df():
    return pd.DataFrame({
        "street_adress": ["Storgata 4", None, "Hovedveien 12B", None],
        "zip_code": ["0155", "0554", None, None],
        "location": ["Oslo", None, "Trondheim", "Bergen"]
    })

def test_transform_adress(raw_df):
    cleaned = transform_adress(raw_df.copy())

    expected = pd.DataFrame({
        "street_adress": ["Storgata 4", None, "Hovedveien 12B", None],
        "zip_code": ["0155", "0554", None, None],
        "location": ["Oslo", None, "Trondheim", "Bergen"],
        "full_adress": [
            "storgata 4, 0155 Oslo",
            "0554",
            "hovedveien 12b, Trondheim",
            "Bergen"
        ]
    })

    assert_frame_equal(cleaned, expected, check_dtype=False)