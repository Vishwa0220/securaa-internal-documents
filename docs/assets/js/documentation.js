// Zona Documentation JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the documentation features
    initNavigation();
    initScrollToTop();
    initCodeCopyButtons();
    initTableOfContents();
    initSearch();
});

// Navigation functionality
function initNavigation() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.documentation-nav a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPage) {
            link.classList.add('active');
        }
        
        // Add smooth scrolling for anchor links
        if (link.getAttribute('href').startsWith('#')) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        }
    });
}

// Scroll to top functionality
function initScrollToTop() {
    // Create scroll to top button
    const scrollButton = document.createElement('button');
    scrollButton.innerHTML = '↑';
    scrollButton.className = 'scroll-to-top';
    scrollButton.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: #3498db;
        color: white;
        border: none;
        font-size: 20px;
        cursor: pointer;
        opacity: 0;
        transition: opacity 0.3s ease;
        z-index: 1000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `;
    
    document.body.appendChild(scrollButton);
    
    // Show/hide scroll button based on scroll position
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollButton.style.opacity = '1';
        } else {
            scrollButton.style.opacity = '0';
        }
    });
    
    // Scroll to top when clicked
    scrollButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Add copy buttons to code blocks
function initCodeCopyButtons() {
    const codeBlocks = document.querySelectorAll('pre code');
    
    codeBlocks.forEach(codeBlock => {
        const pre = codeBlock.parentElement;
        
        // Create copy button
        const copyButton = document.createElement('button');
        copyButton.textContent = 'Copy';
        copyButton.className = 'copy-code-btn';
        copyButton.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            background: #2c3e50;
            color: white;
            border: 1px solid #34495e;
            border-radius: 3px;
            padding: 5px 10px;
            font-size: 12px;
            cursor: pointer;
            transition: background 0.3s ease;
        `;
        
        // Style the pre element
        pre.style.position = 'relative';
        
        // Add hover effect
        copyButton.addEventListener('mouseenter', function() {
            this.style.background = '#34495e';
        });
        
        copyButton.addEventListener('mouseleave', function() {
            this.style.background = '#2c3e50';
        });
        
        // Copy functionality
        copyButton.addEventListener('click', function() {
            const text = codeBlock.textContent;
            
            if (navigator.clipboard) {
                navigator.clipboard.writeText(text).then(() => {
                    showCopySuccess(copyButton);
                });
            } else {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                showCopySuccess(copyButton);
            }
        });
        
        pre.appendChild(copyButton);
    });
}

function showCopySuccess(button) {
    const originalText = button.textContent;
    button.textContent = 'Copied!';
    button.style.background = '#27ae60';
    
    setTimeout(() => {
        button.textContent = originalText;
        button.style.background = '#2c3e50';
    }, 2000);
}

// Generate table of contents
function initTableOfContents() {
    const headings = document.querySelectorAll('h1, h2, h3, h4');
    
    if (headings.length < 3) return; // Don't create TOC for short documents
    
    const tocContainer = document.createElement('div');
    tocContainer.className = 'table-of-contents';
    tocContainer.innerHTML = '<h3>Table of Contents</h3>';
    
    const tocList = document.createElement('ul');
    
    headings.forEach((heading, index) => {
        // Create ID if it doesn't exist
        if (!heading.id) {
            heading.id = 'heading-' + index;
        }
        
        const listItem = document.createElement('li');
        listItem.className = 'toc-' + heading.tagName.toLowerCase();
        
        const link = document.createElement('a');
        link.href = '#' + heading.id;
        link.textContent = heading.textContent;
        link.addEventListener('click', function(e) {
            e.preventDefault();
            heading.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        });
        
        listItem.appendChild(link);
        tocList.appendChild(listItem);
    });
    
    tocContainer.appendChild(tocList);
    
    // Style the TOC
    tocContainer.style.cssText = `
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 5px;
        padding: 1rem;
        margin: 2rem 0;
        position: sticky;
        top: 80px;
        z-index: 10;
    `;
    
    // Insert TOC after the first heading
    const firstHeading = headings[0];
    if (firstHeading && firstHeading.nextElementSibling) {
        firstHeading.parentNode.insertBefore(tocContainer, firstHeading.nextElementSibling);
    }
}

// Simple search functionality
function initSearch() {
    // Create search container
    const searchContainer = document.createElement('div');
    searchContainer.className = 'search-container';
    searchContainer.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1001;
    `;
    
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = 'Search documentation...';
    searchInput.className = 'search-input';
    searchInput.style.cssText = `
        padding: 8px 12px;
        border: 1px solid #ddd;
        border-radius: 20px;
        width: 200px;
        font-size: 14px;
        background: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    `;
    
    searchContainer.appendChild(searchInput);
    document.body.appendChild(searchContainer);
    
    // Search functionality
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            performSearch(this.value);
        }, 300);
    });
    
    // Clear search on escape
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            this.value = '';
            clearSearch();
        }
    });
}

function performSearch(query) {
    clearSearch();
    
    if (query.length < 3) return;
    
    const content = document.querySelector('.main-content');
    const walker = document.createTreeWalker(
        content,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );
    
    const regex = new RegExp(query, 'gi');
    let node;
    
    while (node = walker.nextNode()) {
        if (regex.test(node.textContent)) {
            highlightText(node, regex);
        }
    }
}

function highlightText(textNode, regex) {
    const parent = textNode.parentElement;
    if (parent.tagName === 'SCRIPT' || parent.tagName === 'STYLE') return;
    
    const highlightedText = textNode.textContent.replace(regex, '<mark class="search-highlight">$&</mark>');
    
    if (highlightedText !== textNode.textContent) {
        const wrapper = document.createElement('div');
        wrapper.innerHTML = highlightedText;
        
        while (wrapper.firstChild) {
            parent.insertBefore(wrapper.firstChild, textNode);
        }
        parent.removeChild(textNode);
    }
}

function clearSearch() {
    const highlights = document.querySelectorAll('.search-highlight');
    highlights.forEach(highlight => {
        const parent = highlight.parentElement;
        parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
        parent.normalize();
    });
}

// Add smooth scrolling for all anchor links
document.addEventListener('click', function(e) {
    if (e.target.tagName === 'A' && e.target.getAttribute('href').startsWith('#')) {
        e.preventDefault();
        const targetId = e.target.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
            targetElement.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
});

// Print functionality
function printPage() {
    window.print();
}

// Export page as PDF (if browser supports it)
function exportToPDF() {
    if (window.print) {
        // This will open the print dialog, user can save as PDF
        window.print();
    } else {
        alert('PDF export not supported in this browser');
    }
}