/* ============================================================
   SOLARPULSE - SOLAR ENERGY UNDERPERFORMANCE DETECTION SYSTEM
   File: 02_sql_data_audit.sql

   Purpose:
   - Validate the data after importing the UNISOLAR CSV files
   - Check table row counts and data completeness
   - Identify missing, zero and negative generation values
   - Check generation and weather data ranges
   - Verify timestamp coverage
   - Check site-level data quality
   - Check relationships between generation and site metadata
   - Validate monthly summary data

   Data Source:
   - UNISOLAR Dataset

   Author: Aditya Ujjwal
   ============================================================ */


-- ============================================================
-- 1. SELECT DATABASE
-- ============================================================

-- Select the SolarPulse database before running the audit queries.

USE solarpulse;


-- ============================================================
-- 2. ROW COUNT AUDIT
-- ============================================================

-- Compare the number of records stored in each table.
-- This helps confirm that the CSV data was imported correctly
-- and provides a basic validation of the database loading process.

SELECT 'solar_sites' AS table_name, COUNT(*) AS row_count
FROM solar_sites
UNION ALL
SELECT 'generation_raw', COUNT(*)
FROM generation_raw
UNION ALL
SELECT 'weather_raw', COUNT(*)
FROM weather_raw
UNION ALL
SELECT 'monthly_summary', COUNT(*)
FROM monthly_summary;


-- ============================================================
-- 3. SOLAR GENERATION QUALITY CHECK
-- ============================================================

-- Check the overall quality of the generation data.
-- The query identifies:
--   - Total number of records
--   - Valid/non-null generation values
--   - Missing generation values
--   - Zero generation values
--   - Negative generation values
--   - Minimum generation
--   - Maximum generation
--   - Average generation
--
-- This is important because missing generation should not be
-- automatically interpreted as zero generation.

SELECT
    COUNT(*) AS total_rows,
    COUNT(SolarGeneration) AS valid_generation,
    SUM(SolarGeneration IS NULL) AS missing_generation,
    SUM(SolarGeneration = 0) AS zero_generation,
    SUM(SolarGeneration < 0) AS negative_generation,
    MIN(SolarGeneration) AS minimum_generation,
    MAX(SolarGeneration) AS maximum_generation,
    AVG(SolarGeneration) AS average_generation
FROM generation_raw;


-- ============================================================
-- 4. GENERATION TIMESTAMP COVERAGE
-- ============================================================

-- Identify the earliest and latest generation timestamps.
-- This establishes the overall time period covered by the
-- generation dataset.

SELECT
    MIN(Timestamp) AS first_timestamp,
    MAX(Timestamp) AS last_timestamp
FROM generation_raw;


-- ============================================================
-- 5. NUMBER OF UNIQUE SOLAR SITES
-- ============================================================

-- Determine how many unique solar sites are represented in
-- the generation data.

SELECT
    COUNT(DISTINCT SiteKey) AS number_of_sites
FROM generation_raw;


-- ============================================================
-- 6. MISSING GENERATION BY SITE
-- ============================================================

-- Measure generation missingness separately for every site.
-- This helps identify sites with unusually high levels of
-- missing generation data.

SELECT
    SiteKey,
    COUNT(*) AS total_records,
    SUM(SolarGeneration IS NULL) AS missing_records,
    ROUND(
        100 * SUM(SolarGeneration IS NULL) / COUNT(*),
        2
    ) AS missing_percentage
FROM generation_raw
GROUP BY SiteKey
ORDER BY missing_percentage DESC;


-- ============================================================
-- 7. GENERATION STATISTICS BY SITE
-- ============================================================

-- Calculate basic generation statistics for each site.
-- NULL generation values are excluded from these calculations.

-- This allows us to compare the observed generation behavior
-- across different solar installations.

SELECT
    SiteKey,
    COUNT(*) AS records,
    MIN(SolarGeneration) AS min_generation,
    MAX(SolarGeneration) AS max_generation,
    AVG(SolarGeneration) AS avg_generation
FROM generation_raw
WHERE SolarGeneration IS NOT NULL
GROUP BY SiteKey
ORDER BY SiteKey;


-- ============================================================
-- 8. DUPLICATE GENERATION RECORD CHECK
-- ============================================================

-- Check whether the same SiteKey and Timestamp combination
-- occurs more than once.

-- Duplicate records could cause double-counting and may affect
-- downstream analysis and machine-learning results.

SELECT
    SiteKey,
    Timestamp,
    COUNT(*) AS duplicate_count
FROM generation_raw
GROUP BY SiteKey, Timestamp
HAVING COUNT(*) > 1
LIMIT 20;


-- ============================================================
-- 9. REFERENTIAL INTEGRITY CHECK
-- ============================================================

-- Check whether every SiteKey appearing in the generation data
-- also exists in the solar_sites metadata table.

-- This helps identify generation records that cannot be linked
-- to a known solar installation.

SELECT
    g.CampusKey,
    g.SiteKey,
    COUNT(*) AS records
FROM generation_raw g
LEFT JOIN solar_sites s
    ON g.SiteKey = s.SiteKey
WHERE s.SiteKey IS NULL
GROUP BY
    g.CampusKey,
    g.SiteKey;


-- ============================================================
-- 10. WEATHER MISSING-VALUE AUDIT
-- ============================================================

-- Count missing values for each weather variable.
-- This provides an overview of the completeness of the weather
-- dataset before Python-based preprocessing.

SELECT
    COUNT(*) AS total_rows,

    SUM(ApparentTemperature IS NULL)
        AS missing_apparent_temperature,

    SUM(AirTemperature IS NULL)
        AS missing_air_temperature,

    SUM(DewPointTemperature IS NULL)
        AS missing_dew_point,

    SUM(RelativeHumidity IS NULL)
        AS missing_humidity,

    SUM(WindSpeed IS NULL)
        AS missing_wind_speed,

    SUM(WindDirection IS NULL)
        AS missing_wind_direction

FROM weather_raw;


-- ============================================================
-- 11. WEATHER RANGE CHECK
-- ============================================================

-- Check the minimum and maximum values of each weather variable.
-- This helps identify unusual or potentially invalid physical
-- values before the data is used for modelling.

SELECT
    MIN(AirTemperature) AS min_air_temp,
    MAX(AirTemperature) AS max_air_temp,

    MIN(ApparentTemperature) AS min_apparent_temp,
    MAX(ApparentTemperature) AS max_apparent_temp,

    MIN(DewPointTemperature) AS min_dew_point,
    MAX(DewPointTemperature) AS max_dew_point,

    MIN(RelativeHumidity) AS min_humidity,
    MAX(RelativeHumidity) AS max_humidity,

    MIN(WindSpeed) AS min_wind_speed,
    MAX(WindSpeed) AS max_wind_speed,

    MIN(WindDirection) AS min_wind_direction,
    MAX(WindDirection) AS max_wind_direction

FROM weather_raw;


-- ============================================================
-- 12. WEATHER TIMESTAMP COVERAGE
-- ============================================================

-- Identify the earliest and latest weather timestamps.
-- Comparing this with the generation timestamp range helps
-- identify periods where weather observations may not be available.

SELECT
    MIN(Timestamp) AS first_timestamp,
    MAX(Timestamp) AS last_timestamp
FROM weather_raw;


-- ============================================================
-- 13. SOLAR SITE METADATA REVIEW
-- ============================================================

-- Display all solar site metadata records.
-- This provides a direct view of the site information imported
-- from the UNISOLAR site-details dataset.

SELECT *
FROM solar_sites
ORDER BY SiteKey;


-- ============================================================
-- 14. MISSING SITE METADATA CHECK
-- ============================================================

-- Check for missing site-level information such as:
--   - Installed capacity
--   - Number of panels
--   - Inverter information
--   - Latitude
--   - Longitude
--
-- These fields are important for understanding the completeness
-- of the solar site metadata.

SELECT
    COUNT(*) AS total_sites,
    SUM(kWp IS NULL) AS missing_capacity,
    SUM(Number_of_Panels IS NULL) AS missing_panel_count,
    SUM(Inverter IS NULL) AS missing_inverter,
    SUM(Latitude IS NULL) AS missing_latitude,
    SUM(Longitude IS NULL) AS missing_longitude
FROM solar_sites;


-- ============================================================
-- 15. MONTHLY SUMMARY VALIDITY CHECK
-- ============================================================

-- Check the overall validity of records in the monthly summary
-- table using the DataStatus field.

SELECT
    COUNT(*) AS total_rows,
    SUM(DataStatus = 1) AS valid_months,
    SUM(DataStatus = 0) AS invalid_months
FROM monthly_summary;


-- ============================================================
-- 16. MONTHLY SUMMARY VALIDITY BY SITE
-- ============================================================

-- Examine invalid monthly records for each solar site.
-- Sites are ordered by the number of invalid months so that
-- potential data-quality issues can be identified quickly.

SELECT
    SiteKey,
    COUNT(*) AS months,
    SUM(DataStatus = 0) AS invalid_months
FROM monthly_summary
GROUP BY SiteKey
ORDER BY invalid_months DESC;


-- ============================================================
-- END OF SQL DATA AUDIT
-- ============================================================

-- The results of these checks are used to understand the
-- quality and structure of the imported data before performing
-- Python/Pandas cleaning, feature engineering and ML modelling.