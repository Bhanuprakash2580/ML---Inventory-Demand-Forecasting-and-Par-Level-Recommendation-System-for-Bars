
# Inventory Demand Forecasting and Par Level Recommendation System

## 🌐 Live Demo

Try the deployed Streamlit application:

🔗 [Inventory Demand Forecasting Dashboard](https://nnayvzb8xwhwvp7fwsdfjq.streamlit.app/)

The application provides an interactive interface for exploring inventory data,
demand forecasts, and inventory par-level recommendations.

## 📌 Project Overview

The **Inventory Demand Forecasting and Par Level Recommendation System** is a machine learning and inventory analytics project designed to help bars forecast future item-level consumption and make data-driven inventory planning decisions.

The system analyzes historical inventory movement data across multiple bars, identifies consumption patterns, forecasts future demand, recommends inventory par levels, and simulates inventory management scenarios.

An interactive Streamlit dashboard is provided to visualize the results and explore inventory recommendations.

---

## 🎯 Problem Statement

Bars need to maintain sufficient inventory to meet customer demand while avoiding unnecessary overstocking.

Traditional inventory planning may depend on manual calculations and historical assumptions. This can lead to:

- Stockouts
- Excess inventory
- Inefficient inventory planning
- Increased operational costs
- Difficulty identifying consumption trends

This project aims to develop a data-driven solution for forecasting demand and recommending inventory par levels.

---

## 🚀 Project Objectives

The main objectives of this project are:

1. Analyze historical inventory consumption data.
2. Clean and preprocess the dataset.
3. Identify consumption patterns across bars and products.
4. Develop a demand forecasting solution.
5. Evaluate forecasting performance.
6. Calculate recommended inventory par levels.
7. Simulate inventory management scenarios.
8. Build an interactive Streamlit dashboard.
9. Deploy the application for demonstration.

---

## 🧠 Key Features

- Historical inventory data analysis
- Data cleaning and preprocessing
- Exploratory data analysis
- Time-based demand forecasting
- Baseline model comparison
- Forecast evaluation
- Item-level inventory recommendations
- Safety stock calculation
- Inventory simulation
- Interactive Streamlit dashboard
- CSV export functionality
- GitHub-based deployment

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Programming language |
| Pandas | Data processing and analysis |
| NumPy | Numerical calculations |
| Scikit-learn | Machine learning and evaluation |
| Matplotlib | Data visualization |
| Seaborn | Statistical visualization |
| Streamlit | Interactive dashboard |
| Jupyter Notebook | Data exploration and experimentation |
| Excel | Source dataset |
| Git | Version control |
| GitHub | Repository hosting |
| Streamlit Community Cloud | Application deployment |

> The final technology list should reflect only the libraries actually used in the implementation.

---

## 📂 Project Structure

```text
inventory-demand-forecasting/
│
├── data/
│   └── Consumption Dataset.xlsx
│
├── notebooks/
│   └── exploratory_analysis.ipynb
│
├── src/
│   ├── data_preprocessing.py
│   ├── forecasting.py
│   ├── par_level.py
│   └── evaluation.py
│
├── models/
│   └── forecasting_model.pkl
│
├── outputs/
│   └── inventory_recommendations.csv
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
```

---

## 📊 Dataset Description

The project uses historical inventory movement data stored in an Excel file.

### Dataset Information

| Attribute | Description |
|---|---|
| Dataset file | Consumption Dataset.xlsx |
| Data type | Historical inventory movement data |
| Business domain | Bar inventory management |
| Granularity | Item-level consumption records |
| Time dimension | Date-based historical records |

### Dataset Analysis

The following information is analyzed during preprocessing:

- Number of records
- Date range
- Bar locations
- Brands
- Product categories
- Consumption quantities
- Missing values
- Duplicate records
- Outliers

> Exact dataset statistics should be updated based on the final dataset inspection.

---

## 🔄 Project Workflow

```text
Historical Inventory Dataset
            |
            v
   Data Preprocessing
            |
            v
 Exploratory Data Analysis
            |
            v
 Feature Engineering
            |
            v
 Demand Forecasting
            |
            v
 Model Evaluation
            |
            v
 Par Level Calculation
            |
            v
 Inventory Simulation
            |
            v
 Streamlit Dashboard
            |
            v
       Deployment
```

---

## 🧹 Data Preprocessing

The preprocessing pipeline prepares the historical inventory data for analysis and forecasting.

### Preprocessing Steps

1. Load the Excel dataset.
2. Inspect the dataset structure.
3. Identify relevant columns.
4. Convert date columns into a consistent format.
5. Check missing values.
6. Check duplicate records.
7. Validate consumption quantities.
8. Handle invalid or missing data appropriately.
9. Aggregate consumption by date and item.
10. Prepare the dataset for forecasting.

The preprocessing decisions are documented to improve transparency and reproducibility.

---

## 📈 Exploratory Data Analysis

Exploratory Data Analysis (EDA) is performed to understand inventory consumption patterns.

### Analysis Performed

- Daily consumption trends
- Consumption by bar
- Consumption by brand
- Consumption by product category
- Frequently consumed items
- Distribution of consumption
- Seasonal or weekly patterns
- Potential outliers

### Example Visualizations

- Daily consumption line chart
- Bar-wise consumption chart
- Category-wise consumption chart
- Top consumed items chart
- Actual versus predicted demand chart

---

## 🤖 Demand Forecasting

The forecasting component estimates future consumption using historical inventory data.

### Forecasting Approach

A baseline forecasting method is established first. A suitable machine learning or time-series model may then be trained and compared with the baseline.

Potential approaches include:

- Moving-average baseline
- Lag-based feature models
- Random Forest
- Gradient Boosting
- XGBoost
- Other suitable forecasting methods

The final model is selected based on data suitability, evaluation performance, interpretability, and implementation reliability.

### Feature Engineering

Possible features include:

- Historical consumption lags
- Rolling average consumption
- Day of the week
- Month
- Historical demand statistics
- Item and bar identifiers

Time-based splitting is used to avoid future information leaking into the training data.

---

## 📏 Model Evaluation

The forecasting solution is evaluated using appropriate metrics.

### Evaluation Metrics

#### Mean Absolute Error (MAE)

MAE measures the average absolute difference between actual and predicted consumption.

\[
MAE = \frac{1}{n}\sum_{i=1}^{n}|y_i-\hat{y}_i|
\]

#### Root Mean Squared Error (RMSE)

RMSE measures the square root of the average squared prediction error.

\[
RMSE = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(y_i-\hat{y}_i)^2}
\]

#### Weighted Absolute Percentage Error (WAPE)

WAPE measures the total absolute error relative to total actual consumption.

\[
WAPE = \frac{\sum |y_i-\hat{y}_i|}{\sum |y_i|}
\]

### Evaluation Results

| Metric | Result |
|---|---|
| MAE | TODO: Add measured value |
| RMSE | TODO: Add measured value |
| WAPE | TODO: Add measured value |
| Baseline model | TODO: Add model name |
| Final model | TODO: Add model name |

> Evaluation values must be generated from the actual test results. Do not enter estimated or fabricated metrics.

---

## 📦 Inventory Par Level Recommendation

The system calculates recommended inventory par levels using expected demand and safety stock.

### Key Concepts

**Lead Time:** The time required for inventory replenishment.

**Review Period:** The number of days between inventory reviews or replenishment decisions.

**Safety Stock:** Additional inventory maintained to help account for demand variability.

### General Calculation

Expected demand during the planning period:

\[
Expected\ Demand = Forecasted\ Daily\ Demand \times Planning\ Period
\]

A general par-level formulation is:

\[
Par\ Level = Expected\ Demand + Safety\ Stock
\]

The exact formula and assumptions depend on the implemented forecasting and inventory policy.

### Recommendation Output

The system can generate item-level recommendations containing fields such as:

- Bar
- Brand or item
- Category
- Forecasted demand
- Lead time
- Review period
- Safety stock
- Recommended par level

---

## 🔁 Inventory Simulation

A simulation is included to demonstrate how inventory recommendations may perform under defined assumptions.

### Simulation Components

- Opening inventory
- Daily consumption
- Replenishment logic
- Lead time
- Reorder threshold
- Ending inventory
- Stockout tracking
- Replenishment assumptions

### Simulation Metrics

- Total consumption
- Number of stockout days
- Ending inventory
- Replenishment quantity
- Inventory availability

> Simulation results depend on the assumptions and historical data used. They should not be interpreted as guaranteed real-world business outcomes.

---

## 🖥️ Streamlit Dashboard

The project includes an interactive Streamlit dashboard.

### Dashboard Sections

#### 1. Project Overview

Provides a summary of the business problem, project objectives, and solution.

#### 2. Dataset Overview

Displays:

- Dataset preview
- Number of records
- Date range
- Available bars
- Available brands
- Available categories

#### 3. Exploratory Data Analysis

Displays interactive charts for understanding consumption patterns.

#### 4. Demand Forecasting

Displays:

- Forecast results
- Actual versus predicted demand
- Selected item analysis
- Forecast horizon

#### 5. Model Evaluation

Displays the calculated evaluation metrics for the forecasting models.

#### 6. Par Level Recommendations

Displays:

- Item-level forecasts
- Expected demand
- Safety stock
- Recommended par levels

#### 7. Inventory Simulation

Displays inventory movement and simulation metrics.

#### 8. Download Results

Allows users to download recommendation results in CSV format.

---

## ⚙️ Installation and Setup

### Prerequisites

Install the following:

- Python 3.10 or compatible supported version
- Git
- VS Code (recommended)
- A virtual environment

### Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/inventory-demand-forecasting.git
```

Navigate to the project directory:

```bash
cd inventory-demand-forecasting
```

### Create a Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate the environment:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

Make sure the required dataset and project files are available in their expected locations.

---

## ▶️ Run the Application Locally

Run the Streamlit application from the project root:

```bash
streamlit run app.py
```

The application will open in your browser.

If the application does not open automatically, use the local URL displayed in the terminal.

---

## ☁️ Deployment

The application can be deployed using **Streamlit Community Cloud**.

### Deployment Steps

1. Push the project to a GitHub repository.
2. Confirm that `app.py` is available.
3. Confirm that `requirements.txt` contains the required dependencies.
4. Visit [Streamlit Community Cloud](https://share.streamlit.io/).
5. Sign in using GitHub.
6. Select **Create app**.
7. Select the repository, branch, and entrypoint file.
8. Configure the Python version if required.
9. Click **Deploy**.
10. Test the deployed application.

Streamlit Community Cloud uses the repository's files and dependency configuration to build and run the application.

Official documentation:

- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies

---

## 🔐 Data and Security

- Do not commit passwords, API keys, or private credentials.
- Use `.gitignore` for local environment files.
- Avoid exposing sensitive business information.
- Use Streamlit secrets management for required credentials.
- Validate uploaded files before processing them.

---

## 🧪 Testing and Validation

The project should be tested before deployment.

### Testing Checklist

- [ ] Dataset loads successfully.
- [ ] Preprocessing executes without errors.
- [ ] Missing-value handling works correctly.
- [ ] Forecasting pipeline executes successfully.
- [ ] Evaluation metrics are calculated correctly.
- [ ] Par-level recommendations are generated.
- [ ] Simulation runs successfully.
- [ ] Streamlit dashboard loads.
- [ ] Filters work correctly.
- [ ] Charts display correctly.
- [ ] CSV download works.
- [ ] Deployment works successfully.

---

## ⚠️ Limitations

The project may have the following limitations:

1. Forecast accuracy depends on the quality and availability of historical data.
2. Limited historical data may reduce reliability for some items.
3. External factors such as events, promotions, and seasonal changes may not be fully represented.
4. Inventory recommendations depend on lead-time and safety-stock assumptions.
5. Simulation results are not a substitute for production inventory testing.
6. Forecasting performance may differ across bars and individual items.

---

## 🔮 Future Improvements

Possible future enhancements include:

- Advanced time-series forecasting models
- Automated model selection
- Hyperparameter tuning
- External demand drivers
- Holiday and event features
- Automated retraining
- Real-time inventory integration
- Inventory alert notifications
- User authentication
- Cloud-based data storage
- Monitoring forecast performance over time

---

## 📋 Assignment Deliverables

| Deliverable | Status |
|---|---|
| Data analysis notebook | TODO |
| Forecasting implementation | TODO |
| Inventory par-level recommendations | TODO |
| Inventory simulation | TODO |
| Streamlit application | TODO |
| GitHub repository | TODO |
| Project report | TODO |
| Demonstration video | TODO |

---

## 🎥 Project Demonstration

The demonstration video covers:

1. Project introduction
2. Dataset analysis
3. Data preprocessing
4. Demand forecasting
5. Model evaluation
6. Par-level recommendations
7. Streamlit dashboard
8. Project conclusion

Video link:

> TODO: Add your video link.

---

## 👨‍💻 Author

**Bhanu Prakash Suram**

- GitHub: TODO: Add GitHub profile URL
- LinkedIn: TODO: Add LinkedIn profile URL
- Email: TODO: Add professional email address

---

## 📄 License

This project is created for educational and assignment purposes.

Add an appropriate open-source license if you intend to distribute the project publicly.

---

## ⭐ Acknowledgements

- Python
- Pandas
- NumPy
- Scikit-learn
- Streamlit
- Streamlit Community Cloud

Thank you for reviewing this project.
