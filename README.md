# AI Enabled Workforce & Capacity Planning

This project is developed for M.Tech AIML final semester project under BITS Pilani WILP.

## Objective
The objective of this project is to forecast workforce requirements for Service teams by considering:

- Baseline service engineer availability
- Work order handling capacity
- BAU forecast growth
- Additional Data Center business growth on top of BAU

## Product Lines
- UPS
- Cooling
- Power Products
- Power System
- Industrial Automation

## Regions
- North
- South
- East
- West

## Technology Stack
- Frontend: Streamlit
- Backend: GitHub repository (CSV/JSON storage)
- Language: Python

## Project Structure
```text
ai-workforce-capacity-planning/
│
├── app.py
├── forecasting.py
├── github_backend.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── data/
    ├── baseline_engineers.csv
    ├── work_orders.csv
    └── assumptions.json
