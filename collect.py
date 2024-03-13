from typing import Dict
import requests
import json
import pandas as pd
from pandas_profiling import ProfileReport

api_url = "http://192.168.2.30:3002/api/"

def get_latest_block() -> int:
    """
    Retrieves the height of the latest block from a specified API endpoint.

    Args:
        api_url (str): The URL of the API endpoint.

    Returns:
        int: The height of the latest block as an integer.
    """
    response = requests.get(api_url + "blocks/tip")
    response_json = response.json()
    return int(response_json["height"])


def get_block_info(block_height: int) -> dict:
    """
    Retrieves information about a specific block from a given API endpoint.

    Args:
        block_height (int): The height of the block for which information is requested.

    Returns:
        dict: A JSON object containing the information about the requested block.
    """
    url = f"{api_url}block/{block_height}"
    response = requests.get(url)
    return json.loads(response.text)

def get_transaction(tx):
    url = f"{api_url}tx/{tx}"
    response = requests.get(url)
    return json.loads(response.text)

latest_block = get_latest_block()

n_blocks = 2

tx_df = []
for i in range(latest_block - 1, latest_block - (n_blocks + 1), -1):
    print(i)
    txs = get_block_info(i)['tx']

    for tx in txs[0:1]:
        tx_json = get_transaction(tx)
        normalized_df = pd.DataFrame(pd.json_normalize(tx_json))
        
        for column in normalized_df.columns:
            if normalized_df[column].apply(lambda x: isinstance(x, list)).any():
                normalized_df = normalized_df.explode(column)

        tx_df.append(normalized_df)
    
df = pd.concat(tx_df)

profile = ProfileReport(df, title="Pandas Profiling Report")
df.profile_report()
profile.to_file("your_report.html")
