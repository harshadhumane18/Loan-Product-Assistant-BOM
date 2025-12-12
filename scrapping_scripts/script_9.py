from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import os

URL = "https://bankofmaharashtra.in/maha-super-flexi-housing-loan-scheme"

def extract_faqs(tab):
    faqs = []
    faq_cards = tab.query_selector_all(".accordion.myaccordion .card")
    for card in faq_cards:
        question_btn = card.query_selector(".card-header button")
        answer_div = card.query_selector(".card-body")
        if question_btn and answer_div:
            question = question_btn.inner_text().strip()
            answer = answer_div.inner_text().strip()
            faqs.append(f"Q: {question}\nA: {answer}\n")
    return faqs

def extract_list_items(ul):
    items = []
    if ul:
        for li in ul.query_selector_all("li"):
            text = li.inner_text().strip()
            if text:
                items.append("- " + text)
                # Check for sublist
                sublist = li.query_selector("ul")
                if sublist:
                    for subli in sublist.query_selector_all("li"):
                        subtext = subli.inner_text().strip()
                        if subtext:
                            items.append("  * " + subtext)
    return items

def extract_table_content(table):
    """Extract content from the table in the new page"""
    table_data = []
    if table:
        # Get table headers
        headers = []
        header_row = table.query_selector("thead tr")
        if header_row:
            for th in header_row.query_selector_all("th"):
                header_text = th.inner_text().strip()
                if header_text:
                    headers.append(header_text)
        
        # Get table body rows
        tbody = table.query_selector("tbody")
        if tbody:
            for row in tbody.query_selector_all("tr"):
                row_data = []
                for td in row.query_selector_all("td"):
                    cell_text = td.inner_text().strip()
                    if cell_text:
                        row_data.append(cell_text)
                if row_data:
                    table_data.append(row_data)
    
    return headers, table_data

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(500)

        output_lines = []

        # Listen for new page (tab) event for "Mahabank Personal Loan Scheme"
        with page.expect_popup() as new_page_info:
            page.locator('span.sideMenuSpan', has_text="Mahabank Personal Loan Scheme").first.click()
        new_page = new_page_info.value

        new_page.wait_for_load_state()
        new_page.wait_for_timeout(1000)

        output_lines.append("--- Mahabank Personal Loan Scheme Page ---")
        output_lines.append("Title: " + new_page.title())
        output_lines.append("URL: " + new_page.url)

        # --- Introduction and Interest Rate Box ---
        intro_div = new_page.query_selector("div.col-lg-7")
        if intro_div:
            intro_p = intro_div.query_selector("p")
            if intro_p:
                output_lines.append("\n--- Introduction ---\n" + intro_p.inner_text())

        rate_box = new_page.query_selector("div.col-lg-5 div.intrtbox div.cont")
        if rate_box:
            rate_title = rate_box.query_selector("h4").inner_text()
            rate_value = rate_box.query_selector("h2").inner_text()
            output_lines.append(f"\n--- Interest Rate Box ---\n{rate_title}: {rate_value}")

        # --- Loan Types ---
        types_div = new_page.query_selector("div.col-lg-12.mt-3")
        if types_div:
            h2 = types_div.query_selector("h2")
            if h2:
                output_lines.append(f"\n--- {h2.inner_text()} ---")
            ul = types_div.query_selector("ul.box-list-pl")
            if ul:
                for li in ul.query_selector_all("li"):
                    type_name = li.query_selector("div.in-loan-box2 p")
                    know_more = li.query_selector("div.read-more a")
                    if type_name:
                        line = type_name.inner_text().strip()
                        if know_more:
                            line += f" (Link: {know_more.get_attribute('href')})"
                        output_lines.append("- " + line)

        # --- Tabbed Content ---
        # Features & Benefits
        features_tab = new_page.query_selector('a[title="Personal Loan Features and Benefits"]')
        if features_tab:
            features_tab.click()
            new_page.wait_for_timeout(1000)
        features_card = new_page.query_selector("#pane-fb .card-body")
        if features_card:
            subhead = features_card.query_selector("h2.subhead")
            if subhead:
                output_lines.append(f"\n--- {subhead.inner_text()} ---")
            fblist = features_card.query_selector("ul.fblist")
            output_lines.extend(extract_list_items(fblist))
            normlist = features_card.query_selector("ul.normlist")
            output_lines.extend(extract_list_items(normlist))

        # Documents Required
        docs_tab = new_page.query_selector('a[title="Personal Loan Document Required"]')
        if docs_tab:
            docs_tab.click()
            new_page.wait_for_timeout(1000)
        docs_card = new_page.query_selector("#pane-dr .card-body")
        if docs_card:
            subhead = docs_card.query_selector("h3.subhead")
            if subhead:
                output_lines.append(f"\n--- {subhead.inner_text()} ---")
            docs_ul = docs_card.query_selector("ul.normlist")
            output_lines.extend(extract_list_items(docs_ul))

        # Interest Rates
        ir_tab = new_page.query_selector('a[title="Personal Loan Interest Rate"]')
        if ir_tab:
            ir_tab.click()
            new_page.wait_for_timeout(1000)
        ir_card = new_page.query_selector("#pane-ir .card-body")
        if ir_card:
            subhead = ir_card.query_selector("h3.subhead")
            if subhead:
                output_lines.append(f"\n--- {subhead.inner_text()} ---")
            ir_box = ir_card.query_selector("div.intrtbox div.cont")
            if ir_box:
                ir_title = ir_box.query_selector("h4").inner_text()
                ir_value = ir_box.query_selector("h2").inner_text()
                output_lines.append(f"{ir_title}: {ir_value}")
                for p in ir_box.query_selector_all("p"):
                    output_lines.append(p.inner_text())
                ul = ir_box.query_selector("ul.bomlist")
                output_lines.extend(extract_list_items(ul))

        # EMI Calculator
        emi_tab = new_page.query_selector('a[title="Personal Loan EMI Calculator"]')
        if emi_tab:
            emi_tab.click()
            new_page.wait_for_timeout(1000)
        emi_card = new_page.query_selector("#pane-emi .card-body")
        if emi_card:
            subhead = emi_card.query_selector("h3.subhead")
            if subhead:
                output_lines.append(f"\n--- {subhead.inner_text()} ---")
            # Extract EMI calculator fields and results
            calbox = emi_card.query_selector("div.Calbox")
            if calbox:
                for block in calbox.query_selector_all("div.Rangeblock"):
                    output_lines.append(block.inner_text())
                for block in calbox.query_selector_all("div.Rangeblockbtn"):
                    output_lines.append(block.inner_text())

        # FAQs
        faq_tab = new_page.query_selector('a[title="Frequently Asked Questions"]')
        if faq_tab:
            faq_tab.click()
            new_page.wait_for_timeout(1000)
        faq_card = new_page.query_selector("#pane-faq .card-body")
        if faq_card:
            subhead = faq_card.query_selector("h3.subhead")
            if subhead:
                output_lines.append(f"\n--- {subhead.inner_text()} ---")
            output_lines.extend(extract_faqs(faq_card))

        # How to Apply
        hta_tab = new_page.query_selector('a[title="How to Apply"]')
        if hta_tab:
            hta_tab.click()
            new_page.wait_for_timeout(1000)
        hta_card = new_page.query_selector("#pane-hta .card-body")
        if hta_card:
            subhead = hta_card.query_selector("h3.subhead")
            if subhead:
                output_lines.append(f"\n--- {subhead.inner_text()} ---")
            for p in hta_card.query_selector_all("p"):
                output_lines.append(p.inner_text())
            for h5 in hta_card.query_selector_all("h5"):
                output_lines.append(h5.inner_text())

        # Similar Products
        similar_div = new_page.query_selector("div.col-12.mt-3")
        if similar_div:
            h3 = similar_div.query_selector("h3.subhead")
            if h3:
                output_lines.append(f"\n--- {h3.inner_text()} ---")
            for slide in similar_div.query_selector_all("div.swiper-slide"):
                head = slide.query_selector("p.deposit-head")
                para = slide.query_selector("p.gen-para.com")
                link = slide.query_selector("a.intr-more")
                if head:
                    line = head.inner_text().strip()
                    if para:
                        line += " - " + para.inner_text().strip()
                    if link:
                        line += f" (Link: {link.get_attribute('href')})"
                    output_lines.append("- " + line)

        # --- Similar Products (for the link to Salaried Customers) ---
        salaried_link = None
        similar_div = new_page.query_selector("div.col-12.mt-3")
        if similar_div:
            for slide in similar_div.query_selector_all("div.swiper-slide"):
                head = slide.query_selector("p.deposit-head")
                link = slide.query_selector("a.intr-more")
                if head and "Salaried" in head.inner_text() and link:
                    salaried_link = link
                    break

        # --- Click the "KNOW MORE" for Salaried Customers and extract content from new page ---
        if salaried_link:
            # Listen for new page event when clicking the link
            salaried_link.click()
            new_page.wait_for_load_state("load")
            new_page.wait_for_timeout(2000)

            output_lines.append("\n" + "="*80)
            output_lines.append("--- SALARIED CUSTOMERS PERSONAL LOAN SCHEME DETAILS ---")
            output_lines.append("="*80)
            output_lines.append(f"Title: {new_page.title()}")
            output_lines.append(f"URL: {new_page.url}")

            # Extract the main content from the inner_post_content div
            content_div = new_page.query_selector("div.inner_post_content.inner_post_content-2")
            if content_div:
                # Extract the heading
                heading = content_div.query_selector("div.heading-wrap h1")
                if heading:
                    output_lines.append(f"\n--- {heading.inner_text().strip()} ---")

                # Extract the table content in the requested format
                table = content_div.query_selector("table")
                if table:
                    tbody = table.query_selector("tbody")
                    if tbody:
                        for row in tbody.query_selector_all("tr"):
                            tds = row.query_selector_all("td")
                            if len(tds) == 3:
                                sr_no = tds[0].inner_text().strip()
                                particulars = tds[1].inner_text().strip()
                                guidelines = tds[2].inner_text().strip()
                                output_lines.append(f"{sr_no}\nParticulars: {particulars}\nScheme Guidelines: {guidelines}\n")

                # Extract the EMI calculator button link
                emi_button = content_div.query_selector("a.btn.calcbtnBig")
                if emi_button:
                    emi_link = emi_button.get_attribute("href")
                    emi_text = emi_button.inner_text().strip()
                    output_lines.append(f"\n--- {emi_text} ---")
                    output_lines.append(f"Link: {emi_link}")

        # --- Click the "Maha Bank Personal Loan scheme for Professionals" side menu and extract content ---
        professionals_span = new_page.locator('span.sideMenuSpan', has_text="Maha Bank Personal Loan scheme for Professionals").first
        if professionals_span:
            professionals_span.click()
            new_page.wait_for_load_state("load")
            new_page.wait_for_timeout(2000)

            output_lines.append("\n" + "="*80)
            output_lines.append("--- MAHA BANK PERSONAL LOAN SCHEME FOR PROFESSIONALS DETAILS ---")
            output_lines.append("="*80)
            output_lines.append(f"Title: {new_page.title()}")
            output_lines.append(f"URL: {new_page.url}")

            # Extract the main content from the inner_post_content div
            content_div = new_page.query_selector("div.inner_post_content.inner_post_content-2")
            if content_div:
                # Extract the heading
                heading = content_div.query_selector("div.heading-wrap h1")
                if heading:
                    output_lines.append(f"\n--- {heading.inner_text().strip()} ---")

                # Extract the table content in the requested format
                table = content_div.query_selector("table")
                if table:
                    tbody = table.query_selector("tbody")
                    if tbody:
                        for row in tbody.query_selector_all("tr"):
                            tds = row.query_selector_all("td")
                            if len(tds) == 3:
                                sr_no = tds[0].inner_text().strip()
                                particulars = tds[1].inner_text().strip()
                                guidelines = tds[2].inner_text().strip()
                                output_lines.append(f"{sr_no}\nParticulars: {particulars}\nScheme Guidelines: {guidelines}\n")

                # Extract the EMI calculator button link
                emi_button = content_div.query_selector("a.btn.calcbtnBig")
                if emi_button:
                    emi_link = emi_button.get_attribute("href")
                    emi_text = emi_button.inner_text().strip()
                    output_lines.append(f"\n--- {emi_text} ---")
                    output_lines.append(f"Link: {emi_link}")

        # --- Click the "Maha Bank Personal Loan scheme - for Business Class having Home Loan with us" side menu and extract content ---
        business_class_span = new_page.locator(
            'span.sideMenuSpan', 
            has_text="Maha Bank Personal Loan scheme - for Business Class having Home Loan with us"
        ).first
        if business_class_span:
            business_class_span.click()
            new_page.wait_for_load_state("load")
            new_page.wait_for_timeout(2000)

            output_lines.append("\n" + "="*80)
            output_lines.append("--- MAHA BANK PERSONAL LOAN SCHEME FOR BUSINESS CLASS HAVING HOME LOAN WITH US DETAILS ---")
            output_lines.append("="*80)
            output_lines.append(f"Title: {new_page.title()}")
            output_lines.append(f"URL: {new_page.url}")

            # Extract the main content from the inner_post_content div
            content_div = new_page.query_selector("div.inner_post_content.inner_post_content-2")
            if content_div:
                # Extract the heading
                heading = content_div.query_selector("div.heading-wrap h1")
                if heading:
                    output_lines.append(f"\n--- {heading.inner_text().strip()} ---")

                # Extract the table content in the requested format
                table = content_div.query_selector("table")
                if table:
                    tbody = table.query_selector("tbody")
                    if tbody:
                        for row in tbody.query_selector_all("tr"):
                            tds = row.query_selector_all("td")
                            if len(tds) == 3:
                                sr_no = tds[0].inner_text().strip()
                                particulars = tds[1].inner_text().strip()
                                guidelines = tds[2].inner_text().strip()
                                output_lines.append(f"{sr_no}\nParticulars: {particulars}\nScheme Guidelines: {guidelines}\n")

                # Extract the EMI calculator button link
                emi_button = content_div.query_selector("a.btn.calcbtnBig")
                if emi_button:
                    emi_link = emi_button.get_attribute("href")
                    emi_text = emi_button.inner_text().strip()
                    output_lines.append(f"\n--- {emi_text} ---")
                    output_lines.append(f"Link: {emi_link}")

        # Write output to a text file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # Go up one level from scrapping_scripts/
        output_dir = os.path.join(project_root, "data", "raw")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "script_9.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))

        browser.close()

if __name__ == "__main__":
    main()
