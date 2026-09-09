USE solarpulse;

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

SELECT
    MIN(Timestamp) AS first_timestamp,
    MAX(Timestamp) AS last_timestamp
FROM generation_raw;

SELECT
    COUNT(DISTINCT SiteKey) AS number_of_sites
FROM generation_raw;

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

SELECT
    SiteKey,
    Timestamp,
    COUNT(*) AS duplicate_count
FROM generation_raw
GROUP BY SiteKey, Timestamp
HAVING COUNT(*) > 1
LIMIT 20;

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

SELECT
    MIN(Timestamp) AS first_timestamp,
    MAX(Timestamp) AS last_timestamp
FROM weather_raw;

SELECT *
FROM solar_sites
ORDER BY SiteKey;

SELECT
    COUNT(*) AS total_sites,
    SUM(kWp IS NULL) AS missing_capacity,
    SUM(Number_of_Panels IS NULL) AS missing_panel_count,
    SUM(Inverter IS NULL) AS missing_inverter,
    SUM(Latitude IS NULL) AS missing_latitude,
    SUM(Longitude IS NULL) AS missing_longitude
FROM solar_sites;

SELECT
    COUNT(*) AS total_rows,
    SUM(DataStatus = 1) AS valid_months,
    SUM(DataStatus = 0) AS invalid_months
FROM monthly_summary;

SELECT
    SiteKey,
    COUNT(*) AS months,
    SUM(DataStatus = 0) AS invalid_months
FROM monthly_summary
GROUP BY SiteKey
ORDER BY invalid_months DESC;