import requests
import json
from constants import header, REQUEST_TIMEOUT, SUCCESS_CODE


def fetch_hashes(start, end) -> list[str]:

    res = []
    url = (
        "https://api.gnosisscan.io/api?module=account&action=txlist"
        + "&address=0x9008D19f58AAbD9eD0D60971565AA8510560ab41"
        + "&startblock="
        + str(start)
        + "&endblock="
        + str(end)
        + "&sort=asc&apikey=YourApiKeyToken"
    )
    try:
        response = requests.get(
            url,
            headers=header,
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == SUCCESS_CODE:
            data = json.loads(response.text)
            i = 0
            for x in data['result']:
                res.append(x['hash'])
    except Exception as e:
        return []

    return res
