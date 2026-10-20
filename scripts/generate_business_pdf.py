"""Generate the required BrightPath business profile PDF."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "me" / "about_business.pdf"

NAVY = colors.HexColor("#17365D")
BLUE = colors.HexColor("#2E75B6")
TEAL = colors.HexColor("#159A9C")
PALE = colors.HexColor("#EAF3F8")
TEXT = colors.HexColor("#243447")
MUTED = colors.HexColor("#607080")


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D9E4EC"))
    canvas.line(0.65 * inch, 0.55 * inch, 7.85 * inch, 0.55 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.65 * inch, 0.35 * inch, "BrightPath Tutoring - Fictional course assignment")
    canvas.drawRightString(7.85 * inch, 0.35 * inch, f"Page {doc.page}")
    canvas.restoreState()


def section(title, body, styles):
    return KeepTogether([
        Paragraph(title, styles["Section"]),
        Spacer(1, 4),
        Paragraph(body, styles["BodyCustom"]),
        Spacer(1, 10),
    ])


def build_pdf():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=LETTER,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.62 * inch,
        bottomMargin=0.72 * inch,
        title="BrightPath Tutoring Business Profile",
        author="BrightPath Tutoring",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates(PageTemplate(id="profile", frames=frame, onPage=footer))

    base = getSampleStyleSheet()
    styles = {
        "Title": ParagraphStyle(
            "Title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=25,
            leading=29, textColor=NAVY, alignment=TA_CENTER, spaceAfter=5,
        ),
        "Tag": ParagraphStyle(
            "Tag", parent=base["Normal"], fontName="Helvetica", fontSize=11,
            leading=15, textColor=TEAL, alignment=TA_CENTER, spaceAfter=18,
        ),
        "Section": ParagraphStyle(
            "Section", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=13,
            leading=16, textColor=BLUE, spaceBefore=3, spaceAfter=2,
        ),
        "BodyCustom": ParagraphStyle(
            "BodyCustom", parent=base["BodyText"], fontName="Helvetica", fontSize=9.5,
            leading=13.2, textColor=TEXT,
        ),
        "Small": ParagraphStyle(
            "Small", parent=base["BodyText"], fontName="Helvetica", fontSize=8.6,
            leading=11.2, textColor=TEXT,
        ),
        "Callout": ParagraphStyle(
            "Callout", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=10,
            leading=14, textColor=NAVY, alignment=TA_CENTER,
        ),
    }

    story = [
        Paragraph("BrightPath Tutoring", styles["Title"]),
        Paragraph("Clear explanations. Confident learners. Practical progress.", styles["Tag"]),
        Table(
            [[Paragraph(
                "<b>Mission</b><br/>Make difficult subjects understandable through patient teaching, "
                "guided practice, and study plans matched to each learner.", styles["Callout"])]],
            colWidths=[7.0 * inch],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), PALE),
                ("BOX", (0, 0), (-1, -1), 0.8, TEAL),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
            ]),
        ),
        Spacer(1, 14),
        section(
            "Business overview",
            "BrightPath Tutoring is a fictional learning center based in Hamra, Beirut, with "
            "online lessons available worldwide. It supports students in Grades 6-12 and at "
            "university through private lessons and small groups of two to four learners.", styles,
        ),
        section(
            "Subjects and services",
            "<b>Mathematics:</b> algebra, geometry, trigonometry, pre-calculus, calculus, linear "
            "algebra, differential equations, probability, and introductory statistics.<br/>"
            "<b>Physics:</b> school physics, university mechanics, electricity and magnetism, waves, "
            "and introductory thermodynamics.<br/><b>Programming:</b> Python, Java, C++, web "
            "fundamentals, debugging, and introductory data structures.<br/><b>English:</b> grammar, "
            "conversation, reading, academic writing, presentation skills, and IELTS or TOEFL "
            "foundations.", styles,
        ),
        Paragraph("Tutoring team", styles["Section"]),
        Spacer(1, 5),
    ]

    tutors = [
        ["Tutor", "Specialty", "Profile"],
        ["Maya Rahal", "Mathematics", "School and university mathematics; 8 years of tutoring."],
        ["Karim Nassar", "Physics", "Master's degree in applied physics."],
        ["Lina Haddad", "Programming", "Software engineer; Python, Java, C++, web, and data structures."],
        ["Sarah Khoury", "English", "CELTA-qualified English and academic-writing tutor."],
    ]
    tutor_table = Table(tutors, colWidths=[1.25 * inch, 1.25 * inch, 4.5 * inch], repeatRows=1)
    tutor_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("LEADING", (0, 0), (-1, -1), 11),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B8C7D3")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([tutor_table, Spacer(1, 13), Paragraph("Pricing", styles["Section"]), Spacer(1, 5)])

    pricing = [
        ["Format", "School level", "University level"],
        ["Private, 60 minutes", "USD 28", "USD 35"],
        ["Small group, per student", "USD 16", "USD 20"],
        ["Programming Foundations", "USD 110 per student", "6 small-group sessions"],
    ]
    price_table = Table(pricing, colWidths=[3.1 * inch, 1.95 * inch, 1.95 * inch], repeatRows=1)
    price_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.6),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B8C7D3")),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.extend([
        price_table,
        Spacer(1, 8),
        Paragraph(
            "A free 15-minute placement call is available. It is not a free tutoring lesson. "
            "Payment is due before a lesson or package begins.", styles["Small"],
        ),
        Spacer(1, 12),
        section(
            "Schedule and delivery",
            "Monday-Friday: 3:00 p.m.-9:00 p.m. | Saturday: 9:00 a.m.-5:00 p.m. | "
            "Sunday: closed. Times use the Beirut time zone. Lessons are available online or at "
            "the fictional Hamra center. All tutor assignments and bookings require staff confirmation.", styles,
        ),
        section(
            "Unique value proposition",
            "BrightPath uses a Learn-Practice-Reflect method. Tutors explain concepts in plain "
            "language, guide the student through practice, and end each session with a short progress "
            "note and a clear next-step plan.", styles,
        ),
        section(
            "Policies and boundaries",
            "Groups contain two to four students at a similar level. A lesson cancelled at least 24 "
            "hours in advance may be rescheduled once without charge; later cancellations are charged "
            "in full except for documented emergencies. BrightPath does not guarantee grades or exam "
            "results. A parent or guardian must confirm enrollment and payment for students under 18. "
            "Chemistry, biology, medicine, and advanced graduate research are not currently offered.", styles,
        ),
        section(
            "Enrollment and contact",
            "Prospective students should provide their name, email, subject, academic level, goals, "
            "preferred format, and preferred schedule. Email: hello@brightpathtutoring.example | "
            "Telephone: +961 1 555 014. All contact details and the business are fictional and exist "
            "only for this academic project.", styles,
        ),
    ])
    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build_pdf()
