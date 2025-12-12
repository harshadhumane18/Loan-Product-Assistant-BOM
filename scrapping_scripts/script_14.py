from playwright.sync_api import sync_playwright
import os

URL = "https://bankofmaharashtra.in/mahabank-rooftop-solar-panel-loan"

def extract_cell(cell):
    # Handle lists
    ul = cell.query_selector("ul")
    if ul:
        return "\n  - " + "\n  - ".join([li.inner_text().strip() for li in ul.query_selector_all("li")])
    # Handle nested tables
    nested_table = cell.query_selector("table")
    if nested_table:
        rows = []
        for nrow in nested_table.query_selector_all("tr"):
            ncols = [nc.inner_text().strip() for nc in nrow.query_selector_all("th,td")]
            rows.append(" | ".join(ncols))
        return "\n    " + "\n    ".join(rows)
    # Otherwise, just text
    return cell.inner_text().strip()

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(1000)

        output_lines = []
        output_lines.append("--- Mahabank Rooftop Solar Panel Loan Scheme Page ---")
        output_lines.append("Title: " + page.title())
        output_lines.append("URL: " + page.url)

        # Main content div
        content_div = page.query_selector("div.inner_post_content")
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
                        if not tds:
                            continue
                        s_no = tds[0].inner_text().strip() if len(tds) > 0 else ""
                        parameter = tds[1].inner_text().strip() if len(tds) > 1 else ""
                        if len(tds) == 4:
                            elig_3kw = extract_cell(tds[2])
                            elig_10kw = extract_cell(tds[3])
                        elif len(tds) == 3:
                            elig_3kw = extract_cell(tds[2])
                            elig_10kw = elig_3kw
                        else:
                            elig_3kw = ""
                            elig_10kw = ""
                        output_lines.append(f"S No.: {s_no}")
                        output_lines.append(f"Parameter: {parameter}")
                        output_lines.append(f"Eligibility Condition (Up to 3KW): {elig_3kw}")
                        output_lines.append(f"Eligibility Condition (Above 3KW to 10KW): {elig_10kw}")
                        output_lines.append("-" * 60)

        # Write output to a text file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # Go up one level from scrapping_scripts/
        output_dir = os.path.join(project_root, "data", "raw")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "script_14.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))

        browser.close()

if __name__ == "__main__":
    main()
