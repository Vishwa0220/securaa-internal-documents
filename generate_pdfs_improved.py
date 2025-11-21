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
                page-break-inside: avoid;
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
            
            /* Mermaid diagrams - intelligent sizing */
            .mermaid {
                page-break-before: auto !important;
                page-break-after: auto !important;
                page-break-inside: avoid !important;
                margin: 30px auto !important;
                padding: 20px 0 !important;
                display: block !important;
                width: 100% !important;
                max-width: 100% !important;
                overflow: visible !important;
            }
            
            /* SVG scaling for diagrams with responsive sizing */
            .mermaid svg {
                max-width: 95% !important;
                max-height: 900px !important;
                width: auto !important;
                height: auto !important;
                margin: 0 auto !important;
                display: block !important;
            }
            
            /* Large diagrams (width > 1200px) - scale down more */
            .mermaid svg[width^="1"], 
            .mermaid svg[width^="2"],
            .mermaid svg[width^="3"] {
                transform: scale(0.65) !important;
                transform-origin: center top !important;
                margin-bottom: 40px !important;
            }
            
            /* Medium diagrams (width 600-1200px) - moderate scaling */
            .mermaid svg[width^="6"],
            .mermaid svg[width^="7"],
            .mermaid svg[width^="8"],
            .mermaid svg[width^="9"] {
                transform: scale(0.8) !important;
                transform-origin: center top !important;
                margin-bottom: 30px !important;
            }
            
            /* Small diagrams - keep original size */
            .mermaid svg[width^="4"],
            .mermaid svg[width^="5"] {
                transform: scale(0.9) !important;
                transform-origin: center top !important;
                margin-bottom: 20px !important;
            }
            
            /* Flowchart specific styling */
            .mermaid svg[id*="flowchart"],
            .mermaid svg .flowchart {
                max-height: 850px !important;
            }
            
            /* Sequence diagrams */
            .mermaid svg[id*="sequence"] {
                max-height: 900px !important;
                transform: scale(0.75) !important;
                transform-origin: center top !important;
            }
            
            /* Class diagrams */
            .mermaid svg[id*="class"] {
                max-height: 850px !important;
                transform: scale(0.7) !important;
                transform-origin: center top !important;
            }
            
            /* ER diagrams */
            .mermaid svg[id*="er"] {
                max-height: 800px !important;
                transform: scale(0.75) !important;
                transform-origin: center top !important;
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
                font-size: 9px !important;
                padding: 10px !important;
                page-break-inside: avoid !important;
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
                page-break-inside: avoid !important;
            }
            
            /* Section breaks */
            h2 {
                page-break-before: auto !important;
                margin-top: 30px !important;
            }
            
            /* Keep related content together */
            h3, h4 {
                page-break-after: avoid !important;
            }
            
            h3 + .mermaid,
            h4 + .mermaid,
            h2 + .mermaid {
                page-break-before: avoid !important;
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
        
        # Dynamically adjust diagram sizes based on dimensions
        await page.evaluate("""
            () => {
                const diagrams = document.querySelectorAll('.mermaid svg');
                diagrams.forEach((svg) => {
                    const width = svg.getAttribute('width') || svg.viewBox?.baseVal.width || 0;
                    const height = svg.getAttribute('height') || svg.viewBox?.baseVal.height || 0;
                    
                    const numWidth = parseFloat(width);
                    const numHeight = parseFloat(height);
                    
                    // Very large diagrams (>1500px width or >1000px height)
                    if (numWidth > 1500 || numHeight > 1000) {
                        svg.style.transform = 'scale(0.55)';
                        svg.style.transformOrigin = 'center top';
                        svg.parentElement.style.marginBottom = '60px';
                    }
                    // Large diagrams (1000-1500px width or 700-1000px height)
                    else if (numWidth > 1000 || numHeight > 700) {
                        svg.style.transform = 'scale(0.65)';
                        svg.style.transformOrigin = 'center top';
                        svg.parentElement.style.marginBottom = '50px';
                    }
                    // Medium diagrams (700-1000px width or 500-700px height)
                    else if (numWidth > 700 || numHeight > 500) {
                        svg.style.transform = 'scale(0.75)';
                        svg.style.transformOrigin = 'center top';
                        svg.parentElement.style.marginBottom = '40px';
                    }
                    // Small-medium diagrams (500-700px width)
                    else if (numWidth > 500) {
                        svg.style.transform = 'scale(0.85)';
                        svg.style.transformOrigin = 'center top';
                        svg.parentElement.style.marginBottom = '30px';
                    }
                    // Small diagrams - keep at 95%
                    else {
                        svg.style.transform = 'scale(0.95)';
                        svg.style.transformOrigin = 'center top';
                        svg.parentElement.style.marginBottom = '20px';
                    }
                    
                    // Center align all diagrams
                    svg.style.display = 'block';
                    svg.style.margin = '0 auto';
                    svg.parentElement.style.textAlign = 'center';
                    svg.parentElement.style.pageBreakInside = 'avoid';
                    
                    // Ensure container doesn't overflow
                    svg.parentElement.style.overflow = 'visible';
                    svg.parentElement.style.width = '100%';
                });
            }
        """)
        
        # Additional wait after adjustments
        await page.wait_for_timeout(2000)
        
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
