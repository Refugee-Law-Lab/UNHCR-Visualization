import sys, csv, os, json, urllib, numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import pandas_alive
import pdb
from itertools import groupby
from time import sleep
from datetime import datetime, date, timedelta

import warnings
warnings.filterwarnings("ignore")

mpl.rcParams['figure.dpi'] = 300
mpl.rcParams['savefig.dpi'] = 300

from IPython.display import set_matplotlib_formats
set_matplotlib_formats('svg')

plt.rc('axes', unicode_minus=False)
plt.rcParams["font.serif"] = "cmr10"

#To get applications from API
#Note can also download csv from here: https://www.unhcr.org/refugee-statistics/download/?url=5q9gHV
yearFrom=2000
yearTo=2020
country='can'
url = "https://api.unhcr.org/population/v1/asylum-applications/?limit=100000&page=&yearFrom="+str(yearFrom)+"&yearTo="+str(yearTo)+"&year=&download=&coo=&coa="+country+"&coo_all=false&coa_all="
with urllib.request.urlopen(url) as urlhtml:
    data = json.loads(urlhtml.read().decode())
df_asylumapps = pd.json_normalize(data, 'items')

#To get decisions from API
yearFrom=2000
yearTo=2020
country='can'
url = "https://api.unhcr.org/population/v1/asylum-decisions/?limit=100000&page=&yearFrom="+str(yearFrom)+"&yearTo="+str(yearTo)+"&year=&download=&coo=&coa="+country+"&coo_all=false&coa_all="
with urllib.request.urlopen(url) as urlhtml:
    data = json.loads(urlhtml.read().decode())
df_asylumdecisions = pd.json_normalize(data, 'items')

#To make CSVs for viewing
today = datetime.today()
df_asylumapps.to_csv('asylum_applications_%s.csv'%(today.strftime('%m-%d-%Y')))
df_asylumdecisions.to_csv('asylum_decisions_%s.csv'%(today.strftime('%m-%d-%Y')))

#load asylum country list and asylum app data
url = "http://api.unhcr.org/rsq/v1/asylums"
df_asylum = pd.read_json(url)

#shortening long names of countries
df_asylumapps['coo_name'] = df_asylumapps['coo_name'].str.replace('Dem. Rep. of the Congo','DRC')
df_asylumapps['coo_name'] = df_asylumapps['coo_name'].str.replace('Iran \(Islamic Rep. of\)','Iran')
df_asylumapps['coo_name'] = df_asylumapps['coo_name'].str.replace('Venezuela \(Bolivarian Republic of\)','Venezuela')
df_asylum['country_name'] = df_asylum['country_name'].str.replace('Dem. Rep. of the Congo','DRC')
df_asylum['country_name'] = df_asylum['country_name'].str.replace('Iran \(Islamic Rep. of\)','Iran')
df_asylum['country_name'] = df_asylum['country_name'].str.replace('Venezuela \(Bolivarian Republic of\)','Venezuela')

#only include applications under "FI" or "FA" decision levels, excludes only "AR"
df_asylumapps = df_asylumapps[((df_asylumapps['dec_level'] == 'FI') | (df_asylumapps['dec_level'] == 'FA'))]

#add up all FI and FA applications

years = range(2000,2021,1)
applied_total = []

for i in years:
    for country in df_asylum['country_name']:
        #print(country)
        #parse out data specific to country in year i
        df_test = df_asylumapps[df_asylumapps['coo_name'] == country]
        #add up all the values in applied section and append to applied_total array
        applied_total.append([i, country, np.sum(df_test[df_test['year'] == i]['applied'])])

#turn array into dataframe
df_applied_total = pd.DataFrame(applied_total,columns=['year','country','total_applied'])

#add month and year to year index
df_applied_total['year'] = df_applied_total['year'].astype(str) + "-12-31"

#bar chart race package requires each row to represent particular time and each column a category
#rotate dataframe using df.pivot
df_applied_pivot = df_applied_total.pivot(index='year',columns='country',values='total_applied')

#calculate cumulative sum of each country over each year so that # of applications in prior years are included
df_applied_pivot_cs = df_applied_pivot.cumsum()

#UNHCR asylum dataset begins in 2000 and represents applications applied from Jan 1-Dec 31 of that year
#initialize dataframe so number starts at 0 on January 1, 2000 when chart begins
df1 = pd.DataFrame([[0] * len(df_applied_pivot_cs.columns)], columns=df_applied_pivot_cs.columns)
df_applied_pivot_cs = df1.append(df_applied_pivot_cs)
df_applied_pivot_cs.rename(index={0:'2000-01-01'},inplace=True)

#convert index to datetime format
df_applied_pivot_cs.index = pd.to_datetime(df_applied_pivot_cs.index)

#calculate total number of asylum applications for each year
total_df_applied = df_applied_pivot_cs.sum(axis=1)

#initializing total # of applications on Jan 1 2000
total_df_applied['2000-01-01'] = 0

# calculate recognition rate data
# shortening names of long countries
df_asylumdecisions['coo_name'] = df_asylumdecisions['coo_name'].str.replace('Dem. Rep. of the Congo', 'DRC')
df_asylumdecisions['coo_name'] = df_asylumdecisions['coo_name'].str.replace('Iran \(Islamic Rep. of\)', 'Iran')
df_asylumdecisions['coo_name'] = df_asylumdecisions['coo_name'].str.replace('Venezuela \(Bolivarian Republic of\)',
                                                                            'Venezuela')
# only include applications under "FI" or "FA" decision levels, excludes only "AR"
df_asylumdecisions = df_asylumdecisions[
    ((df_asylumdecisions['dec_level'] == 'FI') | (df_asylumdecisions['dec_level'] == 'FA'))]

# add up all FI and FA applications
years = range(2000, 2021, 1)
decision_total = []

for i in years:
    for country in df_asylum['country_name']:
        # parse out data specific to country in year i
        df_test = df_asylumdecisions[df_asylumdecisions['coo_name'] == country]
        # add up all the values in applied section and append to applied_total array
        decision_total.append([i, country, np.sum(df_test[df_test['year'] == i]['dec_recognized']),
                               np.sum(df_test[df_test['year'] == i]['dec_rejected']),
                               np.sum(df_test[df_test['year'] == i]['dec_total'])])

# turn array into dataframe
df_decision_total = pd.DataFrame(decision_total,
                                 columns=['year', 'country', 'dec_recognized', 'dec_rejected', 'dec_total'])

#create dataframe reflecting global numbers

#initialize array
decision_cs = []

# populate array with total sum of decisions recognized, rejected, and decision total
for i in years:
    decision_cs.append([i,
                        df_decision_total[df_decision_total['year']==i]['dec_recognized'].astype(int).sum(),
                        df_decision_total[df_decision_total['year']==i]['dec_rejected'].astype(int).sum(),
                        df_decision_total[df_decision_total['year']==i]['dec_total'].astype(int).sum()])

#convert to dataframe
df_decision_cs = pd.DataFrame(decision_cs,columns=['year','dec_recognized','dec_rejected','dec_total'])

#calculate recognition rate
df_decision_cs['recog_rate']=df_decision_cs.apply(lambda row: (row.dec_recognized*100)/(row.dec_recognized+row.dec_rejected),axis=1)

#convert index into date time format
df_decision_cs['year'] = df_decision_cs['year'].astype(str) + "-12-31"
df_decision_cs = df_decision_cs.set_index('year')

#initialize dataframe so number starts at 0 on January 1, 2000 when chart begins
df2 = pd.DataFrame([[0] * len(df_decision_cs.columns)], columns=df_decision_cs.columns)
df_decision_cs = df2.append(df_decision_cs)
df_decision_cs.rename(index={0:'2000-01-01'},inplace=True)
df_decision_cs.index = pd.to_datetime(df_decision_cs.index)

#create recognition rate df for easy line graph plotting
df_recognitionrate = df_decision_cs['recog_rate']

#initializing recognition rate on Jan 1 2000 with end of 2000 numbers since pre-2000 data wasn't collected
df_recognitionrate['2000-01-01'] = df_recognitionrate['2000-12-31']

#Plot bar racing chart for top 15 countries of asylum applications in Canada

bar_chart_race = df_applied_pivot_cs.plot_animated(
                    filename='bcr_unhcr_applied_new.mp4',
                    cmap='tab20c',
                    dpi=600,
                    writer='ffmpeg',
                    n_visible=15,
                    period_fmt="%Y",
                    period_length=2500,
                    interpolate_period=True,
                    shared_fontdict={'family': 'Courier New', 'weight': 'bold',
                                    'color': 'rebeccapurple'},
                    period_label={'x': .98, 'y': .15, 'ha': 'right', 'va': 'center', 'size' : 22},
                    title_size='8',
                    title='Top 15 asylum source countries in Canada (2000-2020)',
                    fixed_max=True,
                    fixed_order=False,
                    steps_per_period=20,
                    label_bars=True,
                    bar_size=.95,
                    bar_label_size=5,
                    tick_label_size=5,
                    scale='linear',
                    fig=None,
                    perpendicular_bar_func=False,
                    bar_kwargs={'alpha': .7},
                    filter_column_colors=False,
                    )

# Plot individual line chart showing total # of asylum applications over time in Canada (2000-2020)

def current_total(values):
    s = f'Total asylum applications (cumulative): {int(values):,}'
    return {'x': .01, 'y': .9, 's': s, 'ha': 'left', 'size': 6}

animated_line_chart=total_df_applied.plot_animated(kind='line',
                        filename='totalasylumapps_new.mp4',
                        #period_label=False,
                        period_length=2500,
                        steps_per_period=20,
                        tick_label_size=6,
                        writer='ffmpeg',
                        figsize=(3.5,2),
                        fixed_max=True,
                        period_summary_func = current_total,
                        period_label={'x': .001, 'y': .001, 'ha': 'right', 'va': 'center','size' : 0, 'color' : 'white'},
                        period_fmt="%Y",
                        dpi=600,
                        bar_label_size=10,
                        add_legend=False,
                        #title="Total asylum applications in Canada (2000-2020)"
                        )

#Plot individual line chart showing application recognition rate over time

def recognition_rate(values):
    s = f'Recognition rate (yearly averages): {int(values):} %'
    return {'x': .01, 'y': .9, 's': s, 'ha': 'left', 'size': 6}

animated_line_chart2=df_recognitionrate.plot_animated(kind='line',
                        filename='recognitionrate_new.mp4',
                        period_length=2500,
                        steps_per_period=20,
                        tick_label_size=6,
                        writer='ffmpeg',
                        figsize=(3.5,2),
                        fixed_max=True,
                        period_summary_func = recognition_rate,
                        period_label={'x': .001, 'y': .001, 'ha': 'right', 'va': 'center','size' : 0, 'color' : 'white'},
                        period_fmt="%Y",
                        dpi=600,
                        add_legend=False
                        )
