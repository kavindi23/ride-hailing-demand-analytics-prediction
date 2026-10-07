
-- Q1. What is the highest-demand pickup zone in each borough?


WITH zone_totals AS (

    SELECT
        borough,
        pickup_location_id,
        zone,
        SUM(demand) AS total_demand

    FROM demand_hourly

    GROUP BY
        borough,
        pickup_location_id,
        zone
),

ranked_zones AS (

    SELECT
        borough,
        pickup_location_id,
        zone,
        total_demand,

        ROW_NUMBER() OVER (
            PARTITION BY borough
            ORDER BY total_demand DESC
        ) AS demand_rank

    FROM zone_totals
)

SELECT
    borough,
    pickup_location_id,
    zone,
    total_demand

FROM ranked_zones

WHERE demand_rank = 1

ORDER BY total_demand DESC;



-- Q2. What is the peak demand hour within each borough?


WITH borough_hourly AS (

    SELECT
        borough,
        hour,
        SUM(demand) AS total_demand

    FROM demand_hourly

    WHERE borough <> 'EWR'

    GROUP BY
        borough,
        hour
),

ranked_hours AS (

    SELECT
        borough,
        hour,
        total_demand,

        ROW_NUMBER() OVER (
            PARTITION BY borough
            ORDER BY total_demand DESC
        ) AS demand_rank

    FROM borough_hourly
)

SELECT
    borough,
    hour AS peak_hour,
    total_demand

FROM ranked_hours

WHERE demand_rank = 1

ORDER BY total_demand DESC;



-- Q3. What is the peak demand hour for each day of the week?


WITH day_hour_demand AS (

    SELECT
        day_of_week,
        day_of_week_num,
        hour,
        SUM(demand) AS total_demand

    FROM demand_hourly

    GROUP BY
        day_of_week,
        day_of_week_num,
        hour
),

ranked_hours AS (

    SELECT
        day_of_week,
        day_of_week_num,
        hour,
        total_demand,

        ROW_NUMBER() OVER (
            PARTITION BY day_of_week_num
            ORDER BY total_demand DESC
        ) AS demand_rank

    FROM day_hour_demand
)

SELECT
    day_of_week,
    hour AS peak_hour,
    total_demand

FROM ranked_hours

WHERE demand_rank = 1

ORDER BY day_of_week_num;