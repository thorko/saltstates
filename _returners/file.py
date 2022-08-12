# Import Salt libs
import salt.utils.json
import time
import logging
import salt.returners

__virtualname__ = 'file'

# Get logging started
log = logging.getLogger(__virtualname__)


def _get_conn():
    if 'config.option' in __salt__:
        statefile = __salt__['config.option']('returner.file.file')
    else:
        cfg = __opts__
        statefile = cfg.get('returner.file.file', None)

    if not statefile:
        statefile = '/tmp/salt-state.t'

    return statefile


def returner(ret):
    statefile = _get_conn()
    status = ''

    data = ret["return"]
    f = open(statefile, 'a')
    if type(data) is dict:
        for key, value in data.items():
            if type(value) is dict:
                f.write('{0} {1} {2}\n'.format(time.strftime("[%Y-%m-%d %H:%M:%S]"), value["result"], key))
        f.close()

def save_load(jid, load, minions=None):
    log.info("calling function save_load")


def get_load(jid):
    log.info("calling function get_load")
