
import json
from sys import stdin

def read_json():
    decoder = json.JSONDecoder()

    json_list = []
    current_object = ""

    for line in stdin:
        line = line.strip()
        current_object += line
        
        try:
            while current_object:
                new_json, index = decoder.raw_decode(current_object)
                current_object = current_object[index:].strip()
                json_list.append(new_json)

        except json.decoder.JSONDecodeError:
            pass

    return json_list

def output_to_json(python_data):
    return json.dumps(python_data)

def json_to_python(json_data):
    return json.loads(json_data)