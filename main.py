#!/usr/bin/env python
'''
formerly (from KivyPixels) kivyspritetouch.py
based on http://kivy.org/docs/examples/gen__canvas__fbo_canvas__py.html

'''
try:
    import kivy
except ImportError as ex:
    print("This program requires kivy. Try:")
    print("python -m pip install --user --upgrade pip")
    print("python -m pip install --user --upgrade setuptools wheel")
    print("python -m pip install --user --upgrade kivy")
    exit(1)

from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.colorpicker import ColorPicker
# from kivy.uix.button import Button
import os
# from kivy.graphics.instructions import InstructionGroup

# from kivy.graphics import Color, Rectangle
# from kivy.graphics import Line
from kivymd.app import MDApp
# from kivy.core.window import Window
# from kivy.animation import Animation
# from kivy.factory import Factory
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.metrics import dp
from kivy.clock import Clock
# from kivy.graphics import Ellipse
# from kivy.uix.image import Image
# from kivy.core.image import Image as CoreImage

# import os
# from kivy.graphics import Point
# import random
# TODO: implement resize
# from array import array

# from pythonpixels import PPImage
# from pythonpixels import PPColor
# class MainForm(BoxLayout):
from rotocanvas.kivypixels.pixelwidget import PixelWidget
from rotocanvas.kivypixels.colorpopup import ColorPopup
from rotocanvas import (
    echo0,
)

class RotoCanvasApp(MDApp):

    def build(self):
        self.pixelWidget = None

        self.mainWidget = MDFloatLayout(
            # orientation='horizontal',
            md_bg_color='black',
        )

        self.pixelWidget = PixelWidget()
        self.mainWidget.add_widget(self.pixelWidget)
        self.spacing = dp(8)
        self.margin = dp(8)
        # spacing = self.spacing
        # margin = self.margin
        m_ratio = .01  # Fixed later
        '''
        self.buttonsLayout = MDBoxLayout(
            orientation='vertical',
            size_hint=(.1, 1.0),
            spacing=spacing,
            padding=(margin, margin, margin, margin),
        )
        self.mainWidget.add_widget(self.buttonsLayout)
        '''

        self.paletteWidget = ColorPopup(self.choseColor,
                                        size_hint=(.9, .8))
        self.right_edge_ratio = 1.0 - m_ratio  # fixed later
        self.saveButton = MDFloatingActionButton(
            text="Save",
            icon='content-save',
            on_press=self.pixelWidget.onSaveButtonClick,
            pos_hint={"right": self.right_edge_ratio, "top": 1.0-m_ratio},
            # ^ fixed later.
        )
        self.mainWidget.add_widget(self.saveButton)
        self.previous_button = None
        self.initialized = False
        Clock.schedule_once(self.add_relative_widgets, 1)
        return self.mainWidget

    def add_relative_widgets(self, _):
        '''
        Add widgets that are positioned based on ratios. This 
        must be scheduled since the ratio of the widget width to the
        window's greatest dimension has to be determined, and those
        dimensions can only be determined after the window is
        displayed for at least one frame.
        '''
        self.initialized = True
        self.pack_button(self.saveButton, add=False)
        
        self.paletteButton = MDFloatingActionButton(
            text="Palette",
            icon='palette',
            on_press=self.paletteWidget.open,
        )
        self.pack_button(self.paletteButton)

        '''
        # self.colorButton = MDFloatingActionButton(text="Color",
                                          # id="colorButton")
        # self.buttonsLayout.add_widget(self.colorButton)
        # self.colorButton.bind(on_press=self.pixelWidget.onColorButtonClick)

        # self.eraserButton = MDFloatingActionButton(text="Eraser",
                                           # id="eraserButton")
        # self.buttonsLayout.add_widget(self.eraserButton)
        # self.eraserButton.bind(
            # on_press=self.pixelWidget.onEraserButtonClick)
        '''

    def pack_button(self, button, add=True):
        '''
        Keyword arguments:
        add -- Add to mainWidget.
        '''
        if not self.initialized:
            raise RuntimeError(
                "pack_button can only work after at least 1 frame."
            )
        spacing = self.spacing
        margin = self.margin

        greater_dim = self.mainWidget.width
        if self.mainWidget.height > self.mainWidget.width:
            greater_dim = self.mainWidget.height

        b_ratio = self.saveButton.width / greater_dim
        # ^ For this to work, saveButton must be added on a frame
        #   *before* this method runs!
        s_ratio = spacing / greater_dim
        m_ratio = margin / greater_dim
        r_ratio = 1.0 - m_ratio
        f_ratio = 1.0 - m_ratio  # first button (bottom)
        echo0(f"\nbutton: {button.text}")
        echo0(f"s_ratio: {s_ratio}")  # ~.01
        echo0(f"m_ratio: {m_ratio}")  # ~.01
        echo0(f"r_ratio: {r_ratio}")  # ~.99
        echo0(f"b_ratio: {b_ratio}")  # ~.07
        echo0(f"f_ratio: {f_ratio}")  # ~.01
        if self.previous_button is not None:
            echo0(f"self.previous_button.pos: {self.previous_button.pos}")
            echo0(f"self.previous_button.width: {self.previous_button.width}")
        echo0(f"self.mainWidget.width: {self.mainWidget.width}")
        top = f_ratio
        if self.previous_button is not None:
            prev_bottom = (self.previous_button.pos[1]/self.mainWidget.height)
            echo0(f"prev_bottom: {prev_bottom}")
            top = prev_bottom - m_ratio
            echo0(f"top: {top}")
        button.pos_hint = {
            "top": top,  # bottom does not work on MDFloatLayout
            "right": f_ratio,
        }
        if add:
            self.mainWidget.add_widget(button)
        self.previous_button = button

    def choseColor(self, color):
        if color is not None:
            self.pixelWidget.viewImage.setBrushColor(color)

    def saveBrush(self):
        if self.brushImage is not None:
            self.brushImage.saveAs(
                "debug save (brush).png",
                texture_flipped=self.texture_flipped,
            )
        # normalSize = self.brushImage.get_norm_image_size()
        # self.brushImage.size = (int(normalSize[0]), int(normalSize[1]))
        # data = bytes(self.brushImage.data)
        # # convert from bytearray to bytes
        # surface = pygame.image.fromstring(data,
        # self.brushImage.size,
        # 'RGBA',
        # True)
        # pygame.image.save(surface, "debug save (brush).png")


if __name__ == "__main__":
    RotoCanvasApp().run()
