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


class RotoCanvasApp(MDApp):

    def build(self):
        self.pixelWidget = None

        self.mainWidget = MDBoxLayout(
            orientation='horizontal',
            md_bg_color='black',
        )

        self.pixelWidget = PixelWidget()
        self.mainWidget.add_widget(self.pixelWidget)

        self.buttonsLayout = MDBoxLayout(
            orientation='vertical',
            size_hint=(.1, 1.0),
            spacing='8dp',
            padding=('8dp','8dp','8dp','8dp'),
        )
        self.mainWidget.add_widget(self.buttonsLayout)

        self.paletteWidget = ColorPopup(self.choseColor,
                                        size_hint=(.9, .8))

        self.saveButton = MDFloatingActionButton(
            text="Save",
            icon='content-save',
        )
        # id="saveButton"
        self.buttonsLayout.add_widget(self.saveButton)
        self.saveButton.bind(on_press=self.pixelWidget.onSaveButtonClick)

        self.paletteButton = MDFloatingActionButton(
            text="Palette",
            icon='palette',
        )
        # id="paletteButton"
        self.buttonsLayout.add_widget(self.paletteButton)
        self.paletteButton.bind(on_press=self.paletteWidget.open)
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
        return self.mainWidget

    def choseColor(self, color):
        if color is not None:
            self.pixelWidget.viewImage.setBrushColor(color)

    def saveBrush(self):
        if self.brushImage is not None:
            self.brushImage.saveAs("debug save (brush).png")
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
