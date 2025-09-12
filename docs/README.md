# Zona Platform Documentation

This folder contains the comprehensive HTML documentation for the Zona Platform, automatically generated from the markdown files in the repository.

## Contents

- `index.html` - Main documentation portal and entry point
- `zona-playbook-hld.html` - Zona Playbook Service High-Level Design
- `zona-playbook-lld.html` - Zona Playbook Service Low-Level Design  
- `optimization-guide.html` - Performance Optimization Guide
- `zona-siem-hld.html` - Zona SIEM Service High-Level Design
- `securaa-hld.html` - Securaa Platform High-Level Design
- `assets/` - CSS, JavaScript, and other supporting files

## How to Use

### Local Viewing
1. Open `index.html` in any modern web browser
2. Navigate through the documentation using the top navigation menu
3. Use the search functionality to find specific information
4. Print or export any page as PDF using the browser's print function

### Web Server Deployment
To serve this documentation on a web server:

```bash
# Using Python's built-in server (for testing)
cd docs
python3 -m http.server 8080

# Using Node.js http-server
npx http-server docs -p 8080

# Using nginx or Apache
# Copy the docs folder to your web server's document root
```

### Features

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Search Functionality**: Real-time search across all documentation
- **Table of Contents**: Auto-generated TOC for easy navigation
- **Code Copy Buttons**: One-click copying of code blocks
- **Smooth Scrolling**: Enhanced navigation experience
- **Print Optimization**: Clean formatting for printing/PDF export

### Navigation

The documentation is organized into logical sections:

1. **Zona Playbook Service** - Core SOAR functionality
   - High-Level Design (Architecture, APIs, Security)
   - Low-Level Design (Implementation details, Database schema)
   - Optimization Guide (Performance tuning)

2. **Zona SIEM Service** - Security information and event management
   - High-Level Design (System architecture, Integrations)

3. **Securaa Platform** - Infrastructure and deployment
   - High-Level Design (Deployment topologies, Build system)

### Cross-References

The documentation includes intelligent cross-referencing between related sections. Links are preserved from the original markdown files and updated to work within the HTML structure.

## Technical Details

- **Generated From**: Markdown files in the repository root
- **Converter**: Custom Python script with markdown-to-HTML conversion
- **Styling**: Professional CSS with Zona brand colors
- **JavaScript**: Enhanced functionality for search, navigation, and UX
- **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)

## Maintenance

To update the documentation:

1. Modify the source markdown files in the repository root
2. Re-run the conversion script to regenerate HTML files
3. The documentation structure and styling will be preserved

The documentation is designed to be self-contained and can be easily shared, hosted, or distributed as needed.