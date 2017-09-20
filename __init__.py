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

bl_info = {
    "name": "Torque Shape (.dts)...",
    "author": "Paul Jan",
    "version": (1, 0),
    "blender": (2, 75, 0),
    "location": "File > Export > Torque (.dts)",
    "description": "Export to Torque (.dts) format.",
    "warning": "",
    "wiki_url": "",
    "category": "Export",
}

if "bpy" in locals():
    from importlib import reload
    reload(operator)
    reload(DtsPrefs)
    del reload

import bpy
from . import operator
from . import DtsPrefs

def menu_func(self, context):
    self.layout.operator(operator.DTSExporter.bl_idname, text="Torque (.dts)")

classes = (
    #operator.hi,
    operator.DTSExporter,
    DtsPrefs.DTSAddonPreferences,
)

def register():
    bpy.types.INFO_MT_file_export.append(menu_func)

    from bpy.utils import register_class
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    bpy.types.INFO_MT_file_export.remove(menu_func)

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == "__main__":
    register()