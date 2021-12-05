#!/usr/bin/env python
"""
Command DeepFace Lab automatically.
"""
import os
import shutil
import platform
import subprocess
from datetime import datetime
import json
from threading import Thread
"""
from subprocess import PIPE, Popen
# import fcntl # not available on Windows
from threading  import Thread
try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty  # python 2.x
ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(out, state, isStdErr):
    for line in iter(out.readline, b''):
        state._q.put(line)
    out.close()

# ^
# as per jfs's Feb 4 '11 at 9:14 answer
# on <https://stackoverflow.com/questions/375427/a-non-blocking-read-on-
# a-subprocess-pipe-in-python>
# edited Aug 6 '18 at 15:02 by ankostis

"""

try:
    from pyrotocanvas.rcproject import RCProject
    enableDLM = True
except ModuleNotFoundError:
    mod_paths = ["C:\\Users\\Owner\\GitHub\\pyrotocanvas\\pyrotocanvas"]
    for modules in mod_paths:
        if os.path.isdir(modules):
            sys.path.append(modules)
            break
    if modules is None:
        print("You do not have pyrotocanvas in the path nor in any of"
              " the following known locations: {}".format(mod_paths))
    else:
        print("[choose_dfl_dst] * using {} for modules."
              "".format(modules))
        from dfl import DLMItem
        from dfl import DLM
        enableDLM = True


dfl_install_help_fmt = """
You must install DeepFace Lab such that {} exists.
Visit https://github.com/iperov/DeepFaceLab and scroll down to
"Releases". The magnet link requires a program such as Deluge (free)
from https://dev.deluge-torrent.org/wiki/Download.
"""

dlm_help_fmt = """
After choosing a source and destination, you must run each batch
file in {} in the numbered order.
"""

digits = "0123456789"

def __nonBlockReadline(output):
    # fcntl is NOT AVAILABLE ON WINDOWS
    # so use enqueue_output instead
    try:
        import fcntl
    except ImportError:
        raise EnvironmentError("fcntl is not available")
    # as per John Doe's Dec 13 '11 at 20:46 answer
    # edited Dec 13 '11 at 21:15
    # on <https://stackoverflow.com/questions/8495794/python-popen-
    # stdout-readline-hangs>
    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    try:
        return output.readline()
    except:
        return ''

# DLMItem_members = ['path', 'orig', 'face', 'role', 'form', 'mask',
#                    'hide', 'temp', 'drop']




class DLMItem:
    SAVES = ['path', 'orig', 'face', 'role', 'form', 'mask', 'hide',
             'temp', 'drop']
    MEMBER_HELP = {
        'path': "The current location (dir or file) (unique)",
        'orig': "The original location (dir or file)",
        'face': "name of person or character--no spaces",
        'role': "DLM.ROLE_SRC or DLM.ROLE_DST",
        'form': "see DLM.FORMS_HELP",
        'mask': "path to result_mask.mp4 if form is result",
        'hide': "hide this item (only for workspaces in storage)",
        'drop': "the workspace path in storage when not in the lab",
        'proj': "where to put final video+mask if not in 'drop'",
        # 'temp': deprecated--see isTemp(self),
    }

    def isTemp(self):
        if self.form == DLM.FORM_ORIGINAL:
            return True
        elif self.form == DLM.FORM_MERGED:
            if os.path.isdir(self.path):
                return True
        return False

    def __init__(self, dlm, path, **kwargs):
        """
        Generating an item using the workspace is the normal way since
        the workspace knows the context and can set the members
        properly. Avoid calling this directly.

        Sequential arguments:
        path -- The workspace directory which will contain a source and
                destination (usually one or the other if the workspace
                is in storage and not in the lab).
        Keyword arguments:
        drop -- This is a directory in storage equivalent to the
                where ejected files can be dropped. It should always
                be a directory equivalent to the video filename but
                without an extension.
        """
        if dlm is None:
            raise ValueError("You must specify a pyrotocanvas.dfl.DLM()"
                             " instance.")
        self.dlm = dlm
        for name in DLMItem.SAVES:
            setattr(self, name, None)
        self.hide = False
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        s = self.orig
        if s is None:
            s = self.path
            # print("[dfl.py DLMItem __str__]  - s is the path")
        if self.drop is not None:
            # print("[dfl.py DLMItem __str__]  - s is the drop")
            if platform.system() == "Windows":
                if s.lower().startswith(self.drop.lower()):
                    s = s[len(self.drop):]
            else:
                if s.startswith(self.drop):
                    s = s[len(self.drop):]
        # print("[dfl.py DLMItem __str__]  - s is \"{}\"".format(s))
        return "{}".format(s)
        # ^ must return a string--None causes exception on using __str__

    def getDict(self):
        item = {}
        for name in DLMItem.SAVES:
            item[name] = getattr(self, name)
        return item

    def isInLab(self):
        return self.dlm.isInLab(self.path)

    def setFromItem(self, item, wipe=False):
        """
        Sequential arguments:
        item -- must be the same class or have the members from SAVES.

        Keyword arguments:
        wipe -- If True, set all members to None whose names are in
                SAVES. If false, a member will only be set to None if
                the corresponding member in item is present
        """
        for name in DLMItem.SAVES:
            try:
                got = getattr(item, name)
                setattr(self, name, got)
            except AttributeError:
                if wipe:
                    setattr(self, name, None)

    def setFromDict(self, item, wipe=False):
        """
        Sequential arguments:
        item -- must be the same class or have the members from SAVES.

        Keyword arguments:
        wipe -- If True, set all members to None whose names are in
                SAVES. If false, a member will only be set to None if
                the corresponding member in item is present
        """
        for name in DLMItem.SAVES:
            try:
                got = item[name]
                setattr(self, name, got)
            except KeyError:
                if wipe:
                    setattr(self, name, None)

    def copy(self):
        item = DLMItem(self.dlm, self.path)
        for name in DLMItem.SAVES:
            setattr(item, name, getattr(self, name))
        return item



class DLMWorkspace:
    LOG_NAME = "pyrotocanvas-dlm.log"

    def __init__(self, dlm, path):
        if dlm is None:
            raise ValueError("You must specify a pyrotocanvas.dfl.DLM()"
                             " instance.")
        self.path = path  # must be set before load
        self.dlm = dlm  # must be set before load
        self.load()  # always sets items

    def pop(self, path):
        return self.peek(path, remove=True)

    def peek(self, path, remove=False):
        """
        Remove the item from the metadata.

        returns:
        The removed item, or None if the path doesn't exist in the
        workspace.
        """
        for i in range(len(self.items)):
            item = self.items[i]
            if item.path == path:
                if remove:
                    del self.items[i]
                    self.save()
                return item
        return None

    def setItemProps(self, path, role, **kwargs):
        """
        Set an item's property.

        returns:
        The index of the item in self.items
        """
        resultIndices = []
        for i in range(len(self.items)):
            item = self.items[i]
            if item.path == path:
                if item.role == role:
                    resultIndices.append(i)
        if len(resultIndices) > 1:
            return ValueError("There is more than one \"{}\" with role"
                              " \"{}\".".format(path, role))
        i = resultIndices[0]
        # for i in resultIndices:
        for k, v in kwargs.items():
            if not hasattr(self.items[i], k):
                raise AttributeError("Item has no member named {}."
                                     "".format(k))
            setattr(self.items[i], k, v)

        return None


    def push(self, item, fileOp):
        """
        Sequential arguments:
        fileOp -- 'move' or 'copy' the actual file (item.path)
        """
        ok = False
        error = None
        if item.role is None:
            return False, "The item must have a role before pushing it"
        form = item.form
        role = item.role
        if role not in DLM.getRoles():
            raise ValueError("role must be one of: {} not {}"
                             "".format(DLM.getRoles(), role))
        path1 = item.path
        container = None
        if os.path.isfile(path1):
            container = DLM.C_FILE
        elif os.path.isdir(path1):
            container = DLM.C_DIR
        else:
            return False, "\"{}\" doesn't exist.".format(item.path)
        if self.isInLab():
            got = self.getRoleItems(role)
            if len(got) > 0:
                return False, ("You can only have one {} in the lab."
                               "".format(role))
        newExt = os.path.splitext(item.path)[1]
        paths = []
        forms = DLM.getForms() if form is None else [form]
        for form in forms:
            formPaths, innerError = self.formPaths(item.role, form,
                                                   container)
            print("  * checking forms: {}".format(formPaths))
            if formPaths is None:
                print("    formPaths warning: {}".format(innerError))
                continue
            for formPath in formPaths:
                # print("    * checking for {}".format(formPath))
                # if DLM.existsAs(formPath, container):
                # ^ Do NOT check if it exists. It where the item will go
                if os.path.splitext(formPath)[1] == newExt:
                    paths.append(formPath)
                else:
                    print("WARNING: skipping due to different"
                          " extension: {}".format(formPath))
        if len(paths) > 1:
            raise RuntimeError("multiple targets: {}"
                               " (try setting item.form)".format(paths))
        elif len(paths) < 1:
            raise RuntimeError("There is no possible target when the"
                               " role is {} and the container is {}"
                               " ".format(item.role, container))
        path2 = paths[0]
        logPath = self.logPath
        logLine = (
            ": {} \"{}\" \"{}\"".format(fileOp, path1, path2)
        )
        if fileOp == 'move':
            shutil.move(path1, path2)
            print("* {} \"{}\" \"{}\"".format(fileOp, path1, path2))
            item.path = path2
            self.items.append(item)
            with open(logPath, 'a') as log:
                log.write(DLM.getDtString() + logLine + "\n")
            print("* logged {}: \"{}\"".format(fileOp, logPath))
        elif fileOp == 'copy':
            shutil.copy(path1, path2)
            item.path = path2
            self.items.append(item)
            with open(logPath, 'a') as log:
                log.write(DLM.getDtString() + logLine + "\n")
            print("* logged {}: \"{}\"".format(fileOp, logPath))
        else:
            msg = ("* WARNING: nothing done for \"{}\" \"{}\" since {}"
                   " isn't 'move'/'copy'".format(path1, path2, fileOp))
            error = msg
            print(msg)
        ok = self.save()
        return ok, error

    def findByPath(self, path):
        for i in range(len(self.items)):
            item = self.items[i]
            if path == item.path:
                return i
        return -1

    def populate(self, orig=None, role=None, form=None):
        """
        Keyword arguments:
        orig -- If the workspace is not the lab, specify a filename if
                The filename is not data_src.mp4 nor data_dst.mp4.
                If you set this you should also set role (or the
                workspace will generate an item for each role in
                DLM.getRoles().
        role -- Add only one role for the item. Normally, add this if
                you are adding a workspace that is in storage (not in
                the lab) that doesn't already have DLM metadata
                (in a file named according to DLM.WS_META_NAME).
        form -- Assume orig is in this form (specify one of the
                DLM.FORM_* constants). This only affects the orig file
                (it affects no file if orig is not specified).
        """
        itemForm = form
        roles = [role]
        if role is None:
            roles = DLM.getRoles()
        else:
            if role not in DLM.getRoles():
                raise ValueError("role must be one of: {} not {}"
                                 "".format(DLM.getRoles(), role))
        for role in roles:
            for form in DLM.getSteps():
                for container in DLM.getContainers():
                    thisForm = form
                    try:
                        if orig is not None:
                            if itemForm is not None:
                                thisForm = itemForm
                        item, error = self.generateItem(
                            role,
                            thisForm,
                            container,
                            orig=orig
                        )
                        if item is None:
                            # the role+form+container wouldn't ever
                            # exist.
                            continue
                        if not DLM.existsAs(item.path, container):
                            if orig is not None:
                                raise ValueError("{} doesn't exist"
                                                 "".format(item.path))
                            continue
                        if item is not None:
                            atI = self.findByPath(item.path)
                            if atI >= 0:
                                print("WARNING: overriding item\n {}"
                                      " with\n {}.".format(
                                          self.items[atI],
                                          item
                                      ))
                                self.items[atI].setFromDict(
                                    item.getDict()
                                )
                            else:
                                print("+Adding item: {}"
                                      "".format(item))
                                self.items.append(item)
                        else:
                            print("+Adding warning: {}".format(error))
                    except ValueError:
                        # Do nothing--if it doesn't exist, that's ok
                        # in this case.
                        pass
                    """
                    info = DLM.formInfo(role, thisForm, container)
                    if not info['everExists']:
                        continue
                    path = info['path']
                    if os.path.exists(path):
                        result = self._toItem(path)
                        if result is None:
                            raise RuntimeError("_toItem failed"
                                               " (got None)")
                        results.append(result)
                    """
        self.save()
        return True

    def getRoleItems(self, role):
        """
        Get a list of items matching the role. There is usually only
        one. Only one is allowed if the workspace is the lab workspace.

        Sequential arguments:
        role -- only search a certain role
        """
        if role not in DLM.getRoles():
            raise ValueError("role must be one of: {} not {}"
                             "".format(DLM.getRoles(), role))
        results = []
        for item in self.items:
            if item.role == role:
                results.append(item)
        return results


    def getItemAttribute(self, role, name):
        """
        This will only work if the workspace is the lab's workspace
        usually, otherwise there won't be metadata, but if the

        Sequential arguments:
        role -- only search a certain role
        """
        if role not in DLM.getRoles():
            raise ValueError("role must be one of: {} not {}"
                             "".format(DLM.getRoles(), role))
        for item in self.items:
            if item.role == role:
                try:
                    return getattr(item, name)
                except AttributeError:
                    return None
        return None

    def generateItem(self, role, form, container, orig=None):
        """
        Keyword arguments:
        orig -- If not None, forcibly make the item if it exists.
                Otherwise return (None, error)
                when a standardized container path
                not present. Only set this when the workspace is a user
                workspace in storage (not the lab's workspace).

        returns: tuple of (item or None, error or None)
        """
        other = {}
        other[DLM.C_DIR] = DLM.C_FILE
        other[DLM.C_FILE] = DLM.C_DIR
        if role not in DLM.getRoles():
            raise ValueError("role must be one of: {} not {}"
                             "".format(DLM.getRoles(), role))
        if form not in DLM.getForms():
            raise ValueError("form must be one of: {} not {}"
                             "".format(DLM.getForms(), form))
        if container not in DLM.getContainers():
            raise ValueError("container must be one of: {} not {}"
                             "".format(DLM.getContainers(), container))
        paths = None
        error = None

        if orig is not None:
            if container == DLM.C_DIR:
                if not os.path.isdir(orig):
                    raise ValueError("Setting {} as {} {} is impossible"
                                     " because it isn't a directory."
                                     "".format(orig, role, container))
            else:
                if not os.path.isfile(orig):
                    raise ValueError("Setting {} as {} {} is impossible"
                                     " because it isn't a file."
                                     "".format(orig, role, container))
            paths, error = self.formPaths(role, form, container)
            if paths is None:
                raise ValueError("The path \"{}\" is a {} but the"
                                 " only possible container for the"
                                 " {} role is {}"
                                 "".format(orig, container,
                                           role, other[container]))
            paths = [orig]
        else:
            paths, error = self.formPaths(role, form, container)
        if paths is None:
            # examples:
            # - If role is DLM.ROLE_SRC, there should be no
            #   case where form is merged (only DLM.ROLE_DST ever gets
            #   merged).
            # - If container is DLM.C_FILE, there should be no
            #   case where form is aligned (only images ever get
            #   aligned, and the path for an image sequence is a
            #   directory.
            raise ValueError(error)
            # return None, error
        for path in paths:
            # The only reason this is a loop is that there can be more
            # than one file extention for results.
            # - There will be only one path in paths as per above if the
            #   orig param was not None.
            items = self.getRoleItems(role)
            item = DLMItem(self.dlm, path, role=role, form=form)
            print("  * trying to add item {}...".format(item))
            if len(items) > 0:
                if len(items) > 1:
                    print("WARNING: Getting the item attributes is"
                          " impossible since there is more than one"
                          " item with the {} role in \"{}\"'s metadata"
                          "".format(role, self.path))
                else:
                    for k, v in items[0].getDict().items():
                        setattr(item, k, v)
                        if k not in DLMItem.SAVES:
                            # This case should never occur if
                            # getDict is called as the basis for the
                            # loop.
                            print("WARNING: {} is not one of {} so it"
                                  " will not be saved upon closing the"
                                  " workspace."
                                  "".format(k, DLMItem.SAVES))
                    print("    * item became {}".format(item))
            foundCont = DLM.C_DIR
            if orig is not None:
                # We are adding a new one in this case (from a workspace
                # not in the lab), so the path and origin are the same:
                item.orig = orig
                item.path = path
            if os.path.isfile(path):
                foundCont = DLM.C_FILE
                if container == DLM.C_FILE:
                    if item.path is None:
                        item.path = path
                    return item, None
            else:
                if container == DLM.C_DIR:
                    if item.path is None:
                        item.path = path
                    return item, None
        error = None
        if orig is not None:
            # If the user tried to add a file from storage via adding
            # a workspace, then not generating an item is a failure.
            error = ("The path's detected container is {} but"
                     " you specified {}.".format(foundCont, container))
        # else the workspace can just not report having this item.
        return None, error

    def formed(self, role, form, container):
        """
        returns:
        - True: container exists
        - False: doesn't exist
        - None: The container isn't expected to exist for the role and
                form.
        """
        if role not in DLM.getRoles():
            raise ValueError("role must be one of: {} not {}"
                             "".format(DLM.getRoles(), role))
        if form not in DLM.getForms():
            raise ValueError("form must be one of: {} not {}"
                             "".format(DLM.getForms(), form))
        if container not in DLM.getContainers():
            raise ValueError("container must be one of: {} not {}"
                             "".format(DLM.getContainers(), container))

        item = None
        error = None
        try:
            item, error = generateItem(self, role, form, container)
        except ValueError:
            # if the file isn't there, ignore the problem and
            # return None.
            pass
        return item is not None
        """
        paths, error = self.formPaths(role, form, container)
        for path in paths:
        if path is None:
            # examples:
            # - If role is DLM.ROLE_SRC, there should be no
            #   case where form is merged (only DLM.ROLE_DST ever gets
            #   merged).
            # - If container is DLM.C_FILE, there should be no
            #   case where form is aligned (only images ever get
            #   aligned, and the path for an image sequence is a
            #   directory.
            return None, error
        paths = [path]
        if hasattr(path, 'append'):
            paths = path
        for path in paths:
            if container == DLM.C_FILE:
                if os.path.isfile(path):
                    return True, None
            else:
                if os.path.isdir(path):
                    return True, None
        return False, None
        """

    def maskPath(self, container):
        ws = self.path
        base = os.path.join(ws, 'data_dst')
        if container == DLM.C_FILE:
            return os.path.join(ws, 'result_mask.mp4')
        return os.path.join(base, 'merged_mask')

    def formPaths(self, role, form, container):
        """
        Get a list of path(s) of file/directory for a form.

        returns:
        a tuple containing:
        - a list of paths (or None)
        - an error string (or None)
        """
        if role not in DLM.getRoles():
            raise ValueError("role must be one of: {} not {}"
                             "".format(DLM.getRoles(), role))
        if form not in DLM.getForms():
            raise ValueError("form must be one of: {} not {}"
                             "".format(DLM.getForms(), form))
        if container not in DLM.getContainers():
            raise ValueError("container must be one of: {} not {}"
                             "".format(DLM.getContainers(), container))
        ws = self.path
        roleSub = None

        if role == DLM.ROLE_DST:
            roleSub = os.path.join(ws, 'data_dst')
        elif role == DLM.ROLE_SRC:
            roleSub = os.path.join(ws, 'data_src')
        else:
            raise ValueError('role must be one of: {}'
                             ''.format(DLM.getRoles()))
        paths = None
        if form == DLM.FORM_MERGED:
            if role == DLM.ROLE_SRC:
                return None, "Only dest ever gets merged."
            if container == DLM.C_FILE:
                noExt = os.path.join(ws, 'result')
                paths = [noExt + '.mp4', noExt + '.avi', noExt + '.mov']
            else:
                paths = [os.path.join(roleSub, 'merged')]
        elif form == DLM.FORM_ALIGNED:
            if container == DLM.C_FILE:
                return None, "There is never an aligned video."
            paths = [os.path.join(roleSub, 'aligned')]
        elif form == DLM.FORM_ORIGINAL:
            # The original can only be mp4 with the roleSub as the name.
            paths = [roleSub + '.mp4']
        else:
            raise ValueError("form \"{}\" is not implemented"
                             "".format(form))

        return paths, None

    def isInLab(self):
        return self.dlm.isInLab(self.path)

    def load(self):
        self.items = []
        path  = os.path.join(self.path, DLM.WS_META_NAME)
        if not os.path.isfile(path):
            return False
        self.logPath = os.path.join(self.path, DLMWorkspace.LOG_NAME)
        meta = {}
        with open(path, 'r') as ins:
            meta = json.load(ins)
        if meta.get('items') is None:
            meta['items'] = []
            print("WARNING: There is no items member in \"{}\"."
                  "".format(path))
        else:
            print("* INFO: \"{}\" has {} item(s): {}."
                  "".format(path, len(meta['items']), meta['items']))
        itemDicts = meta['items']
        for itemDict in itemDicts:
            itemPath = itemDict.get('path')
            if itemPath is None:
                print("ERROR: an item in {} is missing a path."
                      "".format(path))
                continue
                # if not self.isInLab():
                #     print("ERROR: an item in {} is missing a path."
                #           "".format(path))
                #    continue
                """
                # Repair the metadata using known paths.
                itemRole = itemDict.get('role')
                if itemRole is None:
                    print("ERROR: an item in {} is missing a path"
                          " & role.".format(path))
                    continue
                itemForm = itemDict.get('form')
                itemForms = [itemForm]
                if itemForm is None:
                    itemForms = DLM.getForms()
                for form in itemForms:
                    for formContainer in DLM.getContainers():
                        formPaths = self.formPaths(
                            itemRole,
                            itemForm,
                            container
                        )
                        # do the rest here if you dare
                """

            if itemPath is None:
                print("ERROR: an item in {} is missing a path."
                      "".format(path))
                continue
            item = DLMItem(self.dlm, itemPath)
            item.setFromDict(itemDict)
            self.items.append(item)
        return True

    def save(self):
        path  = os.path.join(self.path, DLM.WS_META_NAME)
        meta = {}
        meta['items'] = []
        for item in self.items:
            meta['items'].append(item.getDict())
        with open(path, 'w') as outs:
            json.dump(meta, outs, indent=2)
        return True

class DLM:

    """
    This is a DLM manager.
    """
    ZONE_STORAGE = 'storage'
    ZONE_LAB = 'lab'
    # ^ DLM.getZones must list ZONE_*
    ROLE_SRC = 'src'
    ROLE_DST = 'dst'
    # ^ DLM.getRoles must list ROLE_*
    ROLES_HELP = {
        ROLE_SRC: "Choose the video with the face you want to add.",
        ROLE_DST: "Choose the video with the face you want to affect."
    }
    FORM_ORIGINAL = 'original'  # isdir implies "extract images" step
    FORM_ALIGNED = 'aligned'
    FORM_MERGED = 'merged' # isfile implies "merge to ..." step
    # ^ DLM.getForms must list FORM_*
    FORMS_HELP = {
        'original': "not modified by DLM",
        'aligned': "faceset extract is complete",
        'merged': "if directory, then images, if file, then result.mp4",
    }
    IN = 'container'  # for brevity
    C_DIR = 'dir'
    C_FILE = 'file'
    # ^ DLM.getContainers must list C_*

    FORMS_ORDER = [
        # The OP_ codes between the forms are the ones available for
        # the preceding form (At least one produces the next form)
        {'form':FORM_ORIGINAL, 'role':ROLE_SRC,
         'container':C_FILE},
        # OP_EXTRACT_IMAGES_SRC
        {'form':FORM_ORIGINAL, 'role':ROLE_DST,
         'container':C_FILE},
        # OP_EXTRACT_IMAGES_DST
        {'form':FORM_ORIGINAL, 'role':ROLE_SRC,
         'container':C_DIR},
        # OP_EXTRACT_FACESET_SRC, OP_EXTRACT_FACESET_SRC_M
        {'form':FORM_ORIGINAL, 'role':ROLE_DST,
         'container':C_DIR},
        # OP_DENOISE_DST, OP_EXTRACT_DST_FACESET,
        # OP_EXTRACT_DST_FACESET_M, OP_EXTRACT_DST_FACESET_MF
        # ^ Put OP_DENOISE_DST
        #   ("3.optional) denoise data_dst images.bat")
        #   here to avoid confusion (It isn't relevant until now).
        # ^ This form was already available, but progressing to the next
        # form now makes sense, and these ops are next in DLM.
        {'form':FORM_ALIGNED, 'role':ROLE_SRC,
         'container':C_DIR},
        # OP_SORT_SRC, OP_DELETE_BAD_SRC
        # ^  put 5 AFTER all extraction to avoid confusion
        #   since this stuff is optional but recommended and can be done
        #   any time before TRAIN.
        {'form':FORM_ALIGNED, 'role':ROLE_DST,
         'container':C_DIR},
        # After ROLE_SRC and ROLE_DST are both in aligned form, you
        # can train any time, but the sorting and deleting are
        # normally done. You can also merge at any time, but you train
        # first or the output will be incorrect or it will not do
        # anything if there is no model trained at all.
        # OP_SORT_DST, OP_DELETE_BAD_DST, OP_TRAIN_QUICK96,
        # OP_TRAIN_SAEHD, OP_MERGE_QUICK96, OP_MERGE_SAEHD
        {'form':FORM_MERGED, 'role':ROLE_DST,
         'container':C_DIR},
        # OP_FINALIZE_MP4, OP_FINALIZE_MP4_L, OP_FINALIZE_MOV_L,
        # OP_FINALIZE_AVI,
        {'form':FORM_MERGED, 'role':ROLE_DST,
         'container':C_FILE},
    ]
    OP_EXTRACT_IMAGES_SRC = 'Extract src images'
    OP_EXTRACT_IMAGES_DST = 'Extract dst images'
    OP_DENOISE_DST = 'Denoise dst (optional)'
    OP_EXTRACT_FACESET_SRC = 'Extract src faceset'
    OP_EXTRACT_FACESET_SRC_M = 'Extract src faceset (manual)'
    OP_EXTRACT_DST_FACESET = 'Extract dst faceset'
    OP_EXTRACT_DST_FACESET_M = 'Extract dst faceset (manual)'
    OP_EXTRACT_DST_FACESET_MF = 'Extract dst faceset (manual fix)'
    OP_SORT_SRC = 'Sort src faceset (helps manual deletion)'
    OP_DELETE_BAD_SRC = 'Manually delete unused src faces (optional)'
    OP_SORT_DST = 'Sort dst faceset (helps manual deletion)'
    OP_DELETE_BAD_DST = 'Manually delete unused dst faces (recommended)'
    OP_TRAIN_QUICK96 = 'Train (Quick96)'
    OP_TRAIN_SAEHD = 'Train (SAEHD)'
    OP_MERGE_QUICK96 = 'Merge (Quick96): requires train (Quick96)'
    OP_MERGE_SAEHD = 'Merge (SAEHD): requires train (SAEHD)'
    OP_FINALIZE_MP4 = 'Generate MP4'
    OP_FINALIZE_MP4_L = 'Generate MP4 (lossless)'
    OP_FINALIZE_MOV_L = 'Generate MOV (lossless)'
    OP_FINALIZE_AVI = 'Generate AVI'

    OPS_FOR = {
        'original': {
            'src': {
                'file': [
                    OP_EXTRACT_IMAGES_SRC,
                ],
                'dir': [
                    OP_EXTRACT_FACESET_SRC,
                    OP_EXTRACT_FACESET_SRC_M,
                ],
            },
            'dst': {
                'file': [
                    OP_EXTRACT_IMAGES_DST,
                ],
                'dir': [
                    OP_DENOISE_DST,
                    OP_EXTRACT_DST_FACESET,
                    OP_EXTRACT_DST_FACESET_M,
                    OP_EXTRACT_DST_FACESET_MF,
                ],
            },
        },
        'aligned': {
            'src': {
                'dir': [
                    OP_SORT_SRC,  # 4.2 sort first to make 4.1 easier:
                    OP_DELETE_BAD_SRC,
                ],
            },
            'dst': {
                'dir': [
                    # You can technically do any of these now, but
                    # you have to train to get a valid result.
                    OP_SORT_DST,
                    OP_DELETE_BAD_DST,
                    OP_TRAIN_QUICK96,
                    OP_TRAIN_SAEHD,
                    OP_MERGE_QUICK96,
                    OP_MERGE_SAEHD,
                ],
            },
        },
        'merged': {
            'dst': {
                'dir': [
                    OP_FINALIZE_MP4,
                    OP_FINALIZE_MP4_L,
                    OP_FINALIZE_MOV_L,
                    OP_FINALIZE_AVI,
                ],
                # The program doesn't have any batches to save the video
                # it generates. See one of the
                # DLM functions to do that.
            },
        },
    }
    # usage: OPS_FOR[form][role][t] # gets list of OP_ strings
    BATCHES_FOR = {}
    BATCHES_FOR[OP_EXTRACT_IMAGES_SRC] = [
        "2) extract images from video data_src.bat",
    ]
    BATCHES_FOR[OP_EXTRACT_IMAGES_DST] = [
        "3) extract images from video data_dst FULL FPS.bat",
    ]
    BATCHES_FOR[OP_DENOISE_DST] = [
        "3.optional) denoise data_dst images",
    ]
    BATCHES_FOR[OP_EXTRACT_FACESET_SRC] = [
        "4) data_src faceset extract.bat",
    ]
    BATCHES_FOR[OP_EXTRACT_FACESET_SRC_M] = [
        "4) data_src faceset extract MANUAL.bat",
    ]
    BATCHES_FOR[OP_EXTRACT_DST_FACESET] = [
        "5) data_dst faceset extract.bat",
    ]
    BATCHES_FOR[OP_EXTRACT_DST_FACESET_M] = [
        "5) data_dst faceset extract MANUAL.bat",
    ]
    BATCHES_FOR[OP_EXTRACT_DST_FACESET_MF] = [
        "5) data_dst faceset extract + manual fix.bat",
    ]
    # NotImplemented:
    # - "5) data_dst faceset MANUAL RE-EXTRACT DELETED
    #   ALIGNED_DEBUG.bat"
    # Put 4 after 5 to avoid confusion
    # (after all extract steps)
    BATCHES_FOR[OP_SORT_SRC] = [
        "4.2) data_src sort.bat",
    ]
    BATCHES_FOR[OP_DELETE_BAD_SRC] = [
        "4.1) data_src view aligned result.bat",
    ]
    # NotImplemented:
    # - "4.2) data_src util add landmarks debug images.bat"
    # - "4.2) data_src util faceset enhance.bat"
    # - "4.2) data_src util faceset metadata restore.bat"
    # - "4.2) data_src util faceset metadata save.bat"
    # - "4.2) data_src util faceset pack.bat"
    # - "4.2) data_src util faceset unpack.bat"
    # - "4.2) data_src util recover original filename.bat"
    BATCHES_FOR[OP_SORT_DST] = [
        "5.2) data_dst sort.bat",
    ]
    BATCHES_FOR[OP_DELETE_BAD_DST] = [
        "5.1) data_dst view aligned results.bat",
    ]
    # Not Implemented:
    # - "5.1) data_dst view aligned_debug results.bat"
    # - "5.2) data_dst util faceset pack.bat"
    # - "5.2) data_dst util faceset unpack.bat"
    # - "5.2) data_dst util recover original filename.bat"
    # - "5.XSeg) data_dst mask - edit.bat"
    # - "5.XSeg) data_dst mask - fetch.bat"
    # - "5.XSeg) data_dst mask - remove.bat"
    # - "5.XSeg) data_dst trained mask - apply.bat"
    # - "5.XSeg) data_dst trained mask - remove.bat"
    # - "5.XSeg) data_src mask - edit.bat"
    # - "5.XSeg) data_src mask - fetch.bat"
    # - "5.XSeg) data_src mask - remove.bat"
    # - "5.XSeg) data_src trained mask - apply.bat"
    # - "5.XSeg) data_src trained mask - remove.bat"
    # - "5.XSeg) train.bat"
    # Not Implemented:
    # - "10.misc) make CPU only.bat"
    # - "10.misc) start EBSynth.bat"
    BATCHES_FOR[OP_TRAIN_QUICK96] = [
        "6) train Quick96.bat",
    ]
    BATCHES_FOR[OP_TRAIN_SAEHD] = [
        "6) train SAEHD.bat",
    ]
    BATCHES_FOR[OP_MERGE_QUICK96] = [
        "7) merge Quick96.bat",
    ]
    BATCHES_FOR[OP_MERGE_SAEHD] = [
        "7) merge SAEHD.bat",
    ]

    WS_META_NAME = "dlm-workspace.json"
    LAB_META_NAME = "dlm-lab.json"

    @staticmethod
    def existsAs(path, container):
        if container not in DLM.getContainers():
            raise ValueError("container must be one of: {} not {}"
                             "".format(DLM.getContainers(), container))
        if container == DLM.C_DIR:
            return os.path.isdir(path)
        elif container == DLM.C_FILE:
            return os.path.isfile(path)
        else:
            raise NotImplementedError("This should never happen.")
        return False

    @staticmethod
    def getSteps():
        """
        Get the steps of the DLM process.
        DLM.FORM_ORIGINAL:
        - isfile: no steps performed
        - isdir: output of 'extract images'
        DLM.FORM_ALIGNED
        - isfile: invalid
        - isdir: output of 'extract faceset'
        DLM.FORM_MERGED
        - isdir: output of 'MERGE'
        - isfile: output of "merged to " video
        """
        # getCaption must handle each form
        # choose_param must handle each form
        return [DLM.FORM_ORIGINAL, DLM.FORM_ALIGNED, DLM.FORM_MERGED]

    @staticmethod
    def formInfo(role, form, container):
        if role not in DLM.getRoles():
            raise ValueError("role must be one of: {} not {}"
                             "".format(DLM.getRoles(), role))
        if form not in DLM.getForms():
            raise ValueError("form must be one of: {} not {}"
                             "".format(DLM.getForms(), form))
        if container not in DLM.getContainers():
            raise ValueError("container must be one of: {} not {}"
                             "".format(DLM.getContainers(), container))
        ws = self.env['WORKSPACE']
        if form == DLM.FORM_ORIGINAL:
            if container == DLM.C_FILE:
                if role == DLM.ROLE_DST:
                    return {
                        "path": os.path.join(ws, "data_dst.mp4"),
                        "everExists": True,
                    }
                else:
                    return {
                        "path": os.path.join(ws, "data_src.mp4"),
                        "everExists": True,
                    }
            else:
                if role == DLM.ROLE_DST:
                    return {
                        "path": os.path.join(ws, "data_dst"),
                        "everExists": True,
                    }
                else:
                    return {
                        "path": os.path.join(ws, "data_src"),
                        "everExists": True,
                    }
        elif form == DLM.FORM_ALIGNED:
            if container == DLM.C_FILE:
                raise ValueError("There is no aligned video form.")
            else:
                if role == DLM.ROLE_DST:
                    return {
                        "path": os.path.join(ws, "data_dst", "aligned"),
                        "everExists": True,
                    }

                else:
                    return {
                        "path": os.path.join(ws, "data_src", "aligned"),
                        "everExists": True,
                    }

        elif form == DLM.FORM_MERGED:
            if DLM.C_FILE:
                if role == DLM.ROLE_DST:
                    return {
                        "path": os.path.join(ws, "result.mp4"),
                        "everExists": True,
                    }
                    # TODO: ^ handle avi
                else:
                    return {
                        "path": None,
                        "everExists": False,
                    }
            else:
                if role == DLM.ROLE_DST:
                    return {
                        "path": os.path.join(ws, "data_dst", "merged"),
                        "everExists": True,
                    }
                else:
                    return {
                        "path": None,
                        "everExists": False,
                    }

    def __init__(self, dflDir):
        self._errors = []
        self.meta = None
        self.userVideosPath = os.path.join(RCProject.PROFILE, "Videos",
                                           "face-videos")
        self.myAppData = RCProject.RC_APPDATA
        self.userMetaName = "dlm.json"

        self.userVideosPath = None

        self._cmdDone = True
        self._runCmd = None

        self.prompts = []
        self.prompts.append(" : ")

        self.promptEnds = []
        self.promptEnds.append("? : ")

        self.deadFlags = []
        self.deadFlags.append("above this error message"
                              " when asking for help")

        self._continuePrompts = []
        self._continuePrompts.append("to continue")
        self._continuePrompts.append("Done.")
        self.logName = "pyrotocanvas-dlm.log"

        try:
            result = self.setDFLDir(dflDir)
            if result is not None:
                self._errors.append(result)
        except ValueError as ex:
            print(ex)
            self._errors.append("{}".format(ex))
        self.loadLabDefaults() # sets self.meta

    def popErrors(self):
        errors = self._errors
        self._errors = []
        return errors

    def setDFLDir(self, dflDir):
        self._dflDir = dflDir
        return self.generateEnv()

    def isInLab(self, path):
        if platform.system() == "Windows":
            wsLower = self.env["WORKSPACE"].lower()
            return path.lower().startswith(wsLower)
        return path.startswith(self.env["WORKSPACE"])

    @staticmethod
    def any_in(needles, haystack):
        for needle in needles:
            if needle in haystack:
                return True
        return False

    @staticmethod
    def getContainers():
        """
        Get the container list to determine what dict keys to use and
        whether the keys passed to the function are correct.
        """
        return [DLM.C_DIR, DLM.C_FILE]

    @staticmethod
    def getZones():
        """
        'lab' means in DeepFaceLabs directory (or subdirectories).
        'storage' means in anywhere else
        """
        return [DLM.ZONE_LAB, DLM.ZONE_STORAGE]

    @staticmethod
    def getForms():
        """
        Get the form list to determine what dict keys to use and
        whether the keys passed to the function are correct.
        """
        return [DLM.FORM_ORIGINAL, DLM.FORM_ALIGNED, DLM.FORM_MERGED]

    @staticmethod
    def getRoles():
        """
        Get the form list to determine what dict keys to use and
        whether the keys passed to the function are correct.
        src is the face you want to place
        dst is the face you want to replace
        """
        return ['src', 'dst']

    @staticmethod
    def getDtPathString(dateSep="-", dtSep="_", timeSep=".."):
        return DLM.getDtString(dateSep=dateSep, dtSep=dtSep,
                              timeSep=timeSep)

    @staticmethod
    def getDtString(dateSep="-", dtSep=" ", timeSep=":"):
        fmt = '%Y{ds}%m{ds}%d{dts}%H{ts}%M{ts}%S'.format(
            ds=dateSep,
            dts=dtSep,
            ts=timeSep
        )
        nowS = datetime.now().strftime(fmt)
        return nowS

    def generateEnv(self):
        """
        Mimic DeepFaceLab\_internal\setenv.bat but generate
        self.env instead of setting environment variables.
        Always use getenv to use the variables to run another file.

        Set self._dflDir before running this. such as via the
        constructor.
        """
        env = {}
        self.env = env

        # Base env
        if self._dflDir is None:
            return "The _dflDir does not exist: {}".format(self._dflDir)
        env["~dp0"] = self._dflDir  # if playing back, do os.chdir(v)
        if not env["~dp0"].endswith(os.sep):
            env["~dp0"] += os.sep
        env["INTERNAL"] = os.path.join(self._dflDir, "_internal")
        if not os.path.isdir(env["INTERNAL"]):
            raise ValueError("{} does not exist. You must provide a"
                             " valid DeepFaceLabs directory."
                             "".format(env["INTERNAL"]))
        intl = env["INTERNAL"]
        env["LOCALENV_DIR"] = os.path.join(intl, "_e")
        le = env["LOCALENV_DIR"]
        env["TMP"] = os.path.join(le, "t")
        env["TEMP"] = os.path.join(le, "t")
        env["HOME"] = os.path.join(le, "u")
        env["HOMEPATH"] = os.path.join(le, "u")
        env["USERPROFILE"] = os.path.join(le, "u")
        env["LOCALAPPDATA"] = os.path.join(env["USERPROFILE"],
                                           "AppData", "Local")
        env["APPDATA"] = os.path.join(env["USERPROFILE"],
                                      "AppData", "Roaming")

        # Python env
        # env["PYTHON_PATH"] = os.path.join(intl, "python-3.6.8")
        pythons = []
        for sub in os.listdir(intl):
            subPath = os.path.join(intl, sub)
            if not os.path.isdir(subPath):
                continue
            if sub.startswith("python"):
                pythons.append(sub)  # Dir NOT exe
        env["PYTHON_PATH"] = os.path.join(intl, pythons[0])
        if len(pythons) > 1:
            print("WARNING: You have more than one python* in {}"
                  "(chose {}): {}"
                  "".format(intl, env["PYTHON_PATH"], pythons))

        env["PYTHONHOME"] = None
        env["PYTHONPATH"] = None
        # ^ Avoid interfering with the default python.
        pydir = env["PYTHON_PATH"]
        py_exe = "python"
        pyw_exe = "pythonw"
        if platform.system() == "Windows":
            py_exe = "python.exe"
            pyw_exe = "pythonw.exe"
        env["PYTHONEXECUTABLE"] = os.path.join(pydir, py_exe)
        env["PYTHONWEXECUTABLE"] = os.path.join(pydir, pyw_exe)
        env["PYTHON_EXECUTABLE"] = os.path.join(pydir, py_exe)
        env["PYTHONW_EXECUTABLE"] = os.path.join(pydir, pyw_exe)
        env["PYTHON_BIN_PATH"] = env["PYTHON_EXECUTABLE"]
        env["PYTHON_LIB_PATH"] = os.path.join(pydir, "Lib",
                                              "site-packages")
        env["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(
            env["PYTHON_LIB_PATH"],
            "PyQt5",
            "Qt",
            "plugins"
        )
        self._morePaths = [pydir, os.path.join(pydir, "Scripts")]

        # CUDA Env
        self._morePaths = [os.path.join(intl, "CUDA")] + self._morePaths
        wholeV = platform.uname().version
        parts = wholeV.split(".")
        v = ".".join(parts[:2])
        cudaVerSub = None
        if v == "10.0":
            cudaVerSub = "Win10.0"
        else:
            cudaVerSub = "Win6.x"
        env["V"] = v
        self._morePaths = (
            [os.path.join(intl, "CUDNN", cudaVerSub)] + self._morePaths
        )

        # Additional env
        env["XNVIEWMP_PATH"] = os.path.join(intl, "XnViewMP")
        env["FFMPEG_PATH"] = os.path.join(intl, "ffmpeg")
        self._morePaths = (
            [env["XNVIEWMP_PATH"], env["FFMPEG_PATH"]] + self._morePaths
        )
        env["WORKSPACE"] = os.path.join(os.path.dirname(intl),
                                        "workspace")
        env["DFL_ROOT"] = os.path.join(intl, "DeepFaceLab")
        env["TF_MIN_REQ_CAP"] = 30

        # collect _morePaths
        env["PATH"] = os.pathsep.join(
            self._morePaths + [os.environ["PATH"]]
        )
        self._chars = ""
        self.ws = DLMWorkspace(self, env["WORKSPACE"]) # yes, send self
        self.ws.populate()
        if self.myAppData is not None:
            self.userMetaPath = os.path.join(self.myAppData,
                                             self.userMetaName)
        return None

    def saveLabMeta(self):
        self.ws.save()

    def loadLabDefaults(self):
        if self.meta is None:
            self.meta = {}
        self.meta["src_full"] = None
        self.meta["src_face"] = None
        self.meta["dst_full"] = None
        self.meta["dst_face"] = None

    def loadLabMeta(self):
        self.loadLabDefaults()
        if os.path.isfile(self._dflDir):
            tmp = json.load(self._dflDir)
            for k,v in tmp.items():
                if len(k.strip()) > 0:
                    self.meta[k] = v


    def train(self, model, baseModel="SAEHD", gpu="0"):
        """
        Run DFL_ROOT\main.py to train the model on the aligned data.
        (Mimic "6) train SAEHD.bat")

        Sequential arguments:
        model -- Name the model you want to create or reuse (to avoid
                 distorting the source incorrectly, the forum says to
                 use a model that uses the same source).
        baseModel -- Choose a base model that exists in a clean copy
                     of DeepFace Lab, such as "SAEHD" or "Quick96" which
                     will serve as a basis for creating a trained model
                     (used as the --model param for main.py, but does
                     not actually name the trained model--to name that,
                     use the model param of this method).
        gpu -- GPU number or comma-separated list of GPUs.
        """

        # "%PYTHON_EXECUTABLE%" "%DFL_ROOT%\main.py" train ^
        # --training-data-src-dir "%WORKSPACE%\data_src\aligned" ^
        # --training-data-dst-dir "%WORKSPACE%\data_dst\aligned" ^
        # --pretraining-data-dir "%INTERNAL%\pretrain_CelebA" ^
        # --model-dir "%WORKSPACE%\model" ^
        # --model SAEHD
        self._model = model
        self._gpu = gpu
        env = self.env
        ws = env["WORKSPACE"]
        intl = env["INTERNAL"]
        main_py = os.path.join(env["DFL_ROOT"], "main.py")
        if not os.path.isfile(main_py):
            raise RuntimeError("{} does not exist.".format(main_py))
        parts = [env["PYTHON_EXECUTABLE"], main_py, "train",
                 "--training-data-src-dir",
                 os.path.join(ws, "data_src", "aligned"),
                 "--training-data-dst-dir",
                 os.path.join(ws, "data_dst", "aligned"),
                 "--pretraining-data-dir",
                 os.path.join(intl, "pretrain_CelebA"),
                 "--model-dir",
                 os.path.join(ws, "model"),
                 "--model", baseModel]
        self.run_command(parts, shell=True)


    def monitor_output(self, out, isStdErr):
        """
        Monitor and handle the output of a stream.
        """
        while True:
            if self._p is None:
                break
            rawOut = out.read(1)
            self.handle_byte(rawOut, isStdErr)
            # self._q.put(line)
            if len(rawOut) < 1:
                break


        """
        for line in iter(out.readline, b''):
            # self._q.put(line)
            self.handle_bytes(line, isStdErr)
        """
        # ^ readline doesn't get partial lines such as prompts.
        print("Output finished (error stream: {})"
              "".format(isStdErr))
        out.close()


    def is_prompt(self, line):
        if line in self.prompts:
            return True
        for end in self.promptEnds:
            if line.endswith(end):
                return True
        return False


    def handle_byte(self, rawOut, isStdError):
        thisC = rawOut.decode(errors='ignore')
        self._chars += thisC
        # NOTE: rawOut may be b'\r' then later b'\n'
        # print('got "{}"'.format(rawOut))
        # print('got "{}"'.format(thisC))
        _chars = self._chars
        if _chars.endswith(os.linesep) or self.is_prompt(_chars):
            self._chars = ""  # prevent other thread from getting it!
            self.handle_line(_chars.rstrip(os.linesep), isStdError)
        else:
            pass
            # print("[dfl.py] waiting for more (have \"{}\")"
            # "".format(self._chars))


    def handle_bytes(self, rawOut, isStdError):
        line = rawOut.strip().decode(errors='ignore')
        self.handle_line(line, isStdError)

    def _enter_cmd(self, sendS, addNewline=True, silent=False):
        if not silent:
            print("[dfl.py] automatically entering: {}".format(sendS))
        # self._p.communicate(thisB)
        # ^ waits until process is terminated!
        if len(sendS) > 0:
            thisB = bytes(sendS, 'ascii')
            self._p.stdin.write(thisB)
        if addNewline:
            thisB = bytes(os.linesep, 'ascii')
            self._p.stdin.write(thisB)
        self._p.stdin.flush()
        # print("[dfl.py] entered: {}".format(sendS))


    def handle_line(self, line, isStdError):
        if len(line) < 1:
            # print()
            return
        print(line)
        if self._cmdDone:
            self._enter_cmd("", silent=True)  # press to continue
        for deadFlag in self.deadFlags:
            if deadFlag in line:
                self._cmdDone = True
                print("[dfl.py] detected a fatal error")
                self._enter_cmd("", silent=True)  # press to continue
                return
        parts = line.split(" : ")
        if self.is_prompt(line):
            handled = False
            if self._mode is None:
                raise RuntimeError("[dfl.py] could not detect mode"
                                   " (question) before prompt")
            # elif self._mode == "choose model":
            # print("[dfl.py] answering question...")
            if self._pressChar is None:
                if len(self._choices.keys()) > 0:
                    # There are already models, but there
                    # is no model chosen, so make one
                    if self._choseName is None:
                        raise ValueError("The script is"
                                         " asking for a"
                                         " name"
                                         " but you provided"
                                         " no existing or"
                                         " new name.")
                    print("[dfl.py] INFO: using \"{}\""
                          " and ignoring existing choices: {}"
                          "".format(self._choseName,
                                    self._choices.values()))
                else:
                    print("[dfl.py] INFO: using '{}'"
                          "".format(self._choseName))
                # print("[dfl.py] trying to type model")
                sendS = self._choseName
                self._enter_cmd(sendS)
                # print("[dfl.py] tried to type model")
            else:
                # print("[dfl.py] trying to press {}"
                # "".format(self._pressChar))
                sendS = self._pressChar
                self._enter_cmd(sendS)
                # print("[dfl.py] tried to press {}"
                # "".format(self._pressChar))
                self._pressChar = None
                self._mode = None
                self._choices = None
                self._commands = None
        elif DLM.any_in(self._continuePrompts, line):
            self._enter_cmd("")
            print("[dfl.py] tried to continue (entered newline)")
            # See <https://stackoverflow.com/questions/17173946/
            # python-batch-use-python-to-press-any-key-to-
            # continue>
        elif "saved model" in line:
            if self._mode is not None:
                raise RuntimeError('[dfl.py] found "saved model"'
                                   ' prompt before answering previous'
                                   ' question')
            # "Choose one of saved models, or enter a name to
            # create a new model." [sic]
            self._choices = {}
            self._commands = {}
            self._defaultName = None
            self._defaultChar = None
            self._mode = "choose model"
            self._pressChar = None
            self._choseName = self._model
            print("[dfl.py] detected question: {}".format(self._mode))
        elif "Choose one or several GPU idxs" in line:
            if self._mode is not None:
                raise RuntimeError('[dfl.py] found "saved model"'
                                   ' prompt before answering previous'
                                   ' question')
            # "Choose one or several GPU idxs (separated by comma)"
            self._choices = {}
            self._commands = {}
            self._defaultName = None
            self._defaultChar = None
            self._mode = "choose gpu"
            self._pressChar = self._gpu  # csv is ok
            self._choseName = None
        elif len(parts) == 2:
            parts[0] = parts[0].strip()
            if parts[0].startswith("[") and parts[0].endswith("]"):
                cmdChar = parts[0][1:-1]
                if (len(cmdChar) == 1) and (cmdChar in digits):
                    if self._mode == "choose model":
                        defFlag = " - latest"
                        if parts[1].endswith(defFlag):
                            parts[1] = parts[1][:-len(defFlag)]
                            self._defaultName = parts[1].strip()
                            self._defaultChar = cmdChar
                            # if self._mode == "choose model":
                            if self._model is None:
                                self._model = self._defaultName
                                self._pressChar = cmdChar
                    if parts[1] == self._choseName:
                        print("[dfl.py] INFO: Your"
                              " chosen model \"{}\" is"
                              " option {}"
                              "".format(self._choseName, cmdChar))
                        if self._pressChar is not None:
                            n0 = self._choseName
                            c1 = cmdChar
                            c0 = self._pressChar
                            raise ValueError('You wanted {} which is'
                                             'option {}, but already'
                                             'specified option {}'
                                             ''.format(n0, c1, c0))
                        self._pressChar = cmdChar

                    self._choices[cmdChar] = parts[1].strip()
                else:
                    self._commands[cmdChar] = parts[1].strip()
            else:
                print('[dfl.py] ^ unrecognized option format'
                      ' (expected "[x] : Description" where x is a'
                      ' letter or number)')
        else:
            pass
            # print("[dfl.py] ^ unrecognized line")

    def run_command(self, parts, shell=False):
        """
        Run a DeepFace Lab console script and capture the output.
        """
        if self._runCmd is not None:
            raise RuntimeError("There is already a command running.")
        self._cmdDone = False
        cmd = parts[0]
        self._runCmd = parts
        for i in range(1, len(parts)):
            part = parts[i]
            if " " in part:
                cmd += '" {}"'.format(part)
            else:
                cmd += ' {}'.format(part)
        print("[dfl.py] Running {}...".format(cmd))

        devnull = None
        try:
            devnull = subprocess.DEVNULL
        except AttributeError:
            # Python2
            devnull = open(os.devnull,'r')
            # as per  Brent Writes Code Feb 29 '16 at 21:07
            # (comment to Bryce Guinta's Jan 12 '16 at 17:26 answer)
            # on <https://stackoverflow.com/questions/11729562/
            # disable-pause-in-windows-bat-script>
        # NOTE: Calling Popen with stdin=devnull
        # prevents pause, but there are other questions other than
        # "press any key to continue" to answer so that is not
        # applicable.

        # Python 3.5 adds low-level function subprocess.run
        # which also accepts same params as above plus others:
        # https://docs.python.org/3/library/subprocess.html
        print("[dfl.py] Opening process...")
        self._p = subprocess.Popen(parts, env=self.getenv(),
                                   cwd=self.env["~dp0"],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE,
                                   shell=shell, close_fds=True)
        # close_fds: Do not let the subproces inherit open file
        # descriptors.
        self._code = None
        self._mode = None
        self._choices = None
        self._commands = None
        self._defaultName = None
        # ^ default Name to help choose defaultChar
        # ^ that is the value after the command, such as rename in:
        # [r] : rename
        #  where 'r' is cmdChar (pressChar is a cmdChar to send stdin)
        self._defaultChar = None  # default value for pressChar
        self._pressChar = None  # send this character to stdin
        # self._q = Queue()
        self._t0 = None
        self._t1 = None
        self._t0 = Thread(target=self.monitor_output,
                          args=(self._p.stdout, False))
        self._t0.daemon = True # thread dies with the program
        self._t0.start()
        self._t1 = Thread(target=self.monitor_output,
                          args=(self._p.stderr, True))
        self._t1.daemon = True # thread dies with the program
        self._t1.start()

        while True:
            # print("[dfl.py] Polling...")
            self._code = self._p.poll()
            if self._code is not None:
                print("[dfl.py] The process completed with exit code {}"
                      "".format(code))
                break
            if self._cmdDone:
                print("[dfl.py] terminating watch threads...")
                self._t0.join()
                self._t0 = None
                self._t1.join()
                self._t1 = None
                if self._p is not None:
                    print("[dfl.py] terminating process...")
                    self._p.terminate()
                    self._p = None
                break
            """
            stdout, stderr = self._p.communicate()
            print("[dfl.py] Reading output stream...")
            se = ''
            so = self._p.stdout.readline()
            so = nonBlockReadline(self._p.stdout)

            if getErr:
                print("[dfl.py] Reading error stream...")
                se = self._p.stderr.readline()
                ^ will wait forever
                se = nonBlockReadline(self._p.stderr)

            so, se = (self._p.stdout.readline(),
                      self._p.stderr.readline())
            stdall = [so, se]
            """
        self._p = None
        self._cmdDone = True
        self._runCmd = None
        return self._code


    def getenv(self):
        ret = os.environ.copy()
        for k, v in self.env.items():
            if k == "~dp0":
                pass
                # os.chdir(v)
            elif v is None:
                pass
                # os.environ.remove(k)
            elif k == "PATH":
                # Make sure it is up to date:
                # os.environ["PATH"] = os.pathsep.join(
                # self._morePaths + [os.environ["PATH"]]
                # )
                ret[k] = str(v)
            else:
                ret[k] = str(v)
        return ret


    def setenv(self):
        # Usually, use subprocess.Popen(path, env=self.env) instead
        # (wipe vars with None in a copy though)
        for k, v in self.env.items():
            if k == "~dp0":
                os.chdir(v)
            elif v is None:
                os.environ.remove(k)
            elif k == "PATH":
                # Make sure it is up to date:
                os.environ["PATH"] = os.pathsep.join(
                    self._morePaths + [os.environ["PATH"]]
                )
            else:
                os.environ[k] = str(v)

    def help(self):
        return dlm_help_fmt.format(self._dflDir)

    def help_install(self):
        return dfl_install_help_fmt.format(self._dflDir)

    def isAcceptableVideo(self, path):
        dotExts = [".mp4", ".m4v"]
        if not path[-4:].lower() in dotExts:
            return False
        return True

