from playwright.sync_api import sync_playwright
import re
import os

URL = "https://bankofmaharashtra.in/retail-interest-rates"

def extract_table_data(table):
    """Extract data from a table and return as formatted text"""
    if not table:
        return ""
    
    rows = table.query_selector_all("tbody tr")
    if not rows:
        rows = table.query_selector_all("tr")
    
    table_data = []
    for row in rows:
        cells = row.query_selector_all("td")
        if cells:
            row_data = []
            for cell in cells:
                # Handle colspan by getting all text content
                cell_text = cell.inner_text().strip()
                if cell_text:
                    row_data.append(cell_text)
            if row_data:
                table_data.append(" | ".join(row_data))
    
    return "\n".join(table_data)

def get_next_sibling_safe(element):
    """Safely get the next sibling element"""
    try:
        if element:
            return element.evaluate_handle("el => el.nextElementSibling")
    except:
        pass
    return None

def is_heading_element(element):
    """Safely check if element is a heading"""
    try:
        if element:
            tag_name = element.evaluate("el => el ? el.tagName : null")
            return tag_name == "H4"
    except:
        pass
    return False

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(2000)

        output_lines = []
        output_lines.append("--- Rate of Interest Retail Loans Page ---")
        output_lines.append("Title: Rate of Interest Retail Loans")
        output_lines.append(f"URL: {URL}\n")

        # Get the main content container
        main_content = page.query_selector("div.inner_post_content")
        if not main_content:
            main_content = page.query_selector("div.inner_post_content-2")
        
        if main_content:
            # Extract the main heading
            main_heading = main_content.query_selector("h1")
            if main_heading:
                output_lines.append(f"Main Heading: {main_heading.inner_text().strip()}")
            
            # Extract the description paragraph
            desc_paragraphs = main_content.query_selector_all("p")
            for p in desc_paragraphs:
                text = p.inner_text().strip()
                if text and "RLLR" in text:
                    output_lines.append(f"Description: {text}")
                    break
            
            # Extract all h4 headings and their content
            h4_headings = main_content.query_selector_all("h4")
            
            for i, heading in enumerate(h4_headings):
                heading_text = heading.inner_text().strip()
                output_lines.append(f"\n--- {heading_text} ---")
                
                # Get content after this heading until next h4
                current_element = heading
                content_added = False
                
                while current_element:
                    current_element = get_next_sibling_safe(current_element)
                    if not current_element:
                        break
                    
                    # Stop if we reach another h4
                    if is_heading_element(current_element):
                        break
                    
                    try:
                        # Extract text content
                        text_content = current_element.inner_text().strip()
                        if text_content and len(text_content) > 5:  # Filter out very short text
                            # Clean up the text (remove excessive whitespace)
                            text_content = re.sub(r'\s+', ' ', text_content).strip()
                            if text_content:
                                output_lines.append(text_content)
                                content_added = True
                        
                        # Extract tables
                        tables = current_element.query_selector_all("table")
                        for table in tables:
                            table_data = extract_table_data(table)
                            if table_data:
                                output_lines.append("\nTable Data:")
                                output_lines.append(table_data)
                                output_lines.append("")
                                content_added = True
                        
                        # Extract lists
                        ul_lists = current_element.query_selector_all("ul")
                        for ul in ul_lists:
                            for li in ul.query_selector_all("li"):
                                li_text = li.inner_text().strip()
                                if li_text:
                                    output_lines.append("- " + li_text)
                                    content_added = True
                        
                        ol_lists = current_element.query_selector_all("ol")
                        for ol in ol_lists:
                            for idx, li in enumerate(ol.query_selector_all("li"), 1):
                                li_text = li.inner_text().strip()
                                if li_text:
                                    output_lines.append(f"{idx}. {li_text}")
                                    content_added = True
                    
                    except Exception as e:
                        # Skip problematic elements
                        continue
                
                # If no content was added for this section, add a note
                if not content_added:
                    output_lines.append("(No additional content found for this section)")
            
            # Extract abbreviations section
            try:
                abbreviations = main_content.query_selector_all("p")
                abbr_section = []
                for p in abbreviations:
                    text = p.inner_text().strip()
                    if "Abbreviations:" in text or "ER:" in text or "CIC:" in text:
                        abbr_section.append(text)
                
                if abbr_section:
                    output_lines.append("\n--- Abbreviations ---")
                    for abbr in abbr_section:
                        output_lines.append(abbr)
            except:
                pass
        else:
            output_lines.append("Main content container not found")

        output_lines.append("\n------------------------------------------------------------")

        # Write to file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # Go up one level from scrapping_scripts/
        output_dir = os.path.join(project_root, "data", "raw")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "script_16_ROI.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))

        browser.close()

if __name__ == "__main__":
    main() 