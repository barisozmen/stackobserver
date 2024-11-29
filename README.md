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

