#!/usr/bin/env python3
import json
import os
from datetime import datetime

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

def render_heatmap():
    json_path = "data/contributions.json"
    if not os.path.exists(json_path):
        print(f"Error: {json_path} does not exist. Run fetch_contributions.py first.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    days = data.get("days", [])
    total = data.get("total_contributions", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)
    best_day = data.get("best_day", {"date": "", "count": 0})
    username = data.get("username", "XxprogunxX")

    # Dimensions
    svg_width = 860
    svg_height = 205
    cell_size = 11
    cell_gap = 3
    step = cell_size + cell_gap  # 14px

    start_x = 52
    start_y = 66

    # Group days into columns of 7 (Sunday to Saturday)
    # We want 53 columns
    # Let's map days to columns
    # Find the day of week for the first date
    cols = []
    current_col = []
    
    # We will compute month labels
    month_positions = []
    last_month = None

    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        gh_weekday = (dt.weekday() + 1) % 7 # 0 is Sunday, 6 is Saturday
        
        # When Sunday and current_col is not empty, start a new column
        if gh_weekday == 0 and current_col:
            cols.append(current_col)
            current_col = []
            
        current_col.append((gh_weekday, d, dt))

    if current_col:
        cols.append(current_col)

    # Limit to 53 columns
    if len(cols) > 53:
        cols = cols[-53:]

    # Calculate month labels positions
    for col_idx, col in enumerate(cols):
        for gh_weekday, d, dt in col:
            m = dt.strftime("%b")
            if m != last_month and dt.day <= 14: # start of month
                month_positions.append((col_idx, m))
                last_month = m
                break

    # SVG Elements
    cells_svg = []
    for col_idx, col in enumerate(cols):
        for gh_weekday, d, dt in col:
            x = start_x + col_idx * step
            y = start_y + gh_weekday * step
            
            lvl = d.get("level", 0)
            if lvl < 0: lvl = 0
            if lvl >= len(PALETTE): lvl = len(PALETTE) - 1
            color = PALETTE[lvl]

            # Diagonal animation delay
            delay = (col_idx * 0.015) + (gh_weekday * 0.035)
            
            count = d.get("count", 0)
            date_str = d.get("date", "")
            title_text = f"{count} contributions on {date_str}"

            cell_el = f'<rect class="cell" x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2.5" fill="{color}" style="animation-delay: {delay:.3f}s;"><title>{title_text}</title></rect>'
            cells_svg.append(cell_el)

    # Month labels
    months_svg = []
    for col_idx, m_name in month_positions:
        x = start_x + col_idx * step
        y = start_y - 8
        months_svg.append(f'<text x="{x}" y="{y}" class="month-label">{m_name}</text>')

    # Day labels (Mon, Wed, Fri) -> gh_weekday: 1=Mon, 3=Wed, 5=Fri
    days_labels_svg = []
    day_names = [(1, "Mon"), (3, "Wed"), (5, "Fri")]
    for w_idx, label in day_names:
        y = start_y + w_idx * step + 9
        days_labels_svg.append(f'<text x="{start_x - 10}" y="{y}" class="weekday-label" text-anchor="end">{label}</text>')

    # Legend at bottom right
    legend_x = svg_width - 150
    legend_y = svg_height - 18
    legend_svg = [f'<text x="{legend_x - 30}" y="{legend_y + 8}" class="stat-sub">Less</text>']
    for idx, c in enumerate(PALETTE):
        lx = legend_x + idx * (cell_size + 2)
        legend_svg.append(f'<rect x="{lx}" y="{legend_y}" width="{cell_size}" height="{cell_size}" rx="2" fill="{c}" />')
    legend_svg.append(f'<text x="{legend_x + len(PALETTE) * (cell_size + 2) + 5}" y="{legend_y + 8}" class="stat-sub">More</text>')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}" fill="none">
  <defs>
    <style>
      @keyframes cellReveal {{
        0% {{
          opacity: 0;
          transform: scale(0.2);
        }}
        70% {{
          opacity: 1;
          transform: scale(1.15);
        }}
        100% {{
          opacity: 1;
          transform: scale(1);
        }}
      }}
      .terminal-bg {{
        fill: #0d1117;
        stroke: #30363d;
        stroke-width: 1px;
      }}
      .header-bar {{
        fill: #161b22;
        stroke: #30363d;
        stroke-width: 1px;
      }}
      .terminal-title {{
        font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
        font-size: 11px;
        fill: #8b949e;
        font-weight: 500;
      }}
      .cell {{
        opacity: 0;
        transform-box: fill-box;
        transform-origin: center;
        animation: cellReveal 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      }}
      .month-label, .weekday-label {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        font-size: 10px;
        fill: #7d8590;
      }}
      .stat-text {{
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 11px;
        fill: #58a6ff;
        font-weight: 600;
      }}
      .stat-sub {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        font-size: 10px;
        fill: #7d8590;
      }}
      .stat-bold {{
        fill: #c9d1d9;
        font-weight: 600;
      }}
    </style>
  </defs>

  <!-- Container Box -->
  <rect width="{svg_width}" height="{svg_height}" rx="8" class="terminal-bg" />
  
  <!-- Header Bar -->
  <path d="M 0 8 Q 0 0 8 0 L {svg_width - 8} 0 Q {svg_width} 0 {svg_width} 8 L {svg_width} 32 L 0 32 Z" class="header-bar" />
  
  <!-- Window Controls -->
  <circle cx="20" cy="16" r="5.5" fill="#ff5f56" />
  <circle cx="38" cy="16" r="5.5" fill="#ffbd2e" />
  <circle cx="56" cy="16" r="5.5" fill="#27c93f" />

  <!-- Window Title -->
  <text x="{svg_width // 2}" y="20" text-anchor="middle" class="terminal-title">{username}@github: ~/contributions.sh</text>

  <!-- Month Labels -->
  {''.join(months_svg)}

  <!-- Weekday Labels -->
  {''.join(days_labels_svg)}

  <!-- Grid Cells -->
  {''.join(cells_svg)}

  <!-- Footer Stats -->
  <g transform="translate({start_x}, {svg_height - 18})">
    <text y="8" class="stat-sub">
      <tspan class="stat-bold">{total}</tspan> contribuciones en el último año &#160;•&#160; 
      Racha actual: <tspan class="stat-text">{current_streak} días</tspan> &#160;•&#160; 
      Mejor racha: <tspan class="stat-text">{longest_streak} días</tspan>
    </text>
  </g>

  <!-- Legend -->
  {''.join(legend_svg)}
</svg>'''

    with open("contrib-heatmap.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)

    print("Generated contrib-heatmap.svg successfully!")

if __name__ == "__main__":
    render_heatmap()
