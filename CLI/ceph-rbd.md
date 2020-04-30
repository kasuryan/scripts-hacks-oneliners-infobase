# Some scenario specific cli usage
## Scenario 1
  * Sometimes a volume delete command via openstack cli results in no action executed in the backend, so we have to unmanage the volume and delete the image in the ceph backend. First check if there are any snapshots on the volume
  ```
  # rbd --pool volumes-pool snap ls volume-73c96f3a-bd0a-43f3-ad08-1d85965f1003
   SNAPID NAME                                           SIZE TIMESTAMP
     1682 snapshot-391beb6d-59f2-425e-9b9c-eca37fedcdff 10GiB Mon Oct 21 03:39:35 2019
  ```
  * If we want to remove snapshots, we will have to purge snapshots. This may fail when the volume is protected like seen below.
  ```
  # rbd $iad2 --pool volumes-pool snap purge volume-73c96f3a-bd0a-43f3-ad08-1d85965f1003
  Removing all snapshots: 0% complete...failed.
  rbd: snapshot 'snapshot-391beb6d-59f2-425e-9b9c-eca37fedcdff' is protected from removal.
  ```
  * So we need to unprotect and then purge the snapshot.
  ```
  # rbd --pool volumes-pool snap unprotect volume-73c96f3a-bd0a-43f3-ad08-1d85965f1003@snapshot-391beb6d-59f2-425e-9b9c-eca37fedcdff
  # rbd $iad2 --pool volumes-sata snap purge volume-73c96f3a-bd0a-43f3-ad08-1d85965f1003
  ```

  * Then we proceed to remove the volume too
  ```
  # rbd $iad2 --pool volumes-sata rm volume-73c96f3a-bd0a-43f3-ad08-1d85965f1003
  ```

##  Scenario 2
  * Flatten an RBD volume when it is involved in a parent child relationship.
  ```
  # rbd $iad1 --pool volumes-pool flatten volume-28a0f35e-27b8-47b8-b5f1-fedb59fbda81
  ```

## Scenario 3
  * Disabling mirror and removing journaling feature on the source volume.
  ```
  # rbd mirror image disable --pool volumes-pool  volume-60474efd-911f-4c3f-85e2-1351e2207748
  # rbd feature disable --pool volumes-pool volume-60474efd-911f-4c3f-85e2-1351e2207748  journal
  ```

## Scenario 4
  * checking the image(basically a disk file), -p specifies the pool where the disk resides.
  ```
  # rbd du -p glance-pool 5033c6c7-221b-417d-8150-f781af9deb54
  NAME                                      PROVISIONED   USED
  5033c6c7-221b-417d-8150-f781af9deb54@snap      81920M 49144M
  5033c6c7-221b-417d-8150-f781af9deb54           81920M      0
  <TOTAL>                                        81920M 49144M
  ```

## Scenario 5
  * to resize(expand) above disk/image to 160GB
  ```
  # rbd resize --size 163840 nova-hc/684f5b05-000d-4d4d-817e-9478c502b4c1_disk
  Resizing image: 100% complete...done.
  ```

## Scenario 6
  * A bunch of openstack volumes which had a delete operation done on them, failed to clear in the ceph backend as they had snapshots on them and were in protected state(some back story with RBD mirroring etc. not going into that)
    * Gather the volume UUIDs in a file.
    Works on a list of volume UUIDs in the text file /tmp/vols & validate on the snap list output for very volume.
    ```
    # for i in `cat /tmp/vols`
      do
      for s in $(rbd-ssd snap ls volume-$i | grep snapshot | awk '{print$2}')
      do echo volume-$i@$s
      done
      done
    ```
    * Now do the actual deletion after unprotecting the snap and removing them.
    ```
    # for i in `cat /tmp/vols`
      do for s in $(rbd-ssd snap ls volume-$i | grep snapshot | awk '{print$2}')
      do rbd-ssd snap unprotect volume-$i@$s
      rbd-ssd snap remove volume-$i@$s
      done
      done
    ```
