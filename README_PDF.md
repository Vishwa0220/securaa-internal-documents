# PDF Conversion Tool

This script converts the `secura-customer-security-documentation.md` file to a professional PDF document with:
- Cover page with "Information Security Policies - Securaa" headline
- Professional styling and formatting
- Diagram placeholders (for mermaid diagrams)
- Page numbers and headers

## Requirements

Install the required Python packages:

```bash
pip install markdown weasyprint Pillow
```

## Usage

Run the conversion script:

```bash
python3 convert_to_pdf.py
```

This will generate `Information_Security_Policies_Securaa.pdf` in the root directory.

## Output

The generated PDF includes:
- Professional cover page with Securaa branding
- Full security documentation content
- Styled tables, code blocks, and lists
- Visual placeholders for diagrams
- Page numbers and document headers

## Notes

- Mermaid diagrams are represented as styled placeholders with code previews
- For full interactive diagrams, refer to the HTML version in the `docs/` folder
- The PDF is optimized for printing and professional distribution
