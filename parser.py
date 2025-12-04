import os
import re

def extract_links(content: str):
    """Extract markdown links of the form [text](target.md)."""
    links = re.findall(r'\[.*?\]\((.*?)\)', content)
    # Simple normalization: remove leading ./
    return [link.replace('./', '') for link in links]

def extract_headings(content: str):
    """Return all lines that start with # as headings."""
    return [line for line in content.split("\n") if line.strip().startswith("#")]


def parse_all_notes(folder: str):
    notes = {}

    if not os.path.isdir(folder):
        return notes

    for root, dirs, files in os.walk(folder):
        for filename in files:
            if filename.endswith(".md"):
                path = os.path.join(root, filename)

                key = filename
                
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                except UnicodeDecodeError:
                    with open(path, "r", errors="ignore") as f:
                        content = f.read()

                notes[key] = {
                    "content": content,
                    "links": extract_links(content),
                    "headings": extract_headings(content),
                    "path": os.path.relpath(path, folder) # Store relative path for reference
                }

    return notes
