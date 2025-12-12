from playwright.sync_api import sync_playwright
import os

URL = "https://bankofmaharashtra.in/mahabank-green-financing-scheme"

def extract_main_scheme(page, output_lines):
    content_div = page.query_selector("div.inner_post_content")
    car_loan_link = None
    housing_loan_link = None
    if content_div:
        heading = content_div.query_selector("div.heading-wrap h1")
        if heading:
            output_lines.append(f"\n--- {heading.inner_text().strip()} ---")

        paragraphs = content_div.query_selector_all("p")
        for p in paragraphs:
            text = p.inner_text().strip()
            if text:
                output_lines.append(text)

    scheme_types_div = page.query_selector("div.col-lg-12.mt-3")
    if scheme_types_div:
        h4 = scheme_types_div.query_selector("h4")
        if h4:
            output_lines.append(f"\n--- {h4.inner_text().strip()} ---")

        scheme_items = scheme_types_div.query_selector_all("ul.box-list-pl li")
        for item in scheme_items:
            number = item.query_selector("div.in-loan-box1 p")
            name_desc = item.query_selector("div.in-loan-box2 p")
            know_more = item.query_selector("div.read-more a")
            if number and name_desc and know_more:
                output_lines.append(
                    f"{number.inner_text().strip()} {name_desc.inner_text().strip()}"
                )
                link = know_more.get_attribute('href')
                output_lines.append(f"Know More: {link}")
                if "housing-loan-scheme" in link:
                    housing_loan_link = link
                if "car-loan-scheme" in link or "carloan" in link or "electric-car" in link:
                    car_loan_link = link
    return housing_loan_link, car_loan_link

def extract_scheme_details(page, output_lines):
    main_div = page.query_selector("div.col-lg.order-1.order-lg-2.maincontent")
    if not main_div:
        return

    content_div = main_div.query_selector("div.inner_post_content")
    if content_div:
        heading = content_div.query_selector("div.heading-wrap h1")
        if heading:
            output_lines.append(f"\n--- {heading.inner_text().strip()} ---")

        # Paragraphs
        paragraphs = content_div.query_selector_all("p")
        for p in paragraphs:
            text = p.inner_text().strip()
            if text and not p.query_selector("strong"):
                output_lines.append(text)

        # Ordered lists
        ols = content_div.query_selector_all("ol")
        for ol in ols:
            items = ol.query_selector_all("li")
            for idx, li in enumerate(items, 1):
                output_lines.append(f"{idx}. {li.inner_text().strip()}")

        # Key Features (strong in p)
        for p in paragraphs:
            strong = p.query_selector("strong")
            if strong:
                text = strong.inner_text().strip()
                if text and "Key Features" in text:
                    output_lines.append(f"\n--- {text} ---")

        # Unordered lists
        uls = content_div.query_selector_all("ul")
        for ul in uls:
            items = ul.query_selector_all("li")
            for li in items:
                output_lines.append(f"- {li.inner_text().strip()}")

        # Main table (skip rows with nested tables)
        table = content_div.query_selector("table")
        if table:
            tbody = table.query_selector("tbody")
            if tbody:
                for row in tbody.query_selector_all("tr"):
                    # Omit row if any cell contains a table
                    if any(td.query_selector("table") for td in row.query_selector_all("td")):
                        continue
                    tds = row.query_selector_all("td")
                    if len(tds) == 3:
                        s_no = tds[0].inner_text().strip().replace('\n', ' ')
                        particulars = tds[1].inner_text().strip().replace('\n', ' ')
                        scheme_guidelines_text = tds[2].inner_text().strip().replace('\n', ' ')
                        output_lines.append(
                            f"S. No.: {s_no}\nParticulars: {particulars}\nScheme Guidelines: {scheme_guidelines_text}\n"
                        )

        # Buttons (Calculate EMI, Apply Now)
        btns = content_div.query_selector_all("a.btn")
        for btn in btns:
            btn_text = btn.inner_text().strip()
            btn_link = btn.get_attribute("href")
            output_lines.append(f"{btn_text}: {btn_link}")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(1000)

        output_lines = []
        output_lines.append("--- Mahabank Green Financing Scheme Page ---")
        output_lines.append("Title: " + page.title())
        output_lines.append("URL: " + page.url)

        housing_loan_link, car_loan_link = extract_main_scheme(page, output_lines)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # Go up one level from scrapping_scripts/
        output_dir = os.path.join(project_root, "data", "raw")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "script_13.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))

        # Extract housing loan details
        if housing_loan_link:
            if housing_loan_link.startswith("/"):
                next_url = "https://bankofmaharashtra.in" + housing_loan_link
            else:
                next_url = housing_loan_link
            page.goto(next_url, timeout=60000)
            page.wait_for_timeout(1000)

            output_lines2 = []
            output_lines2.append(f"\n--- Details for: {next_url} ---")
            extract_scheme_details(page, output_lines2)

            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)  # Go up one level from scrapping_scripts/
            output_dir = os.path.join(project_root, "data", "raw")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "script_13.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(output_lines))

        # Extract car loan details
        if car_loan_link:
            if car_loan_link.startswith("/"):
                next_url = "https://bankofmaharashtra.in" + car_loan_link
            else:
                next_url = car_loan_link
            page.goto(next_url, timeout=60000)
            page.wait_for_timeout(1000)

            output_lines3 = []
            output_lines3.append(f"\n--- Details for: {next_url} ---")
            extract_scheme_details(page, output_lines3)

            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)  # Go up one level from scrapping_scripts/
            output_dir = os.path.join(project_root, "data", "raw")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "script_13.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(output_lines))

        browser.close()

if __name__ == "__main__":
    main() 