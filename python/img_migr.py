from geix_common.clients import openstack as ost
from oslo_config import cfg
from geix_common import utils
from time import sleep
from paramiko.ssh_exception import NoValidConnectionsError
from novaclient.exceptions import Conflict
from math import ceil
import os
import subprocess
import fabric
import threading
import guestfs
import logging
import argparse
import Queue

CONF = cfg.CONF
opts = [
    cfg.StrOpt('src_os_username',
               help="Source Openstack environment username"),
    cfg.StrOpt('src_os_password',
               help="Source Openstack environment password"),
    cfg.StrOpt('t_os_username',
               help="Source Openstack environment username"),
    cfg.StrOpt('src_os_auth_url',
               help="Source Openstack environment auth_url"),
    cfg.StrOpt('src_os_domain',
               help="Source Openstack environment domain name"),
    cfg.StrOpt('src_os_project_name',
               help="Target Openstack environment project name"),
    cfg.StrOpt('t_os_password',
               help="Target Openstack environment password"),
    cfg.StrOpt('t_os_auth_url',
               help="Target Openstack environment auth_url"),
    cfg.StrOpt('t_os_domain',
               help="Target Openstack environment domain name"),
    cfg.StrOpt('t_os_project_name',
               help="Target Openstack environment project name")
]
CONF.register_opts(opts, group='openstack')
opts = [
    cfg.StrOpt('rescue_img',
               help="Rescue Image UUID to be used in the target openstack \
        environment on the helper instance"
        ),
    cfg.StrOpt('zero_img',
               help="Zero image used to spin up a dummy/helper instannce"),
    cfg.StrOpt('tgt_net_id',
               help="Network UUID for the helper instance"),
    cfg.StrOpt('tgt_avail_zone',
               help="availability_zone to be used in the target environment"),
    cfg.ListOpt('tgt_sec_groups',
                help="An array or list of one or more security_groups to \
                be attached to the helper instance in target environment"
                ),
    cfg.StrOpt('tgt_key_name',
               help="Login Key to be used in the target environment on the \
               helper instance"),
    cfg.StrOpt('tgt_net_id',
               help="Network UUID for the helper instance"),
    cfg.StrOpt('d_key',
               help="Fully Qualified path of private Key file to be used to \
               access the dummy instance over ssh"
               ),
    cfg.StrOpt('nfs_mountp',
               help="NFS share where all source images are available"),
    cfg.StrOpt('nfs_dir',
               help="Directory path for mounted nfs_share"),
]
CONF.register_opts(opts, group='image_migration')
def add_parsers(subparsers):
    ''' Function that adds a argparser subparser for CLI arguments accepting image IDs to the main openstack oslo
    config parser object.'''
    myparser = subparsers.add_parser('images', help="'python img_mig.py images -h' to see more detail in this sub command option")
    group = myparser.add_mutually_exclusive_group()
    group.add_argument(
        "-s", "--single-image",
        help="Pass UUID of a single image for migration"
        )
    group.add_argument(
        "-f", "--file-name",
        help="a txt file with image UUIDs one per line"
    )
    group.add_argument(
        "-a", "--all-active-images",
        help="The script will come up with a list of images actively being used and start migrating them to the target environment",
        action = 'store_true'
        )
CONF.register_cli_opt(cfg.SubCommandOpt('images', handler=add_parsers))
CONF(default_config_files=['/etc/migrator/migrator.conf'])

utils.setup_logging()
LOG = logging.getLogger(__name__)

def get_logger(name, log_file, level=logging.INFO):
    ''' this helper function initializes an instance of logger with filehandler going with it. '''
    fh = logging.FileHandler(log_file)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

class Migrator(threading.Thread):
    '''
    Migrator Class subclassed from the thread class.
    Takes in following arguments for working on an image migration between 2 environments.
    1. src_img_uuid(string type): Image UUID from source environment
    2. src_cl(instance of OSClients): Openstack Client instance providing access to the source OS environment
    3. tgt_cl(instance of OSClients): Openstack Client instance providing access to the target OS environment
    4. proj_mapping(dict): mapping of project IDs between source and target environment
    5. logger: logger instance to do thread level logging
    '''
    def __init__(self, src_img_uuid, src_cl, tgt_cl, proj_mapping, logger):
        threading.Thread.__init__(self)
        self.logger = logger
        self.src_img_uuid = src_img_uuid
        self.c = src_cl
        self.c1 = tgt_cl
        self.src_img = self.c.glance.images.get(self.src_img_uuid)
        self.proj_mapping = proj_mapping
        self.dst_img_owner = self.proj_mapping[self.src_img.owner]
        self.logger.info('Source Image owner is %s and Dest image would be %s',self.src_img.owner,self.dst_img_owner)
        self.rescue_img = CONF.image_migration.rescue_img # Identifies the rescue img from the target environment
        self.zero_img = CONF.image_migration.zero_img # Identifies the image for spinning up the dummy instance.
        # this here will be the target environment network ID for dummy instance creation.
        self.tgt_net_id = CONF.image_migration.tgt_net_id
        # this here is the target compute node in ATL1 stage env
        self.tgt_avail_zone = CONF.image_migration.tgt_avail_zone
        self.tgt_sec_groups = CONF.image_migration.tgt_sec_groups # sec groups to be added to dummy instance
        self.tgt_key_name = CONF.image_migration.tgt_key_name # key to be associated with dummy instance
        self.d_key =  CONF.image_migration.d_key # Full qualified path of private key to access the dummy instance
        self.nfs_mountp = CONF.image_migration.nfs_mountp # NFS export
        self.nfs_dir = CONF.image_migration.nfs_dir

    def get_img_virtual_size(self):
        '''
        Class method that derives the virtual disk size on the image
        '''
        g = guestfs.GuestFS(python_return_dict=True)
        os.chdir(self.nfs_dir)
        if not os.path.isfile(self.src_img_uuid):
            raise Exception("Image not found in NFS repo")
        self.src_img_type = g.disk_format(self.src_img_uuid)
        cmd = "qemu-img info {} | grep 'virtual size' ".format(self.src_img_uuid)
        output = subprocess.check_output(cmd, shell=True)
        self.src_img_virtual_size = int( ceil ( float( output.split(' ')[2].rstrip('G') ) ) )
        self.logger.info('Image file is of type %s and virtual size is %s',self.src_img_type,self.src_img_virtual_size)

    def choose_dummy_inst_flv(self):
        ''' This function determines the flavor for the dummy instance creation to create target image '''
        self.flv_chosen = ''
        # Tracking all custom flavors created for image migration
        migr_flv = { f.id: f for f in self.c1.nova.flavors.list(is_public=False) if 'a1.' in f.name }
        for p in self.c1.keystone.projects.list():
            if p.name == self.c1.auth.project_name:
                proj_id = p.id
        #Figure out the flavor to be used with the dummy instance as per min disk required
        for f in migr_flv:
            if migr_flv[f].disk == self.src_img_virtual_size:
                self.flv_chosen = f
                break
        if not self.flv_chosen:
            self.logger.info("No suitable flavor found!, Creating a new flavor")
            self.flv_chosen = self.c1.nova.flavors.create('a1.c2m4d'+str(self.src_img_virtual_size), ram=4096, \
            vcpus=2, disk=self.src_img_virtual_size, is_public=False)
            self.c1.nova.flavor_access.add_tenant_access(self.flv_chosen.id, proj_id)
        self.logger.info("Flavor chosen for image %s is %s",self.src_img_uuid,self.flv_chosen)

    def dummy_create_rescue(self):
        '''Create a dummy instance & puts into rescue for image sparse and copy process'''
        self.logger.info("Creating Dummy instance to help with image migration")
        inst_name = 'dummy_{}'.format(self.src_img_uuid)
        self.d_inst = self.c1.nova.servers.create(image=self.zero_img, name=inst_name, flavor=self.flv_chosen, nics=[{'net-id':self.tgt_net_id}], \
                        availability_zone=self.tgt_avail_zone, security_groups=self.tgt_sec_groups, \
                        meta={'license':'None','long_run':'True','issue':'None','UAI':'UAI2008331','env':'prod'}, key_name=self.tgt_key_name, \
                        config_drive=True)
        count = 0
        while self.d_inst.status != 'ACTIVE' and count < 120:
            self.d_inst = self.c1.nova.servers.get(self.d_inst.id) # make a call again to fetch all instance details after creation.
            sleep(1)
            count += 1
        self.d_ip = self.d_inst.addresses.values()[0][0]['addr']
        self.d_rescue = self.c1.nova.servers.rescue(self.d_inst, image=self.rescue_img)
        count = 0
        while self.d_inst.status != 'RESCUE' and count < 60:
            self.d_inst = self.c1.nova.servers.get(self.d_inst.id) # make a call again to fetch all instance details after creation.
            sleep(1)
            count += 1
        self.d_ssh_c = fabric.Connection(self.d_ip, user='gecloud', connect_kwargs={'key_filename':self.d_key})
        self.logger.info("Dummy instance for %s created with IP %s",self.src_img_uuid,self.d_ip)
        sleep(5)

    def new_image_creation(self):
        ''' Function that works on new image creation inside the dummy instance'''
        cmd = 'sudo mkdir -p {0};sudo mount {1} {0}'.format(self.nfs_dir,self.nfs_mountp)
        for attempt in range(0,3):
            try:
                self.logger.info(self.d_ssh_c.run(cmd, hide=True))
            except NoValidConnectionsError:
                sleep(5)
                continue
            break
        cmd1 = 'sudo /bin/bash {0}/img.sh {1} {0} {2}'.format(self.nfs_dir,self.src_img_uuid,self.src_img_type)
        self.logger.info(self.d_ssh_c.run(cmd1, hide=True))
        self.c1.nova.servers.unrescue(self.d_inst)
        count = 0
        while self.d_inst.status != 'ACTIVE' and count < 120:
            self.d_inst = self.c1.nova.servers.get(self.d_inst.id) # make a call again to fetch all instance details after creation.
            sleep(1)
            count += 1
        try:
            self.c1.nova.servers.stop(self.d_inst)
        except Conflict:
            sleep(60)
            self.c1.nova.servers.stop(self.d_inst.id)
        count = 0
        while self.d_inst.status != 'SHUTOFF' and count < 60:
            self.d_inst = self.c1.nova.servers.get(self.d_inst.id) # make a call again to fetch all instance details after creation.
            sleep(1)
            count += 1
        self.new_img = self.c1.nova.servers.create_image(self.d_inst, self.src_img.name, metadata={'orig_image_uuid':self.src_img_uuid,
        'hw_disk_bus': 'scsi', 'hw_scsi_model': 'virtio-scsi'})
        sleep(30)
        self.c1.glance.images.update(self.new_img, remove_props=['boot_roles','base_image_ref', 'image_location', 'image_type', 'instance_uuid', \
        'owner_id', 'owner_project_name', 'owner_user_name', 'user_id'])
        self.logger.info("The source image %s has been copied to target image with ID %s",self.src_img_uuid,self.new_img)
        self.logger.info("Deleting dummy instance %s" % self.d_inst.id)
        self.c1.nova.servers.delete(self.d_inst)
        while True:
            try:
                self.c1.nova.servers.get(self.d_inst.id)
            except:
                break
        self.logger.info("Dummy instance %s is deleted" % self.d_inst.id)
        # Rename the chsum file
        old_chsum='%s/%s_cksum' % (self.nfs_dir,self.src_img_uuid)
        new_chsum='%s/%s_cksum' % (self.nfs_dir,self.new_img)
        self.logger.info("Renaming %s to %s" % (old_chsum,new_chsum))
	os.rename(old_chsum,new_chsum)

    def new_image_prop_upd(self):
        '''
        Class method that updates the newly created target image removing unwanted properties and retaining certain eseential proper        ties
        '''
        prop_filter = ['boot_roles', 'base_image_ref', 'checksum', 'container_format', 'created_at',
                        'disk_format', 'file', 'hw_disk_bus', 'hw_scsi_model','id', 'image_location', 'image_state', 'image_type',
                        'instance_uuid', 'kernel_id', 'license', 'min_disk', 'min_ram', 'name', 'owner', 'owner_id',
                        'owner_project_name', 'owner_user_name', 'ramdisk_id', 'role-alias', 'role_alias', 'scalr_meta',
                        'scalr-meta', 'schema', 'size', 'status', 'tags', 'uai', 'updated_at', 'user_id', 'virtual_size',
			'locations','direct_url' ]
        prop_list = list(self.src_img.keys())
        prop_retain = list(set(prop_list) - set(prop_filter))
        prop_retain_dict = { k: self.src_img[k] for k in prop_retain }
        prop_retain_dict['owner'] = self.dst_img_owner
        self.c1.glance.images.update(self.new_img, **prop_retain_dict)
        self.logger.info("The new target image with ID %s has been updated with some additional attributes from source", self.new_img)

    def run(self):
        self.get_img_virtual_size()
        self.choose_dummy_inst_flv()
        self.dummy_create_rescue()
        self.new_image_creation()
        self.new_image_prop_upd()

def main_loop():
    LOG.info("Initializing openstack clients and image migration process")
    c = ost.OSClients(
        auth_url=CONF.openstack.src_os_auth_url,
        domain=CONF.openstack.src_os_domain, project_name=CONF.openstack.src_os_project_name,
        username=CONF.openstack.src_os_username, password=CONF.openstack.src_os_password
    )

    c1 = ost.OSClients(
        auth_url=CONF.openstack.t_os_auth_url,
        domain=CONF.openstack.t_os_domain, project_name=CONF.openstack.t_os_project_name,
        username=CONF.openstack.t_os_username, password=CONF.openstack.t_os_password
    )

    LOG.info('Generate Mapping of project IDs between source and destination')
    src_project_l = {}
    dest_project_l = {}
    for p in c.keystone.projects.list():
        src_project_l[p.name] = p.id
    for p in c1.keystone.projects.list():
        dest_project_l[p.name] = p.id
    # Prepare mapping of Project IDs between source and destination.
    proj_mapping = {}
    for p in src_project_l:
        if p in dest_project_l:
            proj_mapping[ src_project_l[p] ] = dest_project_l[p]

    # Explicit Manual addition to the mapping for DIG1-PRD02 and CAS1-PRD01 projects to SND02 in IAD2.
    additional_mapping = {u'86c7045af1d84c199f6d96a356f86605': u'1ed446fc64ce4fe6b7c1306558b49a2c',
                          u'793266793dc243dbab0d0b2ab9d3d748': u'1ed446fc64ce4fe6b7c1306558b49a2c'
                        }
    proj_mapping.update(additional_mapping)

    LOG.info('List target images')
    target_imgs = c1.glance.images.list()
    copied_img_list = {i.id: i.orig_image_uuid for i in target_imgs if 'orig_image_uuid' in i.keys() }
    imgs = []
    if CONF.images.single_image:
        imgs.append(CONF.images.single_image)
    if CONF.images.file_name:
        for line in open(CONF.images.file_name, 'r'):
            imgs.append(line.strip())
    if CONF.images.all_active_images:
        allvms = c.get_all_vms(extra_attrs=True)
        all_images_src = {i.id: i for i in c.glance.images.list() }
        act_images = []
        for v in allvms:
            try:
                if allvms[v].image['id'] not in act_images:
                    act_images.append(allvms[v].image['id'])
            except (KeyError,TypeError) as e:
                pass
        act_images_d = {}
        for i in act_images:
            try:
                # Check for empty images which need no migration
                if all_images_src[i].size != 0:
                    act_images_d[i] = all_images_src[i]
            except KeyError:
                pass
        imgs.extend(act_images_d.keys())
    workers = Queue.Queue()
    for i in imgs:
        #checking if image has already been copied to destination.
        if i in copied_img_list.values():
            LOG.info('{} is already copied over to the destination'.format(i))
            continue
        cond = True
        logdir = '%s/img_migr/' % os.environ['HOME']
        name = 'migr_{}'.format(i)
        f_name = '{}.log'.format(i)
        t_logger = get_logger(name, os.path.join(logdir, f_name))
        migr = Migrator(i,c,c1,proj_mapping,t_logger)
        if workers.qsize() < 10:
            workers.put(migr)
            migr.start()
        else:
            while cond:
                for w in range(0,len(workers.queue)):
                    if not workers.queue[w].isAlive():
                        workers.queue.remove(workers.queue[w])
                        workers.put(migr)
                        migr.start()
                        cond = False
                        break
    LOG.info("Waiting for threads to finish")
    for w in range(0, len(workers.queue)):
        workers.queue[w].join()
if __name__ == '__main__':
    LOG.info("Starting the Image migration process.. ")
    main_loop()
