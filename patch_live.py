import re

with open("dotproduct_stack-live.html", "r") as f:
    text = f.read()

# Add CSS for timeline
css_add = """
        /* --- Timeline --- */
        .timeline-container {
            background: rgba(10,15,30,0.5);
            border: 1px solid rgba(148,163,184,0.08);
            border-radius: 12px;
            padding: 12px 20px 20px 20px;
            margin-bottom: 12px;
        }
        .timeline-container .side-title { margin-bottom: 8px; }
"""
text = text.replace("/* --- Info Panel --- */", css_add + "/* --- Info Panel --- */")

# Add HTML for timeline above Info Panel
html_add = """
    <div class="timeline-container">
        <div class="side-title" style="text-align: left;">Memory & Timeline</div>
        <svg id="timeline-svg" style="width:100%; height:80px; overflow:visible; cursor:pointer;" onclick="handleTimelineClick(event)"></svg>
    </div>
"""
text = text.replace('<div class="info-panel"', html_add + '\n    <div class="info-panel"')


# Add JS to draw timeline inside renderState()
js_update_timeline = """
    // --- Timeline Graph ---
    renderTimeline();
"""
text = text.replace('document.getElementById(\'step-display\').textContent = `${currentState + 1} / ${states.length}`;', js_update_timeline + '\n    document.getElementById(\'step-display\').textContent = `${currentState + 1} / ${states.length}`;')


# Add renderTimeline function itself
js_timeline_func = """
// ============================================================
// TIMELINE GRAPH
// ============================================================
function renderTimeline() {
    const svg = document.getElementById('timeline-svg');
    const rect = svg.getBoundingClientRect();
    const W = rect.width, H = rect.height;
    
    // Max items for dynamic scaling
    const maxItems = Math.max(16, ...states.map(s => Object.values(s.vars).filter(v => typeof v === 'number').length));
    
    let pathD = "";
    let sHTML = "";
    const N = states.length;
    const stepW = W / Math.max(1, N - 1);
    
    for (let i = 0; i < N; i++) {
        // Count items strictly on stack (numbers)
        const st = states[i];
        let items = Object.values(st.vars).filter(v => typeof v === 'number').length;
        
        // For visual continuity, elements at 'proc' are also considered 'active' memory,
        // but strictly speaking, Mattson size is stack size. Let's count 'proc' as memory footprint too
        let procItems = Object.values(st.vars).filter(v => v === 'proc').length;
        let totalMem = items + procItems; 

        // Normalized Y coordinate
        const hNorm = totalMem / maxItems;
        const cy = H - (hNorm * (H - 20)); // leave top padding
        const cx = i * stepW;
        
        if (i === 0) pathD += `M ${cx} ${cy} `;
        else pathD += `L ${cx} ${cy} `;
        
        // Hover hitbox / interactive column
        sHTML += `<rect x="${cx - stepW/2}" y="0" width="${stepW}" height="${H}" fill="transparent" style="cursor:pointer;" onmousedown="currentState=${i}; renderState();"/>`;
        
        // Data point circle
        const isActive = (i === currentState);
        const r = isActive ? 5 : 3;
        const fill = isActive ? '#00e5ff' : 'rgba(148,163,184,0.5)';
        const stroke = isActive ? 'rgba(0,229,255,0.4)' : 'none';
        const sw = isActive ? 4 : 0;
        
        sHTML += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" pointer-events="none" />`;
        
        // Highlight active step region
        if (isActive) {
            sHTML += `<rect x="${cx - stepW/2 + 2}" y="0" width="${stepW - 4}" height="${H}" fill="rgba(0,229,255,0.06)" rx="4" pointer-events="none"/>`;
            // Label memory
            sHTML += `<text x="${cx}" y="${cy - 12}" text-anchor="middle" fill="#00e5ff" font-family="JetBrains Mono" font-size="10" font-weight="700">${totalMem}</text>`;
        }
    }
    
    // Add filled area graph below line
    let areaPath = pathD + ` L ${W} ${H} L 0 ${H} Z`;
    
    const svgContent = `
        <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="rgba(148,163,184,0.15)"/>
            <stop offset="100%" stop-color="rgba(148,163,184,0.0)"/>
        </linearGradient>
        <path d="${areaPath}" fill="url(#areaGrad)" pointer-events="none" />
        <path d="${pathD}" fill="none" stroke="rgba(148,163,184,0.4)" stroke-width="2" pointer-events="none" />
        ${sHTML}
    `;
    svg.innerHTML = svgContent;
}

// Window resize handler already exists
"""
text = text.replace('function bounce()', js_timeline_func + '\nfunction bounce()')
text = text.replace('// BUILD SVG', js_timeline_func + '\n// ============================================================\n// BUILD SVG')

with open("dotproduct_stack-live.html", "w") as f:
    f.write(text)

