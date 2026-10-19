# Shiny UI tests (local, no AI, no network)

Everything runs on 127.0.0.1. Nothing is sent to any external service.

## Run the app manually
    Rscript -e "shiny::runApp('app', port=3838)"   # from shiny-ui-poc/, then open http://127.0.0.1:3838
Needs the R package `shiny` (one-time install from CRAN).

## Install
    python -m venv .venv && .venv\Scripts\activate
    pip install -r tests/ui/requirements-test.txt
Do NOT run `playwright install chromium`: it downloads from the internet and needs approval.
Set `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1`. Tests use the locally installed Chrome (`--browser-channel chrome` in `pytest.ini`).

If `Rscript` is not on PATH, set `RSCRIPT` to its full path, e.g.
`set RSCRIPT=C:\Users\<you>\AppData\Local\Programs\R\R-4.6.1\bin\Rscript.exe`.

## Run tests (from shiny-ui-poc/)
    pytest tests/ui -v                          # headless
    pytest tests/ui -v --headed --slowmo 300    # watch it run
The app is started and stopped automatically by `conftest.py` (port 3838 must be free).

## Debug
- `PWDEBUG=1 pytest tests/ui -k empty_name --headed` opens the Playwright Inspector.
- `pytest tests/ui --tracing on` then `playwright show-trace test-results/<test>/trace.zip` (local viewer).

## Find element IDs
Open the app, right-click the element, Inspect, and read the `id` attribute (e.g. `#user_name`).
Shiny output/input IDs match the ids in `app/app.R`.

## Verify a test catches a bug
In `app/app.R`, change `!nzchar(name)` to `FALSE`, run `pytest tests/ui -k empty_name`: it must fail.
Revert the change afterwards.
