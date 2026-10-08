import io
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas


def _draw_background(c: canvas.Canvas, width: float, height: float) -> None:
    c.setFillColorRGB(0.97, 0.96, 0.92)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    border_margin = 1.2 * cm
    c.setStrokeColorRGB(0.72, 0.58, 0.27)
    c.setLineWidth(3)
    c.rect(border_margin, border_margin, width - 2 * border_margin, height - 2 * border_margin, fill=0, stroke=1)

    inner_margin = 1.5 * cm
    c.setLineWidth(1)
    c.setStrokeColorRGB(0.72, 0.58, 0.27)
    c.rect(inner_margin, inner_margin, width - 2 * inner_margin, height - 2 * inner_margin, fill=0, stroke=1)


def _draw_decorative_corners(c: canvas.Canvas, width: float, height: float) -> None:
    margin = 1.6 * cm
    size = 1.0 * cm
    c.setStrokeColorRGB(0.72, 0.58, 0.27)
    c.setLineWidth(2)
    corners = [
        (margin, margin),
        (width - margin, margin),
        (margin, height - margin),
        (width - margin, height - margin),
    ]
    for cx, cy in corners:
        c.arc(cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2, 0, 360)


def generate_certificate_pdf_bytes(
    cert_id: str,
    recipient_name: str,
    recipient_email: str,
    event_name: str,
    issued_by: str,
    completion_date: str,
) -> bytes:
    buffer = io.BytesIO()

    page_size = landscape(A4)
    width, height = page_size

    c = canvas.Canvas(buffer, pagesize=page_size)

    _draw_background(c, width, height)
    _draw_decorative_corners(c, width, height)

    gold = colors.HexColor("#B8962E")
    dark = colors.HexColor("#1a1a2e")
    mid = colors.HexColor("#4a4a6a")

    c.setFillColor(gold)
    c.setFont("Times-Bold", 11)
    c.drawCentredString(width / 2, height - 2.8 * cm, "\u2726  CERTIFICATE OF COMPLETION  \u2726")

    c.setFillColor(dark)
    c.setFont("Times-Bold", 42)
    c.drawCentredString(width / 2, height - 5.2 * cm, "Certificate of Completion")

    c.setFillColor(mid)
    c.setFont("Times-Italic", 15)
    c.drawCentredString(width / 2, height - 6.4 * cm, "This is to certify that")

    c.setFillColor(dark)
    c.setFont("Times-Bold", 34)
    c.drawCentredString(width / 2, height - 8.2 * cm, recipient_name)

    c.setFillColor(gold)
    c.setLineWidth(1.5)
    c.setStrokeColor(gold)
    line_y = height - 8.6 * cm
    c.line(width / 2 - 6 * cm, line_y, width / 2 + 6 * cm, line_y)

    c.setFillColor(mid)
    c.setFont("Times-Italic", 14)
    c.drawCentredString(width / 2, height - 9.6 * cm, "has successfully completed")

    c.setFillColor(dark)
    c.setFont("Times-Bold", 22)
    event_y = height - 11.0 * cm
    max_width = width - 8 * cm

    event_words = event_name.split()
    lines = []
    current = ""
    for word in event_words:
        test = (current + " " + word).strip()
        if c.stringWidth(test, "Times-Bold", 22) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    for i, line in enumerate(lines):
        c.drawCentredString(width / 2, event_y - i * 0.8 * cm, line)

    bottom_y = 3.5 * cm

    c.setFillColor(mid)
    c.setFont("Times-Roman", 12)
    c.drawCentredString(width / 4, bottom_y + 1.0 * cm, "Date of Completion")
    c.setFillColor(dark)
    c.setFont("Times-Bold", 13)
    c.drawCentredString(width / 4, bottom_y + 0.2 * cm, completion_date)

    c.setFillColor(gold)
    c.setLineWidth(1)
    c.line(width / 4 - 3 * cm, bottom_y - 0.2 * cm, width / 4 + 3 * cm, bottom_y - 0.2 * cm)

    c.setFillColor(mid)
    c.setFont("Times-Roman", 12)
    c.drawCentredString(3 * width / 4, bottom_y + 1.0 * cm, "Issued By")
    c.setFillColor(dark)
    c.setFont("Times-Bold", 13)
    c.drawCentredString(3 * width / 4, bottom_y + 0.2 * cm, issued_by)

    c.setFillColor(gold)
    c.line(3 * width / 4 - 3 * cm, bottom_y - 0.2 * cm, 3 * width / 4 + 3 * cm, bottom_y - 0.2 * cm)

    c.setFillColor(colors.HexColor("#9a9aaa"))
    c.setFont("Helvetica", 7)
    c.drawCentredString(width / 2, 1.5 * cm, f"Certificate ID: {cert_id}  |  {recipient_email}")

    c.save()
    buffer.seek(0)
    return buffer.read()
