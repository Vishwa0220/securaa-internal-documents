# Securaa Platform Documentation

This folder contains comprehensive HTML and PDF documentation for the Securaa Platform, automatically generated from the markdown files in the repository.

## Contents

### HTML Documentation
- `index.html` - Main documentation portal and entry point
- Individual service documentation files (HLD and LLD for each service)

### PDF Documentation
The `pdf/` folder contains print-optimized PDF versions of all documentation with properly rendered diagrams.

## Generated Files

| Service | High Level Design | Low Level Design |
|---------|------------------|------------------|
| Securaa Platform | `securaa-platform-high-level-design.html` | - |
| Process Manager | `process-manager-high-level-design.html` | `process-manager-low-level-design.html` |
| Playbook Service | `securaa-playbook-high-level-design.html` | `securaa-playbook-low-level-design.html` |
| SIEM Service | `securaa-siem-high-level-design.html` | `securaa-siem-low-level-design.html` |
| User Service | `securaa-user-high-level-design.html` | `securaa-user-low-level-design.html` |
| Custom Services | `securaa-custom-services-high-level-design.html` | `securaa-custom-services-low-level-design.html` |
| Custom Utils | `securaa-custom-utils-high-level-design.html` | `securaa-custom-utils-low-level-design.html` |
| RIS Service | `securaa-ris-high-level-design.html` | `securaa-ris-low-level-design.html` |
| SIA Service | `sia-service-high-level-design.html` | `sia-service-low-level-design.html` |

### Additional Documentation
- `OPTIMIZATION_GUIDE.html` - Performance optimization best practices
- `securaa-make-system.html` - Build and deployment system
- `securaa-ris-client-documentation.html` - RIS client documentation
- `securaa-ris-server-documentation.html` - RIS server documentation
- `secura-customer-security-documentation.html` - Customer security documentation
- `securaa-information-security-risk-assesment-process.html` - Risk assessment process

## How to Regenerate Documentation

### Prerequisites
Create a Python virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install markdown playwright
playwright install chromium
```

### Generate HTML Files
```bash
source venv/bin/activate
python3 generate_documentation.py
```

### Generate PDF Files
```bash
source venv/bin/activate
python3 generate_pdfs_enhanced.py
```

## Features

### HTML Documentation
- **Modern Design**: Clean, professional styling with responsive layout
- **Mermaid Diagrams**: Fully rendered architecture diagrams, flowcharts, sequence diagrams, and ER diagrams
- **Navigation**: Sticky header with quick navigation to all main sections
- **Typography**: Clear hierarchy with readable fonts and proper spacing
- **Code Highlighting**: Syntax-highlighted code blocks with proper formatting
- **Tables**: Styled tables with alternating row colors
- **Print Support**: Optimized CSS for browser printing

### PDF Documentation
- **Proper Diagram Sizing**: Diagrams automatically scaled to fit page width
- **Page Breaks**: Intelligent page breaks to keep content together
- **Headers/Footers**: Page numbers and document title
- **Text Visibility**: All text rendered in black for maximum readability
- **Professional Layout**: A4 format with proper margins

## Technology Stack

- **Markdown Processing**: Python `markdown` library with extensions
- **Mermaid Diagrams**: Mermaid.js v10 for diagram rendering
- **PDF Generation**: Playwright with Chromium for headless rendering
- **Styling**: Custom CSS with CSS variables for theming

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Viewing Documentation

### Local Viewing
Open `index.html` directly in a web browser.

### Web Server
```bash
# Python built-in server
python3 -m http.server 8080

# Or use any static file server
npx serve .
```

Then navigate to `http://localhost:8080/docs_new/`
