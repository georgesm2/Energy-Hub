INSERT INTO energy_metrics (timestamp, category, value) VALUES 
('2026-07-04 12:00','SOLAR',9935.53),
('2026-07-04 12:30','SOLAR',10487.4),
('2026-07-04 13:00','SOLAR',10565.0),
('2026-07-04 13:30','SOLAR',10287.8),
('2026-07-04 14:00','SOLAR',10106.9),
('2026-07-04 14:30','SOLAR',9281.24)ON CONFLICT(timestamp, category) DO UPDATE SET value = EXCLUDED.value WHERE energy_metrics.value IS NOT EXCLUDED.value;