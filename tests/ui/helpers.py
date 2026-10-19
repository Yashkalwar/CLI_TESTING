def wait_for_shiny_idle(page, timeout=10_000):
    page.wait_for_function(
        "() => !document.documentElement.classList.contains('shiny-busy')",
        timeout=timeout,
    )
