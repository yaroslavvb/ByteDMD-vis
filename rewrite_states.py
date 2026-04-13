import re

with open('states_dump.js', 'r') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    if 'label: "Step' in line and '— Read' in line:
        # Extract the full state block
        state_lines = []
        # Find start of block. Usually it's the previous line "{"
        if i > 0 and lines[i-1].strip() == '{':
            state_lines.append(lines[i-1])
            start_idx = i - 1
        else:
            start_idx = i

        while not lines[i].strip() == '},':
            state_lines.append(lines[i])
            i += 1
        state_lines.append(lines[i]) # add "},"

        # We need the "vars" from the PREVIOUS state.
        # So we look backwards in new_lines to find the last vars map.
        prev_vars = ""
        for prev in reversed(new_lines):
            if "vars:" in prev:
                prev_vars = prev
                break

        full_state = "".join(state_lines)
        
        # Highlight state:
        # label: "Step XA — Highlight ..."
        # desc: "Identify ..."
        # vars: prev_vars
        # reads: original
        # cost: original, delta: original
        
        step_name = re.search(r'label: "(Step \w+) — Read ([^"]+)"', full_state).group(1)
        nodes = re.search(r'label: "(Step \w+) — Read ([^"]+)"', full_state).group(2)
        
        desc_highlight = re.search(r'desc: "READ ([^<]+)', full_state).group(1) + ".<br>Cost paths shown in red."
        desc_highlight = desc_highlight.replace('from depth', 'at depth')

        # Create Highlight state explicitly
        highlight_state = '    {\n'
        highlight_state += f'        label: "{step_name} — Highlight {nodes.replace("@8","").replace("@7","").replace("@5","").replace("@4","").replace("@3","").replace("@2","").replace("@1","")}",\n'
        
        highlight_state += f'        desc: "Identify {desc_highlight}",\n'
        highlight_state += prev_vars
        reads_line = [l for l in state_lines if 'reads:' in l][0]
        highlight_state += reads_line
        cost_line = [l for l in state_lines if 'cost:' in l][0]
        highlight_state += cost_line
        highlight_state += '    },\n'

        # Now the Read/Pull state
        # label: "Step XB — Pull ..."
        step_num = step_name.replace('A', '')
        read_state = '    {\n'
        read_state += f'        label: "Step {step_num}B — Pull into Processor",\n'
        read_state += '        desc: "Variables pulled into processor.<br>Dead variables <em>vaporized</em>. Survivors slide.",\n'
        vars_line = [l for l in state_lines if 'vars:' in l][0]
        read_state += vars_line
        read_state += reads_line
        read_line_cost = [l for l in state_lines if 'cost:' in l][0]
        read_cost = re.search(r'cost: \d+', read_line_cost).group(0)
        read_state += f'        {read_cost}, delta: 0,\n'
        read_state += '    },\n'

        new_lines.append(highlight_state)
        new_lines.append(read_state)
    elif 'label: "Step' in line and '— Store' in line:
        state_lines = []
        if i > 0 and lines[i-1].strip() == '{':
           state_lines.append(lines[i-1])
        else:
           pass
        while not lines[i].strip() == '},':
            state_lines.append(lines[i])
            i += 1
        state_lines.append(lines[i]) # add "},"

        full_state = "".join(state_lines)
        # It's Step XB -> Step XC
        step_match = re.search(r'label: "(Step \w+)B — Store', full_state)
        if step_match:
             full_state = full_state.replace(step_match.group(1) + 'B — Store', step_match.group(1) + 'C — Store')
        else:
             step_match = re.search(r'label: "(Step \w+)B — Store', full_state)
             if not step_match:
                 # It might be like Step 3B -> Step 3C
                 step_match2 = re.search(r'label: "(Step \d+)B — Store', full_state)
                 if step_match2:
                      full_state = full_state.replace(step_match2.group(1) + 'B — Store', step_match2.group(1) + 'C — Store')

        new_lines.extend(full_state.split('\n'))
        if new_lines[-1] == '':
             new_lines.pop()
             new_lines[-1] += '\n'
        # we can just write it manually if this logic is flawed.
    else:
        new_lines.append(line)
        if i > 0 and lines[i-1].strip() == '{' and 'label:' not in line:
            pass # we handled it
            
    i += 1

with open('states_new.js', 'w') as f:
    f.writelines(new_lines)
