## How Ceph works
  * Core layer: Reliable Autonomous Distributed Object Store(RADOS)
  * RADOS consists of number of OSD(Object Storage daemons)
  * OSD typically mapped to single disk.
  * Other key component is Monitors.
    * They provide a known cluster state including membership using cluster maps.
  * Other core component is manager.
    * responsible for configuration and statistics

  * Librados is a ceph library to build apps that interact directly with Ceph.


## Ceph Info.

  * A true Software Defined Storage.
  * Decentralized storage unlike traditional storage arrays where access is
  managed through controller heads.
  * A well designed and tuned Ceph cluster should be able to meet most performance
  requirements except a few that need very low latency.
  * Provides reliability, while no component is highly available , when clustered
  together any component can fail without causing an inability to service client
  requests
  * Good to go with commodity hardware

## Some use cases
  * 61% of OS users utilize Ceph.
  * Openstack Manila integrates with CephFS
  * RADOS being an object store, Ceph excels at providing object storage via
    Swift or S3.
  * Distributed FS -- web farm
  * Big data

## Memory Usage
  * A healthy cluster running within the recommendation of 200 PGs per OSD will
  probably use less than 4 GB of RAM per OSD.


## SSD nodes in atl1
  * 22 disks of 1.8T = 39.6 T
  24*2.3 = 55.2

## SATA nodes in atl1
  * 12 * 8.9T = 106.8 T
