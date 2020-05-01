# 3 node baremetal gluster setup
* Use all disks available to use with parted to setup partition table type and create partitions. in this case just a single partition across all disks with a GPT mklabel and format all the disks with XFS.
```
$ for dev in {g..l}; do parted /dev/sd${dev} mklabel gpt; parted /dev/sd${dev} mkpart primary xfs 0% 100%; mkfs.xfs /dev/sd${dev}1; done
$ for dev in {a..f}; do mkfs.xfs -f /dev/sd${dev}1; done
```
* Create directories(mount points) for all  disks(bricks in gluster terminology)
```$ mkdir -p /data/glusterfs/myvol1/brick{1..12}
```
* Next we need to mount them.
Use the paste command on 2 temporary files that hold device file names(/dev/sdx1) and their respective mountpoints(/data/glusterfs/myvol1/brick?)
```
$ paste /tmp/1 /tmp/2 > /tmp/mounts
$ cat /tmp/mounts
/dev/sda1 /data/glusterfs/myvol1/brick1
/dev/sdb1 /data/glusterfs/myvol1/brick2
/dev/sdc1 /data/glusterfs/myvol1/brick3
/dev/sdd1 /data/glusterfs/myvol1/brick4
/dev/sde1 /data/glusterfs/myvol1/brick5
/dev/sdf1 /data/glusterfs/myvol1/brick6
/dev/sdg1 /data/glusterfs/myvol1/brick7
/dev/sdh1 /data/glusterfs/myvol1/brick8
/dev/sdi1 /data/glusterfs/myvol1/brick9
/dev/sdj1 /data/glusterfs/myvol1/brick10
/dev/sdk1 /data/glusterfs/myvol1/brick11
/dev/sdl1 /data/glusterfs/myvol1/brick12

$ cat /tmp/mounts | while read x y ; do mount $x $y; done
```
* With all bricks(disks) mounted and available. Create volumes as desired on top of them.
Create a subdirectory with the volume name under each brick using code below. Here under each brick i will be using a subdirectory that has name of the volume.

  * First i will be generate a big chunk of parameters which identify the bricks that go on to form a gluster volume

  * Example here i say: from brick1 to brick12, generate a subdirectory name matching my volume name that i desire to create. This is in python.
  The ind-ceph006-sata, ind-ceph-013-sata and ind-ceph020-sata are the 3 the short names of the gluster nodes.
  ```
  for b in range(1,12):
      for n in ['ind-ceph006-sata','ind-ceph013-sata','ind-ceph020-sata']:
          print("{}:/data/glusterfs/myvol1/brick{}/images".format(n,b), end=' ')
  ```
* Now i have all the parameters generated as text to be passed to the gluster volume creation command. Below example creates a gluster volume with 3 replicas across the
the 3 nodes.
  * Volume name desired is libvirt_images with a subdirectory under each brick directory spread across all gluster nodes.
  ```
   $ gluster volume create libvirt_images replica 3 transport tcp ind-ceph006-sata:/data/glusterfs/myvol1/brick1/images ind-ceph013-sata:/data/glusterfs/myvol1/brick1/images ind-ceph020-sata:/data/glusterfs/myvol1/brick1/images ind-ceph006-sata:/data/glusterfs/myvol1/brick2/images ind-ceph013-sata:/data/glusterfs/myvol1/brick2/images ind-ceph020-sata:/data/glusterfs/myvol1/brick2/images ind-ceph006-sata:/data/glusterfs/myvol1/brick3/images ind-ceph013-sata:/data/glusterfs/myvol1/brick3/images ind-ceph020-sata:/data/glusterfs/myvol1/brick3/images ind-ceph006-sata:/data/glusterfs/myvol1/brick4/images ind-ceph013-sata:/data/glusterfs/myvol1/brick4/images ind-ceph020-sata:/data/glusterfs/myvol1/brick4/images ind-ceph006-sata:/data/glusterfs/myvol1/brick5/images ind-ceph013-sata:/data/glusterfs/myvol1/brick5/images ind-ceph020-sata:/data/glusterfs/myvol1/brick5/images ind-ceph006-sata:/data/glusterfs/myvol1/brick6/images ind-ceph013-sata:/data/glusterfs/myvol1/brick6/images ind-ceph020-sata:/data/glusterfs/myvol1/brick6/images ind-ceph006-sata:/data/glusterfs/myvol1/brick7/images ind-ceph013-sata:/data/glusterfs/myvol1/brick7/images ind-ceph020-sata:/data/glusterfs/myvol1/brick7/images ind-ceph006-sata:/data/glusterfs/myvol1/brick8/images ind-ceph013-sata:/data/glusterfs/myvol1/brick8/images ind-ceph020-sata:/data/glusterfs/myvol1/brick8/images ind-ceph006-sata:/data/glusterfs/myvol1/brick9/images ind-ceph013-sata:/data/glusterfs/myvol1/brick9/images ind-ceph020-sata:/data/glusterfs/myvol1/brick9/images ind-ceph006-sata:/data/glusterfs/myvol1/brick10/images ind-ceph013-sata:/data/glusterfs/myvol1/brick10/images ind-ceph020-sata:/data/glusterfs/myvol1/brick10/images ind-ceph006-sata:/data/glusterfs/myvol1/brick11/images ind-ceph013-sata:/data/glusterfs/myvol1/brick11/images ind-ceph020-sata:/data/glusterfs/myvol1/brick11/images ind-ceph006-sata:/data/glusterfs/myvol1/brick12/images ind-ceph013-sata:/data/glusterfs/myvol1/brick12/images ind-ceph020-sata:/data/glusterfs/myvol1/brick12/images
   ```

   * Here is an example of VOLUME CREATION WITH AN ARBITER. i.e. 2 replicas with a small arbiter to help when there is a network partition
   ```
   $ gluster volume create libvirt_conf replica 3 arbiter 1 transport tcp ind-ceph006-sata:/data/glusterfs/myvol1/brick1/libvirt_conf ind-ceph013-sata:/data/glusterfs/myvol1/brick1/libvirt_conf ind-ceph020-sata:/data/glusterfs/myvol1/brick1/libvirt_conf ind-ceph006-sata:/data/glusterfs/myvol1/brick2/libvirt_conf ind-ceph013-sata:/data/glusterfs/myvol1/brick2/libvirt_conf ind-ceph020-sata:/data/glusterfs/myvol1/brick2/libvirt_conf ind-ceph006-sata:/data/glusterfs/myvol1/brick3/libvirt_conf ind-ceph013-sata:/data/glusterfs/myvol1/brick3/libvirt_conf ind-ceph020-sata:/data/glusterfs/myvol1/brick3/libvirt_conf ind-ceph006-sata:/data/glusterfs/myvol1/brick4/libvirt_conf ind-ceph013-sata:/data/glusterfs/myvol1/brick4/libvirt_conf ind-ceph020-sata:/data/glusterfs/myvol1/brick4/libvirt_conf ind-ceph006-sata:/data/glusterfs/myvol1/brick5/libvirt_conf ind-ceph013-sata:/data/glusterfs/myvol1/brick5/libvirt_conf ind-ceph020-sata:/data/glusterfs/myvol1/brick5/libvirt_conf ind-ceph006-sata:/data/glusterfs/myvol1/brick6/libvirt_conf ind-ceph013-sata:/data/glusterfs/myvol1/brick6/libvirt_conf ind-ceph020-sata:/data/glusterfs/myvol1/brick6/libvirt_conf ind-ceph006-sata:/data/glusterfs/myvol1/brick7/libvirt_conf ind-ceph013-sata:/data/glusterfs/myvol1/brick7/libvirt_conf ind-ceph020-sata:/data/glusterfs/myvol1/brick7/libvirt_conf ind-ceph006-sata:/data/glusterfs/myvol1/brick8/libvirt_conf ind-ceph013-sata:/data/glusterfs/myvol1/brick8/libvirt_conf ind-ceph020-sata:/data/glusterfs/myvol1/brick8/libvirt_conf ind-ceph006-sata:/data/glusterfs/myvol1/brick9/libvirt_conf ind-ceph013-sata:/data/glusterfs/myvol1/brick9/libvirt_conf ind-ceph020-sata:/data/glusterfs/myvol1/brick9/libvirt_conf ind-ceph006-sata:/data/glusterfs/myvol1/brick10/libvirt_conf ind-ceph013-sata:/data/glusterfs/myvol1/brick10/libvirt_conf ind-ceph020-sata:/data/glusterfs/myvol1/brick10/libvirt_conf ind-ceph006-sata:/data/glusterfs/myvol1/brick11/libvirt_conf ind-ceph013-sata:/data/glusterfs/myvol1/brick11/libvirt_conf ind-ceph020-sata:/data/glusterfs/myvol1/brick11/libvirt_conf ind-ceph006-sata:/data/glusterfs/myvol1/brick12/libvirt_conf ind-ceph013-sata:/data/glusterfs/myvol1/brick12/libvirt_conf ind-ceph020-sata:/data/glusterfs/myvol1/brick12/libvirt_conf
   ```
* Start the volume
```$ gluster volume start libvirt_images
```

* Access the volume now in this case i am just locally mounting the volume.
```$ mount -t glusterfs localhost:/libvirt_images /var/lib/libvirt/images
```

* Creating an application data volume with 2 replicas and 1 arbiter.
```
$ gluster volume create efk_data replica 3 arbiter 1 transport tcp ind-ceph006-sata:/data/glusterfs/myvol1/brick1/efkdata_new ind-ceph013-sata:/data/glusterfs/myvol1/brick1/efkdata_new ind-ceph020-sata:/data/glusterfs/myvol1/brick1/efkdata_new ind-ceph006-sata:/data/glusterfs/myvol1/brick2/efkdata_new ind-ceph013-sata:/data/glusterfs/myvol1/brick2/efkdata_new ind-ceph020-sata:/data/glusterfs/myvol1/brick2/efkdata_new ind-ceph006-sata:/data/glusterfs/myvol1/brick3/efkdata_new ind-ceph013-sata:/data/glusterfs/myvol1/brick3/efkdata_new ind-ceph020-sata:/data/glusterfs/myvol1/brick3/efkdata_new ind-ceph006-sata:/data/glusterfs/myvol1/brick4/efkdata_new ind-ceph013-sata:/data/glusterfs/myvol1/brick4/efkdata_new ind-ceph020-sata:/data/glusterfs/myvol1/brick4/efkdata_new ind-ceph006-sata:/data/glusterfs/myvol1/brick5/efkdata_new ind-ceph013-sata:/data/glusterfs/myvol1/brick5/efkdata_new ind-ceph020-sata:/data/glusterfs/myvol1/brick5/efkdata_new ind-ceph006-sata:/data/glusterfs/myvol1/brick6/efkdata_new ind-ceph013-sata:/data/glusterfs/myvol1/brick6/efkdata_new ind-ceph020-sata:/data/glusterfs/myvol1/brick6/efkdata_new ind-ceph006-sata:/data/glusterfs/myvol1/brick7/efkdata_new ind-ceph013-sata:/data/glusterfs/myvol1/brick7/efkdata_new ind-ceph020-sata:/data/glusterfs/myvol1/brick7/efkdata_new ind-ceph006-sata:/data/glusterfs/myvol1/brick8/efkdata_new ind-ceph013-sata:/data/glusterfs/myvol1/brick8/efkdata_new ind-ceph020-sata:/data/glusterfs/myvol1/brick8/efkdata_new ind-ceph006-sata:/data/glusterfs/myvol1/brick9/efkdata_new ind-ceph013-sata:/data/glusterfs/myvol1/brick9/efkdata_new ind-ceph020-sata:/data/glusterfs/myvol1/brick9/efkdata_new ind-ceph006-sata:/data/glusterfs/myvol1/brick10/efkdata_new ind-ceph013-sata:/data/glusterfs/myvol1/brick10/efkdata_new ind-ceph020-sata:/data/glusterfs/myvol1/brick10/efkdata_new ind-ceph006-sata:/data/glusterfs/myvol1/brick11/efkdata_new ind-ceph013-sata:/data/glusterfs/myvol1/brick11/efkdata_new ind-ceph020-sata:/data/glusterfs/myvol1/brick11/efkdata_new ind-ceph006-sata:/data/glusterfs/myvol1/brick12/efkdata_new ind-ceph013-sata:/data/glusterfs/myvol1/brick12/efkdata_new ind-ceph020-sata:/data/glusterfs/myvol1/brick12/efkdata_new
```

* assign permission & adjust privelege  to the qemu-kvm user id so that KVM instances can have access to the storage volume
```
$ gluster volume set efk_data storage.owner-uid 107
$ gluster volume set efk_data storage.owner-gid 107
$ gluster volume set efk_data server.allow-insecure on
$ gluster volume start efk_data
```

* Thereafter create raw img files on top of the gluster volume so that the KVM instance can start using them .
```
$ for i in 1 2 3 4; do qemu-img create gluster://localhost/efk_data/efkdata${i}.img 1T; done
```
Edit the XML file for the domain where you need to expose the raw disk files to the instance. Example as below.
          <disk type='file' device='disk'>
            <driver name='qemu' type='qcow2'/>
            <source file='/var/lib/libvirt/images/atl1-efk03-root.qcow2'/>
            <backingStore/>
            <target dev='vda' bus='virtio'/>
            <alias name='virtio-disk0'/>
            <address type='pci' domain='0x0000' bus='0x00' slot='0x07' function='0x0'/>
          </disk>
          <disk type='network' device='disk'>
            <driver name='qemu' type='raw' cache='none'/>
            <source protocol='gluster' name='efk_data/efkdata1.img'>
              <host name='localhost' port='24007'/>
            </source>
            <backingStore/>
            <target dev='vdb' bus='virtio'/>
            <alias name='virtio-disk1'/>
            <address type='pci' domain='0x0000' bus='0x00' slot='0x09' function='0x0'/>
          </disk>
          <disk type='network' device='disk'>
            <driver name='qemu' type='raw' cache='none'/>
            <source protocol='gluster' name='efk_data/efkdata2.img'>
              <host name='localhost' port='24007'/>
            </source>
            <backingStore/>
            <target dev='vdc' bus='virtio'/>
            <alias name='virtio-disk2'/>
            <address type='pci' domain='0x0000' bus='0x00' slot='0x11' function='0x0'/>
          </disk>
          <disk type='network' device='disk'>
            <driver name='qemu' type='raw' cache='none'/>
            <source protocol='gluster' name='efk_data/efkdata3.img'>
              <host name='localhost' port='24007'/>
            </source>
            <backingStore/>
            <target dev='vdd' bus='virtio'/>
            <alias name='virtio-disk3'/>
            <address type='pci' domain='0x0000' bus='0x00' slot='0x13' function='0x0'/>
          </disk>
          <disk type='network' device='disk'>
            <driver name='qemu' type='raw' cache='none'/>
            <source protocol='gluster' name='efk_data/efkdata4.img'>
              <host name='localhost' port='24007'/>
            </source>
            <backingStore/>
            <target dev='vde' bus='virtio'/>
            <alias name='virtio-disk4'/>
            <address type='pci' domain='0x0000' bus='0x00' slot='0x15' function='0x0'/>
          </disk>
```
* Thereafter to get the best performance from the underlying files sitting on different bricks, setup a striped(RAID0) LVM volume across all of them.
```
RAID LVM
$ pvcreate /dev/vdb1 /dev/vdc1 /dev/vdd1 /dev/vde1
$ vgcreate efkdata /dev/vdb1 /dev/vdc1 /dev/vdd1 /dev/vde1
$ lvcreate -i 4 -l 100%FREE -I 256 -n lv_efkdata efkdata /dev/vdb1 /dev/vdc1 /dev/vdd1 /dev/vde1
```
