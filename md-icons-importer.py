import os
from guizero import App, TextBox, Box, Picture, Text
from PIL import Image
import cairosvg

class SearchResult:
    def __init__(self):
        self.widgets = []

class IconSearchApp:
    def __init__(self):
        self._last_search_time = 0
        self._names = None
        self._results = []
        self._images = {}
        self._svg_dir = os.path.expanduser("~/Downloads/git/Templarian/MaterialDesign/svg")

        self.app = App("Icon Search", width=800, height=600, layout="grid")

        # Search bar
        self.search_var = ""
        self.search_entry = TextBox(
            self.app,
            command=self.on_search_var_changed,
            grid=[0, 0],
            width=50
        )

        # Results area
        self.results_box = Box(self.app, layout="grid", grid=[0, 1], width="fill", height="fill")

        # Status bar
        self.status_var = ""
        self.status_entry = TextBox(
            self.app,
            text=self.status_var,
            readonly=True,
            grid=[0, 2],
            width=50
        )

        # Start the directory scanning
        self.app.after(100, self._load_icon_names)
        self.app.display()

    def _load_icon_names(self):
        if os.path.isdir(self._svg_dir):
            self._names = os.listdir(self._svg_dir)
        else:
            self.set_status("{} does not exist".format(repr(self._svg_dir)))

    def set_status(self, message):
        self.status_var = message
        self.status_entry.value = message

    def on_search_var_changed(self):
        search_text = self.search_entry.value
        if len(search_text) >= 2:
            self.app.after(100, self.search)
        else:
            self.clear()

    def search(self):
        if self._names is None:
            return
        self.clear()
        query = self.search_entry.value.lower()
        for name in self._names:
            if query in name.lower():
                self._add_result(name)

    def _add_result(self, name):
        image = self._images.get(name)
        if image is None:
            file_path = os.path.join(self._svg_dir, name)
            if os.path.splitext(name)[1].lower() == ".svg":
                png_data = cairosvg.svg2png(url=file_path)
                image = Image.open(io.BytesIO(png_data)).convert("RGBA")
            else:
                image = Image.open(file_path).convert("RGBA")
            self._images[name] = image

        result = SearchResult()

        # Image widget
        img_widget = Picture(
            self.results_box,
            image=image,
            grid=[0, len(self._results)]
        )
        result.widgets.append(img_widget)

        # Label widget
        label_widget = Text(
            self.results_box,
            text=name,
            grid=[1, len(self._results)]
        )
        result.widgets.append(label_widget)

        self._results.append(result)

    def clear(self):
        for result in self._results:
            for widget in result.widgets:
                widget.hide()
        self._results.clear()

if __name__ == "__main__":
    IconSearchApp()
