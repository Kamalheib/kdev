#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0
#
# Author: Kamal Heib <kheib@redhat.com>

from argparse import ArgumentParser
import shutil
import sys
import os

KERNEL_CONF = '/configs/.config'
KERNEL_DIR='/home/kheib/git/linux'
MODULES_DIR='/modules/'
ROOTFS_DIR='/home/kheib/kdev-rootfs'
ROOTFS = '/home/kheib/kdevrootfs.img'

class kdev(object):

    def get_parser(self):
        if not hasattr(self, 'parser'):
            self.parser = ArgumentParser()
        return self.parser

    def parse_args(self, args):
        self.Parser.add_argument('--clean', help='Cleanup',
                                 action='store_true', default=False)
        self.Parser.add_argument('--cleankernel', help='Cleanup kernel directory',
                                 action='store_true', default=False)
        self.Parser.add_argument('--cleanrootfs', help='Cleanup rootfs directory and file',
                                 action='store_true', default=False)
        self.Parser.add_argument('--config', help='Prepare kernel config',
                                 action='store_true', default=False)
        self.Parser.add_argument('--build', help='Build kernel',
                                 action='store_true', default=False)
        self.Parser.add_argument('--mods', help='Install kernel modules',
                                 action='store_true', default=False)
        self.Parser.add_argument('--fedora', help='Install Fedora',
                                 action='store_true', default=False)
        self.Parser.add_argument('--rootfs', help='Create rootfs file',
                                 action='store_true', default=False)
        self.Parser.add_argument('--run', help='Run virtual machine',
                                 action='store_true', default=False)
        self.Parser.parse_args(namespace=self, args=args)

    def clean_kernel(self):
        cwd = os.getcwd()
        os.chdir(KERNEL_DIR)
        os.system('make mrproper')
        os.chdir(cwd)

    def clean_rootfs(self):
        cwd = os.getcwd()
        os.system('rm -rf %s' % ROOTFS_DIR)
        os.system('rm -rf %s' % ROOTFS)
        os.chdir(cwd)

    def cleanup(self):
        cwd = os.getcwd()
        self.clean_kernel()
        self.clean_rootfs()
        os.chdir(cwd)

    def prepare_kernel_conf(self):
        cwd = os.getcwd()
        os.chdir(KERNEL_DIR)
        shutil.copy(cwd + KERNEL_CONF, KERNEL_DIR)
        os.system('make olddefconfig')
        os.chdir(cwd)

    def build_kernel(self):
        cwd = os.getcwd()
        os.chdir(KERNEL_DIR)
        os.system('make -j 8')
        os.chdir(cwd)

    def install_modules(self):
        cwd = os.getcwd()
        os.chdir(KERNEL_DIR)
        os.system('make -j 8 modules_install INSTALL_MOD_PATH=%s' % ROOTFS_DIR)
        shutil.copytree(cwd + MODULES_DIR, ROOTFS_DIR + '/root/modules', dirs_exist_ok=True)
        os.chdir(cwd)

    def install_fedora(self):
        cwd = os.getcwd()
        if not os.path.exists(ROOTFS_DIR):
            os.mkdir(ROOTFS_DIR)
        os.chdir(ROOTFS_DIR)
        os.system('dnf groupinstall "Minimal Install" --releasever=39 --installroot=%s --repo=fedora --repo=updates -y' % ROOTFS_DIR)
        os.system(r"sed -i 's/root:\*:/root::/g' etc/shadow")
        os.system("touch etc/systemd/zram-generator.conf")
        os.chdir(cwd)

    def create_rootfs(self):
        cwd = os.getcwd()
        os.chdir(ROOTFS_DIR)
        os.system('find . | cpio -o --format=newc > %s' % ROOTFS)
        os.chdir(cwd)

    def run_vm(self):
        qemu_cmd = 'qemu-system-x86_64 -s -cpu host -smp cpus=2 -m 3G -nographic -enable-kvm \
                    -append "root=/dev/ram rdinit=/sbin/init console=ttyS0 nokaslr" \
                    -net nic,model=virtio \
                    -kernel %s/arch/x86/boot/bzImage -initrd %s ' % (KERNEL_DIR, ROOTFS)
        os.system(qemu_cmd)

    def execute(self, args):
        self.parse_args(args)
        if self.cleanrootfs:
            self.clean_rootfs()
        if self.cleankernel:
            self.clean_kernel()
        if self.clean:
            self.cleanup()
        if self.config:
            self.prepare_kernel_conf()
        if self.build:
            self.build_kernel()
        if self.fedora:
            self.install_fedora()
        if self.mods:
            self.install_modules()
        if self.rootfs:
            self.create_rootfs()
        if self.run:
            self.run_vm()

    Parser = property(get_parser)


if __name__ == '__main__':
    kdev().execute(sys.argv[1:])