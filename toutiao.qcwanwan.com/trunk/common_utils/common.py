# _*_ coding: utf-8 _*_
# @Time    : 2017/11/6 下午5:41
# @Author  : 杨楚杰
# @File    : common.py
# @license : Copyright(C), 安锋游戏
import calendar
import datetime
import json
import socket
import time
import hashlib
import struct
import traceback
from functools import wraps
import os
import requests


class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:  # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


# 处理耗时监控通知
def run_time_monitor(func):
    @wraps(func)
    def wraper(*args, **kwargs):
        start_time = int(time.time()*1000)
        back = func(*args, **kwargs)
        end_time = int(time.time()*1000)
        if end_time - start_time > 20:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            msg = "[%s] - %s 函数执行超过阈值，执行时间为：%s 毫秒" % (now_time, func.__name__, end_time-start_time)
            print(msg)
        return back
    return wraper


 #获取当前的路径
def get_path():
    path = os.path.split(os.path.realpath(__file__))[0] + '/../'
    return os.path.join(path, "libs")

# 生成时间戳
def gen_timestamp():
    return int(time.time())


def get_dd(str_date):
    _date = time.strptime(str_date, "%Y-%m-%d")
    return int((time.mktime(_date) + 28800) / 86400) - 1


def convert_date_to_dd(_date):
    if _date:
        return get_dd(str(_date))
    return 0


def convert_dd_to_date(dd):
    timestamp = (int(dd) + 1) * 86400 - 28800
    _date = datetime.date.fromtimestamp(timestamp)
    return '%s' % (_date,)


def convert_dd_to_int_date(dd):
    timestamp = (int(dd) + 1) * 86400 - 28800
    _date = datetime.date.fromtimestamp(timestamp)
    str_date = '%s' % (_date,)
    return int(str_date.replace('-', ''))


def convert_int_date_to_str(_date):
    _date = str(_date)
    return '%s-%s-%s' % (_date[0:4], _date[4:6], _date[6:8])


def convert_date_to_int(_date):
    date_str = "%s" % (_date,)
    if _date is None or date_str is None:
        return 0
    return int(date_str.replace("-", ""))


def convert_int_date_to_str_date(_date):
    _date = str(_date)
    return "%s-%s-%s" % (_date[0:4], _date[4:6], _date[6:8])


def convert_datetime_to_int_date(_datetime):
    return int(_datetime.strftime("%Y-%m-%d").replace("-", ""))


def compare_two_datetime(_s_datetime, _e_datetime):
    _s = datetime.datetime.strptime(str(_s_datetime), "%Y-%m-%d %H:%M:%S")
    _e = datetime.datetime.strptime(str(_e_datetime), "%Y-%m-%d %H:%M:%S")
    if _s <= _e:
        return _s_datetime, convert_datetime_to_int_date(_s)
    return _e_datetime, convert_datetime_to_int_date(_e)


def string2timestamp(strValue, fmt="%Y-%m-%d %H:%M:%S"):
    try:
        d = datetime.datetime.strptime(strValue, fmt)
        t = d.timetuple()
        timeStamp = int(time.mktime(t))
        return timeStamp
    except ValueError as e:
        d = datetime.datetime.strptime(strValue, fmt)
        t = d.timetuple()
        timeStamp = int(time.mktime(t))
        return timeStamp


def getDate(dt):

    if dt:
        return dt.strftime("%m-%d %H:%M")
    else:
        return ''

# 获取当前日期在一年中的周数
def get_current_week():
    return int(time.strftime("%W"))


def get_week_from_datetime(_datetime):
    pass


def get_week_from_timestamp(timestamp):
    pass


def convert_date_from_datetime(_datetime):
    str_datetime = '%s' % _datetime
    date_list = str_datetime.split(' ')
    return int(date_list[0].replace('-', ''))


# 将时间戳转换成 datetime 日期时间
def convert_timestamp_to_datetime(ts):
    return datetime.datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts)), '%Y-%m-%d %H:%M:%S')


# 将datetime转化为时间戳
def convert_datetime_to_timestamp(dt, type='s'):
    if isinstance(dt, str):
        try:
            if len(dt) == 10:
                dt = datetime.datetime.strptime(dt.replace('/', '-'), '%Y-%m-%d')
            elif len(dt) == 19:
                dt = datetime.datetime.strptime(dt.replace('/', '-'), '%Y-%m-%d %H:%M:%S')
            else:
                raise ValueError()
        except ValueError as e:
            raise ValueError(
                "{0} is not supported datetime format." \
                "dt Format example: 'yyyy-mm-dd' or yyyy-mm-dd HH:MM:SS".format(dt)
            )

    # if isinstance(dt, time.struct_time):
    #    dt = datetime.datetime.strptime(time.stftime('%Y-%m-%d %H:%M:%S', dt), '%Y-%m-%d %H:%M:%S')

    if isinstance(dt, datetime.datetime):
        if type == 'ms':
            ts = int(dt.timestamp()) * 1000
        else:
            ts = int(dt.timestamp())
    else:
        raise ValueError(
            "dt type not supported. dt Format example: 'yyyy-mm-dd' or yyyy-mm-dd HH:MM:SS"
        )
    return ts


def string2timestamp(strValue, fmt="%Y-%m-%d %H:%M:%S"):
    try:
        d = datetime.datetime.strptime(strValue, fmt)
        t = d.timetuple()
        timeStamp = int(time.mktime(t))
        return timeStamp
    except ValueError as e:
        d = datetime.datetime.strptime(strValue, fmt)
        t = d.timetuple()
        timeStamp = int(time.mktime(t))
        return timeStamp


# 1440751417.283 --> '2015-08-28 16:43:37.283'
def timestamp2string(timeStamp, fmt="%Y-%m-%d %H:%M:%S"):
    try:
        d = datetime.datetime.fromtimestamp(timeStamp)
        str1 = d.strftime(fmt)
        # 2015-08-28 16:43:37.283000'
        return str1
    except Exception as e:
        print(e)
        return ''

# 获取两个日期（datetime类型）的间隔天数
def get_days_between_date(start_date, end_date):
    return (end_date.date() - start_date.date()).days


# 获取两个日期（str类型）的间隔天数
def get_days_between_str_date(start_date, end_date):
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    return (end.date() - start.date()).days


def get_weeks_between_date(start_date, end_date):
    year_count = end_date.year - start_date.year
    start_week = int(start_date.strftime('%U'))
    end_week = int(end_date.strftime('%U'))
    return (end_week - start_week) + (52 * year_count)


def get_months_between_date(start_date, end_date):
    year_count = end_date.year - start_date.year
    start_month = int(start_date.strftime('%m'))  # 周一作为开始
    end_month = int(end_date.strftime('%m'))
    return (end_month - start_month) + (12 * year_count)


# 获取当前日期的月数
def get_current_month():
    return int(time.strftime('%Y%m', time.localtime(time.time())))


def ip2int(addr):
    try:
        result = struct.unpack("!I", socket.inet_aton(addr))[0]
    except Exception as e:
        result = 0
    return result


def int2ip(addr):
    try:
        result = socket.inet_ntoa(struct.pack("!I", addr))
    except Exception as e:
        result = '0.0.0.0'
    return result


def join_key(*args):
    keys = '_'.join(args)
    return hashlib.md5(keys.encode('utf-8')).hexdigest()


def convert_timestamp_to_date(ts):
    return datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d')


# 获取两个时间之间所有天 (2017-12-11 --- 2017-12-17)
def get_every_day(begin_date, end_date):
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    while begin_date <= end_date:
        date_str = int(begin_date.strftime("%Y%m%d"))
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)
    return date_list


# 获取指定时间的下N周起始时间
def get_next_n_week_start_and_end(int_date=20170911, n=1):
    gave_date = datetime.datetime.strptime(str(int_date), "%Y%m%d")
    # 给定日期距离上周最后一天相隔的天数
    day_count = datetime.timedelta(days=gave_date.isoweekday())
    start = gave_date - day_count + datetime.timedelta(days=(1 + 7 * n))
    end = start + datetime.timedelta(days=6)
    date_start = datetime.datetime(start.year, start.month, start.day, 0, 0, 0).strftime('%Y%m%d')
    date_end = datetime.datetime(end.year, end.month, end.day, 23, 59, 59).strftime('%Y%m%d')
    return int(date_start), int(date_end)


# 获取指定时间的下N月起始时间
def get_next_n_month_start_and_end(int_date=20171211, n=1):
    try:
        gave_date = datetime.datetime.strptime(str(int_date), "%Y%m%d")
        first_day = datetime.date(gave_date.year, gave_date.month, 1)
        days_num = calendar.monthrange(gave_date.year, gave_date.month)[1]  # 获取一个月有多少天
        start = first_day + datetime.timedelta(days=days_num)
        end = start + datetime.timedelta(calendar.monthrange(start.year, start.month)[1] - 1)
        n -= 1
        if n:
            eee = int(start.strftime('%Y%m%d'))
            return get_next_n_month_start_and_end(eee, n)
        else:
            start_date = start.strftime('%Y%m%d')
            end_date = end.strftime('%Y%m%d')
            return int(start_date), int(end_date)
    except Exception as e:
        traceback.print_exc()


def get_recent_month():
    ts = gen_timestamp()
    end_date = timestamp2string(ts, fmt='%Y%m%d')

    start_ts = ts - 30 * 24 * 60 *60
    start_date = timestamp2string(start_ts, fmt='%Y%m%d')

    return {'s_t': start_date, 'e_t': end_date}

if __name__ == '__main__':
    print(get_weeks_between_date(datetime.datetime.strptime('2016-11-02 12:32:12', '%Y-%m-%d %H:%M:%S'),
                                 datetime.datetime.strptime('2017-11-16 12:32:12', '%Y-%m-%d %H:%M:%S')))

    print(get_months_between_date(datetime.datetime.strptime('2016-05-02 12:32:12', '%Y-%m-%d %H:%M:%S'),
                                  datetime.datetime.strptime('2017-11-16 12:32:12', '%Y-%m-%d %H:%M:%S')))

    print(convert_datetime_to_timestamp('2017-12-01 16:54:09'))

    xx = get_recent_month()
    print(xx)
