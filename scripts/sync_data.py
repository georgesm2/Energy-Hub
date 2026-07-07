import requests
import os
import subprocess
import pandas as pd
import time
from datetime import datetime, timedelta, UTC
import json

END_DATE = datetime.utcnow()

DB_NAME = os.environ.get("D1_DB_NAME", "energy_db")

DOWNSAMPLE_DAY_CUTOFF = pd.Timestamp.now('UTC').tz_localize(None) - pd.Timedelta(days=1)
DOWNSAMPLE_MONTH_CUTOFF = pd.Timestamp.now('UTC').tz_localize(None) - pd.Timedelta(days=30)
DOWNSAMPLE_YEAR_CUTOFF = pd.Timestamp.now('UTC').tz_localize(None) - pd.Timedelta(days=365)

# params is for anything above
# all energy prices are converted to £/kWh
# all generation is converted to MW
API_CONFIGS = {
    "market_price": {
        "url": "https://data.elexon.co.uk/bmrs/api/v1/balancing/pricing/market-index",
        "days_per_request": 7,
        "needs_unpacking": True,
        "json_data_key": "data",
        "columns_to_keep": ["startTime", "price"],
        "column_rename_map": {"startTime": "timestamp", "price": "value"},
        "category_label": "market_price",
        "conversion": 0.001,
        "params_in_url": False,
        "param_builder": lambda start, end: {
            "from": start.strftime("%Y-%m-%dT%H:%MZ"),
            "to": end.strftime("%Y-%m-%dT%H:%MZ"),
            "dataProviders": "APXMIDP"
        }    
    },
    "octopus_agile": {
        "url": "https://api.octopus.energy/v1/products/AGILE-24-10-01/electricity-tariffs/E-1R-AGILE-24-10-01-A/standard-unit-rates/",
        "days_per_request": 2,
        "needs_unpacking": True,
        "json_data_key": "results",
        "columns_to_keep": ["valid_from", "value_inc_vat"],
        "column_rename_map": {"valid_from": "timestamp", "value_inc_vat": "value"},
        "category_label": "octopus_agile",
        "conversion": 0.01,
        "params_in_url": False,
        "param_builder": lambda start, end: {
            "period_from": start.strftime("%Y-%m-%dT%H:%MZ"),
            "period_to": end.strftime("%Y-%m-%dT%H:%MZ"),
        }
    },
    "generation": {
        "url": "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELINST/stream",
        "days_per_request": 1,
        "needs_unpacking": False,
        "index_column": "pub",
        "columns_to_keep": ["publishTime", "fuelType", "generation"],
        "column_rename_map": {"publishTime": "timestamp", "fuelType": "category", "generation": "value"},
        "record_path": "data",
        "params_in_url": False,
        "param_builder": lambda start, end: {
            "publishDateTimeFrom": start.strftime("%Y-%m-%dT%H:%MZ"),
            "publishDateTimeTo": end.strftime("%Y-%m-%dT%H:%MZ"),
        }
    },
    "solar": {
        "url": "https://api.pvlive.uk/pvlive/api/v4/gsp/0",
        "days_per_request": 2,
        "needs_unpacking": True,
        "json_data_key": "data",
        "index_column": "gsp_id",
        "columns_to_keep": [1,2],
        "column_rename_map": {1: "timestamp", 2: "value"},
        "record_path": "data",
        "category_label": "SOLAR",
        "params_in_url": False,
        "param_builder": lambda start, end: {
            "start": start.strftime("%Y-%m-%dT%H:%MZ"),
            "end": end.strftime("%Y-%m-%dT%H:%MZ"),
        }
    },
    "carbon_intensity": {
        "url": "https://api.carbonintensity.org.uk/intensity/{from}/{to}",
        "days_per_request": 4,
        "needs_unpacking": True,
        "json_data_key": "data",
        "columns_to_keep": ["to", "intensity.actual"],
        "column_rename_map": {"to": "timestamp", "intensity.actual": "value"},
        "category_label": "carbon_intensity",
        "params_in_url": True,
        "param_builder": lambda start, end: {
            "from": start.strftime("%Y-%m-%dT%H:%MZ"),
            "to": end.strftime("%Y-%m-%dT%H:%MZ")
        }
    }
}

def fetch_historical_batches(config, start):
    all_data_frames = []

    url = config["url"]
    days_step = config["days_per_request"]
    columns_to_keep = config["columns_to_keep"]
    
    # move window through dates per API call
    while start < END_DATE:
        end = start + timedelta(days=days_step)
        if end > END_DATE:
            end = END_DATE

        print(f"Fetching data from {start} to {end}")
        params = config["param_builder"](start, end)

        if config["params_in_url"]:
            url = config["url"].format(**params)
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status() 
            data = response.json()

            if config["needs_unpacking"]:
                raw_rows = data.get(config["json_data_key"], [])
            else:
                raw_rows = data
            
            try:
                df = pd.json_normalize(raw_rows)
            except Exception as e:
                print(f"Error normalizing JSON data: {e}")
                df = pd.DataFrame(raw_rows)  # Create an empty DataFrame if normalization fails

            if not df.empty:
                df = df[columns_to_keep]
                all_data_frames.append(df)
        except Exception as e:
            print(f"Error fetching data: {e}")
            print("Stopping")
            break

        time.sleep(0.5)
        start = end

    if all_data_frames:
        combined_df = pd.concat(all_data_frames, ignore_index=True)
        return combined_df
    else:
        return pd.DataFrame()

def process_data(df, config):
    if df.empty:
        print(f"No data collected for {config['category_label']}")
        return pd.DataFrame()

    df = df.rename(columns=config['column_rename_map'])

    if "category_label" in config:
        df["category"] = config["category_label"]
    df["value"] = df["value"].astype(float)

    # convert to standard formats
    if "conversion" in config:
        df["value"] = df["value"] * config["conversion"]

    # separate data into modern full granularity vs month old granular vs year old granularity
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(None)
    deep_data = df[df["timestamp"] < DOWNSAMPLE_YEAR_CUTOFF].copy()
    year_data = df[(df["timestamp"] >= DOWNSAMPLE_YEAR_CUTOFF) & (df["timestamp"] < DOWNSAMPLE_MONTH_CUTOFF)].copy()
    month_data = df[(df["timestamp"] >= DOWNSAMPLE_MONTH_CUTOFF) & (df["timestamp"] < DOWNSAMPLE_DAY_CUTOFF)].copy()
    day_data = df[df["timestamp"] >= DOWNSAMPLE_DAY_CUTOFF].copy()


    processed_blocks = []

    if not deep_data.empty:
        deep_data["timestamp"] = deep_data["timestamp"].dt.floor("D")
        deep_data = deep_data.groupby(["timestamp", "category"])["value"].mean().reset_index()
        processed_blocks.append(deep_data)

    if not year_data.empty:
        year_data["timestamp"] = year_data["timestamp"].dt.floor("6h")
        year_data = year_data.groupby(["timestamp", "category"])["value"].mean().reset_index()
        processed_blocks.append(year_data)

    if not month_data.empty:
        month_data["timestamp"] = month_data["timestamp"].dt.floor("1h")
        month_data = month_data.groupby(["timestamp", "category"])["value"].mean().reset_index()
        processed_blocks.append(month_data)

    if not day_data.empty:
        day_data["timestamp"] = day_data["timestamp"].dt.floor("30min")
        day_data = day_data.groupby(["timestamp", "category"])["value"].mean().reset_index()
        processed_blocks.append(day_data)


    df = pd.concat(processed_blocks, ignore_index=True)

    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
    df = df[["timestamp", "category", "value"]]

    return df 

def push_to_d1(df,config):
    if df.empty:
        return

    temp_file = "batch_insert.sql"

    print("Preparing database upload")

    sql_statements = []
    for _, row in df.iterrows():
        statement = f"('{row['timestamp']}','{row['category']}',{row['value']})"
        sql_statements.append(statement)

    total_rows = len(sql_statements)
    chunk_size = 100
    print(f"Sending {total_rows} records to D1...")

    for i in range(0, total_rows, chunk_size):
        batch = sql_statements[i:i+chunk_size]
        combined_sql = f"INSERT OR IGNORE INTO energy_metrics (timestamp, category, value) VALUES \n" + ",\n".join(batch) + ";"
        with open(temp_file, "w") as f:
            f.write(combined_sql)

        try:
            cmd = [
                "npx", "wrangler", "d1", "execute", DB_NAME, "--remote", f"--file={temp_file}"
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

            progress = min(i + chunk_size, total_rows)
            print(f"Upload progress: {progress}/{total_rows} rows synced...")
        except subprocess.CalledProcessError as e:
            print(f"Upload error: {e.stderr.decode()}")
            break

def get_latest_date():
    try:
        cmd = [
            "npx", "wrangler", "d1", "execute", DB_NAME, "--remote", '--command="SELECT timestamp FROM energy_metrics ORDER BY timestamp DESC LIMIT 1"', "--json"
        ]
        output = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # get the latest time in database then set back a few hours as different APIs have different upload schedules
        start = pd.to_datetime(json.loads(output.stdout)[0]['results'][0]['timestamp']) - pd.Timedelta(hours=5)
        print(f"Last data at {start}.")
        return start
    except subprocess.CalledProcessError as e:
        print(f"Request error: {e.stderr.decode()}")
        return

def main():
    print("Requesting latest timestamp from D1")
    start = get_latest_date()
    print("Fetching historical data...")

    for api_name, config in API_CONFIGS.items():
        print(f"Fetching {api_name} data...")
        raw_df = fetch_historical_batches(config, start)
        df = process_data(raw_df, config)
        push_to_d1(df,config)
        print("Pushed history to D1.")

if __name__ == "__main__":
    main()