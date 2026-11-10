from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

import matplotlib.pyplot as plt

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, Image, KeepTogether
)
from reportlab.lib import colors
from reportlab.lib.styles import (
    getSampleStyleSheet, ParagraphStyle
)
from reportlab.lib.pagesizes import A4

# Oxivaryn colour palette

NAVY = colors.HexColor("#10283F")
TEAL = colors.HexColor("#087F83")
PALE = colors.HexColor("#EAF4F5")
GREY = colors.HexColor("#536476")


def generate_pdf_report(
    df, data_source, mae, stability,
    slope, status, explanation,
    time_unit="measurement",
    sensor_model="Not specified",
    sensor_id="Not specified",
    technician="Not specified",
    test_date=None,
    reference_source="Not specified",
    bias=None,
    max_error=None
):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=42,
        rightMargin=42,
        topMargin=42,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="OxyTitle",
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=32,
        textColor=NAVY,
        spaceAfter=5
    ))

    styles.add(ParagraphStyle(
        name="OxySubtitle",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=15,
        textColor=TEAL,
        spaceAfter=14
    ))

    styles.add(ParagraphStyle(
        name="OxySection",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=NAVY,
        spaceBefore=16,
        spaceAfter=9
    ))

    styles.add(ParagraphStyle(
        name="OxyBody",
        fontSize=9,
        leading=14,
        textColor=GREY
    ))

    styles.add(ParagraphStyle(
        name="OxySmall",
        fontSize=8,
        leading=12,
        textColor=GREY
    ))

    styles.add(ParagraphStyle(
        name="OxyAssessment",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=17,
        textColor=TEAL
    ))

    story = []

    def section(title):
        story.append(
            Paragraph(title, styles["OxySection"])
        )

    def safe(value):
        return escape(str(value))

    def make_table(rows, widths=None):
        table = Table(
            rows,
            colWidths=widths or [250, 250],
            hAlign="LEFT"
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, PALE]),
            ("TEXTCOLOR", (0, 1), (-1, -1), NAVY),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))

        return table

    def make_chart(y_values, title, ylabel,
                   color, reference=None):

        fig, ax = plt.subplots(figsize=(8, 3.2))

        if reference is not None:
            ax.plot(
                df["Time"],
                reference,
                label="Reference Oxygen",
                color="#087F83",
                linestyle="--",
                linewidth=2
            )

        ax.plot(
            df["Time"],
            y_values,
            label=title,
            color=color,
            linewidth=1.8
        )

        ax.set_xlabel(f"Time ({time_unit})")
        ax.set_ylabel(ylabel)
        ax.grid(alpha=0.2)
        ax.legend(frameon=False)

        fig.tight_layout()

        chart_buffer = BytesIO()

        fig.savefig(
            chart_buffer,
            format="png",
            dpi=180
        )

        plt.close(fig)
        chart_buffer.seek(0)

        return Image(
            chart_buffer,
            width=490,
            height=196
        )

    # HEADER
    story.append(
        Paragraph("Oxivaryn", styles["OxyTitle"])
    )

    story.append(Paragraph(
        "OXYGEN SENSOR PERFORMANCE REPORT",
        styles["OxySubtitle"]
    ))

    story.append(Spacer(1, 8))

    story.append(Paragraph(
        f"Report generated: {datetime.now():%d %B %Y, %H:%M}",
        styles["OxySmall"]
    ))

    # SECTION 1
    section("01 | TEST INFORMATION")

    if test_date is None:
        test_date = "Not specified"

    info = [
        ["PARAMETER", "DETAIL"],
        ["Data Source", safe(data_source)],
        ["Sensor Model", safe(sensor_model)],
        ["Sensor ID", safe(sensor_id)],
        ["Test Operator", safe(technician)],
        ["Test Date", safe(test_date)],
        ["Measurements", str(len(df))],
        ["Time Unit", safe(time_unit)]
    ]

    story.append(make_table(info))

    # SECTION 2
    section("02 | REFERENCE INFORMATION")

    story.append(Paragraph(
        f"<b>Reference Source:</b> {safe(reference_source)}",
        styles["OxyBody"]
    ))

    story.append(Paragraph(
        f"<b>Mean Reference Oxygen:</b> "
        f"{df['Reference_Oxygen'].mean():.2f}%",
        styles["OxyBody"]
    ))

    # SECTION 3
    section("03 | PERFORMANCE METRICS")

    metrics = [
        ["METRIC", "RESULT"],
        ["Mean Absolute Error", f"{mae:.3f} pp"],
        ["Stability (Residual SD)", f"{stability:.3f} pp"],
        ["Drift Slope", f"{slope:.4f} pp/{time_unit}"],
        [
            "Mean Signed Error (Bias)",
            f"{bias:.3f} pp" if bias is not None
            else "Not available"
        ],
        [
            "Maximum Absolute Error",
            f"{max_error:.3f} pp" if max_error is not None
            else "Not available"
        ]
    ]

    story.append(make_table(metrics))

    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Units and Terminology:</b> "
        "pp means percentage points. "
        "For example, a difference between 40% "
        "and 38% oxygen is 2 pp. "
        "Drift slope is expressed in pp per "
        "selected time unit.",
        styles["OxySmall"]
    ))

    # SECTION 4
    section("04 | OXYGEN MEASUREMENT TRENDS")

    story.append(make_chart(
        df["Sensor_Reading"],
        "Sensor Reading",
        "Oxygen Concentration (%)",
        "#E49A46",
        reference=df["Reference_Oxygen"]
    ))

    # SECTION 5
    section("05 | MEASUREMENT ERROR ANALYSIS")

    measurement_error = (
        df["Sensor_Reading"] - df["Reference_Oxygen"]
    )

    story.append(make_chart(
        measurement_error,
        "Measurement Error",
        "Measurement Error (pp)",
        "#D65A5A"
    ))

    story.append(Paragraph(
        "Measurement error = sensor reading minus "
        "reference oxygen. Negative values indicate "
        "under-reading relative to the reference.",
        styles["OxySmall"]
    ))

    # SECTION 6
    section("06 | PERFORMANCE ASSESSMENT")

    story.append(KeepTogether([
        Paragraph(
            safe(status),
            styles["OxyAssessment"]
        ),
        Spacer(1, 7),
        Paragraph(
            safe(explanation),
            styles["OxyBody"]
        )
    ]))

    # SECTION 7
    section("07 | LIMITATIONS")

    story.append(Paragraph(
        "Oxivaryn is an educational research prototype. "
        "Its experimental classifications are not "
        "manufacturer-approved acceptance criteria. "
        "Reference measurements are not independently "
        "verified by the software. "
        "The results must not be used for clinical "
        "decisions or approval of medical equipment "
        "for service.",
        styles["OxySmall"]
    ))

    # FOOTER
    def footer(canvas, document):
        canvas.setStrokeColor(TEAL)

        canvas.line(
            42, 35,
            A4[0] - 42, 35
        )

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GREY)

        canvas.drawString(
            42, 23,
            "Oxivaryn | Research Prototype created by Matheesha Bandara"
        )

        canvas.drawRightString(
            A4[0] - 42, 23,
            f"Page {document.page}"
        )

    doc.build(
        story,
        onFirstPage=footer,
        onLaterPages=footer
    )

    buffer.seek(0)

    return buffer.getvalue()
