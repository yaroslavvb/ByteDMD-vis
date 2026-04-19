import re

files = [
    ("dotproduct_stack-live-linear.html", 9),
    ("dotproduct_stack-mattson-linear.html", 15)
]

for f, def_slots in files:
    with open(f, "r") as file:
        content = file.read()
        
    # Re-insert NUM_SLOTS in GEOMETRY section
    if "const NUM_SLOTS" not in content:
        content = content.replace("const CELL = 52;", f"const CELL = 52;\nconst NUM_SLOTS = {def_slots};")

    # Update buildSVG to allow dynamic width sizing for horizontal scroll
    svg_update = """// ============================================================
// BUILD SVG
// ============================================================
function buildSVG() {
    const svg = document.getElementById('grid-svg');
    const container = document.getElementById('viz-container');
    const rect = container.getBoundingClientRect();
    const H = rect.height;
    
    // Allow horizontal scroll if necessary
    container.style.overflowX = 'auto';
    container.style.overflowY = 'hidden';

    PROC_SX = 50;
    PROC_SY = H / 2 - 20;

    // Calculate required width
    const minW = rect.width;
    const requiredW = Math.max(minW, PROC_SX + NUM_SLOTS * CELL + 60);
    
    svg.setAttribute('viewBox', `0 0 ${requiredW} ${H}`);
    svg.style.width = requiredW + 'px';
    svg.style.height = H + 'px';

    let s = '';"""
    
    content = re.sub(r'// ============================================================\n// BUILD SVG.*?let s = \'\';', svg_update, content, flags=re.DOTALL)
    
    # Let's also restore the "proc" check in depthScreen
    # It might be returning just fine, but let's make sure chips correctly offset scroll position
    # The chips are absolutely positioned against viz-container. If viz-container scrolls, chips might scroll out of place if they are position absolute inside a scrolling container.
    # To fix this, chips layer should ALSO have the same width!
    
    chip_layer_update = """    // Dynamic cost-path layer
    s += `<g id="cost-paths"></g>`;

    svg.innerHTML = s;
    const cl = document.getElementById('chips-layer');
    cl.style.width = requiredW + 'px';
    cl.style.height = H + 'px';
}"""
    content = re.sub(r'    // Dynamic cost-path layer\n    s \+= `<g id="cost-paths"></g>`;\n\n    svg\.innerHTML = s;\n}', chip_layer_update, content)
    
    with open(f, "w") as file:
        file.write(content)

