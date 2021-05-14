#!/usr/bin/env bash

set -o errexit

container=$(buildah from ubuntu:18.04)
mountpoint=$(buildah mount $container)

chroot ${mountpoint} bash -c "mkdir /usr/src/example"
wget --no-proxy -P ${mountpoint}/usr/src/example http://atl1-satellite.mgmt.example.cloud.Example.com/pulp/isos/example/Library/custom/automation/example-packages/example_automation-example-common-0.1.12.tar.gz
# curl http://atl1-satellite.mgmt.example.cloud.example.com/pulp/isos/example/Library/custom/automation/example-packages/example_automation-example-common-0.1.12.tar.gz \
# | tar -xzC ${mountpoint}/usr/src/example
chroot ${mountpoint} bash -c "cd /usr/src/example && tar -xzf example_automation-example-common-0.1.12.tar.gz"
wget -P ${mountpoint}/usr/local/share/ca-certificates/ https://static.examplecirtnotification.com/browser_remediation/packages/example_External_Root_CA_2_1.crt
unset no_proxy NO_PROXY
wget -P ${mountpoint}/tmp https://github.com/Yelp/dumb-init/releases/download/v1.2.2/dumb-init_1.2.2_amd64.deb

buildah config --env DEBIAN_FRONTEND=noninteractive ${container}
buildah run $container bash -c "apt-get update && apt-get install -y \
 ca-certificates python3-pip && update-ca-certificates \
 && pip3 install influxdb \
 && dpkg -i /tmp/dumb-init_*.deb \
 && rm -f /tmp/dumb-init_*.deb \
 && cd /usr/src/example/example_automation-example-common-0.1.12/example_common \
 && python3 setup.py install \
 && rm -rf /var/lib/apt/lists/* \
 && rm -fr /usr/src/example/example_automation-example-common-0.1.12*"
buildah copy ${container} /usr/lib/python2.7/dist-packages/certifi/cacert.pem /usr/local/lib/python3.6/dist-packages/certifi/cacert.pem
buildah copy ${container} /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
buildah config --entrypoint '["dumb-init","--single-child","--"]' $container
buildah config --cmd "tail -f /dev/null" $container
buildah commit $container example-automation-base:2.0
