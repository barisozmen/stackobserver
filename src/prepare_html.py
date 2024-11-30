

from pathlib import Path
import re
from bs4 import BeautifulSoup



import sys
print(Path(__file__).parent.parent)
sys.path.append(str(Path(__file__).parent.parent))

import fire
from helpers.utils import count_unclosed_divs, render_html, ColorAssigner
from helpers.metaclasses import Singleton



DEFAULT_INPUT_PATH = 'stacklines.unfinished.html'
DEFAULT_OUTPUT_PATH = 'stacklines.html'







def main(input_path = DEFAULT_INPUT_PATH, output_path = DEFAULT_OUTPUT_PATH):
    input_path = Path(input_path)
    output_path = Path(output_path)

    input_str = input_path.open('r', encoding='utf-8').read()
    input_str += "</div>"*count_unclosed_divs(input_str)


    # Step 1: Parse the HTML content
    soup = BeautifulSoup(input_str, "html.parser")

    # Step 2: Find all <div> elements with 'f_locals' attribute
    divs_with_f_locals = soup.find_all("div", attrs={"f_locals": True})

    # Step 3: Extract id and f_locals values
    info_from_lines = []
    for div in divs_with_f_locals:
        div_id = div.get("id", "no-id")  # Default to "no-id" if id is missing
        f_locals_value = div["f_locals"]
        f_lineno = div["f_lineno"]
        
        info_from_lines.append({"id": div_id, "f_locals": f_locals_value})
        
        if 'line' in div.get("class", ""):
            # add a new div inside the current div
            new_div = soup.new_tag("div")
            if 'f_code_co_filename' in div.attrs:
                new_div.string = div['f_code_co_filename'].split('/')[-1] + ':' + str(f_lineno)
            else:
                new_div.string = str(f_lineno)
            new_div.attrs['class'] = 'line_info'
            div.insert(0, new_div)
            
        if 'stack' in div.get("class", ""):
            filename = div['f_code_co_filename']
            color = ColorAssigner()(filename)
            
            div.attrs['style'] = f'background-color: whitesmoke; border: 0.1em solid rgba({color} 0.5); box-shadow: 0em 0.3em 0.8em rgba({color} 0.3), 0em 0.8em 2em rgba({color} 0.1);'


        style = """
        div, p, pre {{ margin: 0; padding: 0; }}
        pre {{
            display: flex;
            align-items: center;
            word-wrap: break-word;
        }}
        .rounded_container {{
            display: flex;
            align-items: left;
            gap: 0px;
            border-radius: 8px;
            border: 0.04em solid dimgray;
            color: #101010;
            padding-left: 0.4em; padding-right: 0.2em;
            padding-top: 0.1em; padding-bottom: 0.1em;
        }}
        .stack {{
            max-width: 800px;
            display: flex;
            flex-direction: column;
            gap: 0.2em;
            padding-left: 0.5em; padding-right: 0.5em;
            padding-top: 0.5em; padding-bottom: 0.5em;
            margin: 0.2em;
            margin-bottom: 0.4em;
            border-radius: 8px;
            
            # background-color: rgba(255, 182, 193, 0.3);
            
            # border: 0.1em solid dimgray;
            # box-shadow: 
            # 0em 0.3em 0.8em rgba(255, 182, 193, 0.8),
            # 0em 0.8em 2em rgba(255, 182, 193, 0.4);
        }}
        .header {{
            background-color: rgba(245, 245, 245, 0.5);  /* transparent whitesmoke */
        }}
        .line {{
            display: flex;
            flex-direction: row;
            align-items: left;
            gap: 0.4em;
            
            width: 100%;
            border-radius: 6px;
            # padding-left: 0.2em; padding-right: 0.2em;
            # padding-top: 0.2em; padding-bottom: 0.2em;
            margin: 0;
            padding: 0;
            
            color: dimgray;
        }}
        .line_info {{
            border-radius: 6px;
            border-top-right-radius: 0;
            border-bottom-right-radius: 0;
            border: 0.01em solid dimgray;
            # background-color: gainsboro;
            padding-left: 0.4em; padding-right: 0.4em;
            padding-top: 0.2em; padding-bottom: 0.2em;
            margin: 0;
        }}
        .line_info:hover {{
            cursor: pointer;
            background-color: lightgray;
        }}
        .line:hover {{
            cursor: pointer;
            background-color: gainsboro;
        }}
        """
        input_str = re.sub(r'class\s*=\s*"stack([^"]*)"', r'class="stack\1 rounded_container"', input_str)

        # find patterns such as `f_locals="<something>"` and get the <something> for each line, and print it
        divs_with_f_locals = []
        for line in input_str.split('\n'):
            if 'f_locals="' in line:
                f_locals = re.search(r'f_locals="([^"]*)"', line).group(1)
                print(f_locals)


        script = ''
        for f_locals in info_from_lines:
            script += f"""
            tippy('#{f_locals['id']}', {{
                content: "{f_locals['f_locals']}",
                placement: 'top',
                theme: 'light',
                interactive: true,
                allowHTML: true,
            }});
            """

        script = script.replace('{', '{{').replace('}', '}}')

        raw = (
            'html',
            ('head',
                ('title', 'Stack Observer Output'),
                '<link rel="stylesheet" href="https://unpkg.com/tippy.js@4/themes/light.css">',
            ),
            ('body', 
                ('style', style),
                "{INSERT_BODY}",
                '<script src="https://unpkg.com/@popperjs/core@2/dist/umd/popper.min.js"></script>',
                '<script src="https://unpkg.com/tippy.js@6/dist/tippy-bundle.umd.js"></script>',
                '<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>',
                ('script', script),)
        )

        rendered_html = render_html(raw).format(INSERT_BODY=soup.prettify())

        output_path.open('w', encoding='utf-8').write(rendered_html)



if __name__ == '__main__':
    fire.Fire(main)