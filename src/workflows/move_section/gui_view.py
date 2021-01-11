from dataclasses import dataclass

from numpy.core._multiarray_umath import ndarray

from src.gui.window import Window
from src.workflows.move_section.presenter import BaseView


@dataclass
class GuiView(BaseView):
    win: Window

    def update_transform(self, transform: ndarray):
        self.win.volume_view.update_transform(transform=transform)

    def show_error(self, msg: str):
        self.win.show_temp_title(title=msg)