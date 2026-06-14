-- Create a temporary staging table to hold the newly compressed 2-hour blocks
CREATE TEMP TABLE consolidated_rows AS
SELECT 
  strftime('%Y-%m-%d ', timestamp) || 
    printf('%02d:00:00', (cast(strftime('%H', timestamp) as INT) / 2) * 2) as timestamp,
  category,
  AVG(value) as value
FROM energy_metrics
WHERE timestamp < datetime('now', '-30 days');

-- Delete the original raw records that have aged past 1 year
DELETE FROM energy_metrics 
WHERE timestamp < datetime('now', '-30 days');

-- Pour the compressed 2-hour records back into the main table
INSERT OR IGNORE INTO energy_metrics (timestamp, category, value)
SELECT timestamp, category, value FROM consolidated_rows;

-- Clean up the local staging memory and optimize disk footprint space
DROP TABLE consolidated_rows;
VACUUM;