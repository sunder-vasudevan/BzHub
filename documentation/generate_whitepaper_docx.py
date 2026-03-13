#!/usr/bin/env python3
"""
Generates a McKinsey/PwC-style Word document for the BzHub Efficiency White Paper.
Run: python3 documentation/generate_whitepaper_docx.py
Output: documentation/BzHub_Efficiency_WhitePaper.docx
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ── Colour palette stored as (r, g, b) tuples ────────────────────────────────
# Use rgb(*DARK_NAVY) when passing to font.color.rgb; use hex_color() for XML.
DARK_NAVY   = (0x00, 0x2B, 0x5C)   # deep navy — headings, cover
MID_BLUE    = (0x00, 0x5B, 0x99)   # section rules, table headers
ACCENT_TEAL = (0x00, 0x7A, 0x87)   # pull-out boxes
LIGHT_GREY  = (0xF2, 0xF4, 0xF7)   # table row fill
WHITE       = (0xFF, 0xFF, 0xFF)
DARK_TEXT   = (0x1A, 0x1A, 0x2E)
RULE_BLUE   = (0x00, 0x5B, 0x99)


def rgb(t):
    """Convert (r,g,b) tuple to RGBColor."""
    return RGBColor(t[0], t[1], t[2])


def hex_color(t):
    """Convert (r,g,b) tuple to uppercase hex string for XML attributes."""
    return f"{t[0]:02X}{t[1]:02X}{t[2]:02X}"


# ── Helpers ───────────────────────────────────────────────────────────────────

def set_cell_bg(cell, color_tuple):
    """Fill a table cell with a solid background colour."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color(color_tuple))
    tcPr.append(shd)


def add_horizontal_rule(doc, color=RULE_BLUE, thickness_pt: int = 12):
    """Add a coloured horizontal rule paragraph."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(6)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), str(thickness_pt))
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), hex_color(color))
    pBdr.append(bottom)
    pPr.append(pBdr)
    return p


def set_run_font(run, name='Calibri', size_pt=10, bold=False, italic=False,
                 color=None):
    run.font.name = name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = rgb(color)


def heading1(doc, text):
    """Section heading — large, navy, with rule below."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    set_run_font(run, name='Calibri', size_pt=16, bold=True, color=DARK_NAVY)
    add_horizontal_rule(doc, color=MID_BLUE, thickness_pt=8)
    return p


def heading2(doc, text):
    """Sub-section heading."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run(text)
    set_run_font(run, name='Calibri', size_pt=12, bold=True, color=MID_BLUE)
    return p


def body(doc, text, space_after=6):
    """Standard body paragraph."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    set_run_font(run, name='Calibri', size_pt=10, color=DARK_TEXT)
    return p


def bullet(doc, text, level=0):
    """Bullet point."""
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.left_indent = Cm(0.8 + level * 0.5)
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    set_run_font(run, name='Calibri', size_pt=10, color=DARK_TEXT)
    return p


def callout_box(doc, text, label='KEY FINDING'):
    """Teal accent box for key insights."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_bg(cell, (0xE8, 0xF4, 0xF6))
    cell.width = Inches(6)
    # Left border accent
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single')
    left.set(qn('w:sz'), '24')
    left.set(qn('w:color'), hex_color(ACCENT_TEAL))
    tcBorders.append(left)
    tcPr.append(tcBorders)

    p_label = cell.paragraphs[0]
    p_label.paragraph_format.space_before = Pt(4)
    p_label.paragraph_format.space_after = Pt(2)
    r_label = p_label.add_run(label)
    set_run_font(r_label, name='Calibri', size_pt=8, bold=True, color=ACCENT_TEAL)

    p_text = cell.add_paragraph()
    p_text.paragraph_format.space_before = Pt(2)
    p_text.paragraph_format.space_after = Pt(6)
    r_text = p_text.add_run(text)
    set_run_font(r_text, name='Calibri', size_pt=10.5, italic=True, color=DARK_NAVY)
    doc.add_paragraph()


def styled_table(doc, headers, rows, col_widths_cm=None):
    """
    Build a styled table with navy header row and alternating grey rows.
    headers: list of str
    rows: list of list of str
    """
    n_cols = len(headers)
    tbl = doc.add_table(rows=1 + len(rows), cols=n_cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.style = 'Table Grid'

    # Header row
    hdr_cells = tbl.rows[0].cells
    for i, h in enumerate(headers):
        set_cell_bg(hdr_cells[i], MID_BLUE)
        p = hdr_cells[i].paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(h)
        set_run_font(run, name='Calibri', size_pt=9, bold=True, color=WHITE)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # Data rows
    for r_idx, row_data in enumerate(rows):
        row_cells = tbl.rows[r_idx + 1].cells
        bg = LIGHT_GREY if r_idx % 2 == 0 else WHITE
        for c_idx, cell_text in enumerate(row_data):
            set_cell_bg(row_cells[c_idx], bg)
            p = row_cells[c_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            run = p.add_run(str(cell_text))
            set_run_font(run, name='Calibri', size_pt=9, color=DARK_TEXT)

    # Column widths
    if col_widths_cm:
        for row in tbl.rows:
            for i, cell in enumerate(row.cells):
                if i < len(col_widths_cm):
                    cell.width = Cm(col_widths_cm[i])

    doc.add_paragraph()
    return tbl


# ── Footer & ToC helpers ──────────────────────────────────────────────────────

def add_footer(doc):
    """Add page numbers (centre) + copyright line (right) to every section footer."""
    for section in doc.sections:
        footer = section.footer
        footer.is_linked_to_previous = False

        # Single paragraph: copyright left | page number centre
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.clear()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after  = Pt(0)

        # Tab stops: centre at 8.2 cm, right at 16.4 cm
        from docx.oxml import OxmlElement as OE
        pPr = p._p.get_or_add_pPr()
        tabs = OE('w:tabs')
        for pos_twips, align in [("4640", "center"), ("9280", "right")]:
            tab = OE('w:tab')
            tab.set(qn('w:val'), align)
            tab.set(qn('w:pos'), pos_twips)
            tabs.append(tab)
        pPr.append(tabs)

        # Copyright (left)
        r_copy = p.add_run("© 2026 sunder-vasudevan. All rights reserved.")
        set_run_font(r_copy, name='Calibri', size_pt=8, color=(0x88, 0x88, 0x88))

        # Tab to centre
        p.add_run("\t")

        # Page number field: "Page X of Y"
        r_pre = p.add_run("Page ")
        set_run_font(r_pre, name='Calibri', size_pt=8, color=(0x88, 0x88, 0x88))

        def _fld(name):
            fld = OE('w:fldSimple')
            fld.set(qn('w:instr'), f' {name} ')
            r = OE('w:r')
            rpr = OE('w:rPr')
            sz = OE('w:sz')
            sz.set(qn('w:val'), '16')
            rpr.append(sz)
            r.append(rpr)
            t = OE('w:t')
            t.text = name
            r.append(t)
            fld.append(r)
            return fld

        p._p.append(_fld('PAGE'))
        r_of = p.add_run(" of ")
        set_run_font(r_of, name='Calibri', size_pt=8, color=(0x88, 0x88, 0x88))
        p._p.append(_fld('NUMPAGES'))

        # Tab to right — BzHub label
        r_tab2 = p.add_run("\t")
        r_brand = p.add_run("BzHub Efficiency Case Study")
        set_run_font(r_brand, name='Calibri', size_pt=8, italic=True,
                     color=(0x00, 0x5B, 0x99))

        # Top border on footer paragraph
        pBdr = OE('w:pBdr')
        top = OE('w:top')
        top.set(qn('w:val'), 'single')
        top.set(qn('w:sz'), '4')
        top.set(qn('w:space'), '1')
        top.set(qn('w:color'), hex_color(MID_BLUE))
        pBdr.append(top)
        pPr.append(pBdr)


def add_toc(doc):
    """Insert a Table of Contents page using Word's TOC field (auto-updates on open)."""
    # Heading
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after  = Pt(6)
    r_title = p_title.add_run("Table of Contents")
    set_run_font(r_title, name='Calibri', size_pt=16, bold=True, color=DARK_NAVY)
    add_horizontal_rule(doc, color=MID_BLUE, thickness_pt=8)

    # Instruction note
    p_note = doc.add_paragraph()
    r_note = p_note.add_run(
        "Right-click this table and select 'Update Field' to refresh page numbers after opening.")
    set_run_font(r_note, name='Calibri', size_pt=8, italic=True,
                 color=(0x88, 0x88, 0x88))
    p_note.paragraph_format.space_after = Pt(8)

    # TOC field paragraph
    p_toc = doc.add_paragraph()
    p_toc.paragraph_format.space_before = Pt(0)
    p_toc.paragraph_format.space_after  = Pt(0)

    run = p_toc.add_run()
    fld_begin = OxmlElement('w:fldChar')
    fld_begin.set(qn('w:fldCharType'), 'begin')
    run._r.append(fld_begin)

    run2 = p_toc.add_run()
    instr = OxmlElement('w:instrText')
    instr.set(qn('xml:space'), 'preserve')
    instr.text = ' TOC \\o "1-2" \\h \\z \\u '
    run2._r.append(instr)

    run3 = p_toc.add_run()
    fld_sep = OxmlElement('w:fldChar')
    fld_sep.set(qn('w:fldCharType'), 'separate')
    run3._r.append(fld_sep)

    run4 = p_toc.add_run()
    placeholder = OxmlElement('w:t')
    placeholder.text = '[Table of contents — update field in Word to populate]'
    run4._r.append(placeholder)
    set_run_font(run4, name='Calibri', size_pt=9, italic=True,
                 color=(0x88, 0x88, 0x88))

    run5 = p_toc.add_run()
    fld_end = OxmlElement('w:fldChar')
    fld_end.set(qn('w:fldCharType'), 'end')
    run5._r.append(fld_end)

    # Page break after ToC
    doc.add_page_break()


# ── Document assembly ─────────────────────────────────────────────────────────

def build_document():
    doc = Document()

    # Page margins
    for section in doc.sections:
        section.top_margin    = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin   = Cm(2.5)
        section.right_margin  = Cm(2.5)

    # ── COVER PAGE ────────────────────────────────────────────────────────────

    # Top navy band (simulated with a 1-col table)
    cover_band = doc.add_table(rows=1, cols=1)
    cover_cell = cover_band.cell(0, 0)
    set_cell_bg(cover_cell, DARK_NAVY)
    p_band = cover_cell.paragraphs[0]
    p_band.paragraph_format.space_before = Pt(18)
    p_band.paragraph_format.space_after = Pt(18)
    r = p_band.add_run("  ENGINEERING EFFICIENCY WITH AI PAIR PROGRAMMING")
    set_run_font(r, name='Calibri', size_pt=18, bold=True, color=WHITE)

    doc.add_paragraph()

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_sub = p_sub.add_run("A Case Study of BzHub — One Product Owner, One Claude")
    set_run_font(r_sub, name='Calibri', size_pt=14, bold=False, color=MID_BLUE)

    doc.add_paragraph()

    # Meta block
    meta_tbl = doc.add_table(rows=4, cols=2)
    meta_data = [
        ("Author", "sunder-vasudevan"),
        ("Date", "March 2026"),
        ("Version", "1.0"),
        ("Audience", "Technical peers — software engineers, engineering leads, technical founders"),
    ]
    for i, (k, v) in enumerate(meta_data):
        cells = meta_tbl.rows[i].cells
        r_key = cells[0].paragraphs[0].add_run(k)
        set_run_font(r_key, name='Calibri', size_pt=9, bold=True, color=MID_BLUE)
        cells[0].width = Cm(3.5)
        r_val = cells[1].paragraphs[0].add_run(v)
        set_run_font(r_val, name='Calibri', size_pt=9, color=DARK_TEXT)

    doc.add_paragraph()
    add_horizontal_rule(doc, color=MID_BLUE, thickness_pt=16)
    doc.add_page_break()

    # ── TABLE OF CONTENTS ────────────────────────────────────────────────────

    add_toc(doc)

    # ── ABSTRACT ─────────────────────────────────────────────────────────────

    heading1(doc, "Abstract")
    body(doc,
         "This paper documents a real-world experiment: a single Product Owner building BzHub — "
         "a full-stack ERP web application — in collaboration with Claude (Anthropic's AI assistant) "
         "as a persistent pair-programmer. Over 31 calendar days (~10 active coding days), the pair "
         "shipped 9 production releases, migrated across 3 architectural paradigms, and delivered "
         "8 live product modules spanning ~12,600 lines of net new application code. When compared "
         "against the output a traditional 3-person startup development team would reasonably produce "
         "in the same calendar window, the evidence suggests a 2–3x velocity multiplier — consistent "
         "with the Product Owner's own self-assessment. This paper analyses that claim using concrete "
         "git-derived data, identifies where the gains came from, and honestly acknowledges what this "
         "model does not replace.")

    # ── 1. INTRODUCTION ───────────────────────────────────────────────────────

    heading1(doc, "1. Introduction — The Experiment")
    body(doc,
         "Most AI-assisted development studies focus on narrow tasks: code completion accuracy, "
         "bug fix rates, test generation. This case study is different. It examines an end-to-end "
         "product build: ideation, architecture, feature development, cloud deployment, and "
         "documentation — all executed by a single Product Owner with Claude as an active collaborator.")

    heading2(doc, "The Question")
    body(doc,
         "When one capable Product Owner pairs with Claude as a full-session collaborator (not just "
         "a code autocomplete tool), does the output more closely resemble a solo effort or a small team?")

    heading2(doc, "What 'Efficiency' Means Here")
    for item in [
        "Feature throughput per calendar day",
        "Architectural scope delivered without accruing uncontrolled technical debt",
        "Code quality signals visible in git history",
        "Documentation discipline sustained throughout",
    ]:
        bullet(doc, item)

    heading2(doc, "Why It Matters for Technical Teams")
    body(doc,
         "AI pair-programming is often evaluated as a tool for individual tasks. This study argues "
         "the real leverage is at the workflow level — persistent context, zero handoff overhead, "
         "and on-demand expertise across the full stack.")

    # ── 2. PROJECT SCOPE ──────────────────────────────────────────────────────

    heading1(doc, "2. Project Scope — What Was Built")
    body(doc,
         "BzHub is a full-stack business management (ERP) web application targeting small-to-medium "
         "businesses. It is Odoo-inspired, with a goal of becoming a multi-tenant SaaS product.")

    heading2(doc, "Technology Stack")
    styled_table(doc,
        headers=["Layer", "Technology"],
        rows=[
            ("Frontend",    "Next.js 14 (App Router), Tailwind CSS, shadcn/ui"),
            ("Database",    "Supabase (PostgreSQL), Row Level Security enabled"),
            ("Deployment",  "Vercel (CI/CD on every push to main)"),
            ("Language",    "TypeScript throughout"),
        ],
        col_widths_cm=[4, 12]
    )

    heading2(doc, "Live Modules at v4.5.0")
    styled_table(doc,
        headers=["Module", "Key Features"],
        rows=[
            ("Dashboard",              "KPI cards, sales trend chart, fast/slow movers analytics"),
            ("Operations",             "Inventory, POS, Bills, Supplier management, Purchase Orders"),
            ("HR",                     "Employees, Payroll, Goals, Appraisals, Skills Matrix, Leave Requests"),
            ("CRM",                    "Contacts, Leads, Kanban pipeline, lead scoring, follow-ups"),
            ("Reports",                "Sales Report, Top Sellers chart, Inventory Report"),
            ("Settings",               "Company info, currency selector"),
            ("Help",                   "In-app user guide for all modules"),
            ("Employee Self-Service",  "My Goals, My Appraisals, My Leave, My Skills"),
        ],
        col_widths_cm=[4.5, 11.5]
    )

    heading2(doc, "Architecture Evolution")
    body(doc, "The project underwent 3 full architectural paradigm shifts:")
    styled_table(doc,
        headers=["Stage", "Architecture"],
        rows=[
            ("v1.0",  "Desktop app (Tkinter / Python)"),
            ("v2.0",  "Next.js web frontend + FastAPI backend + SQLite"),
            ("v4.0+", "Next.js + Supabase (PostgreSQL) + Vercel (cloud)"),
        ],
        col_widths_cm=[3, 13]
    )
    body(doc, "Each migration was deliberate, documented, and left the codebase in a stable, deployable state.")

    # ── 3. METHODOLOGY ────────────────────────────────────────────────────────

    heading1(doc, "3. Methodology — How Efficiency Is Measured")

    heading2(doc, "Primary Metric: Feature Throughput per Engineer-Day")
    body(doc,
         "The key measure is how many meaningful product features were shipped per active coding day, "
         "compared to what a small team would typically ship in the same calendar window.")

    heading2(doc, "Secondary Metrics")
    for item in [
        "Commit frequency — intensity of active days",
        "Lines of code per feature commit — size and completeness of deliveries",
        "Architectural scope per sprint — how many layers were touched in a single session",
        "Documentation signal — release notes and help pages updated per feature",
    ]:
        bullet(doc, item)

    heading2(doc, "Comparison Baseline: Traditional 3-Person Startup Team")
    body(doc, "The baseline models a typical 3-person startup team:")
    for item in [
        "1 frontend engineer",
        "1 backend engineer",
        "1 tech lead / product manager",
    ]:
        bullet(doc, item)
    body(doc,
         "Typical output for such a team in a 2-week sprint: 2–4 significant features to production, "
         "with 15–25% of time consumed by ceremonies, code review, and coordination. Architecture "
         "migrations are treated as dedicated sprint work, not background activity.")

    heading2(doc, "Data Sources")
    styled_table(doc,
        headers=["Source", "Data Captured"],
        rows=[
            ("git log --shortstat",       "Commit messages, dates, file counts, lines added/deleted"),
            ("Product Owner self-assessment", "Stated 2–3x velocity multiplier vs. working without AI"),
        ],
        col_widths_cm=[5, 11]
    )

    heading2(doc, "Acknowledged Limitations")
    for item in [
        "No formal time-tracking — active coding days inferred from commit timestamps",
        "Not all commits are equal — two node_modules commits (millions of lines) excluded from LOC counts",
        "LOC is an imperfect complexity proxy — a 50-line schema change can unlock more than 500 lines of UI",
        "Greenfield product — results may differ in large legacy codebases",
    ]:
        bullet(doc, item)

    # ── 4. TIMELINE & VELOCITY ────────────────────────────────────────────────

    heading1(doc, "4. Timeline & Velocity Analysis")

    heading2(doc, "Commit Activity by Date")
    styled_table(doc,
        headers=["Date", "Commits", "Notes"],
        rows=[
            ("2026-02-10", "3",  "Project initialisation"),
            ("2026-02-16", "1",  "Stability pass"),
            ("2026-02-17", "1",  "Bug fixes"),
            ("2026-02-18", "8",  "Architecture sprint — FastAPI, Supabase, Next.js scaffolding"),
            ("2026-02-19", "3",  "CRM features, v2.0 release notes"),
            ("2026-03-09", "1",  "v3.0 release tag"),
            ("2026-03-10", "17", "PEAK — full UI build, CRM, HR, Settings, production shadcn/ui"),
            ("2026-03-11", "16", "PEAK — Vercel deploy, Supabase integration, v4.x features"),
            ("2026-03-12", "2",  "Approval workflows, Employee Portal"),
        ],
        col_widths_cm=[3.5, 2.5, 10]
    )
    body(doc,
         "33 of 52 commits (63%) occurred across just 2 days — not a sign of erratic work, but of "
         "sustained high-intensity sessions enabled by Claude's ability to hold architectural context "
         "without cognitive fatigue.")

    heading2(doc, "Milestone-by-Milestone Breakdown")
    styled_table(doc,
        headers=["Release", "Date", "Key Output", "Files", "Insertions"],
        rows=[
            ("v1.0",    "Feb 10–16", "Desktop app, login, sidebar, core UI",                       "—",  "—"),
            ("v2.0",    "Feb 18–19", "CRM module, FastAPI backend, Next.js web frontend",           "41", "3,860"),
            ("v3.0–3.1","Mar 9–10",  "Odoo CRM, Kanban, lead scoring, production shadcn/ui",       "23", "2,368"),
            ("v4.0",    "Mar 10–11", "Inventory image upload, sortable tables, fast/slow movers",   "4",  "369"),
            ("v4.1.x",  "Mar 11",    "Vercel deploy, Supabase integration, mobile responsive",      "11", "440"),
            ("v4.2.0",  "Mar 11",    "Reports page, Supplier management",                           "5",  "699"),
            ("v4.3.0",  "Mar 11",    "Goals, Appraisals, Skills Matrix — 13 new DB functions",      "2",  "1,302"),
            ("v4.4.0",  "Mar 12",    "3 Approval workflows + new DB tables",                        "9",  "1,209"),
            ("v4.5.0",  "Mar 12",    "Employee Self-Service Portal (4 tabs)",                       "6",  "667"),
        ],
        col_widths_cm=[2.2, 2.4, 8.0, 1.7, 2.2]
    )

    # ── 5. COMPARATIVE ANALYSIS ───────────────────────────────────────────────

    heading1(doc, "5. Comparative Analysis")

    heading2(doc, "The Two-Day Sprint Block (Mar 11–12)")
    body(doc,
         "The clearest evidence of velocity is the Mar 11–12 window. In approximately 48 hours:")
    styled_table(doc,
        headers=["Release", "Feature", "Net LOC"],
        rows=[
            ("v4.1.x", "Cloud deployment + mobile responsive",        "~495"),
            ("v4.2.0", "Reports page + Supplier management",          "699"),
            ("v4.3.0", "Goals, Appraisals, Skills Matrix",            "1,302"),
            ("v4.4.0", "3 Approval workflows + DB schema",            "1,209"),
            ("v4.5.0", "Employee Self-Service Portal",                "667"),
            ("TOTAL",  "5 production releases, 6 cross-layer features", "~4,372"),
        ],
        col_widths_cm=[2.5, 9.5, 4.0]
    )

    callout_box(doc,
        "For a 3-person startup team, this block of work — spanning UI, data layer, DB schema design, "
        "cloud deployment, and documentation — would realistically require 1–2 two-week sprints "
        "(3–4 calendar weeks). The AI-assisted pair compressed it to 48 hours.",
        label="KEY FINDING")

    heading2(doc, "Full Project Window Comparison")
    styled_table(doc,
        headers=["Dimension", "1 Product Owner + Claude (31 days)", "3-Person Team (31 days, estimated)"],
        rows=[
            ("Major releases shipped",    "9 (v1.0 → v4.5.0)",           "3–5 (1–2 per 2-week sprint)"),
            ("Architecture migrations",   "3 full paradigm shifts",        "Likely 1 (or as a dedicated project)"),
            ("Live modules delivered",    "8",                             "4–6"),
            ("Documentation maintained", "Per-feature (project rule)",    "Varies — often deferred"),
            ("Deployment pipeline",      "Fully automated (Vercel CI/CD)","2–5 days setup time for a team"),
        ],
        col_widths_cm=[4.5, 6.0, 5.5]
    )
    body(doc, "3-person team estimates are based on conventional startup sprint norms, not empirical benchmarks.",
         space_after=4)

    heading2(doc, "Where the Gains Come From")
    body(doc, "The efficiency delta is not simply 'Claude writes code faster.' The compounding advantages are structural:")

    for label, desc in [
        ("Zero handoff overhead",
         "In a team, frontend and backend engineers coordinate through PRs, Slack, standup, and specs. "
         "Each handoff has a latency cost. The AI pair eliminates this entirely — full-stack features "
         "are conceived, designed, and implemented in a single uninterrupted session."),
        ("Persistent context across sessions",
         "The project uses a structured NOTES.md + memory file system to preserve project state between "
         "sessions. Claude resumes with full context — current version, pending features, known debt, "
         "architecture decisions — without onboarding overhead. A new team hire needs 1–2 weeks to "
         "reach this context depth."),
        ("On-demand full-stack competency",
         "No single engineer is equally strong across Next.js App Router, Supabase RLS design, "
         "Recharts, and mobile-first Tailwind layout. Claude provides competent first-draft "
         "implementations across all layers, which the Product Owner reviews and approves."),
        ("Documentation as a side-effect",
         "Every feature commit was accompanied by release notes, help page updates, and memory file "
         "updates. With Claude handling the mechanical writing, this discipline was sustained throughout "
         "— rare in solo projects and difficult to maintain in teams under delivery pressure."),
    ]:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(2)
        r_label = p.add_run(label + " — ")
        set_run_font(r_label, name='Calibri', size_pt=10, bold=True, color=DARK_NAVY)
        r_desc = p.add_run(desc)
        set_run_font(r_desc, name='Calibri', size_pt=10, color=DARK_TEXT)

    doc.add_paragraph()

    # ── 6. COLLABORATION PATTERNS ─────────────────────────────────────────────

    heading1(doc, "6. Collaboration Patterns Observed")

    heading2(doc, "How Claude Was Used")
    styled_table(doc,
        headers=["Task Category", "Examples from BzHub"],
        rows=[
            ("Feature design",     "DB schema, component structure, and state design before coding"),
            ("Code generation",    "Full page components — 1,300+ LOC in single sessions"),
            ("Architecture",       "FastAPI vs. Supabase direct client; Vercel deployment config"),
            ("Bug diagnosis",      "TypeScript errors, Supabase RLS issues, Next.js config problems"),
            ("Schema design",      "Supabase table definitions, RLS policies, migration scripts"),
            ("Documentation",      "Release notes, help page content, NOTES.md updates per feature"),
            ("Refactoring",        "shadcn/ui adoption decision, data layer abstraction"),
        ],
        col_widths_cm=[4.5, 11.5]
    )

    heading2(doc, "The Context Persistence System")
    body(doc,
         "A key enabler of sustained velocity was explicit context management — the equivalent of a "
         "living spec document that is always current and always read before work begins:")
    for item in [
        "chat_persistent_notes/NOTES.md — master project state, read at session start",
        "documentation/RELEASE_NOTES_v4.1.md — version history maintained per feature",
        ".claude/projects/.../memory/ — auto-memory files for project state and collaboration rules",
    ]:
        bullet(doc, item)
    body(doc,
         "Most teams attempt this with wikis or Confluence — and fail to maintain it. Encoding it as "
         "a session discipline with AI enforcement makes it sustainable.")

    heading2(doc, "Product Owner's Role")
    body(doc,
         "Claude does not replace product or engineering judgment. The Product Owner was responsible for:")
    for item in [
        "Product decisions — what to build, in what order, and what to defer",
        "Architecture calls — which tech stack, which migration path, which trade-offs to accept",
        "Quality gate — reviewing all generated code before committing",
        "Strategic direction — the WhatsApp-first, multi-tenant SaaS end goal shaping every feature",
    ]:
        bullet(doc, item)

    callout_box(doc,
        "Claude was the executor. The Product Owner was the director. "
        "The distinction matters for how teams should think about AI-assisted workflows.",
        label="KEY PRINCIPLE")

    # ── 7. CODE QUALITY ───────────────────────────────────────────────────────

    heading1(doc, "7. Code Quality & Architecture Observations")

    heading2(doc, "Architecture Was Not Sacrificed for Speed")
    body(doc,
         "Three architecture migrations in 31 days could suggest chaotic churning. The git history "
         "tells a different story:")
    for item in [
        "Each migration was preceded by a documented decision commit (e.g., 'docs: record UI modernisation decision — Option B')",
        "Each migration left the codebase in a stable, deployed state before the next one began",
        "Known technical debt was explicitly called out in code and docs rather than hidden",
    ]:
        bullet(doc, item)

    heading2(doc, "Documentation Discipline")
    body(doc, "A project rule was enforced after every feature — no exceptions:")
    for item in [
        "Mark feature done in FEATURE_REQUESTS_AND_BUGS.md",
        "Add version entry to RELEASE_NOTES_v4.1.md",
        "Update NOTES.md with current version and next priority",
        "Update memory files with project state",
        "Add help section to src/app/help/page.tsx",
    ]:
        bullet(doc, item)

    heading2(doc, "Intentional Debt Logged, Not Ignored")
    styled_table(doc,
        headers=["Known Gap", "Status", "Planned Resolution"],
        rows=[
            ("Authentication (hardcoded admin/admin123)", "Intentional — v1 scope", "FEAT-036: Supabase Auth (Phase 3)"),
            ("RLS policies open (no user filtering)",     "Intentional — no auth yet", "Tightens when auth ships"),
            ("No organization_id on tables",              "Intentional — pre-multi-tenant", "FEAT-037: Multi-Tenancy (Phase 3)"),
        ],
        col_widths_cm=[5.5, 4.0, 6.5]
    )

    # ── 8. LIMITATIONS ────────────────────────────────────────────────────────

    heading1(doc, "8. Limitations & Honest Caveats")
    for label, desc in [
        ("No formal time tracking.",
         "Active coding days are inferred from commit timestamps. The '10 active coding days' is an approximation."),
        ("Solo project dynamics differ from team dynamics.",
         "There was no code review from a second human engineer. Code review catches bugs, architectural "
         "issues, and knowledge-sharing opportunities that this model does not replicate."),
        ("Not all commits represent equal effort.",
         "The git history includes node_modules commits with millions of lines (excluded) and single-line "
         "config fixes alongside 1,300-line feature commits."),
        ("Greenfield advantage.",
         "Building from scratch allows architectural freedom that legacy codebases do not afford."),
        ("The multiplier depends on Product Owner quality.",
         "Claude amplifies the Product Owner's ability to execute. A Product Owner who cannot review "
         "code cannot safely use AI-generated code at this velocity."),
        ("Reproducibility is uncertain.",
         "This was one project, one domain. Generalisability to other stacks or engineer profiles is unproven."),
    ]:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(2)
        r_label = p.add_run(label + " ")
        set_run_font(r_label, name='Calibri', size_pt=10, bold=True, color=DARK_NAVY)
        r_desc = p.add_run(desc)
        set_run_font(r_desc, name='Calibri', size_pt=10, color=DARK_TEXT)

    doc.add_paragraph()

    # ── 9. CONCLUSIONS ────────────────────────────────────────────────────────

    heading1(doc, "9. Conclusions & Recommendations")

    heading2(doc, "Key Finding")
    callout_box(doc,
        "One capable Product Owner working with Claude as a persistent, full-session pair-programmer "
        "can approximate the feature throughput of a 3-person startup development team over a sustained "
        "build window. The efficiency gains are real, measurable in the git history, and consistent "
        "with the Product Owner's self-assessment of a 2–3x multiplier.",
        label="CONCLUSION")

    body(doc, "The gains are not from Claude writing faster code. They are structural:")
    for item in [
        "Zero handoff latency",
        "Persistent cross-session context",
        "On-demand full-stack competency",
        "Documentation as a zero-marginal-cost side-effect",
    ]:
        bullet(doc, item)

    heading2(doc, "Recommended Workflow Patterns")
    for n, label, desc in [
        (1, "Invest in context management.",
         "A well-maintained NOTES.md or equivalent session-start document is the single highest-leverage "
         "practice. It eliminates the 15–30 minute catch-up cost at the start of every session."),
        (2, "Treat Claude as a full-session collaborator, not a one-shot query tool.",
         "The compounding gains come from sustained sessions where Claude holds architectural context. "
         "Piecemeal queries do not capture this."),
        (3, "Keep the Product Owner in the architecture seat.",
         "Define what to build and why before asking Claude to help build it. Product direction, "
         "technical trade-offs, and quality gate remain the Product Owner's responsibility."),
        (4, "Use the multiplier effect, not the replacement effect.",
         "The right frame is not 'Claude replaces the Product Owner.' It is 'one Product Owner + Claude "
         "can reach a place that previously required a team.'"),
    ]:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(5)
        p.paragraph_format.space_after = Pt(2)
        r_n = p.add_run(f"{n}. {label} ")
        set_run_font(r_n, name='Calibri', size_pt=10, bold=True, color=MID_BLUE)
        r_d = p.add_run(desc)
        set_run_font(r_d, name='Calibri', size_pt=10, color=DARK_TEXT)

    doc.add_paragraph()

    heading2(doc, "Where This Model Works Best")
    for item in [
        "Greenfield feature development with clear requirements",
        "Database schema design and data layer abstraction",
        "Responsive UI work with established component libraries (shadcn/ui, Tailwind)",
        "Documentation and release note generation",
        "Cross-stack features requiring frontend + backend + DB changes in a single session",
    ]:
        bullet(doc, item)

    heading2(doc, "Where Human Judgment Remains Essential")
    for item in [
        "Product and architectural decisions (what to build, what to defer)",
        "Security-sensitive code (auth, RLS, data access policies)",
        "Code review and quality gating of generated output",
        "Recognising when generated code is plausible but wrong",
    ]:
        bullet(doc, item)

    # ── APPENDIX A ────────────────────────────────────────────────────────────

    heading1(doc, "Appendix A — Full Feature Commit Log (LOC Stats)")
    body(doc, "Excludes node_modules and lock file commits. Sourced from git log --shortstat.")
    styled_table(doc,
        headers=["Date", "Release", "Commit Summary", "Files", "Insertions", "Deletions"],
        rows=[
            ("2026-03-12", "v4.5.0", "Employee Self-Service Portal",                           "6",  "667",   "11"),
            ("2026-03-12", "v4.4.0", "Approval Workflows (Leave, PO, Appraisal)",              "9",  "1,209", "18"),
            ("2026-03-11", "v4.3.0", "HR: Goals, Appraisals, Skills Matrix",                  "2",  "1,302", "125"),
            ("2026-03-11", "v4.2.1", "In-app Help page",                                      "2",  "346",   "0"),
            ("2026-03-11", "v4.2.0", "Reports page + Supplier management",                    "5",  "699",   "3"),
            ("2026-03-11", "v4.1.1", "Mobile/tablet responsive layout",                       "6",  "55",    "16"),
            ("2026-03-11", "v4.1.0", "Supabase integration (data layer)",                     "11", "440",   "7"),
            ("2026-03-11", "v4.0.0", "Inventory image upload, sortable tables, analytics",    "4",  "369",   "99"),
            ("2026-03-10", "v3.1.0", "Recharts, currency, toast notifications",               "8",  "149",   "77"),
            ("2026-03-10", "v3.1.0", "HR + Settings API routers",                             "3",  "126",   "1"),
            ("2026-03-10", "v3.0",   "Complete all pages — HR, Settings, UI",                 "12", "819",   "16"),
            ("2026-03-10", "v3.0",   "Production UI with shadcn/ui",                          "23", "2,368", "826"),
            ("2026-03-10", "v2.0",   "CRM module, FastAPI, Next.js frontend",                 "41", "3,860", "84"),
        ],
        col_widths_cm=[2.5, 1.8, 7.5, 1.4, 2.0, 2.0]
    )
    body(doc, "Total (feature commits only): ~12,600 net new application lines across 16 substantive commits.")

    # ── APPENDIX B ────────────────────────────────────────────────────────────

    heading1(doc, "Appendix B — Module Feature Inventory")
    styled_table(doc,
        headers=["Module", "Feature Count (v4.5.0)", "Highlights"],
        rows=[
            ("Dashboard",             "5",  "KPIs, trend chart, fast/slow movers, currency, clickable filters"),
            ("Operations",            "6",  "Inventory, POS, Bills, Suppliers, Purchase Orders, image upload"),
            ("HR",                    "7",  "Employees, Payroll, Goals, Appraisals, Skills, Leave, workflows"),
            ("CRM",                   "5",  "Contacts, Leads, Kanban, lead scoring, follow-ups"),
            ("Reports",               "3",  "Sales Report, Top Sellers, Inventory Report"),
            ("Settings",              "2",  "Company info, currency selector"),
            ("Help",                  "1",  "In-app user guide covering all modules"),
            ("Employee Self-Service", "4",  "My Goals, My Appraisals, My Leave, My Skills"),
        ],
        col_widths_cm=[4.0, 3.5, 8.5]
    )

    # ── APPENDIX C ────────────────────────────────────────────────────────────

    heading1(doc, "Appendix C — Stack Reference")
    styled_table(doc,
        headers=["Component", "Technology", "Notes"],
        rows=[
            ("Framework",       "Next.js 14 (App Router)",         "TypeScript, strict mode"),
            ("UI Components",   "shadcn/ui + Tailwind CSS",         "Design system"),
            ("Charts",          "Recharts",                         "Sales trend, top sellers"),
            ("Database",        "Supabase (PostgreSQL)",            "RLS enabled"),
            ("Auth",            "Hardcoded (FEAT-036 planned)",     "Supabase Auth, Phase 3"),
            ("Deployment",      "Vercel",                           "Auto-deploy on push to main"),
            ("AI Collaborator", "Claude Sonnet 4.6 (Anthropic)",    "Full-session pair-programmer"),
        ],
        col_widths_cm=[3.5, 5.5, 7.0]
    )

    body(doc,
         "\nAll git statistics were derived from git log --shortstat on the BzHub repository at "
         "commit f1eed240 (v4.5.0). Node_modules and lock file commits are excluded from LOC counts.",
         space_after=4)

    # ── FOOTER & SAVE ─────────────────────────────────────────────────────────

    add_footer(doc)

    out_path = "/Users/scottvalentino/BzHub/documentation/BzHub_Efficiency_WhitePaper.docx"
    doc.save(out_path)
    print(f"✓  Saved: {out_path}")


if __name__ == "__main__":
    build_document()
