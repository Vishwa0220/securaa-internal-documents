# Securaa Internal Documents

Internal documentation repository for the Securaa Security Platform, containing High Level Design (HLD) and Low Level Design (LLD) documents for all platform microservices.

## Quick Start

### View Documentation
Open `docs/index.html` in a web browser, or serve locally:
```bash
cd docs && python3 -m http.server 8080
```

### Regenerate Documentation
```bash
# Setup (first time only)
python3 -m venv venv
source venv/bin/activate
pip install markdown playwright
playwright install chromium

# Generate HTML and PDF
python3 generate_documentation.py
python3 generate_pdfs_enhanced.py
```

## Repository Structure

```
├── *.md                        # Source documentation (markdown)
├── docs/                       # Generated HTML & PDF output
│   ├── *.html                  # HTML documentation
│   ├── pdf/                    # PDF documentation
│   └── README.md               # Docs folder readme
├── generate_documentation.py   # HTML generator script
├── generate_pdfs_enhanced.py   # PDF generator script
├── CLAUDE.md                   # Claude Code project guide
├── SESSION_DATA.md             # Session notes
└── README.md                   # This file
```

## Documentation Contents

### Core Services
| Service | HLD | LLD |
|---------|-----|-----|
| Securaa Platform | ✅ | - |
| Process Manager | ✅ | ✅ |
| Playbook Service | ✅ | ✅ |
| SIEM Service | ✅ | ✅ |
| User Service | ✅ | ✅ |
| Custom Services | ✅ | ✅ |
| Custom Utils | ✅ | ✅ |
| RIS Service | ✅ | ✅ |
| SIA Service | ✅ | ✅ |

### Additional Documentation
- Optimization Guide
- Make System Documentation
- Customer Security Documentation
- Information Security Risk Assessment

## Features

- **Mermaid Diagrams**: All architecture diagrams rendered using Mermaid.js
- **Responsive HTML**: Modern, mobile-friendly documentation portal
- **PDF Export**: Print-ready PDFs with properly sized diagrams
- **Navigation**: Quick navigation between all documentation sections

## Technology Stack

- **Source Format**: Markdown with Mermaid diagrams
- **HTML Generation**: Python `markdown` library
- **PDF Generation**: Playwright + Chromium
- **Diagram Rendering**: Mermaid.js v10

## Contributing

1. Edit the source `.md` files
2. Run `python3 generate_documentation.py` to regenerate HTML
3. Run `python3 generate_pdfs_enhanced.py` to regenerate PDFs
4. Commit and push changes

## License

Proprietary - Securaa Security Platform
