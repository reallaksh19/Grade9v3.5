#!/usr/bin/env python3
"""Repair the generated Core-page shell marker drift exposed by Issue #10.

The shared inline Core CSS and quality observer both key the tablet shell on
``header[data-g9-shell-header]``.  The current ``shell_header`` emitter retained
only the newer CSS class, so its own 48 px target rules did not apply and the
quality observer could not see the shell.  Keep the class and restore the
semantic data marker; also restore the historical PDF action marker while this
header is being reconciled.
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

PATH.write_text(text, encoding="utf-8")
print("reconciled generated Core shell marker and PDF action marker")
