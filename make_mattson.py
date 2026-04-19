with open("dotproduct_stack-live.html", "r") as f:
    text = f.read()

# Replace titles
text = text.replace("ByteDMD Trace", "Mattson Model Trace (No Reclamation)")
text = text.replace("<title>Dot Product — LRU Geometric Stack</title>", "<title>Dot Product — Mattson Model Stack</title>")

# Build the new states array
steps = [
    # 1. READ x0@8, y0@4 -> Store m0 
    {
        "id": "1",
        "nodes": ["x₀", "y₀"],
        "d_obj": [("x0", 8, 3), ("y0", 4, 2)],
        "prev_vars": "{ x0: 8, x1: 7, x2: 6, x3: 5, y0: 4, y1: 3, y2: 2, y3: 1 }",
        "proc_vars": "{ x1: 8, x2: 7, x3: 6, y1: 5, y2: 4, y3: 3, x0: 'proc', y0: 'proc' }",
        "store_vars": "{ x1: 9, x2: 8, x3: 7, y1: 6, y2: 5, y3: 4, x0: 3, y0: 2, m0: 1 }",
        "cost": 5, "delta": 5,
        "delta_desc": "Identified at original depths. Bumped to top.",
        "store_name": "m₀ = x₀·y₀"
    },
    # 2. READ x1@9, y1@6 -> Store m1
    {
        "id": "2",
        "nodes": ["x₁", "y₁"],
        "d_obj": [("x1", 9, 3), ("y1", 6, 3)],
        "prev_vars": "{ x1: 9, x2: 8, x3: 7, y1: 6, y2: 5, y3: 4, x0: 3, y0: 2, m0: 1 }",
        "proc_vars": "{ x2: 9, x3: 8, y2: 7, y3: 6, x0: 5, y0: 4, m0: 3, x1: 'proc', y1: 'proc' }",
        "store_vars": "{ x2: 10, x3: 9, y2: 8, y3: 7, x0: 6, y0: 5, m0: 4, x1: 3, y1: 2, m1: 1 }",
        "cost": 11, "delta": 6,
        "delta_desc": "Bumped to top.",
        "store_name": "m₁ = x₁·y₁"
    },
    # 3. READ m0@4, m1@1 -> Store s01
    {
        "id": "3",
        "nodes": ["m₀", "m₁"],
        "d_obj": [("m0", 4, 2), ("m1", 1, 1)],
        "prev_vars": "{ x2: 10, x3: 9, y2: 8, y3: 7, x0: 6, y0: 5, m0: 4, x1: 3, y1: 2, m1: 1 }",
        "proc_vars": "{ x2: 10, x3: 9, y2: 8, y3: 7, x0: 6, y0: 5, x1: 4, y1: 3, m0: 'proc', m1: 'proc' }",
        "store_vars": "{ x2: 11, x3: 10, y2: 9, y3: 8, x0: 7, y0: 6, x1: 5, y1: 4, m0: 3, m1: 2, s01: 1 }",
        "cost": 14, "delta": 3,
        "delta_desc": "Bumped to top.",
        "store_name": "s₀₁ = m₀ + m₁"
    },
    # 4. READ x2@11, y2@9 -> Store m2
    {
        "id": "4",
        "nodes": ["x₂", "y₂"],
        "d_obj": [("x2", 11, 4), ("y2", 9, 3)],
        "prev_vars": "{ x2: 11, x3: 10, y2: 9, y3: 8, x0: 7, y0: 6, x1: 5, y1: 4, m0: 3, m1: 2, s01: 1 }",
        "proc_vars": "{ x3: 11, y3: 10, x0: 9, y0: 8, x1: 7, y1: 6, m0: 5, m1: 4, s01: 3, x2: 'proc', y2: 'proc' }",
        "store_vars": "{ x3: 12, y3: 11, x0: 10, y0: 9, x1: 8, y1: 7, m0: 6, m1: 5, s01: 4, x2: 3, y2: 2, m2: 1 }",
        "cost": 21, "delta": 7,
        "delta_desc": "Bumped to top.",
        "store_name": "m₂ = x₂·y₂"
    },
    # 5. READ s01@4, m2@1 -> Store s012
    {
        "id": "5",
        "nodes": ["s₀₁", "m₂"],
        "d_obj": [("s01", 4, 2), ("m2", 1, 1)],
        "prev_vars": "{ x3: 12, y3: 11, x0: 10, y0: 9, x1: 8, y1: 7, m0: 6, m1: 5, s01: 4, x2: 3, y2: 2, m2: 1 }",
        "proc_vars": "{ x3: 12, y3: 11, x0: 10, y0: 9, x1: 8, y1: 7, m0: 6, m1: 5, x2: 4, y2: 3, s01: 'proc', m2: 'proc' }",
        "store_vars": "{ x3: 13, y3: 12, x0: 11, y0: 10, x1: 9, y1: 8, m0: 7, m1: 6, x2: 5, y2: 4, s01: 3, m2: 2, s012: 1 }",
        "cost": 24, "delta": 3,
        "delta_desc": "Bumped to top.",
        "store_name": "s₀₁₂ = s₀₁ + m₂"
    },
    # 6. READ x3@13, y3@12 -> Store m3
    {
        "id": "6",
        "nodes": ["x₃", "y₃"],
        "d_obj": [("x3", 13, 4), ("y3", 12, 4)],
        "prev_vars": "{ x3: 13, y3: 12, x0: 11, y0: 10, x1: 9, y1: 8, m0: 7, m1: 6, x2: 5, y2: 4, s01: 3, m2: 2, s012: 1 }",
        "proc_vars": "{ x0: 13, y0: 12, x1: 11, y1: 10, m0: 9, m1: 8, x2: 7, y2: 6, s01: 5, m2: 4, s012: 3, x3: 'proc', y3: 'proc' }",
        "store_vars": "{ x0: 14, y0: 13, x1: 12, y1: 11, m0: 10, m1: 9, x2: 8, y2: 7, s01: 6, m2: 5, s012: 4, x3: 3, y3: 2, m3: 1 }",
        "cost": 32, "delta": 8,
        "delta_desc": "Bumped to top.",
        "store_name": "m₃ = x₃·y₃"
    },
    # 7. READ s012@4, m3@1 -> Store z
    {
        "id": "7",
        "nodes": ["s₀₁₂", "m₃"],
        "d_obj": [("s012", 4, 2), ("m3", 1, 1)],
        "prev_vars": "{ x0: 14, y0: 13, x1: 12, y1: 11, m0: 10, m1: 9, x2: 8, y2: 7, s01: 6, m2: 5, s012: 4, x3: 3, y3: 2, m3: 1 }",
        "proc_vars": "{ x0: 14, y0: 13, x1: 12, y1: 11, m0: 10, m1: 9, x2: 8, y2: 7, s01: 6, m2: 5, x3: 4, y3: 3, s012: 'proc', m3: 'proc' }",
        "store_vars": "{ x0: 15, y0: 14, x1: 13, y1: 12, m0: 11, m1: 10, x2: 9, y2: 8, s01: 7, m2: 6, x3: 5, y3: 4, s012: 3, m3: 2, z: 1 }",
        "cost": 35, "delta": 3,
        "delta_desc": "Bumped to top.",
        "store_name": "z"
    }
]

out = "const states = [\n"
out += """    {
        label: "Initial State",
        desc: "Vectors <strong>x</strong>=[x₀,x₁,x₂,x₃] and <strong>y</strong>=[y₀,y₁,y₂,y₃] loaded onto Mattson LRU stack.<br>Values are NEVER deleted, causing steady growth of memory footprint.",
        vars: { x0: 8, x1: 7, x2: 6, x3: 5, y0: 4, y1: 3, y2: 2, y3: 1 },
        reads: [],
        cost: 0, delta: 0,
    },
"""

for s in steps:
    reads_arr = f"[{{ id: '{s['d_obj'][0][0]}', depth: {s['d_obj'][0][1]} }}, {{ id: '{s['d_obj'][1][0]}', depth: {s['d_obj'][1][1]} }}]"
    
    # A. Highlight
    out += f"""    {{
        label: "Step {s['id']}A — Highlight {s['nodes'][0]}, {s['nodes'][1]}",
        desc: "Identify {s['nodes'][0]} at depth {s['d_obj'][0][1]} (cost {s['d_obj'][0][2]}) and {s['nodes'][1]} at depth {s['d_obj'][1][1]} (cost {s['d_obj'][1][2]}).",
        vars: {s['prev_vars']},
        reads: {reads_arr},
        cost: {s['cost']}, delta: {s['delta']},
    }},
"""
    # B. Pull
    out += f"""    {{
        label: "Step {s['id']}B — Pull into PE",
        desc: "{s['delta_desc']}",
        vars: {s['proc_vars']},
        reads: {reads_arr},
        cost: {s['cost']}, delta: 0,
    }},
"""
    # C. Store
    label_c = "Final" if s['id'] == "7" else f"Step {s['id']}C"
    store_title = f"Store {s['store_name']}" if label_c != "Final" else f"Store {s['store_name']} = x₀y₀ + x₁y₁ + x₂y₂ + x₃y₃"
    desc_c = f"Product <strong>{s['store_name'].split(' ')[0]}</strong> pushed to top. Nothing is vaporized." if s['id'] != "7" else "Dot product result <strong>z</strong> stored at depth 1.<br>Total Mattson cost = <strong>35</strong> — the sum of distances over all reads."
    out += f"""    {{
        label: "{label_c} — {store_title}",
        desc: "{desc_c}",
        vars: {s['store_vars']},
        reads: [],
        cost: {s['cost']}, delta: 0,
    }},
"""

out += "];"

import re
text = re.sub(r'const states = \[(?:[^\[\]]|\[[^\[\]]*\])*\];', out, text, flags=re.DOTALL)

# Adjust ring sizes in SVGs
# In live trace, NUM_SLOTS was 9. The Mattson stack goes up to 15!
# Ring sizes: Ring 1 (1 slot), Ring 2 (3), Ring 3 (5), Ring 4 (7), Ring 5 (9)
# 1 + 3 + 5 + 7 = 16. So we need up to Ring 4.
text = text.replace("const NUM_SLOTS = 9;", "const NUM_SLOTS = 16;")

# We need to expand rings to 4 in grid rendering
rings_block = """    const ringStyles = [
        '',
        { color: 'rgba(139,92,246,0.25)', label: 'Ring 1 — 1 slot', ly: -18 },
        { color: 'rgba(236,72,153,0.2)',  label: 'Ring 2 — 3 slots', ly: -18 },
        { color: 'rgba(251,191,36,0.15)', label: 'Ring 3 — 5 slots', ly: -18 },
        { color: 'rgba(163,230,53,0.2)',  label: 'Ring 4 — 7 slots', ly: -18 },
    ];
    for (let ring = 1; ring <= 4; ring++) {"""
text = re.sub(r'const ringStyles = \[\n.*?for \(let ring = 1; ring <= 3; ring\+\+\) {', rings_block, text, flags=re.DOTALL)


with open("dotproduct_stack-mattson.html", "w") as f:
    f.write(text)

