import yfinance as yf
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import os

# Your tickers (add/remove as needed)
tickers = ['GOOD', 'ARCC', 'GLAD', 'GAIN', 'MO', 'PFE', 'VZ', 'MAIN', 'O', 'PBA', 'AM', 'T', 'PM', 'SCHW', 'QYLD', 'SPYI', 'JEPI', 'DIVO', 'SCHD', 'SWVXX']

cal = Calendar()
cal.add('prodid', '-//Your Dividend Calendar//')
cal.add('version', '2.0')
cal.add('X-WR-CALNAME', 'Dividend Ex-Dates & Pays')

today = datetime.now(pytz.utc)

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Next upcoming ex-date if available (often announced ahead)
        if 'exDividendDate' in info and info['exDividendDate']:
            ex_ts = info['exDividendDate']
            ex_date = datetime.fromtimestamp(ex_ts, tz=pytz.utc)
            if ex_date > today - timedelta(days=1):  # Only future/recent
                amount = info.get('dividendRate', stock.dividends[-1] if not stock.dividends.empty else 0)
                pay_date_est = ex_date + timedelta(days=30)  # Rough est; many are ~1 month

                # Ex-date event
                event_ex = Event()
                event_ex.add('summary', f"{ticker} Ex-Date ${amount:.4f}")
                event_ex.add('dtstart', ex_date.date())
                event_ex.add('dtend', ex_date.date())  # All-day event
                event_ex.add('description', f"Ex-dividend date for {ticker}. Est pay: {pay_date_est.date()}\nAmount: ${amount:.4f}\nCheck Schwab/Yahoo for confirmation.")
                event_ex.add('uid', f"{ticker}-ex-{ex_date.date()}")
                cal.add_component(event_ex)

                # Optional: Separate pay date event
                event_pay = Event()
                event_pay.add('summary', f"{ticker} Pay Date (est)")
                event_pay.add('dtstart', pay_date_est.date())
                event_pay.add('dtend', pay_date_est.date())
                event_pay.add('description', f"Estimated dividend payment for {ticker} (based on ex-date +30 days).")
                event_pay.add('uid', f"{ticker}-pay-{pay_date_est.date()}")
                cal.add_component(event_pay)

        # Add recent historical for context (last 1-2 years)
        dividends = stock.dividends.tail(8)  # Adjust as needed
        for date, amount in dividends.items():
            hist_ex = date.to_pydatetime().replace(tzinfo=pytz.utc)
            if hist_ex.year >= today.year - 2:
                hist_pay_est = hist_ex + timedelta(days=30)
                event_hist = Event()
                event_hist.add('summary', f"{ticker} Ex (hist) ${amount:.4f}")
                event_hist.add('dtstart', hist_ex.date())
                event_hist.add('dtend', hist_ex.date())
                event_hist.add('description', f"Historical ex-date. Amount: ${amount:.4f}")
                event_hist.add('uid', f"{ticker}-hist-{hist_ex.date()}")
                cal.add_component(event_hist)

    except Exception as e:
        print(f"Error for {ticker}: {e}")

# Write to file
ics_path = 'dividends.ics'
with open(ics_path, 'wb') as f:
    f.write(cal.to_ical())

print(f"Generated {ics_path} with events.")
