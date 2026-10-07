# 🚕 Ride-Hailing Demand Analytics and Prediction

An end-to-end data analytics and demand prediction project built using New York City High Volume For-Hire Services (HVFHS) trip data.

The project analyzes historical ride-hailing demand across NYC, identifies temporal and location-based demand patterns, visualizes key insights through Power BI, and provides hourly ride-demand predictions for pickup zones through an interactive Streamlit application.

---

## 📌 Project Overview

Ride-hailing demand varies significantly depending on location, time of day, day of the week, and historical demand patterns.

This project develops a complete analytics and prediction workflow to:

- Process large-scale NYC ride-hailing trip data
- Analyze historical demand patterns
- Perform SQL-based demand analysis
- Create interactive Power BI dashboards
- Engineer time-series demand features
- Train and evaluate machine learning models
- Serve predictions through a FastAPI backend
- Provide a simple Streamlit interface for demand prediction

The final application allows a user to select a **pickup zone, date, and hour** and receive the expected number of rides for that period.

---

## 🎯 Project Objectives

The main objectives of this project are to:

- Analyze hourly ride demand across NYC pickup zones
- Identify peak demand hours and temporal patterns
- Compare demand across boroughs and pickup zones
- Analyze weekday and weekend demand behavior
- Use SQL to extract and investigate important demand patterns
- Build interactive dashboards for historical demand analysis
- Engineer lag and rolling-demand features for prediction
- Develop a model for hourly ride-demand prediction
- Build an API to serve predictions
- Create a simple user interface for interacting with the prediction system

---

## 📊 Dataset

The project uses the **NYC Taxi and Limousine Commission (TLC) High Volume For-Hire Services (HVFHS) trip dataset for January 2025**.

The raw trip dataset contains approximately:

- **20.4 million trip records**
- **25 original columns**

Important trip information includes:

- Request datetime
- Pickup datetime
- Drop-off datetime
- Pickup Location ID
- Drop-off Location ID
- Trip distance
- Trip duration
- Passenger fare
- Tips
- Driver pay
- Shared ride information

NYC Taxi Zone reference data is also used to map location IDs to:

- Borough
- Zone
- Service Zone

For demand modeling, individual trip records are aggregated into **hourly ride demand by pickup zone**.

A complete hourly modeling grid is used so that zone-hour combinations with no observed rides can also be represented with zero demand.

---

## 🔄 Project Workflow

```text
NYC HVFHS Trip Data
        |
        v
Data Understanding
        |
        v
Data Cleaning & Processing
        |
        v
Hourly Zone Demand Aggregation
        |
        v
Exploratory Data Analysis
        |
        +-----------------------+-----------------------+
        |                       |                       |
        v                       v                       v
   SQL Analysis         Power BI Dashboard      Feature Engineering
                                                        |
                                                        v
                                                Model Training
                                                        |
                                                        v
                                                Model Evaluation
                                                        |
                                                        v
                                                   FastAPI
                                                        |
                                                        v
                                             Streamlit Application
                                                        |
                                                        v
                                              Demand Prediction
```

---

## 🧹 Data Processing

The raw HVFHS trip data is processed before analysis and modeling.

The data-processing stage includes:

- Loading large Parquet datasets
- Converting datetime columns
- Examining missing and invalid values
- Checking trip distance
- Checking trip duration
- Checking fare values
- Creating data-quality indicators
- Mapping pickup locations to NYC taxi zones
- Aggregating trips by pickup zone and hour
- Creating a complete zone-hour demand grid

The processed data is stored in Parquet format for efficient analysis.

---

## 🔍 Exploratory Data Analysis

Exploratory Data Analysis (EDA) is used to understand the structure and behavior of ride demand before modeling.

The analysis examines:

- Overall ride-demand distribution
- Daily ride demand
- Hourly demand patterns
- Demand by day of week
- Weekday vs. weekend demand
- Borough-level demand
- Pickup-zone demand
- High-demand locations
- Peak demand periods

The findings from EDA help guide feature engineering, SQL analysis, dashboard development, and model building.

---

## 🗃️ SQL Analysis

SQL is used as a separate analytical component of the project to query the processed demand data and extract useful insights.

The SQL analysis focuses on areas such as:

- Total ride demand
- Demand by pickup zone
- Demand by borough
- Hourly demand
- Daily demand
- Weekday and weekend demand
- High-demand pickup locations
- Peak demand periods

The SQL queries used for the analysis are maintained in the project's `sql/` directory.

SQL complements the Python-based analysis by demonstrating how structured queries can be used to investigate ride-demand patterns efficiently.

---

## 📈 Power BI Dashboard

Power BI is used to create an interactive visual analytics dashboard for historical ride-demand analysis.

The Power BI report contains three main analytical pages:

### Demand Overview

Provides a high-level summary of ride demand and important demand indicators.

### Demand Analysis

Explores temporal demand patterns, including changes in demand across different hours and days.

### Location Analysis

Examines geographical demand patterns across boroughs and pickup zones.

Power BI is maintained as a **separate analytics component** and is not embedded inside the Streamlit prediction interface.

This keeps the two components focused on different purposes:

- **Power BI** → Historical demand analysis and visualization
- **Streamlit** → User interaction with the demand prediction system

---

## ⚙️ Feature Engineering

The hourly demand dataset is transformed into a supervised learning dataset using temporal and historical demand features.

The model uses features including:

- `hour`
- `day_of_week_num`
- `day_of_month`
- `is_weekend`
- `PULocationID`
- `lag_1`
- `lag_2`
- `lag_24`
- `lag_168`
- `rolling_mean_3`
- `rolling_mean_24`

### Lag Features

Lag features provide information about previous demand:

- `lag_1` → Demand one hour earlier
- `lag_2` → Demand two hours earlier
- `lag_24` → Demand at the same time one day earlier
- `lag_168` → Demand at the same time one week earlier

### Rolling Features

Rolling features summarize recent demand behavior:

- `rolling_mean_3` → Average demand over the previous 3 hours
- `rolling_mean_24` → Average demand over the previous 24 hours

These features allow the model to use both calendar information and historical demand behavior.

---

## 🤖 Demand Prediction Model

Several stages of model development are used to build the demand prediction component.

The final prediction system uses a **Histogram-Based Gradient Boosting Regressor (HGB Regressor)** implemented with Scikit-learn.

The trained model is stored using Joblib and loaded by the FastAPI backend when predictions are requested.

The model produces the expected number of rides for a selected:

- Pickup zone
- Date
- Hour

Negative model outputs, if any, are restricted to zero because ride demand cannot be negative.

---

## 🔮 Current and Future Date Prediction

The historical demand dataset is limited to January 2025. Therefore, exact lag values are not directly available for dates outside the historical data period.

The prediction backend handles this automatically.

When exact historical demand exists, the available historical values are used.

When an exact historical timestamp is unavailable, the system estimates the required historical demand features using patterns from the selected pickup zone, prioritizing:

1. Same pickup zone, same day of week, and same hour
2. Same pickup zone and same hour
3. Overall historical average for the pickup zone

These estimated values are then used to construct the lag and rolling features required by the trained model.

This allows the application to return predictions for dates outside the original historical period while keeping the technical process hidden from the end user.

> **Note:** Predictions far beyond the January 2025 data period should be interpreted as model-based estimates derived from historical patterns, not as predictions informed by real-time future conditions.

---

## 🔌 FastAPI Backend

The prediction backend is developed using **FastAPI**.

The API is responsible for:

- Loading the trained model
- Loading the required model feature list
- Loading historical hourly demand data
- Providing pickup-zone information
- Generating prediction features
- Handling historical-pattern fallback logic
- Returning ride-demand predictions to the user interface

### Main API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | API status |
| `GET` | `/health` | Health and model information |
| `GET` | `/zones` | Available pickup zones |
| `POST` | `/predict` | Prediction using manually supplied model features |
| `POST` | `/predict-demand` | Automatic demand prediction using zone and datetime |

The Streamlit application primarily communicates with the `/zones` and `/predict-demand` endpoints.

---

## 🖥️ Streamlit User Interface

The Streamlit application provides a simple interface for obtaining ride-demand predictions.

The user only needs to:

1. Select a pickup zone
2. Select a prediction date
3. Select a prediction hour
4. Click **Predict Ride Demand**

The application then displays:

- Predicted number of rides
- Demand level
- Selected pickup zone
- Prediction date
- Prediction hour

The underlying feature generation and prediction process is handled automatically by the backend, keeping the interface simple for the user.

---

## 🧪 System Testing

The complete prediction workflow was tested using different:

- Pickup zones
- Historical dates
- Future dates
- Prediction hours
- Demand levels

Testing confirmed the complete application flow:

```text
User Input
    |
    v
Streamlit Interface
    |
    v
FastAPI Request
    |
    v
Feature Generation
    |
    v
Prediction Model
    |
    v
API Response
    |
    v
Prediction Display
```

The system successfully returns different demand predictions based on the selected zone, date, and hour.

---

## 🛠️ Technologies Used

### Programming & Data Processing

- Python
- Pandas
- NumPy
- PyArrow
- Jupyter Notebook

### Data Visualization & Analytics

- Matplotlib
- Power BI

### Database / Query Analysis

- SQL

### Machine Learning

- Scikit-learn
- Histogram-Based Gradient Boosting Regressor
- Joblib

### Backend Development

- FastAPI
- Pydantic
- Uvicorn

### User Interface

- Streamlit
- Requests

### Development Tools

- Visual Studio Code
- Git
- GitHub

---

## 📁 Project Structure

A simplified structure of the project is shown below:

```text
Ride_Hailing_Demand_Prediction/
│
├── api/
│   └── app.py
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── models/
│   ├── final_hgb_demand_model.joblib
│   └── model_features.joblib
│
├── notebooks/
│
├── powerbi/
│
├── sql/
│
├── report/
│
├── requirements.txt
│
└── README.md
```

The exact directory contents may contain additional notebooks, datasets, analysis outputs, reports, and supporting project files.

---

## 🚀 Installation and Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Ride_Hailing_Demand_Prediction
```

Replace `<repository-url>` with the GitHub repository URL.

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

For Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

For Windows Command Prompt:

```cmd
.venv\Scripts\activate
```

### 4. Install Required Python Packages

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Project

The FastAPI backend and Streamlit interface need to run at the same time.

### Step 1 — Start FastAPI

From the project root directory:

```bash
uvicorn api.app:app --reload
```

The API runs locally at:

```text
http://127.0.0.1:8000
```

Interactive FastAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### Step 2 — Start Streamlit

Open another terminal, activate the same virtual environment, and run:

```bash
streamlit run dashboard/app.py
```

The Streamlit application will open in the browser.

---

## 📦 Python Requirements

The main Python dependencies are:

```text
pandas
numpy
pyarrow
matplotlib
scikit-learn
joblib
fastapi
pydantic
streamlit
requests
uvicorn
```

Power BI is not included in `requirements.txt` because it is separate desktop software rather than a Python package.

---

## ⚠️ Project Limitations

The current project has several limitations that should be considered when interpreting predictions:

- Historical demand data currently covers January 2025.
- Long-range predictions rely on historical demand patterns rather than real-time demand information.
- Weather conditions are not included.
- Public holidays and special events are not explicitly modeled.
- Traffic conditions are not included.
- The current application operates locally unless separately deployed.

These limitations provide opportunities for future development.

---

## 🔭 Future Improvements

Future versions of the project could include:

- Training with multiple months or years of historical ride data
- Incorporating weather conditions
- Adding public holiday information
- Incorporating major NYC events
- Including real-time or recently observed demand
- Adding traffic-related information
- Evaluating additional time-series and machine learning models
- Improving long-range forecasting
- Deploying the FastAPI backend and Streamlit application to a cloud platform
- Automating data updates and model retraining

---

## 💡 Key Project Outcome

This project demonstrates an end-to-end data analytics workflow that combines:

**Large-Scale Data Processing → Exploratory Data Analysis → SQL Analysis → Power BI Visualization → Feature Engineering → Machine Learning → API Development → Interactive Prediction**

The final system transforms raw ride-hailing trip data into analytical insights and an interactive hourly demand prediction application.

---

## 👤 Author

Developed as a **Ride-Hailing Data Analytics and Demand Prediction** project using NYC HVFHS trip data.