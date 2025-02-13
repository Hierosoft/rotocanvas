# Training Disclosure for rotocanvas
This Training Disclosure, which may be more specifically titled above here (and in this document possibly referred to as "this disclosure"), is based on **Training Disclosure version 1.1.4** at https://github.com/Hierosoft/training-disclosure by Jake Gustafson. Jake Gustafson is probably *not* an author of the project unless listed as a project author, nor necessarily the disclosure editor(s) of this copy of the disclosure unless this copy is the original which among other places I, Jake Gustafson, state IANAL. The original disclosure is released under the [CC0](https://creativecommons.org/public-domain/cc0/) license, but regarding any text that differs from the original:

This disclosure also functions as a claim of copyright to the scope described in the paragraph below since potentially in some jurisdictions output not of direct human origin, by certain means of generation at least, may not be copyrightable (again, IANAL):

Various author(s) may make claims of authorship to content in the project not mentioned in this disclosure, which this disclosure by way of omission unless stated elsewhere implies is of direct human origin unless stated elsewhere. Such statements elsewhere are present and complete if applicable to the best of the disclosure editor(s) ability. Additionally, the project author(s) hereby claim copyright and claim direct human origin to any and all content in the subsections of this disclosure itself, where scope is defined to the best of the ability of the disclosure editor(s), including the subsection names themselves, unless where stated, and unless implied such as by context, being copyrighted or trademarked elsewhere, or other means of statement or implication according to law in applicable jurisdiction(s).

Disclosure editor(s): Hierosoft LLC

Project author: Hierosoft LLC

This disclosure is a voluntary of how and where content in or used by this project was produced by LLM(s) or any tools that are "trained" in any way.

The main section of this disclosure lists such tools. For each, the version, install location, and a scope of their training sources in a way that is specific as possible.

Subsections of this disclosure contain prompts used to generate content, in a way that is complete to the best ability of the disclosure editor(s).

tool(s) used:
- GPT-4-Turbo (Version 4o, chatgpt.com)

Scope of use: code described in subsections--typically modified by hand to improve logic, variable naming, integration, etc.

## rotocanvas
### vob_to_dvd
Use linux to combine all of the VOBs from a DVD at /media/owner/MYMOVIE into one VOB, decrypted

make a bash script to do all that and save the resulting vob in ~/tmp

ok, I see a problem. Some unrelated apt update error that doesn't affect us could halt our script, so fix the vob script by splitting sudo apt update && sudo apt install -y vobcopy into separate lines.

Ok, I don't want the menu screen animations and other junk. Just get the longest title, such as in this output of lsdvd: Title: 01, Length: 02:27:38.467 Chapters: 19, Cells: 54, Audio streams: 01, Subpictures: 03
Title: 02, Length: 00:04:36.367 Chapters: 02, Cells: 03, Audio streams: 01, Subpictures: 03
Title: 03, Length: 00:04:40.567 Chapters: 02, Cells: 02, Audio streams: 01, Subpictures: 03
Title: 04, Length: 00:02:48.066 Chapters: 02, Cells: 02, Audio streams: 01, Subpictures: 03
Title: 05, Length: 00:03:14.133 Chapters: 02, Cells: 03, Audio streams: 01, Subpictures: 03
Title: 06, Length: 00:00:37.066 Chapters: 02, Cells: 02, Audio streams: 01, Subpictures: 03
Title: 07, Length: 00:03:00.166 Chapters: 02, Cells: 02, Audio streams: 01, Subpictures: 03
Title: 08, Length: 00:03:04.200 Chapters: 02, Cells: 02, Audio streams: 01, Subpictures: 03
Title: 09, Length: 00:02:39.066 Chapters: 02, Cells: 02, Audio streams: 01, Subpictures: 03
Title: 10, Length: 00:01:05.900 Chapters: 02, Cells: 02, Audio streams: 01, Subpictures: 03
Title: 11, Length: 00:01:39.567 Chapters: 02, Cells: 02, Audio streams: 01, Subpictures: 03
Title: 12, Length: 00:01:48.066 Chapters: 02, Cells: 02, Audio streams: 01, Subpictures: 03
Title: 13, Length: 00:04:48.867 Chapters: 02, Cells: 02, Audio streams: 01, Subpictures: 03
Title: 14, Length: 00:01:25.500 Chapters: 02, Cells: 02, Audio streams: 01, Subpictures: 03
Title: 15, Length: 00:03:22.166 Chapters: 02, Cells: 02, Audio streams: 01, Subpictures: 03
Title: 16, Length: 00:03:39.834 Chapters: 02, Cells: 03, Audio streams: 01, Subpictures: 03
Title: 17, Length: 00:02:45.667 Chapters: 02, Cells: 02, Audio streams: 01, Subpictures: 03
Title: 18, Length: 00:03:47.667 Chapters: 02, Cells: 02, Audio streams: 01, Subpictures: 03
Title: 19, Length: 00:05:03.934 Chapters: 02, Cells: 02, Audio streams: 01, Subpictures: 03
Title: 20, Length: 00:02:55.500 Chapters: 02, Cells: 02, Audio streams: 01, Subpictures: 00
Title: 21, Length: 00:56:19.266 Chapters: 15, Cells: 15, Audio streams: 01, Subpictures: 03
Title: 22, Length: 00:00:24.000 Chapters: 02, Cells: 02, Audio streams: 01, Subpictures: 00
Title: 23, Length: 00:00:14.000 Chapters: 02, Cells: 02, Audio streams: 01, Subpictures: 00
Title: 24, Length: 00:00:10.233 Chapters: 02, Cells: 02, Audio streams: 01, Subpictures: 00

this is getting out of hand. Convert it to Python and use libraries as necessary to avoid console commands if possible.

For backward compatibility add a python shebang, from __future__ import print_function, and use percent substitution not string interpolation.
ChatGPT said:
ChatGPT

ok now if there is no argument specified, just look through /media/%s where %s is the current username, and see which subfolder contains VIDEO_TS. If multiple contain it, show an error saying more than one dvd is inserted, list all of the resulting paths, and return 1 from main.

For compatibility, avoid pathlib, and just use os.makedirs if output_dir doesn't exist

Replace parts = line.split(',') with segments = line.split("Chapters:", 1) and parts = segments[0].split(',')

if sys.version_info.major >= 3, from subprocess import run as subprocess_run, else define a custom subprocess_run function that has the same args and returns but is python 2 compatible. Then use that in the program instead of subprocess.run

check isn't accepted by Popen in Python 2. Do check=kwargs.get("check") then if "check" in kwargs del kwargs["check"], then do whatever check would do manually instead of passing it to Popen

## channeltinkergimp
- 2025-02-12

gimpfu does not exist in GIMP 2.10.36. Please fix this gimp plug-in:

- paste GIMP 2.0 version.

ImportError: No module named gimp

What is the new equivalent of register(
    "python_fu_ct_remove_halo",
- paste rest of register call

ok now also implement

- paste python_fu_ct_centered_square register call

Finish reimplementing ct_remove_layer_halo based on the old global function (Make it into a method that is compatible with the new GIMP's required class-based approach, class ChannelTinker(Gimp.PlugIn) in our case):

- paste old global ct_remove_layer_halo function

Finish reimplementing this old global function (Make it into a method that is compatible with the new GIMP's required class-based approach, class ChannelTinker(Gimp.PlugIn) in our case):
def ct_draw_centered_circle(image, drawable, radius, color, filled):

- paste old global ct_draw_centered_circle function

- 2025-02-12

- start new conversation

How can I make these custom utility classes from an older version using gimpfu compatible with the new gimp which uses from gi.repository import Gimp, GObject, GLib?

- paste old GimpCTPI and GimpCTI

## channeltinkerpil
### imageprocessorframe
- 2025-02-12

Python 3 included in GIMP has no "site" module. How can I do something like: site.getsitepackages()

## channeltinker
- 2025-02-13
- This only affects fdist and a few lines of testing (3D etc)
write some tests for a distance formula called idist that accepts 2 points. Each point is a Python list.

## output-reader.py
Draw this as ascii art:

- paste output from program (commented print line)

Actually use 0 and 1

Write a tkinter canvas program with File Open menu that opens json files and when one is opened, assume it is a dict. First fill the canvas with gray. Iterate the pairs. The key is a string, and should be split by "," to get coordinates, converted to an int pair. If the value is True, draw black at the coordinates, otherwise draw white. Here is an example input file: {

- paste new (partial JSON) output

Now assume that instead of true and false, there will be a float value from 0 to 1. Create a gray pixel of the value.

Instead of a bunch of rectangles, use a PIL image and set pixel. Add a Save As menu item that opens a file chooser, replaces .json with .png to save default output file path, then confirms to overwrite if file exists.

Here is partial updated save code:
```
    if not img:
        messagebox.showinfo(
            "Save File", "There is no image."
        )
        return
    initialfile = None
    if file_path:
        initialfile = os.path.splitext(file_path)[0] = ".png"
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png")],
        initialfile=initialfile,
    )
```
. Now make the whole program object-oriented.