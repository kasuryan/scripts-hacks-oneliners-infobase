# High Level steps/ Lazy Guide for RBD mirroring setup in 2021 between SRC and DEST.

## Setup Credentials to be used for mirroring and the pools on the target side.

* DEST is our target side and SRC is our source.
* First create the necessary pools on the target side as seen on the source
side.
```
Gather pool data from the source side and use arguments to create pool on the
target side.
# ceph osd pool ls detai

Running below on target to match the source
ceph osd pool create mypool-sata 4096 4096 hdd-rule
ceph osd pool create mypool-ssd 4096 4096 ssd-rule
```

* From the past, we already have a dedicate user created for rbd mirroring in
the past. We will be using the same user for DEST as well
```
Look up the rbdmirroring user list in the below command output and use the
data to create the same user on the target side.
# ceph auth ls

Copy the user permissions to a file
(say /etc/ceph/ceph.client.rbdmirroring.keyring) on the target side
and import the same user authorization on the target side which provides
convenience.

# ceph auth import -i /etc/ceph/ceph.client.rbdmirroring.keyring
```

## PXE nodes setup to facilitate connectivity between sites.

* We will be using point to point VXLAN setup between PXE nodes. On Redhat
nodes, there is a lack of avaialble ifcfg parameter to persist VXLAN setup in a
ifcfg file. So we are going to workaround with the help of systemd service unit
to call a script that sets up VXLAN endpoints on both PXE nodes.

#### steps for DEST node.
* Add below contents to "/etc/systemd/system/vxlan-setup.service"
```
[Unit]
Description=systemd service unit file that sets up VXLAN interface.
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/bin/bash /opt/rbdmirror/vxlan_setup.sh

[Install]
WantedBy=multi-user.target
```

* Host the script at /opt/rbdmirror/vxlan_setup.sh with below contents.
```
#!/bin/bash
ip link add vxlan1 type vxlan id 1001 remote 10.152.110.30 dstport 4789 dev eth1
ip link set vxlan1 mtu 1400
ip addr add dev vxlan1 192.168.99.2/24
ip link set vxlan1 up
firewall-cmd --zone=trusted --add-interface=vxlan1 --permanent
firewall-cmd --reload
```

* Next enable the service and the config will be created every time the system
comes up after a power recycle.
```
# systemctl enable vxlan-setup.service
# systemctl daemon-reload
```

#### steps for SRC node
* Add below contents to "/etc/systemd/system/vxlan-route-setup.service"
```
[Unit]
Description=systemd service unit file that sets up VXLAN interface and static routes to DEST Ceph nodes.
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/bin/bash /opt/rbdmirror/vxlan_route_setup.sh

[Install]
WantedBy=multi-user.target
```
* Host the script at /opt/rbdmirror/vxlan_route_setup.sh with below contents.
```
#!/bin/bash
ip link add vxlan1 type vxlan id 1001 remote 10.153.20.98 dstport 4789 dev eth1
ip link set vxlan1 mtu 1400
ip addr add dev vxlan1 192.168.99.1/24
ip link set vxlan1 up
for i in {11..15} {21..23} {26..28} {31..33} {151..155} {158..162} {165..169}; do ip route add 172.16.23.${i}/32 via 192.168.99.2; done
```

* Next enable the service and the config will be created every time the system
comes up after a power recycle.
```
# systemctl enable vxlan-route-setup.service
# systemctl daemon-reload
```

## Enable traffic back from DEST ceph nodes to SRC PXE node.

* All we need is a static route added on the nodes below. Login the the DEST
director node and run below
```
# export ceph_inv=~/Example_deployment/configs/myregion/ceph/inv
# ansible -i $ceph_inv mon,osds -m shell -a "ip r add 192.168.99.1 via 172.16.23.98" -b

To persist the static route, run below command.

# ansible -i $ceph_inv mons,osds -m copy -a 'content="192.168.99.1 via 172.16.23.98 dev bond0.23\n" dest=/etc/sysconfig/network-scripts/route-bond0.23 mode=0644' -b
```


## Set up Ceph Mirroring on IAD PXE node and testing.

* First lets quickly see the config files in the /etc/ceph directory.
```
[root@SRC-pxe ~]# ls -l /etc/ceph/
total 20
-rw-r--r-- 1 root root 178 Mar 15 06:23 cluster1.client.rbdmirroring.keyring
-rw-r--r-- 1 root root 274 Mar 15 06:06 cluster1.conf
-rw-r--r-- 1 root root 178 Mar 15 06:23 cluster2.client.rbdmirroring.keyring
-rw-r--r-- 1 root root 404 Mar 15 06:10 cluster2.conf
-rw-r--r-- 1 root root  92 Oct 28 16:05 rbdmap
```

* Setup the environment variable for the ceph-rbd-mirror service on the SRC
pxe node.
```
cat > /etc/sysconfig/ceph << EOF
CLUSTER=cluster2
EOF
```

* The systemd unit file is setup as below.
```
cat /etc/systemd/system/ceph-rbd-mirror.target.wants/ceph-rbd-mirror\@cluster2.service
[Unit]
Description=Ceph rbd mirror daemon
After=network-online.target local-fs.target
Wants=network-online.target local-fs.target
PartOf=ceph-rbd-mirror.target

[Service]
LimitNOFILE=1048576
LimitNPROC=1048576
EnvironmentFile=-/etc/sysconfig/ceph
Environment=CLUSTER=ceph
ExecStart=/usr/bin/rbd-mirror -d --cluster ${CLUSTER} --id rbdmirroring --setuser ceph --setgroup ceph
ExecReload=/bin/kill -HUP $MAINPID
PrivateDevices=yes
ProtectHome=true
ProtectSystem=full
PrivateTmp=true
Restart=on-failure
StartLimitInterval=30min
StartLimitBurst=3
TasksMax=infinity

[Install]
WantedBy=ceph-rbd-mirror.target
```

* Start the ceph rbd mirror service on the SRC pxe node.
```
systemctl enable ceph-rbd-mirror.target
systemctl enable ceph-rbd-mirror@cluster2
systemctl start ceph-rbd-mirror@cluster2
```

* Enable mirror on specific pools in image mode
```
rbd mirror pool enable mypool-sata image --cluster cluster2 --id rbdmirroring
rbd mirror pool enable mypool-sata image --cluster cluster1 --id rbdmirroring
```

* Disabling them is as below if ever needed.
```
# Disabling uses these commands.
rbd mirror pool disable mypool-sata --cluster cluster2 --id rbdmirroring
rbd mirror pool disable mypool-sata --cluster cluster1 --id rbdmirroring
```

* # Checking status of mirroring on pools using below.
```
[root@SRC-pxe ~]# rbd --cluster cluster2 --id rbdmirroring mirror pool info mypool-sata
Mode: image
Peers: none
[root@SRC-pxe ~]# rbd --cluster cluster1 --id rbdmirroring mirror pool info mypool-sata
Mode: image
Peers: none
```

* Manually Adding peer for one way replication from cluster1 --> cluster 2
```
root@SRC-pxe ~]# rbd --cluster cluster2 --id rbdmirroring mirror pool peer add mypool-sata client.rbdmirroring@cluster1
318f0e87-c227-419c-b733-7555d03c66c1
```

* Checking the peer visibility on cluster2
```
[root@SRC-pxe ~]# rbd --cluster cluster2 --id rbdmirroring mirror pool info mypool-sata
Mode: image
Peers:
  UUID                                 NAME     CLIENT
  318f0e87-c227-419c-b733-7555d03c66c1 cluster1 client.rbdmirroring

# No peers needs to be added to cluster1 as its a one way replication from
# cluster1 to cluster2, so just add source(cluster1) as a peer to cluster2
# to enable replaying from cluster1 to cluster2

[root@SRC-pxe ~]# rbd --cluster cluster1 --id rbdmirroring mirror pool info mypool-sata
Mode: image
Peers: none
```

* Using a volume to test rbdmirror

```
[root@SRC-cephmon05 ~]# rbd -p mypool-sata info volume-8d3373f4-8a32-4422-85cf-4ec686221771
rbd image 'volume-8d3373f4-8a32-4422-85cf-4ec686221771':
	size 10GiB in 2560 objects
	order 22 (4MiB objects)
	block_name_prefix: rbd_data.7f7af1166950d1
	format: 2
	features: layering, exclusive-lock, object-map, fast-diff, deep-flatten
	flags:
	create_timestamp: Sat Apr 10 01:38:00 2021
```
* Enable Journaling on the test volume.
```
[root@SRC-cephmon05 ~]# rbd -p mypool-sata feature enable volume-8d3373f4-8a32-4422-85cf-4ec686221771 journaling
[root@SRC-cephmon05 ~]# rbd -p mypool-sata info volume-8d3373f4-8a32-4422-85cf-4ec686221771
rbd image 'volume-8d3373f4-8a32-4422-85cf-4ec686221771':
	size 10GiB in 2560 objects
	order 22 (4MiB objects)
	block_name_prefix: rbd_data.7f7af1166950d1
	format: 2
	features: layering, exclusive-lock, object-map, fast-diff, deep-flatten, journaling
	flags:
	create_timestamp: Sat Apr 10 01:38:00 2021
	journal: 7f7af1166950d1
	mirroring state: disabled
```

* Enable mirroring on the volume and verifying.
```
[root@SRC-cephmon05 ~]# rbd -p mypool-sata mirror image enable volume-8d3373f4-8a32-4422-85cf-4ec686221771
Mirroring enabled

[root@SRC-cephmon05 ~]# rbd -p mypool-sata info volume-8d3373f4-8a32-4422-85cf-4ec686221771
rbd image 'volume-8d3373f4-8a32-4422-85cf-4ec686221771':
	size 10GiB in 2560 objects
	order 22 (4MiB objects)
	block_name_prefix: rbd_data.7f7af1166950d1
	format: 2
	features: layering, exclusive-lock, object-map, fast-diff, deep-flatten, journaling
	flags:
	create_timestamp: Sat Apr 10 01:38:00 2021
	journal: 7f7af1166950d1
	mirroring state: enabled
	mirroring global id: 11e78ef7-5568-417b-8c8b-db1b9c1488e3
	mirroring primary: true
```

* On the destination side, you will see up the new volume showing up pretty soon.

```
[root@DEST-cephmon05 ~]# rbd -p mypool-sata ls
[root@DEST-cephmon05 ~]# rbd -p mypool-sata ls
[root@DEST-cephmon05 ~]# rbd -p mypool-sata ls
volume-8d3373f4-8a32-4422-85cf-4ec686221771
[root@DEST-cephmon05 ~]# rbd -p mypool-sata ls
volume-8d3373f4-8a32-4422-85cf-4ec686221771
[root@DEST-cephmon05 ~]# rbd -p mypool-sata info volume-8d3373f4-8a32-4422-85cf-4ec686221771
rbd image 'volume-8d3373f4-8a32-4422-85cf-4ec686221771':
	size 10GiB in 2560 objects
	order 22 (4MiB objects)
	block_name_prefix: rbd_data.23292b6b8b4567
	format: 2
	features: layering, exclusive-lock, object-map, fast-diff, deep-flatten, journaling
	flags:
	create_timestamp: Sat Apr 10 03:07:30 2021
	journal: 23292b6b8b4567
	mirroring state: enabled
	mirroring global id: 11e78ef7-5568-417b-8c8b-db1b9c1488e3
	mirroring primary: false
```
