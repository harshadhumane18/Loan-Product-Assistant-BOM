from playwright.sync_api import sync_playwright
import os

URL = "https://bankofmaharashtra.in/maha-super-flexi-housing-loan-scheme"

def extract_pmvs_table(table):
    """Extracts the PMVS table with correct field names and structure."""
    output = []
    rows = table.query_selector_all("tr")
    for row in rows:
        cells = row.query_selector_all("td")
        if len(cells) == 3:
            sr_no = cells[0].inner_text().strip()
            particulars = cells[1].inner_text().strip()
            guidelines_cell = cells[2]

            guidelines_parts = []

            # Extract <ul> lists
            ul_lists = guidelines_cell.query_selector_all("ul")
            for ul in ul_lists:
                for li in ul.query_selector_all("li"):
                    guidelines_parts.append("  - " + li.inner_text().strip())

            # Extract <ol> lists
            ol_lists = guidelines_cell.query_selector_all("ol")
            for ol in ol_lists:
                for idx, li in enumerate(ol.query_selector_all("li"), 1):
                    guidelines_parts.append(f"  {idx}. {li.inner_text().strip()}")

            # Extract sub-tables
            sub_tables = guidelines_cell.query_selector_all("table")
            for sub_table in sub_tables:
                sub_headers = [th.inner_text().strip() for th in sub_table.query_selector_all("th")]
                sub_rows = sub_table.query_selector_all("tr")
                if sub_headers:
                    guidelines_parts.append("    " + " | ".join(sub_headers))
                    guidelines_parts.append("    " + "-" * (len(" | ".join(sub_headers))))
                for sub_row in sub_rows:
                    sub_cells = [td.inner_text().strip() for td in sub_row.query_selector_all("td")]
                    if sub_cells:
                        guidelines_parts.append("    " + " | ".join(sub_cells))

            # Get direct text, but remove text from sub-tables and lists to avoid duplication
            direct_text = guidelines_cell.inner_text().strip()
            for el in ul_lists + ol_lists + sub_tables:
                el_text = el.inner_text().strip()
                if el_text and el_text in direct_text:
                    direct_text = direct_text.replace(el_text, "")
            if direct_text:
                guidelines_parts.insert(0, direct_text.strip())

            # Remove duplicates and empty lines, preserve order
            seen = set()
            guidelines = "\n".join(
                x for x in guidelines_parts if x and not (x in seen or seen.add(x))
            )

            output.append(
                f"\nSr. No: {sr_no}\nParticulars: {particulars}\nGuidelines:\n{guidelines}\n"
            )
        elif len(cells) == 1:
            # Handle colspan=3 rows (e.g., notes at the end)
            text = cells[0].inner_text().strip()
            output.append(f"\n{'-'*20}\n{text}\n")
    return output

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)  # or slow_mo=0 for fastest
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(500)  # Wait for page to load

        output_lines = []

        # Listen for new page (tab) event for "Education Loan Scheme"
        with page.expect_popup() as new_page_info:
            page.locator('span.sideMenuSpan', has_text="Education Loan Scheme").first.click()
        new_page = new_page_info.value

        new_page.wait_for_load_state()
        new_page.wait_for_timeout(500)  # Wait for new tab to load

        output_lines.append("--- Mahabank Education Loan Page ---")
        output_lines.append("Title: " + new_page.title())
        output_lines.append("URL: " + new_page.url)

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

        # Education Loan Schemes (Loan Types)
        output_lines.append("\n--- Education Loan Schemes ---")
        loan_types = new_page.query_selector_all("ul.box-list-pl li .in-loan-box2 > p")
        for idx, loan in enumerate(loan_types, 1):
            output_lines.append(f"{idx}. {loan.inner_text()}")

        # Features & Benefits (tab)
        features_tab = new_page.query_selector('a[title="Education Loan Features and Benefits"]')
        if features_tab:
            features_tab.click()
            new_page.wait_for_timeout(1000)
        features_list = new_page.query_selector_all("ul.fblist h5")
        output_lines.append("\n--- Features & Benefits ---")
        for feature in features_list:
            output_lines.append("- " + feature.inner_text())

        # Additional Features (normlist)
        normlist_items = new_page.query_selector_all("ul.normlist.wrap.mt-3 li")
        for item in normlist_items:
            output_lines.append("* " + item.inner_text())

        # Documents Required (tab)
        docs_tab = new_page.query_selector('a[title="Documents required for Education Loan"]')
        if docs_tab:
            docs_tab.click()
            new_page.wait_for_timeout(1000)
        docs_list = new_page.query_selector_all("#pane-dr ul.normlist > li")
        output_lines.append("\n--- Documents Required ---")
        for doc in docs_list:
            output_lines.append("- " + doc.inner_text())
            # Check for sublist
            sublist = doc.query_selector_all("ul.sublist li") if hasattr(doc, "query_selector_all") else []
            for sub in sublist:
                output_lines.append("  * " + sub.inner_text())

        # Interest Rates (tab)
        ir_tab = new_page.query_selector('a[title="Education Loan Interest Rates"]')
        if ir_tab:
            ir_tab.click()
            new_page.wait_for_timeout(1000)
        ir_box = new_page.query_selector("#pane-ir .intrtbox .cont")
        if ir_box:
            ir_title = ir_box.query_selector("h4").inner_text()
            ir_value = ir_box.query_selector("h2").inner_text()
            output_lines.append(f"\n--- Interest Rates ---\n{ir_title}: {ir_value}")

        # EMI Calculator (tab)
        emi_tab = new_page.query_selector('a[title="Education Loan EMI Calculator"]')
        if emi_tab:
            emi_tab.click()
            new_page.wait_for_timeout(1000)
        emi_amount = new_page.query_selector("#totalLoanAmt_EduNew span")
        emi_interest = new_page.query_selector("#totalinterest_EduNew span")
        emi_total = new_page.query_selector("#maturityAmount_EduNew span")
        output_lines.append("\n--- EMI Calculator ---")
        if emi_amount and emi_interest and emi_total:
            output_lines.append(f"Monthly Payment (EMI): Rs. {emi_amount.inner_text()}")
            output_lines.append(f"Total Interest: Rs. {emi_interest.inner_text()}")
            output_lines.append(f"Total Repayment: Rs. {emi_total.inner_text()}")

        # Subsidies Scheme (tab)
        subsidies_tab = new_page.query_selector('a[title="Subsidies Scheme"]')
        if subsidies_tab:
            subsidies_tab.click()
            new_page.wait_for_timeout(1000)
        subsidies_text = new_page.query_selector("#pane-elig .card-body")
        if subsidies_text:
            output_lines.append("\n--- Subsidies Scheme ---\n" + subsidies_text.inner_text())

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

        # --- Extract Model Education Loan Scheme Table ---
        know_more_link = new_page.query_selector('a[href*="model-education-loan-scheme"]')
        if know_more_link:
            know_more_link.click()
            new_page.wait_for_load_state("load")
            new_page.wait_for_timeout(2000)

            output_lines.append("\n--- Navigated to 'Model Education Loan Scheme' page ---")
            output_lines.append("URL: " + new_page.url)

            # Extract the content block
            content_block = new_page.query_selector(".inner_post_content.inner_post_content-2")
            if content_block:
                # Extract heading
                heading = content_block.query_selector("h1")
                if heading:
                    output_lines.append("\n" + heading.inner_text().strip())
                # Extract the main table
                table = content_block.query_selector("table")
                if table:
                    output_lines.append("\n--- Scheme Table ---")
                    rows = table.query_selector_all("tr")
                    for row in rows:
                        cells = row.query_selector_all("td")
                        if len(cells) == 2:
                            param = cells[0].inner_text().strip()
                            details_cell = cells[1]
                            details_parts = []

                            # Extract <ul> lists
                            ul_lists = details_cell.query_selector_all("ul")
                            for ul in ul_lists:
                                for li in ul.query_selector_all("li"):
                                    details_parts.append("  - " + li.inner_text().strip())

                            # Extract <ol> lists
                            ol_lists = details_cell.query_selector_all("ol")
                            for ol in ol_lists:
                                for idx, li in enumerate(ol.query_selector_all("li"), 1):
                                    details_parts.append(f"  {idx}. {li.inner_text().strip()}")

                            # Extract sub-tables
                            sub_tables = details_cell.query_selector_all("table")
                            for sub_table in sub_tables:
                                # Sub-table extraction (simple, can be improved)
                                sub_headers = [th.inner_text().strip() for th in sub_table.query_selector_all("th")]
                                sub_rows = sub_table.query_selector_all("tr")
                                if sub_headers:
                                    details_parts.append("    " + " | ".join(sub_headers))
                                    details_parts.append("    " + "-" * (len(" | ".join(sub_headers))))
                                for sub_row in sub_rows:
                                    sub_cells = [td.inner_text().strip() for td in sub_row.query_selector_all("td")]
                                    if sub_cells:
                                        details_parts.append("    " + " | ".join(sub_cells))

                            # Get direct text, but remove text from sub-tables and lists to avoid duplication
                            direct_text = details_cell.inner_text().strip()
                            for el in ul_lists + ol_lists + sub_tables:
                                el_text = el.inner_text().strip()
                                if el_text and el_text in direct_text:
                                    direct_text = direct_text.replace(el_text, "")
                            if direct_text:
                                details_parts.insert(0, direct_text.strip())

                            # Remove duplicates and empty lines, preserve order
                            seen = set()
                            details = "\n".join(
                                x for x in details_parts if x and not (x in seen or seen.add(x))
                            )

                            output_lines.append(
                                f"\nParameter: {param}\nDetails:\n{details}\n"
                            )
                        elif len(cells) == 1:
                            # Handle colspan=2 rows (e.g., notes at the end)
                            text = cells[0].inner_text().strip()
                            output_lines.append(f"\n{'-'*20}\n{text}\n")
                else:
                    output_lines.append("\n--- Scheme Table not found on the page ---")
            else:
                output_lines.append("\n--- Content block not found on the page ---")
        else:
            output_lines.append("\n--- 'Know More...' link for Model Education Loan Scheme not found ---")

        # --- Extract Mahabank Skill Loan Scheme Content (Structured) ---
        skill_loan_span = new_page.locator('span.sideMenuSpan', has_text="Mahabank Skill Loan Scheme").first
        if skill_loan_span:
            skill_loan_span.click()
            new_page.wait_for_load_state("load")
            new_page.wait_for_timeout(2000)

            output_lines.append("\n--- Mahabank Skill Loan Scheme ---")
            output_lines.append("URL: " + new_page.url)

            content_block = new_page.query_selector(".inner_post_content.inner_post_content-2")
            if content_block:
                # Extract heading
                heading = content_block.query_selector("h1")
                if heading:
                    output_lines.append("\n" + heading.inner_text().strip())
                # Extract the main table
                table = content_block.query_selector("table")
                if table:
                    output_lines.append("\n--- Scheme Table ---")
                    rows = table.query_selector_all("tr")
                    for row in rows:
                        cells = row.query_selector_all("td")
                        if len(cells) == 3:
                            s_no = cells[0].inner_text().strip()
                            param = cells[1].inner_text().strip()
                            details_cell = cells[2]
                            details_parts = []

                            # Extract <ul> lists
                            ul_lists = details_cell.query_selector_all("ul")
                            for ul in ul_lists:
                                for li in ul.query_selector_all("li"):
                                    details_parts.append("  - " + li.inner_text().strip())

                            # Extract <ol> lists
                            ol_lists = details_cell.query_selector_all("ol")
                            for ol in ol_lists:
                                for idx, li in enumerate(ol.query_selector_all("li"), 1):
                                    details_parts.append(f"  {idx}. {li.inner_text().strip()}")

                            # Extract sub-tables
                            sub_tables = details_cell.query_selector_all("table")
                            for sub_table in sub_tables:
                                sub_headers = [th.inner_text().strip() for th in sub_table.query_selector_all("th")]
                                sub_rows = sub_table.query_selector_all("tr")
                                if sub_headers:
                                    details_parts.append("    " + " | ".join(sub_headers))
                                    details_parts.append("    " + "-" * (len(" | ".join(sub_headers))))
                                for sub_row in sub_rows:
                                    sub_cells = [td.inner_text().strip() for td in sub_row.query_selector_all("td")]
                                    if sub_cells:
                                        details_parts.append("    " + " | ".join(sub_cells))

                            # Get direct text, but remove text from sub-tables and lists to avoid duplication
                            direct_text = details_cell.inner_text().strip()
                            for el in ul_lists + ol_lists + sub_tables:
                                el_text = el.inner_text().strip()
                                if el_text and el_text in direct_text:
                                    direct_text = direct_text.replace(el_text, "")
                            if direct_text:
                                details_parts.insert(0, direct_text.strip())

                            # Remove duplicates and empty lines, preserve order
                            seen = set()
                            details = "\n".join(
                                x for x in details_parts if x and not (x in seen or seen.add(x))
                            )

                            output_lines.append(
                                f"\nS.No: {s_no}\nParameter: {param}\nDetails:\n{details}\n"
                            )
                        elif len(cells) == 1:
                            # Handle colspan=3 rows (e.g., notes at the end)
                            text = cells[0].inner_text().strip()
                            output_lines.append(f"\n{'-'*20}\n{text}\n")
                else:
                    output_lines.append("\n--- Scheme Table not found on the page ---")
            else:
                output_lines.append("\n--- Content block not found on the page ---")
        else:
            output_lines.append("\n--- 'Mahabank Skill Loan Scheme' side menu not found ---")

        # --- Extract PM - Vidya Laxmi (PMVS) Content (Structured) ---
        pmvs_span = new_page.locator('span.sideMenuSpan', has_text="PM - Vidya Laxmi (PMVS)").first
        if pmvs_span:
            pmvs_span.click()
            new_page.wait_for_load_state("load")
            new_page.wait_for_timeout(500)  # Reduced from 2000

            output_lines.append("\n--- PM - Vidya Laxmi (PMVS) ---")
            output_lines.append("URL: " + new_page.url)

            content_block = new_page.query_selector(".inner_post_content.inner_post_content-2")
            if content_block:
                heading = content_block.query_selector("h1")
                if heading:
                    output_lines.append("\n" + heading.inner_text().strip())

                # Extract all paragraphs before the table
                all_ps = content_block.query_selector_all("p")
                for p in all_ps:
                    text = p.inner_text().strip()
                    if text:
                        output_lines.append(text)

                # Extract all unordered lists before the table
                all_uls = content_block.query_selector_all("ul")
                for ul in all_uls:
                    for li in ul.query_selector_all("li"):
                        output_lines.append("  - " + li.inner_text().strip())

                # Extract all ordered lists before the table
                all_ols = content_block.query_selector_all("ol")
                for ol in all_ols:
                    for idx, li in enumerate(ol.query_selector_all("li"), 1):
                        output_lines.append(f"  {idx}. {li.inner_text().strip()}")

                # Extract the main table
                table = content_block.query_selector("table")
                output_lines.append("\n--- Scheme Table ---")
                if table:
                    output_lines.extend(extract_pmvs_table(table))
                else:
                    output_lines.append("Table not found.")
            else:
                output_lines.append("\n--- Content block not found on the page ---")
        else:
            output_lines.append("\n--- 'PM - Vidya Laxmi (PMVS)' side menu not found ---")

        # Write all output to a text file in Extracteddata_scriptwise
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # Go up one level from scrapping_scripts/
        output_dir = os.path.join(project_root, "data", "raw")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "script_7.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))

        browser.close()

if __name__ == "__main__":
    main() 