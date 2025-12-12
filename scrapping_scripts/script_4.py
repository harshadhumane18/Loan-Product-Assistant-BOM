from playwright.sync_api import sync_playwright
import os

URL = "https://bankofmaharashtra.in/maha-super-flexi-housing-loan-scheme"  # Update if car loan has a different main page

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(2000)  # Wait for page to load

        output_lines = []

        # Listen for new page (tab) event for "Maha Super Car loan"
        with page.expect_popup() as new_page_info:
            # Click the span for "Maha Super Car loan"
            page.locator('span.sideMenuSpan', has_text="Maha Super Car loan").first.click()
        new_page = new_page_info.value

        new_page.wait_for_load_state()
        new_page.wait_for_timeout(2000)  # Wait for new tab to load

        # --- Extraction logic for the car loan page goes here ---
        output_lines.append("--- Maha Super Car Loan Page ---")
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

        # Features & Benefits (tab)
        features_tab = new_page.query_selector('a[title="Car Loan Features and Benefits"]')
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
        docs_tab = new_page.query_selector('a[title="Car Loan Documents Required"]')
        if docs_tab:
            docs_tab.click()
            new_page.wait_for_timeout(1000)
        docs_list = new_page.query_selector_all("#pane-dr ul.normlist > li")
        output_lines.append("\n--- Documents Required ---")
        for doc in docs_list:
            output_lines.append("- " + doc.inner_text())

        # Interest Rates (tab)
        ir_tab = new_page.query_selector('a[title="Car Loan Interest Rate"]')
        if ir_tab:
            ir_tab.click()
            new_page.wait_for_timeout(1000)
        ir_box = new_page.query_selector("#pane-ir .intrtbox .cont")
        if ir_box:
            ir_title = ir_box.query_selector("h4").inner_text()
            ir_value = ir_box.query_selector("h2").inner_text()
            output_lines.append(f"\n--- Interest Rates ---\n{ir_title}: {ir_value}")

        # EMI Calculator (tab)
        emi_tab = new_page.query_selector('a[title="Car Loan EMI Calculator"]')
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
        elig_tab = new_page.query_selector('a[title="Car Loan Eligibility"]')
        if elig_tab:
            elig_tab.click()
            new_page.wait_for_timeout(1000)
        elig_text = new_page.query_selector("#pane-elig h4")
        if elig_text:
            output_lines.append("\n--- Eligibility ---\n" + elig_text.inner_text())

        # How to Apply (tab)
        apply_tab = new_page.query_selector('a[title="How to Apply for Car Loan"]')
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

        # Write all output to a text file in Extracteddata_scriptwise
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # Go up one level from scrapping_scripts/
        output_dir = os.path.join(project_root, "data", "raw")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "script_4.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))

        browser.close()

if __name__ == "__main__":
    main()