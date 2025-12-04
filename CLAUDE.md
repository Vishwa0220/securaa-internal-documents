# Claude Code Project Guide

## Project Overview

This repository contains internal documentation for the Securaa Security Platform. It includes High Level Design (HLD) and Low Level Design (LLD) documents for various microservices, along with automated tools to generate HTML and PDF documentation.

## Repository Structure

```
securaa-internal-documents/
├── *.md                          # Source markdown documentation files
├── docs/                         # Generated documentation output
│   ├── *.html                    # HTML documentation files
│   ├── pdf/                      # PDF documentation files
│   └── README.md                 # Documentation portal readme
├── generate_documentation.py     # HTML generation script
├── generate_pdfs_enhanced.py     # PDF generation script
├── CLAUDE.md                     # This file
└── README.md                     # Project readme
```

## Documentation Services

| Service | Description |
|---------|-------------|
| Securaa Platform | Core platform architecture and deployment |
| Process Manager | Microservices orchestration and lifecycle management |
| Playbook Service | SOAR automation engine for security workflows |
| SIEM Service | Security Information and Event Management |
| User Service | Identity and access management with multi-tenancy |
| Custom Services | Custom application and integration management |
| Custom Utils | Utility services and helper functions |
| RIS Service | Remote Integration Service for connectivity |
| SIA Service | AI-powered SOC automation with LLM integration |

## Key Commands

### Generate HTML Documentation
```bash
# Create and activate virtual environment (first time)
python3 -m venv venv
source venv/bin/activate
pip install markdown playwright
playwright install chromium

# Generate HTML files
python3 generate_documentation.py
```

### Generate PDF Documentation
```bash
source venv/bin/activate
python3 generate_pdfs_enhanced.py
```

### View Documentation Locally
```bash
cd docs
python3 -m http.server 8080
# Open http://localhost:8080 in browser
```

## Code Style & Conventions

- **Markdown Files**: Use Mermaid syntax for all diagrams (flowcharts, sequence diagrams, ER diagrams, class diagrams)
- **Diagram Types**: `graph TB/LR`, `sequenceDiagram`, `erDiagram`, `classDiagram`, `flowchart`, `gantt`
- **File Naming**: `service-name-high-level-design.md` or `service-name-low-level-design.md`

## Important Notes

- All Mermaid diagrams are rendered client-side using Mermaid.js v10
- PDFs are generated using Playwright with Chromium headless browser
- The `docs/` folder contains generated output - regenerate after modifying source `.md` files
- Virtual environment (`venv/`) should not be committed to git

## Dependencies

- Python 3.10+
- `markdown` - Python markdown processing library
- `playwright` - Browser automation for PDF generation
- Chromium (installed via playwright)
