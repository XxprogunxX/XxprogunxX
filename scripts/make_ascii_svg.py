#!/usr/bin/env python3
import sys
import os
import xml.sax.saxutils as saxutils
from PIL import Image

# Density ramp: Bright (sparse) -> Dark (dense)
# Starting with space clears the white background into nothingness
RAMP = " .`:-=+*cs#%@"

def make_ascii_svg(prepped_image_path="source-prepped.png", output_svg_path="javier-ascii.svg"):
    if not os.path.exists(prepped_image_path):
        print(f"Error: {prepped_image_path} does not exist. Run prep_photo.py first.")
        return

    img = Image.open(prepped_image_path).convert("L")
    img_w, img_h = img.size

    # Target dimensions of the terminal window
    svg_width = 370
    svg_height = 460
    header_height = 32

    # Character metrics in monospace
    # Font size 6.8px, character advance ~4.08px, line height ~7.5px
    font_size = 6.8
    char_w = 4.08
    line_h = 7.5
    
    # Available area inside window
    margin_top = header_height + 14
    margin_bottom = 12
    available_h = svg_height - margin_top - margin_bottom
    
    # Target rows ~ 52
    num_rows = int(available_h / line_h)
    
    # Character aspect ratio correction (monospace characters are taller than wide, ~1.84:1)
    char_aspect = line_h / char_w
    img_aspect = img_w / img_h
    num_cols = int(num_rows * img_aspect * char_aspect)

    # Ensure it fits within width
    max_cols = int((svg_width - 24) / char_w)
    if num_cols > max_cols:
        num_cols = max_cols
        num_rows = int(num_cols / (img_aspect * char_aspect))

    # Resize image to ASCII grid
    resized = img.resize((num_cols, num_rows), Image.Resampling.LANCZOS)
    pixels = resized.load()

    # Generate ASCII rows
    ascii_rows = []
    ramp_len = len(RAMP)

    for r in range(num_rows):
        row_str = []
        for c in range(num_cols):
            val = pixels[c, r]  # 0 = black, 255 = white
            # Invert: white (255) -> 0 (space), black (0) -> max density (@)
            ramp_idx = int((255 - val) / 255.0 * (ramp_len - 1))
            if ramp_idx < 0: ramp_idx = 0
            if ramp_idx >= ramp_len: ramp_idx = ramp_len - 1
            row_str.append(RAMP[ramp_idx])
        ascii_rows.append("".join(row_str))

    # Center grid horizontally
    content_width = num_cols * char_w
    start_x = (svg_width - content_width) / 2.0
    start_y = margin_top + line_h

    # Animation timings
    # Total animation ~ 2 seconds
    row_dur = 0.045
    row_delay_step = 0.038

    clip_paths = []
    text_elements = []
    cursor_elements = []

    for i, row_text in enumerate(ascii_rows):
        y = start_y + i * line_h
        delay = i * row_delay_step
        clip_id = f"rclip-{i}"

        # Clip path that wipes horizontally from left to right
        clip_paths.append(f'''    <clipPath id="{clip_id}">
      <rect x="{start_x - 4}" y="{y - line_h + 1}" width="0" height="{line_h + 1}">
        <animate attributeName="width" from="0" to="{content_width + 8}" dur="{row_dur}s" begin="{delay:.3f}s" fill="freeze" calcMode="linear" />
      </rect>
    </clipPath>''')

        # Escaped row text
        escaped_text = saxutils.escape(row_text)
        text_elements.append(f'    <text x="{start_x:.1f}" y="{y:.1f}" clip-path="url(#{clip_id})" class="ascii-line">{escaped_text}</text>')

        # Cursor sweeping across
        cursor_elements.append(f'''    <rect x="{start_x - 3}" y="{y - line_h + 1.5}" width="4" height="{line_h - 1}" fill="#58a6ff" opacity="0">
      <animate attributeName="x" from="{start_x - 3}" to="{start_x + content_width}" dur="{row_dur}s" begin="{delay:.3f}s" fill="freeze" calcMode="linear" />
      <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.05;0.95;1" dur="{row_dur}s" begin="{delay:.3f}s" fill="freeze" />
    </rect>''')

    total_anim_time = (num_rows - 1) * row_delay_step + row_dur
    last_y = start_y + (num_rows - 1) * line_h

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}" fill="none">
  <defs>
    <style>
      @keyframes blink {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0; }}
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
      .ascii-line {{
        font-family: 'SF Mono', 'Fira Code', 'Courier New', 'Consolas', monospace;
        font-size: {font_size}px;
        fill: #c9d1d9;
        font-weight: 500;
        white-space: pre;
      }}
      .blink-cursor {{
        animation: blink 1s step-start infinite;
      }}
    </style>
{chr(10).join(clip_paths)}
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
  <text x="{svg_width // 2}" y="20" text-anchor="middle" class="terminal-title">javier@github: ~/portrait.ascii</text>

  <!-- ASCII Rows -->
{chr(10).join(text_elements)}

  <!-- Animated Typing Cursors -->
{chr(10).join(cursor_elements)}

  <!-- Final Blinking Terminal Cursor -->
  <rect x="{start_x + content_width - 10}" y="{last_y - line_h + 1.5}" width="4" height="{line_h - 1}" fill="#58a6ff" class="blink-cursor" style="animation-delay: {total_anim_time:.2f}s;" />
</svg>'''

    with open(output_svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Generated {output_svg_path} successfully ({num_cols}x{num_rows} grid)!")

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
    out = sys.argv[2] if len(sys.argv) > 2 else "javier-ascii.svg"
    make_ascii_svg(src, out)
