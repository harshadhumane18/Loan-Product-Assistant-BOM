from playwright.sync_api import sync_playwright
import os

URL = "https://bankofmaharashtra.in/mahabank-personalloan-scheme-bpcl-employees"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(1000)

        output_lines = []
        output_lines.append("--- Maha Bank Personal Loan scheme to BPCL Employees Page ---")
        output_lines.append("Title: " + page.title())
        output_lines.append("URL: " + page.url)

        # Main content div
        content_div = page.query_selector("div.inner_post_content.inner_post_content-2")
        if content_div:
            # Heading
            heading = content_div.query_selector("div.heading-wrap h1")
            if heading:
                output_lines.append(f"\n--- {heading.inner_text().strip()} ---")

            # Table extraction
            table = content_div.query_selector("table")
            if table:
                tbody = table.query_selector("tbody")
                if tbody:
                    for row in tbody.query_selector_all("tr"):
                        tds = row.query_selector_all("td")
                        if len(tds) == 2:
                            particulars = tds[0].inner_text().strip()
                            guidelines = tds[1].inner_text().strip()
                            output_lines.append(f"Particulars: {particulars}\nScheme Guidelines: {guidelines}\n")

            # Button links
            emi_button = content_div.query_selector("a.btn.calcbtnBig")
            if emi_button:
                emi_link = emi_button.get_attribute("href")
                emi_text = emi_button.inner_text().strip()
                output_lines.append(f"\n--- {emi_text} ---")
                output_lines.append(f"Link: {emi_link}")

            apply_button = content_div.query_selector("a.btn.applybtnBig")
            if apply_button:
                apply_link = apply_button.get_attribute("href")
                apply_text = apply_button.inner_text().strip()
                output_lines.append(f"\n--- {apply_text} ---")
                output_lines.append(f"Link: {apply_link}")

        # Write output to a text file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # Go up one level from scrapping_scripts/
        output_dir = os.path.join(project_root, "data", "raw")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "script_9_1.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))

        browser.close()

if __name__ == "__main__":
    main() 