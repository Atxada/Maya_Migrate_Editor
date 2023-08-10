# Maya_Migrate_Editor (Beta Version)

## Description

Some maya nodes in the scene use external resources by directory name (String), if the file is
not available in the reference directory, this can cause some error (unresolved connection). In a
studio setup, for example, when each computer is connected to the main server, this problem
frequently occurs when a local pc attempts to transfer a maya file with all associated paths to
the main server.

Migrate editor allows the the user to send the maya file with all resource paths (texture) intact.
The user has the option of choose where to save the resource and where to save the scene.


## Install Instructions

1.Extract Migrate_Tool_Editor.zip (file inside: migrate_editor.py and migrate_editor_installer.py)  
2.Start Autodesk Maya  
3.Drag migrate_editor_installer.py to viewport  
4.Tools have been added to the current active shelf  


## How To Use

1. Click the folder icon in the upper right corner to open the file dialog.  
2. File dialog will appear. The user can specify which folder to export the texture or other
file to (This step is required to migrate).By clicking right mouse button, The user can also
add new folder.  
3. All linked connections will be listed in the resources detail (version 1.0 will only list file
connections). By checking the checkbox to the right of the resolved list, the user can
select which file to export.  
4. If all set, the user can click “save scene as” button. File dialog will appear and ask for the
save destination to begin the migrate operation. (Note: Migrating a file will create a new
Maya scene, save before migrating if necessary)  

## Notes (current version):
-Migrate Editor UI in 2019 might seems different compared to 2020 and above, due to different
version of PySide2 framework
-Migrate Editor (1.0.0) only able to migrate file type resource
-There is still possible bug or error in beta version
