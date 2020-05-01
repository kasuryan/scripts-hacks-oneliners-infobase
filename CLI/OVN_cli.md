* as long as you can reach a CTL node you can access the north bound DB.
```ovn-nbctl --db=tcp:172.16.20.100:6641 show
```
* as long as you can reach a CTL node you can access the north bound DB.
```ovn-sbctl --db=tcp:172.16.20.100:6642 show
```
* You could as well Apply --db to all commands below if you are remotely connecting to the OVN DBs.
```
$ ovn-nbctl list Logical_Switch
$ ovn-nbctl list Logical_Switch_Port
$ ovn-nbctl list ACL
$ ovn-nbctl list Address_Set
$ ovn-nbctl list Logical_Router
$ ovn-nbctl list Logical_Router_Port
$ ovn-nbctl list Gateway_Chassis

$ ovn-sbctl list Chassis
$ ovn-sbctl list Encap
$ ovn-sbctl list Address_Set
$ ovn-sbctl lflow-list
$ ovn-sbctl list Multicast_Group
$ ovn-sbctl list Datapath_Binding
$ ovn-sbctl list Port_Binding
$ ovn-sbctl list MAC_Binding
$ ovn-sbctl list Gateway_Chassis
```
* if for some weird reason, your ovn north DB is wiped out, a repair could be done with below command , which needs to be run from inside of neutron_api container.
Run from neutron api container on controller node
```
neutron-ovn-db-sync-util --config-file /usr/share/neutron/neutron-dist.conf \
--config-dir /usr/share/neutron/server --config-file /etc/neutron/neutron.conf \
--config-file /etc/neutron/plugin.ini --config-dir /etc/neutron/conf.d/common \
--config-dir /etc/neutron/conf.d/neutron-server --ovn-neutron_sync_mode=repair
```
