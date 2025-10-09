#!/usr/bin/env python3
"""
Convert secura-customer-security-documentation.md to PDF with cover page
"""

import re
import markdown
from weasyprint import HTML, CSS
from pathlib import Path

def create_cover_page_styles():
    """Create CSS styles for the cover page"""
    return """
            @page:first {
                size: A4;
                margin: 0;
            }
            .cover-page {
                height: 297mm;
                width: 210mm;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                background: linear-gradient(135deg, #0066CC 0%, #004494 100%);
                color: white;
                text-align: center;
                padding: 40px;
                box-sizing: border-box;
                page-break-after: always;
            }
            .cover-title {
                font-size: 48px;
                font-weight: bold;
                margin-bottom: 20px;
                text-transform: uppercase;
                letter-spacing: 2px;
            }
            .cover-subtitle {
                font-size: 32px;
                margin-bottom: 40px;
            }
            .cover-logo {
                font-size: 64px;
                font-weight: bold;
                margin-top: 60px;
                padding: 20px 40px;
                border: 4px solid white;
                border-radius: 10px;
            }
            .cover-date {
                font-size: 18px;
                margin-top: auto;
                opacity: 0.9;
            }
    """

def create_cover_page_content():
    """Create HTML content for the cover page"""
    return """
        <div class="cover-page">
            <div class="cover-logo">SECURAA</div>
            <div class="cover-title">Information Security Policies</div>
            <div class="cover-subtitle">Comprehensive Security Framework</div>
            <div class="cover-date">© 2025 Securaa Platform. All rights reserved.</div>
        </div>
    """

def preprocess_markdown(content):
    """Preprocess markdown content to handle mermaid diagrams"""
    # Replace mermaid code blocks with styled placeholders
    diagram_count = [0]  # Use list to make it mutable in nested function
    
    def replace_mermaid(match):
        diagram_count[0] += 1
        mermaid_content = match.group(1)
        
        # Extract the diagram type from the first line
        first_line = mermaid_content.strip().split('\n')[0].strip()
        
        # Determine diagram type
        if first_line.startswith('graph'):
            diagram_type = "Flow Diagram"
        elif first_line.startswith('sequenceDiagram'):
            diagram_type = "Sequence Diagram"
        elif first_line.startswith('erDiagram'):
            diagram_type = "Entity Relationship Diagram"
        elif first_line.startswith('classDiagram'):
            diagram_type = "Class Diagram"
        elif first_line.startswith('pie'):
            diagram_type = "Pie Chart"
        else:
            diagram_type = "Diagram"
        
        # Create HTML representation with the actual mermaid code
        preview_lines = '\n'.join(['    ' + line for line in mermaid_content.strip().split('\n')[:10]])
        if len(mermaid_content.strip().split('\n')) > 10:
            preview_lines += '\n    ...'
        
        html_placeholder = f'''
<div style="background: #f0f7ff; border: 2px solid #0066CC; border-radius: 8px; padding: 15px; margin: 15px 0; page-break-inside: avoid;">
    <h4 style="color: #0066CC; margin-top: 0;">📊 {diagram_type} #{diagram_count[0]}</h4>
    <p style="font-style: italic; color: #666; margin: 5px 0;">Architecture visualization - refer to interactive HTML version for full diagram</p>
    <pre style="background: #fff; padding: 10px; border-left: 3px solid #0066CC; margin: 10px 0; font-size: 8pt; overflow: hidden;">
{preview_lines}
    </pre>
</div>
'''
        return html_placeholder
    
    content = re.sub(r'```mermaid\n(.*?)```', replace_mermaid, content, flags=re.DOTALL)
    
    # Handle image placeholders - create visual boxes
    def replace_image(match):
        alt_text = match.group(1)
        return f'<div style="background: #e8f4f8; border: 2px dashed #0066CC; padding: 20px; text-align: center; margin: 10px 0; border-radius: 5px;"><strong>🖼️ {alt_text}</strong></div>'
    
    content = re.sub(
        r'!\[([^\]]*)\]\(https://via\.placeholder\.com/[^\)]+\)',
        replace_image,
        content
    )
    
    return content

def create_main_document_html(markdown_content):
    """Convert markdown to HTML with styling"""
    
    # Preprocess the markdown
    markdown_content = preprocess_markdown(markdown_content)
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=['extra', 'tables', 'fenced_code', 'toc'])
    html_content = md.convert(markdown_content)
    
    # Get cover page styles
    cover_styles = create_cover_page_styles()
    
    # Wrap in a full HTML document with styling
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            {cover_styles}
            
            @page {{
                size: A4;
                margin: 20mm 15mm;
                @top-center {{
                    content: "Information Security Policies - Securaa";
                    font-size: 10pt;
                    color: #666;
                }}
                @bottom-center {{
                    content: counter(page);
                    font-size: 10pt;
                }}
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                font-size: 11pt;
            }}
            
            h1 {{
                color: #0066CC;
                font-size: 24pt;
                margin-top: 20px;
                margin-bottom: 15px;
                page-break-after: avoid;
            }}
            
            h2 {{
                color: #0066CC;
                font-size: 18pt;
                margin-top: 18px;
                margin-bottom: 12px;
                page-break-after: avoid;
            }}
            
            h3 {{
                color: #004494;
                font-size: 14pt;
                margin-top: 15px;
                margin-bottom: 10px;
                page-break-after: avoid;
            }}
            
            h4 {{
                color: #004494;
                font-size: 12pt;
                margin-top: 12px;
                margin-bottom: 8px;
            }}
            
            p {{
                margin-bottom: 10px;
                text-align: justify;
            }}
            
            ul, ol {{
                margin-left: 20px;
                margin-bottom: 10px;
            }}
            
            li {{
                margin-bottom: 5px;
            }}
            
            code {{
                background-color: #f4f4f4;
                padding: 2px 5px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
            }}
            
            pre {{
                background-color: #f4f4f4;
                padding: 10px;
                border-radius: 5px;
                border-left: 4px solid #0066CC;
                overflow-x: auto;
                font-size: 9pt;
                page-break-inside: avoid;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 15px;
                page-break-inside: avoid;
            }}
            
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            
            th {{
                background-color: #0066CC;
                color: white;
                font-weight: bold;
            }}
            
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            
            blockquote {{
                border-left: 4px solid #0066CC;
                padding-left: 15px;
                margin-left: 0;
                color: #555;
                font-style: italic;
            }}
            
            hr {{
                border: none;
                border-top: 2px solid #0066CC;
                margin: 20px 0;
            }}
            
            a {{
                color: #0066CC;
                text-decoration: none;
            }}
            
            a:hover {{
                text-decoration: underline;
            }}
            
            .page-break {{
                page-break-before: always;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    return full_html

def main():
    # Read the markdown file
    md_file = Path('/home/runner/work/securaa-internal-documents/securaa-internal-documents/secura-customer-security-documentation.md')
    
    with open(md_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    print("Creating cover page...")
    cover_content = create_cover_page_content()
    
    print("Converting markdown to HTML...")
    main_html = create_main_document_html(markdown_content)
    
    # Insert cover content at the beginning of the body
    print("Combining content...")
    combined_html = main_html.replace('<body>', '<body>' + cover_content)
    
    print("Generating PDF...")
    output_file = Path('/home/runner/work/securaa-internal-documents/securaa-internal-documents/Information_Security_Policies_Securaa.pdf')
    
    # Generate PDF
    HTML(string=combined_html).write_pdf(output_file)
    
    print(f"PDF generated successfully: {output_file}")
    print(f"File size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")

if __name__ == '__main__':
    main()
