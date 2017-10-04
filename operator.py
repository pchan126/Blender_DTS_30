# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
)

from . import DtsGlobals
from .DtsShape_Blender import *

def doExport(context, filePath, config):
    from .DtsPrefs import prefsClass
    if DtsGlobals.Prefs is not None:
        Prefs = DtsGlobals.Prefs
    else:
        Prefs = prefsClass()

    SceneInfo = DtsGlobals.SceneInfo
    Shape = BlenderShape(Prefs)
    #         # Scene.GetCurrent().getRenderingContext().currentFrame(Prefs['RestFrame'])
    #        bpy.context.scene.frame_set(Prefs['RestFrame'])
    #         # try:
    #         # double check the base path before opening the stream
    #         if not os.path.exists(Prefs['exportBasepath']):
    #             Prefs['exportBasepath'] = SceneInfoClass.getDefaultBasePath()
    #         # double check the file name
    #         if Prefs['exportBasename'] == "":
    #             Prefs['exportBasename'] = SceneInfoClass.getDefaultBaseName()
    #
    #         # make sure our path Separator is correct.
    #         pathSeparator = SceneInfoClass.getPathSeparator()
    #         # getPathSeparator(Prefs['exportBasepath'])
    from .DTSPython import DtsStream
    from .DTSPython import Torque_Util
    Stream = DtsStream(filePath)
    Torque_Util.dump_writeln(
        "Writing shape to  '%s'." % (filePath))
    # Now, start the shape export process if the Stream loaded
    if Stream.fs:
        Torque_Util.dump_writeln("Processing...")

        # Import objects

        '''
        This part of the routine is split up into 4 sections:

        1) Get armatures and add them.
        2) Add every single thing from the base details that isn't an armature or special object.
        3) Add the autobillboard detail, if required.
        4) Add every single collision mesh we can find.
        '''
        # progressBar.pushTask("Importing Objects...", len(self.children), 0.4)
        #             progressBar.pushTask("Importing Objects...", 1, 0.4)
        #
        # set the rest frame, this should be user-selectable in the future.
        bpy.context.scene.frame_set(Prefs['RestFrame'])

        # add all nodes
        Shape.addAllNodes()

        # add visible detail levels
        sortedObjectNIs = SceneInfo.getSortedDtsObjectNames()
        if len(SceneInfo.DTSObjects) != len(sortedObjectNIs):
            print("sortedObjectNIs=", sortedObjectNIs)
            print("PANIC!!!! This should never hapen!")

        Shape.addAllDetailLevels(SceneInfo.DTSObjects, sortedObjectNIs)

        # We have finished adding the regular detail levels. Now add the billboard if required.
        if Prefs['Billboard']['Enabled']:
            Shape.addBillboardDetailLevel(0,
                                          Prefs['Billboard']['Equator'],
                                          Prefs['Billboard']['Polar'],
                                          Prefs['Billboard']['PolarAngle'],
                                          Prefs['Billboard']['Dim'],
                                          Prefs['Billboard']['IncludePoles'],
                                          Prefs['Billboard']['Size'])

        # progressBar.update()
        # progressBar.popTask()

        # Finalize static meshes, do triangle strips
        # progressBar.pushTask("Finalizing Geometry...", 2, 0.6)
        Shape.finalizeObjects()
        Shape.finalizeMaterials()
        # progressBar.update()
        if Prefs['PrimType'] == "TriStrips":
            Shape.stripMeshes(Prefs['MaxStripSize'])
        # progressBar.update()

        # Add all actions (will ignore ones not belonging to shape)
        scene = bpy.context.scene
        render = scene.render
        #           actions  = Armature.NLA.GetActions()

        if scene.sequence_editor is not None:
            actions = scene.sequence_editor.sequences_all

        # check the armatures to see if any are locked in rest position
        # for armOb in scene .objects:
        #     if (armOb.type != 'ARMATURE'): continue
        #     if armOb.data.restPosition:
        #         # this popup was too long and annoying, let the standard warning/error popup handle it.
        #         # Blender.Draw.PupMenu("Warning%t|One or more of your armatures is locked into rest position. This will cause problems with exported animations.")
        #         Torque_Util.dump_writeWarning(
        #             "Warning: One or more of your armatures is locked into rest position.\n This will cause problems with exported animations.")
        #         break

        # Process sequences
        seqKeys = list(Prefs['Sequences'].keys())
        if len(seqKeys) > 0:
            progressBar.pushTask("Adding Sequences...", len(seqKeys * 4), 0.8)
            for seqName in seqKeys:
                Torque_Util.dump_writeln("   Loading sequence '%s'..." % seqName)

                seqKey = Prefs['Sequences'][seqName]

                # does the sequence have anything to export?
                if (seqKey[
                        'NoExport']):  # or not (seqKey['Action']['Enabled'] or seqKey['IFL']['Enabled'] or seqKey['Vis']['Enabled']):
                    # progressBar.update()
                    # progressBar.update()
                    # progressBar.update()
                    # progressBar.update()
                    continue

                # try to add the sequence
                try:
                    action = actions[seqName]
                except:
                    action = None
                sequence = Shape.addSequence(seqName, seqKey, scene, action)
                if sequence == None:
                    Torque_Util.dump_writeWarning("Warning : Couldn't add sequence '%s' to shape!" % seqName)
                    # progressBar.update()
                    # progressBar.update()
                    # progressBar.update()
                    # progressBar.update()
                    continue
                # progressBar.update()

                # Pull the triggers
                if len(seqKey['Triggers']) != 0:
                    Shape.addSequenceTriggers(sequence, seqKey['Triggers'], getSeqNumFrames(seqName, seqKey))
                progressBar.update()
                progressBar.update()

                # Hey you, DSQ!
                if seqKey['Dsq']:
                    Shape.convertAndDumpSequenceToDSQ(sequence, "%s/%s.dsq" % (Prefs['exportBasepath'], seqName),
                                                      Stream.DTSVersion)
                    Torque_Util.dump_writeln("   Loaded and dumped sequence '%s' to '%s/%s.dsq'." % (
                        seqName, Prefs['exportBasepath'], seqName))
                else:
                    Torque_Util.dump_writeln("   Loaded sequence '%s'." % seqName)

                # Clear out matters if we don't need them
                if not sequence.has_loc: sequence.matters_translation = []
                if not sequence.has_rot: sequence.matters_rotation = []
                if not sequence.has_scale: sequence.matters_scale = []
                # progressBar.update()

                # progressBar.popTask()

        # ***** NOTE **********************************************************************************************
        #
        # Here's the low-down on this error/warning:
        #
        # As of Blender 2.47 (and probably earlier versions as well), Blender calculates vertex displacement
        #  for skinned meshes according to bone transform deltas in *Armature Space*.  Torque calculates its
        #  vertex displacements in *world space*.
        #
        # What does this mean?  I'm getting to that...
        #
        # Consider the following scenario:
        #
        #  An armature is rotated 360 degrees in a cyclic animation.  A single bone contained within the
        #  armature is rotated 360 degrees in the opposite direction.  The two rotations nearly cancel
        #  each other out, with just a bit of wobble.
        #
        #  Two meshes are skinned to the single bone contained within the armature; one using Blender's
        #  "Armature parent deform" (implicit armature modifier), and the other one using an explicit armature
        #  modifier (not parented to the armature object).
        #
        #  When the animation is played back in Blender, the mesh with armature parent deform will appear to
        #  wobble somewhat, but will not rotate significantly.  The rotation of the bone in *armature space*
        #  is counteracted by the rotation of the parent armature object.
        #
        #  The mesh with the explicit armature modifier that is not parented to the armature object will go
        #  through a full 360 degree rotation during the animation (when played back in Blender); even though
        #  the bone to which the mesh is skinned appears (mostly) stationary in world space!
        #
        #  When such an animation is exported to the dts file format, both meshes will appear to wobble
        #  slightly, but neither will rotate!
        #
        # The Bottom line:
        #
        #  In a sense, the results as displayed within Blender are counter-intuitive.  One would expect that
        #  Blender should calculate the skinning for a skinned mesh without an armature parent in *world space*,
        #  not in the armature's local space.  This weird behavior does have some possible uses within Blender,
        #  so I can't really say that this is a "bug" :-)
        #
        #  The bad news is that there is no practical way to reproduce the effect of the one "spinning" cube in
        #  the dts file format.  The only way that I can think of that it could conceivably be done would be to
        #  duplicate all of the bones in an armature for every skinned mesh, and set/animate the bones in
        #  worldspace as if they were in the armature's local space (throwing out or ignoring the parent
        #  armature's explicit and implicit rotations).  This approach would be way too messy to implement
        #  and the potential explosion in node count could kill performance if more than one skinned mesh is
        #  present.
        #
        #  Instead, the exporter just warns the user that animations may be screwy if an armature modifier is
        #  used with an implicitly or explicitly animated armature object which is not the direct parent of the
        #  skinned Blender mesh.
        #
        # *********************************************************************************************************
        # Issue warnings for all meshes that have an armature modifier, but no armature parent iff armature *object*
        # is animated.
        warnList = DtsGlobals.SceneInfo.getWarnMeshes(Shape.badArmatures)
        for warn in warnList:
            Torque_Util.dump_writeln("  ****************************************************************************")
            Torque_Util.dump_writeErr(
                "  Error: Skinned mesh \"" + warn[0] + "\" without armature parent has an armature")
            Torque_Util.dump_writeln("   modifier target object (" + warn[1] + ") which is animated!")
            Torque_Util.dump_writeln("    This mesh will probably be mangled.  The problem can be corrected by")
            Torque_Util.dump_writeln("    parenting the mesh to the armature, by using armature parent deform")
            Torque_Util.dump_writeln("    instead of an explicit armature modifier, or by removing the object level")
            Torque_Util.dump_writeln("    animation from the armature (bone animation is OK).")
            Torque_Util.dump_writeln(
                "    See: http://jsgreenawalt.com/documentation/troubleshooting/errors-and-warnings/skinned-mesh-modifier-prob.html")
            Torque_Util.dump_writeln("    for more information.")
            Torque_Util.dump_writeln("  ****************************************************************************")

        Torque_Util.dump_writeln("> Shape Details")
        Shape.dumpShapeInfo()
        # progressBar.update()
        # progressBar.popTask()

        # Now we've finished, we can save shape and burn it.
        # progressBar.pushTask("Writing out DTS...", 1, 0.9)
        Torque_Util.dump_writeln("Writing out DTS...")
        Shape.finalize(Prefs['WriteShapeScript'])
        Shape.write(Stream)
        Torque_Util.dump_writeln("Done.")
        # progressBar.update()
        # progressBar.popTask()

        Stream.closeStream()
        del Stream
        del Shape
    else:
        Torque_Util.dump_writeErr("Error: failed to open shape stream! (try restarting Blender)")
        del Shape
        # progressBar.popTask()
        return None
    '''
    except Exception, msg:
        Torque_Util.dump_writeErr("Error: Exception encountered, bailing out.")
        Torque_Util.dump_writeln(Exception)
        if tracebackImported:
            print "Dumping traceback to log..."
            Torque_Util.dump_writeln(traceback.format_exc())
        Torque_Util.dump_setout("stdout")
        if self.Shape: del self.Shape
        progressBar.popTask()
        raise
    '''

    #
    #
    #     '''
    #         Functions to export shape and load script
    #     '''
    #
    #
    # -------------------------------------------------------------------------------------------------
def handleScene(issueWarnings=False):
    Prefs = DtsGlobals.Prefs
    DtsGlobals.SceneInfo = SceneInfoClass(Prefs)
    SceneInfo = DtsGlobals.SceneInfo
    # if SceneInfo != None: SceneInfo.clear()


    # Torque_Util.dump_writeln("Processing Scene...")
    # What we do here is clear any existing export tree, then create a brand new one.
    # This is useful if things have changed.
    scn = bpy.context.scene
    scn.update()
    # updateOldPrefs()
    # Torque_Util.dump_writeln("Cleaning Preference Keys")
    # cleanKeys()
    # createActionKeys()

    SceneInfo.refreshAll(issueWarnings)

    #
    #
    #     # Prefs.refreshSequencePrefs()
    #     # Prefs.refreshMaterialPrefs()
    #
    #     def export():
    #         SceneInfo = DtsGlobals.SceneInfo
    #         Prefs = DtsGlobals.Prefs
    #         pathSeparator = SceneInfoClass.getPathSeparator()
    #
    #         if DtsGlobals.Debug:
    #             Torque_Util.dump_setout("stdout")
    #         else:
    #             # double check the file name before opening the log
    #             if Prefs['exportBasename'] == "":
    #                 Prefs['exportBasename'] = SceneInfoClass.getDefaultBaseName()
    #
    #             try:
    #                 x = Prefs['LogToOutputFolder']
    #             except KeyError:
    #                 Prefs['LogToOutputFolder'] = True
    #             if Prefs['LogToOutputFolder']:
    #                 Torque_Util.dump_setout("%s%s%s.log" % (Prefs['exportBasepath'], pathSeparator, Prefs['exportBasename']))
    #             else:
    #                 Torque_Util.dump_setout("%s.log" % noext(Blender.Get("filename")))
    #
    #         Torque_Util.dump_writeln("Torque Exporter %s " % DtsGlobals.Version)
    #         Torque_Util.dump_writeln("Using blender, version %s" % Blender.Get('version'))
    #
    #         # refresh prefs
    #
    #         Torque_Util.dump_writeln("Exporting...")
    #         print("Exporting...")
    #         # switch out of edit mode if we are in edit mode
    #         Window.EditMode(0)
    #
    #         # refresh all data.
    #         handleScene(True)
    #         Prefs.refreshSequencePrefs()
    #         Prefs.refreshMaterialPrefs()
    #         Prefs.savePrefs()
    #
    #         cur_progress = Common_Gui.Progress()
    #
    #         if SceneInfo != None:
    #             cur_progress.pushTask("Done", 1, 1.0)
    #
    #             # start the export
    #             doExport(cur_progress)
    #
    #             cur_progress.update()
    #             cur_progress.popTask()
    #             Torque_Util.dump_writeln("Finished.")
    #         else:
    #             Torque_Util.dump_writeErr("Error. Not processed scene yet!")
    #
    #         del cur_progress
    #
    #         if Torque_Util.numErrors > 0 or Torque_Util.numWarnings > 0:
    #             message = ("Export finished with %i error(s) and %s warning(s). Read the log file for more information." % (
    #             Torque_Util.numErrors, Torque_Util.numWarnings))
    #             print(message)
    #             if Prefs["ShowWarningErrorPopup"]:
    #                 message += "%t|Continue|Do not show this message again"
    #                 opt = Blender.Draw.PupMenu(message)
    #                 if opt == 2:
    #                     Prefs["ShowWarningErrorPopup"] = False
    #                     # refresh the state of the button on the general panel
    #                     GeneralControls.refreshAll()
    #             Torque_Util.numWarnings = 0
    #             Torque_Util.numErrors = 0
    #         else:
    #             print("Finished.  See generated log file for details.")
    #
    #         # Reselect any objects that are currently selected.
    #         # this prevents a strange bug where objects are selected after
    #         # export, but behave as if they are not.
    #         if Blender.Object.GetSelected() != None:
    #             for ob in Blender.Object.GetSelected():
    #                 ob.select(True)
    #
    #         Torque_Util.dump_finish()
    #
    #
    #     '''
    #         Entry Point
    #     '''
    #     # -------------------------------------------------------------------------------------------------
    #
    #     if DtsGlobals.Profiling:
    #         try:
    #             import profile
    #             import __main__
    #             import pstats
    #         except:
    #             Profiling = False
    #
    #
    # def entryPoint(a):
    #     # HAVE TO RESET THIS SINCE IT CAN PERSIST BETWEEN FILE LOADS,
    #     # CAUSING ALL KINDS OF PROBLEMS !!!
    #     DtsGlobals.SceneInfo = None
    #
    #     DtsGlobals.Prefs = prefsClass()
    #     Prefs = DtsGlobals.Prefs
    #     # pathSeparator = SceneInfoClass.getPathSeparator()
    #
    #     '''
    #     # sets the global pathSeparator variable
    #     pathSeparator = SceneInfoClass.getPathSeparator()
    #
    #     if DtsGlobals.Debug:
    #         Torque_Util.dump_setout("stdout")
    #     else:
    #         # double check the file name before opening the log
    #         if Prefs['exportBasename'] == "":
    #             Prefs['exportBasename'] = SceneInfoClass.getDefaultBaseName()
    #
    #         try: x = Prefs['LogToOutputFolder']
    #         except KeyError: Prefs['LogToOutputFolder'] = True
    #         if Prefs['LogToOutputFolder']:
    #             Torque_Util.dump_setout( "%s%s%s.log" % (Prefs['exportBasepath'], pathSeparator, Prefs['exportBasename']) )
    #         else:
    #             Torque_Util.dump_setout("%s.log" % noext(Blender.Get("filename")))
    #
    #
    #
    #     Torque_Util.dump_writeln("Torque Exporter %s " % DtsGlobals.Version)
    #     Torque_Util.dump_writeln("Using blender, version %s" % Blender.Get('version'))
    #     '''
    #
    #     # if Torque_Util.Torque_Math.accelerator != None:
    #     #	Torque_Util.dump_writeln("Using accelerated math interface '%s'" % Torque_Util.Torque_Math.accelerator)
    #     # else:
    #     #	Torque_Util.dump_writeln("Using unaccelerated math code, performance may be suboptimal")
    #     # Torque_Util.dump_writeln("**************************")
    #
    #
    #
    #     if (a == 'quick'):
    #         # Use the profiler, if enabled.
    #         if DtsGlobals.Profiling:
    #             # make the entry point available from __main__
    #             __main__.export = export
    #             profile.run('export(),', 'exporterProfilelog.txt')
    #         else:
    #             export()
    #
    #         # dump out profiler stats if enabled
    #         if DtsGlobals.Profiling:
    #             # print out the profiler stats.
    #             p = pstats.Stats('exporterProfilelog.txt')
    #             p.strip_dirs().sort_stats('cumulative').print_stats(60)
    #             p.strip_dirs().sort_stats('time').print_stats(60)
    #             p.strip_dirs().print_callers('__getitem__', 20)
    #     elif a == 'normal' or (a == None):
    #         # Process scene and load configuration gui
    #         # handleScene()
    #         initGui()


class DTSExporter(bpy.types.Operator):
    """
    Export to the Autocad model format (.dxf)
    """
    bl_idname = "export.dts"
    bl_label = "Export DTS"
    filepath = StringProperty(subtype='FILE_PATH')

#     entitylayer_from_items = (
#         ('default_LAYER', 'Default Layer', ''),
#         ('obj.name', 'Object name', ''),
#         ('obj.layer', 'Object layer', ''),
#         ('obj.material', 'Object material', ''),
#         ('obj.data.name', 'Object\' data name', ''),
# #        ('obj.data.material', 'Material of data', ''),
#         ('..vertexgroup', 'Vertex Group', ''),
#         ('..group', 'Group', ''),
#         ('..map_table', 'Table', '')
#     )
#     layerColorFromItems = (
#         ('default_COLOR', 'Vertex Group', ''),
#         ('BYLAYER', 'BYLAYER', ''),
#         ('BYBLOCK', 'BYBLOCK', ''),
#         ('obj.layer', 'Object Layer', ''),
#         ('obj.color', 'Object Color', ''),
#         ('obj.material', 'Object material', ''),
#         # I don'd know ?
# #        ('obj.data.material', 'Vertex Group', ''),
# #        ('..map_table', 'Vertex Group', ''),
#     )
#     layerNameFromItems = (
#         ('LAYERNAME_DEF', 'Default Name', ''),
#         ('drawing_name', 'From Drawing name', ''),
#         ('scene_name', 'From scene name', '')
#     )

    exportModeItems = (
        ('ALL', 'All Objects', ''),
        ('SELECTION', 'Selected Objects', ''),
    )
#    spaceItems = (
#        ('1', 'Paper-Space', ''),
#        ('2', 'Model-Space', '')
#    )

    # entityltype_fromItems = (
    #     ('default_LTYPE', 'default_LTYPE', ''),
    #     ('BYLAYER', 'BYLAYER', ''),
    #     ('BYBLOCK', 'BYBLOCK', ''),
    #     ('CONTINUOUS', 'CONTINUOUS', ''),
    #     ('DOT', 'DOT', ''),
    #     ('DASHED', 'DASHED', ''),
    #     ('DASHDOT', 'DASHDOT', ''),
    #     ('BORDER', 'BORDER', ''),
    #     ('HIDDEN', 'HIDDEN', '')
    # )
    # material_toItems = (
    #     ('NO', 'Do not export', ''),
    #     ('COLOR', 'COLOR', ''),
    #     ('LAYER', 'LAYER', ''),
    #     ('..LINESTYLE', '..LINESTYLE', ''),
    #     ('..BLOCK', '..BLOCK', ''),
    #     ('..XDATA', '..XDATA', ''),
    #     ('..INI-File', '..INI-File', '')
    # )
    # projectionItems=(
    #     ('NO', 'No projection', 'Export 3D scene without any 2D projection'),
    #     ('TOP', 'TOP view', 'Use TOP view for projection'),
    #     ('BOTTOM', 'BOTTOM view', 'Use BOTTOM view for projection'),
    #     ('LEFT', 'LEFT view', 'Use LEFT view for projection'),
    #     ('RIGHT', 'RIGHT view', 'Use RIGHT view for projection'),
    #     ('FRONT', 'FRONT view', 'Use FRONT view for projection'),
    #     ('REAR', 'REAR view', 'Use REAR view for projection')
    # )
    # mesh_asItems = (
    #     ('NO', 'Do not export', ''),
    #     ('3DFACEs', '3DFACEs', ''),
    #     ('POLYFACE', 'POLYFACE', ''),
    #     ('POLYLINE', 'POLYLINE', ''),
    #     ('LINEs', 'LINEs', 'export Mesh as multiple LINEs'),
    #     ('POINTs', 'POINTs', 'Export Mesh as multiple POINTs')
    # )
#    curve_asItems  = (
#        ('NO', 'Do not export', ''),
#        ('LINEs', 'LINEs', ''),
#        ('POLYLINE', 'POLYLINE', ''),
#        ('..LWPOLYLINE r14', '..LWPOLYLINE r14', ''),
#        ('..SPLINE r14', '..SPLINE r14', ''),
#        ('POINTs', 'POINTs',  '')
#    )
#    surface_asItems  = (
#        ('NO', 'Do not export', ''),
#        ('..3DFACEs', '..3DFACEs', ''),
#        ('..POLYFACE', '..POLYFACE', ''),
#        ('..POINTs', '..POINTs', ''),
#        ('..NURBS', '..NURBS', '')
#    )
#    meta_asItems  = (
#        ('NO', 'Do not export', ''),
#        ('..3DFACEs', '..3DFACEs', ''),
#        ('..POLYFACE', '..POLYFACE', ''),
#        ('..3DSOLID', '..3DSOLID', '')
#    )
#    text_asItems  = (
#        ('NO', 'Do not export', ''),
#        ('TEXT', 'TEXT', ''),
#        ('..MTEXT', '..MTEXT', ''),
#        ('..ATTRIBUT', '..ATTRIBUT', '')
#    )
#    empty_asItems  = (
#        ('NO', 'Do not export', ''),
#        ('POINT', 'POINT', ''),
#        ('..INSERT', '..INSERT', ''),
#        ('..XREF', '..XREF', '')
#    )
#    group_asItems  = (
#        ('NO', 'Do not export', ''),
#        ('..GROUP', '..GROUP', ''),
#        ('..BLOCK', '..BLOCK', ''),
#        ('..ungroup', '..ungroup', '')
#    )
##    parent_asItems = ['..BLOCK','..ungroup'] # ???
#    proxy_asItems = (
#        ('NO', 'Do not export', ''),
#        ('..BLOCK','..BLOCK', ''),
#        ('..XREF', '..XREF', ''),
#        ('..ungroup', '..ungroup', ''),
#        ('..POINT', '..POINT', '')
#    )
#    camera_asItems = (
#        ('NO', 'Do not export', ''),
#        ('..BLOCK', '..BLOCK', ''),
#        ('..A_CAMERA', '..A_CAMERA', ''),
#        ('VPORT', 'VPORT', ''),
#        ('VIEW', 'VIEW', ''),
#        ('POINT', 'POINT', '')
#    )
#    lamp_asItems = (
#        ('NO', 'Do not export', ''),
#        ('..BLOCK', '..BLOCK', ''),
#        ('..A_LAMP', '..A_LAMP', ''),
#        ('POINT', 'POINT', '')
#    )
    # --------- CONTROL PROPERTIES --------------------------------------------
    # projectionThrough = EnumProperty(name="Projection", default="NO",
    #                                 description="Select camera for use to 2D projection",
    #                                 items=projectionItems)
    #
    # onlySelected = BoolProperty(name="Only selected", default=True,
    #                           description="What object will be exported? Only selected / all objects")
    #
    # apply_modifiers = BoolProperty(name="Apply modifiers", default=True,
    #                        description="Shall be modifiers applied during export?")
    # GUI_B -----------------------------------------
    # mesh_as = EnumProperty( name="Export Mesh As", default='3DFACEs',
    #                         description="Select representation of a mesh",
    #                         items=mesh_asItems)
#    curve_as = EnumProperty( name="Export Curve As:", default='NO',
#                            description="Select representation of a curve",
#                            items=curve_asItems)
#    surface_as = EnumProperty( name="Export Surface As:", default='NO',
#                            description="Select representation of a surface",
#                            items=surface_asItems)
#    meta_as = EnumProperty( name="Export meta As:", default='NO',
#                            description="Select representation of a meta",
#                            items=meta_asItems)
#    text_as = EnumProperty( name="Export text As:", default='NO',
#                            description="Select representation of a text",
#                            items=text_asItems)
#    empty_as = EnumProperty( name="Export empty As:", default='NO',
#                            description="Select representation of a empty",
#                            items=empty_asItems)
#    group_as = EnumProperty( name="Export group As:", default='NO',
#                            description="Select representation of a group",
#                            items=group_asItems)
##    parent_as = EnumProperty( name="Export parent As:", default='NO',
##                            description="Select representation of a parent",
##                            items=parent_asItems)
#    proxy_as = EnumProperty( name="Export proxy As:", default='NO',
#                            description="Select representation of a proxy",
#                            items=proxy_asItems)
#    camera_as = EnumProperty( name="Export camera As:", default='NO',
#                            description="Select representation of a camera",
#                            items=camera_asItems)
#    lamp_as = EnumProperty( name="Export lamp As:", default='NO',
#                            description="Select representation of a lamp",
#                            items=lamp_asItems)
    # ----------------------------------------------------------
    # entitylayer_from = EnumProperty(name="Entity Layer", default="obj.data.name",
    #                                 description="Entity LAYER assigned to?",
    #                                 items=entitylayer_from_items)
    # entitycolor_from = EnumProperty(name="Entity Color", default="default_COLOR",
    #                                 description="Entity COLOR assigned to?",
    #                                 items=layerColorFromItems)
    # entityltype_from = EnumProperty(name="Entity Linetype", default="CONTINUOUS",
    #                                 description="Entity LINETYPE assigned to?",
    #                                 items=entityltype_fromItems)
    #
    # layerName_from = EnumProperty(name="Layer Name", default="LAYERNAME_DEF",
    #                                 description="From where will layer name be taken?",
    #                                 items=layerNameFromItems)
    # GUI_A -----------------------------------------
#    layFrozen_on = BoolProperty(name="LAYER.frozen status", description="(*todo) Support LAYER.frozen status   on/off", default=False)
#    materialFilter_on = BoolProperty(name="Material filtering", description="(*todo) Material filtering   on/off", default=False)
#    colorFilter_on = BoolProperty(name="Color filtering", description="(*todo) Color filtering   on/off", default=False)
#    groupFilter_on = BoolProperty(name="Group filtering", description="(*todo) Group filtering   on/off", default=False)
#    objectFilter_on = BoolProperty(name="Object filtering", description="(*todo) Object filtering   on/off", default=False)
#    paper_space_on = EnumProperty(name="Space of export:", default="2",
#                                    description="Select space that will be taken for export.",
#                                    items=spaceItems)
#    material_to = EnumProperty(name="Material assigned to?:", default="NO",
#                                    description="Material assigned to?.",
#                                    items=material_toItems)

#    prefix_def = StringProperty(name="Prefix for LAYERs", default="DX_",
#                                    description='Type Prefix for LAYERs')
#    layername_def = StringProperty(name="default LAYER name", default="DEF_LAY",
#                                    description='Type default LAYER name')
#    layercolor_def = StringProperty(name="Default layer color:", default="1",
#                                    description='Set default COLOR. (0=BYBLOCK,256=BYLAYER)')
#    layerltype_def = StringProperty(name="Default LINETYPE", default="DEF_LAY_TYPE",
#                                    description='Set default LINETYPE')

    # verbose = BoolProperty(name="Verbose", default=False
    #                        description="Run the exporter in debug mode.  Check the console for output")

    # restframe = IntProperty(name="Rest Frame", default=0,
    #                         description="Rest Frame")



    def execute(self, context):
        filePath = bpy.path.ensure_ext(self.filepath, ".dts")
        config = {
            # 'projectionThrough' : self._checkNO(self.projectionThrough),
            # 'onlySelected' : self.onlySelected,
            # 'apply_modifiers' : self.apply_modifiers,
            # GUI B
            # 'mesh_as' : self._checkNO(self.mesh_as),
#            'curve_as' : self._checkNO(self.curve_as),
#            'surface_as' : self._checkNO(self.surface_as),
#            'meta_as' : self._checkNO(self.meta_as),
#            'text_as' : self._checkNO(self.text_as),
#            'empty_as' : self._checkNO(self.empty_as),
#            'group_as' : self._checkNO(self.group_as),
#            'proxy_as' : self._checkNO(self.proxy_as),
#            'camera_as' : self._checkNO(self.camera_as),
#            'lamp_as' : self._checkNO(self.lamp_as),

            # 'entitylayer_from' : self.entitylayer_from,
            # 'entitycolor_from' : self.entitycolor_from,
            # 'entityltype_from' : self.entityltype_from,
            # 'layerName_from' : self.layerName_from,

            # NOT USED
#            'layFrozen_on' : self.layFrozen_on,
#            'materialFilter_on' : self.materialFilter_on,
#            'colorFilter_on' : self.colorFilter_on,
#            'groupFilter_on' : self.groupFilter_on,
#            'objectFilter_on' : self.objectFilter_on,
#            'paper_space_on' : self.paper_space_on,
#            'layercolor_def' : self.layercolor_def,
#            'material_to' : self.material_to,

            # 'restframe' : self.restframe
        }

        # from .export_dxf import exportDXF
        # exportDXF(context, filePath, config)
        doExport(context, filePath, config)
        return {'FINISHED'}

    def _checkNO(self, val):
        if val == 'NO': return None
        else: return val

    def invoke(self, context, event):
        from .DtsPrefs import prefsClass
        DtsGlobals.Prefs = prefsClass()
        Prefs = DtsGlobals.Prefs
        if not self.filepath:
            self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".dts")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        # refresh all data.
        handleScene(True)
        Prefs.refreshSequencePrefs()
        Prefs.refreshMaterialPrefs()
        Prefs.savePrefs()
        return {'RUNNING_MODAL'}
