import os
import time
import requests
import pandas as pd
from threading import Thread


def make_iex_request(ticker):
    secret = 'pk_67d5d7a56fc24695af98664bc4615baf'
    secret = 'Tsk_3ef155ee4c5b43a7827db0e06bffca34'
    #ticker = 'aapl'
    response = requests.get("https://sandbox.iexapis.com/stable/stock/{}/batch?types=quote&token={}".format(ticker, secret))  #"https://cloud.iexapis.com/stable/stock/AAPL/batch?types=&token={}".format(ticker, secret))
    return response


def get_position_updates(position, max_retries=10, retry_after=1):
    """Gets metric updates from IEX API for a single Position object"""

    ticker = position['empresa'] #empresa__symbol
    response = make_iex_request(ticker)
    status_code = response.status_code

    while status_code == 429 and max_retries:
        time.sleep(retry_after)
        response = make_iex_request(ticker)
        status_code = response.status_code
        max_retries -= 1
        retry_after += 1

    if status_code != 200:
        raise Exception(f"IEX api failed with with status code: {status_code}")

    data = response.json()

    print(data['quote'])

    # parse price data
    price = data['quote']['latestPrice']
    change = data['quote']['change']
    pct_change = 100. * (data['quote']['changePercent'] or 0.00)

    record = {
        "Name": position['empresa'],
        "Symbol": ticker,
        "Shares": position['total_acciones'],
        "Cost Basis ($)": position['coste_operacion'],
        "Last Price ($)": price,
        "Day's Change ($)": change,
        "Day's Change (%)": pct_change,
        # "Account": position.cartera.nombre
    }

    return record


def process_range(pos_range, store=None):
    """Process a number of positions, storing the results in a list"""
    if store is None:
        store = []
    for p in pos_range:
        store.append(get_position_updates(p))
    return store


def get_positions_dataframe(positions, nthreads=10):
    """
    Constructs updated dataframe for a list of Position objects
    using threaded requests to IEX API
    """

    store = []
    threads = []

    # create the threads
    for i in range(nthreads):
        pos_range = positions[i::nthreads]
        t = Thread(target=process_range, args=(pos_range, store))
        threads.append(t)

    # start the threads
    [t.start() for t in threads]

    # wait for the threads to finish
    [t.join() for t in threads]

    return pd.DataFrame(store)


def get_totals(df):
    """Creates a totals row as a dataframe"""

    totals_df = pd.DataFrame({
        "Name": "Totals",
        "Adj cost": df["Adj cost"].sum(),
        # "Day's Change (%)": (100. * df["Day's Gain/Loss ($)"].sum() / df["Market Value ($)"].sum()),
        "Market Value ($)": df["Market Value ($)"].sum(),
        # "Day's Gain/Loss ($)": df["Day's Gain/Loss ($)"].sum(),
        "Account": ""
    }, index=[0])

    return totals_df


def format_positions_summary(df):
    """Formats report for final display"""

    # rounding
    df["Day's Change ($)"] = df["Day's Change ($)"].astype(float).round(2)
    df["Day's Change (%)"] = df["Day's Change (%)"].astype(float).round(2)
    df["Market Value ($)"] = df["Market Value ($)"].astype(float).round(2)
    df["Day's Gain/Loss ($)"] = df["Day's Gain/Loss ($)"].astype(float).round(2)
    df["Adj cost"] = df["Adj cost"].astype(float).round(2)

    # sort by largest position and fill null values with empty string (b/c I like it that way)
    df.sort_values("Market Value ($)", inplace=True, ascending=False)
    df.fillna("", inplace=True)

    return df


def get_valor_cartera_total_diaria(positions):

    cols = ["Date Snapshot", "Market Value ($)", "Cash (€)", "Total (€)", "Day's Change ($)", "Day's Change (%)",
            "Day's Gain/Loss ($)", "Adj cost", "Total Gain/Loss ($)", "Overall Return (%)", "Account"]
    df = positions
    df["Market Value ($)"] = df["acciones"] * df["Symbol Adj Close"]
    df = df.groupby(['Date Snapshot'], as_index=False).sum()
    # valores_cartera = len(df)
    # print("Hay estos valores:", valores_cartera)
    df = format_positions_summary(df.loc[:, cols])

    return df


def get_position_summary(positions):
    """Builds and formats summary of positions for given Position object input"""

    # columns to return
    cols = ["Date Snapshot", "empresa", "acciones", "Symbol Adj Close", "Market Value ($)", "Day's Change ($)", "Day's Change (%)",
            "Day's Gain/Loss ($)", "Adj cost", "Total Gain/Loss ($)", "Overall Return (%)", "Account"]

    df = positions
    df["Market Value ($)"] = df["acciones"] * df["Symbol Adj Close"]

    #df = get_positions_dataframe(positions, nthreads=10)
    df = df.groupby(['Date Snapshot', 'empresa'], as_index=False)['acciones', 'Symbol Adj Close', 'Market Value ($)'].sum()#['Symbol Adj Close', 'acciones'].sum() #.agg({'acciones':'sum'}).agg({'Symbol Adj Close':'sum'}).reset_index() 
    
    #['acciones'].sum().reset_index() #['Symbol Adj Close', 'acciones','Date Snapshot', 'empresa'].mean().add_suffix('_sum')
    #df = df_series.to_frame()
    print('este:', df)

    # df["Fecha"] = df.groupby('Date Snapshot')
    #df["Nombre"] = df['empresa']


    # derived values needed before adding totals row
    
    # df["Day's Gain/Loss ($)"] = df["acciones"] * df["Day's Change ($)"]

    # create and append totals row
    # totals_df = get_totals(df)
    # df = df.append(totals_df, ignore_index=True)

    # derived values needed after adding totals row
    # Si ya no tengo acciones aqui quiero que aparezca la gancia o perdida
    # print("ESTOOOO Hay X acciones con 0:")
    # print(df['acciones'].isnull().sum().sum())
    # df.loc[df['acciones'].isnull(),'value_is_NaN'] = 'Yes'
    # if (df['Shares'].isnull().any()):
    #     print("Vamos")
    #     df["Total Gain/Loss ($)"] = (df["Market Value ($)"] - df["Cost Basis ($)"]).astype(float).round(2)
    # else:
    #     df["Total Gain/Loss ($)"] = (df["Cost Basis ($)"]).astype(float).round(2)
    
    
    # df["Total Gain/Loss ($)"] = (df["Market Value ($)"] - df["Cost Basis ($)"]).astype(float).round(2)
    # df["Overall Return (%)"] = (100. * df["Total Gain/Loss ($)"] / df["Cost Basis ($)"]).astype(float).round(2)

    # final formatting
    df = format_positions_summary(df.loc[:, cols])

    return df
