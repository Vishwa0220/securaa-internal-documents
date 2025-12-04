#!/usr/bin/env python3
"""
Securaa Enhanced PDF Generator
Generates high-quality PDFs from HTML documentation with properly sized diagrams.
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright


# Configuration
DOCS_DIR = Path('docs')
PDF_DIR = DOCS_DIR / 'pdf'

# HTML files to convert to PDF
HTML_FILES = [
    'securaa-platform-high-level-design.html',
    'process-manager-high-level-design.html',
    'process-manager-low-level-design.html',
    'securaa-playbook-high-level-design.html',
    'securaa-playbook-low-level-design.html',
    'securaa-siem-high-level-design.html',
    'securaa-siem-low-level-design.html',
    'securaa-user-high-level-design.html',
    'securaa-user-low-level-design.html',
    'securaa-custom-services-high-level-design.html',
    'securaa-custom-services-low-level-design.html',
    'securaa-custom-utils-high-level-design.html',
    'securaa-custom-utils-low-level-design.html',
    'securaa-ris-high-level-design.html',
    'securaa-ris-low-level-design.html',
    'securaa-ris-client-documentation.html',
    'securaa-ris-server-documentation.html',
    'sia-service-high-level-design.html',
    'sia-service-low-level-design.html',
    'securaa-make-system.html',
    'OPTIMIZATION_GUIDE.html',
    'secura-customer-security-documentation.html',
    'securaa-information-security-risk-assesment-process.html',
]

# Enhanced CSS for PDF rendering - with LARGER diagrams
PDF_CSS = """
/* PDF-specific styles for better diagram rendering */
@page {
    size: A4;
    margin: 12mm 10mm 15mm 10mm;
}

/* General text styling for better PDF readability */
body {
    font-family: 'Helvetica Neue', Arial, sans-serif !important;
    font-size: 10pt !important;
    line-height: 1.5 !important;
    color: #1a1a1a !important;
    background: white !important;
}

/* Hide navigation and footer for PDF */
.main-header,
.documentation-nav,
.footer {
    display: none !important;
}

/* Main content area - use full width */
.main-content {
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    box-shadow: none !important;
    border-radius: 0 !important;
}

/* Typography for PDF */
h1 {
    font-size: 20pt !important;
    color: #1a365d !important;
    -webkit-text-fill-color: #1a365d !important;
    background: none !important;
    border-bottom: 2px solid #3182ce !important;
    padding-bottom: 6pt !important;
    margin-top: 0 !important;
    margin-bottom: 12pt !important;
    page-break-after: avoid !important;
}

h2 {
    font-size: 14pt !important;
    color: #2c5282 !important;
    border-bottom: 1px solid #cbd5e0 !important;
    padding-bottom: 4pt !important;
    margin-top: 16pt !important;
    margin-bottom: 8pt !important;
    page-break-after: avoid !important;
}

h3 {
    font-size: 12pt !important;
    color: #2d3748 !important;
    margin-top: 12pt !important;
    margin-bottom: 6pt !important;
    page-break-after: avoid !important;
}

h4 {
    font-size: 11pt !important;
    color: #4a5568 !important;
    margin-top: 10pt !important;
    margin-bottom: 4pt !important;
    page-break-after: avoid !important;
}

h5, h6 {
    font-size: 10pt !important;
    color: #4a5568 !important;
    page-break-after: avoid !important;
}

p {
    margin-bottom: 6pt !important;
    text-align: justify !important;
    orphans: 3 !important;
    widows: 3 !important;
}

/* Lists */
ul, ol {
    margin-bottom: 6pt !important;
    padding-left: 18pt !important;
}

li {
    margin-bottom: 3pt !important;
}

/* Code blocks */
pre {
    background: #f7fafc !important;
    color: #2d3748 !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 4pt !important;
    padding: 8pt !important;
    font-size: 7pt !important;
    line-height: 1.3 !important;
    overflow-x: visible !important;
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    page-break-inside: avoid !important;
    margin: 8pt 0 !important;
}

code {
    font-family: 'Consolas', 'Monaco', monospace !important;
    font-size: 7pt !important;
}

:not(pre) > code {
    background: #edf2f7 !important;
    color: #2d3748 !important;
    padding: 1pt 3pt !important;
    border-radius: 2pt !important;
}

/* Tables */
table {
    width: 100% !important;
    border-collapse: collapse !important;
    margin: 8pt 0 !important;
    font-size: 8pt !important;
    page-break-inside: avoid !important;
}

thead {
    background: #2c5282 !important;
}

th {
    color: white !important;
    padding: 6pt !important;
    text-align: left !important;
    font-weight: 600 !important;
    font-size: 7pt !important;
}

td {
    padding: 5pt 6pt !important;
    border: 1px solid #e2e8f0 !important;
}

tr:nth-child(even) {
    background: #f7fafc !important;
}

/* Blockquotes */
blockquote {
    border-left: 3pt solid #3182ce !important;
    padding-left: 10pt !important;
    margin: 8pt 0 !important;
    background: #ebf8ff !important;
    padding: 8pt !important;
    border-radius: 0 4pt 4pt 0 !important;
    page-break-inside: avoid !important;
}

/* Links */
a {
    color: #2b6cb0 !important;
    text-decoration: none !important;
}

/* Horizontal rules */
hr {
    border: none !important;
    border-top: 1px solid #e2e8f0 !important;
    margin: 12pt 0 !important;
}

/* MERMAID DIAGRAMS - LARGE and readable */
.mermaid {
    display: block !important;
    width: 100% !important;
    margin: 12pt 0 !important;
    padding: 8pt !important;
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 4pt !important;
    page-break-inside: avoid !important;
    overflow: visible !important;
    text-align: center !important;
}

/* SVG should take full width */
.mermaid svg {
    display: block !important;
    margin: 0 auto !important;
    width: 100% !important;
    max-width: none !important;
    height: auto !important;
    min-height: 100px !important;
}

/* Ensure diagram labels are readable - LARGER font */
.mermaid text,
.mermaid .nodeLabel,
.mermaid .label,
.mermaid .edgeLabel,
.mermaid .cluster-label,
.mermaid tspan {
    font-family: 'Helvetica Neue', Arial, sans-serif !important;
    font-size: 10pt !important;
    fill: #1a202c !important;
}

/* Node styling for better visibility */
.mermaid .node rect,
.mermaid .node circle,
.mermaid .node polygon,
.mermaid .node ellipse {
    stroke: #2d3748 !important;
    stroke-width: 1.5px !important;
}

/* Edge/line styling - thicker lines */
.mermaid .edgePath path,
.mermaid .flowchart-link {
    stroke: #2d3748 !important;
    stroke-width: 2px !important;
}

/* Arrow styling */
.mermaid marker path {
    fill: #2d3748 !important;
}

/* Cluster/subgraph styling */
.mermaid .cluster rect {
    fill: #f0f4f8 !important;
    stroke: #718096 !important;
    stroke-width: 1.5px !important;
}

/* Sequence diagram specific */
.mermaid .actor {
    stroke: #2d3748 !important;
    fill: #e2e8f0 !important;
}

.mermaid .actor-line {
    stroke: #718096 !important;
    stroke-width: 1px !important;
}

.mermaid .messageLine0,
.mermaid .messageLine1 {
    stroke: #2d3748 !important;
    stroke-width: 1.5px !important;
}

/* ER diagram specific */
.mermaid .er.entityBox {
    fill: #e2e8f0 !important;
    stroke: #2d3748 !important;
}

/* Class diagram specific */
.mermaid .classGroup rect {
    fill: #e2e8f0 !important;
    stroke: #2d3748 !important;
}

/* Flowchart specific - node colors */
.mermaid .node.default > rect,
.mermaid .node.default > polygon {
    fill: #e2e8f0 !important;
}

/* Page break handling */
h2 {
    page-break-before: auto !important;
}

h1, h2, h3, h4, h5, h6 {
    page-break-after: avoid !important;
}

/* Large diagrams get their own page */
.mermaid.large-diagram {
    page-break-before: always !important;
}
"""


async def inject_pdf_styles(page):
    """Inject PDF-specific styles for better rendering."""
    await page.add_style_tag(content=PDF_CSS)


async def wait_for_mermaid_diagrams(page, timeout=45000):
    """Wait for all Mermaid diagrams to render completely."""
    try:
        # Wait for mermaid to be loaded
        await page.wait_for_function(
            "typeof mermaid !== 'undefined'",
            timeout=timeout
        )

        # Wait for initial rendering
        await page.wait_for_timeout(3000)

        # Check if there are mermaid divs and wait for them to be processed
        await page.wait_for_function(
            """() => {
                const diagrams = document.querySelectorAll('.mermaid');
                if (diagrams.length === 0) return true;

                // Check if all diagrams have SVGs
                for (let d of diagrams) {
                    if (!d.querySelector('svg') && !d.getAttribute('data-processed')) {
                        return false;
                    }
                }
                return true;
            }""",
            timeout=timeout
        )

        # Additional wait for SVG rendering to complete
        await page.wait_for_timeout(2000)

    except Exception as e:
        print(f"    Warning: Mermaid wait issue: {e}")


async def optimize_diagrams_for_pdf(page):
    """Optimize diagram sizes for PDF rendering - make them LARGER."""
    await page.evaluate("""
        () => {
            const diagrams = document.querySelectorAll('.mermaid');

            diagrams.forEach((diagram, index) => {
                const svg = diagram.querySelector('svg');
                if (!svg) return;

                // Remove any max-width constraints
                svg.style.maxWidth = 'none';
                svg.style.width = '100%';
                svg.style.height = 'auto';
                svg.style.display = 'block';
                svg.style.margin = '0 auto';

                // Remove width/height attributes to let CSS control sizing
                svg.removeAttribute('width');
                svg.removeAttribute('height');

                // Get the viewBox for proper scaling
                const viewBox = svg.getAttribute('viewBox');
                if (viewBox) {
                    const parts = viewBox.split(' ');
                    if (parts.length === 4) {
                        const vbWidth = parseFloat(parts[2]);
                        const vbHeight = parseFloat(parts[3]);

                        // Set a reasonable aspect ratio preserving size
                        if (vbHeight > vbWidth * 1.5) {
                            // Very tall diagram - mark as large
                            diagram.classList.add('large-diagram');
                        }
                    }
                }

                // Increase text sizes in the SVG
                const texts = svg.querySelectorAll('text, tspan, .nodeLabel, .label, .edgeLabel');
                texts.forEach(text => {
                    const currentSize = parseFloat(window.getComputedStyle(text).fontSize) || 12;
                    if (currentSize < 10) {
                        text.style.fontSize = '10px';
                    }
                });

                // Make lines thicker
                const paths = svg.querySelectorAll('path, line');
                paths.forEach(path => {
                    const currentWidth = parseFloat(window.getComputedStyle(path).strokeWidth) || 1;
                    if (currentWidth < 1.5) {
                        path.style.strokeWidth = '1.5px';
                    }
                });
            });
        }
    """)


async def generate_pdf(html_path: Path, pdf_path: Path):
    """Generate a PDF from an HTML file with optimized diagram rendering."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        try:
            # Set a larger viewport for better diagram rendering
            await page.set_viewport_size({"width": 1400, "height": 900})

            # Navigate to the HTML file
            file_url = f'file://{html_path.absolute()}'
            await page.goto(file_url, wait_until='networkidle')

            # Wait for Mermaid diagrams to render
            await wait_for_mermaid_diagrams(page)

            # Inject PDF-specific styles
            await inject_pdf_styles(page)

            # Optimize diagrams for PDF
            await optimize_diagrams_for_pdf(page)

            # Additional wait for styles to apply
            await page.wait_for_timeout(1500)

            # Generate PDF with optimized settings
            await page.pdf(
                path=str(pdf_path),
                format='A4',
                print_background=True,
                margin={
                    'top': '12mm',
                    'right': '10mm',
                    'bottom': '15mm',
                    'left': '10mm'
                },
                display_header_footer=True,
                header_template='''
                    <div style="font-size: 8pt; color: #718096; width: 100%; text-align: center; padding: 5px 10mm;">
                        Securaa Platform Documentation
                    </div>
                ''',
                footer_template='''
                    <div style="font-size: 8pt; color: #718096; width: 100%; padding: 5px 10mm; display: flex; justify-content: space-between;">
                        <span>Confidential</span>
                        <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
                    </div>
                ''',
                prefer_css_page_size=False,
                scale=1.0  # Full scale for maximum readability
            )

            print(f"  Generated: {pdf_path.name}")

        except Exception as e:
            print(f"  Error generating {pdf_path.name}: {e}")
            raise

        finally:
            await browser.close()


async def main():
    """Main function to generate all PDFs."""
    print("\n=== Securaa PDF Generator ===\n")

    # Ensure PDF directory exists
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    success_count = 0
    error_count = 0

    for html_file in HTML_FILES:
        html_path = DOCS_DIR / html_file
        pdf_file = html_file.replace('.html', '.pdf')
        pdf_path = PDF_DIR / pdf_file

        if not html_path.exists():
            print(f"  Skipped: {html_file} (not found)")
            error_count += 1
            continue

        try:
            await generate_pdf(html_path, pdf_path)
            success_count += 1
        except Exception as e:
            print(f"  Failed: {html_file} - {e}")
            error_count += 1

    print(f"\n=== PDF Generation Complete ===")
    print(f"  Successful: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Output directory: {PDF_DIR.absolute()}")


if __name__ == '__main__':
    asyncio.run(main())
