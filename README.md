# stackobserver

<img width="683" height="1013" alt="image" src="https://github.com/user-attachments/assets/4f5752d9-fab4-44f9-bbcf-14d031cd4781" />


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


#### Intermediate Textual File Format
- start stack
- line
- line
- start stack
- line
- line
- line
- end stack
- end stack


#### View
example:
```html
<div id='<stack id>' class='stack' locals='' globals=''>
    <div class='line' filename='' funcname=''>x=1</div>
    <div class='stack'>
        <div class='line' filename='' funcname=''>y=2</div>
        <div class='line' filename='' funcname=''>z=3</div>
    </div>
</div>
```
