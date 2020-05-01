```
container=$(buildah from ubuntu:18.04)
```
* Quick ability to start editing your image there and then.
```
# buildah run $container bash
```
* DO your thing and quick commit.
```buildah commit $container new-image
```
* I dont have a registry to push images. No problems, just install an rpm and
voila you have a docker registry running locally.
```
# yum install -y docker-distribution
# systemctl start docker-distribution
# systemctl enable docker-distibution
```
* Edit the /etc/docker-distribution/registry/config.yml to use the IP you want, by default runs on localhost.
Put in your instance IP for it be accessible from outside.
```
http:
  addr: 192.168.1.6:5000
```
* Test access to your insecure registry.
```
curl http://192.168.1.6:5000/v2/_catalog
To avoid using proxy, set the no_proxy variable in the shell.
```
* Pushing images from localhost to a registry.
```
# buildah push --tls-verify=false localhost/automation-base:latest localhost:5000/automation-base:latest
```
* Pulling images from insecure registry which is locally hosted.
Buildah pull from insecure registry example
```
# buildah pull --tls-verify=false 10.0.0.1:5000/automation-base
```
* Inspect images that you have built. Check the layers, labels, CMD, RUN arguments etc.
```buildah inspect --type image ubuntu:18.04
```
* Building an image with tag kart-test based on a Dockerfile sitting in the current directory.
```
buildah bud -t kart-test
Another example of passiable variable
# buildah bud --build-arg var=noninteractive -t automation-base .
```
