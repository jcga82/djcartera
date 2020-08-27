#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  5 13:43:01 2018

@author: matthewgrierson
"""
# cd ~/Documents/github/stock_analysis

import pandas as pd
import numpy as np
import datetime
import plotly.express as px
import yfinance as yf
import pandas_market_calendars as mcal
# from plotly.offline import init_notebook_mode, plot
# init_notebook_mode(connected=True)


def create_market_cal(start, end):
    nyse = mcal.get_calendar('NYSE')
    schedule = nyse.schedule(start, end)
    market_cal = mcal.date_range(schedule, frequency='1D')
    market_cal = market_cal.tz_localize(None)
    market_cal = [i.replace(hour=0) for i in market_cal]
    return market_cal


def get_data(stocks, start, end):
    def data(ticker):
        df = yf.download(ticker, start=start, end=(end + datetime.timedelta(days=1)))
        df['symbol'] = ticker
        df.index = pd.to_datetime(df.index)
        return df
    datas = map(data, stocks)
    return(pd.concat(datas, keys=stocks, names=['Ticker', 'Date'], sort=True))


def get_benchmark(benchmark, start, end):
    benchmark = get_data(benchmark, start, end)
    benchmark = benchmark.drop(['symbol'], axis=1)
    benchmark.reset_index(inplace=True)
    return benchmark


def position_adjust(daily_positions, sale):
    stocks_with_sales = pd.DataFrame()
    buys_before_start = daily_positions[daily_positions['tipo'] == 'Compra'].sort_values(by='fecha')
    for position in buys_before_start[buys_before_start['empresa'] == sale[1]['empresa']].iterrows():
        if position[1]['acciones'] <= sale[1]['acciones']:
            sale[1]['acciones'] -= position[1]['acciones']
            position[1]['acciones'] = 0
        else:
            position[1]['acciones'] -= sale[1]['acciones']
            sale[1]['acciones'] -= sale[1]['acciones']
        stocks_with_sales = stocks_with_sales.append(position[1])
    print ('stocks_with_sales, las que quedan:', stocks_with_sales)
    return stocks_with_sales


def cartera_start_balance(portfolio, start_date):
    positions_before_start = portfolio[portfolio['fecha'].astype('datetime64[ns]') <= start_date]
    future_positions = portfolio[portfolio['fecha'].astype('datetime64[ns]') >= start_date]
    sales = positions_before_start[positions_before_start['tipo'] == 'Venta'].groupby(['empresa'])['acciones'].sum()
    sales = sales.reset_index()
    positions_no_change = positions_before_start[~positions_before_start['empresa'].isin(sales['empresa'].unique())]
    adj_positions_df = pd.DataFrame()
    # for sale in sales.iterrows():
    #     adj_positions = position_adjust(positions_before_start, sale)
    #     adj_positions_df = adj_positions_df.append(adj_positions)
    adj_positions_df = adj_positions_df.append(sales)
    adj_positions_df = adj_positions_df.append(positions_no_change)
    adj_positions_df = adj_positions_df.append(future_positions)
    #adj_positions_df = adj_positions_df[adj_positions_df['acciones'] > 0]
    return adj_positions_df

def portfolio_start_balance(portfolio, start_date):
    positions_before_start = portfolio[portfolio['fecha'].astype('datetime64[ns]') <= start_date]
    future_positions = portfolio[portfolio['fecha'].astype('datetime64[ns]') >= start_date]
    sales = positions_before_start[positions_before_start['tipo'] == 'Venta'].groupby(['empresa'])['acciones'].sum()
    sales = sales.reset_index()
    positions_no_change = positions_before_start[~positions_before_start['empresa'].isin(sales['empresa'].unique())]
    adj_positions_df = pd.DataFrame()
    for sale in sales.iterrows():
        adj_positions = position_adjust(positions_before_start, sale)
        adj_positions_df = adj_positions_df.append(adj_positions)
    adj_positions_df = adj_positions_df.append(positions_no_change)
    adj_positions_df = adj_positions_df.append(future_positions)
    adj_positions_df = adj_positions_df[adj_positions_df['acciones'] > 0]
    return adj_positions_df


def fifo(daily_positions, sales, date):
    print('entro al modeulo FIFO...')
    sales = sales[sales['fecha'].astype('datetime64[ns]') == date]
    daily_positions = daily_positions[daily_positions['fecha'].astype('datetime64[ns]') <= date]
    print('daily_positions:', daily_positions)
    positions_no_change = daily_positions[~daily_positions['empresa'].isin(sales['empresa'].unique())]
    print('positions_no_change:', positions_no_change)
    adj_positions = pd.DataFrame()
    for sale in sales.iterrows():
        adj_positions = adj_positions.append(position_adjust(daily_positions, sale))
    adj_positions = adj_positions.append(positions_no_change)
    adj_positions = adj_positions[adj_positions['acciones'] > 0]
    return adj_positions


def time_fill(portfolio, market_cal):
    sales = portfolio[portfolio['tipo'] == 'Venta'].groupby(['empresa','fecha'])['acciones'].sum()
    sales = sales.reset_index()
    print("Las ventas son:", sales)
    per_day_balance = []
    for date in market_cal:
        if (sales['fecha'].astype('datetime64[ns]') == date).any():
            print('entro al if en el date:', date)
            portfolio = fifo(portfolio, sales, date)
        daily_positions = portfolio[portfolio['fecha'].astype('datetime64[ns]') <= date]
        daily_positions = daily_positions[daily_positions['tipo'] == 'Compra']
        daily_positions['Date Snapshot'] = date
        per_day_balance.append(daily_positions)
    return per_day_balance


# matches prices of each asset to open date, then adjusts for  cps of dates
def modified_cost_per_share(portfolio, adj_close, start_date):
    df = pd.merge(portfolio, adj_close, left_on=['Date Snapshot', 'empresa'],
                  right_on=['Date', 'Ticker'], how='left')
    df.rename(columns={'Close': 'Symbol Adj Close'}, inplace=True)
    df['Adj cost daily'] = df['Symbol Adj Close'] * df['acciones']
    df = df.drop(['Ticker', 'Date'], axis=1)
    return df


# merge portfolio data with latest benchmark data and create several calcs
def benchmark_portfolio_calcs(portfolio, benchmark):
    portfolio = pd.merge(portfolio, benchmark, left_on=['Date Snapshot'],
                         right_on=['Date'], how='left')
    portfolio = portfolio.drop(['Date'], axis=1)
    portfolio.rename(columns={'Close': 'Benchmark Close'}, inplace=True)
    benchmark_max = benchmark[benchmark['Date'] == benchmark['Date'].max()]
    portfolio['Benchmark End Date Close'] = portfolio.apply(lambda x: benchmark_max['Close'], axis=1)
    benchmark_min = benchmark[benchmark['Date'] == benchmark['Date'].min()]
    portfolio['Benchmark Start Date Close'] = portfolio.apply(lambda x: benchmark_min['Close'], axis=1)
    return portfolio


def portfolio_end_of_year_stats(portfolio, adj_close_end):
    adj_close_end = adj_close_end[adj_close_end['Date'] == adj_close_end['Date'].max()]
    portfolio_end_data = pd.merge(portfolio, adj_close_end, left_on='empresa',
                                  right_on='Ticker')
    portfolio_end_data.rename(columns={'Close': 'Ticker End Date Close'}, inplace=True)
    portfolio_end_data = portfolio_end_data.drop(['Ticker', 'Date'], axis=1)
    return portfolio_end_data


# Merge the overall dataframe with the adj close start of year dataframe for YTD tracking of tickers.
def portfolio_start_of_year_stats(portfolio, adj_close_start):
    print('adj_close_start:', portfolio)
    adj_close_start = adj_close_start[adj_close_start['Date'] == adj_close_start['Date'].min()]
    portfolio_start = pd.merge(portfolio, adj_close_start[['Ticker', 'Close', 'Date']],
                                    left_on='empresa', right_on='Ticker')
    portfolio_start.rename(columns={'Close': 'Ticker Start Date Close'}, inplace=True)
    portfolio_start['Adj cost per share'] = np.where(portfolio_start['fecha'].astype('datetime64[ns]') <= portfolio_start['Date'],
                                                          portfolio_start['Ticker Start Date Close'],
                                                          portfolio_start['Adj cost daily'])#per share DA ERROR
    portfolio_start['Adj cost'] = portfolio_start['Adj cost per share'] * portfolio_start['acciones']
    portfolio_start = portfolio_start.drop(['Ticker', 'Date'], axis=1)
    portfolio_start['Equiv Benchmark Shares'] = portfolio_start['Adj cost'] / portfolio_start['Benchmark Start Date Close']
    portfolio_start['Benchmark Start Date Cost'] = portfolio_start['Equiv Benchmark Shares'] * portfolio_start['Benchmark Start Date Close']
    return portfolio_start


def calc_returns(portfolio):
    portfolio['Benchmark Return'] = portfolio['Benchmark Close'] / portfolio['Benchmark Start Date Close'] - 1
    portfolio['Ticker Return'] = portfolio['Symbol Adj Close'] / portfolio['Adj cost per share'] - 1
    portfolio['Ticker Share Value'] = portfolio['acciones'] * portfolio['Symbol Adj Close']
    portfolio['Benchmark Share Value'] = portfolio['Equiv Benchmark Shares'] * portfolio['Benchmark Close']
    portfolio['Stock Gain / (Loss)'] = portfolio['Ticker Share Value'] - portfolio['Adj cost']
    portfolio['Benchmark Gain / (Loss)'] = portfolio['Benchmark Share Value'] - portfolio['Adj cost']
    portfolio['Abs Value Compare'] = portfolio['Ticker Share Value'] - portfolio['Benchmark Start Date Cost']
    portfolio['Abs Value Return'] = portfolio['Abs Value Compare']/portfolio['Benchmark Start Date Cost']
    portfolio['Abs. Return Compare'] = portfolio['Ticker Return'] - portfolio['Benchmark Return']
    return portfolio


def per_day_portfolio_calcs(per_day_holdings, daily_benchmark, daily_adj_close, stocks_start):
    df = pd.concat(per_day_holdings, sort=True)
    mcps = modified_cost_per_share(df, daily_adj_close, stocks_start)
    #print('modified_cost_per_share:', mcps)
    bpc = benchmark_portfolio_calcs(mcps, daily_benchmark)
    #print('benchmark_portfolio_calcs:', bpc)
    pes = portfolio_end_of_year_stats(bpc, daily_adj_close)
    print('portfolio_end_of_year_stats:', pes)
    pss = portfolio_start_of_year_stats(pes, daily_adj_close)
    # except:
    #     pss = pd.DataFrame()
    #     print("Hay un problema al calcular el pss")
    print('portfolio_start_of_year_stats:', pss)
    try:
        returns = calc_returns(pss)
    except:
        returns = pd.DataFrame()

    return returns


def line_facets(df, val_1, val_2):
    grouped_metrics = combined_df.groupby(['Symbol','Date Snapshot'])[[val_1,val_2]].sum().reset_index()
    grouped_metrics = pd.melt(grouped_metrics, id_vars=['Symbol','Date Snapshot'],
                              value_vars=[val_1, val_2])
    fig = px.line(grouped_metrics, x="Date Snapshot", y="value",
                  color='variable', facet_col="Symbol", facet_col_wrap=5)
    plot(fig)


def line(df, val_1, val_2):
    grouped_metrics = combined_df.groupby(['Date Snapshot'])[[val_1,val_2]].sum().reset_index()
    grouped_metrics = pd.melt(grouped_metrics, id_vars=['Date Snapshot'],
                              value_vars=[val_1, val_2])
    fig = px.line(grouped_metrics, x="Date Snapshot", y="value", 
                  color='variable')
    plot(fig)




# line_facets(combined_df, 'Ticker Return', 'Benchmark Return')
# line(combined_df, 'Stock Gain / (Loss)', 'Benchmark Gain / (Loss)')
