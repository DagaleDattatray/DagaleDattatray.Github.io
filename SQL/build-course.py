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


def escape_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def md_to_html(md_text):
    """Convert markdown to HTML sections."""
    lines = md_text.split("\n")
    html_parts = []
    i = 0
    in_code = False
    code_lines = []
    code_lang = ""
    in_table = False
    table_lines = []
    in_answers = False
    answer_buffer = []
    exercise_num = [0]

    def flush_table():
        nonlocal in_table, table_lines
        if not table_lines:
            return ""
        out = '<div class="table-wrap"><table>'
        for ti, trow in enumerate(table_lines):
            cells = [c.strip() for c in trow.strip().strip("|").split("|")]
            if ti == 0:
                out += "<thead><tr>" + "".join(f"<th>{escape_html(c)}</th>" for c in cells) + "</tr></thead><tbody>"
            elif ti == 1 and all(set(c.replace("-","").replace(":","").strip()) == set() or set(c.strip()) <= {'-',':'} for c in cells):
                continue
            else:
                out += "<tr>" + "".join(f"<td>{escape_html(c)}</td>" for c in cells) + "</tr>"
        out += "</tbody></table></div>"
        table_lines = []
        in_table = False
        return out

    def process_inline(text):
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # Inline code
        text = re.sub(r'`([^`]+)`', r'<code class="inline-code">\1</code>', text)
        # Italic
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        return text

    while i < len(lines):
        line = lines[i]

        # Code block start
        if line.strip().startswith("```"):
            if in_table:
                html_parts.append(flush_table())
            lang = line.strip()[3:].strip()
            code_lang = lang if lang else "sql"
            code_lines = []
            in_code = True
            i += 1
            continue

        # Code block end
        if in_code:
            if line.strip() == "```":
                code_content = escape_html("\n".join(code_lines))
                html_parts.append(
                    f'<div class="code-block"><div class="code-header">'
                    f'<span class="code-lang">{code_lang.upper()}</span>'
                    f'<button class="copy-btn" onclick="copyCode(this)">Copy</button></div>'
                    f'<pre><code class="language-{code_lang}">{code_content}</code></pre></div>'
                )
                in_code = False
                code_lines = []
            else:
                code_lines.append(line)
            i += 1
            continue

        # Table rows
        if line.strip().startswith("|"):
            if not in_table:
                in_table = True
            table_lines.append(line)
            i += 1
            continue
        elif in_table:
            html_parts.append(flush_table())

        # Horizontal rule
        if line.strip() in ("---", "***", "___"):
            html_parts.append('<hr class="section-divider">')
            i += 1
            continue

        # Headings
        if line.startswith("# "):
            html_parts.append(f'<h1 class="week-title">{process_inline(escape_html(line[2:]))}</h1>')
            i += 1
            continue
        if line.startswith("## "):
            html_parts.append(f'<h2 class="section-heading">{process_inline(escape_html(line[3:]))}</h2>')
            i += 1
            continue
        if line.startswith("### "):
            html_parts.append(f'<h3 class="sub-heading">{process_inline(escape_html(line[4:]))}</h3>')
            i += 1
            continue
        if line.startswith("#### "):
            html_parts.append(f'<h4 class="sub-sub-heading">{process_inline(escape_html(line[5:]))}</h4>')
            i += 1
            continue

        # Numbered list items (practice exercises detection)
        m = re.match(r'^(\d+)\.\s+(.*)', line)
        if m:
            num = int(m.group(1))
            content = m.group(2)
            html_parts.append(
                f'<div class="exercise-item"><span class="ex-num">{num}</span>'
                f'<span class="ex-text">{process_inline(escape_html(content))}</span></div>'
            )
            i += 1
            continue

        # Bullet list items
        if line.startswith("- ") or line.startswith("* "):
            content = line[2:]
            html_parts.append(f'<div class="bullet-item">• {process_inline(escape_html(content))}</div>')
            i += 1
            continue

        # Indented bullet
        if line.startswith("  - ") or line.startswith("  * "):
            content = line[4:]
            html_parts.append(f'<div class="bullet-item indent">◦ {process_inline(escape_html(content))}</div>')
            i += 1
            continue

        # Empty line
        if line.strip() == "":
            html_parts.append('<div class="spacer"></div>')
            i += 1
            continue

        # Paragraph
        html_parts.append(f'<p>{process_inline(escape_html(line))}</p>')
        i += 1

    if in_table:
        html_parts.append(flush_table())

    return "\n".join(html_parts)


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
        <button class="nav-btn complete-btn" onclick="markComplete({week_num}, true); document.getElementById('check-{week_num}').checked=true; updateProgress()">
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
  --sidebar-width: 280px;
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
  line-height: 1.6;
}}

/* HEADER */
.header {{
  height: 56px;
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
  max-width: 300px;
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
  padding-bottom: 16px;
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
.phase-weeks {{ }}
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
.week-link.done .week-link-title {{ color: var(--text-muted); }}
.week-check {{ accent-color: var(--green); cursor: pointer; flex-shrink: 0; }}
.week-link-num {{
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  font-family: 'JetBrains Mono', monospace;
  min-width: 28px;
}}
.week-link-title {{ flex: 1; }}
.week-link[style*="display:none"] {{ display: none !important; }}

.badge {{ font-size: 9px; font-weight: 700; padding: 2px 5px; border-radius: 3px; }}
.badge-project {{ background: rgba(188,140,255,0.2); color: var(--purple); }}
.badge-interview {{ background: rgba(210,153,34,0.2); color: var(--orange); }}
.badge-capstone {{ background: rgba(248,81,73,0.15); color: var(--red); }}

/* MAIN */
.main {{
  flex: 1;
  overflow-y: auto;
  padding: 0;
}}
.main::-webkit-scrollbar {{ width: 6px; }}
.main::-webkit-scrollbar-track {{ background: transparent; }}
.main::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}

/* HOME */
.home-hero {{
  padding: 48px 40px 32px;
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
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
  padding: 32px 40px;
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
.home-card:hover {{
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}}
.home-card.phase1:hover {{ border-color: var(--accent); }}
.home-card.phase2:hover {{ border-color: var(--green); }}
.home-card.phase3:hover {{ border-color: var(--purple); }}
.home-card-week {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 6px;
}}
.home-card.phase1 .home-card-week {{ color: var(--accent); }}
.home-card.phase2 .home-card-week {{ color: var(--green); }}
.home-card.phase3 .home-card-week {{ color: var(--purple); }}
.home-card-title {{
  font-size: 13px;
  font-weight: 500;
  line-height: 1.4;
}}
.home-card-dot {{
  position: absolute;
  top: 12px;
  right: 12px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--border);
  transition: background 0.2s;
}}
.home-card-dot.done {{ background: var(--green); }}

/* WEEK SECTION */
.week-section {{ display: none; }}
.week-section.visible {{ display: block; }}
.week-header {{
  padding: 32px 40px 24px;
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
  padding: 3px 8px;
  border-radius: 4px;
  letter-spacing: 0.06em;
}}
.week-type-badge.lesson {{ background: rgba(88,166,255,0.15); color: var(--accent); }}
.week-type-badge.project {{ background: rgba(188,140,255,0.15); color: var(--purple); }}
.week-type-badge.interview {{ background: rgba(210,153,34,0.15); color: var(--orange); }}
.week-type-badge.capstone {{ background: rgba(248,81,73,0.12); color: var(--red); }}
.week-main-title {{
  font-size: 26px;
  font-weight: 700;
  color: var(--text);
}}

.week-content {{
  padding: 32px 40px;
  max-width: 860px;
}}

/* CONTENT ELEMENTS */
.week-content h1.week-title {{ display: none; }}
.week-content h2.section-heading {{
  font-size: 18px;
  font-weight: 600;
  color: var(--text);
  margin: 28px 0 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}}
.week-content h3.sub-heading {{
  font-size: 15px;
  font-weight: 600;
  color: var(--accent);
  margin: 20px 0 8px;
}}
.week-content h4.sub-sub-heading {{
  font-size: 14px;
  font-weight: 600;
  color: var(--text-muted);
  margin: 16px 0 6px;
}}
.week-content p {{
  margin: 8px 0;
  color: var(--text);
  line-height: 1.7;
}}
.section-divider {{
  border: none;
  border-top: 1px solid var(--border);
  margin: 20px 0;
}}
.spacer {{ height: 4px; }}
.bullet-item {{
  padding: 4px 0 4px 16px;
  color: var(--text);
  line-height: 1.6;
}}
.bullet-item.indent {{ padding-left: 32px; color: var(--text-muted); }}
.exercise-item {{
  display: flex;
  gap: 10px;
  padding: 8px 0;
  align-items: flex-start;
}}
.ex-num {{
  min-width: 24px;
  height: 24px;
  background: var(--accent);
  color: var(--bg);
  border-radius: 50%;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}}
.ex-text {{ line-height: 1.6; }}
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

/* TABLES */
.table-wrap {{
  overflow-x: auto;
  margin: 14px 0;
  border-radius: 8px;
  border: 1px solid var(--border);
}}
table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}}
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
  padding: 24px 40px 48px;
  border-top: 1px solid var(--border);
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
  bottom: 24px;
  right: 24px;
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

@media (max-width: 700px) {{
  :root {{ --sidebar-width: 0px; }}
  .sidebar {{ display: none; }}
  .week-content, .week-header, .week-nav {{ padding-left: 20px; padding-right: 20px; }}
  .home-cards {{ padding: 20px; }}
  .home-hero {{ padding: 28px 20px 20px; }}
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
</div>

<div class="layout">
  <aside class="sidebar">
    <div class="search-wrap">
      <input class="search-input" id="search-input" type="text" placeholder="/ Search weeks..." oninput="filterWeeks(this.value)">
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
  if (sec) {{ sec.style.display = 'block'; }}
  document.querySelectorAll('.week-link').forEach(l => l.classList.remove('active'));
  const link = document.querySelector('.week-link[data-week="' + n + '"]');
  if (link) {{
    link.classList.add('active');
    link.scrollIntoView({{block: 'nearest', behavior: 'smooth'}});
  }}
  currentWeek = n;
  document.getElementById('main').scrollTop = 0;
  hljs.highlightAll();
}}

function markComplete(n, done) {{
  const key = 'week-done-' + n;
  if (done) {{ localStorage.setItem(key, '1'); }}
  else {{ localStorage.removeItem(key); }}
  const link = document.querySelector('.week-link[data-week="' + n + '"]');
  if (link) {{ link.classList.toggle('done', done); }}
  const dot = document.getElementById('dot-' + n);
  if (dot) {{ dot.classList.toggle('done', done); }}
  updateProgress();
  if (done) {{ showToast('Week ' + n + ' marked complete ✓'); }}
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
  const text = pre.innerText;
  navigator.clipboard.writeText(text).then(() => {{
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
  const collapsed = weeks.classList.toggle('collapsed');
  header.classList.toggle('collapsed', collapsed);
}}

document.addEventListener('keydown', e => {{
  if (e.target.tagName === 'INPUT') return;
  if (e.key === 'ArrowRight') showWeek(currentWeek + 1);
  if (e.key === 'ArrowLeft') {{ if (currentWeek <= 1) showHome(); else showWeek(currentWeek - 1); }}
  if (e.key === '/') {{ e.preventDefault(); document.getElementById('search-input').focus(); }}
  if (e.key === 'Escape') {{ document.getElementById('search-input').blur(); }}
}});

// Init
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
    print(f"Open in browser: open '{OUTPUT}'")
