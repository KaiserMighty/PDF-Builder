import os
import sys
import io
import fitz
import tempfile
import shutil
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pdfrw import PdfReader, PdfWriter, PageMerge

INPUT_DIR = "input"
INPUT_PDF = "PDF_Template.pdf"
OUTPUT_PDF = "PDF_Output.pdf"

ITEM_Y_START = 459
ITEM_HEIGHT = 72.5
X_OFFSET = 36
LINK_X_OFFSET = 575

FONT_HEADER = "Cambria-Bold"
FONT_BODY = "Cambria"
FONT_SIZE = 11
LINE_SPACING = 1.2

pdfmetrics.registerFont(TTFont(FONT_BODY, 'C:/Windows/Fonts/cambria.ttc'))
pdfmetrics.registerFont(TTFont(FONT_HEADER, 'C:/Windows/Fonts/cambriab.ttf'))

def parse_item_file(filepath):
    item = {
        "title": "",
        "link": "",
        "subheader": "",
        "bullets": [],
    }
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("Title:"):
                item["title"] = line.replace("Title:", "").strip()
            elif line.startswith("Link:"):
                item["link"] = line.replace("Link:", "").strip()
            elif line.startswith("Subheader:"):
                item["subheader"] = line.replace("Subheader:", "").strip()
            elif line.startswith("Bullet"):
                item["bullets"].append(line.split(":", 1)[1].strip())
    return item

def create_overlay(items):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    for i, item in enumerate(items):
        y_base = ITEM_Y_START - (ITEM_HEIGHT * i)
        title = item['title']
        link = item['link']
        display_link = link.replace("https://", "").replace("http://", "")

        can.setFont(FONT_HEADER, FONT_SIZE)
        can.drawString(X_OFFSET, y_base + 57, title)

        can.setFont(FONT_HEADER, FONT_SIZE)
        link_width = can.stringWidth(display_link, FONT_HEADER, FONT_SIZE)
        link_x = LINK_X_OFFSET - link_width
        can.drawString(link_x, y_base + 57, display_link)
        underline_y = y_base + 55
        can.setLineWidth(0.5)
        can.line(link_x, underline_y, link_x + link_width, underline_y)

        can.setFont(FONT_BODY, FONT_SIZE)
        can.drawString(X_OFFSET, y_base + 44, item['subheader'])

        line_height = FONT_SIZE * LINE_SPACING
        for j, bullet in enumerate(item['bullets']):
            y = y_base + 30 - (j * line_height)
            can.drawString(X_OFFSET-3, y, f"▪     {bullet}")

    can.save()
    packet.seek(0)
    return PdfReader(packet).pages[0]

def build_pdf(input_pdf_path, output_pdf_path, item_keys):
    items = []
    for key in item_keys:
        filepath = os.path.join(INPUT_DIR, f"{key}.txt")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Item file not found: {filepath}")
        items.append(parse_item_file(filepath))

    overlay = create_overlay(items)
    base_pdf = PdfReader(input_pdf_path)
    PageMerge(base_pdf.pages[0]).add(overlay).render()
    PdfWriter(output_pdf_path, trailer=base_pdf).write()
    return items

def add_clickable_links(pdf_path, items):
    doc = fitz.open(pdf_path)
    page = doc[0]
    page_height = letter[1]

    for i, item in enumerate(items):
        y_base = ITEM_Y_START - (ITEM_HEIGHT * i)
        display_link = item['link'].replace("https://", "").replace("http://", "")
        link_width = len(display_link) * 5.5
        link_x1 = LINK_X_OFFSET
        link_x0 = link_x1 - link_width
        y0 = y_base + 60
        y1 = y0 + FONT_SIZE + 2

        rect = fitz.Rect(link_x0, page_height - y1, link_x1, page_height - y0)
        page.insert_link({"kind": fitz.LINK_URI, "from": rect, "uri": item['link']})

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp_path = tmp.name
    doc.save(tmp_path)
    doc.close()
    shutil.move(tmp_path, pdf_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_builder.py item1 item2 item3 item4 item5")
        sys.exit(1)

    item_args = sys.argv[1:]
    parsed_items = build_pdf(INPUT_PDF, OUTPUT_PDF, item_args)
    add_clickable_links(OUTPUT_PDF, parsed_items)
    print(f"{OUTPUT_PDF} has been generated.")
