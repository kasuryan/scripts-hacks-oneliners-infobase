* Testing data points for last 10 mins with curl.
```
curl -k 'https://myapp.example.com/influxdb/query' --data-urlencode 'db=gems' --data-urlencode "q=SELECT "value" FROM "ssh_checks" WHERE ("host" =~ /compute125/) AND time > now() - 10m " | python -m json.tool
```
* Influx CLI access
```
influx -host <IP or FQDN> -port 8086 -username user -password 'PASS' -precision rfc3339
```
* using regex and multiple conditions to pull data
```
> select * from "rpc_maas"."maas_disk_utilisation" where host =~ /compute029/ and time > now() - 5m
```
* see retention policies.
```
> show retention policies
```
* see fields and tags set on a measurement.
```
> show field keys from <measurement name>
> show tag keys from <measureent name>
> select *::field from maas_glance limit 1
```
* USING DERIVATIVE to get the data rate i.e data xmit & recv per hour.
```
> SELECT derivative(first(bytes_recv), 1m) as "download bytes/sec", derivative(first(bytes_sent), 1m) as "upload bytes/sec" FROM net WHERE time > now() - 1h AND interface =~ /bond0.103/ and host =~ /compute017/ group by time(10m) fill(0)

Another one
> select non_negative_derivative("bytes_recv", 1m) from rpc_maas.net WHERE $timeFilter AND interface =~ /bond0.103/ and host =~ /compute\d/ group by host, time($__interval) fill(0)
```
* see the last 5 values for each host, grouped by host.
```select * from rpc_maas.mem group by host order by desc limit 5
```
* specifying time as a filter along with other tags.
```
> select * from cpu where time > '2018-05-03T03:50:05Z' and host='813116-compute014' and cpu='cpu1'
```
* Example to see what tags and fields are part of a measurement.
```
> show tag keys from cpu
name: cpu
tagKey
------
cpu
host
job_reference
node_type
> show field keys from cpu
name: cpu
fieldKey         fieldType
--------         ---------
usage_guest      float
usage_guest_nice float
usage_idle       float
usage_iowait     float
usage_irq        float
usage_nice       float
usage_softirq    float
usage_steal      float
usage_system     float
usage_user       float
```
* list values from last 5 minutes matching the where clause.
```
select * from rpc_maas.diskio where host='813302-compute101' and time > now() - 5m and "name" =~ /sda/
```

* Some other queries
```
SELECT derivative(last("io_time"),1ms) FROM "rpc_maas"."diskio" WHERE time > now() - 1h and host='813302-compute101' and "name" =~ /sda$/ group by "host","name",time(1m)

select mean(disk_avg) from ( select (disk_utilisation_sdb+disk_utilisation_sdc+disk_utilisation_sdd+disk_utilisation_sde+disk_utilisation_sdf+disk_utilisation_sdg+disk_utilisation_sdh+disk_utilisation_sdi+disk_utilisation_sdj+disk_utilisation_sdk+disk_utilisation_sdl+disk_utilisation_sdm+disk_utilisation_sdn)/12 as disk_avg from "rpc_maas"."maas_disk_utilisation" fill(0) ) WHERE "host" =~ /ceph(2[2-9]|[34][0-9])/ and time > now() - 5m group by time(1m), host
```
