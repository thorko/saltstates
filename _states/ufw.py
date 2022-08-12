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
import re

def _check(name):
    cmd = None

    cmd = "ufw status | grep '# {0}'".format(name)
    sp = Popen(cmd,shell=True)
    rc = sp.wait()
    if rc != 0:
        return False
    else:
        return True

def _check_absent(name):
    cmd = None

    cmd = "ufw status | grep '# {0}'".format(name)
    sp = Popen(cmd,shell=True)
    rc = sp.wait()
    if rc != 0:
        return True
    else:
        return False

def _add(name,mode,direction,fr,to,port,proto):
    p = None
    pr = None
    if port == "any":
        p = ""
    else:
        p = "port {0}".format(port)

    if proto == "both":
        pr = ""
    else:
        pr = "proto {0}".format(proto)

    cmd = "ufw {0} {1} from {2} to {3} {4} {5} comment '{6}'".format(mode,direction,fr,to,pr,p,name)
    sp = Popen(cmd,shell=True,stdin=PIPE,stdout=PIPE,stderr=PIPE)
    stderr = sp.communicate()
    rc = sp.wait()
    if rc != 0:
        return {"status": False, "action": "add", "msg": stderr}
    else:
        return {"status": True, "action": "add", "msg": ""}

def _delete(name,mode,fr,to,port,proto):
    p = None
    pr = None
    if port == "any":
        p = ""
    else:
        p = "port {0}".format(port)

    if proto == "both":
        pr = ""
    else:
        pr = "proto {0}".format(proto)

    cmd = "ufw delete {0} from {1} to {2} {3} {4}".format(mode,fr,to,pr,p)
    sp = Popen(cmd,shell=True,stdin=PIPE,stdout=PIPE,stderr=PIPE)
    stderr = sp.communicate()
    rc = sp.wait()
    if rc != 0:
        return {"status": False, "action": "delete", "msg": stderr}
    else:
        return {"status": True, "action": "delete", "msg": ""}


def present(name,mode=None,direction=None,fr="any",to="any",port="any",proto=None,**kwargs):

    ret = {"name": name, "result": False, "changes": {}, "comment": ""}

    if mode is None or direction is None or proto is None:
        ret["result"] = False
        ret["comment"] = "mode, direction and proto is needed"
        return ret

    # check if yay is installed
    cmd = "pacman -Q ufw"
    sp = Popen(cmd,shell=True)
    rc = sp.wait()
    if rc != 0:
        ret["result"] = False
        ret["comment"] = "ufw is not installed"
        return ret

    # check if packages is already installed
    result = _check(name)
    if result:
        ret["result"] = result
        ret["comment"] = "{0} is already configured: {1} {2} {3} {4} {5} {6}".format(name,mode,direction,fr,to,proto,port)
        return ret

    # check if in test mode
    if __opts__["test"]:
        ret["result"] = None
        ret["comment"] = "{0} would configure".format(name)
        ret["changes"] = {"ufw rule": {"{0} configured".format(name)}}
        return ret

    result = _add(name,mode,direction,fr,to,port,proto)
    if result["status"]:
        ret["result"] = result["status"]
        ret["comment"] = "Rule has been added"
        ret["changes"] = {"added": {"{0} {1} from {2} to {3} proto {4} port {5}".format(mode,direction,fr,to,proto,port)}}
        return ret
    else:
        ret["result"] = result["status"]
        ret["comment"] = "Rule not added"
        ret["changes"] = {"error": result["msg"]}
        return ret

def absent(name,mode,direction=None,fr="any",to="any",port="any",proto=None,**kwargs):
    ret = {"name": name, "result": False, "changes": {}, "comment": ""}

    if mode is None or direction is None or proto is None:
        ret["result"] = False
        ret["comment"] = "mode, direction, port and proto is needed"
        return ret

    # check if yay is installed
    cmd = "pacman -Q ufw"
    sp = Popen(cmd,shell=True)
    rc = sp.wait()
    if rc != 0:
        ret["result"] = False
        ret["comment"] = "ufw is not installed"
        return ret

    # check if packages is already installed
    result = _check_absent(name)
    if result:
        ret["result"] = result
        ret["comment"] = "{0} isn't present: {1} {2} {3} {4} {5} {6}".format(name,mode,direction,fr,to,proto,port)
        return ret

    # check if in test mode
    if __opts__["test"]:
        ret["result"] = None
        ret["comment"] = "{0} would delete rule".format(name)
        ret["changes"] = {"ufw rule": {"{0} configured".format(name)}}
        return ret

    result = _delete(name,mode,fr,to,port,proto)
    if result["status"]:
        ret["result"] = result["status"]
        ret["comment"] = "Rule has been deleted"
        ret["changes"] = {"deleted": {"{0} {1} from {2} to {3} proto {4} port {5}".format(mode,direction,fr,to,proto,port)}}
        return ret
    else:
        ret["result"] = result["status"]
        ret["comment"] = "Rule not deleted"
        ret["changes"] = {"error": result["msg"]}
        return ret
