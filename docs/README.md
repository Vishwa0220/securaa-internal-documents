# Securaa Platform Documentation

This folder contains the comprehensive HTML documentation for the Securaa Platform, automatically generated from the markdown files in the repository.

## Contents

- `index.html` - Main documentation portal and entry point
- `securaa-playbook-high-level-design.html` - Securaa Playbook Service High Level Design
- `securaa-playbook-low-level-design.html` - Securaa Playbook Service Low Level Design
- `process-manager-high-level-design.html` - Process Manager High Level Design
- `process-manager-low-level-design.html` - Process Manager Low Level Design
- `optimization-guide.html` - Performance Optimization Guide
- `securaa-siem-high-level-design.html` - Securaa SIEM Service High Level Design
- `securaa-siem-low-level-design.html` - Securaa SIEM Service Low Level Design
- `securaa-platform-high-level-design.html` - Securaa Platform High Level Design
- `securaa-user-high-level-design.html` - Securaa User Service High Level Design
- `securaa-user-low-level-design.html` - Securaa User Service Low Level Design
- `securaa-custom-services-high-level-design.html` - Securaa Custom Services High Level Design
- `securaa-custom-services-low-level-design.html` - Securaa Custom Services Low Level Design
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

1. **Securaa Playbook Service** - Core SOAR functionality
   - High Level Design (Architecture, APIs, Security)
   - Low Level Design (Implementation details, Database schema)

2. **Process Manager** - Microservices orchestration and lifecycle management
   - High Level Design (System architecture, orchestration, integrations)
   - Low Level Design (Component/class diagrams, database, API design)

3. **Securaa SIEM Service** - Security information and event management
   - High Level Design (System architecture, Integrations)
   - Low Level Design (Implementation details, Component design)

4. **Securaa Platform** - Infrastructure and deployment
   - High Level Design (Deployment topologies, Build system)

5. **Securaa User Service** - Identity and access management
   - High Level Design (Authentication, Authorization, Multi-tenancy)
   - Low Level Design (Implementation details, Database design)

6. **Securaa Custom Services** - Custom security applications and workflows
   - High Level Design (Architecture, Integration patterns)
   - Low Level Design (Implementation details, API specifications)

### Cross-References

The documentation includes intelligent cross-referencing between related sections. Links are preserved from the original markdown files and updated to work within the HTML structure.

## Technical Details

- **Generated From**: Markdown files in the repository root
- **Converter**: Custom Python script with markdown-to-HTML conversion
- **Styling**: Professional CSS with Securaa brand colors
- **JavaScript**: Enhanced functionality for search, navigation, and UX
- **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)

## Maintenance

To update the documentation:

1. Modify the source markdown files in the repository root
2. Re-run the conversion script to regenerate HTML files
3. The documentation structure and styling will be preserved

The documentation is designed to be self-contained and can be easily shared, hosted, or distributed as needed.