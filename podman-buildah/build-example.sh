#!/usr/bin/env bash

set -o errexit

container=$(buildah from ubuntu:18.04)
mountpoint=$(buildah mount $container)

wget -P ${mountpoint}/tmp https://github.com/Yelp/dumb-init/releases/download/v1.2.2/dumb-init_1.2.2_amd64.deb
chroot ${mountpoint} bash -c "mkdir /usr/src/example"
curl http://atl1-satellite.mgmt.example.cloud.ge.com/pulp/isos/example/Library/custom/automation/example-packages/example_automation-example-common-0.1.10.tar.gz \
| tar -xzC ${mountpoint}/usr/src/example

buildah copy ${container} /usr/lib/python2.7/dist-packages/certifi/cacert.pem /usr/local/lib/python2.7/dist-packages/certifi/cacert.pem
buildah copy ${container} /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
buildah config --env DEBIAN_FRONTEND=noninteractive ${container}
buildah run $container bash -c "apt-get update && apt-get install -y \
  python-pip \
  && pip install python-glanceclient==2.16.0 python-neutronclient==6.12.0 \
  python-novaclient==16.0.0 python-cinderclient==6.0.0 \
  pyrsistent==0.15.0 stevedore==1.27.0 influxdb==5.3.0 openstacksdk==0.45.0 \
  python-openstackclient==5.2.1\
  && rm -rf /var/lib/apt/lists/* \
  && dpkg -i /tmp/dumb-init_*.deb \
  && rm -f /tmp/dumb-init_*.deb \
  && cd /usr/src/example/example_automation-example-common-0.1.10/example_common \
  && python setup.py install \
  && rm -fr /usr/src/example/example_automation-example-common-0.1.10"
buildah config --entrypoint '["dumb-init","--single-child","--"]' $container
buildah config --cmd "tail -f /dev/null" $container
buildah commit $container example-automation-base:1.2
