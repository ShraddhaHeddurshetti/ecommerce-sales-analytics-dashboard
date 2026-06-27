# E-Commerce Sales Analytics Dashboard

This project is an end-to-end data analytics dashboard developed using the Olist Brazilian E-Commerce Dataset. The goal of the project is to analyze sales performance, customer behavior, order trends, and product categories through an interactive Streamlit dashboard.

## Project Overview

The project follows a complete analytics workflow:

Raw Data → Data Ingestion → Data Cleaning → Data Transformation → SQLite Database → Streamlit Dashboard

## Technologies Used

* Python
* Pandas
* NumPy
* Streamlit
* Plotly
* SQLite
* SQLAlchemy
* Pytest
* GitHub Actions

## Project Structure

```text
ecommerce-analytics-dashboard/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   └── 01_eda.ipynb
├── src/
│   ├── ingest.py
│   ├── clean.py
│   ├── transform.py
│   └── db.py
├── app/
│   └── dashboard.py
├── tests/
│   └── test_clean.py
├── .github/workflows/
│   └── ci.yml
├── requirements.txt
└── README.md
```

## Getting Started

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/ecommerce-analytics-dashboard.git
cd ecommerce-analytics-dashboard
```

Create a virtual environment:

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Mac/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Dataset

Download the Olist Brazilian E-Commerce Dataset from Kaggle and place all CSV files inside the `data/raw/` folder.

Required files:

```text
olist_orders_dataset.csv
olist_order_items_dataset.csv
olist_customers_dataset.csv
olist_products_dataset.csv
olist_sellers_dataset.csv
olist_order_reviews_dataset.csv
product_category_name_translation.csv
```

## Running the Project

Run data ingestion:

```bash
python src/ingest.py
```

Run data cleaning:

```bash
python src/clean.py
```

Run data transformation:

```bash
python src/transform.py
```

Create and load the SQLite database:

```bash
python src/db.py
```

Start the Streamlit dashboard:

```bash
streamlit run app/dashboard.py
```

The dashboard will open in your browser at:

```text
http://localhost:8501
```

## Running Tests

```bash
pytest tests/ -v
```

or

```bash
pytest tests/ -v --tb=short
```

## Dashboard Features

* Revenue and sales performance analysis
* Monthly revenue trends
* Order status distribution
* Top-selling product categories
* Revenue analysis by state
* Customer review score trends
* Interactive filtering options
* Detailed data view for exploration

## Git Commands

Initialize Git:

```bash
git init
```

Add files:

```bash
git add .
```

Commit changes:

```bash
git commit -m "Initial commit"
```

Connect to GitHub:

```bash
git remote add origin https://github.com/YOUR_USERNAME/ecommerce-analytics-dashboard.git
```

Push code:

```bash
git branch -M main
git push -u origin main
```

## Deployment

The application can be deployed easily using Streamlit Cloud.

1. Push the project to GitHub.
2. Sign in to Streamlit Cloud.
3. Create a new app.
4. Select your repository.
5. Set the main file as:

```text
app/dashboard.py
```

6. Click Deploy.

