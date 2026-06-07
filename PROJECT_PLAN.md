# Project Plan
## Introduction
The Kosicodie Macro Dashboard is a web application built using Streamlit, which provides an interactive dashboard for visualizing and analyzing US macroeconomic trends. The application fetches data from the Federal Reserve Economic Data (FRED) API and displays various economic indicators, including GDP, unemployment rate, inflation rate, and yield spread.

## Current Functionality
The project currently does the following:
* Fetches economic data from the FRED API
* Displays the latest values of various economic indicators, including GDP, unemployment rate, and inflation rate
* Plots time series charts for each economic indicator
* Calculates and displays the yield spread and recession probability
* Provides summary statistics and a correlation matrix for the economic indicators
* Displays a simple forecast chart for GDP using a rolling mean

## Broken or Incomplete Features
The following features are broken or incomplete:
* The forecast functionality is very basic and only uses a rolling mean. A more sophisticated forecasting model, such as ARIMA, should be implemented.
* There is no error handling for API requests or data processing. This could lead to the application crashing if there are issues with the FRED API or the data.
* The application does not provide any interactive features, such as the ability to select specific time ranges or economic indicators.
* The recession probability calculation is a simple logistic function and may not accurately reflect the complexity of recession forecasting.

## Next Steps
The following features should be built next:
* Implement a more sophisticated forecasting model, such as ARIMA, for GDP and other economic indicators
* Add error handling for API requests and data processing
* Implement interactive features, such as time range selection and economic indicator selection
* Improve the recession probability calculation using a more advanced model, such as a machine learning model

## Milestone Roadmap
The following milestones are planned:
* **Milestone 1: Forecasting Model Implementation** (1 week)
	+ Implement ARIMA forecasting model for GDP and other economic indicators
	+ Test and refine the forecasting model
* **Milestone 2: Error Handling and Interactive Features** (2 weeks)
	+ Implement error handling for API requests and data processing
	+ Add interactive features, such as time range selection and economic indicator selection
* **Milestone 3: Recession Probability Model Improvement** (2 weeks)
	+ Research and implement a more advanced recession probability model, such as a machine learning model
	+ Test and refine the recession probability model
* **Milestone 4: Finalize and Deploy** (1 week)
	+ Finalize all features and testing
	+ Deploy the application to a production environment
