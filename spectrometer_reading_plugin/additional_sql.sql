CREATE TABLE IF NOT EXISTS as7341_spectrum_readings (
    experiment               TEXT NOT NULL,
    pioreactor_unit          TEXT NOT NULL,
    timestamp                TEXT NOT NULL,
    reading                  REAL,
    band                     INT
);


CREATE VIEW IF NOT EXISTS as7341_spectrum_readings_415 AS
  SELECT * FROM as7341_spectrum_readings WHERE band=415;

CREATE VIEW IF NOT EXISTS as7341_spectrum_readings_445 AS
  SELECT * FROM as7341_spectrum_readings WHERE band=445;

CREATE VIEW IF NOT EXISTS as7341_spectrum_readings_480 AS
  SELECT * FROM as7341_spectrum_readings WHERE band=480;

CREATE VIEW IF NOT EXISTS as7341_spectrum_readings_515 AS
  SELECT * FROM as7341_spectrum_readings WHERE band=515;

CREATE VIEW IF NOT EXISTS as7341_spectrum_readings_555 AS
  SELECT * FROM as7341_spectrum_readings WHERE band=555;

CREATE VIEW IF NOT EXISTS as7341_spectrum_readings_590 AS
  SELECT * FROM as7341_spectrum_readings WHERE band=590;

CREATE VIEW IF NOT EXISTS as7341_spectrum_readings_630 AS
  SELECT * FROM as7341_spectrum_readings WHERE band=630;

CREATE VIEW IF NOT EXISTS as7341_spectrum_readings_680 AS
  SELECT * FROM as7341_spectrum_readings WHERE band=680;
