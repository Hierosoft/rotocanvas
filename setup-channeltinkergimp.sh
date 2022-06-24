#!/bin/bash
if [ ! -f rotocanvas/__init__.py ]; then
    mkdir -p ~/git
    git clone https://github.com/poikilos/rotocanvas ~/git/rotocanvas
    cd ~/git/rotocanvas
fi
if [ -f ~/.config/GIMP/2.10/plug-ins/channel_tinker.py ]; then
    rm ~/.config/GIMP/2.10/plug-ins/channel_tinker.py
fi
if [ -f ~/.config/GIMP/2.10/plug-ins/channeltinkergimp.py ]; then
    rm ~/.config/GIMP/2.10/plug-ins/channeltinkergimp.py
fi
if [ -d ~/.config/GIMP/2.10/plug-ins/channel_tinker ]; then
    rm ~/.config/GIMP/2.10/plug-ins/channel_tinker  # try symlink FIRST
    if [ $? -ne 0 ]; then
        # If there was an error, assume it is a directory:
        rm -Rf ~/.config/GIMP/2.10/plug-ins/channel_tinker
    fi
fi
if [ -d ~/.config/GIMP/2.10/plug-ins/channeltinker ]; then
    rm ~/.config/GIMP/2.10/plug-ins/channeltinker  # try symlink FIRST
    if [ $? -ne 0 ]; then
        # If there was an error, assume it is a directory:
        rm -Rf ~/.config/GIMP/2.10/plug-ins/channeltinker
    fi
fi
cp -R channeltinker ~/.config/GIMP/2.10/plug-ins/
cp channeltinkergimp.py ~/.config/GIMP/2.10/plug-ins/
# or
# ln -s ~/git/rotocanvas/channeltinkergimp.py ~/.config/GIMP/2.10/plug-ins/
# ln -s ~/git/rotocanvas/channeltinker ~/.config/GIMP/2.10/plug-ins/
# ls -l ~/.config/GIMP/2.10/plug-ins/channeltinker
