# Shiny UI Testing POC - Plan

Goal: a dummy R Shiny app plus local, deterministic, AI-free Playwright UI tests. Nothing leaves the machine.

## Constraints
- Local only: no external services, accounts, API keys, telemetry, CDNs, web fonts or remote grids.
- No AI at test time. Tests are hand-written pytest scripts.
- Dummy hard-coded data only.
- Not using shinytest2, LambdaTest, Kane CLI or tunnels.

## Assumptions (checked on this machine)
| Item | Status |
|------|--------|
| Python | 3.12.0 found |
| Chrome | Found at `C:\Program Files\Google\Chrome\Application\chrome.exe` |
| R / Rscript | **Not found on PATH, and not in `C:\Program Files\R`. Must be installed or its path supplied.** |
| Shell | Windows, bash (Git Bash) |
| Port | 3838 on 127.0.0.1 |

## Layout
```
shiny-ui-poc/
  PLAN.md
  app/app.R                 # single-file base-shiny app (< ~80 lines)
  pytest.ini                # --browser-channel chrome
  tests/ui/
    requirements-test.txt   # pinned playwright, pytest, pytest-playwright
    conftest.py             # session autouse fixture: start/stop app, base_url
    helpers.py              # wait_for_shiny_idle(page)
    test_edge_cases.py      # 3 tests
    README.md
```

## Steps
1. **Environment**: install R (or provide the Rscript path). Create a Python venv and run `pip install -r tests/ui/requirements-test.txt`. Set `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1` and skip `playwright install`.
2. **App** (`app/app.R`): the IDs are `user_name`, `age`, `dept`, `submit`, `error_msg`, `greeting`, `people_table`.
   - Validation lives in `observeEvent(input$submit)` and writes to `reactiveValues`.
   - Rules: empty name gives "Name is required"; age NA or outside 1..120 gives "Age must be between 1 and 120"; otherwise the greeting "Hello, <name>! You are <age> years old."
   - The table has about 8 fake people, filtered by `dept`. An empty result shows a "No results" row.
3. **Test infrastructure**:
   - `conftest.py` launches `Rscript -e "shiny::runApp('app', port=3838, host='127.0.0.1', launch.browser=FALSE)"` from `shiny-ui-poc/`.
   - It polls the port for up to 60s and fails with a clear message on timeout.
   - It terminates the process on teardown and exposes `base_url`.
   - `helpers.py` waits for `shiny-busy` to leave `<html>`.
4. **Tests** (web-first `expect`, no `time.sleep`):
   - `test_empty_name_shows_error`
   - `test_invalid_age_shows_error`
   - `test_valid_submit_shows_greeting`
5. **Config**: `pytest.ini` with `--browser-channel chrome` and `testpaths = tests/ui`. No reporters or remote endpoints.
6. **README**: run the app, install, run tests (headless and `--headed --slowmo 300`), debugging (`PWDEBUG=1`, `--tracing on`), finding IDs, and the note on the browser download.

## Verification
- Manual: `Rscript -e "shiny::runApp('app', port=3838)"` and open http://127.0.0.1:3838.
- Automated: `pytest tests/ui -v` should give 3 passed.
- Negative check: in `app.R`, comment out the name-validation branch (rule 1). `test_empty_name_shows_error` should then fail. Restore it afterwards (`git diff` or a backup copy confirms).
- Offline: disable Wi-Fi/Ethernet, or run with no network, and rerun the tests. They should still pass, because everything is on 127.0.0.1.
- Grep check: no `time.sleep` and no external URLs in the tests or app.

## Risks
- R is not installed here, so the app and tests cannot run until it is.
- `shiny` must be installed in R (`install.packages("shiny")` needs the internet once, from CRAN). It needs approval, or an offline library copy.
- Port 3838 may already be in use, in which case the fixture should fail with a clear message.
- Rscript startup on Windows can take 5-15s. The 60s wait covers it.
