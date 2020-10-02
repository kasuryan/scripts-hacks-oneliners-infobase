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

* If you wish to find config applied to individual pools. 
```
# ceph osd dump | grep pool
pool 1 'prod-metrics-ssd' replicated size 3 min_size 2 crush_rule 2 object_hash rjenkins pg_num 2048 pgp_num 2048 last_change 560437 flags hashpspool stripe_width 0 application rbd
pool 2 'prod-cinder-ssd' replicated size 3 min_size 2 crush_rule 2 object_hash rjenkins pg_num 4096 pgp_num 4096 last_change 589030 flags hashpspool stripe_width 0 application rbd
pool 3 'prod-nova-hc' replicated size 3 min_size 2 crush_rule 1 object_hash rjenkins pg_num 1024 pgp_num 1024 last_change 616546 flags hashpspool stripe_width 0 application rbd
pool 4 'prod-glance-hc' replicated size 3 min_size 2 crush_rule 1 object_hash rjenkins pg_num 1024 pgp_num 1024 last_change 616551 flags hashpspool stripe_width 0 application rbd
pool 5 'prod-cinder-hc' replicated size 3 min_size 2 crush_rule 1 object_hash rjenkins pg_num 4096 pgp_num 4096 last_change 616233 flags hashpspool stripe_width 0 application rbd
pool 6 'backup' replicated size 3 min_size 2 crush_rule 1 object_hash rjenkins pg_num 128 pgp_num 128 last_change 610506 flags hashpspool stripe_width 0 application rbd
pool 7 'defaults.rgw.buckets.data' replicated size 3 min_size 2 crush_rule 1 object_hash rjenkins pg_num 256 pgp_num 256 last_change 563695 flags hashpspool stripe_width 0
pool 8 'defaults.rgw.buckets.index' replicated size 3 min_size 2 crush_rule 2 object_hash rjenkins pg_num 128 pgp_num 128 last_change 563694 flags hashpspool stripe_width 0
pool 9 '.rgw.root' replicated size 3 min_size 2 crush_rule 1 object_hash rjenkins pg_num 8 pgp_num 8 last_change 563684 flags hashpspool stripe_width 0 application rgw
pool 10 'default.rgw.control' replicated size 3 min_size 2 crush_rule 1 object_hash rjenkins pg_num 8 pgp_num 8 last_change 563675 flags hashpspool stripe_width 0 application rgw
pool 11 'default.rgw.meta' replicated size 3 min_size 2 crush_rule 1 object_hash rjenkins pg_num 8 pgp_num 8 last_change 563676 flags hashpspool stripe_width 0 application rgw
pool 12 'default.rgw.log' replicated size 3 min_size 2 crush_rule 1 object_hash rjenkins pg_num 8 pgp_num 8 last_change 563677 flags hashpspool stripe_width 0 application rgw
pool 13 'default.rgw.buckets.index' replicated size 3 min_size 2 crush_rule 2 object_hash rjenkins pg_num 8 pgp_num 8 last_change 563699 flags hashpspool stripe_width 0 application rgw
pool 14 'default.rgw.buckets.data' replicated size 3 min_size 2 crush_rule 1 object_hash rjenkins pg_num 8 pgp_num 8 last_change 563696 flags hashpspool stripe_width 0 application rgw
pool 16 'stg-cinder-ssd' replicated size 3 min_size 2 crush_rule 2 object_hash rjenkins pg_num 128 pgp_num 128 last_change 593522 flags hashpspool stripe_width 0 application rbd
```

* Look at the crush map rules that decide the placement of objects.
```
# ceph osd crush rule dump
[
    {
        "rule_id": 0,
        "rule_name": "replicated_rule",
        "ruleset": 0,
        "type": 1,
        "min_size": 1,
        "max_size": 10,
        "steps": [
            {
                "op": "take",
                "item": -1,
                "item_name": "default"
            },
            {
                "op": "chooseleaf_firstn",
                "num": 0,
                "type": "host"
            },
            {
                "op": "emit"
            }
        ]
    },
    {
        "rule_id": 1,
        "rule_name": "hdd-rule",
        "ruleset": 1,
        "type": 1,
        "min_size": 1,
        "max_size": 10,
        "steps": [
            {
                "op": "take",
                "item": -27,
                "item_name": "default~hdd"
            },
            {
                "op": "chooseleaf_firstn",
                "num": 0,
                "type": "rack"
            },
            {
                "op": "emit"
            }
        ]
    },
    {
        "rule_id": 2,
        "rule_name": "ssd-rule",
        "ruleset": 2,
        "type": 1,
        "min_size": 1,
        "max_size": 10,
        "steps": [
            {
                "op": "take",
                "item": -2,
                "item_name": "default~ssd"
            },
            {
                "op": "chooseleaf_firstn",
                "num": 0,
                "type": "rack"
            },
            {
                "op": "emit"
            }
        ]
    }
]
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
## Scenario , a custom ceph pool (from SSD tier) backend for some KVM instances.
```
# ceph osd pool create libvirt-pool-ssd 128 replicated ssd-rule
# rbd pool init libvirt-pool-ssd

Assign appropriate authorization
# ceph auth get-or-create client.libvirt mon 'allow r' osd 'allow rwx pool=libvirt-pool-ssd, allow rwx pool=backup' -o /etc/ceph/ceph.client.libvirt.keyring

Back to the KVM instance, create a image file as below.
rbd create --pool libvirt-pool-ssd --image atl1-efk01-image -s 20G

Validate your creation with below
# rbd -n client.libvirt -p libvirt-pool-ssd ls
# rbd -n client.libvirt info libvirt-pool-ssd/atl1-efk01-image
```
