# stackobserver

## Design
Follow Unix philosophy:

[Rule of composition](http://www.catb.org/esr/writings/taoup/html/ch01s06.html#id2877684): Design programs to be connected with other programs 
- write in simple, textual, stream-oriented, device-independent formats
- use simple filters, get text and output text after processing it
  - otherwise it’s very difficult to hook the programs together

### Design Plan

stackobserver.py
- input > a python script
- output > text stream, where each line represents either a line or stack

htmlmaker.sh
- input > text stream (output of stackobserver.py)
- output > html file, where each line converted to divs of stacks or lines


#### Data Model
Line: represents each line run on the code
- unique by filename + line no
  
Stack: represents a frame (e.g. python frame)
- unique by frame id
- local var, global vars
- parent stack
- children stacks
- corresponding code region

CodeRegion: 
- unique by filename + function name

Stack includes Lines
CodeRegion includes Lines
Each Stack corresponds to a single CodeRegion
One CodeRegion can correspond to multiple Stacks


#### View
example:
```html
<div id='<stack id>' class='stack' locals='' globals=''>
    <div class='line'>x=1</div>
    <div class='stack'>
        <div class='line'>y=2</div>
        <div class='line'>z=3</div>
    </div>
</div>
```
