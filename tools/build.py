"""Build the Weather In My Life page from NOAA Climate Data Online CSVs.

Usage:  python3 tools/build.py

Reads every CSV in data/ (Bakersfield, San Diego and any number of Ann Arbor
files), keeps one station per place, and writes:
  weather-data.js          the compact data the page loads
  docs/index.html          a complete page, served by GitHub Pages
  docs/weather-data.js
  docs/<file>              a copy of each file in static/ (icons)

To add newer Ann Arbor data, download another CSV for station USC00200228
(PRCP, SNOW, TMAX, TMIN) into data/ with a name starting "ann-arbor" and run
this again. Where files overlap, the file that sorts last wins.
"""
import csv
import datetime as dt
import glob
import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
SITE = os.path.join(ROOT, "docs")

# (file prefix, station id, first day, first day of the next place)
PLACES = [
    ("bakersfield", "USW00023155", dt.date(1991, 11, 11), dt.date(2010, 8, 1)),
    ("san-diego", "USW00023188", dt.date(2010, 8, 1), dt.date(2015, 8, 8)),
    ("ann-arbor", "USC00200228", dt.date(2015, 8, 8), None),
]


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load():
    days = {}
    for prefix, station, start, stop in PLACES:
        files = sorted(glob.glob(os.path.join(DATA, prefix + "*.csv")))
        if not files:
            raise SystemExit(f"No CSV files in data/ start with '{prefix}'.")
        for f in files:
            with open(f, newline="") as fh:
                for row in csv.DictReader(fh):
                    if row.get("STATION") != station:
                        continue
                    d = dt.date.fromisoformat(row["DATE"])
                    if d < start or (stop and d >= stop):
                        continue
                    days[d] = [num(row.get(k)) for k in ("TMAX", "TMIN", "PRCP", "SNOW")]
    return days


def main():
    days = load()
    start, end = min(days), max(days)
    n = (end - start).days + 1
    cols = {"tmax": [], "tmin": [], "prcp": [], "snow": []}
    missing = []
    for i in range(n):
        d = start + dt.timedelta(i)
        tmax, tmin, prcp, snow = days.get(d, [None] * 4)
        if d not in days:
            missing.append(d)
        cols["tmax"].append(None if tmax is None else round(tmax))
        cols["tmin"].append(None if tmin is None else round(tmin))
        cols["prcp"].append(None if prcp is None else round(prcp * 100))  # hundredths of an inch
        cols["snow"].append(None if snow is None else round(snow * 10))   # tenths of an inch
    js = "window.WEATHER=" + json.dumps({"start": start.isoformat(), **cols}, separators=(",", ":")) + ";"
    with open(os.path.join(ROOT, "weather-data.js"), "w") as fh:
        fh.write(js)

    # Wrap the page as a complete HTML document for static hosting.
    src = open(os.path.join(ROOT, "index.html")).read()
    split = src.index('<canvas id="sky"')
    head, body = src[:split], src[split:]
    head = re.sub(r'<meta name="claude:[^>]*>\n?', "", head)
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Every day of my life, replayed in the sky: {n:,} days of NOAA weather records from Bakersfield, San Diego and Ann Arbor.">
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
{head}</head>
<body>
{body}</body>
</html>
"""
    os.makedirs(SITE, exist_ok=True)
    with open(os.path.join(SITE, "index.html"), "w") as fh:
        fh.write(page)
    shutil.copy(os.path.join(ROOT, "weather-data.js"), os.path.join(SITE, "weather-data.js"))
    # Icons and other fixed assets.
    for f in glob.glob(os.path.join(ROOT, "static", "*")):
        shutil.copy(f, SITE)

    print(f"{n:,} days, {start} to {end}")
    for k, v in cols.items():
        gaps = sum(x is None for x in v)
        if gaps:
            print(f"  {k}: {gaps} missing readings")
    if missing:
        print(f"  {len(missing)} days have no row at all, e.g. {', '.join(map(str, missing[:5]))}")
    print("Wrote weather-data.js and docs/")


if __name__ == "__main__":
    main()
