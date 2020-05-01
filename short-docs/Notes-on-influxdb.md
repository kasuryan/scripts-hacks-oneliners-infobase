# Main keywords to be known in influx
* Line protocol : text based format for writing data points.
  * measuremen,tag_set1,tag_set2 field_set,field1_set,field2_set timestamp
* measurement : It holds the data (Like table in Sql)
*	tag set (key=value): tags are added to data to filter. (It’s optional)
*	field (key=value) :  it’s the field in data struct which holds the value in the series.
*	Timestamp : data point in nanoseconds UTC. (it’s optional) .
*	Retention policy (RP): This decides on how the data is stored for each measurement.
	* Duration : how long db stores data
  *	replication (N): n of copies across Cluster
	* Shard : compressed data in TSM format
  *	Shrad Group : group of shard organized by time.
*	DB port : 8086
*	DB backup port : 8088

# Query :
* CLI
*	HTTP Methods

# DB Management:
* Influxdb files : /var/lib/influxdb
* Log file :  /var/log/influxdb or /var/log/syslog

* Every measurement can have different retention policies.
```
#> show retention policies

Show shards to view the retention policies and measurement details
#> show shards
Create Retention Policy
#> create retention policy "nova_server_diagnostics" on "kart" duration 2160h replication 1 shard duration 24h
```

# Some more CLI
```
#> show measurements
#> show measurements with measurement =~ /^kart*/
#> show series from <measurement>
#> show tag keys from announcements
#> show field keys from announcements
#> show field keys from nova_server_diagnostics.ret_test
name: ret_test
fieldKey fieldType
-------- ---------
game     string
name     string
value    float
