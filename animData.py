# 23456789+123456789+123456789+123456789+123456789+123456789+123456789+1@345678|
import maya.cmds as cmds
import maya.OpenMayaUI as omui
import json
import os
from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance

""" OBJECTIVE: Tool that will copy the animation data of a character/model and 
    paste all the data on to character of the same physicalities. If a rig or
    character breaks this tool comes in handy so no animation data is lost"""

def get_maya_main_win():
    """Return the Maya main window widget"""
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QtWidgets.QWidget)

class AnimationDataTool(QtWidgets.QDialog):
    """Grid out cylinder face class"""
    """window tool class"""

    def __init__(self):
        """Initialise the object"""
        super(AnimationDataTool, self).__init__(parent=get_maya_main_win())
        self._set_win()
        self._define_widgets()
        self._layout_widgets()
        self._connect_signals_slots()

    def _set_win(self):
        """Window Settings"""
        self.setWindowTitle("Transfer Animation Tool")
        self.resize(300, 100)

    def _define_widgets(self):
        #self.selectAnim_btn = QtWidgets.QPushButton("Select Animation")
        self.inputText1_txt = QtWidgets.QLineEdit()
        self.transferAnim_btn = QtWidgets.QPushButton("Transfer Animation")
        self.inputText2_txt = QtWidgets.QLineEdit()

    def _layout_widgets(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.inputText1_txt)
        #self.main_layout.addWidget(self.selectAnim_btn)
        self.main_layout.addWidget(self.inputText2_txt)
        self.main_layout.addWidget(self.transferAnim_btn)
        self.setLayout(self.main_layout)

    def _connect_signals_slots(self):
        #self.selectAnim_btn.clicked.connect(self.selectAnimationData)
        self.transferAnim_btn.clicked.connect(self.transferAnimationData)

    """@QtCore.Slot()
    def selectAnimationData(self):
        selection_data(name=self.inputText1_txt.text())"""

    @QtCore.Slot()
    def transferAnimationData(self):
        selection_data(name_1=self.inputText1_txt.text(), name_2=self.inputText2_txt.text())
        transfer_data(name=self.inputText2_txt.text())


# Get the user's home directory
home_dir = os.path.expanduser("~")

# Create a subdirectory within the home directory to store the output file
output_dir = os.path.join(home_dir, "AnimationData")
os.makedirs(output_dir, exist_ok=True)

# Generate the output file path
output_file = os.path.join(output_dir, "animation_data.json")

selections = []


def selection_data(name_1="", name_2=""):
    """ FOR CURRENT CHARACTER """
    # Select all the transforms in the maya scene
    transforms = cmds.ls(transforms=True)

    # create dictionary to store animation data
    animation_data = {}

    # for each transform, select the ones that have both animation data
    # (transforms w/ keyframes) and text entered by user in their label
    # Then select animation data (data in graph editor) of all selected transforms
    for transform in transforms:
        # defines variables to check if transform selected has any keyframes
        keys = cmds.keyframe(transform, query=True)
        # select transform if it has key frames & if text entered is included in label
        if keys and name_1 in transform:
            cmds.select(transform, add=True)
            selections.append(transform)

        # select data in graph editor for each transform
        selected = cmds.selectKey(transform, add=True)

        # Get the selected attributes in the graph editor
        if selected:
            selected_attributes = cmds.keyframe(query=True, name=True)

            for attributes in selected_attributes:
                keyframe_data = cmds.keyframe(attributes, query=True, timeChange=True, valueChange=True)

                # replace name of original model with newly imported model name
                if name_1 in attributes:
                    attributes = attributes.replace(name_1, name_2)

                # Store the keyframe data in the animation dictionary
                animation_data[attributes] = {
                    'times': keyframe_data[::2],  # Time values
                    'values': keyframe_data[1::2]  # Attribute values
                }

    # Save the animation data dictionary to the output JSON file
    with open(output_file, 'w') as file:
        json.dump(animation_data, file, indent=4)

    print(f"Animation data saved to {output_file}")


def transfer_data(name=""):
    """ FOR NEWLY IMPORTED CHARACTER """

    # if there are any selections in scene make sure everything is deselected
    cmds.select(clear=True)

    # file path of json file
    file_path = output_file

    # read json file w data
    data_file = open(file_path, 'r')
    data = data_file.read()

    # parse the data from the json file
    animation_data = json.loads(data)

    # Select all the transforms in the maya scene on the newly imported character rig
    new_transforms = cmds.ls(transforms=True)

    # cmds.setKeyframe('malcolm_v201:ctlAnkleGimbalRt', attribute='rotateZ', time=0.0, value=1.0)

    # put all attribute names in set to establish what tranforms are in the file
    for attr_name, data in animation_data.items():
        times = data['times']
        values = data['values']

        no_name = ''
        namespace = ''

        for trans in new_transforms:
            if name in trans:
                no_name = trans.replace(name, "")
                name = trans.replace(no_name, "")
                namespace = name + no_name[0]
                break

        # Set keyframes for each time and value
        for i in range(len(times)):
            # define variable outside 'if-elif' scope
            # variable hold the attribute that needs to be set
            set_attribute = ''
            key_name = ''

            # Set the keyframe on the specified control
            if cmds.objExists(attr_name):
                if 'rotate' in attr_name:
                    index = attr_name.index('rotate')
                    char = attr_name[index + len('rotate')]
                    set_attribute = 'rotate' + char
                    key_name = attr_name[:index]
                elif 'scale' in attr_name:
                    index = attr_name.index('scale')
                    char = attr_name[index + len('scale')]
                    set_attribute = 'scale' + char
                    key_name = attr_name[:index]
                elif 'translate' in attr_name:
                    index = attr_name.index('translate')
                    char = attr_name[index + len('translate')]
                    set_attribute = 'translate' + char
                    key_name = attr_name[:index]
                elif 'smoothCuff' in attr_name:
                    index = attr_name.index('smoothCuff')
                    set_attribute = 'smoothCuff'
                    key_name = attr_name[:index]
                elif 'ik' in attr_name:
                    index = attr_name.index('ik')
                    set_attribute = 'ik'
                    key_name = attr_name[:index]
                elif 'heelPress' in attr_name:
                    index = attr_name.index('heelPress')
                    set_attribute = 'heelPress'
                    key_name = attr_name[:index]
                elif 'toeSquash' in attr_name:
                    index = attr_name.index('toeSquash')
                    set_attribute = 'toeSquash'
                    key_name = attr_name[:index]
                elif 'heelSquash' in attr_name:
                    index = attr_name.index('heelSquash')
                    set_attribute = 'heelSquash'
                    key_name = attr_name[:index]
                elif 'toeRaise' in attr_name:
                    index = attr_name.index('toeRaise')
                    set_attribute = 'toeRaise'
                    key_name = attr_name[:index]
                elif 'hyperExtend' in attr_name:
                    index = attr_name.index('hyperExtend')
                    set_attribute = 'hyperExtend'
                    key_name = attr_name[:index]
                elif 'footRoll' in attr_name:
                    index = attr_name.index('footRoll')
                    set_attribute = 'footRoll'
                    key_name = attr_name[:index]
                elif 'autoStretch' in attr_name:
                    index = attr_name.index('autoStretch')
                    set_attribute = 'autoStretch'
                    key_name = attr_name[:index]
                elif 'legUpLength' in attr_name:
                    index = attr_name.index('legUpLength')
                    set_attribute = 'legUpLength'
                    key_name = attr_name[:index]
                elif 'legLoLength' in attr_name:
                    index = attr_name.index('legLoLength')
                    set_attribute = 'legLoLength'
                    key_name = attr_name[:index]
                elif 'tilt' in attr_name:
                    index = attr_name.index('tilt')
                    set_attribute = 'tilt'
                    key_name = attr_name[:index]
                elif 'kneeRoll' in attr_name:
                    index = attr_name.index('kneeRoll')
                    set_attribute = 'kneeRoll'
                    key_name = attr_name[:index]
                elif 'world' in attr_name:
                    index = attr_name.index('world')
                    set_attribute = 'world'
                    key_name = attr_name[:index]
                elif 'hips' in attr_name:
                    index = attr_name.index('hips')
                    set_attribute = 'hips'
                    key_name = attr_name[:index]
                elif 'kneePin' in attr_name:
                    index = attr_name.index('kneePin')
                    set_attribute = 'kneePin'
                    key_name = attr_name[:index]
                elif 'visibility' in attr_name:
                    index = attr_name.index('visibility')
                    set_attribute = 'visibility'
                    key_name = attr_name[:index]

                key_name = key_name[:-1]
                keyframe = namespace + key_name
                print('Frame - ' + keyframe)
                print('attr_name - ' + attr_name)

                cmds.setKeyframe(keyframe, attribute=set_attribute, time=times[i], value=values[i])


window = AnimationDataTool()
window.show()

if __name__ == "__main__":
    pass