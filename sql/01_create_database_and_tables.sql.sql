/* ============================================================
   SOLARPULSE - SOLAR ENERGY UNDERPERFORMANCE DETECTION SYSTEM
   File: 01_create_database_and_tables.sql

   Purpose:
   - Create the SolarPulse database
   - Create the raw data tables required for the project
   - Define the database structure before importing the CSV data

   Data Source:
   - UNISOLAR Dataset

   Author: Aditya Ujjwal
   ============================================================ */


-- ============================================================
-- 1. CREATE DATABASE
-- ============================================================

-- Create the SolarPulse database if it does not already exist.
-- This database will contain all raw, analytical and ML-related
-- data used throughout the project.

CREATE DATABASE IF NOT EXISTS solarpulse;

-- Select the SolarPulse database for the following operations.
USE solarpulse;


-- ============================================================
-- 2. CREATE SOLAR SITE DETAILS TABLE
-- ============================================================

-- This table stores static information about each solar site,
-- such as its campus, installed capacity, panel and inverter
-- information, and geographical coordinates.

-- SiteKey uniquely identifies each solar installation.

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


-- ============================================================
-- 3. CREATE MONTHLY SUMMARY TABLE
-- ============================================================

-- This table stores the monthly/yearly summary information
-- provided by the UNISOLAR dataset.

-- It contains summary statistics such as average, maximum
-- and minimum solar generation for each site.

CREATE TABLE monthly_summary (
    SiteKey INT,
    Year INT,
    Month INT,
    DataStatus BOOLEAN,
    AverageSolarGeneration DECIMAL(12,4),
    MaxSolarGeneration DECIMAL(12,4),
    MinSolarGeneration DECIMAL(12,4)
);


-- ============================================================
-- 4. CREATE WEATHER RAW TABLE
-- ============================================================

-- This table stores the raw weather observations associated
-- with each campus at 15-minute intervals.

-- Weather information is later used as an input to the ML
-- model for predicting expected solar energy generation.

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


-- ============================================================
-- 5. CREATE SOLAR GENERATION RAW TABLE
-- ============================================================

-- This table stores the raw solar energy generation
-- observations for each solar site.

-- SolarGeneration represents energy generated during the
-- 15-minute observation interval and is measured in kWh.

CREATE TABLE generation_raw (
    CampusKey INT,
    SiteKey INT,
    Timestamp DATETIME,
    SolarGeneration DECIMAL(12,4),

    INDEX idx_generation_site_time (SiteKey, Timestamp),
    INDEX idx_generation_timestamp (Timestamp)
);


-- ============================================================
-- 6. DATABASE SETUP COMPLETE
-- ============================================================

-- At this stage, the database structure has been created.
-- The next step is to import the CSV data into these raw tables.