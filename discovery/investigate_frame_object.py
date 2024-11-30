import sys
from contextlib import ContextDecorator

# https://docs.python.org/3/reference/datamodel.html#frame-objects
# https://docs.python.org/3/reference/datamodel.html#code-objects 


def trace_fn(frame, event, arg):
    
    print('frame >', frame)
    print('type(frame) >', type(frame))
    print('event >', event)
    print('type(event) >', type(event))
    print('arg >', arg)
    print('type(arg) >', type(arg))
    print('\n'*2)
    
    print('frame dir >', dir(frame))
    print('\n'*2)
    

    for attr in ['f_lineno', 'f_globals', 'f_locals', 'f_back', 'f_trace', 'f_lasti', 'f_code']:
        print(f'frame.{attr}')
        print(f'    frame.{attr} >', frame.__getattribute__(attr))
        print('    type(frame.__getattribute__(attr)) >', type(frame.__getattribute__(attr)))
        print('\n')

    
    # https://docs.python.org/3/reference/datamodel.html#code-objects
    print(f'dir(frame.f_code) >', dir(frame.f_code))
    print('\n')
    
    for attr in ['co_name', 'co_qualname', 'co_filename', 'co_firstlineno', 'co_lnotab', 'co_stacksize', 'co_linetable', '_co_code_adaptive', 'co_positions']:
        print(f'frame.f_code.{attr}')
        print(f'    frame.f_code.{attr} >', frame.f_code.__getattribute__(attr))
        print('    type(frame.f_code.__getattribute__(attr)) >', type(frame.f_code.__getattribute__(attr)))
        print('\n')
    
    
    print('\n'*6)
    return trace_fn




class StackObserver(ContextDecorator):
    def __enter__(self):
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

    
