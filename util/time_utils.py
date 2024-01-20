"""
Time utility tools that bring together a few different Python libraries
(dateutil.parser, datautil.tz and pytz) with the aim of parsing any datetime
or string formated date/time into into either a local time or a UTC time with
a correctly offset timezone.
"""
import datetime as dt
import dateutil.parser as dp
from dateutil import tz
import pytz

TODAY = dt.date.today()

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
# The local timezone.
TZ_LOCAL = dt.datetime.now(dt.timezone.utc).astimezone().tzinfo


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


def parse(ds):
    """ Parse date/time string 'ds' into a datetime. """
    try:
        # Try faster ISO parsing.
        return dt.datetime.fromisoformat(ds)
    except ValueError:
        # Try the slower parsing for any date/time string.
        return dp.parse(ds, tzinfos=TZ_MAP)


def to_local(d=None):
    """
    Produce a local timezone aware date from 'd' if given or using the current
    datetime if 'd' is None. If 'd' is a string then parse it as a date/time.
    If the date/time has a timezone then offset to local timezone. If there is
    no timezone then assume the date as given is local.
    """
    if d is not None:
        if isinstance(d, str):
            d = parse(d)
        elif not hasattr(d, 'second'):
            d = dt.datetime.combine(d, dt.time())
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
        if isinstance(d, str):
            d = parse(d)
        elif not hasattr(d, 'second'):
            d = dt.datetime.combine(d, dt.time())
        if is_tz_aware(d):
            return d.astimezone(tz.tzutc())
        else:
            return d.replace(tzinfo=dt.timezone.utc)
    return dt.datetime.now(dt.timezone.utc)
