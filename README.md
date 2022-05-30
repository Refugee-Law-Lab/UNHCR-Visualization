# UNHCR-Visualization

This repository contains python code to create visualizations of asylum application data, using data ulled from the United Nations High Commission for Refugees API. For details, see: https://api.unhcr.org/docs/refugee-statistics.html.

# Asylum Applications in Canada 

Jupyter Notebook: asylum-applications-canada.ipynb
Python: asylum-applications-canada.py

This code creates mp4 videos containing animated graphs from asylum applications in Canada. 

The videos are available here: https://youtu.be/DQUFmRTH8vc

The code pulls from two datasets from the UNHCR API: asylumApplications and asylumDecisions. 

Only data from 2000-2020 are included, partial datasets (e.g. 2021 data) have been omitted. 

For both data sets, only applications and decisions at the first instance (FI) and first instance and appeal (FA) stages of procedure were included. 

Three charts are created:

1. A bar chart showing the top 15 countries in applications for asylum in Canada over time from 2000-2020
2. A line graph showing the cumulative number of asylum applications in Canada over time from 2000-2020
3. A line graph showing the application recognition rate in Canada over time from 2000-2020

Recognition rate was calculated by:

(# of recognized decisions) x 100 /(# of recognized decisions + # of rejected decisions)

# Requirements

This code has been written in python 3.6.2, and has the following requirements: 

matplotlib == 3.3.4

numpy == 1.19.5

scipy == 1.0.0

pandas == 0.22.0

Ffmpeg == 1.4

Pandas-alive == 2020.5.15 

Bar-chart-race == 0.1.0

jupyter-notebook == 6.4.3

ipython == 7.16.1

# Acknowledgements

Thanks to UNHCR for making the data freely and easily accessible.

Thanks also to York University, the Centre for Refugee Studies, and Osgoode Hall Law School for hosting the Refugee Law Laboratory, and this reseach. 

This research was funded in part by the Social Sciences and Humanities Research Council of Canada.

# Refugee Law Lab

To learn more about the Refugee Law Laboratory, please visit: https://refugeelab.ca
