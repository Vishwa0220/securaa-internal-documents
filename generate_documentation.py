#!/usr/bin/env python3
"""
Securaa Documentation Generator
Generates HTML and PDF documentation from Markdown files with properly rendered Mermaid diagrams.
"""

import asyncio
import os
import re
import json
from pathlib import Path
from datetime import datetime
from string import Template
import markdown
from markdown.extensions import codehilite, fenced_code, tables, toc

# Configuration
DOCS_DIR = Path('docs')
PDF_DIR = DOCS_DIR / 'pdf'
ROOT_DIR = Path('.')

# Markdown files to process (order matters for index generation)
MD_FILES = [
    ('securaa-platform-high-level-design.md', 'Securaa Platform - High Level Design'),
    ('process-manager-high-level-design.md', 'Process Manager - High Level Design'),
    ('process-manager-low-level-design.md', 'Process Manager - Low Level Design'),
    ('securaa-playbook-high-level-design.md', 'Securaa Playbook Service - High Level Design'),
    ('securaa-playbook-low-level-design.md', 'Securaa Playbook Service - Low Level Design'),
    ('securaa-siem-high-level-design.md', 'Securaa SIEM Service - High Level Design'),
    ('securaa-siem-low-level-design.md', 'Securaa SIEM Service - Low Level Design'),
    ('securaa-user-high-level-design.md', 'Securaa User Service - High Level Design'),
    ('securaa-user-low-level-design.md', 'Securaa User Service - Low Level Design'),
    ('securaa-custom-services-high-level-design.md', 'Securaa Custom Services - High Level Design'),
    ('securaa-custom-services-low-level-design.md', 'Securaa Custom Services - Low Level Design'),
    ('securaa-custom-utils-high-level-design.md', 'Securaa Custom Utils - High Level Design'),
    ('securaa-custom-utils-low-level-design.md', 'Securaa Custom Utils - Low Level Design'),
    ('securaa-ris-high-level-design.md', 'Securaa RIS - High Level Design'),
    ('securaa-ris-low-level-design.md', 'Securaa RIS - Low Level Design'),
    ('securaa-ris-client-documentation.md', 'Securaa RIS Client Documentation'),
    ('securaa-ris-server-documentation.md', 'Securaa RIS Server Documentation'),
    ('sia-service-high-level-design.md', 'SIA Service - High Level Design'),
    ('sia-service-low-level-design.md', 'SIA Service - Low Level Design'),
    ('MONGODB_SHARDING_ARCHITECTURE.md', 'MongoDB Sharding Architecture'),
    ('securaa-make-system.md', 'Securaa Make System'),
    ('OPTIMIZATION_GUIDE.md', 'Optimization Guide'),
    ('secura-customer-security-documentation.md', 'Customer Security Documentation'),
    ('securaa-information-security-risk-assesment-process.md', 'Information Security Risk Assessment'),
]

# Enhanced CSS with better Mermaid diagram styling
CSS_STYLES = """
:root {
    --primary-color: #4f46e5;
    --primary-dark: #3730a3;
    --primary-light: #818cf8;
    --secondary-color: #06b6d4;
    --accent-color: #f59e0b;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --error-color: #ef4444;
    --text-primary: #1f2937;
    --text-secondary: #6b7280;
    --text-muted: #9ca3af;
    --bg-primary: #ffffff;
    --bg-secondary: #f9fafb;
    --bg-tertiary: #f3f4f6;
    --border-color: #e5e7eb;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
    font-size: 16px;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.7;
    color: var(--text-primary);
    background-color: var(--bg-secondary);
}

/* Header */
.main-header {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
    color: white;
    padding: 1rem 2rem;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: var(--shadow-lg);
}

.header-content {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-logo {
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -0.025em;
}

.header-logo span {
    color: var(--secondary-color);
}

/* Navigation */
.documentation-nav {
    background: var(--bg-primary);
    border-bottom: 1px solid var(--border-color);
    padding: 0.75rem 2rem;
    position: sticky;
    top: 60px;
    z-index: 999;
    box-shadow: var(--shadow-sm);
}

.nav-links {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    justify-content: center;
}

.nav-links a {
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 0.875rem;
    font-weight: 500;
    padding: 0.5rem 0.75rem;
    border-radius: 0.375rem;
    transition: all 0.2s ease;
}

.nav-links a:hover {
    color: var(--primary-color);
    background: var(--bg-tertiary);
}

/* Main Content */
.main-content {
    max-width: 1000px;
    margin: 2rem auto;
    padding: 2.5rem;
    background: var(--bg-primary);
    border-radius: 1rem;
    box-shadow: var(--shadow-md);
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary);
    font-weight: 700;
    line-height: 1.3;
    margin-top: 2rem;
    margin-bottom: 1rem;
}

h1 {
    font-size: 2.5rem;
    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    padding-bottom: 0.75rem;
    border-bottom: 3px solid var(--primary-color);
    margin-top: 0;
}

h2 {
    font-size: 1.875rem;
    color: var(--primary-dark);
    border-bottom: 2px solid var(--border-color);
    padding-bottom: 0.5rem;
}

h3 {
    font-size: 1.5rem;
    color: var(--text-primary);
}

h4 {
    font-size: 1.25rem;
    color: var(--text-secondary);
}

h5 {
    font-size: 1.125rem;
}

h6 {
    font-size: 1rem;
    color: var(--text-muted);
}

p {
    margin-bottom: 1rem;
    color: var(--text-primary);
}

/* Links */
a {
    color: var(--primary-color);
    text-decoration: none;
    transition: color 0.2s ease;
}

a:hover {
    color: var(--primary-dark);
    text-decoration: underline;
}

/* Lists */
ul, ol {
    margin-bottom: 1rem;
    padding-left: 1.5rem;
}

li {
    margin-bottom: 0.5rem;
}

li > ul, li > ol {
    margin-top: 0.5rem;
    margin-bottom: 0;
}

/* Code Blocks */
pre {
    background: #1e1e1e;
    color: #d4d4d4;
    padding: 1.25rem;
    border-radius: 0.5rem;
    overflow-x: auto;
    margin: 1.5rem 0;
    font-size: 0.875rem;
    line-height: 1.6;
    box-shadow: var(--shadow-md);
}

code {
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 0.875em;
}

:not(pre) > code {
    background: var(--bg-tertiary);
    color: var(--primary-dark);
    padding: 0.2rem 0.4rem;
    border-radius: 0.25rem;
    font-size: 0.875em;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
    font-size: 0.9rem;
    box-shadow: var(--shadow-sm);
    border-radius: 0.5rem;
    overflow: hidden;
}

thead {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
    color: white;
}

th {
    padding: 1rem;
    text-align: left;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
}

td {
    padding: 0.875rem 1rem;
    border-bottom: 1px solid var(--border-color);
}

tr:nth-child(even) {
    background: var(--bg-secondary);
}

tr:hover {
    background: var(--bg-tertiary);
}

/* Blockquotes */
blockquote {
    border-left: 4px solid var(--primary-color);
    padding: 1rem 1.5rem;
    margin: 1.5rem 0;
    background: var(--bg-secondary);
    border-radius: 0 0.5rem 0.5rem 0;
    font-style: italic;
    color: var(--text-secondary);
}

blockquote p:last-child {
    margin-bottom: 0;
}

/* Mermaid Diagrams - Enhanced Styling */
.mermaid {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 2rem 0;
    padding: 1.5rem;
    background: linear-gradient(135deg, #fafbfc 0%, #f0f4f8 100%);
    border-radius: 0.75rem;
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow-sm);
    overflow-x: auto;
    overflow-y: visible;
    min-height: 200px;
}

.mermaid svg {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 0 auto;
}

/* Ensure diagrams scale properly */
.mermaid[data-processed="true"] {
    min-height: auto;
}

/* Diagram container for better control */
.diagram-container {
    width: 100%;
    overflow-x: auto;
    padding: 1rem 0;
}

/* HR Styling */
hr {
    border: none;
    border-top: 2px solid var(--border-color);
    margin: 2.5rem 0;
}

/* Table of Contents */
.toc {
    background: var(--bg-secondary);
    padding: 1.5rem;
    border-radius: 0.5rem;
    margin-bottom: 2rem;
    border: 1px solid var(--border-color);
}

.toc-title {
    font-weight: 700;
    color: var(--primary-color);
    margin-bottom: 1rem;
    font-size: 1.125rem;
}

.toc ul {
    list-style: none;
    padding-left: 0;
}

.toc li {
    margin-bottom: 0.5rem;
}

.toc a {
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.toc a:hover {
    color: var(--primary-color);
}

/* Document Info Box */
.doc-info {
    background: linear-gradient(135deg, var(--bg-secondary), var(--bg-tertiary));
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    padding: 1rem 1.5rem;
    margin-bottom: 2rem;
    font-size: 0.875rem;
}

.doc-info strong {
    color: var(--primary-color);
}

/* Footer */
.footer {
    text-align: center;
    padding: 2rem;
    background: var(--bg-tertiary);
    color: var(--text-muted);
    font-size: 0.875rem;
    margin-top: 2rem;
}

/* Scrollbar Styling */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-tertiary);
}

::-webkit-scrollbar-thumb {
    background: var(--text-muted);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text-secondary);
}

/* Print Styles */
@media print {
    .main-header, .documentation-nav, .footer {
        display: none !important;
    }

    .main-content {
        max-width: none;
        margin: 0;
        padding: 20px;
        box-shadow: none;
        border-radius: 0;
    }

    body {
        background: white;
        font-size: 11pt;
    }

    h1 {
        font-size: 24pt;
        -webkit-text-fill-color: var(--primary-dark);
        page-break-after: avoid;
    }

    h2, h3, h4 {
        page-break-after: avoid;
    }

    pre {
        background: #f5f5f5 !important;
        color: #333 !important;
        border: 1px solid #ddd;
        page-break-inside: avoid;
        font-size: 9pt;
    }

    table {
        page-break-inside: avoid;
    }

    .mermaid {
        page-break-inside: avoid;
        background: white !important;
        border: 1px solid #ddd;
        max-width: 100% !important;
    }

    .mermaid svg {
        max-width: 100% !important;
        max-height: 700px !important;
    }

    a {
        color: var(--primary-dark) !important;
        text-decoration: none !important;
    }
}

/* Responsive Design */
@media (max-width: 768px) {
    .main-content {
        margin: 1rem;
        padding: 1.5rem;
        border-radius: 0.5rem;
    }

    h1 {
        font-size: 1.75rem;
    }

    h2 {
        font-size: 1.5rem;
    }

    .nav-links {
        gap: 0.75rem;
    }

    .nav-links a {
        font-size: 0.75rem;
        padding: 0.375rem 0.5rem;
    }

    pre {
        font-size: 0.8rem;
        padding: 1rem;
    }

    table {
        font-size: 0.8rem;
    }

    th, td {
        padding: 0.5rem;
    }
}

/* Animation for smooth transitions */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.main-content {
    animation: fadeIn 0.3s ease-out;
}

/* Index-specific styles */
.hero {
    text-align: center;
    padding: 3rem 0;
    background: linear-gradient(135deg, var(--bg-secondary), var(--bg-tertiary));
    border-radius: 1rem;
    margin-bottom: 3rem;
}

.hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
    border: none;
    padding: 0;
}

.hero p {
    font-size: 1.25rem;
    color: var(--text-secondary);
    max-width: 600px;
    margin: 0 auto;
}

.doc-sections {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-top: 2rem;
}

.doc-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 0.75rem;
    padding: 1.5rem;
    transition: all 0.3s ease;
    box-shadow: var(--shadow-sm);
}

.doc-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
    border-color: var(--primary-light);
}

.doc-card h3 {
    color: var(--primary-color);
    font-size: 1.25rem;
    margin-top: 0;
    margin-bottom: 0.75rem;
}

.doc-card p {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

.doc-card .links {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}

.doc-card .links a {
    font-size: 0.875rem;
    padding: 0.5rem 1rem;
    background: var(--bg-secondary);
    border-radius: 0.375rem;
    transition: all 0.2s ease;
}

.doc-card .links a:hover {
    background: var(--primary-color);
    color: white;
    text-decoration: none;
}

.section-title {
    font-size: 1.75rem;
    color: var(--primary-dark);
    margin-top: 3rem;
    margin-bottom: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--border-color);
}
"""

# HTML Template using $placeholders
HTML_TEMPLATE = Template("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Securaa Platform Documentation - $title">
    <title>$title - Securaa Documentation</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
$css
    </style>
</head>
<body>
    <header class="main-header">
        <div class="header-content">
            <div class="header-logo">Securaa<span>Docs</span></div>
            <div class="header-meta">
                <span>Generated: $date</span>
            </div>
        </div>
    </header>

    <nav class="documentation-nav">
        <div class="nav-links">
            <a href="index.html">Home</a>
            <a href="securaa-platform-high-level-design.html">Platform</a>
            <a href="securaa-playbook-high-level-design.html">Playbook</a>
            <a href="securaa-siem-high-level-design.html">SIEM</a>
            <a href="securaa-user-high-level-design.html">User Service</a>
            <a href="securaa-custom-services-high-level-design.html">Custom Services</a>
            <a href="sia-service-high-level-design.html">SIA Service</a>
            <a href="securaa-ris-high-level-design.html">RIS</a>
        </div>
    </nav>

    <main class="main-content">
        $content
    </main>

    <footer class="footer">
        <p>&copy; $year Securaa Security Platform. All rights reserved.</p>
        <p>Documentation generated on $date</p>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({
            startOnLoad: true,
            theme: 'base',
            themeVariables: {
                primaryColor: '#4f46e5',
                primaryTextColor: '#1f2937',
                primaryBorderColor: '#818cf8',
                lineColor: '#6b7280',
                secondaryColor: '#f3f4f6',
                tertiaryColor: '#e5e7eb',
                background: '#ffffff',
                mainBkg: '#f9fafb',
                secondBkg: '#f3f4f6',
                border1: '#e5e7eb',
                border2: '#d1d5db',
                fontFamily: 'Inter, sans-serif',
                fontSize: '14px',
                nodeBorder: '#4f46e5',
                clusterBkg: '#f0f4f8',
                clusterBorder: '#818cf8',
                edgeLabelBackground: '#ffffff'
            },
            flowchart: {
                htmlLabels: true,
                useMaxWidth: true,
                curve: 'basis',
                padding: 15,
                nodeSpacing: 50,
                rankSpacing: 50
            },
            sequence: {
                actorMargin: 50,
                width: 150,
                height: 65,
                boxMargin: 10,
                boxTextMargin: 5,
                noteMargin: 10,
                messageMargin: 35,
                mirrorActors: true,
                useMaxWidth: true
            },
            er: {
                useMaxWidth: true,
                entityPadding: 15,
                fontSize: 12
            },
            class: {
                useMaxWidth: true,
                padding: 10
            },
            gantt: {
                useMaxWidth: true,
                barHeight: 20,
                barGap: 4,
                topPadding: 50,
                leftPadding: 75
            },
            pie: {
                useMaxWidth: true,
                textPosition: 0.5
            },
            mindmap: {
                useMaxWidth: true,
                padding: 10
            },
            securityLevel: 'loose',
            logLevel: 'error'
        });

        // Re-render mermaid diagrams after page load for better sizing
        window.addEventListener('load', function() {
            setTimeout(function() {
                document.querySelectorAll('.mermaid').forEach(function(el) {
                    if (el.getAttribute('data-processed') !== 'true') {
                        mermaid.init(undefined, el);
                    }
                });
            }, 100);
        });
    </script>
</body>
</html>
""")

# Index Page Template
INDEX_TEMPLATE = Template("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Securaa Platform Documentation Portal">
    <title>Securaa Platform Documentation</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
$css
    </style>
</head>
<body>
    <header class="main-header">
        <div class="header-content">
            <div class="header-logo">Securaa<span>Docs</span></div>
            <div class="header-meta">
                <span>Documentation Portal</span>
            </div>
        </div>
    </header>

    <main class="main-content">
        <div class="hero">
            <h1>Securaa Platform Documentation</h1>
            <p>Comprehensive technical documentation for the Securaa Security Platform, including architecture designs, API references, and implementation guides.</p>
        </div>

        <h2 class="section-title">Core Services</h2>
        <div class="doc-sections">
            <div class="doc-card">
                <h3>Platform Overview</h3>
                <p>High-level architecture and deployment topologies for the Securaa Platform.</p>
                <div class="links">
                    <a href="securaa-platform-high-level-design.html">HLD</a>
                    <a href="pdf/securaa-platform-high-level-design.pdf">PDF</a>
                </div>
            </div>

            <div class="doc-card">
                <h3>Playbook Service</h3>
                <p>SOAR automation engine for security orchestration and response workflows.</p>
                <div class="links">
                    <a href="securaa-playbook-high-level-design.html">HLD</a>
                    <a href="securaa-playbook-low-level-design.html">LLD</a>
                    <a href="pdf/securaa-playbook-high-level-design.pdf">PDF</a>
                </div>
            </div>

            <div class="doc-card">
                <h3>SIEM Service</h3>
                <p>Security Information and Event Management for incident handling and analytics.</p>
                <div class="links">
                    <a href="securaa-siem-high-level-design.html">HLD</a>
                    <a href="securaa-siem-low-level-design.html">LLD</a>
                    <a href="pdf/securaa-siem-high-level-design.pdf">PDF</a>
                </div>
            </div>

            <div class="doc-card">
                <h3>User Service</h3>
                <p>Identity and access management with multi-tenant support.</p>
                <div class="links">
                    <a href="securaa-user-high-level-design.html">HLD</a>
                    <a href="securaa-user-low-level-design.html">LLD</a>
                    <a href="pdf/securaa-user-high-level-design.pdf">PDF</a>
                </div>
            </div>

            <div class="doc-card">
                <h3>Custom Services</h3>
                <p>Custom application and integration management platform.</p>
                <div class="links">
                    <a href="securaa-custom-services-high-level-design.html">HLD</a>
                    <a href="securaa-custom-services-low-level-design.html">LLD</a>
                    <a href="pdf/securaa-custom-services-high-level-design.pdf">PDF</a>
                </div>
            </div>

            <div class="doc-card">
                <h3>SIA Service</h3>
                <p>AI-powered SOC automation with LLM integration for intelligent analysis.</p>
                <div class="links">
                    <a href="sia-service-high-level-design.html">HLD</a>
                    <a href="sia-service-low-level-design.html">LLD</a>
                    <a href="pdf/sia-service-high-level-design.pdf">PDF</a>
                </div>
            </div>
        </div>

        <h2 class="section-title">Infrastructure & Operations</h2>
        <div class="doc-sections">
            <div class="doc-card">
                <h3>Process Manager</h3>
                <p>Microservices orchestration and lifecycle management.</p>
                <div class="links">
                    <a href="process-manager-high-level-design.html">HLD</a>
                    <a href="process-manager-low-level-design.html">LLD</a>
                    <a href="pdf/process-manager-high-level-design.pdf">PDF</a>
                </div>
            </div>

            <div class="doc-card">
                <h3>RIS (Remote Integration Service)</h3>
                <p>Remote integration and connectivity service documentation.</p>
                <div class="links">
                    <a href="securaa-ris-high-level-design.html">HLD</a>
                    <a href="securaa-ris-low-level-design.html">LLD</a>
                    <a href="securaa-ris-client-documentation.html">Client</a>
                    <a href="securaa-ris-server-documentation.html">Server</a>
                </div>
            </div>

            <div class="doc-card">
                <h3>Custom Utils</h3>
                <p>Utility services and helper functions for the platform.</p>
                <div class="links">
                    <a href="securaa-custom-utils-high-level-design.html">HLD</a>
                    <a href="securaa-custom-utils-low-level-design.html">LLD</a>
                    <a href="pdf/securaa-custom-utils-high-level-design.pdf">PDF</a>
                </div>
            </div>

            <div class="doc-card">
                <h3>Make System</h3>
                <p>Build and deployment automation system.</p>
                <div class="links">
                    <a href="securaa-make-system.html">Documentation</a>
                    <a href="pdf/securaa-make-system.pdf">PDF</a>
                </div>
            </div>
        </div>

        <h2 class="section-title">Guides & References</h2>
        <div class="doc-sections">
            <div class="doc-card">
                <h3>Optimization Guide</h3>
                <p>Performance optimization and best practices for the platform.</p>
                <div class="links">
                    <a href="OPTIMIZATION_GUIDE.html">Guide</a>
                    <a href="pdf/OPTIMIZATION_GUIDE.pdf">PDF</a>
                </div>
            </div>

            <div class="doc-card">
                <h3>Security Documentation</h3>
                <p>Customer security documentation and compliance information.</p>
                <div class="links">
                    <a href="secura-customer-security-documentation.html">Security</a>
                    <a href="securaa-information-security-risk-assesment-process.html">Risk Assessment</a>
                </div>
            </div>
        </div>
    </main>

    <footer class="footer">
        <p>&copy; $year Securaa Security Platform. All rights reserved.</p>
        <p>Documentation generated on $date</p>
    </footer>
</body>
</html>
""")


def process_mermaid_blocks(content: str) -> str:
    """
    Convert markdown mermaid code blocks to HTML div elements.
    """
    # Pattern to match mermaid code blocks
    mermaid_pattern = r'```mermaid\s*\n([\s\S]*?)```'

    def replace_mermaid(match):
        diagram_content = match.group(1).strip()
        # Wrap in a div with mermaid class
        return f'<div class="mermaid">\n{diagram_content}\n</div>'

    return re.sub(mermaid_pattern, replace_mermaid, content)


def convert_md_to_html(md_content: str, title: str) -> str:
    """
    Convert markdown content to HTML with proper formatting.
    """
    # Process mermaid blocks first (before markdown processing)
    content = process_mermaid_blocks(md_content)

    # Configure markdown extensions
    md = markdown.Markdown(extensions=[
        'tables',
        'fenced_code',
        'codehilite',
        'toc',
        'sane_lists',
    ], extension_configs={
        'codehilite': {
            'css_class': 'highlight',
            'guess_lang': True,
        },
        'toc': {
            'permalink': False,
            'toc_depth': 4,
        }
    })

    # Convert markdown to HTML
    html_content = md.convert(content)

    # Generate full HTML document
    now = datetime.now()
    full_html = HTML_TEMPLATE.substitute(
        title=title,
        css=CSS_STYLES,
        content=html_content,
        date=now.strftime('%B %d, %Y'),
        year=now.year
    )

    return full_html


def generate_index_page() -> str:
    """
    Generate the index HTML page.
    """
    now = datetime.now()
    return INDEX_TEMPLATE.substitute(
        css=CSS_STYLES,
        date=now.strftime('%B %d, %Y'),
        year=now.year
    )


def main():
    """
    Main function to generate all HTML documentation.
    """
    print("\n=== Securaa Documentation Generator ===\n")

    # Ensure docs directory exists
    DOCS_DIR.mkdir(exist_ok=True)
    PDF_DIR.mkdir(exist_ok=True)

    # Generate index page
    print("Generating index.html...")
    index_html = generate_index_page()
    index_path = DOCS_DIR / 'index.html'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
    print(f"  Created: {index_path}")

    # Process each markdown file
    success_count = 0
    error_count = 0

    for md_file, title in MD_FILES:
        md_path = ROOT_DIR / md_file

        if not md_path.exists():
            print(f"  Skipped: {md_file} (not found)")
            error_count += 1
            continue

        try:
            # Read markdown content
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # Convert to HTML
            html_content = convert_md_to_html(md_content, title)

            # Generate output filename
            html_filename = md_file.replace('.md', '.html')
            html_path = DOCS_DIR / html_filename

            # Write HTML file
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f"  Created: {html_filename}")
            success_count += 1

        except Exception as e:
            print(f"  Error processing {md_file}: {str(e)}")
            error_count += 1

    print(f"\n=== Generation Complete ===")
    print(f"  Successful: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Output directory: {DOCS_DIR.absolute()}")


if __name__ == '__main__':
    main()
