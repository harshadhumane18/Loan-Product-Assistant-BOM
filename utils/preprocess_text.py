import os
import re
import json
from pathlib import Path
from datetime import datetime

SOURCE_DIR = "C:\\Users\\harsh\\Desktop\\My_space\\Projects_2025\\proj_1211_new\\data\\raw"         # folder where your .txt files are stored
OUTPUT_DIR = "C:\\Users\\harsh\\Desktop\\My_space\\Projects_2025\\proj_1211_new\\data\\processed_data"        # folder where cleaned jsonl files will be saved

# -----------------------------------------------------
# Utility functions for text cleaning
# -----------------------------------------------------

def clean_text(text):
    """Clean and normalize raw scraped text."""
    
    # Remove multiple spaces/newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)                     # collapse extra newlines
    text = re.sub(r"[ \t]+", " ", text)                         # collapse multiple spaces
    
    # Remove boilerplate patterns
    boilerplate_patterns = [
        r"©\s*\d{4}.*",                      # copyright footers
        r"All rights reserved.*",
        r"Privacy Policy.*",
        r"Terms of Service.*",
        r"Cookie Policy.*",
        r"Subscribe to.*",
        r"Login\s*|\s*Signup.*"
    ]
    for bp in boilerplate_patterns:
        text = re.sub(bp, "", text, flags=re.IGNORECASE)

    # Normalize unicode & punctuation
    text = text.replace("\u201c", '"').replace("\u201d", '"')   # smart quotes
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\t", " ")

    # Strip spaces
    text = text.strip()
    return text


def split_into_sections(text):
    """Split text using headings and semantic boundaries."""
    
    # Detect headings — lines that are all caps or start with patterns like "##", "###"
    heading_pattern = re.compile(r"(^[A-Z][A-Za-z0-9 ]{3,}$)|(^#+ .*?$)", re.MULTILINE)

    sections = []
    last_pos = 0

    for match in heading_pattern.finditer(text):
        start = match.start()

        if last_pos != 0:
            sections.append(text[last_pos:start].strip())

        last_pos = start

    # Add the last section
    sections.append(text[last_pos:].strip())

    # Filter empty sections
    return [s for s in sections if len(s) > 50]        # ignore useless short junk blocks


def normalize_section(section):
    """Small normalization inside each section."""
    section = re.sub(r"\n{2,}", "\n", section)
    section = section.strip()
    return section


# -----------------------------------------------------
# Main processing pipeline
# -----------------------------------------------------

def process_files():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat()

    for filename in os.listdir(SOURCE_DIR):
        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(SOURCE_DIR, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        print(f"Processing: {filename}")

        # 1. Clean text
        cleaned = clean_text(raw_text)

        # 2. Split into meaningful sections
        sections = split_into_sections(cleaned)

        # 3. Normalize each section
        sections = [normalize_section(sec) for sec in sections]

        # Output JSONL file
        output_file = os.path.join(OUTPUT_DIR, filename.replace(".txt", ".jsonl"))

        with open(output_file, "w", encoding="utf-8") as out:
            for i, sec in enumerate(sections):
                obj = {
                    "id": f"{filename}-{i}",
                    "file_name": filename,
                    "section_index": i,
                    "content": sec,
                    "scraped_date": timestamp
                }
                out.write(json.dumps(obj, ensure_ascii=False) + "\n")

        print(f"Saved → {output_file}")


if __name__ == "__main__":
    process_files()
