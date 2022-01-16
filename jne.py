import json
import re
from io import BytesIO

import pandas as pd
import requests
import urllib3

from secureimage_solver.captcha_api import predict

# Suppress Insecure Request Warning from requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def cek_resi(resilist):
    if isinstance(resilist, str):
        resilist = resilist.split("\n")
    resitring = "\n".join(resilist)

    headers = {
        "Origin": "https://www.jne.co.id",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "Referer": "https://www.jne.co.id/id/tracking/trace",
    }
    rsession = requests.Session()

    # Get Captcha Token
    rtoken = rsession.get(
        "https://www.jne.co.id/id/tracking/trace", verify=False, headers=headers
    )
    rtoken_content = rtoken.text
    token_search = re.search(
        r"_token\" type=\"hidden\" value=\"(.*)\"", rtoken_content, re.IGNORECASE
    )
    if token_search:
        token = token_search.group(1)

    # Solve Captcha
    rcaptcha = rsession.get(
        "https://www.jne.co.id/securimage", verify=False, headers=headers
    )
    with open("img.png", "wb") as f:
        f.write(rcaptcha.content)
    captcha = predict(BytesIO(rcaptcha.content))
    data = {"_token": token, "code": resitring, "captcha": captcha}

    # Get Resi Data
    rtrace = rsession.post(
        "https://www.jne.co.id/id/tracking/trace",
        data=data,
        headers=headers,
        verify=False,
    )

    trace_result = rtrace.text
    if "Captcha not match !" in trace_result:
        print("Captcha Salah!")
        return cek_resi(resilist)

    # Find Detail Resi
    for resi in resilist:
        detail_resi = rsession.get(
            f"https://www.jne.co.id/id/tracking/detail-new/{resi}",
            verify=False,
            headers=headers,
        )
        detail_resi = detail_resi.text
        if "Whoops" in detail_resi:  # Error page
            result_resi = {"resi": resi, "found": False}
            continue
        result_resi = {"resi": resi, "found": True}
        df_resi = pd.read_html(detail_resi)

        # Identification
        ident = df_resi[0].to_dict(orient="records")[0]
        result_resi["service"] = ident["Services"]
        result_resi["date_shipment"] = ident["Date Of Shipment"]
        result_resi["origin"] = ident["Origin"]
        result_resi["destination"] = ident["Destination"]

        # Shipper & Consignee
        shipcons = df_resi[1].to_dict(orient="records")
        result_resi["consignee"] = {}
        result_resi["shipper"] = {}
        result_resi["consignee"]["name"] = shipcons[0]["Consignee"]
        result_resi["consignee"]["address"] = shipcons[1]["Consignee"]
        result_resi["shipper"]["name"] = shipcons[0]["Shipper"]
        result_resi["shipper"]["address"] = shipcons[1]["Shipper"]

        # History Tracking
        histrack = df_resi[2].to_dict(orient="records")
        history_list = [
            {"time": history["History"], "desc": history["History.1"]}
            for history in histrack
        ]

        result_resi["history"] = history_list
    return result_resi
