import yfinance as yf
from icalendar import Calendar, Event
from datetime import datetime, timedelta, date
import pytz

# Your tickers
tickers = ['GOOD', 'ARCC', 'GLAD', 'GAIN', 'MO', 'PFE', 'VZ', 'MAIN', 'O', 'PBA', 'AM', 'T', 'PM', 'SCHW', 'QYLD', 'SPYI', 'JEPI', 'DIVO', 'SCHD', 'SWVXX']

cal = Calendar()
cal.add('prodid', '-//Dividend Calendar//grok')
cal.add('version', '2.0')
cal.add('method', 'PUBLISH')
cal.add('X-WR-CALNAME', 'Dividend Ex-Dates & Pays')
cal.add('X-WR-TIMEZONE', 'UTC')  # Helps some parsers

today = datetime.now(pytz.utc).date()

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Upcoming ex-date if announced
        if 'exDividendDate' in info and info['exDividendDate']:
            ex_ts = info['exDividendDate']
            ex_date = datetime.fromtimestamp(ex_ts, tz=pytz.utc).date()
            if ex_date >= today - timedelta(days=1):  # Recent/future
                amount = info.get('dividendRate', stock.dividends[-1] if not stock.dividends.empty else 0.0)
                pay_date_est = ex_date + timedelta(days=30)

                # Ex-date event (DTEND = next day)
                event_ex = Event()
                event_ex.add('summary', f"{ticker} Ex-Date ${amount:.4f}")
                event_ex.add('dtstart', ex_date)
                event_ex.add('dtend', ex_date + timedelta(days=1))
                event_ex.add('description', f"Ex-dividend date for {ticker}.\nEst pay: {pay_date_est}\nAmount: ${amount:.4f}\nVerify on Schwab/Yahoo.")
                event_ex.add('uid', f"{ticker}-ex-{ex_date.isoformat()}")
                event_ex.add('class', 'PUBLIC')
                event_ex.add('status', 'CONFIRMED')
                cal.add_component(event_ex)

                # Pay date event
                event_pay = Event()
                event_pay.add('summary', f"{ticker} Pay Date (est)")
                event_pay.add('dtstart', pay_date_est)
                event_pay.add('dtend', pay_date_est + timedelta(days=1))
                event_pay.add('description', f"Estimated payment for {ticker} dividend.")
                event_pay.add('uid', f"{ticker}-pay-{pay_date_est.isoformat()}")
                event_pay.add('class', 'PUBLIC')
                event_pay.add('status', 'CONFIRMED')
                cal.add_component(event_pay)

        # Historical (limit to last 2 years, fewer events)
        dividends = stock.dividends.tail(8)
        for hist_date, amount in dividends.items():
            hist_ex = hist_date.date()
            if hist_ex.year >= today.year - 2:
                hist_pay_est = hist_ex + timedelta(days=30)
                event_hist = Event()
                event_hist.add('summary', f"{ticker} Ex (hist) ${amount:.4f}")
                event_hist.add('dtstart', hist_ex)
                event_hist.add('dtend', hist_ex + timedelta(days=1))
                event_hist.add('description', f"Historical ex-date. Amount: ${amount:.4f}")
                event_hist.add('uid', f"{ticker}-hist-{hist_ex.isoformat()}")
                event_hist.add('class', 'PUBLIC')
                event_hist.add('status', 'CONFIRMED')
                cal.add_component(event_hist)

    except Exception as e:
        print(f"Error processing {ticker}: {e}")

# Write file
with open('dividends.ics', 'wb') as f:
    f.write(cal.to_ical())

print("Generated dividends.ics")
