from playwright.sync_api import sync_playwright
import os

URL = "https://bankofmaharashtra.in/maha-adhaar-loan"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(1000)

        output_lines = []
        output_lines.append("--- Mahabank Aadhar Loan Scheme Page ---")
        output_lines.append("Title: " + page.title())
        output_lines.append("URL: " + page.url)

        # Main content div
        content_div = page.query_selector("div.page-con-list-block")
        if content_div:
            # Heading
            heading = content_div.query_selector("div.heading-wrap h1")
            if heading:
                output_lines.append(f"\n--- {heading.inner_text().strip()} ---")

            # Table extraction
            table = content_div.query_selector("table")
            if table:
                # Extract table headers
                thead = table.query_selector("thead")
                if thead:
                    header_row = thead.query_selector("tr")
                    if header_row:
                        ths = header_row.query_selector_all("th")
                        headers = [th.inner_text().strip() for th in ths]
                        output_lines.append(" | ".join(headers))

                # Extract table body
                tbody = table.query_selector("tbody")
                if tbody:
                    for row in tbody.query_selector_all("tr"):
                        tds = row.query_selector_all("td")
                        if len(tds) == 3:
                            s_no = tds[0].inner_text().strip().replace('\n', ' ')
                            particulars = tds[1].inner_text().strip().replace('\n', ' ')
                            scheme_guidelines_text = tds[2].inner_text().strip().replace('\n', ' ')
                            output_lines.append(
                                f"SR No.: {s_no}\nParticulars: {particulars}\nScheme Guidelines: {scheme_guidelines_text}\n"
                            )

            # Apply Now button (if present)
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
        output_path = os.path.join(output_dir, "script_12.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))

        browser.close()

if __name__ == "__main__":
    main() 