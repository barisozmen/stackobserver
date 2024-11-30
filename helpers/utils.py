from helpers.metaclasses import Singleton


# Convert X11/CSS color names to RGBA format
frame_color_list = [
    '220, 20, 60,',    # Crimson
    '75, 0, 130,',     # Indigo
    '173, 216, 230,',  # LightBlue
    '240, 128, 128,',  # LightCoral
    '250, 128, 114,',  # Salmon
    '255, 255, 240,',  # Ivory
    '230, 230, 250,',  # Lavender
    '106, 90, 205,',   # SlateBlue
    '255, 165, 0,',    # Orange
    '175, 238, 238,',  # PaleTurquoise
    '221, 160, 221,',  # Plum
    '216, 191, 216,',  # Thistle
    '102, 205, 170,',  # MediumAquamarine
    '152, 251, 152,',  # PaleGreen
    '188, 143, 143,',  # RosyBrown
    '240, 230, 140,',  # Khaki
    '147, 112, 219,',  # MediumPurple
    '255, 218, 185,',  # PeachPuff
    '95, 158, 160,',   # CadetBlue
    '32, 178, 170,',   # LightSeaGreen
    '244, 164, 96,',   # SandyBrown
    '143, 188, 143,',  # DarkSeaGreen
    '176, 196, 222,',  # LightSteelBlue
    '176, 224, 230,',  # PowderBlue
]

class ColorAssigner(metaclass=Singleton):
    def __init__(self):
        self.assigned_colors = {}
        self.color_index = 0

    def __call__(self, name):
        if name in self.assigned_colors:
            return self.assigned_colors[name]
        color = frame_color_list[self.color_index]
        self.color_index = (self.color_index + 1) % len(frame_color_list)
        self.assigned_colors[name] = color
        return color


def count_unclosed_divs(input_str):
    return input_str.count('<div') - input_str.count('</div')

self_closing_tags = ['img', 'br', 'link', 'meta']

def render_html(raw, indent=0):
      # print('raw>',raw)
    if raw is None: return
    splitted = raw[0].split(maxsplit=1)
    tag, attributes = splitted if len(splitted)>1 else (splitted[0], '')
    html = '\t'*indent + (f'<{tag} {attributes}>\n' if len(attributes) else f'<{tag}>\n')
    for c in raw[1:]:
        if isinstance(c, str):
            html += '\t'*(indent+1) + c + '\n'
        else:
            html += render_html(c, indent+1)
    html += '\t'*indent + ('/>' if tag in self_closing_tags else f'</{tag}>') + '\n'
    return html