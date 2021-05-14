# Objective:
Move the root and boot of a filesystem tree from a disk on XFS filesystem to a
disk on EXT4 filesystem. This was tested on KVM virtual machines running on
CentOS 7.

This basically mirrors the setup at the source and matches that at the target.
You can choose to introduce or adjust the target state of the disk. It will
work. But steps have to be adjusted accordingly using common sense.

# High Level Steps:

Take a note of existing setup and capture the information for reference in case
something breaks while you do it .

* Capture /etc/fstab mount information
* Gather /boot/grub2/grub.cfg and save the information in this file.
* lsblk output as below.
```
[root@atl1-efk02 ~]# lsblk -o NAME,SIZE,FSTYPE,TYPE,MOUNTPOINT,UUID
NAME            SIZE FSTYPE      TYPE MOUNTPOINT UUID
sr0            1024M             rom
vda             100G             disk
├─vda1            1G xfs         part /boot      ad5eb395-fb87-45c8-8ee9-b0bddad8ee10
└─vda2           99G LVM2_member part            9fT3jo-Z872-mn9w-GGJQ-VK75-5FTf-FggYX2
  ├─centos-root
                 50G xfs         lvm  /          1daaddcb-bac5-470c-bee6-dbc1548d2d64
  ├─centos-swap
                 10G swap        lvm  [SWAP]     97db2f71-3e03-4a4a-827d-11cfbf527430
  └─centos-home
                 39G xfs         lvm  /home      c61f16ce-046c-4d2e-8987-e6495a2f23da
vdb             500G             disk
vdc           500.1G ext4        disk /esdata    386bedf4-2469-471e-bbe9-3966fd3bc11d
```

* Having captured all of this information. You will needs a helper CentOS 7 VM
instance, where you are going to attach the source and an empty target disk.
An example command would be like. Adjust arguments as necessary.
```
virt-install --name=test01 --disk path=/var/lib/libvirt/images/test01.qcow2,bus=virtio,size=20 --vcpus=2 --ram=2048 --os-type=Linux --os-variant=rhel7 --location /var/lib/libvirt/images/ISO/CentOS-7-x86_64-Minimal-1804.iso --network bridge=vlan29 --initrd-inject /root/kar/ks.cfg --extra-args="ks=file:/ks.cfg console=tty0 console=ttyS0,115200n8"
```

* Next you need a new disk acting as a target. Here i am using the existing
disk as my reference point and use the same specifications for my target disk.

The first command below dumps xml file for the volume in the default pool, which is in
my case the source disk and redirect it a file , say newvolume.xml
```
virsh vol-dumpxml --pool default atl1-efk02.qcow2 > newvolume.xml
```
Sharing an example output here of an volume xml file definition.
```
<volume type='file'>
  <name>atl1-efk02.qcow2</name>
  <key>/var/lib/libvirt/images/atl1-efk02.qcow2</key>
  <source>
  </source>
  <capacity unit='bytes'>107374182400</capacity>
  <allocation unit='bytes'>64638414848</allocation>
  <physical unit='bytes'>107390894592</physical>
  <target>
<volume type='file'>
    <path>/var/lib/libvirt/images/atl1-efk02.qcow2</path>
    <format type='qcow2'/>
    <permissions>
      <mode>0600</mode>
      <owner>107</owner>
      <group>107</group>
      <label>system_u:object_r:svirt_image_t:s0:c289,c978</label>
    </permissions>
    <timestamps>
      <atime>1606801939.924434686</atime>
      <mtime>1606807037.008476122</mtime>
      <ctime>1606807037.008476122</ctime>
    </timestamps>
    <compat>1.1</compat>
    <features>
      <lazy_refcounts/>
    </features>
  </target>
</volume>
```
* Edit the newvolume.xml and change the term "atl1-efk02" to "atl1-efk02-ext4"
everywhere to produce something like below.
```
<volume type='file'>
  <name>atl1-efk02-ext4.qcow2</name>
  <key>/var/lib/libvirt/images/atl1-efk02-ext4.qcow2</key>
  <source>
  </source>
  <capacity unit='bytes'>107374182400</capacity>
  <allocation unit='bytes'>64638414848</allocation>
  <physical unit='bytes'>107390894592</physical>
  <target>
    <path>/var/lib/libvirt/images/atl1-efk02-ext4.qcow2</path>
    <format type='qcow2'/>
    <permissions>
      <mode>0600</mode>
      <owner>107</owner>
      <group>107</group>
      <label>system_u:object_r:svirt_image_t:s0:c289,c978</label>
    </permissions>
    <timestamps>
      <atime>1606807037.205491595</atime>
      <mtime>1606807068.002910326</mtime>
      <ctime>1606807068.002910326</ctime>
    </timestamps>
    <compat>1.1</compat>
    <features>
      <lazy_refcounts/>
    </features>
  </target>
</volume>
```
* Create the new volume from the XML file.
```
virsh vol-create default newvolume.xml
```
* Bring down the source machine and attach the source and target disks to the
helper instance.

```
# virsh attach-disk test01 /var/lib/libvirt/images/atl1-efk02.qcow2 vdb --driver qemu --subdriver qcow2 --targetbus virtio --persistent

# virsh attach-disk test01 /var/lib/libvirt/images/atl1-efk02-ext4.qcow2 vdc --driver qemu --subdriver qcow2 --targetbus virtio --persistent
```

In my case, post the attachment of disks to the test01 instance, lsblk showed
up something like below.
```
vdb                     100G             disk
├─vdb1                    1G xfs         part            ad5eb395-fb87-45c8-8ee9-b0bddad8ee10
└─vdb2                   99G LVM2_member part            9fT3jo-Z872-mn9w-GGJQ-VK75-5FTf-FggYX2
  ├─centos-swap          10G swap        lvm             97db2f71-3e03-4a4a-827d-11cfbf527430
  ├─centos-home          39G xfs         lvm             c61f16ce-046c-4d2e-8987-e6495a2f23da
  └─centos-root          50G xfs         lvm             1daaddcb-bac5-470c-bee6-dbc1548d2d64
vdc                     100G             disk
```
* I mirrored the setup. so below are the steps.
Use parted and setup the msdos partition table with the partitions and set the
boot flag to the boot partition.

Thereafter create the LVM setup.
```
pvcreate /dev/vdc2
  Physical volume "/dev/vdc2" successfully created.
[root@test01 ~]# vgcreate efk /dev/vdc2
  Volume group "efk" successfully created
[root@test01 ~]# lvcreate -n root -L 50G efk
  Logical volume "root" created.
  [root@test01 ~]# lvdisplay /dev/efk/root
    --- Logical volume ---
    LV Path                /dev/efk/root
    LV Name                root
    VG Name                efk
    LV UUID                wBWINW-qa2j-8imH-u2kB-obrq-5w0c-jti079
    LV Write Access        read/write
    LV Creation host, time test01.mgmt.geix.cloud.ge.com, 2020-12-01 09:23:03 +0000
    LV Status              available
    # open                 0
    LV Size                50.00 GiB
    Current LE             12800
    Segments               1
    Allocation             inherit
    Read ahead sectors     auto
    - currently set to     8192
    Block device           253:5
# lvcreate -n home -l 9983 efk
  Logical volume "home" created.
#lvcreate -n swap -L 10G efk
  Logical volume "swap" created.
```
Time to setup ext4 filesystem on the disk partitions.
```
First the boot partition.
# mkfs.ext4 /dev/vdc1
mke2fs 1.42.9 (28-Dec-2013)
Filesystem label=
OS type: Linux
Block size=4096 (log=2)
Fragment size=4096 (log=2)
Stride=0 blocks, Stripe width=0 blocks
65536 inodes, 262144 blocks
13107 blocks (5.00%) reserved for the super user
First data block=0
Maximum filesystem blocks=268435456
8 block groups
32768 blocks per group, 32768 fragments per group
8192 inodes per group
Superblock backups stored on blocks:
	32768, 98304, 163840, 229376

Allocating group tables: done
Writing inode tables: done
Creating journal (8192 blocks): done
Writing superblocks and filesystem accounting information: done

Same for the the remaining
# mkfs.ext4 /dev/efk/root
# mkfs.ext4 /dev/efk/home
# mkswap /dev/efk/swap
```

*Create a few directories for mounting the disk filesystem from the source and
target disks.
```
# mkdir /{oldroot,oldboot,oldhome,newroot,newboot,newhome}

# mount /dev/vdb1 /oldboot/ && mount /dev/centos/root /oldroot && mount /dev/centos/home /oldhome

# mount /dev/vdc1 /newboot/ && mount /dev/efk/root /newroot && mount /dev/efk/home /newhome
```

* Copy data at the Fileystem level using rsync.
```
# rsync -avz -A -X /oldboot/ /newboot/
# rsync -avz -A -X /oldroot/ /newroot/
# rsync -avz -A -X /oldhome /newhome/
```
* Umount the source disk.
```
# umount /oldroot/ /oldboot/ /oldhome/
```
* Remount the new boot partition & home LV inside /newroot
```
mount /dev/vdc1 /newroot/boot
mount /dev/efk/home /newroot/home
```
* Change root to newroot
```
chroot /newroot/
```
* Next edit /etc/fstab to boot off the new disk partition and LVs

* Next, mount a few other filesystems inside newroot.
```
for i in dev proc sys tmp ; do mount -o bind /${i} /newroot/${i}; done
```

* Time to regenerate grub2 config file
```
grub2-mkconfig -o /boot/grub2/grub.cfg
```

* You will have to edit the above grub.cfg and correct references to the LVs.
Make sure 2 occurrences of the linux16 line in the file has the correct
reference to the vg/lv name, in this case, rd.lvm.lv was incorrect and it had to
be adjusted. SO make sure you edit and set the correct vg/lv names.
```
linux16 /vmlinuz-3.10.0-862.el7.x86_64 root=/dev/mapper/efk-root ro crashkernel=auto rd.lvm.lv=efk/root rd.lvm.lv=efk/swap rhgb quiet
linux16 /vmlinuz-0-rescue-3aadc44dc7ad439c920e792b5eb80926 root=/dev/mapper/efk-root ro crashkernel=auto rd.lvm.lv=efk/root rd.lvm.lv=efk/swap rhgb quiet
```
Thereafter you may also choose to remove some unncessary lines that get added
between these 2 commented lines below. You can choose to simply get rid of them.
```
### BEGIN /etc/grub.d/30_os-prober ###
### END /etc/grub.d/30_os-prober ###
```

* Generate initrd again.
```
# dracut --print-cmdline
rd.lvm.lv=efk/root
root=/dev/mapper/efk-root rootflags=rw,relatime,seclabel,data=ordered rootfstype=ext4

# dracut -f
Make sure it remains the same after running dracut.

# dracut --print-cmdline
rd.lvm.lv=efk/root
root=/dev/mapper/efk-root rootflags=rw,relatime,seclabel,data=ordered rootfstype=ext4
```
* Run the grub2-install on the device.
```
# grub2-install /dev/vdc
```

* Time to unwind. Unmount all FS
```
Get out of chroot using ctrl+d

# for i in dev proc sys tmp; do umount /newroot/${i}; done
# umount /newroot/boot && /newroot/home/ && unmount /newroot
```

* Detach disks from the test01 (helper) instances
```
virsh detach-disk test01 vdb --persistent
virsh detach-disk test01 vdc --persistent
```

* Edit the xml file to change the reference of the disk file mapped to vda and
refer to the new target disk file.
```
<disk type='file' device='disk'>
  <driver name='qemu' type='qcow2'/>
  <source file='/var/lib/libvirt/images/atl1-efk02-ext4.qcow2'/>
  <backingStore/>
  <target dev='vda' bus='virtio'/>
  <alias name='virtio-disk0'/>
  <address type='pci' domain='0x0000' bus='0x00' slot='0x07' function='0x0'/>
</disk>
```

* Boot the instance and Voila, everything should come up fine.
Typos in the /etc/fstab or missing edits like forgetting on one line to say ext4
instead of XFS can land you into trouble.
