CREATE TABLE IF NOT EXISTS as7341_spectrum_readings (
    experiment               TEXT NOT NULL,
    pioreactor_unit          TEXT NOT NULL,
    timestamp                TEXT NOT NULL,
    reading                  REAL,
    band                     INT,
)