"""
This is a pythons script that fetches the current status of the stations from the API, 
processes the raw data if necessary (preserving the station location etc. in the data),
and stores them in one single file every time it is run without overwriting the previous data.
"""

import requests
import datetime
import json

url = "https://api.wstw.at/gateway/WL_WIENMOBIL_API/1/station_status.json"

def get_station_status():
    """
    fetches the station status from the API
    :return: data"""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("API request failed. Status code {}".format(response.status_code))
    data = response.json()
    print("API request successful.")
    return data

def processing(raw_data):
    """
    processes the raw data if necessary -> maybe into smaller functions ? 
    :param raw_data: raw data from the API
    :return: processed data 
    """
    # Convert main last_updated timestamp
    if 'last_updated' in raw_data:  
        main_timestamp = raw_data['last_updated']  
        main_time = datetime.datetime.fromtimestamp(
            main_timestamp
        ).strftime('%Y-%m-%d %H:%M:%S')
        raw_data['last_updated'] = main_time  

    # checking if certain attributes are stable for all 
    # is_renting: True
    all_renting = all(station.get('is_renting', False) 
                     for station in raw_data['data']['stations'])
    # is_returning: True
    all_returning = all((station.get('is_returning', False)
                         for station in raw_data['data']['stations']))
    # is_installed: True
    all_installed = all((station.get('is_installed', False)
                         for station in raw_data['data']['stations']))
    
    # process each station
    for station in raw_data['data']['stations']:
        # convert timestamp to datetime
        if 'last_reported' in station:
            timestamp = station['last_reported']
            station_time = datetime.datetime.fromtimestamp(
                timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
            # keep last_reported only if it's different from last_updated
            if station_time == raw_data['last_updated']:
                del station['last_reported']
            else:
                station['last_reported'] = station_time
        
        # Remove is_renting if all are True
        if all_renting and 'is_renting' in station:
            del station['is_renting']
        # Remove is_returning if all are True
        if all_returning and 'is_returning' in station:
            del station['is_returning']
        # Remove is_installed if all are True
        if all_installed and 'is_installed' in station:
            del station['is_installed']
    
    processed_data = raw_data
    return processed_data

def save_file(data):
    """
    saves data to a file
    :param data: dict, data to be saved
    :param filename: str, name of the file
    """
    now = datetime.datetime.now() # get current date and time
    str_date = now.strftime("%Y-%m-%d_%H-%M-%S") # need to convert now into a string to use it as file name 
    filename = "station_status_" + str_date # saves file under this name
    with open(f"{filename}.json", "w", encoding='utf-8') as f: 
        # w = write, creates new file if the file does not exist
        # encoding for special characters 
        json.dump(data, f, ensure_ascii=False, indent=4) # adds content to the json file (need dump because it is json data)
    print("Data saved successfully.")

if __name__ == "__main__": 
    data = get_station_status()
    print(data)
    data = processing(data)
    print(data)
    save_file(data) # save data to a single file 
    