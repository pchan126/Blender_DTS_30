'''
__init__.py

Copyright (c) 2004 - 2006 James Urquhart(j_urquhart@btinternet.com)

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
    'name': 'DtsPython',
    'author': 'Paul Jan',
    'location': 'File > Export > Export DTS',
    'category': 'File'
}

# To support reload properly, try to access a package var,
# if it's there, reload everything
if "bpy" in locals():
    import importlib

    importlib.reload(Dts_mesh)
    importlib.reload(Dts_Shape)
    importlib.reload(Dts_Stream)
    importlib.reload(Dts_Stripper)
    importlib.reload(Dts_Test)
    importlib.reload(Dts_TranslucentSort)
    importlib.reload(Nv_TriStrip)
    importlib.reload(Nv_TriStripObjects)
    importlib.reload(Nv_VertexCache)
    importlib.reload(pyBisect)
    importlib.reload(QADTriStripper)
    importlib.reload(Stripper_VTK)
    importlib.reload(Torque_Math)
    importlib.reload(Torque_Utils)
    print("Reloaded multifiles")
else:
    from .Torque_Util import *
    from .Dts_Stream import *
    from .Dts_Stripper import *
    from .Dts_Mesh import *
    from .Dts_TranslucentSort import *
    from .Dts_Shape import *
    from .pyBisect import *
    print("Imported multifiles")



