# ##### BEGIN GPL LICENSE BLOCK #####
#
#  <Implement the Addon Updater the easy way>
#    Copyright (C) <2020>  <Blender Defender>
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
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
    IntProperty,
    StringProperty
)
from bpy.types import (
    Context,
    UILayout
)

from . import addon_updater_ops

import re
import os
from os import path as p

import shutil
import platform

import time

bl_info = {
    "name": "Implement Addon Updater",
    "author": "Blender Defender",
    "version": (1, 1, 1),
    "blender": (2, 80, 0),
    "location": "Text Editor > Text > Implement Addon Updater",
    "description": "Implement the Addon Updater the easy way.",
    "warning": "Checkout Gumroad for other Addons and more...",
    "doc_url": "https://github.com/BlenderDefender/implement_addon_updater#implement-addon-updater",
    "tracker_url": "https://github.com/BlenderDefender/implement_addon_updater/issues/new",
    "category": "Development"
}

SCRIPT_DIR = p.dirname(__file__)


# Multiple uses:
# -----------------------------------------------------------------------------
def insert_and_print_text(arr):
    print(arr)
    bpy.ops.text.insert(text=arr)

# -----------------------------------------------------------------------------


class IMPLEMENTUPDATER_OT_main(bpy.types.Operator):
    """Implement the Addon Updater quick and easy"""
    bl_label = "Implement Updater"
    bl_idname = "implement_updater.main"

    add_license_block: BoolProperty(
        name="Add GPL 3 license Block",
        default=True
    )
    license_author: StringProperty(name="Author")
    license_description: StringProperty(
        name="Description", description="nne line to give the program's name and a brief idea of what it does")

    auto_check: BoolProperty(
        name="Enable 'Auto Check for update' by default"
    )

    import_end: IntProperty(
        name="Which line is the last of the import part?",
        default=3,
        min=1
    )

    main_code_end: IntProperty(
        name="Which line is the last of the main part?",
        default=100,
        min=1
    )

    updater_engine: EnumProperty(items=[
        ("GitHub", "GitHub", "Choose GitHub as updater engine"),
        ("GitLab", "GitLab", "Choose GitLab as updater engine"),
        ("Bitbucket", "Bitbucket", "Choose Bitbucket as updater engine")
    ],
        name="Choose updater engine"
    )

    addon_name: StringProperty(
        name="Addon Name", description="Type in the name of your addon.", default="")

    classnames: StringProperty(
        name="Classnames", description="Type in your class names, seperated with a comma", default="")

    def execute(self, context):

        main_code_end = self.main_code_end + self.add_gpl_and_imports()

        self.add_addon_prefs(main_code_end)
        self.add_classes_registry()

        # filepath = p.join(p.dirname(
        #     p.abspath(__file__)), "AddonUpdater.blend")
        # print(filepath)
        # with bpy.data.libraries.load(filepath) as (data_from, data_to):
        #     data_to.texts = data_from.texts

        templates_dir = p.join(SCRIPT_DIR, "templates")

        with open(p.join(templates_dir, "addon_updater.txt"), "r") as f:
            updater = bpy.data.texts.new("addon_updater.py")
            updater.write(f.read())

        with open(p.join(templates_dir, "addon_updater_ops.txt"), "r") as f:
            ops_template: str = f.read()

        ops_template = ops_template.replace("<engine>", self.updater_engine)

        updater_ops = bpy.data.texts.new("addon_updater_ops.py")
        updater_ops.write(ops_template)

        context.space_data.text = bpy.data.texts['addon_updater_ops.py']
        bpy.ops.text.jump(line=1332)

        # print(self.updater_engine)

        return {'FINISHED'}

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context: 'Context'):
        layout: 'UILayout' = self.layout

        layout.prop(self, "add_license_block")
        if self.add_license_block:
            layout.prop(self, "license_author")
            layout.prop(self, "license_description")
        layout.separator()

        layout.prop(self, "import_end")
        layout.prop(self, "main_code_end")
        layout.separator()

        layout.prop(self, "updater_engine", text="Updater Engine")
        layout.prop(self, "addon_name")
        layout.prop(self, "classnames")
        layout.prop(self, "auto_check")

    def add_gpl_and_imports(self):

        bpy.ops.text.jump(line=self.import_end + 1)
        bpy.ops.text.insert(text="from . import addon_updater_ops\n")

        if self.add_license_block:
            bpy.ops.text.jump(line=1)
            bpy.ops.text.select_line()
            bpy.ops.text.cut()

            with open(p.join(SCRIPT_DIR, "templates", "gpl_license_block.txt"), "r", encoding="utf-8") as f:
                gpl_data = f.read()

            if self.license_description == "":
                gpl_data = gpl_data.replace(
                    "<program description>", "<one line to give the program's name and a brief idea of what it does.>")
            else:
                gpl_data = gpl_data.replace(
                    "<program description>", f"<{self.license_description}>")

            gpl_data = gpl_data.replace("<year>", time.strftime("<%Y>"))

            if self.license_author != "":
                gpl_data = gpl_data.replace(
                    "<name of author>", f"<{self.license_author}>")

            insert_and_print_text(gpl_data + "\n")
            # bpy.ops.text.move(type='NEXT_LINE')
            bpy.ops.text.paste()

            return len(gpl_data.split("\n"))

        return 0

    def add_addon_prefs(self, code_end):
        pref = ""
        with open(p.join(SCRIPT_DIR, "templates", "preferences.txt"), "r", encoding="utf-8") as f:
            pref = f.read()

        pref = pref.replace("\"<auto_check_update>\"",
                            str(self.auto_check == True))

        addon_name_as_class = self.addon_name.upper().strip().replace(" ", "_")
        if addon_name_as_class == "":
            addon_name_as_class = "MY_ADDON"
        self.addon_prefs_string = addon_name_as_class + "_APT_preferences"
        pref = pref.replace("MY_ADDON_APT_preferences",
                            self.addon_prefs_string)

        bpy.ops.text.jump(line=code_end+1)
        bpy.ops.text.select_line()
        bpy.ops.text.cut()

        insert_and_print_text(pref + "\n")
        print("add_addon_prefs was a success")

    def add_classes_registry(self):
        t = re.sub(r'(,)', r'\1\n\t', self.classnames)
        classes = f"{t},\n\t{self.addon_prefs_string},\n"

        with open(p.join(SCRIPT_DIR, "templates", "register_code.txt"), "r", encoding="utf-8") as f:
            register_code = f.read()

        register_code = register_code.replace("# <placeholder>", classes)

        bpy.ops.text.move(type='NEXT_LINE')
        insert_and_print_text(register_code)


def menu_func(self, context):
    self.layout.operator(IMPLEMENTUPDATER_OT_main.bl_idname, icon='ADD')


class IMPLEMENTUPDATER_APT_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    # addon updater preferences

    auto_check_update: BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=True,
    )
    updater_intrval_months: IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0
    )
    updater_intrval_days: IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
        max=31
    )
    updater_intrval_hours: IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
    )
    updater_intrval_minutes: IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
    )

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.url_open", text="Checkout Gumroad for other addons and more...",
                        icon='FUND').url = "https://gumroad.com/blenderdefender"

        # col = layout.column() # works best if a column, or even just self.layout
        mainrow = layout.row()
        col = mainrow.column()

        # updater draw function
        # could also pass in col as third arg
        addon_updater_ops.update_settings_ui(self, context)

        # Alternate draw function, which is more condensed and can be
        # placed within an existing draw function. Only contains:
        #   1) check for update/update now buttons
        #   2) toggle for auto-check (interval will be equal to what is set above)
        # addon_updater_ops.update_settings_ui_condensed(self, context, col)

        # Adding another column to help show the above condensed ui as one column
        # col = mainrow.column()
        # col.scale_y = 2
        # col.operator("wm.url_open","Open webpage ").url=addon_updater_ops.updater.website


classes = (
    IMPLEMENTUPDATER_OT_main,
    IMPLEMENTUPDATER_APT_Preferences
)


def register():
    # addon updater code and configurations
    # in case of broken version, try to register the updater first
    # so that users can revert back to a working version
    addon_updater_ops.register(bl_info)

    bpy.types.TEXT_MT_text.append(menu_func)

    # register the example panel, to show updater buttons
    for cls in classes:
        addon_updater_ops.make_annotations(
            cls)  # to avoid blender 2.8 warnings
        bpy.utils.register_class(cls)


def unregister():
    # addon updater unregister
    addon_updater_ops.unregister()

    bpy.types.TEXT_MT_text.remove(menu_func)

    # register the example panel, to show updater buttons
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
