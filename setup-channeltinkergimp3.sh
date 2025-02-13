#!/bin/bash
VERY_OLD_MODULE_NAME=channeltinkergimp2
MODULE_NAME=channeltinkergimp
# DEST_NAME="__init__.py"
DEST_PLUGIN_DIR=~/.config/GIMP/3.0/plug-ins/$MODULE_NAME
DEST_NAME="$MODULE_NAME.py"
DEST_PATH=$DEST_PLUGIN_DIR/$DEST_NAME
UNINSTALL=0

if [ "x$1" = "x--uninstall" ]; then
    UNINSTALL=1
fi

if [ ! -f rotocanvas/__init__.py ]; then
    if [ -d ~/git/rotocanvas ]; then
        cd ~/git/rotocanvas
    fi
fi
if [ ! -f rotocanvas/__init__.py ]; then
    mkdir -p ~/git
    echo "[$0] Cloning into ~/git/rotocanvas..."
    git clone https://github.com/Hierosoft/rotocanvas.git ~/git/rotocanvas
    cd ~/git/rotocanvas || exit $?
fi
if [ -f $DEST_PLUGIN_DIR/channel_tinker.py ]; then
    rm $DEST_PLUGIN_DIR/channel_tinker.py || exit $?
fi
if [ -f $DEST_PATH ]; then
    rm $DEST_PATH || exit $?
fi
if [ -f $DEST_PLUGIN_DIR/$VERY_OLD_MODULE_NAME.py ]; then
    rm $DEST_PLUGIN_DIR/$VERY_OLD_MODULE_NAME.py || exit $?
fi
if [ -d $DEST_PLUGIN_DIR/channel_tinker ]; then
    if [ -L $DEST_PLUGIN_DIR/channel_tinker ]; then
        # symlink
        rm $DEST_PLUGIN_DIR/channel_tinker
    else
        rm -Rf $DEST_PLUGIN_DIR/channel_tinker
    fi
fi
if [ -d $DEST_PLUGIN_DIR/channeltinker ]; then
    if [ -L $DEST_PLUGIN_DIR/channeltinker ]; then
        # symlink
        rm $DEST_PLUGIN_DIR/channeltinker
    else
        rm -Rf $DEST_PLUGIN_DIR/channeltinker
    fi
fi
if [ $UNINSTALL -eq 1 ]; then
    echo "[$0] Uninstalled."
    exit $?
fi
mkdir -p $DEST_PLUGIN_DIR || exit $?
# ^ 3.0 requires each plug-in to have its own *folder*
cp -R channeltinker $DEST_PLUGIN_DIR/ || exit $?
if [ -d $DEST_PLUGIN_DIR/channeltinker/channeltinker ]; then
    echo "[$0] Error: Installed $DEST_PLUGIN_DIR/channeltinker/channeltinker"
    exit 1
elif [ -d $DEST_PLUGIN_DIR/channeltinker ]; then
    echo "[$0] Installed $DEST_PLUGIN_DIR/channeltinker/"
fi
# cp $MODULE_NAME.py $DEST_PLUGIN_DIR/ || exit $?
# chmod +x $DEST_PATH
# echo "[$0] Installed $DEST_PATH"

cp "$MODULE_NAME.py" "$DEST_PATH" || exit $?
chmod +x $DEST_PATH || exit $?
echo "[$0] Installed $DEST_PATH"

# or
# ln -s ~/git/rotocanvas/$MODULE_NAME.py $DEST_PLUGIN_DIR/
# ln -s ~/git/rotocanvas/channeltinker $DEST_PLUGIN_DIR/
# ls -l $DEST_PLUGIN_DIR/channeltinker
