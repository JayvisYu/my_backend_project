# -*- coding:utf-8 -*-
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from db.set_db import create_engine, DB_URI
from datetime import datetime

Base = declarative_base()


def init_article_db():
    engine = create_engine(DB_URI, echo=False)
    Base.metadata.create_all(engine)


def drop_article_db():
    engine = create_engine(DB_URI, echo=False)
    Base.metadata.drop_all(engine)


# 策略表
class Tactic(Base):
    __tablename__ = 'tactic'
    id = Column(Integer, primary_key=True)
    tactic_name = Column(String(64))  # 策略英文名称
    tactic_name_cn = Column(String(64))  # 策略中文名称
    select_num = Column(Integer)  # 选择数量
    select_circle = Column(String(16))  # 选择周期
    para = Column(String(64))  # 策略参数
    tactic_type = Column(String(64))  # 策略类型
    tactic_importance = Column(Integer)  # 策略评级 1, 2, 3, (4, 5)
    tactic_introduction = Column(Text)  # 策略介绍
    tactic_save_time = Column(DateTime, default=datetime.now())  # 保存时间
    deleted = Column(Integer, default=0)


# 选股策略评价表
class SelectStockComments(Base):
    __tablename__ = 'select_stock_comments'
    id = Column(Integer, primary_key=True)
    tactic_id = Column(Integer, index=True)  # 关联策略表
    accumulated_net = Column(String(64))  # 累计净值
    max_return = Column(String(64))  # 最大收益
    annualized_yield = Column(String(64))  # 年化收益率
    max_drawdown = Column(String(64))  # 最大回撤
    annualized_yield_drawdown_ratio = Column(String(64))  # 年化收益回撤比
    drawdown_start_time = Column(DateTime)  # 最大回撤开始时间
    drawdown_end_time = Column(DateTime)  # 最大回撤结束时间
    average_range = Column(String(64))  # 平均涨幅
    profit_times = Column(Integer)  # 盈利次数
    loss_times = Column(Integer)  # 亏损次数
    win_rate = Column(String(64))  # 胜率
    max_continuous_rise_days = Column(Integer)  # 最大连续上涨天数
    max_continuous_down_days = Column(Integer)  # 最大连续下跌天数
    max_single_circle_rise_range = Column(String(64))  # 最大单周期涨幅
    max_single_circle_down_range = Column(String(64))  # 最大单周期跌幅
    profit_volatility = Column(String(64))  # 收益波动率
    base_accumulated_net = Column(String(64))  # 基准累计净值
    base_annualized_yield = Column(String(64))  # 基准年化收益率
    alpha = Column(String(64))  # alpha
    beta = Column(String(64))  # beta
    sharp_ratio = Column(String(64))  # 夏普比率
    treynor_ratio = Column(String(64))  # 特雷诺比率
    inf_ratio = Column(String(64))  # 信息比率
    comments_save_time = Column(DateTime, default=datetime.now())  # 保存时间
    deleted = Column(Integer, default=0)


# 资金曲线&最大回撤表
class Curve(Base):
    __tablename__ = 'curve'
    id = Column(Integer, primary_key=True)
    tactic_id = Column(Integer, index=True)  # 关联策略表
    curve_date = Column(LONGTEXT)  # 策略时间周期
    tactic_curve = Column(LONGTEXT)  # 策略资金曲线
    tactic_max_drawdown = Column(LONGTEXT)  # 策略最大回撤曲线
    index_curve = Column(LONGTEXT)  # 指数资金曲线
    index_max_drawdown = Column(LONGTEXT)  # 指数最大回撤曲线
    curve_save_time = Column(DateTime, default=datetime.now())  # 保存时间
    deleted = Column(Integer, default=0)


# 每年收益情况表
class YearProfit(Base):
    __tablename__ = 'year_profit'
    id = Column(Integer, primary_key=True)
    tactic_id = Column(Integer, index=True)  # 关联策略表
    tactic_year_profit = Column(Text)  # 策略历年收益
    index_year_profit = Column(Text)  # 基准历年收益
    year_profit_save_time = Column(DateTime, default=datetime.now())  # 保存时间
    deleted = Column(Integer, default=0)


# 稳健性分析表
class Robustness(Base):
    __tablename__ = 'robustness'
    id = Column(Integer, primary_key=True)
    tactic_id = Column(Integer, index=True)  # 关联策略表
    tactic_perform = Column(Text)  # 策略表现
    robustness_save_time = Column(DateTime, default=datetime.now())  # 保存时间
    deleted = Column(Integer, default=0)


# 每日收益情况表
class DailyProfit(Base):
    __tablename__ = 'daily_profit'
    id = Column(Integer, primary_key=True)
    tactic_id = Column(Integer, index=True)  # 关联策略表
    daily_profit = Column(LONGTEXT)  # 每日收益
    daily_profit_save_time = Column(DateTime, default=datetime.now())
    deleted = Column(Integer, default=0)


# 选股结果表
class Result(Base):
    __tablename__ = 'result'
    id = Column(Integer, primary_key=True)
    tactic_id = Column(Integer, index=True)  # 关联策略表
    selected_stocks_result = Column(LONGTEXT)  # 所选股票列表
    result_save_time = Column(DateTime, default=datetime.now())  # 保存时间
    deleted = Column(Integer, default=0)


# 下周期选股结果
class NextStocks(Base):
    __tablename__ = 'next_stocks'
    id = Column(Integer, primary_key=True)
    tactic_id = Column(Integer, index=True)  # 关联策略表
    select_stocks_code = Column(Text)  # 下周期选股代码
    select_stocks_name = Column(Text)  # 下周期选股名称
    next_stocks_save_time = Column(DateTime, default=datetime.now())  # 保存时间
    deleted = Column(Integer, default=0)


# 择时策略评价表
class TimingComments(Base):
    __tablename__ = 'timing_comments'
    id = Column(Integer, primary_key=True)
    tactic_id = Column(Integer, index=True)  # 关联策略表
    accumulated_net = Column(String(64))  # 累计净值
    annualized_yield = Column(String(64))  # 年化收益率
    max_drawdown = Column(String(64))  # 最大回撤
    annualized_yield_drawdown_ratio = Column(String(64))  # 年化收益回撤比
    drawdown_start_time = Column(DateTime)  # 最大回撤开始时间
    drawdown_end_time = Column(DateTime)  # 最大回撤结束时间
    average_range = Column(String(64))  # 每笔交易平均盈亏
    profit_loss_ratio = Column(String(8))  # 盈亏收益比
    profit_times = Column(Integer)  # 盈利次数
    loss_times = Column(Integer)  # 亏损次数
    win_rate = Column(String(64))  # 胜率
    max_single_circle_rise_range = Column(String(64))  # 单笔最大盈利
    max_single_circle_down_range = Column(String(64))  # 单笔最大亏损
    max_holding_duration = Column(String(64))  # 单笔最长持有时间
    min_holding_duration = Column(String(64))  # 单笔最短持有时间
    average_holding_duration = Column(String(64))  # 平均持仓周期
    max_continuous_rise_days = Column(Integer)  # 最大连续盈利笔数
    max_continuous_down_days = Column(Integer)  # 最大连续亏损笔数
    comments_save_time = Column(DateTime, default=datetime.now())  # 保存时间
    deleted = Column(Integer, default=0)  # 逻辑删除


if __name__ == '__main__':
    drop_article_db()
    init_article_db()
