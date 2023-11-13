import requests
from prometheus_client import start_http_server, Gauge,Info
import time
import xml.etree.ElementTree as ET
import os
import logging
from dotenv import load_dotenv



#XML PROCESSING
#funciion to load xml response to xml tree
def load_response_text_to_xml(response_text):
    try:
        root = ET.fromstring(response_text)
        return ET.ElementTree(root)
    except ET.ParseError as e:
        logging.info(f"Error parsing XML: {e}")
        return None

#function to get all keys from xml tree
def get_all_keys(xml_tree):
    all_keys = set()

    for element in xml_tree.iter():
        all_keys.add(element.tag)

    return all_keys

#function to get all values from xml tree
def get_value_from_xml(xml_file, key):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Find the key in the XML file
    for element in root.iter(key):
        return element.text

    # If the key is not found, return None or raise an exception, depending on your requirements
    return None


# function to extract values from nested JSON dict
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




#Interaction with ITB
#function to send start request to ITB for a specific test sessionn and return the session ids
def send_curl_start_request(start_api_endpoint, start_payload, itb_api_key):
    url = start_api_endpoint
    payload =start_payload
    headers = {
        'ITB_API_KEY': itb_api_key,
        'Content-Type': 'text/plain'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    logging.info("Sending start request to: " + url + "\n with payload" + payload)
    return (extract_values_by_key(response.json(),'session'))


#function to get report request from ITB for a specific test session
def get_curl_report_request(sessions,itb_api_key,report_api_endpoint):
    results = {}
    namespace = {'ns2': 'http://www.gitb.com/core/v1/'}
    for session in sessions:
        url = report_api_endpoint + session
        logging.info("Getting report for: " + url)
        payload = {}
        headers = {
            'ITB_API_KEY': itb_api_key
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        #When the response is success 200 with a valid test result, return the report to the prometheuse.
        while (response.status_code != 200) or ET.fromstring(response.text).find(
                '{http://www.gitb.com/tr/v1/}result').text == "UNDEFINED":
            response = requests.request("GET", url, headers=headers, data=payload)
        test_descripton = ET.fromstring(response.text).find('.//ns2:name', namespaces=namespace).text
        result = ET.fromstring(response.text).find(
                '{http://www.gitb.com/tr/v1/}result').text

        results[test_descripton] = ET.fromstring(response.text).find('{http://www.gitb.com/tr/v1/}result').text
        logging.info("result for "+ test_descripton  +"is: " + result )
    return results

if __name__ == '__main__':
    start_http_server(8000)
    #load configurable parameters
    load_dotenv()
    start_api_endpoint = os.getenv("START_API_ENDPOINT")
    start_payload= os.getenv("START_PAYLOAD")
    itb_api_key = os.getenv("ITB_API_KEY")
    debug_level =os.getenv("DEBUG_LEVEL")
    report_api_endpoint = os.getenv("REPORT_API_ENDPOINT")
    logging.basicConfig(level=debug_level)

    #todo: Define how to reflect results to Prometheuse.
    #todo: Which testcases we are looking for from the ITB?
    info_1 = Info('test_results_info_1', 'The results of test')
    while True:
         sessions = send_curl_start_request(start_api_endpoint,start_payload,itb_api_key)
         test_results = get_curl_report_request(sessions,itb_api_key,report_api_endpoint)
         print(test_results)
         test_description, result = next(iter(test_results.items()))
         info_1.info({'test session': sessions[0], 'test description':test_description, 'test result': result})
