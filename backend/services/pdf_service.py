# backend/services/pdf_service.py
from markdown_it import MarkdownIt
from weasyprint import HTML, CSS

def create_pdf_from_itinerary(markdown_text: str) -> bytes:
    """
    Converts a markdown string into a styled PDF document.
    """
    md = MarkdownIt()
    html_content = md.render(markdown_text)
    
    # CSS for styling the PDF document
    css_string = """
    @page { size: A4; margin: 2cm; }
    body { font-family: 'Helvetica', sans-serif; font-size: 11pt; line-height: 1.5; }
    h1, h2, h3 { font-family: 'Times New Roman', serif; color: #333; }
    h1 { font-size: 22pt; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 20px;}
    h2 { font-size: 16pt; }
    h3 { font-size: 13pt; }
    strong { font-weight: bold; }
    """
    
    # Generate PDF from HTML and CSS
    pdf_bytes = HTML(string=html_content).write_pdf(stylesheets=[CSS(string=css_string)])
    return pdf_bytes
