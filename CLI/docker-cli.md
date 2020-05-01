* Adding proxy to docker environment:
```
#mkdir /etc/systemd/system/docker.service.d

Now create a file called /etc/systemd/system/docker.service.d/http-proxy.conf that adds the HTTP_PROXY environment variable:

[Service]
Environment="HTTP_PROXY=http://proxy.example.com:80"
Environment="HTTPS_PROXY=http://proxy.example.com:80"

If you have internal Docker registries that you need to contact without proxying you can specify them via the NO_PROXY environment variable:

Environment="HTTP_PROXY=http://proxy.example.com:80/"
Environment="NO_PROXY=localhost,127.0.0.0/8,docker-registry.somecorporation.com

Get the changes in and validate.
$ sudo systemctl daemon-reload
$ sudo systemctl restart docker
$ sudo systemctl show --property Environment docker
Environment=HTTP_PROXY=http://proxy.example.com:80/
```

* Check the catalog on a remote private registry
```curl -k -v --noproxy <IP or FQDN> -X GET https://<IP or FQDN>:5000/v2/_catalog
```
* Login to docker hub
```$sudo docker login -u <user> -p <pass>
```
* Pulling a specific version with the version tag under grafana
```$sudo docker pull grafana/grafana:4.5.2
```
* Run 2 containers on the same port but exposed on different ports via the host.
$sudo docker run -d --name=grafana -p 3000:3000 grafana/grafana
$sudo docker run -d --name=grafana_452 -p 3010:3000 grafana/grafana:4.5.2
* Picking on a specific attribute from the container.
```
docker inspect -f {{.GraphDriver.Data.DeviceName}} 19de0d06a506
docker-253:2-269058711-b8cbe8b322e2d5fee4e082cfe1a92be758a47ba988bb18891a6645a2337840f4
```
* Making Changes to an image , commit and save it locally.
```
docker commit -a "Kartik" -m "installed elasticsearch with proxy and cert set" efk_compose_fluentd_1 fluent_elastic
```
