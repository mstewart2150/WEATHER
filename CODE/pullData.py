import requests
import pandas as pd

def get_gridpoint_info(lat, lon, api_key):
    response = requests.get(f"https://api.weather.gov/points/{lat},{lon}", headers={'User-Agent': 'weather-api-client'})
    response.raise_for_status()
    return response.json()

def get_nam_gfs_forecast(lat, lon, model, api_key):
    model = 'gfs'
    grid_info = get_gridpoint_info(lat, lon, api_key)
    forecast_office = grid_info['properties']['gridId']
    grid_x = grid_info['properties']['gridX']
    grid_y = grid_info['properties']['gridY']
    
    base_url = "https://api.weather.gov/gridpoints/"
    if model.lower() == 'gfs':
        forecast_url = f"{base_url}{forecast_office}/{grid_x},{grid_y}/forecast/hourly"
    elif model.lower() == 'nam':
        forecast_url = f"{base_url}{forecast_office}/{grid_x},{grid_y}/forecast"
    else:
        raise ValueError("Unsupported model. Use 'GFS' or 'NAM'.")
    
    response = requests.get(forecast_url, headers={'User-Agent': 'weather-api-client'})
    response.raise_for_status()
    return response.json()

def get_hrrr_data(lat, lon):
    # HRRR data can be accessed via NOMADS, here is a basic example of how to construct the URL
    base_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_hrrr_2d.pl"
    params = {
        'file': 'hrrr.t00z.wrfsfcf00.grib2',
        'lev_2_m_above_ground': 'on',
        'var_TMP': 'on',
        'subregion': '',
        'leftlon': lon,
        'rightlon': lon,
        'toplat': lat,
        'bottomlat': lat,
        'dir': '/hrrr.20230527'
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.content

def get_mos_data(lat, lon, model):
    base_url = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/"
    if model.lower() == 'gfsmos':
        data_url = f"{base_url}gfs.t00z.mos/MOSGFS"
    elif model.lower() == 'nammos':
        data_url = f"{base_url}nam.t00z.mos/MOSNAM"
    else:
        raise ValueError("Unsupported MOS model. Use 'GFSMOS' or 'NAMMOS'.")
    
    response = requests.get(data_url)
    response.raise_for_status()
    return response.text

def main(lat, lon):
    #lat = 40.367557
    #lon = -75.190168
    api_key = 'your_api_key_here'  # Replace with your actual API key
    
    try:
        # Get GFS forecast
        gfs_data = get_nam_gfs_forecast(lat, lon, 'GFS', api_key)
        gfs_df = pd.json_normalize(gfs_data['properties']['periods'])
        
        # Get HRRR data
        hrrr_data = get_hrrr_data(lat, lon)
        print("HRRR Data retrieved:", len(hrrr_data), "bytes")
        
        # Get MOS data
        gfsmos_data = get_mos_data(lat, lon, 'gfsmos')
        print("GFSMOS Data:")
        print(gfsmos_data[:500])  # Print first 500 characters for preview
        
    except Exception as e:
        print("Error:", e)

df_KPHL = main(40.367557, -75.190168)