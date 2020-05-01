* Check availability of instances on known ports.
```
nmap -P0 -T4 -sT -p22,3389,80,443 -iL /tmp/ips -oG /tmp/out
grep -vE 'open|closed' /tmp/out |grep filtered
```
* Adding a CA cert to your cert store on Ubuntu 18.04
```
Go to /usr/local/share/ca-certificates/
Create a new folder, i.e. "sudo mkdir org"
Copy the .crt file into the org folder
Make sure the permissions are OK (755 for the folder, 644 for the file)
Run "sudo update-ca-certificates"
```
* Attach a sos report to a Redhat Case on cli.
```
export https_proxy=http://ind.proxy.corporate.example.com:80
export http_proxy=http://ind.proxy.corporate.example.com:80
redhat-support-tool addattachment -c 1111111 /var/tmp/sosreport-ind1-cmp001-2019-02-01 rkykqiz.tar.xz
```
* Extending /var Logical Volume with free disk space
  * Create a new partition using parted on disk /dev/sda where free space is available.
  ```
  # parted /dev/sda print free
    Number  Start     End       Size      Type     File system  Flags
              0.03MB    1.05MB    1.02MB             Free Space
      1      1.05MB    1262MB    1261MB    primary  ext4         boot
      2      1262MB    161061MB  159799MB  primary
              161061MB  483184MB  322123MB           Free Space
  ```

  * Create a new primary or secondary partition out of the free space
  ```# mkpart primary 161061MB 483184MB
  ```

  * create a PV and add the PV to the VG and extend the LV using the free space available.
  ```
  # pvcreate /dev/sda3
  # vgextend sysvg /dev/sda3
  # lvextend -l 100%FREE /dev/sysvg/lv_var

  Another command if we have to use extents from another physical disk.
  # lvextend -r /dev/sysvg/lv_var /dev/sdc1
  ```

  * We need to extend /var lv which was xfs filesystem online.
    * First do a dry run with -n option and once satisfied run the actual command without -n switch.
    ```
    # xfs_growfs -n /dev/mapper/sysvg-lv_var
    # xfs_growfs  /dev/mapper/sysvg-lv_var
    ```
* Adding DNS records to IDM01 in bulk.
  ```
  $ while read -r name && read -r ip<&3; do ipa dnsrecord-add mgmt.cloud.example.com $name --a-rec $ip; done <iad-node-names 3<iad-node-ips
  ```

* SAR example
  * display disk stats for 5 samples with interval of 1 second.
  ```# sar -d -p 1 5
  ```

  * Every 2 seconds show device stats and grep for a particular device as the output is refreshed.
  ```
  # sar -n DEV 2 | grep br-ctl
  ```

* AWK tricks
  ```
  # awk here takes out alternate lines from the file and works on it.
  for vol in `awk 'NR % 2 {print}' /tmp/vollist_6`; do openstack server remove volume migration_migrate6 ${vol}; done

  #try following variations of the awk command to print even and odd lines from a file.
  awk 'NR % 2 == 1 {print}' /tmp/vollist
  awk 'NR % 2 == 0 {print}' /tmp/vollist
  ```
* Adding CA Certs on Redhat/CentOS
```
CentOS/Redhat SSL certs
copy your certificates inside
/etc/pki/ca-trust/source/anchors/
then run the following command
# update-ca-trust
# For ubuntu 16.04
; copy your certs here
/usr/local/share/ca-certificates
;then run below cmd
# update-ca-certificates.
```

* Some crontab definitions
  * Crontab that periodically checks that tunnel remains open, if not spawns an SSH tunnel
  ```
  */2 * * * *  bash -c 'ps -ef | grep -v grep | grep "ssh -f -N -R 8000:saga.apps.example.com:443 cloud-ops@10.152.122.6" > /dev/null; if [ $? != 0 ]; then ssh -f -N -R 8000:saga.apps.example.com:443 cloud-ops@10.152.122.6; fi'
  ```

  * Crontab on deploy node to nullify the nohup.out at regular intervals.
  ```
  * */1 * * * bash -c "> /home/cloud-ops/kart/nohup.out"
  ```

* Firewall-cmd usage
  ```
  firewall commands
  firewall-cmd --add-service=http
  firewall-cmd --runtime-to-permanent
  ```
* allow HTTP scripts and modules to connect to network
  ```/usr/sbin/setsebool -P httpd_can_network_connect 1
  ```

* partclone - The utility for clone and restore a partition
  ```
  # partclone.<fstyp> -b -s </lvpath> -o <dstlvpath>
  ```

* SSH-KEYGEN operations.
  * Generate a public key from a pem file.
  ```
  ssh-keygen -yf <path to the pem file> > /tmp/pubout.key
  ```

  * Generate the MD5 fingerprint from the pubkey. Example below.
  ```
  # ssh-keygen -E md5 -lf /tmp/pubout.keygen
  2048 MD5:a9:4c:e3:cb:fa:c0:1c:10:d1:a2:ee:56:05:e9:ae:5e ubuntu@ip-10-227-80-66 (RSA)
  ```

* IDRAC reset from cli
  ```
  # ipmitool mc reset cold
  ```

* Using multiple search string patterns and individually printing different colums for the search. example below.
  ```
  # head -20 /tmp/something.txt
  #!/bin/bash
  # VM
  nova interface-detach 10922c42-cf96-4446-b45b-f6e94a0905e7 008a7bbb-a520-4216-a02c-046cb2ac2623
  nova interface-attach --port-id ad8f9948-df80-47cd-a48f-747762049969 10922c42-cf96-4446-b45b-f6e94a0905e7
  # VM
  nova interface-detach c97f109a-2a18-4967-9589-d08a0323a557 00a85f3b-b13f-4f0e-ab63-bd7ff2f8d304
  nova interface-attach --port-id 18c4502b-b288-4128-9b41-c26f03172dd8 c97f109a-2a18-4967-9589-d08a0323a557
  # VM
  nova interface-detach dee32fd7-45f4-45d1-b896-dfc510f188b4 01101619-af5b-415b-8063-e2090ee1409a
  nova interface-attach --port-id fb1512b5-7d89-4acb-9979-6a07dc6fd999 dee32fd7-45f4-45d1-b896-dfc510f188b4
  # VM
  # nova interface-detach b3aece90-e5f7-4aad-8152-931953a74502 07479d81-7dc6-4544-a00b-d779c2ea9a00
  # nova interface-attach --port-id ff5a5a5c-7e65-470a-8487-386a3b78ea4e b3aece90-e5f7-4aad-8152-931953a74502
  # VM
  nova interface-detach 2113278d-0e80-4b13-8837-4e524d0095ac 088dc014-aa92-4229-b816-5c9014222c9a
  nova interface-attach --port-id 925c0b52-5984-46db-828c-db1da1325c4f 2113278d-0e80-4b13-8837-4e524d0095ac

  # head -20 /tmp/something.txt | grep -v ^# | awk '/detach/ {print $3,$4} /attach/ {print $5,$4}'
  10922c42-cf96-4446-b45b-f6e94a0905e7 008a7bbb-a520-4216-a02c-046cb2ac2623
  10922c42-cf96-4446-b45b-f6e94a0905e7 ad8f9948-df80-47cd-a48f-747762049969
  c97f109a-2a18-4967-9589-d08a0323a557 00a85f3b-b13f-4f0e-ab63-bd7ff2f8d304
  c97f109a-2a18-4967-9589-d08a0323a557 18c4502b-b288-4128-9b41-c26f03172dd8
  dee32fd7-45f4-45d1-b896-dfc510f188b4 01101619-af5b-415b-8063-e2090ee1409a
  dee32fd7-45f4-45d1-b896-dfc510f188b4 fb1512b5-7d89-4acb-9979-6a07dc6fd999
  2113278d-0e80-4b13-8837-4e524d0095ac 088dc014-aa92-4229-b816-5c9014222c9a
  2113278d-0e80-4b13-8837-4e524d0095ac 925c0b52-5984-46db-828c-db1da1325c4f
  62e8cb43-aabf-41dd-bf99-f31f3766cb03 0d8595d7-d06f-4ad7-a7f2-1fc09e19556b

  ```
