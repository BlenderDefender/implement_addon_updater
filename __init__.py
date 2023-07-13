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

from . import addon_updater_ops

import re
import os
from os.path import expanduser

import shutil
import platform

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
    "category": "Development"}


# Multiple uses:
# -----------------------------------------------------------------------------
def insert_text_from_array(arr):
    for x in arr:
        print(x)
        bpy.ops.text.insert(text=x)

# -----------------------------------------------------------------------------


# addon-updater-ops operators
# -----------------------------------------------------------------------------

def insert_updater_engine(context, machine):
    context.space_data.text = bpy.data.texts['addon_updater_ops.py']
    bpy.ops.text.jump(line=1323)

    if machine == "github":
        print("updater.engine = GitHub")
        return

    bpy.ops.text.select_line()
    bpy.ops.text.cut()

    if machine == "gitlab":
        print("updater.engine = GitLab")
        bpy.ops.text.insert(text='\tupdater.engine = "GitLab"')
        return

    if machine == "bitbucket":
        print("updater.engine = Bitbucket")
        bpy.ops.text.insert(text='\tupdater.engine = "Bitbucket"')
        return

    print("Defaulting to GitHub")
    bpy.ops.text.insert(text='\tupdater.engine = "GitHub"')


# -----------------------------------------------------------------------------


# Script Operators
# -----------------------------------------------------------------------------

def add_addon_prefs(code_end, pref):

    bpy.ops.text.jump(line=code_end+1)
    bpy.ops.text.select_line()
    bpy.ops.text.cut()

    insert_text_from_array(pref)
    print("add_addon_prefs was a success")


def add_gpl_and_imports(add_license, imports_end, gpl):

    bpy.ops.text.jump(line=imports_end+1)
    bpy.ops.text.insert(text="from . import addon_updater_ops\n")

    if add_license:

        bpy.ops.text.jump(line=1)
        bpy.ops.text.select_line()
        bpy.ops.text.cut()

        insert_text_from_array(gpl)
        # bpy.ops.text.move(type='NEXT_LINE')
        bpy.ops.text.paste()
        return 21

    return 0


def add_classes_registry(text):
    t = re.sub(r'(,)', r'\1\n\t', text)
    classes = "classes = (\n\t " + t + ",\n\t DemoPreferences\n)"
    ret = ['\n\n', classes, '\n', '\n', 'def register():\n', '\t# addon updater code and configurations\n', '\t# in case of broken version, try to register the updater first\n', '\t# so that users can revert back to a working version\n', '\taddon_updater_ops.register(bl_info)\n', '\n', '\t# register the example panel, to show updater buttons\n', '\tfor cls in classes:\n',
           '\t\taddon_updater_ops.make_annotations(cls) # to avoid blender 2.8 warnings\n', '\t\tbpy.utils.register_class(cls)\n', '\n', '\n', 'def unregister():\n', '\t# addon updater unregister\n', '\taddon_updater_ops.unregister()\n', '\n', '\t# register the example panel, to show updater buttons\n', '\tfor cls in reversed(classes):\n', '\t\tbpy.utils.unregister_class(cls)\n\n']
    print(ret)

    bpy.ops.text.move(type='NEXT_LINE')
    insert_text_from_array(ret)
    return ret


def auto_check_t_o_f(bool):
    return f'\t\tdefault={bool == True},\n'
# -----------------------------------------------------------------------------


class IMPLEMENTUPDATER_OT_main(bpy.types.Operator):
    """Implement the Addon Updater quick and easy"""
    bl_label = "Implement Updater"
    bl_idname = "implement_updater.main"

    ask_license_block: BoolProperty(
        name="Add GPL 3 license Block",
        default=True
    )

    ask_auto_check: BoolProperty(
        name="Enable 'Auto Check for update' by default"
    )

    ask_import_end: IntProperty(
        name="Which line is the last of the import part?",
        default=3,
        min=1
    )

    ask_main_code_end: IntProperty(
        name="Which line is the last of the main part?",
        default=100,
        min=1
    )

    ask_updater_engine: EnumProperty(items=[
        ("github", "Github", "Choose Github as updater engine"),
        ("gitlab", "GitLab", "Choose GitLab as updater engine"),
        ("bitbucket", "Bitbucket", "Choose Bitbucket as updater engine")
    ],
        name="Choose updater engine"
    )

    ask_classnames: StringProperty(
        name="Type in your class names, seperated with a comma.", default="")

    def execute(self, context):

        ask_license_block = self.ask_license_block
        ask_auto_check = self.ask_auto_check
        ask_import_end = self.ask_import_end
        ask_main_code_end = self.ask_main_code_end
        ask_classnames = self.ask_classnames
        ask_updater_engine = self.ask_updater_engine

        auto_check_true_or_false = auto_check_t_o_f(ask_auto_check)

        gpl = ['# ##### BEGIN GPL LICENSE BLOCK #####\n', '#\n', "#  <one line to give the program's name and a brief idea of what it does.>\n", '#    Copyright (C) <year>  <name of author>\n', '#\n', '#  This program is free software; you can redistribute it and/or\n', '#  modify it under the terms of the GNU General Public License\n', '#  as published by the Free Software Foundation; either version 3\n', '#  of the License, or (at your option) any later version.\n', '#\n', '#  This program is distributed in the hope that it will be useful,\n',
               '#  but WITHOUT ANY WARRANTY; without even the implied warranty of\n', '#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n', '#  GNU General Public License for more details.\n', '#\n', '#  You should have received a copy of the GNU General Public License\n', '#  along with this program; if not, write to the Free Software Foundation,\n', '#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.\n', '#\n', '# ##### END GPL LICENSE BLOCK #####', '\n\n']
        pref = ['\n', 'class DemoPreferences(bpy.types.AddonPreferences):\n', '\tbl_idname = __package__\n', '\n', '\t# addon updater preferences\n', '\n', '\tauto_check_update: bpy.props.BoolProperty(\n', '\t\tname="Auto-check for Update",\n', '\t\tdescription="If enabled, auto-check for updates using an interval",\n', auto_check_true_or_false, '\t\t)\n', '\tupdater_intrval_months: bpy.props.IntProperty(\n', "\t\tname='Months',\n", '\t\tdescription="Number of months between checking for updates",\n', '\t\tdefault=0,\n', '\t\tmin=0\n', '\t\t)\n', '\tupdater_intrval_days: bpy.props.IntProperty(\n', "\t\tname='Days',\n", '\t\tdescription="Number of days between checking for updates",\n', '\t\tdefault=7,\n', '\t\tmin=0,\n', '\t\tmax=31\n', '\t\t)\n', '\tupdater_intrval_hours: bpy.props.IntProperty(\n', "\t\tname='Hours',\n", '\t\tdescription="Number of hours between checking for updates",\n', '\t\tdefault=0,\n', '\t\tmin=0,\n', '\t\tmax=23\n', '\t\t)\n', '\tupdater_intrval_minutes: bpy.props.IntProperty(\n', "\t\tname='Minutes',\n",
                '\t\tdescription="Number of minutes between checking for updates",\n', '\t\tdefault=0,\n', '\t\tmin=0,\n', '\t\tmax=59\n', '\t\t)\n', '\n', '\tdef draw(self, context):\n', '\t\tlayout = self.layout\n', '\t\t# col = layout.column() # works best if a column, or even just self.layout\n', '\t\tmainrow = layout.row()\n', '\t\tcol = mainrow.column()\n', '\n', '\t\t# updater draw function\n', '\t\t# could also pass in col as third arg\n', '\t\taddon_updater_ops.update_settings_ui(self, context)\n', '\n', '\t\t# Alternate draw function, which is more condensed and can be\n', '\t\t# placed within an existing draw function. Only contains:\n', '\t\t#   1) check for update/update now buttons\n', '\t\t#   2) toggle for auto-check (interval will be equal to what is set above)\n', '\t\t# addon_updater_ops.update_settings_ui_condensed(self, context, col)\n', '\n', '\t\t# Adding another column to help show the above condensed ui as one column\n', '\t\t# col = mainrow.column()\n', '\t\t# col.scale_y = 2\n', '\t\t# col.operator("wm.url_open","Open webpage ").url=addon_updater_ops.updater.website\n']

        ask_main_code_end += add_gpl_and_imports(
            ask_license_block, ask_import_end, gpl)
        add_addon_prefs(ask_main_code_end, pref)
        add_classes_registry(ask_classnames)

        # filepath = os.path.join(os.path.dirname(
        #     os.path.abspath(__file__)), "AddonUpdater.blend")
        # print(filepath)
        # with bpy.data.libraries.load(filepath) as (data_from, data_to):
        #     data_to.texts = data_from.texts

        SCRIPT_DIR = os.path.dirname(__file__)
        templates_dir = os.path.join(SCRIPT_DIR, "templates")

        with open(os.path.join(templates_dir, "addon_updater.txt"), "r") as f:
            updater = bpy.data.texts.new("addon_updater.py")
            updater.write(f.read())

        with open(os.path.join(templates_dir, "addon_updater_ops.txt"), "r") as f:
            updater_ops = bpy.data.texts.new("addon_updater_ops.py")
            updater_ops.write(f.read())

#        print(ask_updater_engine)
        insert_updater_engine(context, ask_updater_engine)

        return {'FINISHED'}

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)


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
