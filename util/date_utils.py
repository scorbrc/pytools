from calendar import monthrange
from datetime import datetime, timedelta
from math import ceil, floor

DAY_SECS = 60 * 60 * 24


def days_from_month(point_dt=datetime.now()):
    """
    Calculates numbers of days from beginning of the month and to the
    end of the month for 'point_dt'. Examples:
    days_from_month(dp.parse('2014-04-01'))
    >(0, 30)
    days_from_month(dp.parse('2014-04-02'))
    >(1, 29)
    days_from_month(dp.parse('2014-04-30'))
    >(29, 1)
    """
    first_day = point_dt.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0)
    last_day = first_day + \
        timedelta(days=monthrange(point_dt.year, point_dt.month)[1])
    days_to_start = floor((point_dt - first_day).total_seconds() / DAY_SECS)
    days_to_end = ceil((last_day - point_dt).total_seconds() / DAY_SECS)
    return days_to_start, days_to_end


def work_week(point_dt=datetime.now()):
    """
    Provides the year and week number for the working week, which ends on
    Friday, formatted as YYYY:WW and the ending Friday of that week.
    Thus Tuesday, Feb 4th, 2014 returns 2014:08, 2014-02-07.
    """
    point_dt = point_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    year, weeknum = [int(x) for x in point_dt.strftime('%Y %W').split()]
    if point_dt.weekday() < 4:
        week_ends_on = point_dt + timedelta(days=4 - point_dt.weekday())
        work_week = weeknum
    elif point_dt.weekday() == 4:
        week_ends_on = point_dt
        work_week = weeknum
    elif point_dt.weekday() == 5:
        week_ends_on = point_dt + timedelta(days=6)
        work_week = weeknum + 1
    else:
        week_ends_on = point_dt + timedelta(days=5)
        work_week = weeknum + 1
    if work_week > 52:
        work_week = 0
        year += 1
    return year, work_week, week_ends_on
