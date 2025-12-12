from playwright.sync_api import sync_playwright
import os

URL = "https://bankofmaharashtra.in/maha-super-flexi-housing-loan-scheme"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(2000)  # Wait for page to load

        output_lines = []

        # Listen for new page (tab) event
        with page.expect_popup() as new_page_info:
            page.click('a.sideMenuA')
        new_page = new_page_info.value

        new_page.wait_for_load_state()
        new_page.wait_for_timeout(2000)  # Wait for new tab to load

        # Introduction
        intro_selector = "div.col-lg-7 > p"
        intro_text = new_page.query_selector(intro_selector).inner_text()
        output_lines.append("\n--- Introduction ---\n" + intro_text)

        # Interest Rate Box
        rate_selector = "div.intrtbox div.cont"
        rate_box = new_page.query_selector(rate_selector)
        if rate_box:
            rate_title = rate_box.query_selector("h4").inner_text()
            rate_value = rate_box.query_selector("h2").inner_text()
            output_lines.append(f"\n--- Interest Rate Box ---\n{rate_title}: {rate_value}")

        # Loan Types
        output_lines.append("\n--- Loan Types ---")
        loan_types = new_page.query_selector_all("ul.box-list-pl li .in-loan-box2 > p")
        for idx, loan in enumerate(loan_types, 1):
            output_lines.append(f"{idx}. {loan.inner_text()}")

        # Features & Benefits (tab)
        # Click the Features & Benefits tab if not already active
        features_tab = new_page.query_selector('a[title="Home Loan Features and Benefits"]')
        if features_tab:
            features_tab.click()
            new_page.wait_for_timeout(1000)
        features_list = new_page.query_selector_all("ul.fblist h5")
        output_lines.append("\n--- Features & Benefits ---")
        for feature in features_list:
            output_lines.append("- " + feature.inner_text())

        # Extract the additional features from the normlist under Features & Benefits
        normlist_items = new_page.query_selector_all("ul.normlist.wrap.mt-3 li")
        for item in normlist_items:
            output_lines.append("* " + item.inner_text())

        # Documents Required (tab)
        docs_tab = new_page.query_selector('a[title="Documents required for Home Loan"]')
        if docs_tab:
            docs_tab.click()
            new_page.wait_for_timeout(1000)
        docs_list = new_page.query_selector_all("#pane-dr ul.normlist > li")
        output_lines.append("\n--- Documents Required ---")
        for doc in docs_list:
            output_lines.append("- " + doc.inner_text())

        # Interest Rates (tab)
        ir_tab = new_page.query_selector('a[title="Home Loan Interest Rates"]')
        if ir_tab:
            ir_tab.click()
            new_page.wait_for_timeout(1000)
        ir_box = new_page.query_selector("#pane-ir .intrtbox .cont")
        if ir_box:
            ir_title = ir_box.query_selector("h4").inner_text()
            ir_value = ir_box.query_selector("h2").inner_text()
            output_lines.append(f"\n--- Interest Rates ---\n{ir_title}: {ir_value}")

        # EMI Calculator (tab)
        emi_tab = new_page.query_selector('a[title="Home Loan EMI Calculator"]')
        if emi_tab:
            emi_tab.click()
            new_page.wait_for_timeout(1000)
        emi_amount = new_page.query_selector("#emiamount span")
        emi_interest = new_page.query_selector("#interestamounbt span")
        emi_total = new_page.query_selector("#totalamounbt span")
        output_lines.append("\n--- EMI Calculator ---")
        if emi_amount and emi_interest and emi_total:
            output_lines.append(f"Monthly Payment (EMI): Rs. {emi_amount.inner_text()}")
            output_lines.append(f"Total Interest: Rs. {emi_interest.inner_text()}")
            output_lines.append(f"Total Repayment: Rs. {emi_total.inner_text()}")

        # Eligibility (tab)
        elig_tab = new_page.query_selector('a[title="Home Loan Eligibility"]')
        if elig_tab:
            elig_tab.click()
            new_page.wait_for_timeout(1000)
        elig_text = new_page.query_selector("#pane-elig h4")
        if elig_text:
            output_lines.append("\n--- Eligibility ---\n" + elig_text.inner_text())

        # How to Apply (tab)
        apply_tab = new_page.query_selector('a[title="How to apply home loan"]')
        if apply_tab:
            apply_tab.click()
            new_page.wait_for_timeout(1000)
        apply_text = new_page.query_selector("#pane-hta .card-body p.mb-0")
        if apply_text:
            output_lines.append("\n--- How to Apply ---\n" + apply_text.inner_text())

        # FAQ (tab)
        faq_tab = new_page.query_selector('a[title="Frequently Asked Questions"]')
        if faq_tab:
            faq_tab.click()
            new_page.wait_for_timeout(1000)
        output_lines.append("\n--- FAQs ---")
        faq_cards = new_page.query_selector_all("#pane-faq #accordionFAQ .card")
        for card in faq_cards:
            question_btn = card.query_selector(".card-header button")
            answer_div = card.query_selector(".card-body")
            if question_btn and answer_div:
                question = question_btn.inner_text().strip()
                answer = answer_div.inner_text().strip()
                output_lines.append(f"Q: {question}\nA: {answer}\n")

        # Click the "Purchase of New House/Flat" link under Similar Products
        # The link has class "intr-more" and a specific href
        house_flat_link = new_page.query_selector('a.intr-more[title="Purchase New House or Flat"]')
        if house_flat_link:
            with new_page.expect_popup() as house_flat_popup_info:
                house_flat_link.click()
            house_flat_page = house_flat_popup_info.value
            house_flat_page.wait_for_load_state()
            output_lines.append("\n--- Navigated to 'Purchase of New House/Flat' page ---")
            output_lines.append("URL: " + house_flat_page.url)

            # --- Extract the main table from the new page ---
            table_selector = ".page-con-list-block table"
            table = house_flat_page.query_selector(table_selector)
            if table:
                output_lines.append("\n--- Scheme Table ---")
                rows = table.query_selector_all("tbody tr")
                for row in rows:
                    cells = row.query_selector_all("td")
                    if len(cells) == 3:
                        s_no = cells[0].inner_text().strip()
                        particular = cells[1].inner_text().strip()
                        scheme_cell = cells[2]

                        # Extract all text, including lists and sub-tables, from scheme_cell
                        scheme_text_parts = []

                        # Get direct text (excluding text from child elements)
                        # We'll use inner_text for the whole cell, but also extract lists and sub-tables separately
                        direct_text = scheme_cell.inner_text().strip()
                        if direct_text:
                            scheme_text_parts.append(direct_text)

                        # Extract any <ul> lists
                        ul_lists = scheme_cell.query_selector_all("ul")
                        for ul in ul_lists:
                            for li in ul.query_selector_all("li"):
                                scheme_text_parts.append("  - " + li.inner_text().strip())

                        # Extract any sub-tables
                        sub_tables = scheme_cell.query_selector_all("table")
                        for sub_table in sub_tables:
                            sub_rows = sub_table.query_selector_all("tr")
                            for sub_row in sub_rows:
                                sub_cells = sub_row.query_selector_all("td")
                                if sub_cells:
                                    sub_row_text = "    " + " | ".join([sc.inner_text().strip() for sc in sub_cells])
                                    scheme_text_parts.append(sub_row_text)

                        # Remove duplicates and empty lines, preserve order
                        seen = set()
                        scheme_text = "\n".join(
                            x for x in scheme_text_parts if x and not (x in seen or seen.add(x))
                        )

                        # Write to output
                        output_lines.append(
                            f"\nS.No: {s_no}\nParticulars: {particular}\nScheme guidelines:\n{scheme_text}\n"
                        )
            else:
                output_lines.append("\n--- Scheme Table not found on the page ---")

            # Wait a bit before clicking the next link
            house_flat_page.wait_for_timeout(1000)  # Wait for 3 seconds

            # Click the span for "Purchase of Plot and construction thereon"
            plot_span = house_flat_page.locator('span.sideMenuSpan', has_text="Maha Super Housing Loan Scheme : Purchase of Plot and construction thereon")
            if plot_span.count() > 0:
                plot_span.first.click()
                house_flat_page.wait_for_load_state()
                output_lines.append("\n--- Navigated to 'Purchase of Plot and construction thereon' page ---")
                output_lines.append("URL: " + house_flat_page.url)

                # --- Extract the main table from the new page ---
                table_selector = ".page-con-list-block table"
                table = house_flat_page.query_selector(table_selector)
                if table:
                    output_lines.append("\n--- Scheme Table (Purchase of Plot & construction thereon) ---")
                    rows = table.query_selector_all("tbody tr")
                    for row in rows:
                        cells = row.query_selector_all("td")
                        if len(cells) == 3:
                            s_no = cells[0].inner_text().strip()
                            particular = cells[1].inner_text().strip()
                            scheme_cell = cells[2]

                            # Extract all text, including lists and sub-tables, from scheme_cell
                            scheme_text_parts = []

                            # Get direct text (excluding text from child elements)
                            direct_text = scheme_cell.inner_text().strip()
                            if direct_text:
                                scheme_text_parts.append(direct_text)

                            # Extract any <ul> lists
                            ul_lists = scheme_cell.query_selector_all("ul")
                            for ul in ul_lists:
                                for li in ul.query_selector_all("li"):
                                    scheme_text_parts.append("  - " + li.inner_text().strip())

                            # Extract any sub-tables
                            sub_tables = scheme_cell.query_selector_all("table")
                            for sub_table in sub_tables:
                                sub_rows = sub_table.query_selector_all("tr")
                                for sub_row in sub_rows:
                                    sub_cells = sub_row.query_selector_all("td")
                                    if sub_cells:
                                        sub_row_text = "    " + " | ".join([sc.inner_text().strip() for sc in sub_cells])
                                        scheme_text_parts.append(sub_row_text)

                            # Remove duplicates and empty lines, preserve order
                            seen = set()
                            scheme_text = "\n".join(
                                x for x in scheme_text_parts if x and not (x in seen or seen.add(x))
                            )

                            # Write to output
                            output_lines.append(
                                f"\nS.No: {s_no}\nParticulars: {particular}\nScheme guidelines:\n{scheme_text}\n"
                            )
                else:
                    output_lines.append("\n--- Scheme Table not found on the 'Purchase of Plot and construction thereon' page ---")
            else:
                output_lines.append("\n--- 'Purchase of Plot and construction thereon' span not found ---")

            # Click the span for "Maha Super Housing Loan Scheme for repairs/renovation/alteration of existing house/flat."
            repairs_span = house_flat_page.locator(
                'span.sideMenuSpan',
                has_text="Maha Super Housing Loan Scheme for repairs/renovation/alteration of existing house/flat."
            )
            if repairs_span.count() > 0:
                repairs_span.first.click()
                house_flat_page.wait_for_load_state()
                output_lines.append("\n--- Navigated to 'Maha Super Housing Loan Scheme for repairs/renovation/alteration of existing house/flat.' page ---")
                output_lines.append("URL: " + house_flat_page.url)

                # --- Extract the main table from the new page ---
                table_selector = ".page-con-list-block table"
                table = house_flat_page.query_selector(table_selector)
                if table:
                    output_lines.append("\n--- Scheme Table (Repairs/Renovation/Alteration) ---")
                    rows = table.query_selector_all("tbody tr")
                    for row in rows:
                        cells = row.query_selector_all("td")
                        if len(cells) == 3:
                            s_no = cells[0].inner_text().strip()
                            particular = cells[1].inner_text().strip()
                            scheme_cell = cells[2]

                            # Extract all text, including lists, sub-tables, and ordered lists from scheme_cell
                            scheme_text_parts = []

                            # Get direct text
                            direct_text = scheme_cell.inner_text().strip()
                            if direct_text:
                                scheme_text_parts.append(direct_text)

                            # Extract any <ul> lists
                            ul_lists = scheme_cell.query_selector_all("ul")
                            for ul in ul_lists:
                                for li in ul.query_selector_all("li"):
                                    scheme_text_parts.append("  - " + li.inner_text().strip())

                            # Extract any <ol> lists
                            ol_lists = scheme_cell.query_selector_all("ol")
                            for ol in ol_lists:
                                for idx, li in enumerate(ol.query_selector_all("li"), 1):
                                    scheme_text_parts.append(f"  {idx}. {li.inner_text().strip()}")

                            # Extract any sub-tables
                            sub_tables = scheme_cell.query_selector_all("table")
                            for sub_table in sub_tables:
                                sub_rows = sub_table.query_selector_all("tr")
                                for sub_row in sub_rows:
                                    sub_cells = sub_row.query_selector_all("td")
                                    if sub_cells:
                                        sub_row_text = "    " + " | ".join([sc.inner_text().strip() for sc in sub_cells])
                                        scheme_text_parts.append(sub_row_text)

                            # Remove duplicates and empty lines, preserve order
                            seen = set()
                            scheme_text = "\n".join(
                                x for x in scheme_text_parts if x and not (x in seen or seen.add(x))
                            )

                            # Write to output
                            output_lines.append(
                                f"\nS.No: {s_no}\nParticulars: {particular}\nScheme guidelines:\n{scheme_text}\n"
                            )
                else:
                    output_lines.append("\n--- Scheme Table not found on the 'Repairs/Renovation/Alteration' page ---")
            else:
                output_lines.append("\n--- 'Repairs/Renovation/Alteration' span not found ---")
        else:
            output_lines.append("\n--- 'Purchase of New House/Flat' link not found ---")

        # Write all output to a text file with the same name as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # Go up one level from scrapping_scripts/
        output_dir = os.path.join(project_root, "data", "raw")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "script_1.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))

        browser.close()

if __name__ == "__main__":
    main()