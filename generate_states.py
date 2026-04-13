import json

def rt(cost_str):
    return f"cost = ⌈√{cost_str}⌉ = <strong>{cost_str}</strong>"

# The 7 steps
steps = [
    # 1. READ x0@8, y0@4 -> Store m0 
    {
        "id": "1",
        "nodes": ["x₀", "y₀"],
        "d_text": "x₀@8, y₀@4",
        "d_obj": [("x0", 8, "⌈√8⌉ = <strong>3</strong>"), ("y0", 4, "⌈√4⌉ = <strong>2</strong>")],
        "prev_vars": "{ x0: 8, x1: 7, x2: 6, x3: 5, y0: 4, y1: 3, y2: 2, y3: 1 }",
        "proc_vars": "{ x0: 'proc', x1: 6, x2: 5, x3: 4, y0: 'proc', y1: 3, y2: 2, y3: 1 }",
        "store_vars": "{ x1: 7, x2: 6, x3: 5, y1: 4, y2: 3, y3: 2, m0: 1 }",
        "store_desc": "Product <strong>m₀</strong> pushed to depth 1. All survivors pushed outward by 1.",
        "cost": 5, "delta": 5,
        "store_name": "m₀ = x₀·y₀"
    },
    # 2. READ x1@7, y1@4 -> Store m1
    {
        "id": "2",
        "nodes": ["x₁", "y₁"],
        "d_text": "x₁@7, y₁@4",
        "d_obj": [("x1", 7, "⌈√7⌉ = <strong>3</strong>"), ("y1", 4, "⌈√4⌉ = <strong>2</strong>")],
        "prev_vars": "{ x1: 7, x2: 6, x3: 5, y1: 4, y2: 3, y3: 2, m0: 1 }",
        "proc_vars": "{ x1: 'proc', x2: 5, x3: 4, y1: 'proc', y2: 3, y3: 2, m0: 1 }",
        "store_vars": "{ x2: 6, x3: 5, y2: 4, y3: 3, m0: 2, m1: 1 }",
        "store_desc": "Product <strong>m₁</strong> pushed to depth 1. Survivors pushed outward.",
        "cost": 10, "delta": 5,
        "store_name": "m₁ = x₁·y₁"
    },
    # 3. READ m0@2, m1@1 -> Store s01
    {
        "id": "3",
        "nodes": ["m₀", "m₁"],
        "d_text": "m₀@2, m₁@1",
        "d_obj": [("m0", 2, "⌈√2⌉ = <strong>2</strong>"), ("m1", 1, "⌈√1⌉ = <strong>1</strong>")],
        "prev_vars": "{ x2: 6, x3: 5, y2: 4, y3: 3, m0: 2, m1: 1 }",
        "proc_vars": "{ x2: 4, x3: 3, y2: 2, y3: 1, m0: 'proc', m1: 'proc' }",
        "store_vars": "{ x2: 5, x3: 4, y2: 3, y3: 2, s01: 1 }",
        "store_desc": "Partial sum <strong>s₀₁</strong> = x₀y₀ + x₁y₁ pushed to depth 1. Survivors pushed outward.",
        "cost": 13, "delta": 3,
        "store_name": "s₀₁ = m₀ + m₁"
    },
    # 4. READ x2@5, y2@3 -> Store m2
    {
        "id": "4",
        "nodes": ["x₂", "y₂"],
        "d_text": "x₂@5, y₂@3",
        "d_obj": [("x2", 5, "⌈√5⌉ = <strong>3</strong>"), ("y2", 3, "⌈√3⌉ = <strong>2</strong>")],
        "prev_vars": "{ x2: 5, x3: 4, y2: 3, y3: 2, s01: 1 }",
        "proc_vars": "{ x2: 'proc', x3: 3, y2: 'proc', y3: 2, s01: 1 }",
        "store_vars": "{ x3: 4, y3: 3, s01: 2, m2: 1 }",
        "store_desc": "Product <strong>m₂</strong> pushed to depth 1. Survivors pushed outward.",
        "cost": 18, "delta": 5,
        "store_name": "m₂ = x₂·y₂"
    },
    # 5. READ s01@2, m2@1 -> Store s012
    {
        "id": "5",
        "nodes": ["s₀₁", "m₂"],
        "d_text": "s₀₁@2, m₂@1",
        "d_obj": [("s01", 2, "⌈√2⌉ = <strong>2</strong>"), ("m2", 1, "⌈√1⌉ = <strong>1</strong>")],
        "prev_vars": "{ x3: 4, y3: 3, s01: 2, m2: 1 }",
        "proc_vars": "{ x3: 2, y3: 1, s01: 'proc', m2: 'proc' }",
        "store_vars": "{ x3: 3, y3: 2, s012: 1 }",
        "store_desc": "Partial sum <strong>s₀₁₂</strong> = x₀y₀ + x₁y₁ + x₂y₂ pushed to depth 1. Survivors pushed outward.",
        "cost": 21, "delta": 3,
        "store_name": "s₀₁₂ = s₀₁ + m₂"
    },
    # 6. READ x3@3, y3@2 -> Store m3
    {
        "id": "6",
        "nodes": ["x₃", "y₃"],
        "d_text": "x₃@3, y₃@2",
        "d_obj": [("x3", 3, "⌈√3⌉ = <strong>2</strong>"), ("y3", 2, "⌈√2⌉ = <strong>2</strong>")],
        "prev_vars": "{ x3: 3, y3: 2, s012: 1 }",
        "proc_vars": "{ x3: 'proc', y3: 'proc', s012: 1 }",
        "store_vars": "{ s012: 2, m3: 1 }",
        "store_desc": "Product <strong>m₃</strong> pushed to depth 1. s₀₁₂ pushed to depth 2.",
        "cost": 25, "delta": 4,
        "store_name": "m₃ = x₃·y₃"
    },
    # 7. READ s012@2, m3@1 -> Store z
    {
        "id": "7",
        "nodes": ["s₀₁₂", "m₃"],
        "d_text": "s₀₁₂@2, m₃@1",
        "d_obj": [("s012", 2, "⌈√2⌉ = <strong>2</strong>"), ("m3", 1, "⌈√1⌉ = <strong>1</strong>")],
        "prev_vars": "{ s012: 2, m3: 1 }",
        "proc_vars": "{ s012: 'proc', m3: 'proc' }",
        "store_vars": "{ z: 1 }",
        "store_desc": "Dot product result <strong>z</strong> stored at depth 1.<br>Total ByteDMD cost = <strong>28</strong> — the sum of Manhattan distances over all reads.",
        "cost": 28, "delta": 3,
        "store_name": "z"
    }
]

out = "const states = [\n"
out += """    {
        label: "Initial State",
        desc: "Vectors <strong>x</strong>=[x₀,x₁,x₂,x₃] and <strong>y</strong>=[y₀,y₁,y₂,y₃] loaded onto the LRU stack.<br>y₃ is most-recently-used (depth 1). x₀ is deepest (depth 8, ring 3).",
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
        desc: "Identify {s['nodes'][0]} at depth {s['d_obj'][0][1]} (cost = {s['d_obj'][0][2]}) and {s['nodes'][1]} at depth {s['d_obj'][1][1]} (cost = {s['d_obj'][1][2]}).<br>Cost paths shown in red.",
        vars: {s['prev_vars']},
        reads: {reads_arr},
        cost: {s['cost']}, delta: {s['delta']},
    }},
"""
    # B. Pull
    out += f"""    {{
        label: "Step {s['id']}B — Pull into PE",
        desc: "Variables pulled into processor.<br>Dead variables <em>vaporized</em>. Survivors slide.",
        vars: {s['proc_vars']},
        reads: {reads_arr},
        cost: {s['cost']}, delta: 0,
    }},
"""
    # C. Store
    label_c = "Final" if s['id'] == "7" else f"Step {s['id']}C"
    store_title = f"Store {s['store_name']}" if label_c != "Final" else f"Store {s['store_name']} = x₀y₀ + x₁y₁ + x₂y₂ + x₃y₃"
    out += f"""    {{
        label: "{label_c} — {store_title}",
        desc: "{s['store_desc']}",
        vars: {s['store_vars']},
        reads: [],
        cost: {s['cost']}, delta: 0,
    }},
"""

out += "];"

with open("states_perfect.js", "w") as f:
    f.write(out)

