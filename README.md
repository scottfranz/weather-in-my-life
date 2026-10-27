# Weather In My Life

A scroll story that replays every day of NOAA weather records from Bakersfield, San Diego and Ann Arbor in an animated sky, followed by interactive charts.

Live at https://scottfranz.github.io/weather-in-my-life/

## Files

- `index.html`: the page source (without the `<html>`/`<head>` wrapper)
- `data/`: the raw NOAA Climate Data Online CSVs
- `tools/build.py`: merges the CSVs and builds the site
- `docs/`: the finished page, which GitHub Pages serves

## Updating the Ann Arbor data

This happens automatically. The **Update Ann Arbor weather** workflow (`.github/workflows/update-weather.yml`) runs on the 3rd of every month. It downloads the newest days from NOAA (`tools/fetch_ann_arbor.py`), rebuilds the page (`tools/build.py`), and commits the result, and GitHub Pages then republishes. To run it right away, open the **Actions** tab, choose the workflow, and click **Run workflow**.

Each run asks NOAA for the 30 days before the last day already saved, so late corrections to recent days get picked up. The download is saved as a new `data/ann-arbor-<first day>.csv`. Where files overlap, the file whose name sorts last wins.

To update by hand instead, run `python3 tools/fetch_ann_arbor.py` and then `python3 tools/build.py`, or save a CSV from NOAA in `data/` with a name starting `ann-arbor`, then commit and push.

The day count, end date, records and charts all update from the data. Missing readings show as "–" and as blank squares in the heatmap, and they aren't counted as zero.

## GitHub Pages setup

Settings → Pages → Source: **Deploy from a branch**, branch `main`, folder `/docs`.
