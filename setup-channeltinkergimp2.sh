#!/bin/bash
VERY_OLD_MODULE_NAME=channeltinkergimp
MODULE_NAME=channeltinkergimp2

if [ ! -f rotocanvas/__init__.py ]; then
    if [ -d ~/git/rotocanvas ]; then
        cd ~/git/rotocanvas
    fi
fi
if [ ! -f rotocanvas/__init__.py ]; then
    mkdir -p ~/git
    echo "Cloning into ~/git/rotocanvas..."
    git clone https://github.com/Hierosoft/rotocanvas.git ~/git/rotocanvas
    cd ~/git/rotocanvas || exit $?
fi
if [ -f ~/.config/GIMP/2.10/plug-ins/channel_tinker.py ]; then
    rm ~/.config/GIMP/2.10/plug-ins/channel_tinker.py || exit $?
fi
if [ -f ~/.config/GIMP/2.10/plug-ins/$MODULE_NAME.py ]; then
    rm ~/.config/GIMP/2.10/plug-ins/$MODULE_NAME.py || exit $?
fi
if [ -f ~/.config/GIMP/2.10/plug-ins/$VERY_OLD_MODULE_NAME.py ]; then
    rm ~/.config/GIMP/2.10/plug-ins/$VERY_OLD_MODULE_NAME.py || exit $?
fi
if [ -d ~/.config/GIMP/2.10/plug-ins/channel_tinker ]; then
    if [ -L ~/.config/GIMP/2.10/plug-ins/channel_tinker ]; then
        # symlink
        rm ~/.config/GIMP/2.10/plug-ins/channel_tinker
    else
        rm -Rf ~/.config/GIMP/2.10/plug-ins/channel_tinker
    fi
fi
if [ -d ~/.config/GIMP/2.10/plug-ins/channeltinker ]; then
    if [ -L ~/.config/GIMP/2.10/plug-ins/channeltinker ]; then
        # symlink
        rm ~/.config/GIMP/2.10/plug-ins/channeltinker
    else
        rm -Rf ~/.config/GIMP/2.10/plug-ins/channeltinker
    fi
fi
cp -R channeltinker ~/.config/GIMP/2.10/plug-ins/
cp $MODULE_NAME.py ~/.config/GIMP/2.10/plug-ins/
echo "Installed ~/.config/GIMP/2.10/plug-ins/$MODULE_NAME.py"
# or
# ln -s ~/git/rotocanvas/$MODULE_NAME.py ~/.config/GIMP/2.10/plug-ins/
# ln -s ~/git/rotocanvas/channeltinker ~/.config/GIMP/2.10/plug-ins/
# ls -l ~/.config/GIMP/2.10/plug-ins/channeltinker
