#!/usr/bin/env python3
"""Repair generated Core-page shell/touch drift exposed by Issue #10.

The quality observer and inline Core CSS key the tablet shell on
``header[data-g9-shell-header]``. The renderer had retained only the newer CSS
class, so restore the semantic marker and the historical PDF action marker.

The cold-run also exposed six shared concept-triad links whose rendered hit
boxes were only line-height tall: three breadcrumb links and the Learn / Practice /
Question Bank links. Give those generated links the same 48 px minimum touch
geometry as the rest of the governed shell without changing academic content.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PATH = REPO / "Shared/tools/render_core.py"
text = PATH.read_text(encoding="utf-8")

old_header = "return (f'<header class=\"g9-shell-header\"><div class=\"g9-header-inner\">'"
new_header = "return (f'<header class=\"g9-shell-header\" data-g9-shell-header><div class=\"g9-header-inner\">'"
if old_header in text:
    text = text.replace(old_header, new_header, 1)
elif new_header not in text:
    raise SystemExit("shell_header emitter shape changed; reconcile manually")

old_pdf = "pdf_btn = f'<a class=\"g9-header-btn\" href=\"{esc(pdf_href)}\" title=\"{esc(pdf_name)}\">PDF</a>' if pdf_href else \"\""
new_pdf = "pdf_btn = f'<a class=\"g9-header-btn\" data-g9-action=\"pdf\" href=\"{esc(pdf_href)}\" title=\"{esc(pdf_name)}\">PDF</a>' if pdf_href else \"\""
if old_pdf in text:
    text = text.replace(old_pdf, new_pdf, 1)
elif new_pdf not in text:
    raise SystemExit("PDF header action emitter shape changed; reconcile manually")

old_touch = ".g9-triad-context a{color:inherit;text-decoration:none}\n.g9-triad-context a:hover{text-decoration:underline}"
new_touch = (
    ".g9-triad-context a{color:inherit;text-decoration:none;min-height:var(--g9-touch-min);"
    "min-width:var(--g9-touch-min);padding:0 8px;box-sizing:border-box;display:inline-flex;"
    "align-items:center;justify-content:center;touch-action:manipulation}\n"
    ".g9-triad-context a:hover{text-decoration:underline}\n"
    ".g9-triad-actions a{min-height:var(--g9-touch-min);min-width:var(--g9-touch-min);"
    "padding:10px 14px;box-sizing:border-box;display:inline-flex;align-items:center;"
    "justify-content:center;touch-action:manipulation}"
)
if old_touch in text:
    text = text.replace(old_touch, new_touch, 1)
elif new_touch not in text:
    raise SystemExit("concept-triad CSS shape changed; reconcile manually")

PATH.write_text(text, encoding="utf-8")
print("reconciled generated Core shell markers and concept-triad touch geometry")
