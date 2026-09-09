USE solarpulse;

DROP TABLE IF EXISTS performance_results;

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

    INDEX idx_performance_site_time (SiteKey, Timestamp),
    INDEX idx_performance_status (PerformanceStatus),
    INDEX idx_performance_operational_status (OperationalStatus)
);

SELECT COUNT(*) AS total_records
FROM performance_results;

SELECT
    PerformanceStatus,
    COUNT(*) AS records
FROM performance_results
GROUP BY PerformanceStatus
ORDER BY records DESC;

SELECT
    OperationalStatus,
    COUNT(*) AS records
FROM performance_results
GROUP BY OperationalStatus
ORDER BY records DESC;

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

SELECT *
FROM vw_site_performance
ORDER BY AveragePerformanceRatio;