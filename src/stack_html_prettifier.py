from pathlib import Path
import re
from bs4 import BeautifulSoup
import subprocess

import sys
sys.path.append(str(Path(__file__).parent.parent))

import fire
from helpers.utils import count_unclosed_divs, render_html, ColorAssigner
from helpers.metaclasses import Singleton

from src.stack_observer import PathDecider
from src.static import scrollbar_style



DATA_TIPPY_CONTENT = 'data-tippy-content'
UNEMPHASIZED_STACK_OPACITY = '0.2'


# TODO: highlight the code line in code_from_file that shows the start of the corresponding stack.
# TODO: make the code_from_file scrollable up as well, and start the scroll top on the line that shows the start of the corresponding stack.

# Use html2canvas to save the page as an image. Use it as snapshot of your code, and also for scroll preview.

stack_styles = {}


def remove_js_comments(js):
    # remove all parts in between /* and */
    js = re.sub(r'/\*.*?\*/', '', js, flags=re.DOTALL)
    # remove all lines that start with //
    js = re.sub(r'//.*?\n', '', js, flags=re.DOTALL)
    return js

def prettify_html(input_str):
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
            line_info_div = soup.new_tag("div")
            if 'f_code_co_filename' in div.attrs:
                line_info_div.string = div['f_code_co_filename'].split('/')[-1] + ':' + str(f_lineno)
                line_info_div.attrs['data-tippy-content'] = div['f_code_co_filename']
            else:
                line_info_div.string = str(f_lineno)
            line_info_div.attrs['class'] = 'line_info'
            
            div.insert(0, line_info_div)
            
            div.attrs[DATA_TIPPY_CONTENT] = 'locals: ' + str(f_locals_value)
            
            if 'literal_locals' in div.attrs and (pre_tag := div.find('pre')):
                # add literal_locals to pre child of div
                literal_locals_div = soup.new_tag('div', attrs={'class': 'literal_locals'})
                literal_locals_div.string = div['literal_locals']
                pre_tag.append(literal_locals_div)

            
        if 'stack' in div.get("class", ""):
            stack_key = div['stack_key']
            filename = div['f_code_co_filename']
            color = ColorAssigner()(stack_key)
            
            grayish = '189, 183, 107'
            
            
            from_python_lib = ('python' in filename and 'lib' in filename) or 'site-packages' in filename or filename.split('/')[-1].startswith('<')
            
            if from_python_lib:
                background_color = f'rgba(255, 255, 255, 1.0)'
                border = '0.2em solid silver'
            else:
                background_color = f'rgba({color} 1.0)'
                border = '0.2em solid dimgray'
        
            # div.attrs['style'] = f'background-color: rgba({color} 0.8); border: 0.1em solid rgba({color} 0.5); box-shadow: 0em 0.3em 0.8em rgba({grayish} 0.3), 0em 0.8em 2em rgba({grayish} 0.1);'
            div.attrs['style'] = f'background-color: {background_color}; border: {border};'
            
            stack_styles[stack_key] = div.attrs['style']
            
            # for children '.code_from_file' divs, add the style
            for code_from_file in div.find_all('div', attrs={'class': 'code_from_file'}):
                code_from_file.attrs['style'] = div.attrs['style']
            

        if 'line_run_counter' in div.attrs:
            run_counter_div = soup.new_tag('div')
            run_counter_div.string = 'x' + str(div['line_run_counter'])
            run_counter_div.attrs['class'] = 'line_run_counter'
            div.append(run_counter_div)
            
    
    
    # make stack_names list for stacks
    for div in soup.find_all('div', attrs={'stack_names': True}):
        
        stack_names_html = ''
        for name in div['stack_names'].split('\n'):
            if name in stack_styles:
                stack_names_html += f'<div style="{stack_styles[name]} color: black; border-radius: 4px; border-width: 0.1em;">{name}</div>'
            else:
                stack_names_html += f'<div>{name}</div>'
        
        div.attrs[DATA_TIPPY_CONTENT] = stack_names_html
    
    
    # for pre in soup.find_all('pre'):
    #     if 'class' in pre.attrs:
    #         pre.attrs['class'] = pre.attrs['class'] + ' prettyprint'
    #     else:
    #         pre.attrs['class'] = 'prettyprint'

    style = """
    div, p, pre { margin: 0; padding: 0; }
    body {
        display: flex;
        flex-direction: column;
        align-items: left;
        overflow-y: scroll;
    }
    """+scrollbar_style+"""
    pre {
        width: 100%;
        display: flex;
        align-items: center;
        word-wrap: break-word;
        border-radius: 4px;
        padding-left: 0.4em;
    }
    .line pre {
        background-color: rgba(255, 255, 255, 0.6);
    }
    
    .rounded_container {
        display: flex;
        align-items: left;
        gap: 0px;
        border-radius: 8px;
        border: 0.04em solid dimgray;
        color: #101010;
        padding: 0.1em 0.2em 0.1em 0.4em;
    }
    .stack {
        max-width: 700px; min-width: 700px;
        display: flex;
        flex-direction: column;
        gap: 0.2em;
        //padding: 0.5em 0.5em 0.5em 0.5em;
        padding-left: 0.7em; padding-top: 0.7em; padding-bottom: 0.7em;
        margin: 0.2em;
        margin-bottom: 0.4em;
        border-radius: 8px;
        
        background-color: rgba(255, 182, 193, 0.3);
        
        border: 0.1em solid dimgray;
        //box-shadow: 
        //0em 0.3em 0.8em rgba(255, 182, 193, 0.8),
        //0em 0.8em 2em rgba(255, 182, 193, 0.4);
    }
    .stack_header {
        color: black;
        display: flex; flex-direction: row; 
        align-items: right;
        justify-content: right;
        gap: 0.4em;
        background-color: transparent;
        padding: 0.2em 0.4em 0.8em 0.4em;
    }
    .stack_header_element {
        background-color: rgba(255, 255, 255, 0.7);
        border-radius: 6px;
        color: black;
        padding: 0.2em 0.4em 0.2em 0.4em;
    }
    .code_from_file {
        display: none;
        position: absolute;
        top: 0px;  /* Position it below the parent */
        left: 100%;
        min-width: 300px;  /* Give it a reasonable minimum width */
        max-width: 600px;  /* Limit maximum width */
        
        padding: 1em;
        
        color: white;
        border-radius: 8px;
        z-index: 1000;  /* Ensure it appears above other elements */
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    .code_from_file pre code {
        border-radius: 8px;
        max-height: 780px;
        
        /* Add these properties for scrolling */
        overflow-y: scroll;
    }
    .stack_key {
        position: relative;
        margin-right: auto;
        font-size: 1.1em;
        padding: 0.3em 0.5em 0.3em 0.5em;
    }
    .header {
        // background-color: rgba(245, 245, 245, 0.1);  /* transparent whitesmoke */
    }
    .line {
        display: flex;
        flex-direction: row;
        align-items: left;
        gap: 0.8em;
        
        width: 100%;
        border-radius: 6px;
        # padding-left: 0.2em; padding-right: 0.2em;
        # padding-top: 0.2em; padding-bottom: 0.2em;
        margin: 0;
        padding: 0;
        
        color: black;
    }
    .literal_locals {
        color: rgba(0, 0, 0, 0.4);
        text-align: right;
    }
    .line_info {
        border-radius: 6px;
        border-top-right-radius: 0;
        border-bottom-right-radius: 0;
        border: 0.01em solid dimgray;
        padding: 0.2em 0.4em 0.2em 0.4em;
        margin: 0;
        
        color: black;
    }
    .line_info:hover {
        cursor: pointer;
        background-color: lightgray;
    }
    .line_run_counter {
        border-radius: 6px;
        background-color: gainsboro;
        border: 0.05em solid lightgray;
        padding: 0.1em 0.2em 0.1em 0.2em;
        color: black;
        align-self: flex-end;
        margin-left: auto;
    }
    .line:hover {
        cursor: pointer;
        background-color: rgba(0, 0, 0, 0.2);  /* semi-transparent black overlay */
    }
    .tippy-content {
        white-space: pre-wrap;      /* Preserves whitespace and wraps */
        word-wrap: break-word;      /* Breaks long words */
        overflow-wrap: break-word;  /* Modern version of word-wrap */
        max-width: 100%;           /* Ensures content doesn't overflow */
        line-height: 1.4;          /* Improves readability */
    }
    """
    input_str = re.sub(r'class\s*=\s*"stack([^"]*)"', r'class="stack\1 rounded_container"', input_str)


    script = ''
    
    script += """
    tippy('["""+DATA_TIPPY_CONTENT+"""]', {
        allowHTML: true,
        theme: 'light',
        placement: 'right',
        interactive: true,
        // Add these for text wrapping:
        animation: 'fade',
        inlinePositioning: true,
    });
    """
    
    # hover all line_key:xxx divs together
    script += """
    console.log('jQuery version:', $.fn.jquery);  // Verify jQuery is loaded
    $(document).ready(function () {
        console.log('Number of .line elements:', $('.line').length);  // Check if elements exist
        $('.line').each(function() {
            console.log('line_key:', $(this).attr('line_key'));  // Check line_key values
        });
        // Using event delegation for better performance
        $(document).on({
            mouseenter: function() {
                const lineKey = $(this).attr('line_key');
                if (lineKey) {  // Only proceed if line_key exists
                    $('.line[line_key="' + lineKey + '"]').addClass('hovered');
                }
            },
            mouseleave: function() {
                const lineKey = $(this).attr('line_key');
                if (lineKey) {  // Only proceed if line_key exists
                    $('.line[line_key="' + lineKey + '"]').removeClass('hovered');
                }
            }
        }, '.line');
    });
    """

    
    # Add stack click handler with jquery
    script += """
    $(document).ready(function () {
        $('.stack').click(function(e) {
            // Only proceed if this is the actual clicked element, not a parent stack
            if (e.target.closest('.stack') === this) {
                console.log('stack clicked', $(this).attr('stack_key'));
                console.log('window.clicked_stack_id', window.clicked_stack_id);
                
                if (window.clicked_stack_id) {
                    // reset the opacity of all stacks
                    $('.stack').css('opacity', '1');
                    window.clicked_stack_id = null;
                }
                else {
                    // get all the .stack children of this stack
                    const stack_children = $(this).find('.stack');
                    
                    // make opacity 0.1 of all stack children
                    stack_children.css('opacity', '"""+UNEMPHASIZED_STACK_OPACITY+"""');
                    
                    // keep id of the clicked stack on the window global variable
                    window.clicked_stack_id = $(this).attr('id');
                }
                
            }
            e.stopPropagation();  // Prevent event from bubbling to parent stacks
        });
        
        // add a click handler to the body to reset the opacity of all stack children when the body is clicked
        $('body').click(function() {
            console.log('body clicked');
            // if the click is not on a stack, so reset the opacity of all stack children
            if (window.clicked_stack_id) {
                $('.stack').css('opacity', '1');
                window.clicked_stack_id = null;
            }
        });
    });
    """
    
    # With jquery, find all line string parts that are calling the next stack, and highlight them
    script += """
    $(document).ready(function () {
        $('.stack').each(function() {
            const stack_key = $(this).attr('stack_key');
            const stack_color = $(this).css('background-color');
            // get the sibling line just before the stack
            const calling_line = $(this).prev('.line');
            if (!calling_line.length) {
                return;
            }
            console.log('calling_line', calling_line);
            
            const stackFunctionName = stack_key.split(' ').at(-1);
            
            // in the string of the calling line, find the part that matches the stackFunctionName, and highlight it
            const pre_tag = calling_line.find('pre');
            if (!pre_tag.length) {
                return;
            }
            
            // highlight the entire function call pattern: functionName(args)
            const regex = new RegExp(`${stackFunctionName}\\([^)]*\\)+`, 'g');
            pre_tag[0].innerHTML = pre_tag[0].innerHTML.replace(regex, `<span style="background-color: ${stack_color}">$&</span>`);
        });
    });
    """
    
    # show the code_from_file divs when hovering over the stack_key divs
    script += """
    $(document).ready(function () {
        $('.stack_key').hover(
            function() {  // mouseenter
                console.log('mouseenter to .stack_key');
                $(this).find('.code_from_file').show();
            },
            function() {  // mouseleave
                console.log('mouseleave from .stack_key');
                $(this).find('.code_from_file').hide();
            }
        );
    });
    """
    
    # add class="language-python" for all python code
    for stack_div in soup.find_all('div', attrs={'stack_key': True}):
        if '.py' in stack_div['stack_key']:
            for code in stack_div.find_all('code'):
                if 'class' in code.attrs:
                    code.attrs['class'] = code.attrs['class'] + ' language-python'
                else:
                    code.attrs['class'] = 'language-python'
    
    
    
    # https://highlightjs.org/
    highlight_js = """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/atom-one-dark.min.css">

        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/languages/python.min.js"></script>
        <script>hljs.highlightAll();</script>
        """


    raw = (
        'html',
        ('head',
            ('title', 'Stack Observer Output'),
            '<link rel="stylesheet" href="https://unpkg.com/tippy.js@4/themes/light.css">',
            highlight_js,
        ),
        ('body', 
            ('style', style),
            soup.prettify(),
            '<script src="https://unpkg.com/@popperjs/core@2/dist/umd/popper.min.js"></script>',
            '<script src="https://unpkg.com/tippy.js@6/dist/tippy-bundle.umd.js"></script>',
            '<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>',
            ('script', script),
        )
    )
    return render_html(raw)



def io(file_path):
    path_decider = PathDecider(file_path)
        
    input_str = path_decider.intermediate_path.open('r', encoding='utf-8').read()
    
    print('Html Prettifier read intermediate html from >>', path_decider.intermediate_path)
    
    output_str = prettify_html(input_str)
    
    path_decider.last_html_path.open('w', encoding='utf-8').write(output_str)
    
    print('Html Prettifier wrote prettified html to >>', path_decider.last_html_path)
    
    # open the html file in the browser
    subprocess.run(['open', str(path_decider.last_html_path)])
    
    print('Html Prettifier opened the html file in the browser >>', path_decider.last_html_path)



if __name__ == '__main__':
    fire.Fire(io)