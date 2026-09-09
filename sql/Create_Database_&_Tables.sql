create database solarpulse;

use solarpulse;

CREATE TABLE solar_sites (
    CampusKey INT NOT NULL,
    SiteKey INT NOT NULL,
    kWp DECIMAL(10,2),
    Number_of_Panels INT,
    Panel VARCHAR(255),
    Inverter VARCHAR(255),
    Optimizers VARCHAR(255),
    Metric VARCHAR(100),
    Latitude DECIMAL(10,6),
    Longitude DECIMAL(10,6),

    PRIMARY KEY (SiteKey)
);

CREATE TABLE generation_raw (
    CampusKey INT,
    SiteKey INT,
    Timestamp DATETIME,
    SolarGeneration DECIMAL(12,4),

    INDEX idx_generation_site_time (SiteKey, Timestamp),
    INDEX idx_generation_timestamp (Timestamp)
);

CREATE TABLE weather_raw (
    CampusKey INT,
    Timestamp DATETIME,
    ApparentTemperature DECIMAL(8,3),
    AirTemperature DECIMAL(8,3),
    DewPointTemperature DECIMAL(8,3),
    RelativeHumidity DECIMAL(8,3),
    WindSpeed DECIMAL(8,3),
    WindDirection DECIMAL(8,3),

    INDEX idx_weather_timestamp (Timestamp),
    INDEX idx_weather_campus_time (CampusKey, Timestamp)
);

CREATE TABLE monthly_summary (
    SiteKey INT,
    Year INT,
    Month INT,
    DataStatus BOOLEAN,
    AverageSolarGeneration DECIMAL(12,4),
    MaxSolarGeneration DECIMAL(12,4),
    MinSolarGeneration DECIMAL(12,4)
);
