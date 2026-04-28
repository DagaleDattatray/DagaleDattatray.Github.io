#!/usr/bin/env python3
"""
SQL Master Course HTML Generator
Reads all 23 week markdown files and outputs sql-course.html
Run: python3 build-course.py
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(BASE_DIR, "sql-course.html")

WEEKS = [
    (1,  "week-01-lesson.md",          "What is SQL + Databases",        "lesson",    1),
    (2,  "week-02-lesson.md",          "Filtering Data",                  "lesson",    1),
    (3,  "week-03-lesson.md",          "Aggregate Functions",             "lesson",    1),
    (4,  "week-04-lesson.md",          "GROUP BY + HAVING",               "lesson",    1),
    (5,  "week-05-lesson.md",          "Subqueries",                      "lesson",    1),
    (6,  "week-06-lesson.md",          "NULL Values",                     "lesson",    1),
    (7,  "week-07-mini-project-1.md",  "Mini Project 1",                  "project",   1),
    (8,  "week-08-lesson.md",          "JOINs — INNER & LEFT",           "lesson",    2),
    (9,  "week-09-lesson.md",          "JOINs — RIGHT, FULL & CROSS",    "lesson",    2),
    (10, "week-10-lesson.md",          "String Functions",                "lesson",    2),
    (11, "week-11-lesson.md",          "Date & Time Functions",           "lesson",    2),
    (12, "week-12-lesson.md",          "CASE Statements",                 "lesson",    2),
    (13, "week-13-lesson.md",          "Views",                           "lesson",    2),
    (14, "week-14-lesson.md",          "Stored Procedures",               "lesson",    2),
    (15, "week-15-mini-project-2.md",  "Mini Project 2",                  "project",   2),
    (16, "week-16-lesson.md",          "Window Functions — Ranking",      "lesson",    3),
    (17, "week-17-lesson.md",          "Window Functions — LAG/LEAD",     "lesson",    3),
    (18, "week-18-lesson.md",          "CTEs",                            "lesson",    3),
    (19, "week-19-lesson.md",          "Indexes & Performance",           "lesson",    3),
    (20, "week-20-lesson.md",          "Transactions & ACID",             "lesson",    3),
    (21, "week-21-lesson.md",          "Advanced Subqueries",             "lesson",    3),
    (22, "week-22-interview-prep.md",  "Interview Prep",                  "interview", 3),
    (23, "week-23-capstone-project.md","Capstone Project",                "capstone",  3),
]

PHASE_NAMES = {1: "Phase 1 — Foundations", 2: "Phase 2 — Intermediate", 3: "Phase 3 — Advanced"}

# Section headings that get special callout styling
CALLOUT_SECTIONS = {
    "what you already know":  ("callout-recap",    "📌 What You Already Know"),
    "key things to remember": ("callout-tip",      "💡 Key Things to Remember"),
    "next week":              ("callout-next",     "→ Next Week"),
    "interview tips":         ("callout-tip",      "💡 Interview Tips"),
    "setup sql":              ("callout-setup",    "🛠 Setup SQL — Run This First"),
    "try it":                 ("callout-tryit",    "▶ Try It in DB Browser"),
}

_answer_toggle_id = [0]


def escape_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def process_inline(text):
    """Apply inline markdown: bold, inline code, italic."""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Inline code (must run before italic to avoid conflicts)
    text = re.sub(r'`([^`]+)`', r'<code class="inline-code">\1</code>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    return text


def render_table(table_lines):
    if not table_lines:
        return ""
    out = '<div class="table-wrap"><table>'
    for ti, trow in enumerate(table_lines):
        cells = [c.strip() for c in trow.strip().strip("|").split("|")]
        if ti == 0:
            out += "<thead><tr>" + "".join(
                f"<th>{process_inline(escape_html(c))}</th>" for c in cells
            ) + "</tr></thead><tbody>"
        elif ti == 1 and all(
            not c.strip().replace("-","").replace(":","").strip() for c in cells
        ):
            continue
        else:
            out += "<tr>" + "".join(
                f"<td>{process_inline(escape_html(c))}</td>" for c in cells
            ) + "</tr>"
    out += "</tbody></table></div>"
    return out


def render_code_block(code_lines, lang, in_answers):
    code_content = escape_html("\n".join(code_lines))
    lang_label = lang.upper() if lang else "SQL"
    lang_class = lang if lang else "sql"
    inner = (
        f'<div class="code-block">'
        f'<div class="code-header">'
        f'<span class="code-lang">{lang_label}</span>'
        f'<button class="copy-btn" onclick="copyCode(this)">Copy</button>'
        f'</div>'
        f'<pre><code class="language-{lang_class}">{code_content}</code></pre>'
        f'</div>'
    )
    if in_answers:
        _answer_toggle_id[0] += 1
        tid = _answer_toggle_id[0]
        return (
            f'<div class="answers-wrap" id="ans-wrap-{tid}">'
            f'<button class="show-answers-btn" onclick="toggleAnswers({tid})">Show Answers</button>'
            f'<div class="answers-content" id="ans-{tid}" style="display:none">'
            f'{inner}'
            f'</div></div>'
        )
    return inner


def md_to_html(md_text):
    lines = md_text.split("\n")
    out = []

    # State
    in_code = False
    code_lines = []
    code_lang = ""
    in_table = False
    table_lines = []
    bullet_buffer = []      # consecutive bullet items
    numbered_buffer = []    # consecutive numbered items
    current_section = ""    # tracks the current h2 section name
    in_answers = False
    in_callout = False
    callout_type = ""
    callout_title = ""
    callout_items = []

    def flush_bullets():
        if not bullet_buffer:
            return
        items = "".join(f"<li>{process_inline(escape_html(b))}</li>" for b in bullet_buffer)
        out.append(f'<ul class="content-list">{items}</ul>')
        bullet_buffer.clear()

    def flush_numbered():
        if not numbered_buffer:
            return
        items = "".join(
            f'<li><span class="ex-text">{process_inline(escape_html(t))}</span></li>'
            for t in numbered_buffer
        )
        out.append(f'<ol class="exercise-list">{items}</ol>')
        numbered_buffer.clear()

    def flush_table():
        nonlocal in_table, table_lines
        if table_lines:
            out.append(render_table(table_lines))
        table_lines = []
        in_table = False

    def flush_callout():
        nonlocal in_callout, callout_items, callout_type, callout_title
        if not in_callout:
            return
        items_html = "".join(
            f"<li>{process_inline(escape_html(item))}</li>" for item in callout_items
        )
        out.append(
            f'<div class="callout {callout_type}">'
            f'<div class="callout-title">{callout_title}</div>'
            f'<ul>{items_html}</ul>'
            f'</div>'
        )
        in_callout = False
        callout_items = []
        callout_type = ""
        callout_title = ""

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # ── CODE BLOCK ────────────────────────────────────────────
        if stripped.startswith("```"):
            flush_bullets()
            flush_numbered()
            if in_table:
                flush_table()
            if in_callout:
                flush_callout()
            if in_code:
                # closing fence
                out.append(render_code_block(code_lines, code_lang, in_answers))
                in_code = False
                code_lines = []
                code_lang = ""
            else:
                # opening fence
                in_code = True
                code_lang = stripped[3:].strip() or "sql"
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        # ── TABLE ─────────────────────────────────────────────────
        if stripped.startswith("|"):
            flush_bullets()
            flush_numbered()
            if in_callout:
                flush_callout()
            in_table = True
            table_lines.append(line)
            i += 1
            continue
        elif in_table:
            flush_table()

        # ── HR ────────────────────────────────────────────────────
        if stripped in ("---", "***", "___"):
            flush_bullets()
            flush_numbered()
            if in_callout:
                flush_callout()
            out.append('<hr class="section-divider">')
            in_answers = False
            i += 1
            continue

        # ── HEADINGS ──────────────────────────────────────────────
        h_match = re.match(r'^(#{1,4})\s+(.*)', line)
        if h_match:
            flush_bullets()
            flush_numbered()
            if in_callout:
                flush_callout()
            level = len(h_match.group(1))
            title = h_match.group(2).strip()
            title_lower = title.lower()

            if level == 1:
                # Main week title — hidden (shown in week header instead)
                out.append(f'<h1 class="week-title-hidden">{escape_html(title)}</h1>')
                i += 1
                continue

            if level == 2:
                current_section = title_lower
                in_answers = (title_lower == "answers")

                # Check if this h2 triggers a callout block
                callout_key = next((k for k in CALLOUT_SECTIONS if k in title_lower), None)
                if callout_key:
                    in_callout = True
                    callout_type, callout_title = CALLOUT_SECTIONS[callout_key]
                    callout_items = []
                    i += 1
                    continue
                else:
                    in_callout = False
                    out.append(f'<h2 class="section-heading">{process_inline(escape_html(title))}</h2>')
                    i += 1
                    continue

            if level == 3:
                # Q&A style (interview prep) — special styling
                if re.match(r'^Q\d+\.', title):
                    out.append(f'<div class="interview-q"><span class="q-label">Q</span>{process_inline(escape_html(title[title.index(".")+1:].strip()))}</div>')
                else:
                    out.append(f'<h3 class="sub-heading">{process_inline(escape_html(title))}</h3>')
                i += 1
                continue

            if level == 4:
                out.append(f'<h4 class="sub-sub-heading">{process_inline(escape_html(title))}</h4>')
                i += 1
                continue

        # ── BULLET ITEMS ──────────────────────────────────────────
        bullet_match = re.match(r'^(\s*)[-*]\s+(.*)', line)
        if bullet_match:
            flush_numbered()
            content = bullet_match.group(2)
            indent = len(bullet_match.group(1))
            if in_callout:
                callout_items.append(content)
            elif indent >= 2:
                # sub-bullet: flush main bullets first
                flush_bullets()
                out.append(f'<ul class="content-list sub-list"><li>{process_inline(escape_html(content))}</li></ul>')
            else:
                bullet_buffer.append(content)
            i += 1
            continue

        # ── NUMBERED ITEMS ────────────────────────────────────────
        num_match = re.match(r'^(\d+)\.\s+(.*)', line)
        if num_match:
            flush_bullets()
            if in_callout:
                callout_items.append(num_match.group(2))
            else:
                numbered_buffer.append(num_match.group(2))
            i += 1
            continue

        # ── EMPTY LINE ────────────────────────────────────────────
        if stripped == "":
            flush_bullets()
            flush_numbered()
            # Don't flush callout on empty lines — let it accumulate
            out.append('<div class="spacer"></div>')
            i += 1
            continue

        # ── PARAGRAPH ─────────────────────────────────────────────
        flush_bullets()
        flush_numbered()
        if in_callout:
            # Paragraph inside callout section — treat as a regular paragraph after the callout
            flush_callout()
        out.append(f'<p>{process_inline(escape_html(stripped))}</p>')
        i += 1

    # Flush anything remaining
    flush_bullets()
    flush_numbered()
    if in_table:
        flush_table()
    if in_callout:
        flush_callout()

    return "\n".join(out)


def read_week(filename):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        return f"<p>File not found: {filename}</p>"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_sidebar():
    html = ""
    current_phase = None
    for week_num, filename, title, wtype, phase in WEEKS:
        if phase != current_phase:
            if current_phase is not None:
                html += '</div></div>'
            html += f'''
            <div class="phase-group" data-phase="{phase}">
              <div class="phase-header" onclick="togglePhase(this)">
                <span>{PHASE_NAMES[phase]}</span>
                <span class="phase-arrow">▼</span>
              </div>
              <div class="phase-weeks">'''
            current_phase = phase
        badge = ""
        if wtype == "project":
            badge = '<span class="badge badge-project">PROJECT</span>'
        elif wtype == "interview":
            badge = '<span class="badge badge-interview">INTERVIEW</span>'
        elif wtype == "capstone":
            badge = '<span class="badge badge-capstone">CAPSTONE</span>'
        html += f'''
                <div class="week-link" data-week="{week_num}" onclick="showWeek({week_num})">
                  <input type="checkbox" class="week-check" id="check-{week_num}"
                    onchange="markComplete({week_num}, this.checked)" onclick="event.stopPropagation()">
                  <span class="week-link-num">W{week_num:02d}</span>
                  <span class="week-link-title">{title}</span>
                  {badge}
                </div>'''
    html += '</div></div>'
    return html


def build_week_section(week_num, filename, title, wtype, phase):
    # Reset answer toggle ID per week
    _answer_toggle_id[0] = week_num * 100

    md = read_week(filename)
    content_html = md_to_html(md)

    type_badge = ""
    if wtype == "project":
        type_badge = '<span class="week-type-badge project">PROJECT</span>'
    elif wtype == "interview":
        type_badge = '<span class="week-type-badge interview">INTERVIEW PREP</span>'
    elif wtype == "capstone":
        type_badge = '<span class="week-type-badge capstone">CAPSTONE</span>'
    else:
        type_badge = f'<span class="week-type-badge lesson">PHASE {phase}</span>'

    prev_nav = f'<button class="nav-btn" onclick="showWeek({week_num-1})">← Week {week_num-1}</button>' if week_num > 1 else ''
    next_nav = f'<button class="nav-btn" onclick="showWeek({week_num+1})">Week {week_num+1} →</button>' if week_num < 23 else ''

    return f'''
    <section id="week-{week_num}" class="week-section" style="display:none">
      <div class="week-header">
        <div class="week-meta">
          <span class="week-number">Week {week_num}</span>
          {type_badge}
        </div>
        <h1 class="week-main-title">{title}</h1>
      </div>
      <div class="week-content">
        {content_html}
      </div>
      <div class="week-nav">
        {prev_nav}
        <button class="nav-btn complete-btn" onclick="markComplete({week_num}, true); document.getElementById('check-{week_num}').checked=true;">
          ✓ Mark Complete
        </button>
        {next_nav}
      </div>
    </section>'''


def build_home():
    cards = ""
    for week_num, filename, title, wtype, phase in WEEKS:
        color_class = f"phase{phase}"
        cards += f'''
        <div class="home-card {color_class}" onclick="showWeek({week_num})">
          <div class="home-card-week">W{week_num:02d}</div>
          <div class="home-card-title">{title}</div>
          <div class="home-card-dot" id="dot-{week_num}"></div>
        </div>'''
    return f'''
    <section id="home" class="week-section">
      <div class="home-hero">
        <h1>SQL Mastery Course</h1>
        <p>23 weeks · 3 phases · From zero to job-ready</p>
        <div class="home-progress-wrap">
          <div class="home-progress-bar"><div class="home-progress-fill" id="home-fill"></div></div>
          <span id="home-count">0 / 23 complete</span>
        </div>
      </div>
      <div class="home-cards">{cards}</div>
    </section>'''


def build_html():
    sidebar_html = build_sidebar()
    home_html = build_home()
    weeks_html = ""
    for w in WEEKS:
        weeks_html += build_week_section(*w)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SQL Mastery Course</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/sql.min.js"></script>
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root {{
  --bg: #0d1117;
  --sidebar: #161b22;
  --card: #1c2128;
  --border: #30363d;
  --accent: #58a6ff;
  --green: #3fb950;
  --orange: #d29922;
  --red: #f85149;
  --purple: #bc8cff;
  --text: #e6edf3;
  --text-muted: #8b949e;
  --sidebar-width: 290px;
}}

html, body {{ height: 100%; }}
body {{
  font-family: 'Inter', sans-serif;
  background: var(--bg);
  color: var(--text);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-size: 15px;
  line-height: 1.7;
}}

/* HEADER */
.header {{
  height: 54px;
  background: var(--sidebar);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 16px;
  flex-shrink: 0;
  z-index: 100;
}}
.header-logo {{
  font-weight: 700;
  font-size: 16px;
  color: var(--accent);
  cursor: pointer;
  white-space: nowrap;
}}
.progress-bar-wrap {{
  flex: 1;
  max-width: 280px;
  background: var(--border);
  height: 6px;
  border-radius: 3px;
  overflow: hidden;
}}
.progress-bar-fill {{
  height: 100%;
  background: var(--green);
  border-radius: 3px;
  transition: width 0.4s ease;
  width: 0%;
}}
.progress-label {{
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
}}
.shortcuts-hint {{
  font-size: 11px;
  color: var(--text-muted);
  margin-left: auto;
}}

/* LAYOUT */
.layout {{
  display: flex;
  flex: 1;
  overflow: hidden;
}}

/* SIDEBAR */
.sidebar {{
  width: var(--sidebar-width);
  background: var(--sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;
}}
.search-wrap {{
  padding: 12px;
  border-bottom: 1px solid var(--border);
}}
.search-input {{
  width: 100%;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 12px;
  color: var(--text);
  font-size: 13px;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s;
}}
.search-input:focus {{ border-color: var(--accent); }}
.sidebar-nav {{
  flex: 1;
  overflow-y: auto;
  padding-bottom: 20px;
}}
.sidebar-nav::-webkit-scrollbar {{ width: 4px; }}
.sidebar-nav::-webkit-scrollbar-track {{ background: transparent; }}
.sidebar-nav::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 2px; }}

.phase-group {{ border-bottom: 1px solid var(--border); }}
.phase-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  cursor: pointer;
  user-select: none;
  transition: color 0.2s;
}}
.phase-header:hover {{ color: var(--text); }}
.phase-arrow {{ transition: transform 0.2s; font-size: 10px; }}
.phase-header.collapsed .phase-arrow {{ transform: rotate(-90deg); }}
.phase-weeks.collapsed {{ display: none; }}

.week-link {{
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 14px;
  cursor: pointer;
  font-size: 13px;
  border-left: 3px solid transparent;
  transition: background 0.15s, border-color 0.15s;
}}
.week-link:hover {{ background: rgba(88,166,255,0.06); }}
.week-link.active {{
  background: rgba(88,166,255,0.1);
  border-left-color: var(--accent);
}}
.week-link.done .week-link-num {{ color: var(--green); }}
.week-link.done .week-link-title {{ color: var(--text-muted); text-decoration: line-through; }}
.week-check {{ accent-color: var(--green); cursor: pointer; flex-shrink: 0; }}
.week-link-num {{
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  font-family: 'JetBrains Mono', monospace;
  min-width: 28px;
}}
.week-link-title {{ flex: 1; }}

.badge {{ font-size: 9px; font-weight: 700; padding: 2px 5px; border-radius: 3px; }}
.badge-project {{ background: rgba(188,140,255,0.2); color: var(--purple); }}
.badge-interview {{ background: rgba(210,153,34,0.2); color: var(--orange); }}
.badge-capstone {{ background: rgba(248,81,73,0.15); color: var(--red); }}

/* MAIN */
.main {{
  flex: 1;
  overflow-y: auto;
}}
.main::-webkit-scrollbar {{ width: 6px; }}
.main::-webkit-scrollbar-track {{ background: transparent; }}
.main::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}

/* HOME */
.home-hero {{
  padding: 48px 44px 32px;
  border-bottom: 1px solid var(--border);
}}
.home-hero h1 {{
  font-size: 32px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 8px;
}}
.home-hero p {{
  color: var(--text-muted);
  font-size: 15px;
  margin-bottom: 24px;
}}
.home-progress-wrap {{
  display: flex;
  align-items: center;
  gap: 14px;
  max-width: 400px;
}}
.home-progress-bar {{
  flex: 1;
  background: var(--border);
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
}}
.home-progress-fill {{
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--green));
  border-radius: 4px;
  transition: width 0.4s ease;
  width: 0%;
}}
.home-cards {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(175px, 1fr));
  gap: 12px;
  padding: 32px 44px;
}}
.home-card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  transition: transform 0.15s, border-color 0.15s, box-shadow 0.15s;
  position: relative;
}}
.home-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 20px rgba(0,0,0,0.3); }}
.home-card.phase1:hover {{ border-color: var(--accent); }}
.home-card.phase2:hover {{ border-color: var(--green); }}
.home-card.phase3:hover {{ border-color: var(--purple); }}
.home-card-week {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  margin-bottom: 6px;
}}
.home-card.phase1 .home-card-week {{ color: var(--accent); }}
.home-card.phase2 .home-card-week {{ color: var(--green); }}
.home-card.phase3 .home-card-week {{ color: var(--purple); }}
.home-card-title {{ font-size: 13px; font-weight: 500; line-height: 1.4; }}
.home-card-dot {{
  position: absolute;
  top: 12px; right: 12px;
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--border);
  transition: background 0.2s;
}}
.home-card-dot.done {{ background: var(--green); }}

/* WEEK SECTION */
.week-section {{ display: none; }}

.week-header {{
  padding: 32px 44px 24px;
  border-bottom: 1px solid var(--border);
  background: linear-gradient(180deg, rgba(88,166,255,0.03) 0%, transparent 100%);
}}
.week-meta {{
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}}
.week-number {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: var(--text-muted);
  background: var(--card);
  padding: 3px 8px;
  border-radius: 4px;
  border: 1px solid var(--border);
}}
.week-type-badge {{
  font-size: 10px;
  font-weight: 700;
  padding: 3px 9px;
  border-radius: 4px;
  letter-spacing: 0.06em;
}}
.week-type-badge.lesson {{ background: rgba(88,166,255,0.15); color: var(--accent); }}
.week-type-badge.project {{ background: rgba(188,140,255,0.15); color: var(--purple); }}
.week-type-badge.interview {{ background: rgba(210,153,34,0.15); color: var(--orange); }}
.week-type-badge.capstone {{ background: rgba(248,81,73,0.12); color: var(--red); }}
.week-main-title {{ font-size: 26px; font-weight: 700; color: var(--text); }}

.week-content {{
  padding: 32px 44px 16px;
  max-width: 880px;
}}

.week-title-hidden {{ display: none; }}

/* CONTENT ELEMENTS */
.week-content h2.section-heading {{
  font-size: 18px;
  font-weight: 600;
  color: var(--text);
  margin: 32px 0 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
}}
.week-content h3.sub-heading {{
  font-size: 15px;
  font-weight: 600;
  color: var(--accent);
  margin: 22px 0 10px;
}}
.week-content h4.sub-sub-heading {{
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  margin: 16px 0 6px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}}
.week-content p {{
  margin: 10px 0;
  color: var(--text);
  line-height: 1.75;
}}
.section-divider {{
  border: none;
  border-top: 1px solid var(--border);
  margin: 24px 0;
}}
.spacer {{ height: 4px; }}

/* LISTS */
.content-list {{
  margin: 10px 0 10px 0;
  padding-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}}
.content-list li {{
  color: var(--text);
  line-height: 1.65;
  padding-left: 4px;
}}
.content-list li::marker {{ color: var(--accent); }}
.sub-list {{ margin-left: 20px; }}
.sub-list li::marker {{ color: var(--text-muted); }}

/* EXERCISE LIST */
.exercise-list {{
  margin: 10px 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
}}
.exercise-list li {{
  display: flex;
  gap: 12px;
  align-items: flex-start;
  counter-increment: exercise-counter;
}}
.exercise-list {{  counter-reset: exercise-counter; }}
.exercise-list li::before {{
  content: counter(exercise-counter);
  min-width: 26px;
  height: 26px;
  background: var(--accent);
  color: var(--bg);
  border-radius: 50%;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
}}
.ex-text {{ line-height: 1.65; }}

/* INLINE CODE */
.inline-code {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  background: rgba(88,166,255,0.1);
  color: var(--accent);
  padding: 1px 5px;
  border-radius: 3px;
  border: 1px solid rgba(88,166,255,0.2);
}}

/* CODE BLOCKS */
.code-block {{
  margin: 14px 0;
  border-radius: 8px;
  border: 1px solid var(--border);
  overflow: hidden;
}}
.code-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 14px;
  background: #161b22;
  border-bottom: 1px solid var(--border);
}}
.code-lang {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: var(--text-muted);
  font-weight: 600;
  letter-spacing: 0.08em;
}}
.copy-btn {{
  background: var(--card);
  border: 1px solid var(--border);
  color: var(--text-muted);
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s, color 0.15s;
}}
.copy-btn:hover {{ background: var(--border); color: var(--text); }}
.copy-btn.copied {{ color: var(--green); border-color: var(--green); }}
.code-block pre {{
  margin: 0;
  padding: 16px;
  overflow-x: auto;
  background: var(--bg);
}}
.code-block pre code {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
  background: transparent !important;
}}

/* ANSWERS TOGGLE */
.answers-wrap {{ margin: 14px 0; }}
.show-answers-btn {{
  background: rgba(63,185,80,0.1);
  border: 1px solid var(--green);
  color: var(--green);
  padding: 9px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-family: inherit;
  font-size: 13px;
  font-weight: 500;
  transition: background 0.15s;
  width: 100%;
  text-align: left;
}}
.show-answers-btn:hover {{ background: rgba(63,185,80,0.18); }}
.answers-content {{ margin-top: 8px; }}

/* CALLOUT BOXES */
.callout {{
  border-radius: 8px;
  padding: 16px 20px;
  margin: 16px 0;
  border-left: 4px solid;
}}
.callout ul {{
  margin-top: 10px;
  padding-left: 18px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}}
.callout ul li {{ line-height: 1.65; }}
.callout-title {{
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  margin-bottom: 4px;
}}

.callout-recap {{
  background: rgba(88,166,255,0.07);
  border-color: var(--accent);
}}
.callout-recap .callout-title {{ color: var(--accent); }}
.callout-recap ul li::marker {{ color: var(--accent); }}

.callout-tip {{
  background: rgba(210,153,34,0.08);
  border-color: var(--orange);
}}
.callout-tip .callout-title {{ color: var(--orange); }}
.callout-tip ul li::marker {{ color: var(--orange); }}

.callout-next {{
  background: rgba(63,185,80,0.07);
  border-color: var(--green);
}}
.callout-next .callout-title {{ color: var(--green); }}
.callout-next ul li::marker {{ color: var(--green); }}

.callout-setup {{
  background: rgba(188,140,255,0.07);
  border-color: var(--purple);
}}
.callout-setup .callout-title {{ color: var(--purple); }}

.callout-tryit {{
  background: rgba(88,166,255,0.05);
  border-color: var(--accent);
  font-style: italic;
}}
.callout-tryit .callout-title {{ color: var(--accent); }}

/* INTERVIEW Q STYLE */
.interview-q {{
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin: 20px 0 8px;
  font-weight: 600;
  font-size: 15px;
  color: var(--text);
}}
.q-label {{
  min-width: 26px;
  height: 26px;
  background: rgba(188,140,255,0.2);
  color: var(--purple);
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}}

/* TABLES */
.table-wrap {{
  overflow-x: auto;
  margin: 14px 0;
  border-radius: 8px;
  border: 1px solid var(--border);
}}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
thead {{ background: var(--card); }}
th {{
  padding: 10px 14px;
  text-align: left;
  font-weight: 600;
  color: var(--text-muted);
  font-size: 12px;
  letter-spacing: 0.04em;
  border-bottom: 1px solid var(--border);
}}
td {{
  padding: 9px 14px;
  border-bottom: 1px solid rgba(48,54,61,0.5);
  color: var(--text);
}}
tr:last-child td {{ border-bottom: none; }}
tbody tr:hover {{ background: rgba(88,166,255,0.04); }}

/* WEEK NAV */
.week-nav {{
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 44px 48px;
  border-top: 1px solid var(--border);
  margin-top: 24px;
}}
.nav-btn {{
  background: var(--card);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 9px 18px;
  border-radius: 6px;
  cursor: pointer;
  font-family: inherit;
  font-size: 13px;
  font-weight: 500;
  transition: background 0.15s, border-color 0.15s;
}}
.nav-btn:hover {{ background: var(--border); }}
.complete-btn {{
  background: rgba(63,185,80,0.1);
  border-color: var(--green);
  color: var(--green);
  margin-left: auto;
}}
.complete-btn:hover {{ background: rgba(63,185,80,0.2); }}

/* TOAST */
.toast {{
  position: fixed;
  bottom: 24px; right: 24px;
  background: var(--card);
  border: 1px solid var(--green);
  color: var(--green);
  padding: 10px 18px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.2s, transform 0.2s;
  pointer-events: none;
  z-index: 1000;
}}
.toast.show {{ opacity: 1; transform: translateY(0); }}

/* MOBILE MENU BUTTON */
.mobile-menu-btn {{
  display: none;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 6px;
  cursor: pointer;
  flex-shrink: 0;
  font-size: 18px;
  color: var(--text);
  margin-left: auto;
}}

/* MOBILE DRAWER OVERLAY */
.drawer-overlay {{
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  z-index: 200;
  backdrop-filter: blur(2px);
}}
.drawer-overlay.open {{ display: block; }}

/* MOBILE DRAWER */
.mobile-drawer {{
  position: fixed;
  top: 0; left: 0; bottom: 0;
  width: 300px;
  background: var(--sidebar);
  border-right: 1px solid var(--border);
  z-index: 300;
  display: flex;
  flex-direction: column;
  transform: translateX(-100%);
  transition: transform 0.25s ease;
}}
.mobile-drawer.open {{ transform: translateX(0); }}
.drawer-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  font-weight: 600;
  font-size: 15px;
  color: var(--accent);
}}
.drawer-close {{
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 22px;
  cursor: pointer;
  line-height: 1;
  padding: 0 4px;
}}
.drawer-search {{
  padding: 12px;
  border-bottom: 1px solid var(--border);
}}
.drawer-search input {{
  width: 100%;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 12px;
  color: var(--text);
  font-size: 13px;
  font-family: inherit;
  outline: none;
}}
.drawer-search input:focus {{ border-color: var(--accent); }}
.drawer-nav {{
  flex: 1;
  overflow-y: auto;
  padding-bottom: 20px;
}}
.drawer-nav::-webkit-scrollbar {{ width: 4px; }}
.drawer-nav::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 2px; }}

@media (max-width: 700px) {{
  .sidebar {{ display: none; }}
  .mobile-menu-btn {{ display: flex; }}
  .shortcuts-hint {{ display: none; }}

  .week-content, .week-header, .week-nav {{ padding-left: 18px; padding-right: 18px; }}
  .home-cards {{ padding: 16px; grid-template-columns: repeat(auto-fill, minmax(145px, 1fr)); gap: 10px; }}
  .home-hero {{ padding: 24px 18px 20px; }}
  .home-hero h1 {{ font-size: 24px; }}
  .week-main-title {{ font-size: 20px; }}
  .week-content h2.section-heading {{ font-size: 16px; }}
  .code-block pre {{ padding: 12px; }}
  .code-block pre code {{ font-size: 12px; }}
  .week-nav {{ flex-wrap: wrap; gap: 8px; }}
  .complete-btn {{ margin-left: 0; width: 100%; justify-content: center; }}
}}
</style>
</head>
<body>

<div class="header">
  <span class="header-logo" onclick="showHome()">SQL Mastery</span>
  <div class="progress-bar-wrap">
    <div class="progress-bar-fill" id="progress-fill"></div>
  </div>
  <span class="progress-label" id="progress-label">0 / 23</span>
  <span class="shortcuts-hint">← → navigate &nbsp;|&nbsp; / search</span>
  <button class="mobile-menu-btn" onclick="openDrawer()" aria-label="Open menu">☰</button>
</div>

<!-- Mobile drawer overlay -->
<div class="drawer-overlay" id="drawer-overlay" onclick="closeDrawer()"></div>

<!-- Mobile drawer -->
<div class="mobile-drawer" id="mobile-drawer">
  <div class="drawer-header">
    <span>SQL Mastery</span>
    <button class="drawer-close" onclick="closeDrawer()">×</button>
  </div>
  <div class="drawer-search">
    <input type="text" placeholder="Search weeks..." oninput="filterWeeks(this.value)" id="drawer-search-input">
  </div>
  <nav class="drawer-nav" id="drawer-nav">
    {sidebar_html}
  </nav>
</div>

<div class="layout">
  <aside class="sidebar">
    <div class="search-wrap">
      <input class="search-input" id="search-input" type="text"
        placeholder="/ Search weeks..." oninput="filterWeeks(this.value)">
    </div>
    <nav class="sidebar-nav" id="sidebar-nav">
      {sidebar_html}
    </nav>
  </aside>

  <main class="main" id="main">
    {home_html}
    {weeks_html}
  </main>
</div>

<div class="toast" id="toast"></div>

<script>
let currentWeek = 0;
const TOTAL = 23;

function showHome() {{
  document.querySelectorAll('.week-section').forEach(s => s.style.display = 'none');
  document.getElementById('home').style.display = 'block';
  document.querySelectorAll('.week-link').forEach(l => l.classList.remove('active'));
  currentWeek = 0;
  document.getElementById('main').scrollTop = 0;
  updateHomeDots();
}}

function showWeek(n) {{
  if (n < 1 || n > TOTAL) return;
  document.querySelectorAll('.week-section').forEach(s => s.style.display = 'none');
  const sec = document.getElementById('week-' + n);
  if (sec) sec.style.display = 'block';
  document.querySelectorAll('.week-link').forEach(l => l.classList.remove('active'));
  const link = document.querySelector('.week-link[data-week="' + n + '"]');
  if (link) {{
    link.classList.add('active');
    link.scrollIntoView({{block: 'nearest', behavior: 'smooth'}});
  }}
  currentWeek = n;
  document.getElementById('main').scrollTop = 0;
  closeDrawer();
  hljs.highlightAll();
}}

function toggleAnswers(id) {{
  const content = document.getElementById('ans-' + id);
  const btn = document.querySelector('#ans-wrap-' + id + ' .show-answers-btn');
  const visible = content.style.display !== 'none';
  content.style.display = visible ? 'none' : 'block';
  btn.textContent = visible ? 'Show Answers' : 'Hide Answers';
  if (!visible) hljs.highlightAll();
}}

function markComplete(n, done) {{
  const key = 'week-done-' + n;
  if (done) localStorage.setItem(key, '1');
  else localStorage.removeItem(key);
  const link = document.querySelector('.week-link[data-week="' + n + '"]');
  if (link) link.classList.toggle('done', done);
  const dot = document.getElementById('dot-' + n);
  if (dot) dot.classList.toggle('done', done);
  updateProgress();
  if (done) showToast('Week ' + n + ' marked complete ✓');
}}

function updateProgress() {{
  let done = 0;
  for (let i = 1; i <= TOTAL; i++) {{
    if (localStorage.getItem('week-done-' + i)) done++;
  }}
  const pct = Math.round((done / TOTAL) * 100);
  document.getElementById('progress-fill').style.width = pct + '%';
  document.getElementById('progress-label').textContent = done + ' / ' + TOTAL;
  const hf = document.getElementById('home-fill');
  if (hf) hf.style.width = pct + '%';
  const hc = document.getElementById('home-count');
  if (hc) hc.textContent = done + ' / ' + TOTAL + ' complete';
}}

function updateHomeDots() {{
  for (let i = 1; i <= TOTAL; i++) {{
    const dot = document.getElementById('dot-' + i);
    if (dot) dot.classList.toggle('done', !!localStorage.getItem('week-done-' + i));
  }}
}}

function loadProgress() {{
  for (let i = 1; i <= TOTAL; i++) {{
    const done = !!localStorage.getItem('week-done-' + i);
    const check = document.getElementById('check-' + i);
    if (check) check.checked = done;
    const link = document.querySelector('.week-link[data-week="' + i + '"]');
    if (link) link.classList.toggle('done', done);
  }}
  updateProgress();
  updateHomeDots();
}}

function copyCode(btn) {{
  const pre = btn.closest('.code-block').querySelector('pre');
  navigator.clipboard.writeText(pre.innerText).then(() => {{
    btn.textContent = 'Copied!';
    btn.classList.add('copied');
    setTimeout(() => {{ btn.textContent = 'Copy'; btn.classList.remove('copied'); }}, 2000);
  }});
}}

function showToast(msg) {{
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2500);
}}

function openDrawer() {{
  document.getElementById('mobile-drawer').classList.add('open');
  document.getElementById('drawer-overlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}}

function closeDrawer() {{
  document.getElementById('mobile-drawer').classList.remove('open');
  document.getElementById('drawer-overlay').classList.remove('open');
  document.body.style.overflow = '';
}}

function filterWeeks(q) {{
  const query = q.toLowerCase().trim();
  document.querySelectorAll('.week-link').forEach(link => {{
    const title = link.querySelector('.week-link-title').textContent.toLowerCase();
    const num = link.querySelector('.week-link-num').textContent.toLowerCase();
    link.style.display = (!query || title.includes(query) || num.includes(query)) ? '' : 'none';
  }});
}}


function togglePhase(header) {{
  const weeks = header.nextElementSibling;
  weeks.classList.toggle('collapsed');
  header.classList.toggle('collapsed');
}}

document.addEventListener('keydown', e => {{
  if (e.target.tagName === 'INPUT') return;
  if (e.key === 'ArrowRight') showWeek(currentWeek + 1);
  if (e.key === 'ArrowLeft') {{ if (currentWeek <= 1) showHome(); else showWeek(currentWeek - 1); }}
  if (e.key === '/') {{ e.preventDefault(); document.getElementById('search-input').focus(); }}
  if (e.key === 'Escape') document.getElementById('search-input').blur();
}});

loadProgress();
showHome();
hljs.highlightAll();
</script>
</body>
</html>"""


if __name__ == "__main__":
    print("Building SQL course HTML...")
    html = build_html()
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)
    size_kb = os.path.getsize(OUTPUT) // 1024
    print(f"Done! → sql-course.html ({size_kb} KB)")
    print(f"Open: open '{OUTPUT}'")
