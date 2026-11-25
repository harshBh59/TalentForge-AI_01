"""
Generates a formatted .docx resume from structured builder data, and a
plain-text rendering of the same data (so it can be run back through the
existing resume parser/scorer for a consistency check).
"""

from __future__ import annotations

import io

from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH


def _add_heading(document: Document, text: str):
    heading = document.add_heading(text.upper(), level=2)
    heading.runs[0].font.color.rgb = RGBColor(0x1F, 0x3B, 0x57)


def build_resume_docx(data: dict) -> bytes:
    """data keys: full_name, email, phone, location, linkedin, summary,
    skills (list[str]), experience (list[dict]), education (list[dict]),
    certifications (list[str])
    """
    document = Document()

    style = document.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10.5)

    # --- Header ---
    name_para = document.add_paragraph()
    name_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    name_run = name_para.add_run(data.get("full_name", "").strip() or "Your Name")
    name_run.bold = True
    name_run.font.size = Pt(20)

    contact_bits = [b for b in [
        data.get("email"), data.get("phone"), data.get("location"), data.get("linkedin"),
    ] if b]
    if contact_bits:
        contact_para = document.add_paragraph(" | ".join(contact_bits))
        contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # --- Summary ---
    if data.get("summary", "").strip():
        _add_heading(document, "Summary")
        document.add_paragraph(data["summary"].strip())

    # --- Skills ---
    skills = [s.strip() for s in data.get("skills", []) if s.strip()]
    if skills:
        _add_heading(document, "Skills")
        document.add_paragraph(" • ".join(skills))

    # --- Experience ---
    experience = [e for e in data.get("experience", []) if e.get("title") or e.get("company")]
    if experience:
        _add_heading(document, "Experience")
        for entry in experience:
            title_line = document.add_paragraph()
            title_run = title_line.add_run(
                f"{entry.get('title', '')} — {entry.get('company', '')}".strip(" —")
            )
            title_run.bold = True

            meta_bits = [b for b in [entry.get("location"),
                                      f"{entry.get('start', '')} – {entry.get('end', '')}"
                                      if entry.get("start") or entry.get("end") else None]
                         if b]
            if meta_bits:
                meta_para = document.add_paragraph(" · ".join(meta_bits))
                meta_para.runs[0].italic = True

            for bullet in entry.get("bullets", []):
                bullet = bullet.strip()
                if bullet:
                    document.add_paragraph(bullet, style="List Bullet")

    # --- Education ---
    education = [e for e in data.get("education", []) if e.get("degree") or e.get("institution")]
    if education:
        _add_heading(document, "Education")
        for entry in education:
            title_line = document.add_paragraph()
            title_run = title_line.add_run(
                f"{entry.get('degree', '')} — {entry.get('institution', '')}".strip(" —")
            )
            title_run.bold = True

            meta_bits = [b for b in [entry.get("location"),
                                      f"{entry.get('start', '')} – {entry.get('end', '')}"
                                      if entry.get("start") or entry.get("end") else None]
                         if b]
            if meta_bits:
                meta_para = document.add_paragraph(" · ".join(meta_bits))
                meta_para.runs[0].italic = True

            if entry.get("details", "").strip():
                document.add_paragraph(entry["details"].strip())

    # --- Certifications ---
    certifications = [c.strip() for c in data.get("certifications", []) if c.strip()]
    if certifications:
        _add_heading(document, "Certifications")
        for cert in certifications:
            document.add_paragraph(cert, style="List Bullet")

    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def build_resume_plain_text(data: dict) -> str:
    """Plain-text rendering of the same data, used to feed the existing
    nlp.resume_parser / ml.resume_scorer pipeline for a live score preview.
    """
    lines = []

    lines.append(data.get("full_name", ""))
    contact_bits = [b for b in [data.get("email"), data.get("phone"),
                                 data.get("location"), data.get("linkedin")] if b]
    lines.append(" | ".join(contact_bits))
    lines.append("")

    if data.get("summary", "").strip():
        lines.append("Summary")
        lines.append(data["summary"].strip())
        lines.append("")

    skills = [s.strip() for s in data.get("skills", []) if s.strip()]
    if skills:
        lines.append("Skills")
        lines.append(", ".join(skills))
        lines.append("")

    experience = [e for e in data.get("experience", []) if e.get("title") or e.get("company")]
    if experience:
        lines.append("Experience")
        for entry in experience:
            lines.append(f"{entry.get('title', '')} - {entry.get('company', '')} "
                          f"({entry.get('start', '')} - {entry.get('end', '')})")
            for bullet in entry.get("bullets", []):
                if bullet.strip():
                    lines.append(f"- {bullet.strip()}")
        lines.append("")

    education = [e for e in data.get("education", []) if e.get("degree") or e.get("institution")]
    if education:
        lines.append("Education")
        for entry in education:
            lines.append(f"{entry.get('degree', '')} - {entry.get('institution', '')} "
                          f"({entry.get('start', '')} - {entry.get('end', '')})")
        lines.append("")

    certifications = [c.strip() for c in data.get("certifications", []) if c.strip()]
    if certifications:
        lines.append("Certifications")
        lines.extend(certifications)

    return "\n".join(lines)
