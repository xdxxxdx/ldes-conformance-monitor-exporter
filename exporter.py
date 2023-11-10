import requests
from prometheus_client import start_http_server, Gauge
import random
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

def get_all_keys(xml_tree):
    all_keys = set()

    for element in xml_tree.iter():
        all_keys.add(element.tag)

    return all_keys

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

def load_response_text_to_xml(response_text):
    try:
        root = ET.fromstring(response_text)
        return ET.ElementTree(root)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None
def get_curl_report_request(sessions):

    for session in sessions:
        url = "http://localhost:9000/api/rest/tests/report/"+session
        print(url)
        payload = {}
        headers = {
            'ITB_API_KEY': '4ADF04C1X2ABFX4B08XA89DXABF8D577AE06'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        while response.status_code == 404:
            response = requests.request("GET", url, headers=headers, data=payload)
        while ET.fromstring(response.text).find(
                '{http://www.gitb.com/tr/v1/}result').text == "UNDEFINED":
            response = requests.request("GET", url, headers=headers, data=payload)
        return ET.fromstring(response.text).find(
                '{http://www.gitb.com/tr/v1/}result').text

example_metric = Gauge('example_metric', 'Description of example metric')
# Function to update the metric value
def update_metric():
    while True:
        # Simulate updating a metric value (replace this with your actual metric logic)
        metric_value = random.randint(1, 100)
        example_metric.set(metric_value)

        # Sleep for a short duration (e.g., 5 seconds)
        time.sleep(5)
        
if __name__ == '__main__':
    start_http_server(8000)
    sessions = send_curl_start_request()
    get_curl_report_request(sessions)
    update_metric()
