import yfinance as yf
from icalendar import Calendar, Event
from datetime import date, timedelta
import pytz

tickers = ['GOOD', 'ARCC', 'GLAD', 'GAIN', 'MO', 'PFE', 'VZ', 'MAIN', 'O', 'PBA', 'AM', 'T', 'PM', 'SCHW', 'QYLD', 'SPYI', 'JEPI', 'DIVO', 'SCHD']  # Skip SWVXX for now

cal = Calendar()
cal.add('prodid', '-//Custom Dividend Calendar//')
cal.add('version', '2.0')
cal.add('method', 'PUBLISH')  # Required for many strict parsers
cal.add('X-WR-CALNAME', 'Dividend Ex-Dates & Pays')
cal.add('X-WR-TIMEZONE', 'UTC')

today = date.today()

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Upcoming if available
        ex_date = None
        if 'exDividendDate' in info and info['exDividendDate']:
            ex_ts = info['exDividendDate']
            ex_date = date.fromtimestamp(ex_ts)
            if ex_date >= today - timedelta(days=30):  # Recent/future buffer
                amount = info.get('dividendRate', 0.0) or (stock.dividends[-1] if not stock.dividends.empty else 0.0)
                pay_est = ex_date + timedelta(days=30)

                # Ex event
                ex_event = Event()
                ex_event.add('summary', f"{ticker} Ex-Date ${amount:.4f}")
                ex_event.add('dtstart', ex_date)
                ex_event.add('dtend', ex_date + timedelta(days=1))  # +1 day for single-day all-day
                ex_event.add('description', f"Ex-dividend date.\nEst pay: {pay_est}\nAmount: ${amount:.4f}\nCheck source.")
                ex_event.add('uid', f"{ticker}-ex-{ex_date.isoformat()}@divcalendar")
                ex_event.add('class', 'PUBLIC')
                ex_event.add('status', 'CONFIRMED')
                cal.add_component(ex_event)

                # Pay event
                pay_event = Event()
                pay_event.add('summary', f"{ticker} Pay (est)")
                pay_event.add('dtstart', pay_est)
                pay_event.add('dtend', pay_est + timedelta(days=1))
                pay_event.add('description', f"Estimated dividend payment.")
                pay_event.add('uid', f"{ticker}-pay-{pay_est.isoformat()}@divcalendar")
                pay_event.add('class', 'PUBLIC')
                pay_event.add('status', 'CONFIRMED')
                cal.add_component(pay_event)

        # Historical (last 8)
        divs = stock.dividends.tail(8)
        for d, amt in divs.items():
            hist_ex = d.date()
            if hist_ex.year >= today.year - 2:
                hist_pay = hist_ex + timedelta(days=30)
                h_event = Event()
                h_event.add('summary', f"{ticker} Ex (hist) ${amt:.4f}")
                h_event.add('dtstart', hist_ex)
                h_event.add('dtend', hist_ex + timedelta(days=1))  # +1 day
                h_event.add('description', f"Historical ex-date. Amount: ${amt:.4f}")
                h_event.add('uid', f"{ticker}-hist-{hist_ex.isoformat()}@divcalendar")
                h_event.add('class', 'PUBLIC')
                h_event.add('status', 'CONFIRMED')
                cal.add_component(h_event)

    except Exception as e:
        print(f"Skipped {ticker}: {e}")

with open('dividends.ics', 'wb') as f:
    f.write(cal.to_ical())

print("ICS generated")
