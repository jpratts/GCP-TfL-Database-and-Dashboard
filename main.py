# Uses tflwrapper, a Python wrapper for the Transport for London API, to pull data about bike point use around Greater London. 
from tflwrapper import bikePoint, crowding
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import pandas_gbq
import datetime

def pull_data(event, context):
    #Credentials for BigQuery Access
    credentials_path = ~
    credentials = service_account.Credentials.from_service_account_file(credentials_path)

    # Sign-up to TFL Open Data service for API details
    app_key = ~

    # Retrieves crowding level at London Bridge Station using station code. Saves this to a DataFrame
    crwd = crowding(app_key)
    crowd_data = crwd.getLiveByNaptan("940GZZLULNB")
    crowd_pd = pd.DataFrame([crowd_data])

    # Retrieves details from all bike points around Greater London. They require cleaning given that its a multi-nested list
    bkpt = bikePoint(app_key)
    bike_data = bkpt.getAll()

    # Clean up data from the bike pull
    bike_list = []
    n = 0
    for x in bike_data:
        bikes_list = bike_list.append([
        bike_data[n]["id"],
        bike_data[n]["commonName"],
        bike_data[n]["placeType"],
        bike_data[n]["lat"],
        bike_data[n]["lon"],
        bike_data[n]["additionalProperties"][6]["value"],
        bike_data[n]["additionalProperties"][7]["value"],
        bike_data[n]["additionalProperties"][8]["value"],
        bike_data[n]["additionalProperties"][0]["modified"]
        ])
        n = n + 1

    bike_pd = pd.DataFrame(bike_list)
    bike_pd = bike_pd.rename(columns={
    0:"bikepoint_number",
    1:"location_name",
    2:"place_type",
    3:"lat",
    4:"lon",
    5:"nb_bikes",
    6:"empty_docks",
    7:"nb_docks",
    8:"dat_modified"})

    # Project id used in GCP
    project_id = ~

    # Table which bike data will be appended to
    bike_table = "tfl_data.bike_table"

    # Table which crowd data will be appended to
    crowd_table = "tfl_data.crowd_table"

    # Uses gbq to pass data into bigquery
    pandas_gbq.to_gbq(bike_pd, bike_table, project_id=project_id, credentials=credentials, if_exists="append")
    
    # Uses gbq to pass data into bigquery
    pandas_gbq.to_gbq(crowd_pd, crowd_table, project_id=project_id, credentials=credentials, if_exists="append")

