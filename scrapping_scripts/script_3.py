from playwright.sync_api import sync_playwright
import os

URL = "https://bankofmaharashtra.in/pradhan-mantri-awas-yojana-2"  # Replace with the actual URL if different

def extract_table1(table):
    """Extracts the first table (Sno, Particulars, Details)"""
    output = []
    rows = table.query_selector_all("tbody tr")
    for row in rows:
        cells = row.query_selector_all("td")
        if len(cells) == 3:
            s_no = cells[0].inner_text().strip()
            particular = cells[1].inner_text().strip()
            details_cell = cells[2]
            # Extract paragraphs and lists
            details_parts = []
            # Paragraphs
            for p in details_cell.query_selector_all("p"):
                text = p.inner_text().strip()
                if text:
                    details_parts.append(text)
            # Lists
            for ul in details_cell.query_selector_all("ul"):
                for li in ul.query_selector_all("li"):
                    details_parts.append("  - " + li.inner_text().strip())
            # Remove duplicates and empty lines
            seen = set()
            details = "\n".join(x for x in details_parts if x and not (x in seen or seen.add(x)))
            output.append(f"\nS.No: {s_no}\nParticulars: {particular}\nDetails:\n{details}\n")
    return output

def extract_table2(table):
    """Extracts the second table (Eligibility Criteria) in a block format."""
    output = []
    # Get headers
    headers = [th.inner_text().strip() for th in table.query_selector_all("thead tr th")]
    # Expecting: [Criteria, EWS, LIG, MIG]
    for row in table.query_selector_all("tbody tr"):
        cells = row.query_selector_all("td")
        if len(cells) == 4:
            output.append(f"Criteria: {cells[0].inner_text().strip()}")
            output.append(f"  EWS: {cells[1].inner_text().strip()}")
            output.append(f"  LIG: {cells[2].inner_text().strip()}")
            output.append(f"  MIG: {cells[3].inner_text().strip()}\n")
        elif len(cells) == 1:
            # Single cell, possibly a section header or merged row
            output.append(f"{cells[0].inner_text().strip()}\n")
        elif len(cells) == 3:
            # For merged columns (e.g., Property Location)
            output.append(f"Criteria: {cells[0].inner_text().strip()}")
            output.append(f"  EWS/LIG/MIG: {cells[1].inner_text().strip()} | {cells[2].inner_text().strip()}\n")
        else:
            # Fallback: just join all cells
            output.append(" | ".join([cell.inner_text().strip() for cell in cells]) + "\n")
    return output

def extract_steps(ol):
    """Extracts the steps to apply (ordered list)"""
    output = []
    for idx, li in enumerate(ol.query_selector_all("li"), 1):
        # Check for link
        a = li.query_selector("a")
        if a:
            text = li.inner_text().replace(a.inner_text(), "").strip()
            href = a.get_attribute("href")
            output.append(f"{idx}. {text} [Link: {href}]")
        else:
            output.append(f"{idx}. {li.inner_text().strip()}")
    return output

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(2000)

        # Click the menu/span for "Pradhan Mantri Awas Yojana – Urban 2.0"
        # You may need to adjust the selector if the menu is dynamic
        # Try to find the span by text
        target_span = page.locator('span.sideMenuSpan', has_text="Pradhan Mantri Awas Yojana – Urban 2.0")
        if target_span.count() > 0:
            target_span.first.click()
            page.wait_for_load_state()
            page.wait_for_timeout(2000)
        else:
            print("Target span not found!")
            browser.close()
            return

        # Now extract from the loaded content
        block = page.query_selector("div.page-con-list-block")
        output_lines = []

        # Title
        h1 = block.query_selector("h1")
        if h1:
            output_lines.append("--- Title ---")
            output_lines.append(h1.inner_text().strip())

        # All tables in the block
        tables = block.query_selector_all("table")
        if len(tables) >= 2:
            # Table 1
            output_lines.append("\n--- Table 1: Scheme Details ---")
            output_lines.extend(extract_table1(tables[0]))
            # Table 2
            output_lines.append("\n--- Table 2: Eligibility Criteria ---")
            output_lines.extend(extract_table2(tables[1]))
        else:
            output_lines.append("\n--- Tables not found or less than 2 tables present ---")

        # Steps to Apply
        h3s = block.query_selector_all("h3")
        steps_ol = None
        for h3 in h3s:
            if "Steps to Apply" in h3.inner_text():
                # Find the next <ol>
                steps_ol = h3.evaluate_handle(
                    """el => {
                        let sib = el.nextElementSibling;
                        while (sib) {
                            if (sib.tagName === 'OL') return sib;
                            sib = sib.nextElementSibling;
                        }
                        return null;
                    }"""
                )
                break
        if steps_ol:
            output_lines.append("\n--- Steps to Apply ---")
            output_lines.extend(extract_steps(steps_ol))
        else:
            output_lines.append("\n--- Steps to Apply not found ---")

        # Write to output file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # Go up one level from scrapping_scripts/
        output_dir = os.path.join(project_root, "data", "raw")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "script_3.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))

        browser.close()

if __name__ == "__main__":
    main()