import streamlit as st
import requests
from datetime import datetime
from textwrap import dedent


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Ride-Hailing Demand Prediction",
    page_icon="🚕",
    layout="wide"
)


# --------------------------------------------------
# API CONFIGURATION
# --------------------------------------------------

API_BASE_URL = "http://127.0.0.1:8000"


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
<style>
.prediction-card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 14px;
    padding: 30px;
    text-align: center;
    margin-top: 10px;
    margin-bottom: 25px;
}

.prediction-label {
    font-size: 18px;
    font-weight: 600;
    color: #c9d1d9;
    margin-bottom: 8px;
}

.prediction-value {
    font-size: 52px;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.2;
}

.prediction-description {
    font-size: 15px;
    color: #8b949e;
    margin-top: 6px;
    margin-bottom: 18px;
}

.low-demand {
    display: inline-block;
    background-color: rgba(46, 160, 67, 0.15);
    color: #56d364;
    border: 1px solid rgba(46, 160, 67, 0.35);
    border-radius: 20px;
    padding: 7px 16px;
    font-weight: 600;
}

.medium-demand {
    display: inline-block;
    background-color: rgba(210, 153, 34, 0.15);
    color: #e3b341;
    border: 1px solid rgba(210, 153, 34, 0.35);
    border-radius: 20px;
    padding: 7px 16px;
    font-weight: 600;
}

.high-demand {
    display: inline-block;
    background-color: rgba(248, 81, 73, 0.15);
    color: #ff7b72;
    border: 1px solid rgba(248, 81, 73, 0.35);
    border-radius: 20px;
    padding: 7px 16px;
    font-weight: 600;
}

.info-card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 14px;
    padding: 22px;
    min-height: 150px;
}

.info-title {
    font-size: 14px;
    font-weight: 700;
    color: #c9d1d9;
    margin-bottom: 18px;
}

.info-value {
    font-size: 18px;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 6px;
}

.info-caption {
    font-size: 14px;
    color: #8b949e;
}

div.stButton > button {
    width: 100%;
    font-weight: 600;
}
</style>
""",
    unsafe_allow_html=True
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🚕 Ride-Hailing Demand Prediction")

st.caption("NYC Hourly Ride Demand Forecasting System")

st.write(
    "Select a pickup zone, date and hour to estimate the expected ride demand."
)

st.divider()


# --------------------------------------------------
# LOAD PICKUP ZONES FROM API
# --------------------------------------------------

@st.cache_data
def load_zones():
    try:
        response = requests.get(
            f"{API_BASE_URL}/zones",
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()

            if isinstance(data, list):
                return data

            if isinstance(data, dict):
                if "zones" in data:
                    return data["zones"]

                if "pickup_zones" in data:
                    return data["pickup_zones"]

        return []

    except requests.exceptions.RequestException:
        return []


zones = load_zones()


# --------------------------------------------------
# CHECK API CONNECTION
# --------------------------------------------------

if not zones:
    st.error(
        "Could not load pickup zones from the API. "
        "Make sure FastAPI is running on port 8000."
    )

    st.stop()


# --------------------------------------------------
# DEMAND PREDICTION SECTION
# --------------------------------------------------

st.subheader("🔮 Demand Prediction")

col1, col2, col3 = st.columns(3)


# --------------------------------------------------
# PICKUP ZONE
# --------------------------------------------------

with col1:
    selected_zone = st.selectbox(
        "📍 Pickup Zone",
        zones,
        format_func=lambda x: (
            f"{x['Zone']} ({x['Borough']})"
            if isinstance(x, dict)
            else str(x)
        )
    )


# --------------------------------------------------
# PREDICTION DATE
# --------------------------------------------------

with col2:
    prediction_date = st.date_input(
        "🗓️ Prediction Date"
    )


# --------------------------------------------------
# PREDICTION HOUR
# --------------------------------------------------

with col3:
    prediction_hour = st.selectbox(
        "🕐 Prediction Hour",
        range(24),
        format_func=lambda x: datetime.strptime(
            str(x),
            "%H"
        ).strftime("%I:00 %p")
    )


st.write("")


# --------------------------------------------------
# PREDICT BUTTON
# --------------------------------------------------

if st.button(
    "🔮 Predict Ride Demand",
    type="primary",
    use_container_width=True
):

    # --------------------------------------------------
    # GET SELECTED ZONE INFORMATION
    # --------------------------------------------------

    if isinstance(selected_zone, dict):
        pickup_location_id = selected_zone["PULocationID"]
        zone_name = selected_zone["Zone"]
        borough = selected_zone["Borough"]

    else:
        st.error(
            "Invalid zone information received from API."
        )

        st.stop()


    # --------------------------------------------------
    # CREATE PREDICTION DATETIME
    # --------------------------------------------------

    prediction_datetime = datetime.combine(
        prediction_date,
        datetime.min.time()
    ).replace(
        hour=prediction_hour
    )

    prediction_datetime_string = (
        prediction_datetime.strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
    )


    # --------------------------------------------------
    # CREATE API PAYLOAD
    # --------------------------------------------------

    payload = {
        "pickup_location_id": int(pickup_location_id),
        "prediction_datetime": prediction_datetime_string
    }

    api_url = f"{API_BASE_URL}/predict-demand"


    # --------------------------------------------------
    # CALL FASTAPI
    # --------------------------------------------------

    try:

        with st.spinner(
            "Predicting ride demand..."
        ):

            response = requests.post(
                api_url,
                json=payload,
                timeout=30
            )


        # --------------------------------------------------
        # SUCCESS
        # --------------------------------------------------

        if response.status_code == 200:

            result = response.json()

            predicted_demand = result.get(
                "predicted_demand"
            )

            if predicted_demand is not None:

                predicted_demand = float(
                    predicted_demand
                )

                st.success(
                    "Prediction completed successfully!"
                )

                st.divider()

                st.subheader(
                    "📊 Prediction Result"
                )


                # --------------------------------------------------
                # DEMAND LEVEL
                # --------------------------------------------------

                if predicted_demand < 100:
                    demand_level = "Low Demand"
                    demand_class = "low-demand"
                    demand_icon = "🟢"

                elif predicted_demand < 250:
                    demand_level = "Medium Demand"
                    demand_class = "medium-demand"
                    demand_icon = "🟡"

                else:
                    demand_level = "High Demand"
                    demand_class = "high-demand"
                    demand_icon = "🔴"


                # --------------------------------------------------
                # MAIN PREDICTION CARD
                # --------------------------------------------------

                prediction_card = dedent(
                    f"""
                    <div class="prediction-card">
                        <div class="prediction-label">Predicted Ride Demand</div>
                        <div class="prediction-value">{predicted_demand:.0f}</div>
                        <div class="prediction-description">Expected rides during this hour</div>
                        <div class="{demand_class}">{demand_icon} {demand_level}</div>
                    </div>
                    """
                ).strip()

                st.markdown(
                    prediction_card,
                    unsafe_allow_html=True
                )


                # --------------------------------------------------
                # FORMAT DATE AND HOUR
                # --------------------------------------------------

                formatted_hour = (
                    prediction_datetime.strftime(
                        "%I:00 %p"
                    )
                )

                formatted_date = (
                    prediction_date.strftime(
                        "%B %d, %Y"
                    )
                )


                # --------------------------------------------------
                # RESULT DETAIL CARDS
                # --------------------------------------------------

                result_col1, result_col2, result_col3 = (
                    st.columns(3)
                )


                # PICKUP ZONE CARD
                with result_col1:

                    zone_card = dedent(
                        f"""
                        <div class="info-card">
                            <div class="info-title">📍 PICKUP ZONE</div>
                            <div class="info-value">{zone_name}</div>
                            <div class="info-caption">{borough}</div>
                        </div>
                        """
                    ).strip()

                    st.markdown(
                        zone_card,
                        unsafe_allow_html=True
                    )


                # DATE CARD
                with result_col2:

                    date_card = dedent(
                        f"""
                        <div class="info-card">
                            <div class="info-title">🗓️ PREDICTION DATE</div>
                            <div class="info-value">{formatted_date}</div>
                            <div class="info-caption">Selected prediction date</div>
                        </div>
                        """
                    ).strip()

                    st.markdown(
                        date_card,
                        unsafe_allow_html=True
                    )


                # HOUR CARD
                with result_col3:

                    hour_card = dedent(
                        f"""
                        <div class="info-card">
                            <div class="info-title">🕐 PREDICTION HOUR</div>
                            <div class="info-value">{formatted_hour}</div>
                            <div class="info-caption">Hourly demand forecast</div>
                        </div>
                        """
                    ).strip()

                    st.markdown(
                        hour_card,
                        unsafe_allow_html=True
                    )


                # --------------------------------------------------
                # FOOTER
                # --------------------------------------------------

                st.divider()

                st.caption(
                    "Ride-Hailing Demand Analytics & Prediction "
                    "• NYC HVFHS Data "
                )


            else:

                st.warning(
                    "Prediction was returned, but "
                    "predicted_demand was not found "
                    "in the API response."
                )

                st.json(result)


        # --------------------------------------------------
        # API ERROR
        # --------------------------------------------------

        else:

            st.error(
                f"Prediction failed. "
                f"API returned status code "
                f"{response.status_code}."
            )

            try:
                error_data = response.json()

                if isinstance(error_data, dict):
                    detail = error_data.get("detail")

                    if detail:
                        st.warning(str(detail))
                    else:
                        st.json(error_data)

                else:
                    st.json(error_data)

            except Exception:
                st.write(response.text)


    # --------------------------------------------------
    # CONNECTION ERROR
    # --------------------------------------------------

    except requests.exceptions.ConnectionError:

        st.error(
            "Cannot connect to FastAPI. "
            "Make sure the API is running "
            "on port 8000."
        )


    # --------------------------------------------------
    # TIMEOUT
    # --------------------------------------------------

    except requests.exceptions.Timeout:

        st.error(
            "The prediction API took too long "
            "to respond."
        )


    # --------------------------------------------------
    # OTHER ERROR
    # --------------------------------------------------

    except Exception as e:

        st.error(
            f"An unexpected error occurred: {e}"
        )