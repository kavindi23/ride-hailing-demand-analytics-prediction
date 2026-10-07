-- 1. Total number of rows
SELECT COUNT(*) AS total_rows
FROM demand_hourly;


-- 2. Dataset date range
SELECT
    MIN(datetime) AS start_datetime,
    MAX(datetime) AS end_datetime
FROM demand_hourly;


-- 3. Number of pickup zones
SELECT
    COUNT(DISTINCT pickup_location_id) AS unique_zones
FROM demand_hourly;


-- 4. Total demand represented in the dataset
SELECT
    SUM(demand) AS total_demand
FROM demand_hourly;


-- 5. Zero-demand observations
SELECT
    COUNT(*) AS zero_demand_rows,
    ROUND(
        100.0 * COUNT(*) /
        (SELECT COUNT(*) FROM demand_hourly),
        2
    ) AS zero_demand_percentage
FROM demand_hourly
WHERE demand = 0;


-- 6. Check for duplicate zone-hour records
SELECT
    datetime,
    pickup_location_id,
    COUNT(*) AS record_count
FROM demand_hourly
GROUP BY
    datetime,
    pickup_location_id
HAVING COUNT(*) > 1;