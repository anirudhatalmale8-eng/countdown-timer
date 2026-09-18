from playwright.sync_api import sync_playwright

PATH = "file:///var/lib/freelancer/projects/55/index.html"
OUT = "/var/lib/freelancer/projects/55"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 900, "height": 860})
    page.goto(PATH)

    def read():
        return (
            page.text_content("#display"),
            page.text_content("#status"),
            page.text_content("#startPause"),
        )

    def log(label):
        t, s, b = read()
        print(f"{label:<28} {t:>8} | {s:<9} | {b}")

    log("initial")

    page.fill("#minutes", "2")
    log("set 2 minutes")

    page.click("#startPause")
    page.wait_for_timeout(2500)
    log("running ~2.5s")

    page.click("#startPause")
    at_pause = read()[0]
    page.wait_for_timeout(1500)
    after_pause = read()[0]
    log("paused")
    print(f"{'pause holds value':<28} {at_pause} == {after_pause} -> {at_pause == after_pause}")

    page.screenshot(path=f"{OUT}/timer-paused.png")

    page.click("#startPause")
    page.wait_for_timeout(1200)
    log("resumed")

    page.click("#reset")
    log("after reset")

    page.click('.preset[data-min="25"]')
    log("preset 25 min")

    page.click("body")
    page.keyboard.press("Space")
    page.wait_for_timeout(800)
    log("space = start")
    page.keyboard.press("Space")
    log("space = pause")
    page.keyboard.press("r")
    log("r = reset")

    # run one countdown all the way to zero (3 seconds)
    page.fill("#minutes", "0.05")
    page.click("#startPause")
    page.wait_for_timeout(4200)
    log("countdown finished")
    page.screenshot(path=f"{OUT}/timer-done.png")

    # the finished state must be restartable without pressing Reset first
    page.click("#startPause")
    page.wait_for_timeout(600)
    log("restart from finished")

    # a 0-minute duration must not be startable
    page.click("#reset")
    page.fill("#minutes", "0")
    print(f"{'0 min disables Start':<28} {page.is_disabled('#startPause')}")

    page.click("#reset")
    page.fill("#minutes", "5")
    page.click("#startPause")
    page.wait_for_timeout(1100)
    page.screenshot(path=f"{OUT}/timer-running.png")

    # mobile width sanity check
    m = browser.new_page(viewport={"width": 390, "height": 780})
    m.goto(PATH)
    m.screenshot(path=f"{OUT}/timer-mobile.png")

    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    print("console errors:", errors or "none")

    browser.close()
