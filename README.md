# Nutrient-data-visualization

## LINK: https://seavisualization.herokuapp.com/

## Project 
- Simple web app for visualising the marine data (nutrients: [NO3-], [PO4-3]; other: salinity, ... )
- the Data are from the database of the Leibniz Institute for Baltic Sea Research - IOW (https://www.io-warnemuende.de)

## Files & folders
**Data** - folder with all datasets provided by the IOW. 113, 213 and 271 are three monitoring stations in the Baltic Sea; the 271 Gotland Deep station is of the main interest

**Dash_app.py** - the web application using Plotly & Dash. Meant for deployment on Heroku

**Data_Analysis.ipynb** - notebook used for data analysis and testing things to be later added to Dash_app.py

**Procfile** - file needed for connecting the Dash_app.py with Heroku server

**requirements.txt** - all libraries (versions) needed for the Dash_app.py (and its deployment on Heroku)

**haloclinedata271.csv, no3data.csv** - datasets derived from the data in Data folder and so far the only data used by Dash_app.py 

**example of app functionality:**

<img width="936" alt="Screenshot 2023-10-30 at 01 05 06" src="https://github.com/KoldaEFK/Nutrient-data-visualization/assets/49583199/37d31869-c11b-4d5f-bf25-24c0ba8d67a8">

## References:
- https://plotly.com/
- https://dash.plotly.com/
