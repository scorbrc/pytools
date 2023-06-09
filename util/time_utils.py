"""
Time utility tools that aim to parse any date/time into either a
local time or a UTC time.
"""
import datetime as dt
import dateutil.parser as dp
from dateutil import tz
import pytz
from dateutil.relativedelta import relativedelta


DAY_SECS = 60 * 60 * 24

# Build a timezone map that includes daylight savings time-zones.
TZ_MAP = {}
now = dt.datetime.utcnow()
summer_day = dt.datetime(now.year, 7, 1)
winter_day = dt.datetime(now.year, 1, 1)
for zone in pytz.all_timezones:
    for day in (summer_day, winter_day):
        try:
            tzdate = pytz.timezone(zone).localize(day, is_dst=None)
            TZ_MAP[tzdate.tzname()] = tz.gettz(zone)
        except pytz.NonExistentTimeError:
            pass

# Local timezone
TZ_LOCAL = dt.datetime.now(dt.timezone.utc).astimezone().tzinfo


def days_from_month(dt):
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
    dt = to_utc(dt)
    start_day = to_utc(dt.strftime('%Y-%m-01'))
    end_day = to_utc(
        (dt + relativedelta(months=1)).strftime('%Y-%m-01'))
    return (int((dt - start_day).total_seconds() / DAY_SECS),
            int((end_day - dt).total_seconds() / DAY_SECS))


def is_local(d):
    """ Returns true if datetime 'd' has the local timezone. """
    if is_tz_aware(d):
        dz = dt.datetime(d.year, d.month, d.day)
        return d.strftime('%Z') == to_local(dz).strftime('%Z')
    return False


def is_tz_aware(d):
    """ Returns True if datetime 'd' is timezone aware."""
    return d.tzinfo is not None and d.tzinfo.utcoffset(d) is not None


def is_utc(d):
    """ Returns true if datetime 'd' has the UTC timezone. """
    return is_tz_aware(d) and d.strftime('%Z') == to_utc().strftime('%Z')


def last_day_in_week(date):
    """ Finds the last day in week for 'date'. """
    dx = to_utc(date)
    d0 = dx.replace(hour=0, minute=0, second=0, microsecond=0)
    wk = dx.strftime('%Y-%W')
    td = dt.timedelta(days=1)
    for i in range(1, 8):
        d1 = d0 + td
        if d1.strftime('%Y-%W') != wk:
            return d0
        d0 = d1
    return d0


def to_local(d=None):
    """
    Produce a local timezone aware date from 'd' if given or using the current
    datetime if 'd' is None. If 'd' is a string then parse it as a date/time.
    If the date/time has a timezone then offset to local timezone. If there is
    no timezone then assume the date as given is local.
    """
    if d is not None:
        if not isinstance(d, dt.datetime):
            d = dp.parse(d, tzinfos=TZ_MAP)
        if is_tz_aware(d):
            dz = dt.datetime(d.year, d.month, d.day)
            return d.astimezone(dz.tzinfo)
        else:
            return d.astimezone()
    return dt.datetime.now().astimezone(TZ_LOCAL)


def to_utc(d=None):
    """
    Produce a UTC timezone aware date from 'd' if given or using the current
    datetime if 'd' is None. If 'd' is a string then parse it as a date/time.
    If the date/time has a timezone then offset to UTC. If there is no
    timezone then assume the date as given is UTC.
    """
    if d is not None:
        if not isinstance(d, dt.datetime):
            d = dp.parse(d, tzinfos=TZ_MAP)
        if is_tz_aware(d):
            return d.astimezone(tz.tzutc())
        else:
            return d.replace(tzinfo=dt.timezone.utc)
    return dt.datetime.now(dt.timezone.utc)


def truncate_to_day(d):
    """ Truncate datetome 'd' to day granularity. """
    return d.replace(hour=0, minute=0, second=0, microsecond=0)


def truncate_to_hour(d):
    """ Truncate datetome 'd' to hour granularity. """
    return d.replace(minute=0, second=0, microsecond=0)


def truncate_to_minute(d):
    """ Truncate datetome 'd' to minute granularity. """
    return d.replace(second=0, microsecond=0)


def truncate_to_second(d):
    """ Truncate datetome 'd' to minute granularity. """
    return d.replace(microsecond=0)
