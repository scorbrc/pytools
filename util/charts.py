""" Statistical utility functions. """
import scipy.stats as ss
import datetime as dt
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import numpy as np
from util.util_tools import to_snake_name


def cpd_chart(title, dates, data, cps, fp=None):
    """
    Generate a chart with 'title' showing values 'data' by periods in 'dates'
    and 'cps' changepoints '. Chart is written to 'fp', by default
    'charts/title.png'.
    """
    colors = ['peru', 'rebeccapurple', 'darkgreen', 'firebrick', 'black']
    markers = 'dv*os'

    if fp is None:
        # Make a file path.
        fp = 'charts/%s.png' % title.lower().replace(' ', '_')
        if not os.path.exists('charts'):
            os.mkdir('charts')

    # Create a range of dates.
    int_secs = (dates[-1] - dates[0]).total_seconds() / len(dates)
    x_dates = mpl.dates.drange(
        dates[0], dates[-1], dt.timedelta(seconds=int_secs))
    n = min(len(x_dates), len(data))

    # Create the overall chart.
    fig, ax1 = plt.subplots(1, 1, figsize=(10, 8))
    fig.suptitle("Changepoints for %s\nfrom %s to %s" %
                 (title,
                  dates[0].strftime('%Y-%m-%dT%H:%M'),
                  dates[-1].strftime('%Y-%m-%dT%H:%M')),
                 fontsize=14)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
    ax1.plot_date(x_dates[:n], data[:n], 'dodgerblue', label='observed')

    # Plot each changepoint.
    for i, cp in enumerate(cps):
        eps = [cp['m0']] * (cp['ci'] - cp['si']) + \
              [cp['m1']] * (cp['ei'] - cp['ci'])
        ax1.plot_date(
            x_dates[cp['si']:cp['ei']],
            eps,
            colors[i % len(colors)])
        ax1.plot(
            dates[cp['ci']],
            cp['m1'],
            marker=markers[i % len(markers)],
            color=colors[i % len(colors)],
            linewidth=2,
            markersize=8,
            label="CP: %.3f %s m0=%.4f m1=%.4f" %
            (cp['score'],
             dates[cp['ci']].strftime('%Y-%m-%dT%H:%M'),
             cp['m0'],
             cp['m1']))

    ax1.legend(loc=2, fontsize='small')
    ax1.grid(True)
    fig.autofmt_xdate()
    plt.savefig(fp)
    plt.close()


def chart(title, dates, obs, names=None, fp=None):
    """
    Generate a chart with 'title', 'dates' on X axis and 'obs' on Y axis.
    'obs' can be a single list of values or list of lists of values,
    which will allow charting multiple series.
    """
    if len(obs) > 0 and isinstance(obs[0], (list, tuple, np.ndarray)):
        data = obs
    else:
        data = [obs]
    if fp is None:
        fp = "charts/%s.png" % to_snake_name(title)
    interval_secs = (dates[-1] - dates[0]).total_seconds() / len(dates)
    x_dates = mpl.dates.drange(
        dates[0], dates[-1], dt.timedelta(seconds=interval_secs))
    n = min(len(x_dates), len(data[0]))
    fig = plt.figure(figsize=(10, 8))
    fig.suptitle("%s\nfrom %s to %s" %
                 (title,
                  dates[0].strftime('%Y-%m-%dT%H:%M'),
                  dates[-1].strftime('%Y-%m-%dT%H:%M')),
                 fontsize=14)
    gs = mpl.gridspec.GridSpec(1, 1)
    ax1 = plt.subplot(gs[0])
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
    for i, obs in enumerate(data):
        if names is not None and len(names) == len(data):
            label = "%s:" % names[i]
        else:
            label = "Series%d:" % (i + 1)
        label = "%s: mu=%.3f sd=%.3f kr=%.3f" % \
            (label, np.mean(obs), np.std(obs), ss.kurtosis(obs))
        colors = ['dodgerblue',
                  'darkgoldenrod',
                  'lightcoral',
                  'limegreen',
                  'indianred']
        ax1.plot_date(x_dates[:n], obs, colors[i % len(colors)], label=label)
    ax1.legend(loc=2, fontsize='small')
    ax1.grid(True)
    fig.autofmt_xdate()
    plt.savefig(fp)
    plt.close()


def test_chart(title, before, after, score, pct_diff=0, fp=None):
    """
    Generate a test chart with 'title' at the top and the 'before' and
    'after' values used for the test. 'score' is the tst score and 'pct_diff'
    is the percentage different between before and after values.
    """
    if fp is None:
        fp = "charts/%s_test.png" % to_snake_name(title)
    fig = plt.figure(figsize=(10, 8))
    fig.suptitle("%s\nscore=%.3f pct_diff=%.3f" %
                 (title, score, pct_diff), fontsize=14)
    gs = mpl.gridspec.GridSpec(1, 1)
    ax1 = plt.subplot(gs[0])
    xv = list(range(len(before) + len(after)))
    ax1.plot(xv[:len(before)], before, 'dodgerblue', label="before")
    ax1.plot(xv[-len(after):], after, 'darkgoldenrod', label="after")
    ax1.hlines(ss.trim_mean(before, .25), 0, len(xv), 'black')
    ax1.hlines(ss.trim_mean(after, .25), len(before), len(xv), 'darkred')
    ax1.legend(loc=2, fontsize='small')
    ax1.grid(True)
    plt.savefig(fp)
    plt.close()
