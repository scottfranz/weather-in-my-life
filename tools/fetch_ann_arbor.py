"""Download the latest Ann Arbor SE (USC00200228) daily records from NOAA.

Usage:  python3 tools/fetch_ann_arbor.py

Finds the last day already in data/ann-arbor*.csv, then asks NOAA's access
service for everything from 30 days before that through today. The overlap
picks up NOAA's late corrections to recent days. The result is saved as
data/ann-arbor-<first day>.csv, which sorts after the older files, so its
values win where they overlap. Prints nothing new and writes nothing when
NOAA has no new days yet.
"""
import csv
import datetime as dt
import glob
import io
import os
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
STATION = "USC00200228"
OVERLAP_DAYS = 30
URL = "https://www.ncei.noaa.gov/access/services/data/v1"


def last_day():
    last = None
    for f in glob.glob(os.path.join(DATA, "ann-arbor*.csv")):
        with open(f, newline="") as fh:
            for row in csv.DictReader(fh):
                if row.get("STATION") == STATION:
                    d = dt.date.fromisoformat(row["DATE"])
                    last = d if last is None or d > last else last
    if last is None:
        raise SystemExit("No Ann Arbor rows found in data/.")
    return last


def download(start, end):
    query = urllib.parse.urlencode({
        "dataset": "daily-summaries",
        "stations": STATION,
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "dataTypes": "PRCP,SNOW,TMAX,TMIN",
        "format": "csv",
        "units": "standard",
    })
    for attempt in range(4):
        try:
            with urllib.request.urlopen(f"{URL}?{query}", timeout=60) as resp:
                return resp.read().decode("utf-8")
        except OSError as err:
            if attempt == 3:
                raise
            print(f"Download failed ({err}), retrying")
            time.sleep(2 ** (attempt + 1))


def main():
    last = last_day()
    start = last - dt.timedelta(days=OVERLAP_DAYS)
    today = dt.date.today()
    text = download(start, today)
    rows = [r for r in csv.DictReader(io.StringIO(text)) if r.get("STATION") == STATION]
    newest = max((dt.date.fromisoformat(r["DATE"]) for r in rows), default=None)
    if newest is None or newest <= last:
        print(f"No new days yet. The data already runs to {last}.")
        return
    # Replace any earlier fetch that starts on the same day.
    path = os.path.join(DATA, f"ann-arbor-{start.isoformat()}.csv")
    with open(path, "w", newline="") as fh:
        fh.write(text)
    print(f"Saved {len(rows)} days ({start} to {newest}) to {os.path.relpath(path, ROOT)}")


if __name__ == "__main__":
    main()
