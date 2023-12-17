from app import app
from entsoe import EntsoePandasClient
import pandas as pd

from modules.config import get_entsoe_api_key

def get_entsoe_data(country_code: str, start: str, end: str):
    client = EntsoePandasClient(api_key=get_entsoe_api_key())
    start_pd = pd.Timestamp(start, tz='Europe/Brussels')
    end_pd = pd.Timestamp(end, tz='Europe/Brussels')
    
    ts = client.query_generation(country_code, start=start_pd,end=end_pd, psr_type=None)
    return ts.to_json()
