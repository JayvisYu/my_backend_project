# -*- coding:utf-8 -*-
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import OAuth2PasswordRequestForm
from utils.decorators import login_require
from sqlalchemy.orm import Session
from models.tactic import *
from db.set_db import create_session as create_tactic_session
from db.set_redis import r, pool
from starlette.requests import Request
from typing import Optional, List
from pydantic import BaseModel, constr, Field
from datetime import timedelta
import tushare as ts
import numpy as np
import pandas as pd
import json

stock_router = APIRouter()


# 获取选股风险分析表
@stock_router.get('/get_stock_risk_analysis_data', summary='获取选股风险分析表')
@login_require
async def get_stock_risk_analysis_data(request: Request, tactic_name: str, select_num: int, select_circle: str):
    session = create_tactic_session()
    tactic_data_query = session.query(Tactic).filter_by(tactic_name=tactic_name, select_num=select_num,
                                                        select_circle=select_circle).order_by(
        -Tactic.tactic_save_time).first()
    tactic_id = tactic_data_query.id
    comments_data_query = session.query(SelectStockComments).filter_by(tactic_id=tactic_id).order_by(
        -SelectStockComments.comments_save_time).first()
    if comments_data_query:
        comments_dict = dict()
        comments_dict['accumulated_net'] = comments_data_query.accumulated_net  # 累计净值
        comments_dict['max_return'] = comments_data_query.max_return  # 最大收益
        comments_dict['annualized_yield'] = comments_data_query.annualized_yield  # 年化收益率
        comments_dict['max_drawdown'] = comments_data_query.max_drawdown  # 最大回撤
        comments_dict[
            'annualized_yield_drawdown_ratio'] = comments_data_query.annualized_yield_drawdown_ratio  # 年化收益回撤比
        comments_dict['drawdown_start_time'] = comments_data_query.drawdown_start_time  # 最大回撤开始时间
        comments_dict['drawdown_end_time'] = comments_data_query.drawdown_end_time  # 最大回撤结束时间
        comments_dict['average_range'] = comments_data_query.average_range  # 平均涨幅
        comments_dict['profit_times'] = comments_data_query.profit_times  # 盈利次数
        comments_dict['loss_times'] = comments_data_query.loss_times  # 亏损次数
        comments_dict['win_rate'] = comments_data_query.win_rate  # 胜率
        comments_dict['max_continuous_rise_days'] = comments_data_query.max_continuous_rise_days  # 最大连续上涨天数
        comments_dict['max_continuous_down_days'] = comments_data_query.max_continuous_down_days  # 最大连续下跌天数
        comments_dict['max_single_circle_rise_range'] = comments_data_query.max_single_circle_rise_range  # 最大单周期涨幅
        comments_dict['max_single_circle_down_range'] = comments_data_query.max_single_circle_down_range  # 最大单周期跌幅
        comments_dict['profit_volatility'] = comments_data_query.profit_volatility  # 收益波动率
        comments_dict['base_accumulated_net'] = comments_data_query.base_accumulated_net  # 基准累计净值
        comments_dict['base_annualized_yield'] = comments_data_query.base_annualized_yield  # 基准年化收益率
        comments_dict['alpha'] = comments_data_query.alpha  # alpha
        comments_dict['beta'] = comments_data_query.beta  # beta
        comments_dict['sharp_ratio'] = comments_data_query.sharp_ratio  # 夏普比率
        comments_dict['treynor_ratio'] = comments_data_query.treynor_ratio  # 特雷诺比率
        comments_dict['inf_ratio'] = comments_data_query.inf_ratio  # 信息比率
        session.close()
        return {'code': 200, 'data': {'comments_dict': comments_dict}}
    else:
        session.close()
        return {'code': 401, 'data': {'comments_dict': {}}}


# 获取选股资金曲线/最大回撤表
@stock_router.get('/get_stock_curve_chart_data', summary='获取选股资金曲线/最大回撤表')
@login_require
async def get_stock_curve_chart_data(request: Request, tactic_name: str, select_num: int, select_circle: str):
    session = create_tactic_session()
    tactic_data_query = session.query(Tactic).filter_by(tactic_name=tactic_name, select_num=select_num,
                                                        select_circle=select_circle).order_by(
        -Tactic.tactic_save_time).first()
    tactic_id = tactic_data_query.id
    curve_data_query = session.query(Curve).filter_by(tactic_id=tactic_id).order_by(
        -Curve.curve_save_time).first()
    if curve_data_query:
        curve_dict = dict()
        curve_dict['curve_date'] = json.loads(curve_data_query.curve_date)  # 策略资金曲线
        curve_dict['tactic_curve'] = json.loads(curve_data_query.tactic_curve)  # 策略资金曲线
        curve_dict['tactic_max_drawdown'] = json.loads(curve_data_query.tactic_max_drawdown)  # 策略最大回撤曲线
        curve_dict['index_curve'] = json.loads(curve_data_query.index_curve)  # 指数资金曲线
        curve_dict['index_max_drawdown'] = json.loads(curve_data_query.index_max_drawdown)  # 指数最大回撤曲线
        session.close()
        return {'code': 200, 'data': {'curve_dict': curve_dict}}
    else:
        session.close()
        return {'code': 401, 'data': {'curve_dict': {}}}


# 获取选股历年收益表
@stock_router.get('/get_stock_year_profit_data', summary='获取选股历年收益表')
@login_require
async def get_stock_year_profit_data(request: Request, tactic_name: str, select_num: int, select_circle: str):
    session = create_tactic_session()
    tactic_data_query = session.query(Tactic).filter_by(tactic_name=tactic_name, select_num=select_num,
                                                        select_circle=select_circle).order_by(
        -Tactic.tactic_save_time).first()
    tactic_id = tactic_data_query.id
    year_profit_data_query = session.query(YearProfit).filter_by(tactic_id=tactic_id).order_by(
        -YearProfit.year_profit_save_time).first()
    if year_profit_data_query:
        year_profit_dict = {}
        year_list = ['2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018',
                     '2019', '2020', '2021']
        year_profit_dict['year_data'] = year_list
        tactic_year_profit_list = json.loads(year_profit_data_query.tactic_year_profit)
        for i in range(len(tactic_year_profit_list)):
            tactic_year_profit_list[i] *= 100
        tactic_year_profit_list_np = np.array(tactic_year_profit_list)  # 列表转数组
        tactic_year_profit_list_np = np.round(tactic_year_profit_list_np, 2)  # 对数组中的元素保留两位小数
        tactic_year_profit_list = list(tactic_year_profit_list_np)  # 数组转列表

        index_year_profit_list = json.loads(year_profit_data_query.index_year_profit)
        for i in range(len(index_year_profit_list)):
            index_year_profit_list[i] *= 100
        index_year_profit_list_np = np.array(index_year_profit_list)  # 列表转数组
        index_year_profit_list_np = np.round(index_year_profit_list_np, 2)  # 对数组中的元素保留两位小数
        index_year_profit_list = list(index_year_profit_list_np)  # 数组转列表
        year_profit_dict['tactic_year_profit'] = tactic_year_profit_list
        year_profit_dict['index_year_profit'] = index_year_profit_list
        session.close()
        return {'code': 200, 'data': {'year_profit_dict': year_profit_dict}}
    else:
        session.close()
        return {'code': 401, 'data': {'year_profit_dict': {}}}


# 获取最新选股数据
@stock_router.get('/get_last_select_data', summary='获取最新选股数据')
@login_require
async def get_year_profit_data(request: Request, tactic_name: str, select_num: int, select_circle: str):
    buy_date = ''
    next_select_date = ''
    session = create_tactic_session()
    tactic_data_query = session.query(Tactic).filter_by(
        tactic_name=tactic_name, select_num=select_num, select_circle=select_circle).order_by(
        -Tactic.tactic_save_time).first()
    tactic_id = tactic_data_query.id
    last_select_data_query = session.query(NextStocks).filter_by(tactic_id=tactic_id).order_by(
        -NextStocks.next_stocks_save_time).first()
    if last_select_data_query:
        select_stocks_code = json.loads(last_select_data_query.select_stocks_code)
        select_stocks_name = json.loads(last_select_data_query.select_stocks_name)
        session.close()
        pro = ts.pro_api('3dfbaa2d3278ecce1409b7c058fb392ece8c3ea26cbdc08dd40a7b4c')
        start_date = datetime.now().strftime("%Y%m%d")
        end_date = (datetime.now() + timedelta(30)).strftime("%Y%m%d")
        res = pro.trade_cal(exchange='SSE', start_date=start_date, end_date=end_date)
        res['cal_date'] = pd.to_datetime(res['cal_date'], format='%Y-%m-%d')
        for i, row_i in res.iterrows():
            if res.iloc[i]['is_open'] == 1 and res.iloc[i - 1]['is_open'] == 0:
                buy_date = row_i['cal_date'].strftime("%Y-%m-%d")
                break
        res_new = res[res['cal_date'] >= buy_date]
        res_new.reset_index(inplace=True, drop=True)
        for j, row_j in res_new.iterrows():
            if res_new.iloc[j]['is_open'] == 1 and res_new.iloc[j + 1]['is_open'] == 0:
                next_select_date = row_j['cal_date'].strftime("%Y-%m-%d")
                break
        print(buy_date, next_select_date)
        return {'code': 200,
                'data': {'select_stocks_code': select_stocks_code, 'select_stocks_name': select_stocks_name,
                         'buy_date': buy_date, 'next_select_date': next_select_date}}
    else:
        session.close()
        return {'code': 401,
                'data': {'select_stocks_code': [], 'select_stocks_name': [], 'buy_date': buy_date,
                         'next_select_date': next_select_date}}


# 获取历史选股数据
@stock_router.get('/get_his_result_data', summary='获取历史选股数据')
@login_require
async def get_his_result_data(request: Request, tactic_name: str, select_num: int, select_circle: str):
    session = create_tactic_session()
    tactic_data_query = session.query(Tactic).filter_by(tactic_name=tactic_name, select_num=select_num,
                                                        select_circle=select_circle).order_by(
        -Tactic.tactic_save_time).first()
    if tactic_data_query:
        tactic_id = tactic_data_query.id
        his_result_data_query = session.query(Result).filter_by(tactic_id=tactic_id).order_by(
            -Result.result_save_time).first()
        selected_stocks_result = json.loads(his_result_data_query.selected_stocks_result)
        session.close()
        return {'code': 200, 'data': {'selected_stocks_result': selected_stocks_result}}
    else:
        session.close()
        return {'code': 401, 'data': {'selected_stocks_result': {}}}


# 获取每日收益数据
@stock_router.get('/get_daily_profit_data', summary='获取每日收益数据')
@login_require
async def get_daily_profit_data(request: Request, tactic_name: str, select_num: int, select_circle: str):
    session = create_tactic_session()
    tactic_data_query = session.query(Tactic).filter_by(tactic_name=tactic_name, select_num=select_num,
                                                        select_circle=select_circle).order_by(
        -Tactic.tactic_save_time).first()
    tactic_id = tactic_data_query.id
    daily_profit_data_query = session.query(DailyProfit).filter_by(tactic_id=tactic_id).order_by(
        -DailyProfit.daily_profit_save_time).first()
    if daily_profit_data_query:
        daily_profit_list = json.loads(daily_profit_data_query.daily_profit)
        session.close()
        return {'code': 200, 'data': {'daily_profit_list': daily_profit_list}}
    else:
        session.close()
        return {'code': 401, 'data': {'daily_profit_list': []}}


# 获取稳健性分析数据
@stock_router.get('/get_robustness_result_data', summary='获取稳健性分析数据')
@login_require
async def get_his_result_data(request: Request, tactic_name: str, select_num: int, select_circle: str):
    session = create_tactic_session()
    tactic_data_query = session.query(Tactic).filter_by(
        tactic_name=tactic_name, select_num=select_num, select_circle=select_circle).order_by(
        -Tactic.tactic_save_time).first()
    if tactic_data_query:
        tactic_id = tactic_data_query.id
        robustness_result_data_query = session.query(Robustness).filter_by(tactic_id=tactic_id).order_by(
            -Robustness.robustness_save_time).first()
        if robustness_result_data_query:
            robustness_result = json.loads(robustness_result_data_query.tactic_perform)
            session.close()
            return {'code': 200, 'data': {'robustness_result': robustness_result}}
    session.close()
    return {'code': 401, 'data': {'robustness_result': {}}}


# 获取择时风险分析表
@stock_router.get('/get_timing_risk_analysis_data', summary='获取择时风险分析表')
@login_require
async def get_timing_risk_analysis_data(request: Request, tactic_name: str):
    session = create_tactic_session()
    tactic_data_query = session.query(Tactic).filter_by(tactic_name=tactic_name).order_by(
        -Tactic.tactic_save_time).first()
    tactic_id = tactic_data_query.id
    comments_data_query = session.query(TimingComments).filter_by(tactic_id=tactic_id).order_by(
        -TimingComments.comments_save_time).first()
    if comments_data_query:
        comments_dict = dict()
        comments_dict['accumulated_net'] = comments_data_query.accumulated_net  # 累计净值
        comments_dict['annualized_yield'] = comments_data_query.annualized_yield  # 年化收益率
        comments_dict['max_drawdown'] = comments_data_query.max_drawdown  # 最大回撤
        comments_dict[
            'annualized_yield_drawdown_ratio'] = comments_data_query.annualized_yield_drawdown_ratio  # 年化收益回撤比
        comments_dict['drawdown_start_time'] = comments_data_query.drawdown_start_time  # 最大回撤开始时间
        comments_dict['drawdown_end_time'] = comments_data_query.drawdown_end_time  # 最大回撤结束时间
        comments_dict['average_range'] = comments_data_query.average_range  # 平均涨幅
        comments_dict['profit_loss_ratio'] = comments_data_query.profit_loss_ratio  # 盈亏收益比
        comments_dict['profit_times'] = comments_data_query.profit_times  # 盈利次数
        comments_dict['loss_times'] = comments_data_query.loss_times  # 亏损次数
        comments_dict['win_rate'] = comments_data_query.win_rate  # 胜率
        comments_dict['max_continuous_rise_days'] = comments_data_query.max_continuous_rise_days  # 最大连续上涨天数
        comments_dict['max_continuous_down_days'] = comments_data_query.max_continuous_down_days  # 最大连续下跌天数
        comments_dict['max_single_circle_rise_range'] = comments_data_query.max_single_circle_rise_range  # 最大单周期涨幅
        comments_dict['max_single_circle_down_range'] = comments_data_query.max_single_circle_down_range  # 最大单周期跌幅
        comments_dict['max_holding_duration'] = comments_data_query.max_holding_duration  # 单笔最长持有时间
        comments_dict['min_holding_duration'] = comments_data_query.min_holding_duration  # 单笔最短持有时间
        comments_dict['average_holding_duration'] = comments_data_query.average_holding_duration  # 单笔最短持有时间
        session.close()
        return {'code': 200, 'data': {'comments_dict': comments_dict}}
    else:
        session.close()
        return {'code': 401, 'data': {'comments_dict': {}}}


# 获取择时资金曲线/最大回撤表
@stock_router.get('/get_timing_curve_chart_data', summary='获取择时资金曲线/最大回撤表')
@login_require
async def get_timing_curve_chart_data(request: Request, tactic_name: str):
    session = create_tactic_session()
    tactic_data_query = session.query(Tactic).filter_by(tactic_name=tactic_name).order_by(
        -Tactic.tactic_save_time).first()
    tactic_id = tactic_data_query.id
    curve_data_query = session.query(Curve).filter_by(tactic_id=tactic_id).order_by(
        -Curve.curve_save_time).first()
    if curve_data_query:
        curve_dict = dict()
        curve_dict['curve_date'] = json.loads(curve_data_query.curve_date)  # 策略资金曲线
        curve_dict['tactic_curve'] = json.loads(curve_data_query.tactic_curve)  # 策略资金曲线
        curve_dict['tactic_max_drawdown'] = json.loads(curve_data_query.tactic_max_drawdown)  # 策略最大回撤曲线
        curve_dict['index_curve'] = json.loads(curve_data_query.index_curve)  # 指数资金曲线
        curve_dict['index_max_drawdown'] = json.loads(curve_data_query.index_max_drawdown)  # 指数最大回撤曲线
        session.close()
        return {'code': 200, 'data': {'curve_dict': curve_dict}}
    else:
        session.close()
        return {'code': 401, 'data': {'curve_dict': {}}}


# 获取择时历年收益表
@stock_router.get('/get_timing_year_profit_data', summary='获取择时历年收益表')
@login_require
async def get_timing_year_profit_data(request: Request, tactic_name: str):
    session = create_tactic_session()
    tactic_data_query = session.query(Tactic).filter_by(tactic_name=tactic_name).order_by(
        -Tactic.tactic_save_time).first()
    tactic_id = tactic_data_query.id
    year_profit_data_query = session.query(YearProfit).filter_by(tactic_id=tactic_id).order_by(
        -YearProfit.year_profit_save_time).first()
    if year_profit_data_query:
        year_profit_dict = {}
        year_list = ['2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018',
                     '2019', '2020', '2021']
        year_profit_dict['year_data'] = year_list
        tactic_year_profit_list = json.loads(year_profit_data_query.tactic_year_profit)
        for i in range(len(tactic_year_profit_list)):
            tactic_year_profit_list[i] *= 100
        tactic_year_profit_list_np = np.array(tactic_year_profit_list)  # 列表转数组
        tactic_year_profit_list_np = np.round(tactic_year_profit_list_np, 2)  # 对数组中的元素保留两位小数
        tactic_year_profit_list = list(tactic_year_profit_list_np)  # 数组转列表

        index_year_profit_list = json.loads(year_profit_data_query.index_year_profit)
        for i in range(len(index_year_profit_list)):
            index_year_profit_list[i] *= 100
        index_year_profit_list_np = np.array(index_year_profit_list)  # 列表转数组
        index_year_profit_list_np = np.round(index_year_profit_list_np, 2)  # 对数组中的元素保留两位小数
        index_year_profit_list = list(index_year_profit_list_np)  # 数组转列表
        year_profit_dict['tactic_year_profit'] = tactic_year_profit_list
        year_profit_dict['index_year_profit'] = index_year_profit_list
        session.close()
        return {'code': 200, 'data': {'year_profit_dict': year_profit_dict}}
    else:
        session.close()
        return {'code': 401, 'data': {'year_profit_dict': {}}}


# 获取择时html数据
@stock_router.get('/get_timing_kline_data', summary='获取择时开平仓图')
@login_require
async def get_timing_kline_data(request: Request, tactic_name: str):
    df = pd.read_csv('/Users/jarvisyu/05_hobbies/Jarvis_Admin/backend/app/backtest/stock/data/' + tactic_name + '.csv')
    df['equity_change_new'] = df['equity_change'].shift(-1)
    df = df[['candle_begin_time', 'open', 'high', 'low', 'close', 'volume', 'signal', 'equity_change_new']]
    df['last_signal'] = df['signal'].copy()
    df['last_signal'].fillna(method='ffill', inplace=True)
    # 获取最新信号
    last_signal = int(df['last_signal'].to_list()[-1])
    date_list = df['candle_begin_time'].to_list()
    open_list = df['open'].to_list()
    high_list = df['high'].to_list()
    low_list = df['low'].to_list()
    close_list = df['close'].to_list()
    volume_list = df['volume'].to_list()
    df.dropna(inplace=True, axis=0)
    print('last_signal', last_signal)
    value_list = []
    for i, v in enumerate(open_list):
        temp_list = [open_list[i], close_list[i], low_list[i], high_list[i]]
        value_list.append(temp_list)
        if close_list[i] > open_list[i]:
            volume_list[i] = [i, volume_list[i], 1]
        else:
            volume_list[i] = [i, volume_list[i], -1]
    color = {
        1: '#91cc75',
        -1: '#fac858',
        0: '#5470c6',
    }
    # 有信号的时间之list
    # 有信号的最高价之list，标记在最高价才不会挡到K线
    signal_list = []
    for x_coord, y_coord, signal, equity_change in df[
        ['candle_begin_time', 'high', 'signal', 'equity_change_new']].values:
        word = {
            1: '做多' + '%.2f' % equity_change + '%',
            -1: '做空' + '%.2f' % equity_change + '%',
            0: '平仓',
        }
        temp_dict = {'coord': [x_coord, y_coord, word[signal]],
                     'itemStyle': {'color': color[signal]}}
        signal_list.append(temp_dict)
    k_line_dict = {
        'categoryData': date_list,
        'values': value_list,
        'signal_list': signal_list,
        'volume_list': volume_list,
        'last_signal': last_signal
    }

    return {'code': 200, 'data': {'k_line_dict': k_line_dict}}


if __name__ == '__main__':
    pro = ts.pro_api('3dfbaa2d3278ecce1409b7c058fb392ece8c3ea26cbdc08dd40a7b4c')
    res = pro.trade_cal(exchange='', start_date='20170712', end_date='20201031')
    print(res)
    count = 0
    for i, row in res.iterrows():
        if row['is_open'] == 1:
            count += 1
    print(count * 48)
