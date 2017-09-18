'''
ShapeOptions.py

Copyright (c) 2003 - 2008 James Urquhart(j_urquhart@btinternet.com)

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

import bpy
import Common_Gui
import DtsGlobals
import math
from DtsSceneInfo import *

'''
***************************************************************************************************
*
* Class that creates and owns the GUI controls on the Shape Options sub-panel.
*
***************************************************************************************************
'''


class ShapeOptionsControlsClass:
    def __init__(self, guiShapeOptionsSubtab):
        global globalEvents
        Prefs = DtsGlobals.Prefs

        # initialize GUI controls
        self.guiStripText = Common_Gui.SimpleText("guiStripText", "Geometry type:", None, self.guiStripTextResize)
        self.guiTriMeshesButton = Common_Gui.ToggleButton("guiTriMeshesButton", "Triangles",
                                                          "Generate individual triangles for meshes", 6,
                                                          self.handleGuiTriMeshesButtonEvent,
                                                          self.guiTriMeshesButtonResize)
        self.guiTriListsButton = Common_Gui.ToggleButton("guiTriListsButton", "Triangle Lists",
                                                         "Generate triangle lists for meshes", 7,
                                                         self.handleGuiTriListsButtonEvent,
                                                         self.guiTriListsButtonResize)
        self.guiStripMeshesButton = Common_Gui.ToggleButton("guiStripMeshesButton", "Triangle Strips",
                                                            "Generate triangle strips for meshes", 8,
                                                            self.handleGuiStripMeshesButtonEvent,
                                                            self.guiStripMeshesButtonResize)
        self.guiMaxStripSizeSlider = Common_Gui.NumberSlider("guiMaxStripSizeSlider", "Strip Size ",
                                                             "Maximum size of generated triangle strips", 9,
                                                             self.handleGuiMaxStripSizeSliderEvent,
                                                             self.guiMaxStripSizeSliderResize)
        # --
        # might get around to fixing this someday, probably not though, since it's not even implemented in TGEA (depricated)
        # self.guiClusterText = Common_Gui.SimpleText("guiClusterText", "Cluster Mesh", None, self.guiClusterTextResize)
        # self.guiClusterWriteDepth = Common_Gui.ToggleButton("guiClusterWriteDepth", "Write Depth ", "Always Write the Depth on Cluster meshes", 10, self.handleGuiClusterWriteDepthEvent, self.guiClusterWriteDepthResize)
        # self.guiClusterDepth = Common_Gui.NumberSlider("guiClusterDepth", "Depth", "Maximum depth Clusters meshes should be calculated to", 11, self.handleGuiClusterDepthEvent, self.guiClusterDepthResize)
        # --
        self.guiBillboardText = Common_Gui.SimpleText("guiBillboardText", "Auto-Billboard LOD:", None,
                                                      self.guiBillboardTextResize)
        self.guiBillboardButton = Common_Gui.ToggleButton("guiBillboardButton", "Enable",
                                                          "Add a billboard detail level to the shape", 12,
                                                          self.handleGuiBillboardButtonEvent,
                                                          self.guiBillboardButtonResize)
        self.guiBillboardEquator = Common_Gui.NumberPicker("guiBillboardEquator", "Equator",
                                                           "Number of images around the equator", 13,
                                                           self.handleGuiBillboardEquatorEvent,
                                                           self.guiBillboardEquatorResize)
        self.guiBillboardPolar = Common_Gui.NumberPicker("guiBillboardPolar", "Polar",
                                                         "Number of images around the polar", 14,
                                                         self.handleGuiBillboardPolarEvent,
                                                         self.guiBillboardPolarResize)
        self.guiBillboardPolarAngle = Common_Gui.NumberSlider("guiBillboardPolarAngle", "Polar Angle",
                                                              "Angle to take polar images at", 15,
                                                              self.handleGuiBillboardPolarAngleEvent,
                                                              self.guiBillboardPolarAngleResize)
        self.guiBillboardDim = Common_Gui.NumberPicker("guiBillboardDim", "Dim", "Dimensions of billboard images", 16,
                                                       self.handleGuiBillboardDimEvent, self.guiBillboardDimResize)
        self.guiBillboardPoles = Common_Gui.ToggleButton("guiBillboardPoles", "Poles", "Take images at the poles", 17,
                                                         self.handleGuiBillboardPolesEvent,
                                                         self.guiBillboardPolesResize)
        self.guiBillboardSize = Common_Gui.NumberSlider("guiBillboardSize", "Size", "Size of billboard's detail level",
                                                        18, self.handleGuiBillboardSizeEvent,
                                                        self.guiBillboardSizeResize)
        # --
        self.guiMiscText = Common_Gui.SimpleText("guiMiscText", "Miscellaneous:", None, self.guiMiscTextResize)
        self.guiScale = Common_Gui.NumberPicker("guiScale", "Export Scale", "Multiply output scale by this number", 26,
                                                self.handleGuiScaleEvent, self.guiScaleResize)

        # set initial states
        try:
            x = Prefs['PrimType']
        except KeyError:
            Prefs['PrimType'] = "Tris"
        if Prefs['PrimType'] == "Tris":
            self.guiTriMeshesButton.state = True
        else:
            self.guiTriMeshesButton.state = False
        if Prefs['PrimType'] == "TriLists":
            self.guiTriListsButton.state = True
        else:
            self.guiTriListsButton.state = False
        if Prefs['PrimType'] == "TriStrips":
            self.guiStripMeshesButton.state = True
        else:
            self.guiStripMeshesButton.state = False
        self.guiMaxStripSizeSlider.min, self.guiMaxStripSizeSlider.max = 3, 30
        self.guiMaxStripSizeSlider.value = Prefs['MaxStripSize']
        # self.guiClusterDepth.min, self.guiClusterDepth.max = 3, 30
        # self.guiClusterDepth.value = Prefs['ClusterDepth']
        # self.guiClusterWriteDepth.state = Prefs['AlwaysWriteDepth']
        self.guiBillboardButton.state = Prefs['Billboard']['Enabled']
        self.guiBillboardEquator.min, self.guiBillboardEquator.max = 2, 64
        self.guiBillboardEquator.value = Prefs['Billboard']['Equator']
        self.guiBillboardPolar.min, self.guiBillboardPolar.max = 3, 64
        self.guiBillboardPolar.value = Prefs['Billboard']['Polar']
        self.guiBillboardPolarAngle.min, self.guiBillboardPolarAngle.max = 0.0, 45.0
        self.guiBillboardPolarAngle.value = Prefs['Billboard']['PolarAngle']
        self.guiBillboardDim.min, self.guiBillboardDim.max = 16, 128
        self.guiBillboardDim.value = Prefs['Billboard']['Dim']
        self.guiBillboardPoles.state = Prefs['Billboard']['IncludePoles']
        self.guiBillboardSize.min, self.guiBillboardSize.max = 0.0, 128.0
        self.guiBillboardSize.value = Prefs['Billboard']['Size']

        self.guiScale.value = Prefs['ExportScale']
        self.guiScale.min = 0.001
        self.guiScale.max = 1000000.0

        # Hiding these for now, since cluster mesh sorting is still broken.
        # self.guiClusterText.visible = False
        # self.guiClusterWriteDepth.visible = False
        # self.guiClusterDepth.visible = False


        # add controls to containers
        guiShapeOptionsSubtab.addControl(self.guiStripText)
        guiShapeOptionsSubtab.addControl(self.guiTriMeshesButton)
        guiShapeOptionsSubtab.addControl(self.guiTriListsButton)
        guiShapeOptionsSubtab.addControl(self.guiStripMeshesButton)
        guiShapeOptionsSubtab.addControl(self.guiMaxStripSizeSlider)
        # guiShapeOptionsSubtab.addControl(self.guiClusterText)
        # guiShapeOptionsSubtab.addControl(self.guiClusterDepth)
        # guiShapeOptionsSubtab.addControl(self.guiClusterWriteDepth)
        guiShapeOptionsSubtab.addControl(self.guiBillboardText)
        guiShapeOptionsSubtab.addControl(self.guiBillboardButton)
        guiShapeOptionsSubtab.addControl(self.guiBillboardEquator)
        guiShapeOptionsSubtab.addControl(self.guiBillboardPolar)
        guiShapeOptionsSubtab.addControl(self.guiBillboardPolarAngle)
        guiShapeOptionsSubtab.addControl(self.guiBillboardDim)
        guiShapeOptionsSubtab.addControl(self.guiBillboardPoles)
        guiShapeOptionsSubtab.addControl(self.guiBillboardSize)
        guiShapeOptionsSubtab.addControl(self.guiMiscText)
        guiShapeOptionsSubtab.addControl(self.guiScale)

    def cleanup(self):
        '''
        Must destroy any GUI objects that are referenced in a non-global scope
        explicitly before interpreter shutdown to avoid the dreaded
        "error totblock" message when exiting Blender.
        Note: __del__ is not guaranteed to be called for objects that still
        exist when the interpreter exits.
        '''
        # initialize GUI controls
        del self.guiStripText
        del self.guiTriMeshesButton
        del self.guiTriListsButton
        del self.guiStripMeshesButton
        del self.guiMaxStripSizeSlider

        # --
        # del self.guiClusterText
        # del self.guiClusterWriteDepth
        # del self.guiClusterDepth
        del self.guiBillboardText
        del self.guiBillboardButton
        del self.guiBillboardEquator
        del self.guiBillboardPolar
        del self.guiBillboardPolarAngle
        del self.guiBillboardDim
        del self.guiBillboardPoles
        del self.guiBillboardSize
        # --
        del self.guiMiscText
        del self.guiScale

    def refreshAll(self):
        pass

    def handleGuiTriMeshesButtonEvent(self, control):
        Prefs = DtsGlobals.Prefs
        Prefs['PrimType'] = "Tris"
        self.guiTriListsButton.state = False
        self.guiStripMeshesButton.state = False
        self.guiTriMeshesButton.state = True

    def handleGuiTriListsButtonEvent(self, control):
        Prefs = DtsGlobals.Prefs
        Prefs['PrimType'] = "TriLists"
        self.guiTriListsButton.state = True
        self.guiStripMeshesButton.state = False
        self.guiTriMeshesButton.state = False

    def handleGuiStripMeshesButtonEvent(self, control):
        Prefs = DtsGlobals.Prefs
        Prefs['PrimType'] = "TriStrips"
        self.guiTriListsButton.state = False
        self.guiStripMeshesButton.state = True
        self.guiTriMeshesButton.state = False

    def handleGuiMaxStripSizeSliderEvent(self, control):
        Prefs = DtsGlobals.Prefs
        Prefs['MaxStripSize'] = control.value

    def handleGuiScaleEvent(self, control):
        Prefs = DtsGlobals.Prefs
        Prefs['ExportScale'] = control.value

    # def handleGuiClusterWriteDepthEvent(self, control):
    #	Prefs = DtsGlobals.Prefs
    #	Prefs['AlwaysWriteDepth'] = control.state
    # def handleGuiClusterDepthEvent(self, control):
    #	Prefs = DtsGlobals.Prefs
    #	Prefs['ClusterDepth'] = control.value
    def handleGuiBillboardButtonEvent(self, control):
        Prefs = DtsGlobals.Prefs
        Prefs['Billboard']['Enabled'] = control.state

    def handleGuiBillboardEquatorEvent(self, control):
        Prefs = DtsGlobals.Prefs
        Prefs['Billboard']['Equator'] = control.value

    def handleGuiBillboardPolarEvent(self, control):
        Prefs = DtsGlobals.Prefs
        Prefs['Billboard']['Polar'] = control.value

    def handleGuiBillboardPolarAngleEvent(self, control):
        Prefs = DtsGlobals.Prefs
        Prefs['Billboard']['PolarAngle'] = control.value

    def handleGuiBillboardDimEvent(self, control):
        Prefs = DtsGlobals.Prefs
        val = int(control.value)
        # need to constrain this to be a power of 2
        # it would be easier just to use a combo box, but this is more fun.
        # did the value go up or down?
        if control.value > Prefs['Billboard']['Dim']:
            # we go up
            val = int(2 ** math.ceil(math.log(control.value, 2)))
        elif control.value < Prefs['Billboard']['Dim']:
            # we go down
            val = int(2 ** math.floor(math.log(control.value, 2)))
        control.value = val
        Prefs['Billboard']['Dim'] = control.value

    def handleGuiBillboardPolesEvent(self, control):
        Prefs = DtsGlobals.Prefs
        Prefs['Billboard']['IncludePoles'] = control.state

    def handleGuiBillboardSizeEvent(self, control):
        Prefs = DtsGlobals.Prefs
        Prefs['Billboard']['Size'] = control.value

    def guiStripTextResize(self, control, newwidth, newheight):
        control.x, control.y = 10, newheight - 50

    def guiTriMeshesButtonResize(self, control, newwidth, newheight):
        control.x, control.y, control.width = 102, newheight - 60 - control.height, 90

    def guiTriListsButtonResize(self, control, newwidth, newheight):
        control.x, control.y, control.width = 10, newheight - 60 - control.height, 90

    def guiStripMeshesButtonResize(self, control, newwidth, newheight):
        control.x, control.y, control.width = 194, newheight - 60 - control.height, 90

    def guiMaxStripSizeSliderResize(self, control, newwidth, newheight):
        control.x, control.y, control.width = 286, newheight - 60 - control.height, 180

    # def guiClusterTextResize(self, control, newwidth, newheight):
    #	control.x, control.y = 10,newheight-70
    # def guiClusterWriteDepthResize(self, control, newwidth, newheight):
    #	control.x, control.y, control.width = 10,newheight-80-control.height, 80
    # def guiClusterDepthResize(self, control, newwidth, newheight):
    #	control.x, control.y, control.width = 92,newheight-80-control.height, 180
    def guiBillboardTextResize(self, control, newwidth, newheight):
        control.x, control.y = 10, newheight - 150

    def guiBillboardButtonResize(self, control, newwidth, newheight):
        control.x, control.y, control.width = 10, newheight - 160 - control.height, 50

    def guiBillboardEquatorResize(self, control, newwidth, newheight):
        control.x, control.y, control.width = 62, newheight - 160 - control.height, 100

    def guiBillboardPolarResize(self, control, newwidth, newheight):
        control.x, control.y, control.width = 62, newheight - 182 - control.height, 100

    def guiBillboardPolarAngleResize(self, control, newwidth, newheight):
        control.x, control.y, control.width = 164, newheight - 182 - control.height, 200

    def guiBillboardDimResize(self, control, newwidth, newheight):
        control.x, control.y, control.width = 366, newheight - 160 - control.height, 100

    def guiBillboardPolesResize(self, control, newwidth, newheight):
        control.x, control.y, control.width = 366, newheight - 182 - control.height, 100

    def guiBillboardSizeResize(self, control, newwidth, newheight):
        control.x, control.y, control.width = 164, newheight - 160 - control.height, 200

    def guiMiscTextResize(self, control, newwidth, newheight):
        control.x, control.y = 10, newheight - 250

    def guiScaleResize(self, control, newwidth, newheight):
        control.x, control.y, control.width = 10, newheight - 260 - control.height, 180
