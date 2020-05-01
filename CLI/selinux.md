* Checking the SElinux users.
```# semanage login -l
Login Name           SELinux User         MLS/MCS Range        Service

__default__          unconfined_u         s0-s0:c0.c1023       *
root                 unconfined_u         s0-s0:c0.c1023       *
system_u             system_u             s0-s0:c0.c1023       *
```
* Checking the sestatus
```
# sestatus
SELinux status:                 enabled
SELinuxfs mount:                /sys/fs/selinux
SELinux root directory:         /etc/selinux
Loaded policy name:             targeted
Current mode:                   enforcing
Mode from config file:          enforcing
Policy MLS status:              enabled
Policy deny_unknown status:     allowed
Max kernel policy version:      31
```

* Checking the roles within selinux. you will need to install (yum install -y setools-console)
```
# seinfo -r

Roles: 14
   auditadm_r
   dbadm_r
   guest_r
   staff_r
   user_r
   logadm_r
   object_r
   secadm_r
   sysadm_r
   system_r
   webadm_r
   xguest_r
   nx_server_r
   unconfined_r

# semanage boolean -l
SELinux boolean                State  Default Description

privoxy_connect_any            (on   ,   on)  Allow privoxy to connect any
smartmon_3ware                 (off  ,  off)  Allow smartmon to 3ware
mpd_enable_homedirs            (off  ,  off)  Allow mpd to enable homedirs
xdm_sysadm_login               (off  ,  off)  Allow xdm to sysadm login
xen_use_nfs                    (off  ,  off)  Allow xen to use nfs
mozilla_read_content           (off  ,  off)  Allow mozilla to read content
ssh_chroot_rw_homedirs         (off  ,  off)  Allow ssh to chroot rw homedirs
mount_anyfile                  (on   ,   on)  Allow mount to anyfile
cron_userdomain_transition     (on   ,   on)  Allow cron to userdomain transition
xdm_write_home                 (off  ,  off)  Allow xdm to write home
openvpn_can_network_connect    (on   ,   on)  Allow openvpn to can network connect
xserver_execmem                (off  ,  off)  Allow xserver to execmem
minidlna_read_generic_user_content (off  ,  off)  Allow minidlna to read generic user content
authlogin_nsswitch_use_ldap    (off  ,  off)  Allow authlogin to nsswitch use ldap
gluster_anon_write             (off  ,  off)  Allow g

..... <Trimmed output>
```

* Changing the selinux context on a file using chcon.
```
# chcon -u system_u -t svirt_image_t new/261c4428-ec5a-4c00-9820-5bab95ddaa99_80
# ls -lZ new/261c4428-ec5a-4c00-9820-5bab95ddaa99_80
-rw-r--r--. qemu qemu system_u:object_r:svirt_image_t:s0 new/261c4428-ec5a-4c00-9820 5bab95ddaa99_80
```
  * Another example:
  ```
  # chcon -u system_u -t svirt_image_t -l s0:c247,c696 /var/kart/new/261c4428-ec5a-4c00-9820-5bab95ddaa99_80
  # ls -Z /var/lib/libvirt/images/261c4428-ec5a-4c00-9820-5bab95ddaa99_80
  -rw-r--r--. qemu qemu system_u:object_r:svirt_image_t:s0:c247,c696 /var/lib/libvirt/images/261c4428-ec5a-4c00-9820-5bab95ddaa99_80
  ```
