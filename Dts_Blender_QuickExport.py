#!BPY

"""
Name: 'Torque Shape (.dts) Quick Export...'
Blender: 240
Group: 'Export'
Tooltip: 'Export to Torque (.dts) format.'
"""
'''
 Dts_Blender_QuickExport.py
 
 Copyright (c) 2006 Joseph Greenawalt (jsgreenawalt@gmail.com)
 
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

## @package Dts_Blender_QuickExport
# When run from the Blender scrips or file->export menu,
# this script calls the main entry point in Dts_Blender.py
# with a special 'quick' parameter that causes the exporter
# to skip the loading of the user interface and perform an
# immediate export.

import Dts_Blender
from Dts_Blender import *

entryPoint('quick')
