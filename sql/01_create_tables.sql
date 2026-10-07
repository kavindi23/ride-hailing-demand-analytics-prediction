CREATE TABLE IF NOT EXISTS demand_hourly (
    datetime TIMESTAMP NOT NULL,
    date DATE NOT NULL,
    hour SMALLINT NOT NULL,
    day_of_week VARCHAR(10) NOT NULL,
    day_of_week_num SMALLINT NOT NULL,
    day_of_month SMALLINT NOT NULL,
    month SMALLINT NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    pickup_location_id INTEGER NOT NULL,
    borough VARCHAR(50),
    zone VARCHAR(100),
    service_zone VARCHAR(50),
    demand INTEGER NOT NULL,

    PRIMARY KEY (datetime, pickup_location_id)
);