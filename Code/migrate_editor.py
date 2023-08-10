"""
Maya Migrate tools version 0.0
by Aldo Aldrich 
Autodesk Maya is a property of Autodesk, Inc.

version 1.1 (postpone)
-user c migrate to multiple folder
-filter by alphabet order
-(Minor) use spacer to align content detail
-(Minor) prevent user click refresh while function running
"""

from PySide2 import QtCore,QtWidgets,QtGui
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui

import os
import shutil

# boilerplate code, return maya main window
def maya_main_window():
    # Return the maya main window widget as a python object
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    
class migrateSceneMaya(QtWidgets.QDialog):
    
    # Class constants 
    DIR_SEPARATOR = os.sep #deprecated
    NODE_TYPE = "file"
    
    def initiate_dialog(self,parent=maya_main_window()):
        super(migrateEditorUI, self).__init__(parent)
        """
        # Check any unresolved path 
        if cmds.filePathEditor(q=1,lf="",unresolved=1) != None:
            file_dict = self.find_all_file_path(self.NODE_TYPE,unresolved=False)
        print (file_dict)
        """
              
    # Function to get resource target path by user input
    def call_fileDialog2(self,dialog_mode = 0, title_name="Save Scene As",confirm_caption="Save"): 
        # call file dialog2 
        temp = cmds.fileDialog2(fileMode=dialog_mode, caption=title_name, 
                                dialogStyle=1,fileFilter="Maya ASCII (*.ma);;Maya Binary (*.mb)",
                                rf=1,okc=confirm_caption)

        if temp != None: print ("Result: %s"%temp[0])
        else: return
        
        if temp[1] == "Maya Binary":
            new_maya_type = "mayaBinary"
        else:
            new_maya_type = "mayaAscii"
            
        # function variables
        new_file_dir = temp[0]
        new_folder_dir = new_file_dir.rpartition("/")[0]
        """
        # deprecated
        new_file_dir = new_file_dir.replace("/",self.DIR_SEPARATOR )
        new_folder_dir = new_folder_dir.replace("/",self.DIR_SEPARATOR)
        """

        return new_file_dir,new_folder_dir,new_maya_type     
            
    # note: Pass directory argument with correct separator
    def create_folder_on_disk(self,directory,folder_name):
        folder = os.path.join(directory,folder_name)
        # Create resource folder 
        os.makedirs(folder)
        print ("New Folder: %s")%folder,
        return folder
        
    # function to find all unresolved path in scene
    def find_all_file_path(self,node_type="file",unresolved=True):
        full_path = []
        node_attribute = []
        file_dict = {}
        cmds.filePathEditor(rf=1) #refresher
        
        def file_path_getter(unresolved=unresolved):
            # Check if local variable is clear
            if file_dict != {}:
                file_dict.clear()
            if full_path != []:
                del full_path[:]
            if node_attribute != []:
                del node_attribute[:]
            
            if cmds.filePathEditor(q=1,ld="",unresolved=unresolved) == None:
                return
            
            for path in cmds.filePathEditor(q=1,ld="",unresolved=unresolved):
                if cmds.filePathEditor(q=1,lf=path,unresolved=unresolved,bt=node_type) != None:
                    #path = path.replace("/",os.sep)
                    temp = cmds.filePathEditor(q=1,lf=path,unresolved=unresolved,bt=node_type)
                    temp2 = cmds.filePathEditor(q=1,lf=path,unresolved=unresolved,wa=1,bt=node_type)[1::2]
                    
                    if isinstance(temp,type([])):
                        for count,i in enumerate(temp):
                           full_path.append(path+"/"+i)
                           node_attribute.append(temp2[count])
                    else:
                        full_path.append(path+"/"+temp)
                        node_attribute.append(temp2)
  
                else:
                    pass
                       
            # assign dictionary (keys:value) => (node+attribute:file directory)
            if full_path != None:
                for count,node in enumerate(node_attribute):
                    file_dict[node] = full_path[count]
            
            return file_dict
        
        file_path_getter()
             
        if unresolved==False:
            resolved_dict = file_dict.copy()
            unresolved_dict = file_path_getter(unresolved=True)
            
            if unresolved_dict == None: return
            
            for unresolved_item in unresolved_dict.items():
                if unresolved_item in resolved_dict.items():
                    resolved_dict.pop(unresolved_item[0])
            
            return resolved_dict
        
        else:
            return file_dict
        
    def open_file_path_editor(self):
        cmds.filePathEditor(rf=1)
        cmds.FilePathEditor()
            
    # change the string reference in node attribute
    def save_scene_as(self,file_dir=False,file_type="mayaAscii"):
        # Save scene as
        cmds.file(rename=file_dir)
        if file_type != "mayaBinary":
            file_type = "mayaAscii"
        cmds.file(save=True, type=file_type) 

class migrateEditorUI(migrateSceneMaya):
    
    # Runtime Cache 
    unresolved_input_dict = {}
    resolved_content_list = []
    resolved_dynamic_widget_list = []
    unresolved_dynamic_widget_list = []
    
    class_instance = None
    
    @classmethod
    def show_dialog(cls):
        if not cls.class_instance:
            cls.class_instance = migrateEditorUI()
        if cls.class_instance.isHidden():
            cls.class_instance.show()
        else:
            cls.class_instance.raise_()
            cls.class_instance.activateWindow()
    
    def __init__(self):
        self.initiate_dialog()
        
        self.setWindowTitle("Migrate Editor")
        self.setWindowFlags(QtCore.Qt.WindowType.Window)
        self.setStyleSheet("borderstyle:outset")
        self.setMinimumWidth(250)
        self.setMinimumHeight(200)
        self.resize(500,450)
        
        # Remove window question 
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        
        # Construct Window UI element and connection
        self.create_widgets()
        self.create_layouts()
        self.create_connections()  
        self.create_file_path_content()
    
    def create_widgets(self):
        # Label
        self.target_dir_label = QtWidgets.QLabel("Target Directory:")
        
        self.resolved_label = QtWidgets.QLabel("Resolved Path")
        self.resolved_node_label = QtWidgets.QLabel("Node")
        self.resolved_file_label = QtWidgets.QLabel("                           File Name") # don't ask me why(ver 1.0)
        self.resolved_migrate_label = QtWidgets.QLabel("Migrate:")
        
        self.unresolved_label = QtWidgets.QLabel("Unresolved Path")
        self.unresolved_node_label = QtWidgets.QLabel("Node")
        self.unresolved_file_label = QtWidgets.QLabel("           File Name")
        self.unresolved_input_label = QtWidgets.QLabel("Input        ")
        
        # Label Font
        boldFont = QtGui.QFont()
        boldFont.setBold(True)
        boldFont.setPixelSize(12)
        
        # Label icon and qimage class
        self.resolved_icon_image = QtGui.QImage(":confirm")     # for resize image
        self.resolved_icon_image = self.resolved_icon_image.scaled(18,18, QtCore.Qt.IgnoreAspectRatio, 
                                                                          QtCore.Qt.SmoothTransformation)
        self.resolved_icon_pixmap = QtGui.QPixmap()
        self.resolved_icon_pixmap.convertFromImage(self.resolved_icon_image)
        
        self.resolved_icon_label = QtWidgets.QLabel()
        self.resolved_icon_label.setPixmap(self.resolved_icon_pixmap)
        
        self.unresolved_icon_image = QtGui.QImage(":error")     # for resize image
        self.unresolved_icon_image = self.unresolved_icon_image.scaled(18,18, QtCore.Qt.IgnoreAspectRatio, 
                                                                              QtCore.Qt.SmoothTransformation)
        self.unresolved_icon_pixmap = QtGui.QPixmap()
        self.unresolved_icon_pixmap.convertFromImage(self.unresolved_icon_image)
        
        self.unresolved_icon_label = QtWidgets.QLabel()
        self.unresolved_icon_label.setPixmap(self.unresolved_icon_pixmap)
        
        # Line edit
        self.target_dir_line_edit = QtWidgets.QLineEdit()
        
        # Button
        self.target_folder_btn = QtWidgets.QPushButton()
        
        self.file_path_editor_btn = QtWidgets.QPushButton("File Path Editor")
        self.refresh_list_btn = QtWidgets.QPushButton("Refresh List")
        self.migrate_btn = QtWidgets.QPushButton("Save Scene As")
        
        # check box
        self.global_checkbox = QtWidgets.QCheckBox()
        self.global_checkbox.setMinimumWidth(27)
        self.global_checkbox.setChecked(True)
        
        # Splitter
        self.splitter_mid = QtWidgets.QSplitter()
        self.splitter_mid.setOrientation(QtCore.Qt.Vertical)
      
        # Scroll area
        self.resolved_widget_scroll = QtWidgets.QWidget()
        self.resolved_scroll_area = QtWidgets.QScrollArea()
        self.resolved_scroll_area.setWidgetResizable(True)
        self.resolved_scroll_area.setWidget(self.resolved_widget_scroll)
        
        self.unresolved_widget_scroll = QtWidgets.QWidget()
        self.unresolved_scroll_area = QtWidgets.QScrollArea()
        self.unresolved_scroll_area.setWidgetResizable(True)
        self.unresolved_scroll_area.setWidget(self.unresolved_widget_scroll)
        
        # Modify Widget
        # ========================================================================
        # Label
        self.resolved_node_label.setAlignment(QtCore.Qt.AlignCenter)
        self.resolved_file_label.setAlignment(QtCore.Qt.AlignCenter)
        self.resolved_migrate_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.unresolved_node_label.setAlignment(QtCore.Qt.AlignCenter)
        self.unresolved_file_label.setAlignment(QtCore.Qt.AlignCenter)
        self.unresolved_input_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.resolved_label.setFont(boldFont)
        self.resolved_node_label.setFont(boldFont)
        self.resolved_file_label.setFont(boldFont)
        
        self.unresolved_label.setFont(boldFont)
        self.unresolved_node_label.setFont(boldFont)
        self.unresolved_file_label.setFont(boldFont)
        self.unresolved_input_label.setFont(boldFont)

        # Set icon to Button
        self.target_folder_btn.setIcon(QtGui.QIcon(":folder-open"))
        
        # Query OptionVar
        # ========================================================================
        # Line edit
        target_dir_optionVar = cmds.optionVar(q="Migrate_Editor_Target_Directory")
        if not target_dir_optionVar == 0:
            self.target_dir_line_edit.setText(target_dir_optionVar)
        
        
    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
                
        # QWidget as parent for specific layout, for visual purpose
        resolved_qwidget = QtWidgets.QWidget()
        unresolved_qwidget = QtWidgets.QWidget()
        resolved_tab_qwidget = QtWidgets.QWidget()
        unresolved_tab_qwidget = QtWidgets.QWidget()

        # secondary layout    
        target_dir_layout = QtWidgets.QHBoxLayout()
        content_layout = QtWidgets.QVBoxLayout()
        resolved_layout = QtWidgets.QVBoxLayout(resolved_qwidget)
        unresolved_layout = QtWidgets.QVBoxLayout(unresolved_qwidget)
        bottom_layout = QtWidgets.QHBoxLayout()
        
        # tertiary layout
        resolved_tab_layout = QtWidgets.QHBoxLayout(resolved_tab_qwidget)
        resolved_detail_layout = QtWidgets.QHBoxLayout()
        
        unresolved_tab_layout = QtWidgets.QHBoxLayout(unresolved_tab_qwidget)
        unresolved_detail_layout = QtWidgets.QHBoxLayout()
        
        # lower than quternary layout
        self.resolved_content_layout = QtWidgets.QVBoxLayout(self.resolved_widget_scroll)
        self.unresolved_content_layout = QtWidgets.QVBoxLayout(self.unresolved_widget_scroll)
        
        # parent secondary layout to main
        content_layout.addWidget(self.splitter_mid) 
        
        self.splitter_mid.addWidget(resolved_qwidget)
        self.splitter_mid.addWidget(unresolved_qwidget)
        
        main_layout.addLayout(target_dir_layout)
        main_layout.addLayout(content_layout)
        main_layout.addLayout(bottom_layout)
        
        # parent tertiary layout to secondary
        resolved_layout.addWidget(resolved_tab_qwidget)
        resolved_layout.addLayout(resolved_detail_layout)
        resolved_layout.addWidget(self.resolved_scroll_area)
        
        unresolved_layout.addWidget(unresolved_tab_qwidget)
        unresolved_layout.addLayout(unresolved_detail_layout)
        unresolved_layout.addWidget(self.unresolved_scroll_area)
        
        # set alignment
        self.resolved_content_layout.setAlignment(QtCore.Qt.AlignTop)
        self.unresolved_content_layout.setAlignment(QtCore.Qt.AlignTop)
        
        #unresolved_layout.setAlignment(QtCore.Qt.AlignTop)
        
        # add widget to corresponding layout
        target_dir_layout.addWidget(self.target_dir_label)
        target_dir_layout.addWidget(self.target_dir_line_edit)
        target_dir_layout.addWidget(self.target_folder_btn)
        
        resolved_tab_layout.addWidget(self.resolved_label)
        resolved_tab_layout.addWidget(self.resolved_icon_label)
        resolved_tab_layout.addStretch()
        
        resolved_detail_layout.addWidget(self.resolved_node_label)
        resolved_detail_layout.addItem(self.add_spacer())
        resolved_detail_layout.addWidget(self.resolved_file_label)
        resolved_detail_layout.addItem(self.add_spacer())
        resolved_detail_layout.addWidget(self.resolved_migrate_label)
        resolved_detail_layout.addWidget(self.global_checkbox)
        
        unresolved_tab_layout.addWidget(self.unresolved_label)
        unresolved_tab_layout.addWidget(self.unresolved_icon_label)
        unresolved_tab_layout.addStretch()
        
        unresolved_detail_layout.addWidget(self.unresolved_node_label)
        unresolved_detail_layout.addItem(self.add_spacer())
        unresolved_detail_layout.addWidget(self.unresolved_file_label)
        unresolved_detail_layout.addItem(self.add_spacer())
        unresolved_detail_layout.addWidget(self.unresolved_input_label)
        
        bottom_layout.addWidget(self.file_path_editor_btn)
        bottom_layout.addWidget(self.refresh_list_btn)
        bottom_layout.addWidget(self.migrate_btn)
        
        # change Widget background color
        self.resolved_widget_scroll.setStyleSheet("background-color: #333333;")
        self.unresolved_widget_scroll.setStyleSheet("background-color: #333333;")
        resolved_qwidget.setStyleSheet("background-color: #333333;")
        unresolved_qwidget.setStyleSheet("background-color: #333333;")
        resolved_tab_qwidget.setStyleSheet("background-color: #252525;")
        unresolved_tab_qwidget.setStyleSheet("background-color: #252525;")
        
    def create_connections(self):
        # the structure is (widget_name. signals.connect.function that run)
        # lambda acts as outer function from original function
        self.target_folder_btn.clicked.connect(self.store_target_dir_result)
        self.file_path_editor_btn.clicked.connect(self.open_file_path_editor)
        self.refresh_list_btn.clicked.connect(self.refresh_migrate_editor)
        self.migrate_btn.clicked.connect(self.migrate_resolved)
        self.global_checkbox.clicked.connect(self.apply_check_global)
    
    def add_spacer(self,width=0,height=0):
        return QtWidgets.QSpacerItem(width, height, QtWidgets.QSizePolicy.Expanding, 
                                                    QtWidgets.QSizePolicy.Fixed)
    
    def create_file_path_content(self):
        resolved_file_dict = self.find_all_file_path(unresolved=False)
        unresolved_file_dict = self.find_all_file_path(unresolved=True)
        
        if resolved_file_dict == None: return
        if unresolved_file_dict == None: return
        
        for key in resolved_file_dict.keys():
            # Create label for each key and value from dict
            self.resolved_node_content_line = QtWidgets.QLineEdit(key)
            self.resolved_file_name_content_line = QtWidgets.QLineEdit(resolved_file_dict[key])
            self.resolved_migrate_check = QtWidgets.QCheckBox()
            
            # modify widget before passing to scroll area
            self.resolved_migrate_check.setChecked(True)
            
            self.resolved_node_content_line.setReadOnly(True)
            self.resolved_file_name_content_line.setReadOnly(True)
            
            self.resolved_node_content_line.setStyleSheet("background-color: #303030;")
            self.resolved_file_name_content_line.setStyleSheet("background-color: #303030;")
            
            # Create new column inside scroll area
            temp = [self.resolved_node_content_line,
                    self.resolved_file_name_content_line,
                    self.resolved_migrate_check]
            
            dynamic_resolved_layout = QtWidgets.QHBoxLayout()
            for widget in temp:
                dynamic_resolved_layout.addWidget(widget)  
            
            dynamic_resolved_layout.setAlignment(QtCore.Qt.AlignTop)
            self.resolved_content_layout.addLayout(dynamic_resolved_layout)
            
            # Store data to variable
            resolved_content_temp = [key,resolved_file_dict[key],self.resolved_migrate_check]
            resolved_widget_temp = [self.resolved_node_content_line,self.resolved_file_name_content_line,
                                    self.resolved_migrate_check,dynamic_resolved_layout]
                                    
            self.resolved_content_list.append(resolved_content_temp)
            self.resolved_dynamic_widget_list.append(resolved_widget_temp)
        
            
        for key in unresolved_file_dict.keys():
            # Create label for each key and value from dict
            self.unresolved_node_content_line = QtWidgets.QLineEdit(key)
            self.unresolved_file_name_content_line = QtWidgets.QLineEdit(unresolved_file_dict[key])
            self.unresolved_input_content_btn = QtWidgets.QPushButton()
            
            # Create widget connection
            self.unresolved_input_content_btn.clicked.connect(self.explore_input_connection)
            
            # modify widget before passing to scroll area
            self.unresolved_input_content_btn.setIcon(QtGui.QIcon(":input"))
            self.unresolved_input_content_btn.setMaximumHeight(20)
            self.unresolved_input_content_btn.setMaximumWidth(30)
            self.unresolved_input_content_btn.setStyleSheet("background-color: #252525;")
            
            self.unresolved_node_content_line.setReadOnly(True)
            self.unresolved_file_name_content_line.setReadOnly(True)
            self.unresolved_node_content_line.setStyleSheet("background-color: #303030;")
            self.unresolved_file_name_content_line.setStyleSheet("background-color: #303030;")
            
            # Create new column inside scroll area
            temp = [self.unresolved_node_content_line,
                    self.unresolved_file_name_content_line,
                    self.unresolved_input_content_btn]
            
            dynamic_unresolved_layout = QtWidgets.QHBoxLayout()
            for widget in temp:
                dynamic_unresolved_layout.addWidget(widget)  
                #dynamic_layout.addItem(spacer)
                
            dynamic_unresolved_layout.setAlignment(QtCore.Qt.AlignTop)
            self.unresolved_content_layout.addLayout(dynamic_unresolved_layout)
            
            # Store data to variable
            self.unresolved_input_dict[self.unresolved_input_content_btn] = key.rpartition(".")[0]
            
            unresolved_widget_temp = [self.unresolved_node_content_line,
                                      self.unresolved_file_name_content_line,
                                      self.unresolved_input_content_btn,
                                      dynamic_unresolved_layout]
                                      
            self.unresolved_dynamic_widget_list.append(unresolved_widget_temp)
        
    def store_target_dir_result(self):
        target_dir = self.call_fileDialog2(dialog_mode=2,
                                            title_name="Export Resource as",
                                            confirm_caption="Select Folder")
        
        if target_dir == None: return
        self.target_dir_line_edit.setText(target_dir[0])
        cmds.optionVar(sv=("Migrate_Editor_Target_Directory",target_dir[0]))
        
    def explore_input_connection(self,node):
        sender = self.sender()
        file_node = self.unresolved_input_dict.get(sender)
        cmds.select(file_node)
        cmds.workspaceControl('AttributeEditor', e=True, visible=True, r=True)
        
    def apply_check_global(self):
        sender = self.sender()
        if sender.isChecked():
            status = True
        else:
            status = False
            
        for i in self.resolved_content_list:
            i[2].setChecked(status)
    
    def migrate_resolved(self):
        checked_migrate_list = []
        
        # Check first if target directory exist
        if not os.path.isdir(self.target_dir_line_edit.text()):
            cmds.warning("Warning: Target directory not found")
            return
            
        # Save scene as so you can edit attribute live
        migrate_info = self.call_fileDialog2(dialog_mode=0,
                                            title_name="Save Scene As",
                                            confirm_caption="Save")    
        if migrate_info == None: return 
        
        self.save_scene_as(file_dir=migrate_info[0],
                           file_type=migrate_info[2])
        
        # query all checked migrate list
        for item in self.resolved_content_list:
            if item[2].isChecked():
                checked_migrate_list.append(item)
        
        # Move resource file to resource_target_directory and change file attribute
        for item in checked_migrate_list:
            """cmds.sysFile(item[1],copy=self.target_dir_line_edit.text())"""
            if not os.path.exists(self.target_dir_line_edit.text()+"/"+item[1].rpartition("/")[2]):
                shutil.copy(item[1],self.target_dir_line_edit.text())
                
            cmds.setAttr(item[0],self.target_dir_line_edit.text()+"/"+item[1].rpartition("/")[2],type="string")
            cmds.select(cl=1)
            cmds.file(save=1)
            
        
        # Create info dialog (confirm user, the current workspace is updated and operation success)    
        self.call_confirm_dialog(message="Migrate complete""<br>""<br>""Target Resource: {0}""<br>""Current Scene: {1}".format(
                                          self.target_dir_line_edit.text(),
                                          migrate_info[0]),title="Success")

    def refresh_migrate_editor(self):
        # Deactivate button for a while
        duration = 2000
        refresh_btn = self.sender()
 
        # Delete all the UI first
        for item in self.resolved_dynamic_widget_list:
            for widget in item:
                widget.deleteLater()
                widget = None
                if widget == item[-1]:
                    widget.setLayout(None)
            
        for item in self.unresolved_dynamic_widget_list:
            for widget in item:
                widget.deleteLater()
                widget = None
                if widget == item[-1]:
                    widget.setLayout(None)
        
        # Clear cache 
        self.unresolved_input_dict.clear()
        del self.resolved_content_list[:]
        del self.resolved_dynamic_widget_list[:]
        del self.unresolved_dynamic_widget_list[:]
        
        # Reload content
        self.create_file_path_content()
        
    def call_confirm_dialog(self,message,title,icon='information'):
        cmds.confirmDialog(message=message,title=title,icon=icon)
    
# development phase code

if __name__ == "__main__":
    
    try:
        migrateEditorWindow.close()
        migrateEditorWindow.deleteLater()
    except:
        pass
    
    migrateEditorWindow = migrateEditorUI()
    migrateEditorWindow.show()  