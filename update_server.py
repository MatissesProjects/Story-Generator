import sys

with open('server.py', 'r') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "                    # Modify prompt for continuation" in line:
        start_idx = i
    if "                await log_progress(websocket, \"Turn complete.\", \"success\")" in line:
        end_idx = i

if start_idx != -1 and end_idx != -1:
    new_lines = lines[:start_idx]
    new_lines.append("                    await turn_orchestrator.process_turn(\n")
    new_lines.append("                        websocket, client_id, user_input, intent,\n")
    new_lines.append("                        log_progress, vision_orchestrator, music, world, atmosphere, curator_visual\n")
    new_lines.append("                    )\n")
    new_lines.append(lines[end_idx])
    new_lines.extend(lines[end_idx+1:])
    
    with open('server.py', 'w') as f:
        f.writelines(new_lines)
    print("Success")
else:
    print(f"Failed to find indices. Start: {start_idx}, End: {end_idx}")

