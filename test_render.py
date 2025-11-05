#!/usr/bin/env python3
"""Test the guilds panel rendering."""

# Mock data
dms_data = [
    {'display_name': 'Espe', 'id': '1', 'type': 'dm'},
    {'display_name': '_Glitch', 'id': '2', 'type': 'dm'},
    {'display_name': 'Kawz 🦑 🧢', 'id': '3', 'type': 'dm'},
    {'display_name': 'Clarity', 'id': '4', 'type': 'dm'},
    {'display_name': 'Ido Levi', 'id': '5', 'type': 'dm'},
]

guilds_data = [
    {'name': 'DanVek', 'id': '10', 'type': 'guild'},
    {'name': 'alvaro7000', 'id': '11', 'type': 'guild'},
    {'name': 'Antlers too Big', 'id': '12', 'type': 'guild'},
    {'name': 'darklord_95', 'id': '13', 'type': 'guild'},
    {'name': 'carlitoscardenas', 'id': '14', 'type': 'guild'},
    {'name': 'Zig', 'id': '15', 'type': 'guild'},
    {'name': 'vybecoder', 'id': '16', 'type': 'guild'},
    {'name': 'Appo', 'id': '17', 'type': 'guild'},
    {'name': 'glade', 'id': '18', 'type': 'guild'},
    {'name': 'Rin\'s Agent', 'id': '19', 'type': 'guild'},
]

def render_guilds():
    """Render guilds and DMs in fancy ASCII box format."""
    lines = []
    
    width = 28
    
    # Top border
    top_border = "╭Guilds" + "─" * (width - 6) + "╮"
    lines.append(top_border)
    
    # DMs section
    for dm in dms_data:
        name = dm.get('display_name', 'Unknown')
        available = width - 4
        if len(name) > available:
            name = name[:available - 1] + "…"
        line = f"│ ╰──{name:<{available}}│"
        lines.append(line)
    
    # Guilds section
    for guild in guilds_data:
        name = guild.get('name', 'Unknown')
        available = width - 4
        if len(name) > available:
            name = name[:available - 1] + "…"
        line = f"│ ╰──{name:<{available}}│"
        lines.append(line)
    
    # Bottom border
    bottom_border = "╰" + "─" * width + "╯"
    lines.append(bottom_border)
    
    return "\n".join(lines)

if __name__ == '__main__':
    output = render_guilds()
    print(output)
