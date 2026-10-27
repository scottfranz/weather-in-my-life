# Weather In My Life

A scroll story that replays every day of NOAA weather records from Bakersfield, San Diego and Ann Arbor in an animated sky, followed by interactive charts.

Live at https://scottfranz.github.io/weather-in-my-life/

## Files

- `index.html`: the page source (without the `<html>`/`<head>` wrapper)
- `data/`: the raw NOAA Climate Data Online CSVs
- `tools/build.py`: merges the CSVs and builds the site
- `docs/`: the finished page, which GitHub Pages serves

## Updating the Ann Arbor data

1. Download the new days for the Ann Arbor SE station (USC00200228) as a CSV. This link needs no account; change the dates as needed:

   https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&stations=USC00200228&startDate=2026-10-26&endDate=2027-10-26&dataTypes=PRCP,SNOW,TMAX,TMIN&format=csv&units=standard

2. Save it in `data/` with a name that starts with `ann-arbor`, for example `data/ann-arbor-2026-2027.csv`. If two files cover the same day, the one whose name sorts last wins.
3. Run `python3 tools/build.py`. It prints the date range it found and any missing readings.
4. Commit and push. GitHub Pages republishes `docs/` within a minute or two.

The day count, end date, records and charts all update from the data. Missing readings show as "–" and as blank squares in the heatmap, and they aren't counted as zero.

## GitHub Pages setup

Settings → Pages → Source: **Deploy from a branch**, branch `main`, folder `/docs`.
