from pathlib import Path

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "final_hgb_demand_model.joblib"
)

FEATURES_PATH = (
    BASE_DIR
    / "models"
    / "model_features.joblib"
)

DEMAND_DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "hourly_zone_demand_2025_01.parquet"
)


# ============================================================
# 2. LOAD TRAINED MODEL AND FEATURE LIST
# ============================================================

model = joblib.load(MODEL_PATH)
features = joblib.load(FEATURES_PATH)

print("Model loaded successfully.")
print(f"Model features: {len(features)}")


# ============================================================
# 3. LOAD HISTORICAL DEMAND DATA
# ============================================================

demand_history = pd.read_parquet(
    DEMAND_DATA_PATH,
    columns=[
        "datetime",
        "PULocationID",
        "Borough",
        "Zone",
        "demand"
    ]
)

demand_history["datetime"] = pd.to_datetime(
    demand_history["datetime"]
)

demand_history = (
    demand_history
    .sort_values(
        ["PULocationID", "datetime"]
    )
    .reset_index(drop=True)
)

print(
    f"Historical demand loaded: "
    f"{len(demand_history):,} rows"
)


# ============================================================
# 4. CREATE ZONE LOOKUP TABLE
# ============================================================

zone_info = (
    demand_history[
        [
            "PULocationID",
            "Borough",
            "Zone"
        ]
    ]
    .drop_duplicates("PULocationID")
    .set_index("PULocationID")
)

valid_zone_ids = set(
    demand_history["PULocationID"].unique()
)


# ============================================================
# 5. HISTORICAL PATTERN DEMAND ESTIMATION
# ============================================================

def estimate_historical_demand(
    pickup_location_id: int,
    target_datetime: pd.Timestamp
):
    """
    Estimate demand when the exact historical timestamp
    is not available.

    Priority:
    1. Same pickup zone + same weekday + same hour
    2. Same pickup zone + same hour
    3. Overall average demand for the pickup zone
    """

    zone_data = demand_history[
        demand_history["PULocationID"]
        == pickup_location_id
    ].copy()

    if zone_data.empty:
        raise ValueError(
            "No historical demand data is available "
            "for this pickup zone."
        )

    # --------------------------------------------------------
    # SAME WEEKDAY + SAME HOUR
    # --------------------------------------------------------

    same_pattern = zone_data[
        (
            zone_data["datetime"].dt.dayofweek
            == target_datetime.dayofweek
        )
        &
        (
            zone_data["datetime"].dt.hour
            == target_datetime.hour
        )
    ]

    if not same_pattern.empty:
        return float(
            same_pattern["demand"].mean()
        )

    # --------------------------------------------------------
    # SAME HOUR
    # --------------------------------------------------------

    same_hour = zone_data[
        zone_data["datetime"].dt.hour
        == target_datetime.hour
    ]

    if not same_hour.empty:
        return float(
            same_hour["demand"].mean()
        )

    # --------------------------------------------------------
    # FINAL FALLBACK - ZONE AVERAGE
    # --------------------------------------------------------

    return float(
        zone_data["demand"].mean()
    )


# ============================================================
# 6. AUTOMATIC FEATURE GENERATION
# ============================================================

def build_prediction_features(
    pickup_location_id: int,
    prediction_datetime: pd.Timestamp
):
    """
    Build all features required by the trained ML model.

    If exact historical demand exists, actual demand is used.

    If exact historical demand is unavailable, demand is
    estimated automatically using historical patterns for
    the same pickup zone.
    """

    # --------------------------------------------------------
    # SELECT HISTORY FOR THE PICKUP ZONE
    # --------------------------------------------------------

    zone_history = demand_history[
        demand_history["PULocationID"]
        == pickup_location_id
    ].copy()

    zone_history = zone_history.sort_values(
        "datetime"
    )

    if zone_history.empty:
        raise ValueError(
            "No historical demand data is available "
            "for this pickup zone."
        )

    demand_lookup = (
        zone_history
        .set_index("datetime")["demand"]
    )


    # --------------------------------------------------------
    # GET ACTUAL OR ESTIMATED DEMAND
    # --------------------------------------------------------

    def get_demand(target_datetime):

        # Use exact historical demand when available
        if target_datetime in demand_lookup.index:

            value = demand_lookup.loc[
                target_datetime
            ]

            # Safety in case duplicate timestamps exist
            if isinstance(value, pd.Series):
                value = value.iloc[0]

            return float(value)

        # Otherwise estimate using historical patterns
        return estimate_historical_demand(
            pickup_location_id,
            target_datetime
        )


    # --------------------------------------------------------
    # REQUIRED LAG TIMESTAMPS
    # --------------------------------------------------------

    lag_1_time = (
        prediction_datetime
        - pd.Timedelta(hours=1)
    )

    lag_2_time = (
        prediction_datetime
        - pd.Timedelta(hours=2)
    )

    lag_24_time = (
        prediction_datetime
        - pd.Timedelta(hours=24)
    )

    lag_168_time = (
        prediction_datetime
        - pd.Timedelta(hours=168)
    )


    # --------------------------------------------------------
    # LAG FEATURES
    # --------------------------------------------------------

    lag_1 = get_demand(
        lag_1_time
    )

    lag_2 = get_demand(
        lag_2_time
    )

    lag_24 = get_demand(
        lag_24_time
    )

    lag_168 = get_demand(
        lag_168_time
    )


    # --------------------------------------------------------
    # ROLLING MEAN - PREVIOUS 3 HOURS
    # --------------------------------------------------------

    previous_3_hours = [
        prediction_datetime
        - pd.Timedelta(hours=i)
        for i in range(1, 4)
    ]

    previous_3_values = [
        get_demand(timestamp)
        for timestamp in previous_3_hours
    ]

    rolling_mean_3 = (
        sum(previous_3_values)
        / len(previous_3_values)
    )


    # --------------------------------------------------------
    # ROLLING MEAN - PREVIOUS 24 HOURS
    # --------------------------------------------------------

    previous_24_hours = [
        prediction_datetime
        - pd.Timedelta(hours=i)
        for i in range(1, 25)
    ]

    previous_24_values = [
        get_demand(timestamp)
        for timestamp in previous_24_hours
    ]

    rolling_mean_24 = (
        sum(previous_24_values)
        / len(previous_24_values)
    )


    # --------------------------------------------------------
    # CALENDAR FEATURES
    # --------------------------------------------------------

    day_of_week_num = (
        prediction_datetime.dayofweek
    )


    # --------------------------------------------------------
    # FINAL FEATURE DICTIONARY
    # --------------------------------------------------------

    feature_data = {
        "hour":
            prediction_datetime.hour,

        "day_of_week_num":
            day_of_week_num,

        "day_of_month":
            prediction_datetime.day,

        "is_weekend":
            int(day_of_week_num >= 5),

        "PULocationID":
            pickup_location_id,

        "lag_1":
            float(lag_1),

        "lag_2":
            float(lag_2),

        "lag_24":
            float(lag_24),

        "lag_168":
            float(lag_168),

        "rolling_mean_3":
            float(rolling_mean_3),

        "rolling_mean_24":
            float(rolling_mean_24)
    }

    return feature_data


# ============================================================
# 7. CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Ride-Hailing Demand Prediction API",
    description=(
        "API for predicting hourly ride demand "
        "by pickup zone."
    ),
    version="1.1.0"
)


# ============================================================
# 8. ROOT ENDPOINT
# ============================================================

@app.get("/")
def home():

    return {
        "message":
            "Ride-Hailing Demand Prediction API",
        "status":
            "running"
    }


# ============================================================
# 9. HEALTH CHECK ENDPOINT
# ============================================================

@app.get("/health")
def health():

    return {
        "status":
            "healthy",

        "model_loaded":
            model is not None,

        "historical_rows":
            len(demand_history),

        "number_of_zones":
            len(zone_info),

        "number_of_features":
            len(features),

        "features":
            features
    }


# ============================================================
# 10. AVAILABLE ZONES ENDPOINT
# ============================================================

@app.get("/zones")
def get_zones():

    zones = (
        demand_history[
            [
                "PULocationID",
                "Borough",
                "Zone"
            ]
        ]
        .drop_duplicates(
            "PULocationID"
        )
        .sort_values(
            [
                "Borough",
                "Zone"
            ]
        )
    )

    return {
        "total_zones":
            len(zones),

        "zones":
            zones.to_dict(
                orient="records"
            )
    }


# ============================================================
# 11. MANUAL PREDICTION INPUT
# ============================================================

class DemandPredictionInput(BaseModel):

    hour: int = Field(
        ge=0,
        le=23
    )

    day_of_week_num: int = Field(
        ge=0,
        le=6
    )

    day_of_month: int = Field(
        ge=1,
        le=31
    )

    is_weekend: int = Field(
        ge=0,
        le=1
    )

    PULocationID: int = Field(
        ge=1
    )

    lag_1: float = Field(
        ge=0
    )

    lag_2: float = Field(
        ge=0
    )

    lag_24: float = Field(
        ge=0
    )

    lag_168: float = Field(
        ge=0
    )

    rolling_mean_3: float = Field(
        ge=0
    )

    rolling_mean_24: float = Field(
        ge=0
    )


# ============================================================
# 12. MANUAL PREDICTION ENDPOINT
# ============================================================

@app.post("/predict")
def predict_demand(
    data: DemandPredictionInput
):

    input_data = pd.DataFrame(
        [data.model_dump()]
    )

    # Exact feature order used during training
    input_data = input_data[
        features
    ]

    prediction = model.predict(
        input_data
    )[0]

    # Demand cannot be negative
    prediction = max(
        float(prediction),
        0.0
    )

    return {
        "predicted_demand":
            round(
                prediction,
                2
            )
    }


# ============================================================
# 13. SIMPLE / AUTOMATIC PREDICTION INPUT
# ============================================================

class SimplePredictionInput(BaseModel):

    pickup_location_id: int = Field(
        ge=1
    )

    prediction_datetime: str


# ============================================================
# 14. AUTOMATIC PREDICTION ENDPOINT
# ============================================================

@app.post("/predict-demand")
def predict_demand_automatic(
    data: SimplePredictionInput
):

    # --------------------------------------------------------
    # CONVERT DATETIME STRING
    # --------------------------------------------------------

    try:

        prediction_datetime = pd.Timestamp(
            data.prediction_datetime
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid datetime format. "
                "Use YYYY-MM-DD HH:MM:SS"
            )
        )


    # --------------------------------------------------------
    # REQUIRE START OF HOUR
    # --------------------------------------------------------

    if (
        prediction_datetime.minute != 0
        or prediction_datetime.second != 0
        or prediction_datetime.microsecond != 0
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Prediction datetime must be "
                "at the start of an hour."
            )
        )


    # --------------------------------------------------------
    # VALIDATE PICKUP ZONE
    # --------------------------------------------------------

    if (
        data.pickup_location_id
        not in valid_zone_ids
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Pickup Location ID not found."
            )
        )


    # --------------------------------------------------------
    # AUTOMATICALLY GENERATE MODEL FEATURES
    # --------------------------------------------------------

    try:

        feature_data = (
            build_prediction_features(
                data.pickup_location_id,
                prediction_datetime
            )
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


    # --------------------------------------------------------
    # CONVERT FEATURES TO DATAFRAME
    # --------------------------------------------------------

    input_df = pd.DataFrame(
        [feature_data]
    )

    # Exact feature order used by model
    input_df = input_df[
        features
    ]


    # --------------------------------------------------------
    # MAKE PREDICTION
    # --------------------------------------------------------

    prediction = model.predict(
        input_df
    )[0]

    # Demand cannot be negative
    prediction = max(
        float(prediction),
        0.0
    )


    # --------------------------------------------------------
    # GET ZONE INFORMATION
    # --------------------------------------------------------

    zone = zone_info.loc[
        data.pickup_location_id
    ]

    zone_name = str(
        zone["Zone"]
    )

    borough = str(
        zone["Borough"]
    )


    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "pickup_location_id":
            data.pickup_location_id,

        "zone":
            zone_name,

        "borough":
            borough,

        "prediction_datetime":
            str(
                prediction_datetime
            ),

        "predicted_demand":
            round(
                prediction,
                2
            )
    }