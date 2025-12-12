from playwright.sync_api import sync_playwright
import os

URL = "https://bankofmaharashtra.in/lad"

def get_list_after_heading(page, heading_text, list_type="ul"):
    # Find all <p> tags in the main block
    ps = page.query_selector_all("div.page-con-list-block > p")
    for p in ps:
        strong = p.query_selector("strong")
        if strong and heading_text.lower() in strong.inner_text().strip().lower():
            # Get the next sibling element (should be <ul> or <ol>)
            next_sibling = p.evaluate_handle("el => el.nextElementSibling")
            if next_sibling:
                if list_type == "ul" and next_sibling.query_selector_all("li"):
                    return [li.inner_text().strip() for li in next_sibling.query_selector_all("li")]
                if list_type == "ol" and next_sibling.query_selector_all("li"):
                    return [li.inner_text().strip() for li in next_sibling.query_selector_all("li")]
    return []

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(1000)

        output_lines = []
        output_lines.append("--- Loan Against Deposit (LAD) Page ---")
        output_lines.append("Title: Loan Against Deposit (LAD)")
        output_lines.append(f"URL: {URL}\n")

        # App Download Link
        app_link = ""
        app_btn = page.query_selector('a.btn.btn-primary')
        if app_btn:
            app_link = app_btn.get_attribute("href")
        if not app_link:
            app_link = "//bankofmaharashtra.in/maha-mobile?lk=dc"

        # Video Guide Link
        video_link = ""
        video_btn = page.query_selector('a.video')
        if video_btn:
            video_link = video_btn.get_attribute("href")
        if not video_link:
            video_link = "//youtu.be/1i9C6MtTXTU?si=zD6EMDDtoO7ioD8J&rel=0&showinfo=0"

        output_lines.append("--- Loan Against Deposit (LAD) ---")
        output_lines.append(f"App Download Link: {app_link}")
        output_lines.append(f"Video Guide: {video_link}\n")

        # Introduction
        h4 = page.query_selector("div.page-con-list-block h4")
        if h4:
            output_lines.append("--- Introduction ---")
            output_lines.append(h4.inner_text().strip())
        intro_ps = page.query_selector_all("div.page-con-list-block > p")
        for p in intro_ps:
            text = p.inner_text().strip()
            # Skip headings
            if text and not p.query_selector("strong"):
                output_lines.append(text)

        # Features
        features = get_list_after_heading(page, "Features of Loan Against Deposit", "ul")
        if features:
            output_lines.append("\n--- Features of Loan Against Deposit ---")
            for feat in features:
                output_lines.append("- " + feat)

        # Benefits
        benefits = get_list_after_heading(page, "Benefits of Loan Against Deposit During Emergencies", "ul")
        if benefits:
            output_lines.append("\n--- Benefits of Loan Against Deposit During Emergencies ---")
            for ben in benefits:
                output_lines.append("- " + ben)

        # How to Avail
        steps = get_list_after_heading(page, "How to Avail a Loan Against Fixed Deposit", "ol")
        if steps:
            output_lines.append("\n--- How to Avail a Loan Against Fixed Deposit ---")
            for idx, step in enumerate(steps, 1):
                output_lines.append(f"{idx}. {step}")

        # Final note/summary
        summary = ""
        summary_block = page.query_selector('div.page-con-list-block .row .col-12')
        if summary_block:
            summary = summary_block.inner_text().strip()
        if summary:
            output_lines.append("\n--- Summary ---")
            output_lines.append(summary)

        output_lines.append("------------------------------------------------------------")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # Go up one level from scrapping_scripts/
        output_dir = os.path.join(project_root, "data", "raw")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "script_15.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))

        browser.close()

if __name__ == "__main__":
    main()
