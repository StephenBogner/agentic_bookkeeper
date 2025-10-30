# Third-Party Licenses

This document lists all third-party open-source libraries used in Agentic Bookkeeper and their respective licenses.

**Last Updated:** 2025-10-30

---

## Summary

Agentic Bookkeeper uses the following open-source dependencies:

| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| PySide6 | >=6.6.0 | LGPL v3 | GUI Framework |
| watchdog | >=3.0.0 | Apache 2.0 | File System Monitoring |
| python-dotenv | >=1.0.0 | BSD 3-Clause | Configuration Management |
| pypdf | >=3.0.0 | BSD 3-Clause | PDF Processing |
| Pillow | >=10.0.0 | HPND | Image Processing |
| pytesseract | >=0.3.10 | Apache 2.0 | OCR Integration |
| pymupdf | >=1.23.0 | AGPL v3 | Advanced PDF Processing |
| requests | >=2.31.0 | Apache 2.0 | HTTP Client |
| openai | >=1.0.0 | MIT | OpenAI API Client |
| anthropic | >=0.7.0 | MIT | Anthropic API Client |
| google-generativeai | >=0.3.0 | Apache 2.0 | Google AI API Client |
| reportlab | >=4.0.0 | BSD 3-Clause | PDF Generation |
| pandas | >=2.0.0 | BSD 3-Clause | Data Analysis |
| cryptography | >=41.0.0 | Apache 2.0 / BSD | Encryption |

---

## License Details

### PySide6 (LGPL v3)

**License:** GNU Lesser General Public License v3
**Website:** https://www.qt.io/qt-for-python
**Copyright:** The Qt Company Ltd.

PySide6 is licensed under LGPL v3, which allows:

- Commercial use
- Modification
- Distribution
- Patent use
- Private use

Conditions:

- Disclose source for modifications to PySide6 itself (not required for applications using PySide6)
- Include license and copyright notice
- State changes made to the library

Note: Agentic Bookkeeper uses PySide6 as a library without modification, which is permitted under LGPL v3.

### watchdog (Apache 2.0)

**License:** Apache License 2.0
**Website:** https://github.com/gorakhargosh/watchdog
**Copyright:** Copyright 2011 Yesudeep Mangalapilly

Permissive license allowing commercial use, modification, distribution, and private use.

### python-dotenv (BSD 3-Clause)

**License:** BSD 3-Clause License
**Website:** https://github.com/theskumar/python-dotenv
**Copyright:** Copyright (c) 2014, Saurabh Kumar

Permissive license allowing commercial use, modification, distribution, and private use.

### pypdf (BSD 3-Clause)

**License:** BSD 3-Clause License
**Website:** https://github.com/py-pdf/pypdf
**Copyright:** Copyright (c) 2006-2008, Mathieu Fenniak; Copyright (c) 2007, Ashish Kulkarni

Permissive license allowing commercial use, modification, distribution, and private use.

### Pillow (HPND)

**License:** Historical Permission Notice and Disclaimer (HPND)
**Website:** https://python-pillow.org/
**Copyright:** Copyright (c) 1997-2011 by Secret Labs AB; Copyright (c) 1995-2011 by Fredrik Lundh

Permissive license similar to MIT/BSD allowing commercial use, modification, and distribution.

### pytesseract (Apache 2.0)

**License:** Apache License 2.0
**Website:** https://github.com/madmaze/pytesseract
**Copyright:** Copyright 2010-2022 Samuel Hoffstaetter

Permissive license allowing commercial use, modification, distribution, and private use.

### pymupdf (AGPL v3)

**License:** GNU Affero General Public License v3
**Website:** https://pymupdf.readthedocs.io/
**Copyright:** Copyright (c) 2015-2024 Artifex Software, Inc.

PyMuPDF is licensed under AGPL v3, which requires:

- Disclosure of source code if distributed
- Network use is considered distribution
- Same license for derivative works

Note: Agentic Bookkeeper uses PyMuPDF as a library without modification. For commercial applications distributed over a
network, consult PyMuPDF's commercial licensing options at https://artifex.com/licensing/.

### requests (Apache 2.0)

**License:** Apache License 2.0
**Website:** https://requests.readthedocs.io/
**Copyright:** Copyright 2019 Kenneth Reitz

Permissive license allowing commercial use, modification, distribution, and private use.

### openai (MIT)

**License:** MIT License
**Website:** https://github.com/openai/openai-python
**Copyright:** Copyright (c) OpenAI

Permissive license allowing commercial use, modification, distribution, and private use.

### anthropic (MIT)

**License:** MIT License
**Website:** https://github.com/anthropics/anthropic-sdk-python
**Copyright:** Copyright (c) Anthropic

Permissive license allowing commercial use, modification, distribution, and private use.

### google-generativeai (Apache 2.0)

**License:** Apache License 2.0
**Website:** https://github.com/google/generative-ai-python
**Copyright:** Copyright 2023 Google LLC

Permissive license allowing commercial use, modification, distribution, and private use.

### reportlab (BSD 3-Clause)

**License:** BSD 3-Clause License
**Website:** https://www.reportlab.com/opensource/
**Copyright:** Copyright (c) 2000-2023 ReportLab Inc.

Permissive license allowing commercial use, modification, distribution, and private use.

### pandas (BSD 3-Clause)

**License:** BSD 3-Clause License
**Website:** https://pandas.pydata.org/
**Copyright:** Copyright (c) 2008-2011, AQR Capital Management, LLC; Copyright (c) 2011-2024, Open source contributors

Permissive license allowing commercial use, modification, distribution, and private use.

### cryptography (Apache 2.0 / BSD)

**License:** Apache License 2.0 / BSD License (dual-licensed)
**Website:** https://cryptography.io/
**Copyright:** Copyright (c) Individual contributors

Permissive licenses allowing commercial use, modification, distribution, and private use.

---

## License Compliance

### Copyleft Licenses

Two dependencies use copyleft licenses that require special consideration:

1. **PySide6 (LGPL v3):** Used as a library without modification. LGPL v3 permits this usage in proprietary applications.

2. **PyMuPDF (AGPL v3):** Used as a library without modification. AGPL v3 requires source disclosure if the application
is distributed over a network. For network-based distribution of Agentic Bookkeeper, consider PyMuPDF's commercial license
or alternative PDF libraries.

### Permissive Licenses

The remaining 12 dependencies use permissive licenses (MIT, Apache 2.0, BSD 3-Clause, HPND) that allow:

- Commercial use
- Modification
- Distribution
- Private use

With minimal requirements:

- Include copyright notices
- Include license text
- Disclaimer of warranties

---

## Attribution

We gratefully acknowledge the authors and maintainers of these open-source libraries. Their contributions make
Agentic Bookkeeper possible.

---

## Obtaining License Texts

Full license texts for each dependency can be obtained:

1. From the Python package metadata:

   ```bash
   pip show <package-name>
   ```

2. From the package installation directory:

   ```bash
   python -c "import <package>; print(<package>.__file__)"
   # Look for LICENSE or COPYING file in package directory
   ```

3. From the project's GitHub repository or website (links provided above)

---

## License Text Locations

When distributing Agentic Bookkeeper, include this file (THIRD_PARTY_LICENSES.md) to comply with attribution
requirements. Full license texts are available in the installed Python packages.

---

## Questions or Concerns

For questions about license compliance or third-party dependencies, contact:

Stephen Bogner, P.Eng.
Email: stephenbogner@stephenbogner.com

---

**Note:** This document reflects the licenses as of the last update date. License information may change with package
updates. Always verify current license information from the package maintainers.
