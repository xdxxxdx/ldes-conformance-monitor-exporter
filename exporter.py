import requests
from json import JSONDecoder
import prometheus_client
import time
import xml.etree.ElementTree as ET

def extract_values_by_key(data, key):
    values = []

    if isinstance(data, dict):
        for k, v in data.items():
            if k == key:
                values.append(v)
            elif isinstance(v, (dict, list)):
                values.extend(extract_values_by_key(v, key))
    elif isinstance(data, list):
        for item in data:
            values.extend(extract_values_by_key(item, key))

    return values

def get_value_from_xml(xml_file, key):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Find the key in the XML file
    for element in root.iter(key):
        return element.text

    # If the key is not found, return None or raise an exception, depending on your requirements
    return None

def send_curl_start_request():
    url = "http://localhost:9000/api/rest/tests/start"
    payload = "{\r\n  \"system\": \"CF4AFE0FX7412X4410X83FCX78171EF71A1D\",\r\n  \"actor\": \"74EC1E15XDDFFX4BABXA3C6X60E9B06403A9\",\r\n  \"inputMapping\": [\r\n    {\r\n      \"input\": {\r\n        \"name\": \"endpointByName\",\r\n        \"value\": \"http://ldes-server:8080/kbo/by-name\"\r\n      }\r\n    }\r\n  ],\r\n   \"testCase\": [ \"ts1_tc9\" ]\r\n}"
    headers = {
        'ITB_API_KEY': '4ADF04C1X2ABFX4B08XA89DXABF8D577AE06',
        'Content-Type': 'text/plain'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print("sending start request to: " + url)
    return (extract_values_by_key(response.json(),'session'))


def get_curl_report_request(sessions):

    for session in sessions:
        url = "http://localhost:9000/api/rest/tests/report/"+session
        print(url)
        payload = {}
        headers = {
            'ITB_API_KEY': '4ADF04C1X2ABFX4B08XA89DXABF8D577AE06'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        while get_value_from_xml(response.text,session) != 'FAILURE':
            response = requests.request("GET", url, headers=headers, data=payload)
        print(response.text)



if __name__ == '__main__':
    sessions = send_curl_start_request()
    get_curl_report_request(sessions)