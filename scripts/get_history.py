import requests
import os
import subprocess
import pandas as pd
import time
from datetime import datetime, timedelta, UTC

START_DATE = datetime(2026, 6, 14, 12, 0, 0)
END_DATE = datetime.utcnow()

DOWNSAMPLE_MONTH_CUTOFF = pd.Timestamp.now('UTC').tz_localize(None) - pd.Timedelta(days=30)
DOWNSAMPLE_YEAR_CUTOFF = pd.Timestamp.now('UTC').tz_localize(None) - pd.Timedelta(days=365)

# params is for anything above
# all energy prices are converted to £/kWh
# all generation is converted to MW
API_CONFIGS = {
    "market_price": {
        "url": "https://data.elexon.co.uk/bmrs/api/v1/balancing/pricing/market-index",
        "days_per_request": 7,
        "json_data_key": "data",
        "is_wide_format": False,
        "columns_to_keep": ["startTime", "price"],
        "column_rename_map": {"startTime": "timestamp", "price": "value"},
        "category_label": "market_price",
        "conversion": 0.001,
        "param_builder": lambda start, end: {
            "from": start.strftime("%Y-%m-%dT%H:%MZ"),
            "to": end.strftime("%Y-%m-%dT%H:%MZ"),
            "dataProviders": "APXMIDP"
        }    
    },
    "octopus_agile": {
        "url": "https://api.octopus.energy/v1/products/AGILE-24-10-01/electricity-tariffs/E-1R-AGILE-24-10-01-A/standard-unit-rates/",
        "days_per_request": 2,
        "json_data_key": "results",
        "is_wide_format": False,
        "columns_to_keep": ["valid_from", "value_inc_vat"],
        "column_rename_map": {"valid_from": "timestamp", "value_inc_vat": "value"},
        "category_label": "octopus_agile",
        "conversion": 0.01,
        "param_builder": lambda start, end: {
            "period_from": start.strftime("%Y-%m-%dT%H:%MZ"),
            "period_to": end.strftime("%Y-%m-%dT%H:%MZ"),
        }
    },
    "generation": {
        "url": "https://data.elexon.co.uk/bmrs/api/v1/generation/actual/per-type",
        "days_per_request": 7,
        "json_data_key": "data",
        "is_wide_format": True,
        "index_column": "startTime",
        "columns_to_keep": ["startTime", "psrType", "quantity"],
        "column_rename_map": {"startTime": "timestamp", "psrType": "category", "quantity": "value"},
        "param_builder": lambda start, end: {
            "from": start.strftime("%Y-%m-%dT%H:%MZ"),
            "to": end.strftime("%Y-%m-%dT%H:%MZ"),
        }
    },
    "demand": {
        "url": "https://data.elexon.co.uk/bmrs/api/v1/demand/actual/total",
        "days_per_request": 7,
        "json_data_key": "data",
        "index_column": "startTime",
        "columns_to_keep": ["startTime", "quantity"],
        "column_rename_map": {"startTime": "timestamp", "quantity": "value"},
        "category_label": "demand",
        "param_builder": lambda start, end: {
            "from": start.strftime("%Y-%m-%dT%H:%MZ"),
            "to": end.strftime("%Y-%m-%dT%H:%MZ"),
        }
    }
}

def fetch_historical_batches(config):
    start = START_DATE
    all_data_frames = []

    url = config["url"]
    days_step = config["days_per_request"]
    data_key = config["json_data_key"]
    columns_to_keep = config["columns_to_keep"]
    
    # move window through dates per API call
    while start < END_DATE:
        end = start + timedelta(days=days_step)
        if end > END_DATE:
            end = END_DATE

        print(f"Fetching data from {start} to {end}")

        params = config["param_builder"](start, end)
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status() 
            data = response.json()

            if config.get("is_wide_format"):
                df = pd.json_normalize(
                    data.get(config["json_data_key"], []),
                    record_path=["data"], 
                    meta=[config["index_column"]]
                )
            else:
                raw_rows = data.get(data_key, [])
                df = pd.DataFrame(raw_rows)

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
    mid_data = df[(df["timestamp"] >= DOWNSAMPLE_YEAR_CUTOFF) & (df["timestamp"] < DOWNSAMPLE_MONTH_CUTOFF)].copy()
    modern_data = df[df["timestamp"] >= DOWNSAMPLE_MONTH_CUTOFF].copy()

    processed_blocks = []

    if not deep_data.empty:
        deep_data["timestamp"] = deep_data["timestamp"].dt.floor("8h")
        deep_data = deep_data.groupby(["timestamp", "category"])["value"].mean().reset_index()
        processed_blocks.append(deep_data)

    if not mid_data.empty:
        mid_data["timestamp"] = mid_data["timestamp"].dt.floor("4h")
        mid_data = mid_data.groupby(["timestamp", "category"])["value"].mean().reset_index()
        processed_blocks.append(mid_data)

    if not modern_data.empty:
        processed_blocks.append(modern_data)

    df = pd.concat(processed_blocks, ignore_index=True)

    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
    df = df[["timestamp", "category", "value"]]

    return df 

def push_to_d1(df,config):
    if df.empty:
        return

    db_name = "energy_db"
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
                "npx", "wrangler", "d1", "execute", db_name, "--remote", f"--file={temp_file}"
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

            progress = min(i + chunk_size, total_rows)
            print(f"Upload progress: {progress}/{total_rows} rows synced...")
        except subprocess.CalledProcessError as e:
            print(f"Upload error: {e.stderr.decode()}")
            break

def main():
    print("Fetching historical data...")

    for api_name, config in API_CONFIGS.items():
        print(f"Fetching {api_name} data...")
        raw_df = fetch_historical_batches(config)
        df = process_data(raw_df, config)
        push_to_d1(df,config)
        print("Pushed history to D1.")

if __name__ == "__main__":
    main()