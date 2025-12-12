from playwright.sync_api import sync_playwright
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

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(500)

        output_lines = []

        # Listen for new page (tab) event for "Maha Gold Loan Scheme"
        with page.expect_popup() as new_page_info:
            page.locator('span.sideMenuSpan', has_text="Maha Gold Loan Scheme").first.click()
        new_page = new_page_info.value

        new_page.wait_for_load_state()
        new_page.wait_for_timeout(1000)

        output_lines.append("--- Maha Gold Loan Scheme Page ---")
        output_lines.append("Title: " + new_page.title())
        output_lines.append("URL: " + new_page.url)

        # --- Introduction and Interest Rate Box ---
        intro_div = new_page.query_selector("div.col-lg-7")
        if intro_div:
            heading = intro_div.query_selector("h1")
            if heading:
                output_lines.append("\n--- Heading ---\n" + heading.inner_text())
            intro_p = intro_div.query_selector("p")
            if intro_p:
                output_lines.append("\n--- Introduction ---\n" + intro_p.inner_text())

        rate_box = new_page.query_selector("div.intrtbox div.cont")
        if rate_box:
            rate_title = rate_box.query_selector("h4").inner_text()
            rate_value = rate_box.query_selector("h2").inner_text()
            output_lines.append(f"\n--- Interest Rate Box ---\n{rate_title}: {rate_value}")

        # --- Apply Today Section ---
        apply_today = new_page.query_selector('div.row.col-md-12')
        if apply_today:
            h3 = apply_today.query_selector("h3")
            p = apply_today.query_selector("p")
            if h3 and p:
                output_lines.append(f"\n--- {h3.inner_text()} ---\n{p.inner_text()}")

        # --- Tabbed Content ---
        # Features & Benefits
        features_tab = new_page.query_selector('a[title="Gold Loan Features and Benefits"]')
        if features_tab:
            features_tab.click()
            new_page.wait_for_timeout(1000)
        features_card = new_page.query_selector("#pane-fb .card-body")
        if features_card:
            subhead = features_card.query_selector("h2.subhead")
            if subhead:
                output_lines.append(f"\n--- {subhead.inner_text()} ---")
            # Main features list
            fblist = features_card.query_selector("ul.fblist")
            output_lines.extend(extract_list_items(fblist))
            # Normlist
            normlist = features_card.query_selector("ul.normlist")
            output_lines.extend(extract_list_items(normlist))
            # Special Features (accordion)
            special_features = features_card.query_selector("ol")
            if special_features:
                output_lines.append("\nSpecial Features:")
                for idx, li in enumerate(special_features.query_selector_all("li"), 1):
                    output_lines.append(f"  {idx}. {li.inner_text().strip()}")
            # Margin Table
            margin_table = features_card.query_selector("table.mytable")
            if margin_table:
                output_lines.append("\n--- Margin Table ---")
                headers = [th.inner_text().strip() for th in margin_table.query_selector_all("thead th")]
                output_lines.append(" | ".join(headers))
                for row in margin_table.query_selector_all("tbody tr"):
                    cells = [td.inner_text().strip() for td in row.query_selector_all("td")]
                    output_lines.append(" | ".join(cells))
            # Margin note
            margin_note = features_card.query_selector("p.card-text")
            if margin_note:
                output_lines.append(margin_note.inner_text())
            # Processing charges
            processing_ul = features_card.query_selector("ul.bomlist")
            if processing_ul:
                output_lines.append("\nProcessing Charges:")
                output_lines.extend(extract_list_items(processing_ul))
            # Loan Tenure
            tenure_ul = features_card.query_selector_all("ul.bomlist")
            if len(tenure_ul) > 1:
                output_lines.append("\nLoan Tenure:")
                output_lines.extend(extract_list_items(tenure_ul[1]))
            # Security
            security_p = features_card.query_selector("div#acFour p")
            if security_p:
                output_lines.append("\nSecurity:\n" + security_p.inner_text())

        # Documents Required
        docs_tab = new_page.query_selector('a[title="Documents required for Gold Loan"]')
        if docs_tab:
            docs_tab.click()
            new_page.wait_for_timeout(1000)
        docs_card = new_page.query_selector("#pane-dr .card-body")
        if docs_card:
            subhead = docs_card.query_selector("h2.subhead")
            if subhead:
                output_lines.append(f"\n--- {subhead.inner_text()} ---")
            docs_ul = docs_card.query_selector("ul.normlist")
            output_lines.extend(extract_list_items(docs_ul))

        # Interest Rates
        ir_tab = new_page.query_selector('a[title="Gold Loan Interest Rates"]')
        if ir_tab:
            ir_tab.click()
            new_page.wait_for_timeout(1000)
        ir_box = new_page.query_selector("#pane-ir .intrtbox .cont")
        if ir_box:
            ir_title = ir_box.query_selector("h4").inner_text()
            ir_value = ir_box.query_selector("h2").inner_text()
            output_lines.append(f"\n--- Interest Rates ---\n{ir_title}: {ir_value}")
            ir_p = ir_box.query_selector("p")
            if ir_p:
                output_lines.append(ir_p.inner_text())

        # Eligibility
        elig_tab = new_page.query_selector('a[title="Gold Loan Eligibility"]')
        if elig_tab:
            elig_tab.click()
            new_page.wait_for_timeout(1000)
        elig_card = new_page.query_selector("#pane-elig .card-body")
        if elig_card:
            subhead = elig_card.query_selector("h2.subhead")
            if subhead:
                output_lines.append(f"\n--- {subhead.inner_text()} ---")
            h4s = elig_card.query_selector_all("h4")
            for h4 in h4s:
                output_lines.append(h4.inner_text())
            ps = elig_card.query_selector_all("p")
            for p in ps:
                output_lines.append(p.inner_text())
            elig_ul = elig_card.query_selector("ul.bomlist")
            output_lines.extend(extract_list_items(elig_ul))

        # Repayment
        repay_tab = new_page.query_selector('a[title="gold loan in india"]')
        if repay_tab:
            repay_tab.click()
            new_page.wait_for_timeout(1000)
        repay_card = new_page.query_selector("#pane-repay .card-body")
        if repay_card:
            subhead = repay_card.query_selector("h2.subhead")
            if subhead:
                output_lines.append(f"\n--- {subhead.inner_text()} ---")
            h4s = repay_card.query_selector_all("h4")
            for h4 in h4s:
                output_lines.append(h4.inner_text())
            h5s = repay_card.query_selector_all("h5")
            for h5 in h5s:
                output_lines.append(h5.inner_text())
            h6s = repay_card.query_selector_all("h6")
            for h6 in h6s:
                output_lines.append(h6.inner_text())
            bs = repay_card.query_selector_all("b")
            for b in bs:
                output_lines.append(b.inner_text())
            ps = repay_card.query_selector_all("p")
            for p in ps:
                output_lines.append(p.inner_text())

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

        # Loan Process
        hta_tab = new_page.query_selector('a[title="Loan Process"]')
        if hta_tab:
            hta_tab.click()
            new_page.wait_for_timeout(1000)
        hta_card = new_page.query_selector("#pane-hta .card-body")
        if hta_card:
            subhead = hta_card.query_selector("h2.subhead")
            if subhead:
                output_lines.append(f"\n--- {subhead.inner_text()} ---")
            ps = hta_card.query_selector_all("p")
            for p in ps:
                output_lines.append(p.inner_text())
            ol = hta_card.query_selector("ol")
            if ol:
                for idx, li in enumerate(ol.query_selector_all("li"), 1):
                    output_lines.append(f"{idx}. {li.inner_text().strip()}")
            h5s = hta_card.query_selector_all("h5")
            for h5 in h5s:
                output_lines.append(h5.inner_text())

        # Write output to a text file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # Go up one level from scrapping_scripts/
        output_dir = os.path.join(project_root, "data", "raw")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "script_8.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))

        browser.close()

if __name__ == "__main__":
    main()
