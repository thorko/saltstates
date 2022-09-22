# Import Salt libs
import salt.utils.pkg
import salt.utils.platform
import salt.utils.versions
from salt.exceptions import CommandExecutionError, MinionError, SaltInvocationError

# Import 3rd-party libs
from salt.ext import six
from salt.modules.pkg_resource import _repack_pkgs
from salt.output import nested
from salt.utils.functools import namespaced_function as _namespaced_function
from salt.utils.odict import OrderedDict as _OrderedDict

from subprocess import Popen, PIPE

import os
import pwd

def _check(name):
    cmd = "pacman -Q " + name
    sp = Popen(cmd,shell=True)
    rc = sp.wait()
    if rc != 0:
        return False
    else:
        return True

def _demote(user_id, user_gid):
    def set_ids():
        os.setgid(user_gid)
        os.setuid(user_id)

    return set_ids

def _install(name,runas,password,updateflag,overwrite=False):
    # yay args
    # update package if updateflag is there
    if overwrite:
        overwrite = "--overwrite '*'"
    else:
        overwrite = ""
    action = "installed"
    if updateflag != None and os.path.isfile(updateflag):
        yay_args = "--aur --answerclean None --answeredit None --answerdiff None --noconfirm --sudoflags '-S' " + overwrite
        action = "updated"
    else:
        yay_args = "--answerclean None --answeredit None --answerdiff None --noconfirm --sudoflags '-S' " + overwrite
    cmd = "echo '{2}' |yay -S {0} {1}".format(yay_args,name,password)
    uid=pwd.getpwnam(runas).pw_uid
    gid=pwd.getpwnam(runas).pw_gid

    sp = Popen(cmd, preexec_fn=_demote(uid,gid), shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stderr = sp.communicate()
    rc = sp.wait()
    if rc != 0:
        return {"status": False, "action": action, "msg": stderr}
    else:
        # if updateflag specified and updated remove updateflag
        if updateflag != None and os.path.isfile(updateflag):
            os.remove(updateflag)
        return {"status": True, "action": action, "msg": ""}

def installed(
    name,
    runas=None,
    password=None,
    updateflag=None,
    **kwargs):

    ret = {"name": name, "result": False, "changes": {}, "comment": ""}

    if password is None or runas is None:
        ret["result"] = False
        ret["comment"] = "password and runas needed"
        return ret

    # check if yay is installed
    cmd = "pacman -Q yay"
    sp = Popen(cmd,shell=True)
    rc = sp.wait()
    if rc != 0:
        ret["result"] = False
        ret["comment"] = "yay is not installed"
        return ret

    # check if packages is already installed
    result = _check(name)
    if result:
        if updateflag == None or not os.path.isfile(updateflag):
            ret["result"] = result
            ret["comment"] = "{0} is already installed".format(name)
            return ret

    # check if in test mode
    if __opts__["test"]:
        ret["result"] = None
        if updateflag != None:
            ret["comment"] = "{0} would be updated".format(name)
            ret["changes"] = {"updated": {"{0} updating".format(name)}}
        else:
            ret["comment"] = "{0} would be installed".format(name)
            ret["changes"] = {"installed": {"{0} installing".format(name)}}
        return ret

    result = _install(name, runas, password, updateflag)
    if result["status"]:
        ret["result"] = result["status"]
        ret["comment"] = "{0} has been {1}".format(name, result["action"])
        ret["changes"] = {"installed": {"{0}".format(name)}}
        return ret
    else:
        ret["result"] = result["status"]
        ret["comment"] = "{0} not being installed".format(name)
        ret["changes"] = {"error": result["msg"]}
        return ret
