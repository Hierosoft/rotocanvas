"""
Import Material Design Icons into assets, converting svg to png.

Search Examples:
some: 1 result: font-awesome.svg
"""
from collections import OrderedDict
import threading
import cairosvg
import io
import os
import time
import tkinter as tk
import sys

from guizero import (
    App,
    TextBox,
    Box,
    Picture,
    Text,
)
from logging import getLogger
from PIL import Image
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter.ttk import Progressbar

from rotocanvas import ASSETS_DIR  # recommended by guizero:
#   <https://github.com/lawsie/guizero/issues/238#issuecomment-500101223>
APP_ROOT = os.path.dirname(os.path.realpath(__file__))

logger = getLogger(__name__)


class SearchResult:
    def __init__(self, name, row):
        self.widgets = []
        self.image = None
        self.picture = None
        self.name = name
        self.row = row


class IconSearchApp(App):
    def __init__(self):
        App.__init__(
            self,
            "Material Design Icons Importer",
            width=1280,
            height=800,
            # layout="grid",
        )
        self.ratio = None
        self.loading_ratio = None
        self.loading_idx = 0
        self.threads = OrderedDict()
        self._cancel_loading = False
        self.load_images_thread = None
        self.search_thread = None
        self.optional_q = OrderedDict()
        self._query_quick_lengths = {}
        self._last_search_time = 0
        self._names = None
        self._results = []
        self._results_of = None
        self._images = {}
        self._svg_dir = os.path.expanduser("~/Downloads/git/Templarian/MaterialDesign/svg")

        self.search_entry = TextBox(
            self,
            command=self.on_search_entry_changed,
            # grid=[0, 0],
            width=50
        )

        self.results_outer_box = ttk.Frame(self.tk)
        self.scroll_canvas = tk.Canvas(self.results_outer_box, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(
            self.results_outer_box, orient="vertical", command=self.scroll_canvas.yview)

        self.results_box = ttk.Frame(self.scroll_canvas)
        self.results_box.bind(
            "<Configure>",
            lambda e: self.scroll_canvas.configure(
                scrollregion=self.scroll_canvas.bbox("all")
            )
        )
        self.scroll_canvas.create_window(
            (0, 0), window=self.results_box, anchor="nw")
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        # self.results_box = Box(
        #     self,
        #     width="fill",
        #     height="fill",
        #     layout="grid",
        #     # grid=[0, 1],
        # )
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.add_tk_widget(
            self.results_outer_box,
            width="fill",
            height="fill",
        ) # self.results_outer_box.pack(side="left", fill="both", expand=True)
        self.progress_box = Box(self, width="fill")  # , grid=[0, 2]
        self.pb = Progressbar(
            self.progress_box.tk,  #self.tk
            # orient=tk.HORIZONTAL,
            # length=100,
            # mode='determinate',
        )
        self.progress_box.add_tk_widget(
            self.pb,
            width='fill',
        )

        # Status bar
        self.status_var = ""
        self.status_entry = TextBox(
            self,
            text=self.status_var,
            enabled=False,  # TODO: make readonly instead if possible
            # grid=[0, 3],
            width=50,
        )

        # Start the directory scanning
        self.after(100, self._load_icon_names)
        self.display()
        self.process_q_run_count = 0
        self.after(200, self._process_q)

    def _load_icon_names(self):
        if os.path.isdir(self._svg_dir):
            self._names = os.listdir(self._svg_dir)
        else:
            self.set_status("{} does not exist".format(repr(self._svg_dir)))

    def set_status(self, message):
        self.status_var = message
        self.status_entry.value = message

    def search_if(self):
        if self.status_entry.value != self._results_of:
            # FIX: self.stop_load_images_sync()  # stuck at 0 (race condition?)
            # Try again. Must have typed during search.
            # self._cancel_loading = True
            # time.sleep(.1)  # wait for load_images thread just a little.
            # ^ also messes things up (images don't load)
            #   since search_if is called directly after
            #   search starts the image loading thread.
            self.on_search_entry_changed()

    def on_search_entry_changed(self):
        if self.search_thread is not None:
            print("search thread is busy: {:.0%}  ".format(self.ratio))
            return
        if len(self.search_entry.value) >= 3:
            # self.on_search_entered()
            # Start immediately
            #   to make sure self.search_thread is set
            #   to prevent duplicate calls to search_thread
            self.after(0, self.on_search_entered)
        else:
            self.clear()

    def enable_search(self, enable):
        print("enable_search({}) after 0...".format(enable))
        self.after(0, self._enable_search, args=(enable,))

    def _enable_search(self, enable):
        return  # since race conditions thrash this badly
        print("_enable_search({})".format(enable))
        if enable:
            self.search_entry.enable()
            # self.search_entry.configure(state=tk.NORMAL)
        else:
            self.search_entry.disable()
            # self.search_entry.configure(state=tk.DISABLED)


    def on_search_entered(self):
        query = self.search_entry.value.lower()
        if self._results_of == query:
            # Occurs if box is disabled but user tried typing in it.
            logger.info(
                "Already showing results for {}".format(repr(query)))
            return
        self._results_of = query
        print("on_search_entered query={}".format(repr(query)))
        if self._names is None:
            self.set_status("Nothing in {}".format(repr(self._svg_dir)))
            return
        # for key, name in self.threads.items():
        #     if name == "load_images":
        #         raise RuntimeError("load_images_thread is already running!")
        if self.search_thread:
            # should be disabled
            raise RuntimeError("Already running self.search_thread")
        # if len(self.threads):  # commented since search does stop_load_images_sync
        #     raise RuntimeError("already running {}!".format(list(self.threads.values())))
        self.search_thread = threading.Thread(
            target=self._search,
            args=(query,),
            daemon=True,  # True: terminate when program stops
        )
        self.clear_q()  # prevent lagged enable/disable of box etc.
        self.enable_search(False)
        self.clear()
        self.set_progress(0)
        print("Starting search_thread {}".format(len(self.threads)))
        self.threads[id(self.search_thread)] = "search"
        self.search_thread.start()
        print("OK (search_thread started)")

    def clear_q(self):
        self.optional_q.clear()

    def _process_q(self):
        if self.process_q_run_count == 0:
            print("[_process_q] first run...")
        try:
            while True:
                try:
                    k, item = self.optional_q.popitem(last=False)
                except KeyError:
                    break  # Nothing in queue
                print("[_process_q] {}".format(k))
                if item is not None:
                    fn, args, kwargs = item
                    fn(*args, **kwargs)
        except Exception as ex:
            print("[_process_q] {}: {}".format(type(ex).__name__, ex))
            raise
        finally:
            self.after(500, self._process_q)
            if self.process_q_run_count == 0:
                print("[_process_q] first run done.")
            self.process_q_run_count += 1

    def optional_after(self, key, fn, args=None, kwargs=None):
        """Add function fn to queue or replace previous one at key"""
        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = {}
        if key not in self.optional_q or key != "set_progress":
            # log if not a frequent message
            print(
                "optional_after {}{}, {})...".format(
                    key,
                    repr(args).replace(")", "").rstrip(","),
                    repr(kwargs).replace("{", "").replace("}", ""),
                )
            )
        self.optional_q[key] = (fn, args, kwargs)

    def _search(self, search_query):
        self.stop_load_images_sync()
        self.ratio = 0
        self._search_max_count = \
            self._query_quick_lengths.get(search_query)
        # ^ Optimize max_count to end loop early if count of query known.
        # ^ An index position, *not* len of results.
        if self._search_max_count is None:
            self._search_max_count = len(self._names)
            print("Checking all {} results for {}"
                  .format(self._search_max_count, repr(search_query)))
        else:
            print("Predicted {} results for {}"
                  .format(self._search_max_count, repr(search_query)))
        idx = 0
        last_found_idx = -1

        # while self._iterate_search():
        #     pass
        while idx < self._search_max_count:
            name = self._names[idx]
            if search_query in name.lower():
                self._add_result(name)
                last_found_idx = idx
            idx += 1
            self.ratio = idx / self._search_max_count
            self.optional_after("set_progress", self.set_progress, args=(self.ratio,))
        sys.stderr.write("\n")
        sys.stderr.flush()
        self.optional_after("enable_search", self.enable_search, args=(True,))
        if search_query not in self._query_quick_lengths:
            self._query_quick_lengths[search_query] = \
                last_found_idx + 1
            # ^ index, *not* result count
            if len(self.threads) > 1:
                raise RuntimeError(
                    "Inaccurate self._query_quick_lengths[_search_query]"
                    " due to multiple threads: {}"
                    .format(list(self.threads.values())))
            else:
                print("Set predicted count for {} to {}"
                      .format(repr(search_query),
                              self._query_quick_lengths[search_query]))
        search_t_count = 0
        for key, name in self.threads.items():
            if name == "load_images":
                raise RuntimeError("load_images_thread is already running!")
            elif name == "search":
                search_t_count += 1
        if search_t_count > 1:
            raise RuntimeError("Error: {} search thread(s)".format(search_t_count))
        self._cancel_loading = False
        self.loading_ratio = 0
        load_images_thread = threading.Thread(
            target = self._load_images,
            daemon=True,  # True: terminate when program stops
        )
        self.load_images_thread = load_images_thread
        print("Starting load_images_thread {}".format(len(self.threads)))
        self.threads[id(load_images_thread)] = "load_images"
        load_images_thread.start()
        print("OK (load_images_thread started)")
        del self.threads[id(self.search_thread)]
        print("Done search_thread")
        self.ratio = 0
        self.search_thread = None
        self.after(0, self.search_if)
        return

    def import_image(self, result):
        name = result.name
        print("importing {}...".format(repr(name)))
        new_name = os.path.splitext(name)[0] + ".png"
        new_dir = os.path.join(ASSETS_DIR, "icons", "md")
        new_path = os.path.join(new_dir, new_name)
        result.path = new_path
        rel_path = new_path
        if new_path.startswith(APP_ROOT):
            rel_path = rel_path[len(APP_ROOT)+1:]  # +1 removes leading "/"
        if os.path.isfile(result.path):
            self.set_status("Already saved {}".format(repr(rel_path)))
            return
        try:
            result.image.save(new_path)
            self.set_status("Saved {}".format(repr(rel_path)))
        except Exception as ex:
            error = "{}: {}".format(type(ex).__name__, ex)
            self.set_status(error)

    def _load_images(self):
        if not self._results:
            print("Nothing to do, ending load_images_thread")
            del self.threads[id(self.load_images_thread)]
            self.load_images_thread = None
        for i, result in enumerate(self._results):
            self.loading_idx = i
            if self._cancel_loading:
                sys.stderr.write("cancelled _load_images...")
                sys.stderr.flush()
                break
            if result.picture:
                continue
            name = result.name
            self.loading_ratio = i / len(self._results)
            image = self._images.get(name)
            # if result.image:
            #     image = result.image
            if image is not None:
                result.image = image
            else:
                del image
                file_path = os.path.join(self._svg_dir, name)
                if os.path.splitext(name)[1].lower() == ".svg":
                    png_data = cairosvg.svg2png(url=file_path)
                    result.image = Image.open(io.BytesIO(png_data)).convert("RGBA")
                else:
                    result.image = Image.open(file_path).convert("RGBA")
                self._images[name] = result.image
            # result.picture = Picture(
            #     self.results_box,
            #     image=result.image,
            #     grid=[0, result.row]
            # )
            result.photo = ImageTk.PhotoImage(result.image)
            # ^ keep reference, otherwise disposed
            result.picture = ttk.Button(
                self.results_box,
                image=result.photo,
                command=lambda r=result: self.import_image(r),
                # borderwidth=0,
            )
            if self._cancel_loading:
                sys.stderr.write("cancelled _load_images before add...")
                sys.stderr.flush()
                break
            result.picture.grid(column=0, row=result.row)
            result.widgets.append(result.picture)
        self.loading_ratio = 1
        this_id = id(self.load_images_thread)
        if this_id in self.threads:
            del self.threads[this_id]
        else:
            logger.warning(
                "id({})=load_images not in self.threads"
                .format(repr(self.load_images_thread)))
        self.load_images_thread = None
        print("Done load_images_thread")
        print()

    def stop_load_images_sync(self):
        self._cancel_loading = True
        sys.stderr.write("stop_load_images_sync...")
        sys.stderr.flush()
        max_sec = 3
        start_sec = time.perf_counter()
        warned = False
        while self.load_images_thread is not None:
            if not self.load_images_thread.is_alive():
                print("Warning: stopping tracking for dead load_images_thread",
                      file=sys.stderr)
                del self.threads[id(self.load_images_thread)]
                self.load_images_thread = None
                return
            if not self._cancel_loading:
                raise RuntimeError(
                    "self._cancel_loading was reset by another thread")
            time.sleep(.01)
            passed = time.perf_counter() - start_sec
            if passed > max_sec:
                if not warned:
                    start_sec = time.perf_counter()  # warned = True
                    error =(
                        "Error: still won't stop after waiting"
                        " {:.1}s (progress {:.3%} at results[{}])..."
                        .format(passed, self.loading_ratio,
                                self.loading_idx))
                    sys.stderr.write(error)
                    sys.stderr.flush()
                    self.after(0, self.set_status, args=(error,))
        print("OK (stop_load_images_sync)", file=sys.stderr)

    def set_progress(self, ratio):
        self.pb['value'] = min(int(round(100 * ratio)), 100)
        sys.stderr.write("\r{:.0%}  ".format(ratio))
        sys.stderr.flush()

    def _add_result(self, name):
        result = SearchResult(name, len(self._results))
        # Label widget
        # label_widget = Text(
        #     self.results_box,
        #     text=name,
        #     grid=[1, result.row]
        # )
        label_widget = ttk.Label(
            self.results_box,
            text=name,
            # grid=[1, result.row]
        )
        label_widget.grid(column=1, row=result.row)
        result.widgets.append(label_widget)
        self._results.append(result)
        print(result.name)

    def clear(self):
        self._cancel_loading = True
        time.sleep(.1)  # wait for load_images thread just a little.
        # FIXME: self.stop_load_images_sync()  # won't start (race condition?)
        print("clear")
        for result in self._results:
            # Doing it forward prevents race condition where misses one
            #   added by load_images thread.
            for widget in result.widgets:
                widget.destroy()  # widget.hide()
        self._results.clear()
        self.results_of = None

if __name__ == "__main__":
    IconSearchApp()
