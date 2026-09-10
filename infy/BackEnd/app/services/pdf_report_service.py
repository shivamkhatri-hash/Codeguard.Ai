import io
import datetime
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

from app.schemas.analysis import Finding
from app.services.agents.pr_summary_agent import pr_summary_agent


class PDFReportService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.title_style = ParagraphStyle(
            'DocTitle',
            parent=self.styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0f172a'),
            alignment=TA_LEFT,
            spaceAfter=4
        )
        self.subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#475569'),
            spaceAfter=15
        )
        self.section_heading = ParagraphStyle(
            'SectionHeading',
            parent=self.styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#0284c7'),
            spaceBefore=14,
            spaceAfter=8
        )
        self.body_style = ParagraphStyle(
            'BodyDark',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor('#1e293b')
        )
        self.code_style = ParagraphStyle(
            'CodeText',
            parent=self.styles['Normal'],
            fontName='Courier',
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor('#0f172a')
        )
        self.table_header_style = ParagraphStyle(
            'TableHeader',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=11,
            textColor=colors.HexColor('#0f172a')
        )
        self.table_cell_style = ParagraphStyle(
            'TableCell',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor('#334155')
        )
        self.badge_high = ParagraphStyle(
            'BadgeHigh',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#e11d48')
        )
        self.badge_medium = ParagraphStyle(
            'BadgeMedium',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#d97706')
        )
        self.badge_low = ParagraphStyle(
            'BadgeLow',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#0284c7')
        )

    def generate_pdf(
        self,
        analysis_id: str,
        filename: str,
        language: str,
        code: str,
        findings: List[Finding],
        remediations: List[Dict[str, Any]] = None
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        elements = []

        # Compile PR summary for health score & roadmap
        pr_summary = pr_summary_agent.generate_summary(
            analysis_id=analysis_id,
            findings=findings,
            code=code,
            language=language
        )

        # -------------------------------------------------------------
        # 1. HEADER & COVER BRANDING
        # -------------------------------------------------------------
        elements.append(Paragraph("🛡️ Smart Code Inspection Report", self.title_style))
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elements.append(Paragraph(
            f"<b>Target File:</b> {filename} | <b>Language:</b> {language.upper()} | "
            f"<b>Analysis ID:</b> <code>{analysis_id}</code> | <b>Generated:</b> {date_str}",
            self.subtitle_style
        ))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=15))

        # -------------------------------------------------------------
        # 2. EXECUTIVE SUMMARY & CODE HEALTH SCORE GAUGE
        # -------------------------------------------------------------
        health_score = pr_summary.health_score
        verdict = pr_summary.verdict

        verdict_color = colors.HexColor('#059669') if health_score >= 80 else (
            colors.HexColor('#d97706') if health_score >= 60 else colors.HexColor('#e11d48')
        )

        score_p_style = ParagraphStyle(
            'ScoreBoxRight',
            parent=self.body_style,
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            alignment=TA_RIGHT
        )

        verdict_p_style = ParagraphStyle(
            'ScoreBoxLeft',
            parent=self.body_style,
            fontName='Helvetica',
            fontSize=9.5,
            leading=14,
            alignment=TA_LEFT
        )

        summary_box_data = [
            [
                Paragraph(f"<font size=8 color='#64748b'><b>OVERALL VERDICT</b></font><br/><font size=11 color='{verdict_color.hexval()}'><b>{verdict}</b></font>", verdict_p_style),
                Paragraph(f"<font size=18 color='{verdict_color.hexval()}'><b>{health_score}/100</b></font><br/><font size=8 color='#64748b'><b>CODE HEALTH SCORE</b></font>", score_p_style)
            ]
        ]
        summary_table = Table(summary_box_data, colWidths=[340, 200])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Executive Overview", self.section_heading))
        elements.append(Paragraph(pr_summary.executive_overview, self.body_style))
        elements.append(Spacer(1, 10))

        # -------------------------------------------------------------
        # 3. SEVERITY BREAKDOWN TABLE
        # -------------------------------------------------------------
        elements.append(Paragraph("Severity Breakdown", self.section_heading))
        sb = pr_summary.severity_breakdown
        breakdown_data = [
            [
                Paragraph("<b>High Severity Risks</b>", self.table_header_style),
                Paragraph("<b>Medium Severity Issues</b>", self.table_header_style),
                Paragraph("<b>Low / Code Smells</b>", self.table_header_style),
                Paragraph("<b>Total Findings</b>", self.table_header_style),
            ],
            [
                Paragraph(f"<font color='#e11d48'><b>{sb.high} High</b></font>", self.table_cell_style),
                Paragraph(f"<font color='#d97706'><b>{sb.medium} Medium</b></font>", self.table_cell_style),
                Paragraph(f"<font color='#0284c7'><b>{sb.low} Low</b></font>", self.table_cell_style),
                Paragraph(f"<b>{sb.total} Issues</b>", self.table_cell_style),
            ]
        ]
        breakdown_table = Table(breakdown_data, colWidths=[135, 135, 135, 135])
        breakdown_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(breakdown_table)
        elements.append(Spacer(1, 14))

        # -------------------------------------------------------------
        # 4. PRIORITIZED FIX CHECKLIST
        # -------------------------------------------------------------
        elements.append(Paragraph("Prioritized Fix Roadmap", self.section_heading))

        if pr_summary.prioritized_fixes:
            checklist_data = [
                [
                    Paragraph("<b>Rank</b>", self.table_header_style),
                    Paragraph("<b>Issue Title</b>", self.table_header_style),
                    Paragraph("<b>Line</b>", self.table_header_style),
                    Paragraph("<b>Severity</b>", self.table_header_style),
                    Paragraph("<b>Recommended Action</b>", self.table_header_style),
                ]
            ]
            for fix in pr_summary.prioritized_fixes:
                sev_style = (
                    self.badge_high if fix.severity.lower() == 'high'
                    else (self.badge_medium if fix.severity.lower() == 'medium' else self.badge_low)
                )
                checklist_data.append([
                    Paragraph(f"<b>#{fix.priority}</b>", self.table_cell_style),
                    Paragraph(f"<b>{fix.title}</b>", self.table_cell_style),
                    Paragraph(f"L{fix.line}", self.table_cell_style),
                    Paragraph(fix.severity.upper(), sev_style),
                    Paragraph(fix.action_required, self.table_cell_style),
                ])

            checklist_table = Table(checklist_data, colWidths=[35, 130, 45, 65, 265])
            checklist_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(checklist_table)
        else:
            elements.append(Paragraph("✓ No prioritized fixes required. Code is clean and safe.", self.body_style))

        elements.append(Spacer(1, 16))

        # -------------------------------------------------------------
        # 5. REMEDIATION & CORRECTED CODE ROADMAP
        # -------------------------------------------------------------
        if remediations and len(remediations) > 0:
            elements.append(Paragraph("AI Remediation Details & Corrected Code", self.section_heading))

            for idx, rem in enumerate(remediations, 1):
                finding = findings[idx - 1] if (findings and idx <= len(findings)) else None

                if isinstance(rem, dict):
                    title = rem.get("finding_title") or (finding.title if finding else f"Issue #{idx}")
                    line = rem.get("line") or (finding.line if finding else "?")
                    corrected_code = rem.get("corrected_code") or ""
                    explanation = rem.get("explanation") or (finding.description if finding else "")
                    why_it_works = rem.get("why_it_works") or rem.get("recommendation") or (finding.recommendation if finding else "")
                else:
                    title = getattr(rem, "finding_title", None) or (finding.title if finding else f"Issue #{idx}")
                    line = getattr(rem, "line", None) or (finding.line if finding else "?")
                    corrected_code = getattr(rem, "corrected_code", "") or ""
                    explanation = getattr(rem, "explanation", "") or (finding.description if finding else "")
                    why_it_works = getattr(rem, "why_it_works", "") or getattr(rem, "recommendation", "") or (finding.recommendation if finding else "")

                rem_block = []
                rem_block.append(Paragraph(f"<b>Finding #{idx}: {title} (Line {line})</b>", ParagraphStyle('RemTitle', parent=self.body_style, fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#0f172a'))))
                rem_block.append(Spacer(1, 4))
                if explanation:
                    rem_block.append(Paragraph(f"<b>Explanation:</b> {explanation}", self.body_style))
                    rem_block.append(Spacer(1, 3))

                if corrected_code:
                    code_p = Paragraph(f"<font fontName='Courier' size=8>{corrected_code.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>')}</font>", self.code_style)
                    code_table = Table([[code_p]], colWidths=[540])
                    code_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
                        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                        ('PADDING', (0, 0), (-1, -1), 8),
                    ]))
                    rem_block.append(code_table)
                    rem_block.append(Spacer(1, 4))

                if why_it_works:
                    rem_block.append(Paragraph(f"<b>Why It Works:</b> {why_it_works}", self.body_style))

                rem_block.append(Spacer(1, 10))
                elements.append(KeepTogether(rem_block))

        # Footer
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=15, spaceAfter=10))
        elements.append(Paragraph(
            "Generated by Smart Code Inspection Platform with Vulnerability Detection System • Enterprise Native PDF Module",
            ParagraphStyle('Footer', parent=self.body_style, fontSize=8, textColor=colors.HexColor('#94a3b8'), alignment=TA_CENTER)
        ))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()


pdf_report_service = PDFReportService()
