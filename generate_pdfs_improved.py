#!/usr/bin/env python3
"""
Improved PDF Generator for Securaa Documentation
Addresses text visibility and image scaling issues
"""

import asyncio
import os
from playwright.async_api import async_playwright
from pathlib import Path

# HTML files to convert
HTML_FILES = [
    'index.html',
    'optimization-guide.html',
    'process-manager-high-level-design.html',
    'process-manager-low-level-design.html',
    'securaa-custom-services-high-level-design.html',
    'securaa-custom-services-low-level-design.html',
    'securaa-custom-utils-high-level-design.html',
    'securaa-custom-utils-low-level-design.html',
    'securaa-make-system-high-level-design.html',
    'securaa-make-system-low-level-design.html',
    'securaa-platform-high-level-design.html',
    'securaa-playbook-high-level-design.html',
    'securaa-playbook-low-level-design.html',
    'securaa-ris-high-level-design.html',
    'securaa-ris-low-level-design.html',
    'securaa-ris-client-documentation.html',
    'securaa-ris-server-documentation.html',
    'securaa-siem-high-level-design.html',
    'securaa-siem-low-level-design.html',
    'securaa-user-high-level-design.html',
    'securaa-user-low-level-design.html',
    'sia-service-high-level-design.html',
    'sia-service-low-level-design.html',
    'secura-customer-security-documentation.html',
    'securaa-information-security-risk-assesment-process.html',
]

async def inject_pdf_styles(page):
    """Inject additional styles to improve PDF rendering"""
    await page.add_style_tag(content="""
        @media print {
            /* Force all text to be visible */
            * {
                color: #000 !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            
            /* Ensure headers are visible */
            h1, h2, h3, h4, h5, h6 {
                color: #000 !important;
                page-break-after: avoid;
            }
            
            /* Make paragraphs and list items visible */
            p, li, td, th, span, div {
                color: #000 !important;
            }
            
            /* Code blocks */
            pre, code {
                color: #000 !important;
                background: #f5f5f5 !important;
                border: 1px solid #ddd !important;
            }
            
            /* Tables */
            table {
                width: 100% !important;
                page-break-inside: avoid;
            }
            
            th {
                background: #4f46e5 !important;
                color: #fff !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            
            /* Mermaid diagrams - reduce size */
            .mermaid {
                transform: scale(0.75);
                transform-origin: top left;
                margin: 20px 0 !important;
                page-break-inside: avoid;
                max-width: 100% !important;
            }
            
            /* SVG scaling for diagrams */
            .mermaid svg {
                max-width: 100% !important;
                height: auto !important;
            }
            
            /* Ensure backgrounds print */
            body {
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            
            /* Links should be visible */
            a {
                color: #4f46e5 !important;
                text-decoration: underline;
            }
            
            /* Hide navigation and header for cleaner PDF */
            .main-header,
            .documentation-nav {
                display: none !important;
            }
            
            /* Adjust main content padding */
            .main-content {
                padding: 20px !important;
                max-width: 100% !important;
            }
            
            /* Code blocks should fit */
            pre {
                white-space: pre-wrap !important;
                word-wrap: break-word !important;
                font-size: 10px !important;
                padding: 10px !important;
            }
            
            /* Lists */
            ul, ol {
                padding-left: 20px !important;
            }
            
            /* Blockquotes */
            blockquote {
                border-left: 4px solid #4f46e5 !important;
                padding-left: 15px !important;
                color: #333 !important;
            }
        }
    """)

async def generate_pdf(html_file, pdf_file):
    """Generate a single PDF from HTML with improved rendering"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Load the HTML file
        html_path = f"file://{os.path.abspath(html_file)}"
        await page.goto(html_path, wait_until='networkidle', timeout=60000)
        
        # Inject PDF-specific styles
        await inject_pdf_styles(page)
        
        # Wait for mermaid diagrams to render
        await page.wait_for_timeout(5000)
        
        # Additional wait to ensure all diagrams are rendered
        try:
            await page.wait_for_selector('.mermaid svg', timeout=10000)
        except:
            pass  # Some pages might not have mermaid diagrams
        
        # Generate PDF with optimized settings
        await page.pdf(
            path=pdf_file,
            format='A4',
            print_background=True,
            margin={
                'top': '20mm',
                'right': '15mm',
                'bottom': '20mm',
                'left': '15mm'
            },
            prefer_css_page_size=False,
            display_header_footer=True,
            header_template='<div style="font-size:10px;width:100%;text-align:center;color:#666;"></div>',
            footer_template='<div style="font-size:10px;width:100%;text-align:center;color:#666;padding:5px;">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>',
        )
        
        await browser.close()

async def main():
    """Main function to process all HTML files"""
    print("\n=== Starting Improved PDF Generation ===\n")
    
    docs_dir = Path('docs')
    pdf_dir = docs_dir / 'pdf'
    
    # Ensure PDF directory exists
    pdf_dir.mkdir(exist_ok=True)
    
    total_files = len(HTML_FILES)
    print(f"Total files to process: {total_files}\n")
    
    for idx, html_file in enumerate(HTML_FILES, 1):
        html_path = docs_dir / html_file
        pdf_path = pdf_dir / html_file.replace('.html', '.pdf')
        
        if not html_path.exists():
            print(f"⚠ Skipped: {html_file} (file not found)")
            continue
        
        try:
            await generate_pdf(str(html_path), str(pdf_path))
            print(f"✓ [{idx}/{total_files}] Generated: {pdf_path.name}")
        except Exception as e:
            print(f"✗ [{idx}/{total_files}] Failed: {html_file} - {str(e)}")
    
    print("\n=== PDF Generation Complete ===\n")
    print(f"PDFs saved to: {pdf_dir.absolute()}")

if __name__ == '__main__':
    asyncio.run(main())
