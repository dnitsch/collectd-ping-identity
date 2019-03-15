# collectd-ping-identity

collectd python plugin to read out and parse heartbeat endpoints from PingAccess and PingFederate

DESCRIPTION:
===
collects metrics from the Ping Identity  Heartbeat enpoints and parses them to collectd reader. 

currently only enabled for Ping Access and PingFederate

PRE-REQUISITES:
===

Enable detailed monitoring on the product you wish to monitor, examples and notes aroun the supported products below.

  PingAccess:
  ---
  Available from version (X.x.x)
  `enable.detailed.heartbeat.response=true`

  set collection interval to higher than 0 

  `pa.statistics.window.seconds=10`

  You can enable/disable statistics in this file `$PA_HOME/conf/template/heartbeat.page.json`

  PingFederate:
  --- 
  Available from version (7.3.x) notes on setting up can be found [here](https://ping.force.com/Support/PingFederate/Administration/Enabling-heartbeat-in-PingFederate-7-3-and-above)

  Only available for engine nodes of Ping Federate


  Pip dependencies: `requests` (though this package is part of the distutils so no need to install it specifically from python 2.7)

OPTIONS:
===
`url`  - the heartbeat URL should contain the ```proto//fqdn||ip:port/heartbeatpath```

`type` - accepted values `admin` || `engine`

`product` - accepted values `access` || `federate`

USAGE:
===
Download the `ping_indentity.py` and place it, preferrably in a custom defined diretory to avoid collectd python package clashes e.g. `/var/my/collectd/modules/` 

because of the nature of HTTP heartbeat endpoint - you could elect single master monitoring node that will query all the others, however it is much more common (adviseable) to have the collectd agent per node - [config scenarios](####Scenarios) are covered below.


#### Scenarios
##### Standalone mode PA

PA outputs monitoring on both engine and admin nodes, in cases where you are running PA in standalone mode you will have 

```XML
  <LoadPlugin python>
    Globals true
  </LoadPlugin>
  <Plugin python>
      ModulePath "/var/my/collectd/modules/"
      LogTraces true
      Interactive false
      Import "ping_identity"
      <Module ping_identity>
        url "https://127.0.0.1:3000/pa/heartbeat.ping"
        type "engine"
        product "access"
      </Module>
      <Module ping_identity>
        url "https://127.0.0.1:9000/pa/heartbeat.ping"
        type "admin"
        product "access"
      </Module>
  </Plugin>
```



##### Aggregate mode PF remote and PA local

```XML
  <LoadPlugin python>
    Globals true
  </LoadPlugin>
  <Plugin python>
      ModulePath "/var/my/collectd/modules/"
      LogTraces true
      Interactive false
      Import "ping_identity"
      <Module ping_identity>
        url "https://private.remote.ping-fed.local:9031/pf/heartbeat.ping"
        type "engine"
        product "federate"
      </Module>
      <Module ping_identity>
        url "https://127.0.0.1:3000/pa/heartbeat.ping"
        type "engine"
        product "access"
      </Module>
      <Module ping_identity>
        url "https://127.0.0.1:9000/pa/heartbeat.ping"
        type "admin"
        product "access"
      </Module>
  </Plugin>
```

The plugin by default accepts most metrics, though you should enable/disable the ones you wish you use - refer to the templates.

`Hostname`  and `LastRefreshTime` are ignored by design.

SAMPLE OUTPUT:
===

Using collectd writers you can write a number of systems, examples below are using the cloudwatch.

Ping Access Memory


Ping Access CPU

[1]: https://i.ibb.co/VD94Bff/Screenshot-2019-03-05-at-14-25-46.png
[2]: https://i.ibb.co/8KL1LvB/Screenshot-2019-03-05-at-14-19-36.png
![1]

![2]

Ping Access Applications/OpenConnections


NOTES:
===
SELinux needs to be run in `Permissive` or `Disabled` mode 
