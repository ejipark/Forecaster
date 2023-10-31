import requests
import pandas as pd
from datetime import datetime, timedelta, date
import sklearn
import joblib
import calendar

gb_model = joblib.load('artifacts/gb_model.pkl')
ls_model = joblib.load('artifacts/ls_model.pkl')
rf_model = joblib.load('artifacts/rf_model.pkl')
stacking_model = joblib.load('artifacts/stacking_model.pkl')

from flask import Flask,render_template,request
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('home.html')

@app.route('/home')
def get_home():
    return render_template('home.html')

@app.route('/about')
def get_about():
    return render_template('about.html')

@app.route('/help')
def get_help():
    return render_template('help.html')

@app.route('/contact')
def get_contact():
    return render_template('contact.html')

@app.route('/predict',methods=['post'])
def get_forecast():
    Airport = request.form['Airport']
    Date = request.form['dateInput']

    k = ['ATL', 'LAX', 'ORD', 'DFW', 'DEN', 'JFK', 'SFO', 'LAS', 'SEA', 'CLT']
    days = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thurday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    ap_names = {'ATL':'Hartsfield-Jackson Atlanta International Airport', 'LAX':'Los Angeles International Airport', 'ORD':"Chicago O'Hare International Airport", 'DFW':'Dallas/Fort Worth International Airport', 'DEN':'Denver International Airport', 'JFK':'John F. Kennedy International Airport', 'SFO':'San Francisco International Airport', 'LAS':'Harry Reid International Airport', 'SEA':'Seattle-Tacoma International Airport', 'CLT':'Charlotte Douglas International Airport'}
    airport_name = ap_names[Airport]

    loc = {'ATL': '33.6407,-84.4277', 'LAX': '33.9416,-118.4085', 'ORD': '41.9802,-87.90899', 'DFW': '32.8998,-97.0403', 'DEN': '39.8561,-104.6737', 'JFK': '40.6413,-73.7781', 'SFO': '37.6213,-122.3790', 'LAS': '36.0840,-115.1537', 'SEA': '47.4480,-122.3088', 'CLT': '35.2144,-80.9473'}
    url = 'https://api.weatherbit.io/v2.0/forecast/daily?'
    
    APIKey = '9688b0708e704469beb49279f95cfdc6'
    gets = []
    for key, value in loc.items():
        lat = '&lat=' + value.split(",")[0]
        long = '&lon=' + value.split(",")[1]
        key = '&key=' + APIKey
        n = url+lat+long+key
        gets.append(n)
    locs = dict(zip(k, gets))
    
    APIKey2 = '8a00dc3c01ed47269c3dc00fd7177b35'
    gets2 = []
    for key, value in loc.items():
        lat = '&lat=' + value.split(",")[0]
        long = '&lon=' + value.split(",")[1]
        key = '&key=' + APIKey2
        n2 = url+lat+long+key
        gets2.append(n2)
    locs2 = dict(zip(k, gets2))

    def get_all_forecast(airport):
        try:
            loc = locs[airport]
            grid = requests.get(loc)
            data = grid.json()
            df = pd.DataFrame(data['data'])
        except KeyError:
            loc = locs2[airport]
            grid = requests.get(loc)
            data = grid.json()
            df = pd.DataFrame(data['data'])
        df['Airport'] = airport
        df['precip'] = df['precip'] * 0.0393701 / 24
        df['wind_spd'] = df['wind_spd'] * 1.94384
        if 'vis' in df.columns:
            df['vis'] = df['vis'] * 0.621371
        df['vis'].where(df['vis'] < 10.0, 10.0, inplace=True)
        df['temp'] = (df['temp'] *9/5) + 32
        df['dewpt'] = (df['dewpt'] *9/5) + 32
        df["TempDate"] = pd.to_datetime(df["datetime"])
        df['DOW'] = df['TempDate'].dt.dayofweek
        df['day_of_week'] = df['DOW'].replace(days)
        df['temp_month'] = df['TempDate']
        df['month'] = df['TempDate'].dt.month.apply(lambda x: calendar.month_name[x])
        df2 = pd.get_dummies(data = df, prefix = 'day_of_week', columns = ['day_of_week'])
        df3 = pd.get_dummies(data = df2, prefix = 'month', columns = ['month'])
        df3['airtemp'] = df3['Airport']
        df4 = pd.get_dummies(data = df3, prefix = 'origin', columns = ['airtemp'])

        temp_list = ['vis', 'day_of_week_Monday', 'day_of_week_Tuesday', 'day_of_week_Wednesday', 'day_of_week_Thursday', 'day_of_week_Friday', 'day_of_week_Saturday', 'day_of_week_Sunday', \
                    'month_April', 'month_August', 'month_December', 'month_February', 'month_January', 'month_July', 'month_June', 'month_March', 'month_May', 'month_November', 'month_October', 'month_September', \
                    'origin_ATL', 'origin_CLT', 'origin_DEN', 'origin_DFW', 'origin_JFK', 'origin_LAS', 'origin_LAX', 'origin_ORD', 'origin_SEA', 'origin_SFO']
        
        for i in temp_list:
            if i not in df4.columns:
                df4[i] = 0

        df4['datetime'] = pd.to_datetime(df4["datetime"])
        df4['display_dtm'] = df4['datetime'].dt.strftime('%m/%d/%Y')
        df4 = df4.rename(columns = {'dewpt': 'dewp', 'rh': 'relh', 'wind_spd': 'wind_speed', 'slp': 'pressure', 'vis': 'visib'})
        df4 = df4[['Airport', 'datetime', 'display_dtm', 'precip', 'temp', 'dewp', 'relh', 'wind_dir', 'wind_speed', 'pressure', 'visib',
                'day_of_week_Friday', 'day_of_week_Monday', 'day_of_week_Saturday',
                'day_of_week_Sunday', 'day_of_week_Thursday', 'day_of_week_Tuesday',
                'day_of_week_Wednesday', 'month_April', 'month_August', 'month_December',
                'month_February', 'month_January', 'month_July', 'month_June', 'month_March',
                'month_May', 'month_November', 'month_October', 'month_September',
                'origin_ATL', 'origin_CLT', 'origin_DEN', 'origin_DFW', 'origin_JFK',
                'origin_LAS', 'origin_LAX', 'origin_ORD', 'origin_SEA', 'origin_SFO']]
        return df4

    temp_all_list = []
    for i in k:
        ports = get_all_forecast(i)
        temp_all_list.append(ports)
    df_future = pd.concat(temp_all_list)

    feats = df_future.iloc[:, 3:]

    gb_preds = gb_model.predict(feats)
    ls_preds = ls_model.predict(feats)
    rf_preds = rf_model.predict(feats)
    stacking_preds = stacking_model.predict(feats)

    df_future['predicted_rate'] = gb_preds

    if request.form['action'] == 'actual':
        pred = False
        ddtm = df_future[(df_future['datetime'] == Date) & (df_future['Airport'] == Airport)].iloc[0]['display_dtm']
        rate = df_future[(df_future['datetime'] == Date) & (df_future['Airport'] == Airport)].iloc[0]['predicted_rate']
        precip = round(df_future[(df_future['datetime'] == Date) & (df_future['Airport'] == Airport)].iloc[0]['precip'], 3)
        temp = int(df_future[(df_future['datetime'] == Date) & (df_future['Airport'] == Airport)].iloc[0]['temp'])
        wind_speed = round(df_future[(df_future['datetime'] == Date) & (df_future['Airport'] == Airport)].iloc[0]['wind_speed'], 1)
        dewpt = int(df_future[(df_future['datetime'] == Date) & (df_future['Airport'] == Airport)].iloc[0]['dewp'])
        pres = round(df_future[(df_future['datetime'] == Date) & (df_future['Airport'] == Airport)].iloc[0]['pressure'], 1)
        wind_dir = int(df_future[(df_future['datetime'] == Date) & (df_future['Airport'] == Airport)].iloc[0]['wind_dir'])
        visib = round(df_future[(df_future['datetime'] == Date) & (df_future['Airport'] == Airport)].iloc[0]['visib'], 1)
        relh = int(df_future[(df_future['datetime'] == Date) & (df_future['Airport'] == Airport)].iloc[0]['relh'])

    else: # customize weather
        f_precip = float(request.form['Precipitation'])
        f_temp = float(request.form['Temperature'])
        f_dewpt = float(request.form['DewPoint'])
        f_relh = float(request.form['RelHumidity'])
        f_wind_dir = float(request.form['WindDirection'])
        f_wind_speed = float(request.form['WindSpeed'])
        f_pres = float(request.form['Pressure'])
        f_visib = float(request.form['Visibility'])

        data = [[Airport, Date, f_precip, f_temp, f_dewpt, f_relh, f_wind_dir, f_wind_speed, f_pres, f_visib]]
        df = pd.DataFrame(data, columns = ['Airport', 'datetime', 'precip', 'temp', 'dewp', 'relh', 'wind_dir', 'wind_speed', 'pressure', 'visib'])
        df["TempDate"] = pd.to_datetime(df["datetime"])
        df['DOW'] = df['TempDate'].dt.dayofweek
        df['day_of_week'] = df['DOW'].replace(days)
        df['temp_month'] = df['TempDate']
        df['month'] = df['TempDate'].dt.month.apply(lambda x: calendar.month_name[x])

        df2 = pd.get_dummies(data = df, prefix = 'day_of_week', columns = ['day_of_week'])
        df3 = pd.get_dummies(data = df2, prefix = 'month', columns = ['month'])
        df3['airtemp'] = df3['Airport']
        df4 = pd.get_dummies(data = df3, prefix = 'origin', columns = ['airtemp'])

        temp_list = ['day_of_week_Monday', 'day_of_week_Tuesday', 'day_of_week_Wednesday', 'day_of_week_Thursday', 'day_of_week_Friday', 'day_of_week_Saturday', 'day_of_week_Sunday', \
                    'month_April', 'month_August', 'month_December', 'month_February', 'month_January', 'month_July', 'month_June', 'month_March', 'month_May', 'month_November', 'month_October', 'month_September', \
                    'origin_ATL', 'origin_CLT', 'origin_DEN', 'origin_DFW', 'origin_JFK', 'origin_LAS', 'origin_LAX', 'origin_ORD', 'origin_SEA', 'origin_SFO']
        
        for i in temp_list:
            if i not in df4.columns:
                df4[i] = 0

        df4['datetime'] = pd.to_datetime(df4["datetime"])
        df4['display_dtm'] = df4['datetime'].dt.strftime('%m/%d/%Y')
        df4 = df4[['Airport', 'datetime', 'display_dtm', 'precip', 'temp', 'dewp', 'relh', 'wind_dir', 'wind_speed', 'pressure', 'visib',
                'day_of_week_Friday', 'day_of_week_Monday', 'day_of_week_Saturday',
                'day_of_week_Sunday', 'day_of_week_Thursday', 'day_of_week_Tuesday',
                'day_of_week_Wednesday', 'month_April', 'month_August', 'month_December',
                'month_February', 'month_January', 'month_July', 'month_June', 'month_March',
                'month_May', 'month_November', 'month_October', 'month_September',
                'origin_ATL', 'origin_CLT', 'origin_DEN', 'origin_DFW', 'origin_JFK',
                'origin_LAS', 'origin_LAX', 'origin_ORD', 'origin_SEA', 'origin_SFO']]

        df_custom_future = df4
        custom_feats = df_custom_future.iloc[:, 3:]

        gb_preds = gb_model.predict(custom_feats)
        ls_preds = ls_model.predict(custom_feats)
        rf_preds = rf_model.predict(custom_feats)
        stacking_preds = stacking_model.predict(custom_feats)

        df_custom_future['predicted_rate'] = gb_preds

        pred = True
        ddtm = df_custom_future.iloc[0]['display_dtm']
        rate = df_custom_future.iloc[0]['predicted_rate']
        precip = round(df_custom_future.iloc[0]['precip'], 3)
        temp = int(df_custom_future.iloc[0]['temp'])
        wind_speed = round(df_custom_future.iloc[0]['wind_speed'], 1)
        dewpt = int(df_custom_future.iloc[0]['dewp'])
        pres = round(df_custom_future.iloc[0]['pressure'], 1)
        wind_dir = int(df_custom_future.iloc[0]['wind_dir'])
        visib = round(df_custom_future.iloc[0]['visib'], 1)
        relh = int(df_custom_future.iloc[0]['relh'])

    # Recommendation
    minim = df_future[df_future['Airport'] == Airport]['predicted_rate'].min()
    min_rate = df_future[(df_future['predicted_rate'] == minim) & (df_future['Airport'] == Airport)].iloc[0]['predicted_rate']
    rec_date = df_future[(df_future['predicted_rate'] == minim) & (df_future['Airport'] == Airport)].iloc[0]['display_dtm']

    # Get predicted rate of all airports for specific date
    atl_rate = df_future[(df_future['Airport'] == 'ATL') & (df_future['datetime'] == Date)].iloc[0]['predicted_rate']
    lax_rate = df_future[(df_future['Airport'] == 'LAX') & (df_future['datetime'] == Date)].iloc[0]['predicted_rate']
    ord_rate = df_future[(df_future['Airport'] == 'ORD') & (df_future['datetime'] == Date)].iloc[0]['predicted_rate']
    dfw_rate = df_future[(df_future['Airport'] == 'DFW') & (df_future['datetime'] == Date)].iloc[0]['predicted_rate']
    den_rate = df_future[(df_future['Airport'] == 'DEN') & (df_future['datetime'] == Date)].iloc[0]['predicted_rate']
    jfk_rate = df_future[(df_future['Airport'] == 'JFK') & (df_future['datetime'] == Date)].iloc[0]['predicted_rate']
    sfo_rate = df_future[(df_future['Airport'] == 'SFO') & (df_future['datetime'] == Date)].iloc[0]['predicted_rate']
    las_rate = df_future[(df_future['Airport'] == 'LAS') & (df_future['datetime'] == Date)].iloc[0]['predicted_rate']
    sea_rate = df_future[(df_future['Airport'] == 'SEA') & (df_future['datetime'] == Date)].iloc[0]['predicted_rate']
    clt_rate = df_future[(df_future['Airport'] == 'CLT') & (df_future['datetime'] == Date)].iloc[0]['predicted_rate']

    # Get predicted delay rate of all dates for specific airport
    al_df = df_future[(df_future['Airport'] == Airport)]
    al_df = al_df.rename(columns = {'datetime': 'date', 'predicted_rate': 'value'})
    sp_df = al_df[['date', 'value']]
    sp_df.to_csv('static/delay.csv', sep=',', encoding='utf-8', header='true', index=False)

    return render_template('home.html',
        airport_code=Airport, airport_name=airport_name, date=Date, ddtm=ddtm, rate=rate, pred=pred,
        precip=precip, temp=temp, dewpt=dewpt, relh=relh, wind_dir=wind_dir, wind_speed=wind_speed, pres=pres, visib=visib,
        min_rate=min_rate, rec_date=rec_date,
        atl_rate=atl_rate, lax_rate=lax_rate, ord_rate=ord_rate, dfw_rate=dfw_rate, den_rate=den_rate, jfk_rate=jfk_rate, sfo_rate=sfo_rate, las_rate=las_rate, sea_rate=sea_rate, clt_rate=clt_rate)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
