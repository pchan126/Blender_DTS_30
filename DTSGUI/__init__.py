'''
__init__.py

Copyright (c) 2008 Joseph Greenawalt(jsgreenawalt@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

'''
	DTSPython Module Init Code
'''

#    Addon info
bl_info = {
    'name': 'DtsGUI',
    'author': 'Paul Jan',
    'location': 'File > Export > Export DTS',
    'category': 'File'
}

# To support reload properly, try to access a package var,
# if it's there, reload everything
if "bpy" in locals():
    import importlib

    importlib.reload(About)
    importlib.reload(DetailLevels)
    importlib.reload(DtsGUI)
    importlib.reload(General)
    importlib.reload(IFLAnim)
    importlib.reload(Materials)
    importlib.reload(Nodes)
    importlib.reload(SequenceBase)
    importlib.reload(SequenceOptions)
    importlib.reload(SequenceProperties)
    importlib.reload(ShapeOptions)
    importlib.reload(UserAnimBase)
    importlib.reload(VisAnim)
    print("Reloaded multifiles")
else:
    from .DtsGUI import *

    print("Imported multifiles")
