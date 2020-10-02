# Just saving some ansible one liners

  * Just let me know if a service is running or not without the multi line
  details of the service.
  ```  
  # ansible -i inv prod -m shell -a  "hostname; pgrep td-agent-bit > /dev/null ; if [ \$? != 0 ]; then echo \"Starting service\"; systemctl start td-agent-bit; fi"
  ```
  * Say you would like to override a variable that is a list of dictionaries on the fly with the ansible-playbook cli, here is how. I am overriding a file_vars which is of the type list and each element of that list is a map/dictionary (key: values). 
  On top of that i am skipping some tasks using tags.
  ```
  ansible-playbook -i $inv logrotate.yml -e file_vars='[{"name":"syslog"}]' --skip-tags move_logrotate_cron -u root
  ```

  * Example of a copy module use on the cli, could be applied on any other
  module too.
  ```
  # ansible -i inv_mgmt kart-10.0.0.49 -m copy -a "src=/root/efk/compute/ dest=/etc/td-agent-bit mode=0644"
  # ansible -i inv cmp-prod -m copy -a "src=/tmp/efk/compute/ dest=/etc/td-agent-bit/ mode=0644"
  ```

  * Just an example of firewall acl addition to a bunch of nodes using ansible cli.
  ```
  # ansible -i inv prod -m shell -a "firewall-cmd --add-port=9100/tcp --zone=public --permanent; firewall-cmd --reload"
  ```

  * Using regular expressions on your target node names with ansible cli tool.
  The critical part of the is the **~"kart-10.0.0.10[0-3]$"** which identifies your regex.
  ```
  # ansible i inv ~"kart-10.0.0.10[0-3]$" -m shell -a "hostname; systemctl start td-agent-bit"
  ```

  * Escaping some characters when using shell module of ansible.
  ```
  # ansible -i inv kart-10.0.0.93 -m shell -a "for s in \`systemctl -t service | grep ceph | awk '{print \$1}'\`; do systemctl restart \$s; done "

  # ansible -i inv ceph -m shell -a "for dev in p4p1 p4p2 p8p1 p8p2 ; do ip l show \$dev; done" -b
  ```

  * Target a particular subgroup of a grouping within ansible inventory.
  ```
  # for n in `ansible -i inv ceph-prod --list-hosts | grep kart` ;
  do ansible -i inv $n -m shell -a "for c in \`docker ps -q\`; do docker restart \$c; sleep 10; done ";
  done

  Another example, pick & apply on a subgroup from a grouping named "osds"
  # ansible -i hosts.inventory osds -l "`echo kart-ceph00{1..3}-ssd`" -m shell -a \
  "systemctl -t service -l | grep ceph-osd | awk '{print \$1}' | xargs systemctl restart "
  ```

  * Running a stress-ng of a bunch of fresh hardware.
  ```
  ansible -i inv -m shell -a "stress-ng --cpu 0 --cpu-method all -t 1h; stress-ng --vm 8 --vm-bytes 80% -t 1h" rack1 -f 20
  ```
  * Using a BASH variable with ansible.
  ```
  # cat /tmp/kart | while read snap vol; do ansible -i hosts cinder01 -s -m shell -a "rbd -n client.cinder snap ls -p volumes-sata volume-$vol | grep $snap"; done
  ```
