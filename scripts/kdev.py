#!/usr/bin/env python3

import os
import sys
import shutil
from argparse import ArgumentParser

PKGS = 'pciutils ethtool rdma-core infiniband-diags libibverbs-utils librdmacm-utils'
CUSTOM_PKGS = '/home/kheib/rdma-core-build/RPMS/x86_64/*.rpm'
KERNEL_DIR = '/home/kheib/git/upstream/linux'
ROOTFS_DIR = '/home/kheib/rootfs'
HOME_DIR = '/home/kheib'

class kdev(object):

    def get_parser(self):
        if not hasattr(self, 'parser'):
            self.parser = ArgumentParser()
        return self.parser

    def parse_args(self, args):
        self.Parser.add_argument('--build', help='Build kernel and update \
            rootfs kernel modules', action='store_true', default=False)
        self.Parser.add_argument('--rootfs', help='Create fedora rootfs \
            file', action='store_true', default=False)
        self.Parser.add_argument('--custom_pkgs', help='Install custom packages',
                action='store_true', default=False)
        self.Parser.add_argument('--run', help='Run an instance of VM using \
             the built kernel', action='store_true', default=False)
        self.Parser.parse_args(namespace=self, args=args)

    def build_kernel(self):
        cwd = os.getcwd()
        os.chdir(KERNEL_DIR)
        os.system('make -j 8')
        os.system('make -j 8 modules_install INSTALL_MOD_PATH=%s' % ROOTFS_DIR)
        os.chdir(ROOTFS_DIR)
        os.system('find . | cpio -o --format=newc > %s/rootfs.img' % HOME_DIR)
        os.chdir(cwd)

    def create_rootfs(self):
        cwd = os.getcwd()
        if os.path.exists(ROOTFS_DIR):
            shutil.rmtree(ROOTFS_DIR)
        os.mkdir(ROOTFS_DIR)
        os.chdir(ROOTFS_DIR)
        os.system('dnf groupinstall "Minimal Install" --releasever=33 --installroot=%s --repo=fedora --repo=updates -y' % ROOTFS_DIR)
        os.system('dnf install --releasever=33 --installroot=%s --repo=fedora  --repo=updates -y %s' % (ROOTFS_DIR, PKGS))
        os.system("sed -i 's/root:\*:/root::/g' etc/shadow")
        os.system('find . | cpio -o --format=newc > %s/rootfs.img' % HOME_DIR)
        os.chdir(cwd)

    def install_custom_pkgs(self):
        cwd = os.getcwd()
        if os.path.exists(ROOTFS_DIR):
            os.chdir(ROOTFS_DIR)
            os.system('dnf reinstall --releasever=33 --installroot=%s --repo=fedora --repo=updates -y %s' % (ROOTFS_DIR, CUSTOM_PKGS))
            os.system('find . | cpio -o --format=newc > %s/rootfs.img' % HOME_DIR)
            os.chdir(cwd)
        else:
            print("NO rootfs directory created!!")

    def run_vm(self):
        qemu_cmd = 'qemu-system-x86_64 -s -cpu host -smp cpus=4 -m 4G -nographic -enable-kvm \
                    -append "root=/dev/ram rdinit=/sbin/init console=ttyS0 nokaslr" \
                    -net nic,model=virtio \
                    -kernel %s/arch/x86/boot/bzImage -initrd %s/rootfs.img ' % (KERNEL_DIR, HOME_DIR)
        os.system(qemu_cmd)

    def execute(self, args):
        self.parse_args(args)
        if self.build:
            self.build_kernel()
        if self.rootfs:
            self.create_rootfs()
        if self.custom_pkgs:
            self.install_custom_pkgs()
        if self.run:
            self.run_vm()

    Parser = property(get_parser)

if __name__ == '__main__':
    kdev().execute(sys.argv[1:])
