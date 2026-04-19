import os, re

files = [
    "dotproduct_stack-live-linear.html",
    "dotproduct_stack-mattson-linear.html"
]

geometry_replacement = """// ============================================================
// GEOMETRY — Linear horizontal layout
// ============================================================
const CELL = 52;

// Processor screen coords
let PROC_SX, PROC_SY;

function isqrtCeil(x) {
    if (x <= 0) return 0;
    return Math.floor(Math.sqrt(x - 1)) + 1;
}

function depthScreen(d) {
    if (d === 'proc') return [PROC_SX, PROC_SY];
    // Linear horizontal: processor on the left, stack grows to the right
    return [PROC_SX + d * CELL, PROC_SY];
}
"""

buildsvg_replacement = """// ============================================================
// BUILD SVG
// ============================================================
function buildSVG() {
    const svg = document.getElementById('grid-svg');
    const rect = document.getElementById('viz-container').getBoundingClientRect();
    const W = rect.width, H = rect.height;
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);

    PROC_SX = 50;
    PROC_SY = H / 2 - 20;

    let s = '';

    // Defs
    s += `<defs>
        <marker id="arr" markerWidth="7" markerHeight="5" refX="6" refY="2.5" orient="auto">
            <polygon points="0 0, 7 2.5, 0 5" fill="rgba(148,163,184,0.4)"/>
        </marker>
        <marker id="arr-red" markerWidth="7" markerHeight="5" refX="6" refY="2.5" orient="auto">
            <polygon points="0 0, 7 2.5, 0 5" fill="rgba(251,113,133,0.8)"/>
        </marker>
    </defs>`;

    // Cost Tier Bands
    const tiers = [
        { c: 1, start: 1, end: 1, color: 'rgba(139,92,246,0.2)' },
        { c: 2, start: 2, end: 4, color: 'rgba(236,72,153,0.15)' },
        { c: 3, start: 5, end: 9, color: 'rgba(251,191,36,0.12)' },
        { c: 4, start: 10, end: 16, color: 'rgba(163,230,53,0.1)' },
    ];

    tiers.forEach(t => {
        if (t.start > NUM_SLOTS) return;
        const e = Math.min(t.end, NUM_SLOTS);
        const [x1] = depthScreen(t.start);
        const [x2] = depthScreen(e);
        const width = (x2 - x1) + CELL;
        const startX = x1 - CELL/2;
        
        s += `<rect x="${startX}" y="${PROC_SY - 35}" width="${width}" height="70" rx="12" fill="${t.color}" stroke="${t.color}" stroke-width="2"/>`;
        s += `<text x="${startX + width/2}" y="${PROC_SY - 42}" text-anchor="middle" fill="${t.color.replace(/\\.[0-9]+\\)/, '0.8)')}" font-family="JetBrains Mono" font-size="10" font-weight="700">Cost = ${t.c} (${t.end - t.start + 1} slots)</text>`;
    });

    // Processor Box
    s += `<g>
        <rect x="${PROC_SX - 20}" y="${PROC_SY - 20}" width="40" height="40" rx="8"
              fill="rgba(20,10,40,0.85)" stroke="#e879a0" stroke-width="2.5"/>
        <text x="${PROC_SX}" y="${PROC_SY + 5}" text-anchor="middle" fill="white"
              font-family="JetBrains Mono" font-weight="700" font-size="13">PE</text>
    </g>`;

    // Depth slot circles with labels
    const slotColor = d => {
        const r = isqrtCeil(d);
        if (r === 1) return '#8b5cf6';
        if (r === 2) return '#ec4899';
        if (r === 3) return '#fbbf24';
        return '#a3e635';
    };

    for (let d = 1; d <= NUM_SLOTS; d++) {
        const [sx, sy] = depthScreen(d);
        const c = slotColor(d);
        // Draw slot circle
        s += `<circle cx="${sx}" cy="${sy}" r="24" fill="none" stroke="${c}" stroke-width="1.5" stroke-dasharray="4,3" opacity="0.4" id="slot-${d}"/>`;
        // Draw depth label
        s += `<text x="${sx}" y="${sy + 42}" text-anchor="middle" fill="${c}" font-family="JetBrains Mono" font-size="10" font-weight="600" opacity="0.6">d=${d}</text>`;
    }
    
    // Line arrows bridging adjacent slots
    for (let d = 0; d < NUM_SLOTS; d++) {
        const [x1] = depthScreen(d === 0 ? 'proc' : d);
        const [x2] = depthScreen(d + 1);
        s += `<line x1="${x1 + 25}" y1="${PROC_SY}" x2="${x2 - 27}" y2="${PROC_SY}" stroke="rgba(148,163,184,0.15)" stroke-width="2" marker-end="url(#arr)"/>`;
    }

    // Dynamic cost-path layer
    s += `<g id="cost-paths"></g>`;

    svg.innerHTML = s;
}
"""

for f in files:
    with open(f, "r") as file:
        content = file.read()
        
    # Replace Geometry section
    content = re.sub(
        r'// ============================================================\n// GEOMETRY — Upper-half spiral from manhattan_figure.py\n// ============================================================.*?// ============================================================\n// VARIABLE DEFINITIONS',
        geometry_replacement + '\n// ============================================================\n// VARIABLE DEFINITIONS',
        content,
        flags=re.DOTALL
    )
    
    # Replace Build SVG section
    content = re.sub(
        r'// ============================================================\n// BUILD SVG\n// ============================================================.*?// ============================================================\n// BUILD CHIPS',
        buildsvg_replacement + '\n// ============================================================\n// BUILD CHIPS',
        content,
        flags=re.DOTALL
    )
    
    # In renderState, we need to update the cost-path drawing logic
    # Find the cost-path logic
    cost_path_replacement = """    // --- Cost paths (Arched lines) ---
    const cp = document.getElementById('cost-paths');
    let pathHTML = '';
    st.reads.forEach((r, idx) => {
        const [tx, ty] = depthScreen(r.depth);
        const cost = isqrtCeil(r.depth);
        
        // Draw arc from PROC to Target
        const heightArc = -40 - (idx * 25); // staggered height for multiple arcs
        const midX = (PROC_SX + tx) / 2;
        
        pathHTML += `<path d="M ${PROC_SX} ${PROC_SY - 25} Q ${midX} ${PROC_SY + heightArc * 2} ${tx} ${ty - 25}" fill="none" stroke="rgba(251,113,133,0.55)" stroke-width="3" marker-end="url(#arr-red)"/>`;
        
        // Cost label
        pathHTML += `<rect x="${midX - 25}" y="${PROC_SY + heightArc - 10}" width="50" height="20" rx="4" fill="rgba(15,23,42,0.8)" stroke="#fb7185" stroke-width="1"/>`;
        pathHTML += `<text x="${midX}" y="${PROC_SY + heightArc + 3}" text-anchor="middle" fill="#fb7185" font-family="JetBrains Mono" font-size="10" font-weight="700">cost=${cost}</text>`;
    });
    cp.innerHTML = pathHTML;"""
    
    content = re.sub(
        r'    // --- Cost paths \(red L-shapes\) ---.*?cp\.innerHTML = pathHTML;',
        cost_path_replacement,
        content,
        flags=re.DOTALL
    )
    
    # Update side table to remove (x,y) grid coordinates since it's 1D linear now
    # Replace <th>(x, y)</th> with <th>Cost</th>, but wait, Cost is already there. Let's just remove the <th>
    content = content.replace("<th>(x, y)</th>", "")
    
    # In renderState, the side table generation:
    # rows += `<tr class="${cls}">...<td>(${gx >= 0 ? '+' : ''}${gx}, ${gy})</td>...
    # We remove that td entirely
    content = re.sub(
        r'const \[gx, gy\] = spiralGrid\(e\.depth\);',
        '',
        content
    )
    content = re.sub(
        r'<td>\(\$\{gx >= 0 \? \'\+\' : \'\'\}\$\{gx\}, \$\{gy\}\)</td>\n',
        '',
        content
    )
    
    with open(f, "w") as file:
        file.write(content)
