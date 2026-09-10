/* ============================================================
   SOLARPULSE - SOLAR ENERGY UNDERPERFORMANCE DETECTION SYSTEM
   File: 03_performance_table_and_views.sql

   Purpose:
   - Create the final performance results table
   - Store ML predictions and underperformance results
   - Verify that performance results were loaded correctly
   - Create analytical SQL views for Power BI
   - Create site-level performance summaries

   Data Flow:
   Raw Data → Python / ML → Performance Results → SQL Views
                                      ↓
                                   Power BI

   Author: Aditya Ujjwal
   ============================================================ */


-- ============================================================
-- 1. SELECT DATABASE
-- ============================================================

-- Select the SolarPulse database before creating and querying
-- the performance table and analytical views.

USE solarpulse;


-- ============================================================
-- 2. REMOVE EXISTING PERFORMANCE TABLE
-- ============================================================

-- Remove the existing performance table if it already exists.
-- This allows the table to be recreated with the required
-- structure when the performance-generation process is rerun.

DROP TABLE IF EXISTS performance_results;


-- ============================================================
-- 3. CREATE PERFORMANCE RESULTS TABLE
-- ============================================================

-- This table stores the final results produced by the ML and
-- underperformance-detection pipeline.
--
-- It combines:
--   - Actual solar generation
--   - ML-predicted expected generation
--   - Prediction residual
--   - Performance deviation
--   - Performance ratio
--   - Normal / Warning / Critical classification
--   - Underperformance persistence information
--   - Operational status
--   - Estimated energy loss

CREATE TABLE performance_results (
    PerformanceID BIGINT AUTO_INCREMENT PRIMARY KEY,

    CampusKey INT NOT NULL,
    SiteKey INT NOT NULL,
    Timestamp DATETIME NOT NULL,

    ActualGeneration DECIMAL(12,4),
    ExpectedGeneration DECIMAL(12,4),

    Residual DECIMAL(12,4),
    PerformanceDeviation DECIMAL(12,4),
    PerformanceRatio DECIMAL(12,6),

    PerformanceStatus VARCHAR(30),
    UnderperformanceStreak INT,
    PersistentUnderperformance TINYINT(1),

    OperationalStatus VARCHAR(40),

    EnergyLoss DECIMAL(12,4),

    -- Index used to make site/time-based queries faster.
    INDEX idx_performance_site_time (SiteKey, Timestamp),

    -- Index used for filtering/grouping by performance status.
    INDEX idx_performance_status (PerformanceStatus),

    -- Index used for filtering/grouping by operational status.
    INDEX idx_performance_operational_status (OperationalStatus)
);


-- ============================================================
-- 4. VERIFY PERFORMANCE TABLE LOADING
-- ============================================================

-- Check the total number of records stored in the
-- performance_results table.
--
-- This is a basic validation step to confirm that the ML
-- performance results were loaded into MySQL.

SELECT COUNT(*) AS total_records
FROM performance_results;


-- ============================================================
-- 5. CHECK PERFORMANCE STATUS DISTRIBUTION
-- ============================================================

-- Count the number of records assigned to each
-- performance-status category.
--
-- PerformanceStatus is derived from the actual-versus-expected
-- generation comparison and may contain:
--   - Normal
--   - Warning
--   - Critical
--
-- This check helps validate that the classification logic
-- produced results successfully.

SELECT
    PerformanceStatus,
    COUNT(*) AS records
FROM performance_results
GROUP BY PerformanceStatus
ORDER BY records DESC;


-- ============================================================
-- 6. CHECK OPERATIONAL STATUS DISTRIBUTION
-- ============================================================

-- Count records belonging to each operational-status category.
--
-- OperationalStatus provides an additional operational view
-- of the detected performance condition.

SELECT
    OperationalStatus,
    COUNT(*) AS records
FROM performance_results
GROUP BY OperationalStatus
ORDER BY records DESC;


-- ============================================================
-- 7. CREATE DETAILED SOLAR PERFORMANCE VIEW
-- ============================================================

-- Create a detailed analytical view combining the performance
-- results with the corresponding solar-site metadata.
--
-- This view is designed to make downstream analysis easier by
-- bringing ML results and site information into one dataset.
--
-- The LEFT JOIN ensures performance records are retained even
-- if some site metadata fields are unavailable.

CREATE OR REPLACE VIEW vw_solar_performance AS
SELECT
    p.PerformanceID,
    p.CampusKey,
    p.SiteKey,
    p.Timestamp,

    p.ActualGeneration,
    p.ExpectedGeneration,

    p.Residual,
    p.PerformanceDeviation,
    p.PerformanceRatio,

    p.PerformanceStatus,
    p.UnderperformanceStreak,
    p.PersistentUnderperformance,
    p.OperationalStatus,

    p.EnergyLoss,

    s.kWp,
    s.Number_of_Panels,
    s.Panel,
    s.Inverter,
    s.Optimizers,
    s.Latitude,
    s.Longitude

FROM performance_results p
LEFT JOIN solar_sites s
    ON p.SiteKey = s.SiteKey;


-- ============================================================
-- 8. CREATE SITE-LEVEL PERFORMANCE VIEW
-- ============================================================

-- Create an aggregated view containing one summary record
-- for each solar site.
--
-- This view is particularly useful for Power BI because it
-- provides site-level KPIs without requiring Power BI to
-- perform all aggregations itself.
--
-- The view calculates:
--   - Number of observations
--   - Total actual generation
--   - Total expected generation
--   - Total potential energy loss
--   - Average performance deviation
--   - Average performance ratio
--   - Number of Warning events
--   - Number of Critical events
--   - Number of Persistent Underperformance events

CREATE OR REPLACE VIEW vw_site_performance AS
SELECT
    p.SiteKey,
    MAX(p.CampusKey) AS CampusKey,

    COUNT(*) AS Observations,

    SUM(p.ActualGeneration) AS ActualGeneration,
    SUM(p.ExpectedGeneration) AS ExpectedGeneration,

    SUM(p.EnergyLoss) AS EnergyLoss,

    AVG(p.PerformanceDeviation) AS AverageDeviation,
    AVG(p.PerformanceRatio) AS AveragePerformanceRatio,

    SUM(
        CASE
            WHEN p.PerformanceStatus = 'Warning'
            THEN 1
            ELSE 0
        END
    ) AS WarningEvents,

    SUM(
        CASE
            WHEN p.PerformanceStatus = 'Critical'
            THEN 1
            ELSE 0
        END
    ) AS CriticalEvents,

    SUM(
        CASE
            WHEN p.PersistentUnderperformance = 1
            THEN 1
            ELSE 0
        END
    ) AS PersistentEvents

FROM performance_results p
GROUP BY p.SiteKey;


-- ============================================================
-- 9. VERIFY SITE-LEVEL PERFORMANCE VIEW
-- ============================================================

-- Display the site-level performance summary.
-- Sites are ordered by AveragePerformanceRatio so that sites
-- with lower average performance appear first.

SELECT *
FROM vw_site_performance
ORDER BY AveragePerformanceRatio;


-- ============================================================
-- 10. CHECK PERSISTENT UNDERPERFORMANCE
-- ============================================================

-- Count how many performance records were classified as
-- persistent underperformance versus non-persistent.
--
-- PersistentUnderperformance = 1 indicates that the defined
-- consecutive-critical condition was met.

SELECT
    PersistentUnderperformance,
    COUNT(*) AS records
FROM performance_results
GROUP BY PersistentUnderperformance;


-- ============================================================
-- 11. FINAL OPERATIONAL STATUS CHECK
-- ============================================================

-- Provide a final distribution check of operational statuses.
-- This helps confirm that the operational classification was
-- successfully stored in the performance_results table.

SELECT
    OperationalStatus,
    COUNT(*) AS records
FROM performance_results
GROUP BY OperationalStatus;


-- ============================================================
-- END OF PERFORMANCE TABLE AND VIEW CREATION
-- ============================================================

-- At this stage:
--   1. Performance results are stored in MySQL.
--   2. The loaded results have been validated.
--   3. Detailed performance data is available through
--      vw_solar_performance.
--   4. Site-level aggregated performance is available through
--      vw_site_performance.
--
-- These views can now be connected to Power BI for dashboard
-- analysis and visualization.