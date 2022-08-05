# saltstates
state modules for saltstack

* [saltstates](#saltstates)
   * [general usage](#general-usage)
   * [salt.states.ufw.present](#saltstatesufwpresent)
      * [example](#example)
   * [salt.states.ufw.absent](#saltstatesufwabsent)
      * [example](#example-1)
   * [salt.states.yay.installed](#saltstatesyayinstalled)
      * [example](#example-2)


## general usage

- create a *_states* directory in your *file_roots*

- place the <state>.py file in *_states* 

  

## salt.states.ufw.present

(name,mode=None,direction=None,fr="any",to="any",port="any",proto=None,**kwargs)

create firewall rules using ufw command

**name**
	the identifier for the firewall rule. will be added as comment and displayed at the ```ufw status``` output

**mode**
	the mode used for ufw, can be *allow* or *deny* 

**direction**
	the direction for the firewall rule. can be *in* or *out* 

**fr**
	from which ip prefix allow connections

**to**
	to which ip prefix allow connections

**port**
	which port(s) to be used for the firewall rule

**porto**
	which protocol to be used, can be *tcp*, *udp* or *both*

### example

```yaml
port_443:
  ufw.present:
    - mode: allow
    - direction: in
    - fr: any
    - to: 192.168.0.13
    - proto: tcp
```



## salt.states.ufw.absent

(name,mode,direction=None,fr="any",to="any",port="any",proto=None,**kwargs)

delete firewall rules using ufw

**name**
	the identifier for the firewall rule. 

**mode**
	the mode used for ufw, can be *allow* or *deny* 

**direction**
	the direction for the firewall rule. can be *in* or *out* 

**fr**
	from which ip prefix allow connections

**to**
	to which ip prefix allow connections

**port**
	which port(s) to be used for the firewall rule

**porto**
	which protocol to be used, can be *tcp*, *udp* or *both*

### example

```yaml
port_443:
  ufw.absent:
    - mode: allow
    - direction: in
    - fr: any
    - to: 192.168.0.13
    - proto: tcp
```



## salt.states.yay.installed

(name,runas=None,password=None,updateflag=None, **kwargs)

install aur packages with yay

**name**
	the package to be installed with yay

**runas**
	run as user

**password**
	use password when installing the package

**updateflag**
	a file which is used to update the package. The file gets deleted after successful update

### example

```yaml
sensu-agent:
  yay.installed:
    - runas: yay
    - password: {{ pillar['yay_password'] }}
    - updateflag: /tmp/sensu-agent.update
```

