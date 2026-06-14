CREATE TABLE if NOT EXISTS energy_metrics (
    timestamp TEXT NOT NULL,
    category TEXT NOT NULL,
    value REAL NOT NULL,
    PRIMARY KEY (timestamp, category)
);