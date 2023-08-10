import os
import logging
import shutil
import maya.cmds as cmds
import maya.mel as mel

# scriptule to track events that happen when some software runs
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def onMayaDroppedPythonFile(*args):
    try:
        # Script directory for where file come from, script_file_path for full address
        installer_directory = os.path.dirname(__file__)
        script_file_path = os.path.join(installer_directory, "migrate_editor.py")
        
        # raise runtime error if script not found
        if not os.path.exists(script_file_path):
                raise RuntimeError("Unable to find 'migrate_editor.py' relative to this installer file")
        
        # Get default script directory for suggestion
        prefs_dir = os.path.dirname(cmds.about(preferences=True))
        scripts_dir = os.path.normpath(os.path.join(prefs_dir, "scripts"))
        
        shutil.copy(script_file_path,scripts_dir)

        # Generate Shelf
        current_shelf = mel.eval("string $currentShelf = `tabLayout -query -selectTab $gShelfTopLevel`;")
        cmds.setParent(current_shelf)
        cmds.shelfButton(command="from migrate_editor import migrateEditorUI; migrateEditorUI.show_dialog()",ann="Migrate_Editor",
        label="migrate_editor",image="folder-new.png",sourceType="python",iol="Migrate")

        cmds.confirmDialog(message="Script successfully installed ""<br>""<br>""{0}".format(scripts_dir),
        title="Confirmation dialog")
    
    except Exception as e:
        cmds.confirmDialog(message="Script failed to installed: {0}".format(e),icon = "warning",title="ERROR")
        