from geix_common.clients import openstack as ost
from geix_common import utils
from collections import defaultdict
from IPy import IP, IPSet
from oslo_config import cfg
from itertools import groupby
from operator import itemgetter
import logging
import itertools

CONF = cfg.CONF
opts = [
    cfg.StrOpt('src_os_username',
               help="Source Openstack environment cloud-admin username"),
    cfg.StrOpt('src_os_password',
               help="Source Openstack environment cloud-admin password"),
    cfg.StrOpt('src_os_auth_url',
               help="Source Openstack environment auth_url"),
    cfg.StrOpt('src_os_domain',
               help="Source Openstack environment domain name"),
    cfg.StrOpt('src_os_project_name',
               help="Target Openstack environment project name"),
    cfg.StrOpt('t_os_username',
               help="Target Openstack environment username"),
    cfg.StrOpt('t_os_password',
               help="Target Openstack environment password"),
    cfg.StrOpt('t_os_auth_url',
               help="Target Openstack environment auth_url"),
    cfg.StrOpt('t_os_domain',
               help="Target Openstack environment domain name"),
    cfg.StrOpt('t_os_project_name',
               help="Target Openstack environment project name"),
    cfg.ListOpt('t_subnets_exclude',
                default=['0ac97869-f947-40d9-b9b6-5bbd39962ca1',
                         'b4d5e84e-bc5c-44fa-b45f-8a1aa26c28a9'],
                help="Target environment subnets to be excluded \
                those that dont map to source environment")
]
CONF.register_opts(opts, group='openstack')


def add_parsers(subparsers):
    ''' Function that adds a argparser subparser for CLI arguments accepting
    subnet IDs to the main openstack oslo config parser object.
    '''
    myparser = subparsers.add_parser(
        'subnets',
        help="'python subnet_pool_alloc.py subnets -h' to \
        see more detail in this sub command option"
        )
    myparser.add_argument(
        '-p', '--free-pool-count', nargs='?',
        type=int, const=3,
        help="Free pool count desired which may or may not be available"
        )
    myparser.add_argument(
        '-pi', '--preserve-free-ips', type=int, default=10,
        help="Number of IPs to preserve in the source environment, \
        default being 10, you are free to override with this option"
        )
    group = myparser.add_mutually_exclusive_group()
    group.add_argument(
        "-s", "--single-subnet",
        help="Pass UUID of a single subnet from source for determining pool \
        allocation on source and target side"
        )
    group.add_argument(
        "-f", "--file-name",
        help="a txt file with subnet UUIDs from source one per line"
    )
    group.add_argument(
        "-a", "--all-subnets",
        help="The script will come up with a list of subnets \
        actively being used and some out with pool recommendation on the \
        source and the target environment", action='store_true'
        )


CONF.register_cli_opt(cfg.SubCommandOpt('subnets', handler=add_parsers))
CONF(default_config_files=['/etc/subnet_pool/subnet_pool.conf'])

utils.setup_logging()
LOG = logging.getLogger(__name__)


def main_loop():
    LOG.info("Initializing openstack clients.")
    cadm = ost.OSClients(
                         auth_url=CONF.openstack.src_os_auth_url,
                         domain=CONF.openstack.src_os_domain,
                         project_name=CONF.openstack.src_os_project_name,
                         username=CONF.openstack.src_os_username,
                         password=CONF.openstack.src_os_password
    )

    c1adm = ost.OSClients(
                          auth_url=CONF.openstack.t_os_auth_url,
                          domain=CONF.openstack.t_os_domain,
                          project_name=CONF.openstack.t_os_project_name,
                          username=CONF.openstack.t_os_username,
                          password=CONF.openstack.t_os_password
    )
    LOG.info("Determining subnets available on the target environment side")
    t_all_subnets = c1adm.neutron.list_subnets()['subnets']
    t_10_152_subnets = {s['id']: s for s in t_all_subnets
                        if s['name'].startswith('TSUBNET')
                        and s['cidr'].startswith('10.152.')}
    LOG.info("Removal of subnets that are non existent on the source side")
    # Explicit removal of unwanted subnets with CIDR as they dont exist
    # in source TSUBNET-GEIX-IAD1-SND1-Internal-SND01,
    # TSUBNET-GEIX-POC-IAD1-ENG1-Internal2-SND01
    for s in CONF.openstack.t_subnets_exclude:
        t_10_152_subnets.pop(s)
    t_cidr = {s['id']: s['cidr'] for s in t_10_152_subnets.values()}
    t_subnet_pools_range = defaultdict(list)
    for s in t_10_152_subnets:
        t_range = []
        for p in t_10_152_subnets[s]['allocation_pools']:
            t_range.extend([IP(p['start']), IP(p['end'])])
        t_subnet_pools_range[t_10_152_subnets[s]['id']] = t_range

    # Determine all subnets from the source side
    s_all_subnets = cadm.neutron.list_subnets()['subnets']
    s_10_152_subnets = {}
    for s in s_all_subnets:
        if s['cidr'] in t_cidr.values():
            s_10_152_subnets[s['id']] = s
    s_cidr = {s['id']: s['cidr'] for s in s_10_152_subnets.values()}

    subnet_mapping = {}
    if len(s_cidr) != len(t_cidr):
        LOG.error("One to one subnet mapping is broken without which \
                script logic will fail, Please add subnet IDs to the \
                exclusion list that need not be looked at in the CONF \
                file. Quitting now..")
        exit()
    for i in zip(sorted(s_cidr.items(), key=lambda x: x[1]),
                 sorted(t_cidr.items(), key=lambda x: x[1])):
        subnet_mapping[i[0][0]] = i[1][0]
    # Get a list of active ports.
    LOG.info("Getting a list of active ports on the source side")
    s_all_ports = cadm.neutron.list_ports()['ports']
    s_subnet_ips = defaultdict(list)    # Get the list of IPs in each subnet
    for p in s_all_ports:
        if p['description'] == ';;;{"origin": "iad2"}':
             continue
        else:
            for i in p['fixed_ips']:
                if i['subnet_id'] in s_10_152_subnets:
                    s_subnet_ips[i['subnet_id']].append(i['ip_address'])
    # Maintain a list of IPs for each subnet in IP objects.
    s_subnet_ips_ipform = defaultdict(IPSet)
    for s in s_subnet_ips:
        for ip in s_subnet_ips[s]:
            s_subnet_ips_ipform[s].add(IP(ip))
    # Create an IPSet from the pool ranges defined for a subnets
    s_subnet_pools = defaultdict(list)       # IPSet of current allocation-pool
    # Capture start/end pool IPS for subnet
    s_subnet_pools_range = defaultdict(list)
    for s in s_10_152_subnets:
        s_ipset = IPSet()
        s_range = []
        for p in s_10_152_subnets[s]['allocation_pools']:
            for ip in range(IP(p['start']).int(), IP(p['end']).int()+1):
                s_ipset.add(IP(ip))
            s_range.extend([IP(p['start']), IP(p['end'])])
        s_subnet_pools[s_10_152_subnets[s]['id']] = s_ipset
        s_subnet_pools_range[s_10_152_subnets[s]['id']] = s_range

    def get_freeiprange(sub_id, top_free_count, preserve_free_ips):
        '''Function that returns the IPSet() of free IPs.
        Takes in a subnet ID to work on.
        Takes in a count of free subnets to be returned.
        Takes in a count of free IPs to be preserved.
        '''
        s_free_ipset = s_subnet_pools[sub_id] - s_subnet_ips_ipform[sub_id]
        s_free_ips_expanded = []   # List to capture all IPs in IPSet()
        for ip in s_free_ipset:
            for ip in ip:
                s_free_ips_expanded.append(ip)
        s_free_ips_expanded.sort()
        s_free_ip_ranges = []
        for k, g in groupby(
          enumerate(s_free_ips_expanded), lambda (i, x): i-(x.int())):
            s_free_ip_ranges.append(map(itemgetter(1), g))

        s_free_ip_ranges_sorted = sorted(
            s_free_ip_ranges, key=lambda x: len(x), reverse=True)
        s_free_range_bounds = []
        s_chosen_free_pool_ips = []
        for r in range(0, top_free_count):
            try:
                f = s_free_ip_ranges_sorted[r]
                start, end = f[0], f[-1]
                s_free_range_bounds.extend([start, end])
                s_chosen_free_pool_ips.extend(f)
            except IndexError:
                LOG.info("No more free IP ranges available in %s", sub_id)
                break
        s_leftover_free_pool_ips = []
        try:
            s_leftover_free_pool_ips = s_free_ip_ranges_sorted[top_free_count:]
            s_leftover_free_pool_ips = list(
                itertools.chain.from_iterable(s_leftover_free_pool_ips)
                )
        except IndexError:
            LOG.info("No free IPs available outside of the chosen free range, \
            will require to shrink from the chosen free pool of IPs")
        if len(s_leftover_free_pool_ips) < preserve_free_ips:
            diff_count = preserve_free_ips - len(s_leftover_free_pool_ips)
            LOG.info("Dipping into the chosen free pool to reach the \
                    desired number of free IPs to be preserved")
            if diff_count > (len(s_chosen_free_pool_ips)-2):
                LOG.error(
                    "Preserving {} IPs will exhaust your free IP pool".format(
                     preserve_free_ips))
                exit()
            else:
                s_chosen_free_pool_ips = s_chosen_free_pool_ips[:-diff_count]
                s_free_ip_ranges = []
                for k, g in groupby(
                  enumerate(s_chosen_free_pool_ips),
                  lambda (i, x): i-(x.int())):
                    s_free_ip_ranges.append(map(itemgetter(1), g))
                s_free_ip_ranges_sorted = sorted(
                    s_free_ip_ranges, key=lambda x: len(x), reverse=True)
                s_free_range_bounds = []
                for r in s_free_ip_ranges_sorted:
                    start, end = r[0], r[-1]
                    s_free_range_bounds.extend([start, end])
        return s_free_range_bounds

    def get_alloc_pool_bounds(sub_id, s_free_range_bounds):
        s_alloc_pool_bounds = []
        for i in range(0, len(s_free_range_bounds)):
            if i % 2 == 0:
                ip = IP(s_free_range_bounds[i].int() - 1)
                s_alloc_pool_bounds.append(ip)
            else:
                ip = IP(s_free_range_bounds[i].int() + 1)
                s_alloc_pool_bounds.append(ip)
        s_alloc_pool_bounds.extend(s_subnet_pools_range[sub_id])
        s_alloc_pool_bounds.sort()
        return s_alloc_pool_bounds

    def gen_s_cli_cmd(sub_id, s_alloc_pool_bounds):
        cmd = 'openstack subnet set --no-allocation-pool '
        for i in range(0, len(s_alloc_pool_bounds)):
            if i % 2 == 0:
                start = s_alloc_pool_bounds[i].strNormal()
                end = s_alloc_pool_bounds[i+1].strNormal()
                pool = "--allocation-pool start={},end={} ".format(start, end)
                cmd += pool
            else:
                continue
        cmd += sub_id
        LOG.info("Source environment subnet pool reallocation commands below \
            for subnet %s", sub_id)
        print(cmd)

    def gen_t_cli_cmd(sub_id, s_free_range_bounds):
        t_sub_id = subnet_mapping[sub_id]
        cmd = 'openstack subnet set --no-allocation-pool '
        if s_10_152_subnets[sub_id]['allocation_pools']
        == t_10_152_subnets[t_sub_id]['allocation_pools']:
            for i in range(0, len(s_free_range_bounds), 2):
                start = s_free_range_bounds[i].strNormal()
                end = s_free_range_bounds[i+1].strNormal()
                pool = "--allocation-pool start={},end={} ".format(
                    start, end)
                cmd += pool
        else:
            new_pool = t_subnet_pools_range[t_sub_id] + s_free_range_bounds
            new_pool.sort()
            cont = False
            for i in range(0, len(new_pool), 2):
                if not cont:
                    start = new_pool[i].strNormal()
                try:
                    if new_pool[i+1].int()+1 == new_pool[i+2].int():
                        cont = True
                        continue
                    else:
                        end = new_pool[i+1].strNormal()
                        pool = "--allocation-pool start={},end={} ".format(
                            start, end)
                        cmd += pool
                        cont = False
                except IndexError:
                    end = new_pool[i+1].strNormal()
                    pool = "--allocation-pool start={},end={} ".format(
                        start, end)
                    cmd += pool
        cmd += t_sub_id
        LOG.info("Target environment subnet pool reallocation commands for \
            mapping subnet on target side %s", t_sub_id)
        print(cmd)

    def get_pool(sub_id):
        s_free_range_bounds = get_freeiprange(
            sub_id, CONF.subnets.free_pool_count,
            CONF.subnets.preserve_free_ips
            )
        s_alloc_pool_bounds = get_alloc_pool_bounds(
            sub_id, s_free_range_bounds
        )
        gen_s_cli_cmd(sub_id, s_alloc_pool_bounds)
        gen_t_cli_cmd(sub_id, s_free_range_bounds)
        print("\n\n")

    if CONF.subnets.single_subnet:
        get_pool(CONF.subnets.single_subnet)
    if CONF.subnets.file_name:
        for line in open(CONF.subnets.file_name, 'r'):
            get_pool(line.strip())
    if CONF.subnets.all_subnets:
        for sub_id in s_10_152_subnets:
            get_pool(sub_id)


if __name__ == '__main__':
    LOG.info("Starting the subnet pool check process.. ")
main_loop()
