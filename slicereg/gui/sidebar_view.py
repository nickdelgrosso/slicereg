from functools import partial

from PySide2.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QButtonGroup, \
    QHBoxLayout, QLabel, QSlider
from PySide2.QtCore import Qt

from slicereg.gui.base import BaseQtView
from slicereg.gui.slider import LabelledSliderWidget


class SidebarView(BaseQtView):

    def __init__(self):

        self.widget = QWidget()

        layout = QVBoxLayout()
        self.widget.setLayout(layout)

        # Section Buttons
        load_image_button = QPushButton("Load Section")
        layout.addWidget(load_image_button)
        load_image_button.clicked.connect(self.show_load_image_dialog)

        load_image_button2 = QPushButton("Quick Load Section")
        layout.addWidget(load_image_button2)
        load_image_button2.clicked.connect(lambda: self.load_section("data/RA_10X_scans/MeA/S1_07032020.ome.tiff"))

        # Scale Slider (Set Section Resolution)
        self.resample_widget = LabelledSliderWidget(min=15, max=200, label="Scale")
        layout.addLayout(self.resample_widget.layout)
        self.resample_widget.connect(lambda val: self.set_section_image_resolution(val))

        self.dim_widgets = []
        for dim in ['right', 'superior', 'anterior', 'rot_lateral', 'rot_axial', 'rot_median']:
            widget = LabelledSliderWidget(min=-10000 if not dim.startswith('rot_') else -180, max=10000 if not dim.startswith('rot_') else 180, label=dim)
            layout.addLayout(widget.layout)
            fun = lambda d, value: self.transform_section(**{d: value})
            widget.connect(partial(fun, dim))
            self.dim_widgets.append((widget, fun))

        # Atlas BUttons
        button_hbox = QHBoxLayout()
        layout.addLayout(button_hbox)

        atlas_buttons = QButtonGroup(self.widget)
        atlas_buttons.setExclusive(True)
        atlas_buttons.buttonToggled.connect(self.atlas_button_toggled)
        

        for resolution in [100, 25, 10]:
            atlas_button = QPushButton(f"{resolution}um")
            atlas_button.setCheckable(True)
            button_hbox.addWidget(atlas_button)
            atlas_buttons.addButton(atlas_button)

            # The 10um atlas takes way too long to download at the moment.
            # It needs some kind of progress bar or async download feature to be useful.
            # The disabled button here shows it as an option for the future, but keeps it from being used.
            if resolution == 10:
                atlas_button.setDisabled(True)

    @property
    def qt_widget(self) -> QWidget:
        return self.widget

    def show_load_image_dialog(self):
        filename, filetype = QFileDialog.getOpenFileName(
            parent=self.qt_widget,
            caption="Load Image",
            dir="../data/RA_10X_scans/MEA",
            filter="OME-TIFF (*.ome.tiff)"
        )
        if not filename:
            return
        self.load_section(filename=filename)

    def atlas_button_toggled(self, button: QPushButton, is_checked: bool):
        if not is_checked:  # Don't do anything for the button being unselected.
            return

        resolution_label = button.text()
        resolution = int("".join(filter(str.isdigit, resolution_label)))
        self.load_atlas(resolution=resolution)

    # Comand Routing
    def load_section(self, filename: str):
        raise NotImplementedError("Connect to a LoadImageCommand before using.")

    def transform_section(self, **kwargs):
        raise NotImplementedError("Connect to UpdateSectionTransformCommand before using.")
    
    def set_section_image_resolution(self, resolution_um: float):
        raise NotImplementedError("Connect to ResampleSectionCommand before using.")
        
    def load_atlas(self, resolution: int):
        raise NotImplementedError("Connect to LoadAtlasCommand before using.")

