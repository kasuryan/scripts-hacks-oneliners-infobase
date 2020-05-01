# Openstack Neutron LBaaSv1 and LBaasS v2 cli usage
```
# neutron lbaas-loadbalancer-create --name kart-lb TENANTSUBNET-IND-Sandbox-Internal
    Created a new loadbalancer:
    +---------------------+--------------------------------------+
    | Field               | Value                                |
    +---------------------+--------------------------------------+
    | admin_state_up      | True                                 |
    | description         |                                      |
    | id                  | 9c26c73a-f13e-45e2-8795-0812b4eaf4fa |
    | listeners           |                                      |
    | name                | kart-lb                              |
    | operating_status    | OFFLINE                              |
    | pools               |                                      |
    | provider            | haproxy                              |
    | provisioning_status | PENDING_CREATE                       |
    | tenant_id           | feacaa2326204509bd19e395917b47d6     |
    | vip_address         | 10.152.124.73                        |
    | vip_port_id         | 3d3509c6-a57f-47b0-beee-87dfbf3db2de |
    | vip_subnet_id       | 0dc68c76-4cf2-4952-90a5-de9206fb0246 |
    +---------------------+--------------------------------------+

# neutron security-group-create kart-lb-sg
# neutron security-group-show kart-lb-sg -f yaml
    neutron CLI is deprecated and will be removed in the future. Use openstack CLI instead.
    created_at: '2019-09-27T06:11:04Z'
    description: ''
    id: b22f2edb-dd4e-4840-bb27-73366bccd548
    name: kart-lb-sg
    project_id: feacaa2326204509bd19e395917b47d6
    revision_number: 1
    security_group_rules:
    - created_at: '2019-09-27T06:11:04Z'
      description: null
      direction: egress
      ethertype: IPv4
      id: 47347003-7fca-40d2-b494-eded692d85c6
      port_range_max: null
      port_range_min: null
      project_id: feacaa2326204509bd19e395917b47d6
      protocol: null
      remote_group_id: null
      remote_ip_prefix: null
      revision_number: 1
      security_group_id: b22f2edb-dd4e-4840-bb27-73366bccd548
      tenant_id: feacaa2326204509bd19e395917b47d6
      updated_at: '2019-09-27T06:11:04Z'
    - created_at: '2019-09-27T06:11:04Z'
      description: null
      direction: egress
      ethertype: IPv6
      id: 824c20f3-bcd2-42f9-ad50-2244b1885905
      port_range_max: null
      port_range_min: null
      project_id: feacaa2326204509bd19e395917b47d6
      protocol: null
      remote_group_id: null
      remote_ip_prefix: null
      revision_number: 1
      security_group_id: b22f2edb-dd4e-4840-bb27-73366bccd548
      tenant_id: feacaa2326204509bd19e395917b47d6
      updated_at: '2019-09-27T06:11:04Z'
    tenant_id: feacaa2326204509bd19e395917b47d6
    updated_at: '2019-09-27T06:11:04Z'

# neutron security-group-rule-create \
    > --direction ingress --protocol tcp \
    > --port-range-min 80 --port-range-max 80 \
    > --remote-ip-prefix 0.0.0.0/0 \
    > kart-lb-sg
    neutron CLI is deprecated and will be removed in the future. Use openstack CLI instead.
    Created a new security_group_rule:
    +-------------------+--------------------------------------+
    | Field             | Value                                |
    +-------------------+--------------------------------------+
    | created_at        | 2019-09-27T06:16:29Z                 |
    | description       |                                      |
    | direction         | ingress                              |
    | ethertype         | IPv4                                 |
    | id                | f05957c3-6ef3-43c9-8516-4a628e374019 |
    | port_range_max    | 80                                   |
    | port_range_min    | 80                                   |
    | project_id        | feacaa2326204509bd19e395917b47d6     |
    | protocol          | tcp                                  |
    | remote_group_id   |                                      |
    | remote_ip_prefix  | 0.0.0.0/0                            |
    | revision_number   | 1                                    |
    | security_group_id | b22f2edb-dd4e-4840-bb27-73366bccd548 |
    | tenant_id         | feacaa2326204509bd19e395917b47d6     |
    | updated_at        | 2019-09-27T06:16:29Z                 |
    +-------------------+--------------------------------------+

    # neutron security-group-rule-create \
    --direction ingress --protocol tcp \
    --port-range-min 443 --port-range-max 443 \
    --remote-ip-prefix 0.0.0.0/0 \
    kart-lb-sg

# neutron CLI is deprecated and will be removed in the future. Use openstack CLI instead.
    Created a new security_group_rule:
    +-------------------+--------------------------------------+
    | Field             | Value                                |
    +-------------------+--------------------------------------+
    | created_at        | 2019-09-27T06:18:10Z                 |
    | description       |                                      |
    | direction         | ingress                              |
    | ethertype         | IPv4                                 |
    | id                | af5881ee-5039-431a-b9d2-d78664879424 |
    | port_range_max    | 443                                  |
    | port_range_min    | 443                                  |
    | project_id        | feacaa2326204509bd19e395917b47d6     |
    | protocol          | tcp                                  |
    | remote_group_id   |                                      |
    | remote_ip_prefix  | 0.0.0.0/0                            |
    | revision_number   | 1                                    |
    | security_group_id | b22f2edb-dd4e-4840-bb27-73366bccd548 |
    | tenant_id         | feacaa2326204509bd19e395917b47d6     |
    | updated_at        | 2019-09-27T06:18:10Z                 |
    +-------------------+--------------------------------------+

# neutron lbaas-listener-create --name kart-lb-http \
  --loadbalancer kart-lb \
  --protocol HTTP --protocol-port 80
    neutron CLI is deprecated and will be removed in the future. Use openstack CLI instead.
    Created a new listener:
    +---------------------------+------------------------------------------------+
    | Field                     | Value                                          |
    +---------------------------+------------------------------------------------+
    | admin_state_up            | True                                           |
    | connection_limit          | -1                                             |
    | default_pool_id           |                                                |
    | default_tls_container_ref |                                                |
    | description               |                                                |
    | id                        | 1ffddc08-8dfb-4a2b-93c0-7b896eb0c934           |
    | loadbalancers             | {"id": "9c26c73a-f13e-45e2-8795-0812b4eaf4fa"} |
    | name                      | kart-lb-http                                   |
    | protocol                  | HTTP                                           |
    | protocol_port             | 80                                             |
    | sni_container_refs        |                                                |
    | tenant_id                 | feacaa2326204509bd19e395917b47d6               |
    +---------------------------+------------------------------------------------+

# neutron lbaas-listener-create \
    --name kart-lb-https \
    --loadbalancer kart-lb \
    --protocol HTTPS \
    --protocol-port 443
    neutron CLI is deprecated and will be removed in the future. Use openstack CLI instead.
    Created a new listener:
    +---------------------------+------------------------------------------------+
    | Field                     | Value                                          |
    +---------------------------+------------------------------------------------+
    | admin_state_up            | True                                           |
    | connection_limit          | -1                                             |
    | default_pool_id           |                                                |
    | default_tls_container_ref |                                                |
    | description               |                                                |
    | id                        | d83c7e89-89f5-4fb0-8f24-3ce28ebb8851           |
    | loadbalancers             | {"id": "9c26c73a-f13e-45e2-8795-0812b4eaf4fa"} |
    | name                      | kart-lb-https                                  |
    | protocol                  | HTTPS                                          |
    | protocol_port             | 443                                            |
    | sni_container_refs        |                                                |
    | tenant_id                 | feacaa2326204509bd19e395917b47d6               |
    +---------------------------+------------------------------------------------+

# neutron lbaas-pool-create \
    --name kart-lb-pool-http \
    --lb-algorithm ROUND_ROBIN \
    --listener kart-lb-http \
    --protocol HTTP
    neutron CLI is deprecated and will be removed in the future. Use openstack CLI instead.
    Created a new pool:
    +---------------------+------------------------------------------------+
    | Field               | Value                                          |
    +---------------------+------------------------------------------------+
    | admin_state_up      | True                                           |
    | description         |                                                |
    | healthmonitor_id    |                                                |
    | id                  | 7f49bcf4-5773-4e50-94b3-fdd96d4fb917           |
    | lb_algorithm        | ROUND_ROBIN                                    |
    | listeners           | {"id": "1ffddc08-8dfb-4a2b-93c0-7b896eb0c934"} |
    | loadbalancers       | {"id": "9c26c73a-f13e-45e2-8795-0812b4eaf4fa"} |
    | members             |                                                |
    | name                | kart-lb-pool-http                              |
    | protocol            | HTTP                                           |
    | session_persistence |                                                |
    | tenant_id           | feacaa2326204509bd19e395917b47d6               |
    +---------------------+------------------------------------------------+

# neutron lbaas-pool-create \
    > --name kart-lb-pool-https \
    > --lb-algorithm ROUND_ROBIN \
    > --listener kart-lb-https \
    > --protocol HTTPS
    neutron CLI is deprecated and will be removed in the future. Use openstack CLI instead.
    Created a new pool:
    +---------------------+------------------------------------------------+
    | Field               | Value                                          |
    +---------------------+------------------------------------------------+
    | admin_state_up      | True                                           |
    | description         |                                                |
    | healthmonitor_id    |                                                |
    | id                  | d3ad3fdf-3317-45b4-a3ef-86f33e1177e8           |
    | lb_algorithm        | ROUND_ROBIN                                    |
    | listeners           | {"id": "d83c7e89-89f5-4fb0-8f24-3ce28ebb8851"} |
    | loadbalancers       | {"id": "9c26c73a-f13e-45e2-8795-0812b4eaf4fa"} |
    | members             |                                                |
    | name                | kart-lb-pool-https                             |
    | protocol            | HTTPS                                          |
    | session_persistence |                                                |
    | tenant_id           | feacaa2326204509bd19e395917b47d6               |
    +---------------------+------------------------------------------------+

# neutron lbaas-member-create \
    > --subnet 0dc68c76-4cf2-4952-90a5-de9206fb0246 \
    > --address 10.152.124.41 \
    > --protocol-port 80 \
    > kart-lb-pool-http
    neutron CLI is deprecated and will be removed in the future. Use openstack CLI instead.
    Created a new member:
    +----------------+--------------------------------------+
    | Field          | Value                                |
    +----------------+--------------------------------------+
    | address        | 10.152.124.41                        |
    | admin_state_up | True                                 |
    | id             | be66a60b-f224-4cd9-80f9-b0ce203eef48 |
    | name           |                                      |
    | protocol_port  | 80                                   |
    | subnet_id      | 0dc68c76-4cf2-4952-90a5-de9206fb0246 |
    | tenant_id      | feacaa2326204509bd19e395917b47d6     |
    | weight         | 1                                    |
    +----------------+--------------------------------------+

# neutron lbaas-member-create --subnet 0dc68c76-4cf2-4952-90a5-de9206fb0246 \
  --address 10.152.124.41 --protocol-port 443 kart-lb-pool-https
    neutron CLI is deprecated and will be removed in the future. Use openstack CLI instead.
    Created a new member:
    +----------------+--------------------------------------+
    | Field          | Value                                |
    +----------------+--------------------------------------+
    | address        | 10.152.124.41                        |
    | admin_state_up | True                                 |
    | id             | 2dbf48d3-84ef-4926-a1bb-ebb51bc0e937 |
    | name           |                                      |
    | protocol_port  | 443                                  |
    | subnet_id      | 0dc68c76-4cf2-4952-90a5-de9206fb0246 |
    | tenant_id      | feacaa2326204509bd19e395917b47d6     |
    | weight         | 1                                    |
    +----------------+--------------------------------------+


*******    OPENSTACK BASED LOADBALANCER COMMANDS   ************

Below commands in the context of trying to migrate instances in IND1 to IND2
IND1 uses LBAASv2 and IND2 uses a enhancement over LBAASv2 i.e Octavia.

Migration script does not deal with LBs and hence they need to be migrated/setup
manually in IND2

Port Mirroring script has created a port for the LB virtual port in IND2.

First thing to do is use/associate the existing mirrored port in IND2. Then
start replicating the setup as in IND1 to be able to reuse the LB in IND2.

(openstack) loadbalancer create --vip-port-id \
5d2d9224-9d46-4ff4-90ab-1e10e22e7bd3 --name kart-lb
+---------------------+--------------------------------------+
| Field               | Value                                |
+---------------------+--------------------------------------+
| admin_state_up      | True                                 |
| created_at          | 2019-09-30T05:05:52                  |
| description         |                                      |
| flavor_id           |                                      |
| id                  | 872ffcd7-731a-4f2a-9b02-862b84686990 |
| listeners           |                                      |
| name                | kart-lb                              |
| operating_status    | OFFLINE                              |
| pools               |                                      |
| project_id          | 8885e368558d4ac6a63526b1e7ca0f5e     |
| provider            | octavia                              |
| provisioning_status | PENDING_CREATE                       |
| updated_at          | None                                 |
| vip_address         | 10.152.124.73                        |
| vip_network_id      | 5fe37a12-edd4-40c2-8304-6a37a306ef5c |
| vip_port_id         | 5d2d9224-9d46-4ff4-90ab-1e10e22e7bd3 |
| vip_qos_policy_id   | None                                 |
| vip_subnet_id       | a57453d1-60bb-49ab-b858-1aed6d01bb00 |
+---------------------+--------------------------------------+

(openstack) loadbalancer show kart-lb
+---------------------+--------------------------------------+
| Field               | Value                                |
+---------------------+--------------------------------------+
| admin_state_up      | True                                 |
| created_at          | 2019-09-30T05:05:52                  |
| description         |                                      |
| flavor_id           |                                      |
| id                  | 872ffcd7-731a-4f2a-9b02-862b84686990 |
| listeners           |                                      |
| name                | kart-lb                              |
| operating_status    | ONLINE                               |
| pools               |                                      |
| project_id          | 8885e368558d4ac6a63526b1e7ca0f5e     |
| provider            | octavia                              |
| provisioning_status | ACTIVE                               |
| updated_at          | 2019-09-30T05:07:19                  |
| vip_address         | 10.152.124.73                        |
| vip_network_id      | 5fe37a12-edd4-40c2-8304-6a37a306ef5c |
| vip_port_id         | 5d2d9224-9d46-4ff4-90ab-1e10e22e7bd3 |
| vip_qos_policy_id   | None                                 |
| vip_subnet_id       | a57453d1-60bb-49ab-b858-1aed6d01bb00 |
+---------------------+--------------------------------------+

(openstack) port show 5d2d9224-9d46-4ff4-90ab-1e10e22e7bd3
+-----------------------+------------------------------------------------------------------------------------------------------+
| Field                 | Value                                                                                                |
+-----------------------+------------------------------------------------------------------------------------------------------+
| admin_state_up        | UP                                                                                                   |
| allowed_address_pairs |                                                                                                      |
| binding_host_id       |                                                                                                      |
| binding_profile       |                                                                                                      |
| binding_vif_details   |                                                                                                      |
| binding_vif_type      | unbound                                                                                              |
| binding_vnic_type     | normal                                                                                               |
| created_at            | 2019-09-27T06:13:53Z                                                                                 |
| data_plane_status     | None                                                                                                 |
| description           | ;;;{"origin": "ind1"}                                                                                |
| device_id             |                                                                                                      |
| device_owner          |                                                                                                      |
| dns_assignment        | fqdn='host-10-152-124-73.openstacklocal.', hostname='host-10-152-124-73', ip_address='10.152.124.73' |
| dns_name              |                                                                                                      |
| extra_dhcp_opts       |                                                                                                      |
| fixed_ips             | ip_address='10.152.124.73', subnet_id='a57453d1-60bb-49ab-b858-1aed6d01bb00'                         |
| id                    | 5d2d9224-9d46-4ff4-90ab-1e10e22e7bd3                                                                 |
| ip_address            | None                                                                                                 |
| mac_address           | fa:16:aa:64:aa:c0                                                                                    |
| name                  |                                                                                                      |
| network_id            | 5fe37a12-edd4-40c2-8304-6a37a306ef5c                                                                 |
| option_name           | None                                                                                                 |
| option_value          | None                                                                                                 |
| port_security_enabled | True                                                                                                 |
| project_id            | 8885e368558d4ac6a63526b1e7ca0f5e                                                                     |
| qos_policy_id         | None                                                                                                 |
| revision_number       | 8                                                                                                    |
| security_group_ids    | 68ac37e3-f44b-4a6c-94bb-eba78beb8559                                                                 |
| status                | DOWN                                                                                                 |
| subnet_id             | None                                                                                                 |
| tags                  |                                                                                                      |
| trunk_details         | None                                                                                                 |
| updated_at            | 2019-09-30T05:07:04Z                                                                                 |
+-----------------------+------------------------------------------------------------------------------------------------------+


(openstack) security group create kart-lb-sg
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| Field           | Value                                                                                                                                                 |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| created_at      | 2019-09-30T05:08:30Z                                                                                                                                  |
| description     | kart-lb-sg                                                                                                                                            |
| id              | 805cd5a0-8518-4c9f-8e6d-020f23555e15                                                                                                                  |
| name            | kart-lb-sg                                                                                                                                            |
| project_id      | 8885e368558d4ac6a63526b1e7ca0f5e                                                                                                                      |
| revision_number | 2                                                                                                                                                     |
| rules           | created_at='2019-09-30T05:08:30Z', direction='egress', ethertype='IPv6', id='53bfd977-e696-4a07-bd10-50dce0d866ad', updated_at='2019-09-30T05:08:30Z' |
|                 | created_at='2019-09-30T05:08:30Z', direction='egress', ethertype='IPv4', id='53ff8b60-c51e-44ba-bfd5-d0ad6f9e4a3b', updated_at='2019-09-30T05:08:30Z' |
| updated_at      | 2019-09-30T05:08:30Z                                                                                                                                  |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+


(openstack) security group rule create --ingress --protocol tcp --dst-port 80 --remote-ip 0.0.0.0/0 kart-lb-sg
+-------------------+--------------------------------------+
| Field             | Value                                |
+-------------------+--------------------------------------+
| created_at        | 2019-09-30T05:11:31Z                 |
| description       |                                      |
| direction         | ingress                              |
| ether_type        | IPv4                                 |
| id                | 088cb970-76ae-49fd-bfd4-313af8d1995e |
| name              | None                                 |
| port_range_max    | 80                                   |
| port_range_min    | 80                                   |
| project_id        | 8885e368558d4ac6a63526b1e7ca0f5e     |
| protocol          | tcp                                  |
| remote_group_id   | None                                 |
| remote_ip_prefix  | 0.0.0.0/0                            |
| revision_number   | 0                                    |
| security_group_id | 805cd5a0-8518-4c9f-8e6d-020f23555e15 |
| updated_at        | 2019-09-30T05:11:31Z                 |
+-------------------+--------------------------------------+
(openstack) security group rule create --ingress --protocol tcp --dst-port 443 --remote-ip 0.0.0.0/0 kart-lb-sg
+-------------------+--------------------------------------+
| Field             | Value                                |
+-------------------+--------------------------------------+
| created_at        | 2019-09-30T05:11:43Z                 |
| description       |                                      |
| direction         | ingress                              |
| ether_type        | IPv4                                 |
| id                | cc165d97-0ccc-4dcd-b479-af5f694a8dd5 |
| name              | None                                 |
| port_range_max    | 443                                  |
| port_range_min    | 443                                  |
| project_id        | 8885e368558d4ac6a63526b1e7ca0f5e     |
| protocol          | tcp                                  |
| remote_group_id   | None                                 |
| remote_ip_prefix  | 0.0.0.0/0                            |
| revision_number   | 0                                    |
| security_group_id | 805cd5a0-8518-4c9f-8e6d-020f23555e15 |
| updated_at        | 2019-09-30T05:11:43Z                 |
+-------------------+--------------------------------------+


(openstack) security group rule list kart-lb-sg
+--------------------------------------+-------------+-----------+------------+-----------------------+
| ID                                   | IP Protocol | IP Range  | Port Range | Remote Security Group |
+--------------------------------------+-------------+-----------+------------+-----------------------+
| 088cb970-76ae-49fd-bfd4-313af8d1995e | tcp         | 0.0.0.0/0 | 80:80      | None                  |
| 53bfd977-e696-4a07-bd10-50dce0d866ad | None        | None      |            | None                  |
| 53ff8b60-c51e-44ba-bfd5-d0ad6f9e4a3b | None        | None      |            | None                  |
| cc165d97-0ccc-4dcd-b479-af5f694a8dd5 | tcp         | 0.0.0.0/0 | 443:443    | None                  |
+--------------------------------------+-------------+-----------+------------+-----------------------+


Next Create listeners.

(openstack) loadbalancer listener create --name kart-lb-http --protocol HTTP --protocol-port 80 kart-lb
+-----------------------------+--------------------------------------+
| Field                       | Value                                |
+-----------------------------+--------------------------------------+
| admin_state_up              | True                                 |
| connection_limit            | -1                                   |
| created_at                  | 2019-09-30T05:19:25                  |
| default_pool_id             | None                                 |
| default_tls_container_ref   | None                                 |
| description                 |                                      |
| id                          | d7ad438f-f03a-417d-a29b-0e971dd51abb |
| insert_headers              | None                                 |
| l7policies                  |                                      |
| loadbalancers               | 872ffcd7-731a-4f2a-9b02-862b84686990 |
| name                        | kart-lb-http                         |
| operating_status            | OFFLINE                              |
| project_id                  | 8885e368558d4ac6a63526b1e7ca0f5e     |
| protocol                    | HTTP                                 |
| protocol_port               | 80                                   |
| provisioning_status         | PENDING_CREATE                       |
| sni_container_refs          | []                                   |
| timeout_client_data         |                                      |
| timeout_member_connect      |                                      |
| timeout_member_data         |                                      |
| timeout_tcp_inspect         |                                      |
| updated_at                  | None                                 |
| client_ca_tls_container_ref |                                      |
| client_authentication       |                                      |
| client_crl_container_ref    |                                      |
+-----------------------------+--------------------------------------+
(openstack) loadbalancer listener create --name kart-lb-https --protocol HTTPS --protocol-port 443 kart-lb
+-----------------------------+--------------------------------------+
| Field                       | Value                                |
+-----------------------------+--------------------------------------+
| admin_state_up              | True                                 |
| connection_limit            | -1                                   |
| created_at                  | 2019-09-30T05:20:02                  |
| default_pool_id             | None                                 |
| default_tls_container_ref   | None                                 |
| description                 |                                      |
| id                          | 4305db82-a478-4bea-8945-6a940147c00b |
| insert_headers              | None                                 |
| l7policies                  |                                      |
| loadbalancers               | 872ffcd7-731a-4f2a-9b02-862b84686990 |
| name                        | kart-lb-https                        |
| operating_status            | OFFLINE                              |
| project_id                  | 8885e368558d4ac6a63526b1e7ca0f5e     |
| protocol                    | HTTPS                                |
| protocol_port               | 443                                  |
| provisioning_status         | PENDING_CREATE                       |
| sni_container_refs          | []                                   |
| timeout_client_data         |                                      |
| timeout_member_connect      |                                      |
| timeout_member_data         |                                      |
| timeout_tcp_inspect         |                                      |
| updated_at                  | None                                 |
| client_ca_tls_container_ref |                                      |
| client_authentication       |                                      |
| client_crl_container_ref    |                                      |
+-----------------------------+--------------------------------------+

Create LB pools without members.

(openstack) loadbalancer pool create --name kart-lb-pool-http --lb-algorithm ROUND_ROBIN --listener kart-lb-http --protocol HTTP
+----------------------+--------------------------------------+
| Field                | Value                                |
+----------------------+--------------------------------------+
| admin_state_up       | True                                 |
| created_at           | 2019-09-30T05:21:33                  |
| description          |                                      |
| healthmonitor_id     |                                      |
| id                   | d15d3732-64a4-48ea-97d9-4787e0c16377 |
| lb_algorithm         | ROUND_ROBIN                          |
| listeners            | d7ad438f-f03a-417d-a29b-0e971dd51abb |
| loadbalancers        | 872ffcd7-731a-4f2a-9b02-862b84686990 |
| members              |                                      |
| name                 | kart-lb-pool-http                    |
| operating_status     | OFFLINE                              |
| project_id           | 8885e368558d4ac6a63526b1e7ca0f5e     |
| protocol             | HTTP                                 |
| provisioning_status  | PENDING_CREATE                       |
| session_persistence  | None                                 |
| updated_at           | None                                 |
| tls_container_ref    |                                      |
| ca_tls_container_ref |                                      |
| crl_container_ref    |                                      |
| tls_enabled          |                                      |
+----------------------+--------------------------------------+
(openstack) loadbalancer pool create --name kart-lb-pool-https --lb-algorithm ROUND_ROBIN --listener kart-lb-https --protocol HTTPS
+----------------------+--------------------------------------+
| Field                | Value                                |
+----------------------+--------------------------------------+
| admin_state_up       | True                                 |
| created_at           | 2019-09-30T05:22:03                  |
| description          |                                      |
| healthmonitor_id     |                                      |
| id                   | 96eb78f5-7705-435e-955d-bc74d1f795a8 |
| lb_algorithm         | ROUND_ROBIN                          |
| listeners            | 4305db82-a478-4bea-8945-6a940147c00b |
| loadbalancers        | 872ffcd7-731a-4f2a-9b02-862b84686990 |
| members              |                                      |
| name                 | kart-lb-pool-https                   |
| operating_status     | OFFLINE                              |
| project_id           | 8885e368558d4ac6a63526b1e7ca0f5e     |
| protocol             | HTTPS                                |
| provisioning_status  | PENDING_CREATE                       |
| session_persistence  | None                                 |
| updated_at           | None                                 |
| tls_container_ref    |                                      |
| ca_tls_container_ref |                                      |
| crl_container_ref    |                                      |
| tls_enabled          |                                      |
+----------------------+--------------------------------------+
```
