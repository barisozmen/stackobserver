import sys
from contextlib import ContextDecorator
import linecache
from pathlib import Path
from singletons import Counter
# https://docs.python.org/3/reference/datamodel.html#frame-objects
# https://docs.python.org/3/reference/datamodel.html#code-objects 

OUTPUT_PATH = Path('stacklines.unfinished.html')

def output(text):
    OUTPUT_PATH.open('a', encoding='utf-8').write(text + '\n')





def trace_fn(frame, event, arg):
    line_id = 'line_' + str(Counter().next_id)

    if event == 'call':
        output(f"""<div class="stack"
                    f_lineno="{frame.f_lineno}"
                    f_globals="{frame.f_globals}"
                    f_locals="{frame.f_locals}"
                    f_code_co_name="{frame.f_code.co_name}"
                    f_code_co_filename="{frame.f_code.co_filename}"
                    f_code_co_stacksize="{frame.f_code.co_stacksize}"
              >
              <div class="header line" id="{line_id}" f_code_co_filename="{frame.f_code.co_filename}" f_lineno="{frame.f_lineno}" f_locals="{frame.f_locals}">
                <pre>{linecache.getline(frame.f_code.co_filename, frame.f_lineno).rstrip()}</pre>
              </div>
              """)

    elif event == 'return':
        output(f"""
        <div class="return" id="{line_id}" f_lineno="{frame.f_lineno}" f_locals="{frame.f_locals}">
            # return
        </div>
        </div>""")

    elif event == 'line':
        output(f"""
        <div class="line" id="{line_id}" f_code_co_filename="{frame.f_code.co_filename}" f_lineno="{frame.f_lineno}" f_locals="{frame.f_locals}">
            <pre>{linecache.getline(frame.f_code.co_filename, frame.f_lineno).rstrip()}</pre>
        </div>
        """)

    else:
        raise ValueError(f'Unknown event: {event}')

    return trace_fn



class StackObserver(ContextDecorator):
    def __enter__(self):
        OUTPUT_PATH.unlink(missing_ok=True)
        sys.settrace(trace_fn)
        return self

    def __exit__(self, *exc):
        sys.settrace(None)
        return False
    
    
    


def add_one(x):
    return x+1
    
def fn3():
    pass
    
def fn2():
    fn3()
    
def fn1():
    fn2()
    
def foo():
    print('hello')
    print('world')
    x=1
    y = add_one(x)
    z = x+y
    fn1()
    a=1


with StackObserver():
    foo()