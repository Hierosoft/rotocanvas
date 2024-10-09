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

Scope of use: code described in subsections--typically modified by hand to improve logic, variable naming, integration, etc, but in this commit, unmodified.

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