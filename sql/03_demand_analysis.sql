
-- Q1. Which dates recorded the highest ride demand?


SELECT
    date,
    SUM(demand) AS total_demand
FROM demand_hourly
GROUP BY date
ORDER BY total_demand DESC
LIMIT 10;



-- Q2. Which dates recorded the lowest ride demand?


SELECT
    date,
    SUM(demand) AS total_demand
FROM demand_hourly
GROUP BY date
ORDER BY total_demand ASC
LIMIT 10;



-- Q3. Which hours have the highest ride demand?


SELECT
    hour,
    SUM(demand) AS total_demand,
    ROUND(AVG(demand), 2) AS avg_zone_hour_demand
FROM demand_hourly
GROUP BY hour
ORDER BY total_demand DESC;



-- Q4. How does demand differ between weekdays and weekends?


SELECT
    CASE
        WHEN is_weekend THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,

    SUM(demand) AS total_demand,
    ROUND(AVG(demand), 2) AS avg_zone_hour_demand

FROM demand_hourly
GROUP BY is_weekend
ORDER BY total_demand DESC;



-- Q5. Which boroughs generate the highest ride demand?


SELECT
    borough,
    SUM(demand) AS total_demand,

    ROUND(
        SUM(demand) * 100.0 /
        SUM(SUM(demand)) OVER (),
        2
    ) AS demand_percentage

FROM demand_hourly
GROUP BY borough
ORDER BY total_demand DESC;



-- Q6. What are the top 10 pickup zones?


SELECT
    pickup_location_id,
    borough,
    zone,
    SUM(demand) AS total_demand,

    ROUND(
        SUM(demand) * 100.0 /
        SUM(SUM(demand)) OVER (),
        2
    ) AS demand_percentage

FROM demand_hourly

GROUP BY
    pickup_location_id,
    borough,
    zone

ORDER BY total_demand DESC
LIMIT 10;



-- Q7. Which high-demand zones show the greatest variability?


SELECT
    pickup_location_id,
    borough,
    zone,

    ROUND(AVG(demand), 2) AS avg_hourly_demand,

    ROUND(
        STDDEV_SAMP(demand),
        2
    ) AS demand_std,

    ROUND(
        STDDEV_SAMP(demand) /
        NULLIF(AVG(demand), 0),
        3
    ) AS coefficient_of_variation

FROM demand_hourly

GROUP BY
    pickup_location_id,
    borough,
    zone

HAVING AVG(demand) >= 100

ORDER BY coefficient_of_variation DESC
LIMIT 10;