#!/usr/bin/env bash

set -o errexit

container=$(buildah from 10.153.29.26:5000/exampleix-automation-base)
mountpoint=$(buildah mount ${container})
wget -P ${mountpoint}/tmp https://github.com/Yelp/dumb-init/releases/download/v1.2.2/dumb-init_1.2.2_amd64.deb
buildah copy ${container} /opt/klaus /opt/klaus
buildah copy ${container} /opt/klaus/local/lib/python2.7/site-packages/certifi/cacert.pem \
/opt/klaus/local/lib/python2.7/site-packages/certifi/cacert.pem
buildah copy ${container} /etc/ssl/certs/ca-certificates.crt \
/etc/ssl/certs/ca-certificates.crt
buildah config --env \
REQUESTS_CA_BUNDLE=/opt/klaus/local/lib/python2.7/site-packages/certifi/cacert.pem \
--env WEBSOCKET_CLIENT_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
--env PYTHONPATH=/opt/klaus/etc \
${container}
buildah run ${container} bash -c "mkdir -p /var/log/klaus \
  && dpkg -i /tmp/dumb-init_*.deb \
  && rm -f /tmp/dumb-init_*.deb"
buildah config --entrypoint '["dumb-init","--single-child","--"]' ${container}
buildah config --cmd '/opt/klaus/bin/run_klaus --config-file /opt/klaus/etc/klaus.conf --logfile /var/log/klaus/klaus.log' ${container}
buildah commit ${container} klausbot
