import logging
import os
import re
import vtk
from PIL import Image
import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin


#
# vf_helper_module
#

class vf_helper_module(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "vf_helper_module"  # TODO: make this more human readable by adding spaces
        self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#vf_helper_module">module documentation</a>.
"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#

def registerSampleData():
    """
    Add data sets to Sample Data module.
    """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData
    iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # vf_helper_module1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='vf_helper_module',
        sampleName='vf_helper_module1',
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, 'vf_helper_module1.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        fileNames='vf_helper_module1.nrrd',
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums='SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
        # This node name will be used when the data set is loaded
        nodeNames='vf_helper_module1'
    )

    # vf_helper_module2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='vf_helper_module',
        sampleName='vf_helper_module2',
        thumbnailFileName=os.path.join(iconsPath, 'vf_helper_module2.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        fileNames='vf_helper_module2.nrrd',
        checksums='SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
        # This node name will be used when the data set is loaded
        nodeNames='vf_helper_module2'
    )


#
# vf_helper_moduleWidget
#

class vf_helper_moduleWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/vf_helper_module.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = vf_helper_moduleLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML sc

        # New buttons
        self.ui.publishNeedleTipTransform.connect('clicked(bool)', self.onPublishNeedleTipTransform)
        self.ui.publishCauteryTipTransform.connect('clicked(bool)', self.onPublishCauteryTipTransform)
        self.ui.updateAMBFVolumeButton.connect('clicked(bool)', self.onUpdateAMBFVolumeButton)
        self.ui.setUpOpenIGTLinkNodeButton.connect('clicked(bool)', self.onSetUpOpenIGTLinkNodeButton)
        self.ui.updateBreastPluginFile.connect('clicked(bool)', self.onUpdateBreastPluginFile)
        self.ui.resizeVolumeButton.connect('clicked(bool)', self.onResizeVolumeButton)


        # recording and saving
        self.ui.recordUSButton.connect('clicked(bool)', self.onRecordUSButton)
        self.ui.saveUltrasoundButton.connect('clicked(bool)', self.onSaveUltrasoundButton)

        self.ui.recordTrackingButton.connect('clicked(bool)', self.onRecordTrackingButton)
        self.ui.saveTrackingButton.connect('clicked(bool)', self.onSaveTrackingButton)

        self.ui.resetSequencesButton.connect('clicked(bool)', self.onResetSequencesButton)


        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

        # # Record session button
        # self.ui.recordSessionButton.connect('clicked(bool)', self.onRecordSessionButton)

    def cleanup(self):
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self):
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self):
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
        self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    def onSceneStartClose(self, caller, event):
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event):
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self):
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if not self._parameterNode.GetNodeReference("InputVolume"):
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

    def setParameterNode(self, inputParameterNode):
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if inputParameterNode:
            self.logic.setDefaultParameters(inputParameterNode)

        # Unobserve previously selected parameter node and add an observer to the newly selected.
        # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
        # those are reflected immediately in the GUI.
        if self._parameterNode is not None:
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

        # Initial GUI update
        self.updateGUIFromParameterNode()

    def updateGUIFromParameterNode(self, caller=None, event=None):
        """
        This method is called whenever parameter node is changed.
        The module GUI is updated to show the current state of the parameter node.
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
        self._updatingGUIFromParameterNode = True

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

        self._parameterNode.SetNodeReferenceID("InputVolume", self.ui.inputSelector.currentNodeID)
        self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.outputSelector.currentNodeID)
        self._parameterNode.SetParameter("Threshold", str(self.ui.imageThresholdSliderWidget.value))
        self._parameterNode.SetParameter("Invert", "true" if self.ui.invertOutputCheckBox.checked else "false")
        self._parameterNode.SetNodeReferenceID("OutputVolumeInverse", self.ui.invertedOutputSelector.currentNodeID)

        self._parameterNode.EndModify(wasModified)

    def onApplyButton(self):
        """
        Run processing when user clicks "Apply" button.
        """
        with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):

            # Compute output
            self.logic.process(self.ui.inputSelector.currentNode(), self.ui.outputSelector.currentNode(),
                               self.ui.imageThresholdSliderWidget.value, self.ui.invertOutputCheckBox.checked)

            # Compute inverted output (if needed)
            if self.ui.invertedOutputSelector.currentNode():
                # If additional output volume is selected then result with inverted threshold is written there
                self.logic.process(self.ui.inputSelector.currentNode(), self.ui.invertedOutputSelector.currentNode(),
                                   self.ui.imageThresholdSliderWidget.value, not self.ui.invertOutputCheckBox.checked, showResult=False)

    def onPublishNeedleTipTransform(self):

        self.logic.publishNeedleTipTransform()

    def onPublishCauteryTipTransform(self):

        self.logic.publishCauteryTipTransform()

    def onUpdateAMBFVolumeButton(self):

        self.logic.exportModelAsLabelMap()
        self.logic.auto_run_ambf_utils(self.ui.pathLineEdit.text)

    def onSetUpOpenIGTLinkNodeButton(self):

        self.logic.setupOpenIGTLinkNode()

    def onUpdateBreastPluginFile(self):
        self.logic.onUpdateBreastPluginFile(self.ui.pathLineEdit.text)

    def onResizeVolumeButton(self):
        self.logic.resizeVolumeFromAMBF()

    def onRecordUSButton(self):

        self.logic.recordUSData()

    def onSaveUltrasoundButton(self):
        self.logic.saveUSRecording(self.ui.participantNumberLineEdit.text)

    def onRecordTrackingButton(self):
        self.logic.recordTrackingData()

    def onSaveTrackingButton(self):
        self.logic.saveTrackingButton(self.ui.participantNumberLineEdit.text)

    def onResetSequencesButton(self):

        self.logic.onResetSequencesButton()



#
# vf_helper_moduleLogic
#

class vf_helper_moduleLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)




    def setDefaultParameters(self, parameterNode):
        """
        Initialize parameter node with default settings.
        """
        if not parameterNode.GetParameter("Threshold"):
            parameterNode.SetParameter("Threshold", "100.0")
        if not parameterNode.GetParameter("Invert"):
            parameterNode.SetParameter("Invert", "false")

    def publishNeedleTipTransform(self):
        self.ros2 = slicer.util.getModuleLogic('ROS2')
        self.node = self.ros2.GetDefaultROS2Node()
        self.NeedleTipToNeedle = slicer.mrmlScene.GetFirstNodeByName('NeedleTipToNeedle')
        if self.NeedleTipToNeedle is None:
            print("Transform NeedleTipToNeedle is not in the scene")
            return
        self.node.CreateAndAddPublisherNode('vtkMRMLROS2PublisherPoseStampedNode', 'NeedleTipToNeedle')
        publisher = slicer.mrmlScene.GetFirstNodeByName('ros2:pub:NeedleTipToNeedle')
        publisher.Publish(self.NeedleTipToNeedle.GetMatrixTransformToParent())


    def publishCauteryTipTransform(self):
        self.ros2 = slicer.util.getModuleLogic('ROS2')
        self.node = self.ros2.GetDefaultROS2Node()
        self.CauteryTipToCautery = slicer.mrmlScene.GetFirstNodeByName('CauteryTipToCautery')
        if self.CauteryTipToCautery is None:
            print("Transform CauteryTipToCautery is not in the scene")
            return
        self.node.CreateAndAddPublisherNode('vtkMRMLROS2PublisherPoseStampedNode', 'CauteryTipToCautery') # sometimes just PoseStamped as first arguement
        publisher = slicer.mrmlScene.GetFirstNodeByName('ros2:pub:CauteryTipToCautery')
        publisher.Publish(self.CauteryTipToCautery.GetMatrixTransformToParent())

    def process(self, inputVolume, outputVolume, imageThreshold, invert=False, showResult=True):
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param inputVolume: volume to be thresholded
        :param outputVolume: thresholding result
        :param imageThreshold: values above/below this threshold will be set to 0
        :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
        :param showResult: show output volume in slice viewers
        """

        if not inputVolume or not outputVolume:
            raise ValueError("Input or output volume is invalid")

        import time
        startTime = time.time()
        logging.info('Processing started')

        # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
        cliParams = {
            'InputVolume': inputVolume.GetID(),
            'OutputVolume': outputVolume.GetID(),
            'ThresholdValue': imageThreshold,
            'ThresholdType': 'Above' if invert else 'Below'
        }
        cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
        # We don't need the CLI module node anymore, remove it to not clutter the scene with it
        slicer.mrmlScene.RemoveNode(cliNode)

        stopTime = time.time()
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')

    def exportModelAsLabelMap(self):

        modelNode = slicer.mrmlScene.GetFirstNodeByName('TumorModel')
        modelNode.SetAndObserveTransformNodeID(None)
        self.model_to_label_map(modelNode, "TumorLabelMap")
        modelNode.SetAndObserveTransformNodeID(slicer.mrmlScene.GetFirstNodeByName('NeedleToReference').GetID())


    def model_to_label_map(self, model_node, output_volume_name):
        segmentation_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
        segmentation_node.CreateDefaultDisplayNodes()
        segmentation_node.SetName("Segmentation")

        slicer.modules.segmentations.logic().ImportModelToSegmentationNode(model_node, segmentation_node)
        segmentation_node.CreateClosedSurfaceRepresentation()

        label_map_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
        label_map_node.SetName(output_volume_name)

        slicer.modules.segmentations.logic().ExportVisibleSegmentsToLabelmapNode(segmentation_node, label_map_node) # not sure what third should be

        # Clean up
        slicer.mrmlScene.RemoveNode(segmentation_node)

        return label_map_node

    def setupOpenIGTLinkNode(self):

        connectorNode = slicer.vtkMRMLIGTLConnectorNode()
        connectorNode.SetName("MyIGTLinkConnector")
        slicer.mrmlScene.AddNode(connectorNode)
        connectorNode.SetTypeClient('169.254.184.175', 18944)
        connectorNode.Start()

        connectorNode = slicer.vtkMRMLIGTLConnectorNode()
        connectorNode.SetName("Camera")
        slicer.mrmlScene.AddNode(connectorNode)
        connectorNode.SetTypeClient('169.254.184.175', 18945)
        connectorNode.Start()


    def auto_run_ambf_utils(self, output_directory):

        label_map_volume_name = "TumorLabelMap"
        module_widget = slicer.modules.AMBF_utilsWidget

        module_widget.outputDirSelector.setCurrentPath(output_directory)

        label_map_volume = slicer.util.getNode(label_map_volume_name)
        if label_map_volume:
            module_widget.segmentLabelMapSelector.setCurrentNode(label_map_volume)

        module_widget.imagePrefix.text = "slice"
        module_widget.exportLabelMapAsGrayscale.checked = False

        module_widget.onExportLabelMapButton()
        module_widget.showAmbfOrigin.setChecked(False)
        module_widget.enableLabelMapRenderingAtAmbfPose.setChecked(False)
        module_widget.enableLabelMapVolumeRendering.setChecked(False)

    def onUpdateBreastPluginFile(self, file1_path):

        file1_path = file1_path + "volume.yaml"

        file2_path = "/home/lauraconnolly/vf_deepdive/simulation/breast_plugin/ADF/volume.yaml"
        with open(file1_path, 'r') as file:
            file1_contents = file.read()

        with open(file2_path, 'r') as file:
            file2_contents = file.read()

        count_pattern = r'count: (\d+)'
        dimensions_pattern = r'dimensions: \{x: ([\d.]+), y: ([\d.]+), z: ([\d.]+)\}'
        position_pattern = r'position: \{x: ([-\d.]+) , y: ([-\d.]+), z: ([-\d.]+)\}'
        scale_pattern = r'scale: [\d.]+'

        count = re.search(count_pattern, file1_contents).group(1)
        dimensions = re.search(dimensions_pattern, file1_contents).group(0)
        position_match = re.search(position_pattern, file1_contents)
        position = f"position: {{x: {-float(position_match.group(1)) * 10} , y: {-float(position_match.group(2)) * 10}, z: {float(position_match.group(3)) * 10}}}"

        file2_contents = re.sub(count_pattern, f'count: {count}', file2_contents)
        file2_contents = re.sub(dimensions_pattern, dimensions, file2_contents)
        file2_contents = re.sub(position_pattern, position, file2_contents)
        file2_contents = re.sub(scale_pattern, 'scale: 10.0', file2_contents)

        with open(file2_path, 'w') as file:
            file.write(file2_contents)

    def resizeVolumeFromAMBF(self):
        scale = 0.5  # Resize to 50% of the original size
        output_folder = "/home/lauraconnolly/vf_deepdive/AMBF_volumes/volume/"
        input_folder = "/home/lauraconnolly/vf_deepdive/AMBF_volumes/volume/"
        # Ensure output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for filename in os.listdir(input_folder):
            if filename.endswith(".png"):
                input_path = os.path.join(input_folder, filename)
                output_path = os.path.join(output_folder, filename)

                with Image.open(input_path) as img:
                    new_width = int(img.width * scale)
                    new_height = int(img.height * scale)

                    resized_img = img.resize((new_width, new_height))

                    resized_img.save(output_path)

    def recordUSData(self):
        sequenceBrowser = slicer.mrmlScene.GetFirstNodeByName("UltrasoundSequenceBrowser")
        sequenceBrowser.SetRecordingActive(True)

    def saveUSRecording(self, participantID):
        sequenceBrowser = slicer.mrmlScene.GetFirstNodeByName("UltrasoundSequenceBrowser")
        sequenceBrowser.SetRecordingActive(False)
        save_directory = "/home/lauraconnolly/Desktop/UserStudyData/participant" + participantID + "/sceneWUSRecording.mrb"
        success = slicer.util.saveScene(save_directory)
        print("All sequences saved successfully.")

    def recordTrackingData(self):
        print("Recording tracking data")
        sequenceBrowser = slicer.mrmlScene.GetFirstNodeByName("TrackingSequenceBrowser")
        sequenceLogic = slicer.modules.sequences.logic()
        image = slicer.mrmlScene.GetFirstNodeByName("ImageRGB_ImageRGB")
        seqNode = sequenceLogic.AddSynchronizedNode(None, image, sequenceBrowser)
        sequenceBrowser.SetRecording(seqNode, True)
        sequenceBrowser.SetRecordingActive(True)

    def saveTrackingButton(self, participantID):

        sequenceBrowser = slicer.mrmlScene.GetFirstNodeByName("TrackingSequenceBrowser")
        sequenceBrowser.SetRecordingActive(False)
        save_directory = "/home/lauraconnolly/Desktop/UserStudyData/participant" + participantID + "/sceneWUSAndTrackingRecording.mrb"
        success = slicer.util.saveScene(save_directory)
        print("All sequences saved successfully.")

    def onResetSequencesButton(self):

        browserNode = slicer.util.getNode('TrackingSequenceBrowser')

        if browserNode.GetRecordingActive():
            browserNode.SetRecordingActive(False)

        sequenceNodes = slicer.util.getNodesByClass('vtkMRMLSequenceNode')
        for sequenceNode in sequenceNodes:
            associatedBrowserNode = slicer.modules.sequences.logic().GetFirstBrowserNodeForSequenceNode(sequenceNode)
            if associatedBrowserNode and associatedBrowserNode.GetID() == browserNode.GetID():
                sequenceNode.RemoveAllDataNodes()


#
# vf_helper_moduleTest
#

class vf_helper_moduleTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_vf_helper_module1()

    def test_vf_helper_module1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

        # Get/create input data

        import SampleData
        registerSampleData()
        inputVolume = SampleData.downloadSample('vf_helper_module1')
        self.delayDisplay('Loaded test data set')

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        threshold = 100

        # Test the module logic

        logic = vf_helper_moduleLogic()

        # Test algorithm with non-inverted threshold
        logic.process(inputVolume, outputVolume, threshold, True)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], threshold)

        # Test algorithm with inverted threshold
        logic.process(inputVolume, outputVolume, threshold, False)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], inputScalarRange[1])

        self.delayDisplay('Test passed')
