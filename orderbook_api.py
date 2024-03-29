"""
OrderbookAPI for fetching relevant data using the CoW Swap Orderbook API.
"""
# pylint: disable=logging-fstring-interpolation

from typing import Any, Optional
import json
import requests
from constants import (
    header,
    REQUEST_TIMEOUT,
    SUCCESS_CODE,
    FAIL_CODE,
)

PROD_BASE_URL = "https://api.cow.fi/xdai/api/v1/"
BARN_BASE_URL = "https://barn.api.cow.fi/xdai/api/v1/"


def get_solver_competition_data(tx_hash: str) -> Optional[dict[str, Any]]:
    """
    Get solver competition data from a transaction hash.
    The returned dict follows the schema outlined here:
    https://api.cow.fi/docs/#/default/get_api_v1_solver_competition_by_tx_hash__tx_hash_
    """
    prod_endpoint_url = f"{PROD_BASE_URL}solver_competition/by_tx_hash/{tx_hash}"
    barn_endpoint_url = f"{BARN_BASE_URL}solver_competition/by_tx_hash/{tx_hash}"
    solver_competition_data: Optional[dict[str, Any]] = None
    environment = "prod"
    try:
        json_competition_data = requests.get(
            prod_endpoint_url,
            headers=header,
            timeout=REQUEST_TIMEOUT,
        )
        if json_competition_data.status_code == SUCCESS_CODE:
            solver_competition_data = json.loads(json_competition_data.text)
        elif json_competition_data.status_code == FAIL_CODE:
            barn_competition_data = requests.get(
                barn_endpoint_url, headers=header, timeout=REQUEST_TIMEOUT
            )
            if barn_competition_data.status_code == SUCCESS_CODE:
                environment = "barn"
                solver_competition_data = json.loads(barn_competition_data.text)
            else:
                return None, None
    except requests.RequestException as err:
        print("Issue with orderbook api")
        return None, None
    return solver_competition_data, environment
