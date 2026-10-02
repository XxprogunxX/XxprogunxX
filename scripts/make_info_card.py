#!/usr/bin/env python3
import os

def generate_info_card():
    is_static = os.environ.get("STATIC") == "1"
    
    width = 490
    height = 460
    
    rows = [
        ("user_header", '<tspan fill="#58a6ff" font-weight="700">javier</tspan><tspan fill="#8b949e">@</tspan><tspan fill="#7ee787" font-weight="700">XxprogunxX</tspan>'),
        ("separator", '<tspan fill="#30363d">--------------------------------------------------</tspan>'),
        ("OS", "Web &amp; Cloud Environment"),
        ("Role", "Software Developer | Full Stack"),
        ("Specialty", "E-commerce &amp; Payment Gateways (Mercado Pago)"),
        ("Frontend", "React, Next.js, TypeScript, Tailwind CSS"),
        ("Backend", "Node.js, Express, Prisma, GraphQL"),
        ("Databases", "PostgreSQL, MySQL, Redis"),
        ("DevOps", "Docker, Cloudflare Workers, Linux, Vercel"),
        ("separator2", '<tspan fill="#30363d">--------------------------------------------------</tspan>'),
        ("Project 1", "🥖 Panaderia (E-commerce + Mercado Pago)"),
        ("Project 2", "📋 TASKFLOW (Agile Task Management)"),
        ("Project 3", "📲 OrderFlow (Active Order System)"),
        ("Location", "Mexico 🇲🇽"),
        ("Status", "🟢 Open to impactful projects &amp; freelance"),
    ]

    lines_svg = []
    base_y = 62
    line_height = 21

    for idx, item in enumerate(rows):
        y = base_y + idx * line_height
        delay = idx * 0.08
        anim_style = "" if is_static else f'style="animation-delay: {delay:.2f}s;"'
        
        if item[0].startswith("separator") or item[0] == "user_header":
            content = item[1]
            lines_svg.append(f'    <text x="24" y="{y}" class="line" {anim_style}>{content}</text>')
        else:
            key, val = item
            key_colored = f'<tspan fill="#d2a8ff" font-weight="600">{key}:</tspan>'
            val_colored = f'<tspan fill="#c9d1d9"> {val}</tspan>'
            lines_svg.append(f'    <text x="24" y="{y}" class="line" {anim_style}>{key_colored}{val_colored}</text>')

    # Color swatches at bottom (neofetch signature)
    swatch_y1 = base_y + len(rows) * line_height + 10
    swatch_y2 = swatch_y1 + 14
    swatches1 = ["#0d1117", "#ff7b72", "#7ee787", "#f2cc60", "#58a6ff", "#bc8cff", "#39c5cf", "#b1bac4"]
    swatches2 = ["#484f58", "#ffa198", "#56d364", "#e3b341", "#79c0ff", "#d2a8ff", "#56d4dd", "#f0f6fc"]

    swatch_elements = []
    swatch_w = 20
    swatch_h = 10
    swatch_start_x = 24
    
    delay_palette = len(rows) * 0.08 + 0.1
    anim_palette = "" if is_static else f'style="animation-delay: {delay_palette:.2f}s;"'

    for i, (c1, c2) in enumerate(zip(swatches1, swatches2)):
        x = swatch_start_x + i * (swatch_w + 3)
        swatch_elements.append(f'<rect x="{x}" y="{swatch_y1}" width="{swatch_w}" height="{swatch_h}" rx="2" fill="{c1}" class="line" {anim_palette} />')
        swatch_elements.append(f'<rect x="{x}" y="{swatch_y2}" width="{swatch_w}" height="{swatch_h}" rx="2" fill="{c2}" class="line" {anim_palette} />')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" fill="none">
  <defs>
    <style>
      @keyframes lineFadeIn {{
        0% {{
          opacity: 0;
          transform: translateY(6px);
        }}
        100% {{
          opacity: 1;
          transform: translateY(0);
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
      .line {{
        font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', Consolas, monospace;
        font-size: 11.5px;
        {"opacity: 1;" if is_static else "opacity: 0; animation: lineFadeIn 0.35s ease forwards;"}
      }}
    </style>
  </defs>

  <!-- Container Box -->
  <rect width="{width}" height="{height}" rx="8" class="terminal-bg" />
  
  <!-- Header Bar -->
  <path d="M 0 8 Q 0 0 8 0 L {width - 8} 0 Q {width} 0 {width} 8 L {width} 32 L 0 32 Z" class="header-bar" />
  
  <!-- Window Controls -->
  <circle cx="20" cy="16" r="5.5" fill="#ff5f56" />
  <circle cx="38" cy="16" r="5.5" fill="#ffbd2e" />
  <circle cx="56" cy="16" r="5.5" fill="#27c93f" />

  <!-- Window Title -->
  <text x="{width // 2}" y="20" text-anchor="middle" class="terminal-title">javier@github: ~/neofetch</text>

  <!-- Content Lines -->
{chr(10).join(lines_svg)}

  <!-- Terminal Color Palette -->
  {chr(10).join(swatch_elements)}
</svg>'''

    with open("info-card.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)

    print("Generated info-card.svg successfully!")

if __name__ == "__main__":
    generate_info_card()
