# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).


## [git] - 2024-03-17
### Fixed
- Add missing `__init__.py` to tests (imports now work in nose-py3 and pytest now).


## [git] - 2023-04-08
### Added
- Add a Kivy-based GUI.
  - Merge KivySpriteTouch with this project as the main GUI (main.py).


## [git] - 2021-12-04
### Added
- Merge the gimp-plugin-channel-tinker project into rotocanvas.
  - Rename `channel_tinker_gimp.py` to `channeltinkergimp.py`
  - Rename `channel_tinker_pil.py` to `channeltinkerpil/__init__.py`
    - Edit diffimages.py and diffimagesratio.py scripts to reflect the
      change.
  - Merge the readme.
  - Add the gimp-plugin-channel-tinker changelog as the new rotocanvas
    changelog.
  - Change tests.py to channeltinkerpil/tests/test_channeltinkerpil.py
    and move test data to that directory.

### Changed
- Rename the project from pyrotocanvas to rotocanvas.


## [git] - 2020-02-20
(gimp-plugin-channel-tinker)
### Added
- diffimage.py compares two images (calls tinkerduck.py)
- ChannelTinkerProgressInterface and ChannelTinkerInterface are
  available and allow the module to contain more of the functions that
  would otherwise be dependent upon the backend (GIMP or PIL).

### Changed
- Rename plug-in to channel_tinker a.k.a. "Channel Tinker" (and module
  to channel_tinker)
- Make the channel_tinker module entirely duck-typed.
    - Move gimp-specific usages to plugin script.


## [git] - 2020-02-19
(gimp-plugin-channel-tinker)
### Added
- Draw Centered Square.
