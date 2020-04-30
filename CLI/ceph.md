```
# ceph df
GLOBAL:
    SIZE      AVAIL     RAW USED     %RAW USED
    1947T     1939T        8166G          0.41
POOLS:
    NAME                           ID     USED       %USED     MAX AVAIL     OBJECTS
    prod-metrics-ssd               1      44088M      0.04          108T     2802809
    prod-cinder-ssd                2        130G      0.12          108T       33513
    prod-nova-hc                   3        683G      0.13          504T       99487
    prod-glance-hc                 4       1812G      0.35          504T      232373
    prod-cinder-hc                 5      51330M         0          504T       16327
    backup                         6          19         0          504T           2
    defaults.rgw.buckets.data      7           0         0          504T           0
    defaults.rgw.buckets.index     8           0         0          108T           0
    .rgw.root                      9        3177         0          504T           7
    default.rgw.control            10          0         0          504T           8
    default.rgw.meta               11      18953         0          504T          66
    default.rgw.log                12          0         0          504T         217
    default.rgw.buckets.index      13          0         0          108T          11
    default.rgw.buckets.data       14     19688M         0          504T        5176

# ceph osd tree

# ceph osd pool get prod-cinder-ssd min_size
min_size: 2

# ceph -s
  cluster:
    id:     f8f21cdb-b694-471c-a1d8-6fa27bf44c49
    health: HEALTH_OK

  services:
    mon: 5 daemons, quorum atl1-ceph-mon01,atl1-ceph-mon02,atl1-ceph-mon03,atl1-ceph-mon04,atl1-ceph-mon05
    mgr: atl1-ceph-mon01(active), standbys: atl1-ceph-mon02, atl1-ceph-mon03, atl1-ceph-mon04, atl1-ceph-mon05
    osd: 378 osds: 378 up, 378 in
    rgw: 5 daemons active

  data:
    pools:   14 pools, 12848 pgs
    objects: 3115k objects, 2738 GB
    usage:   8166 GB used, 1939 TB / 1947 TB avail
    pgs:     12848 active+clean

  io:
    client:   2876 B/s rd, 1607 kB/s wr, 73 op/s rd, 120 op/s wr

# ceph -s

# ceph -w (Watch)

# ceph df

# ceph osd tree

# ceph osd df tree

# ceph osd pool ls
```

* tells you on which host and which disk is the OSD service running.
```# ceph osd metadata osd.<num>
```

* Where is a particular file written to.
```
# ceph osd map prod-glance-hc e1d28b79-c0b1-4359-ae74-8802534bb8c6
osdmap e6829 pool 'prod-glance-hc' (4) object 'e1d28b79-c0b1-4359-ae74-8802534bb8c6' -> pg 4.debcd926 (4.126) -> up ([494,594,398], p494) acting ([494,594,398], p494)
```

* Ceph Health Detail command helps tell you which osd has how many processes blocked.
```
# ceph health detail
HEALTH_WARN 218 slow requests are blocked > 32 sec. Implicated osds 587
REQUEST_SLOW 218 slow requests are blocked > 32 sec. Implicated osds 587
    199 ops are blocked > 65.536 sec
    19 ops are blocked > 32.768 sec
    osd.587 has blocked requests > 65.536 sec
```
* PG listing(Large output)
```# ceph pg ls

# ceph pg 4.126 query
```
* Listing of files inside a pool.
```# rbd -p glance-hc ls -l
```

* Watching a Image file being written to Ceph
```
# watch -n 1 "rbd -p glance-hc ls -l | grep 39048d2b-23cd-40eb-85bd-ac7da1206c04"
```
