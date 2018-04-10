#!/usr/bin/env python
#coding: UTF-8

"""
Starts the seafile/seahub server and watches the controller process. It is
the entrypoint command of the docker container.
"""

import json
import os
from os.path import abspath, basename, exists, dirname, join, isdir
import shutil
import sys
import time

from utils import (
    call, get_conf, get_install_dir, get_script, get_command_output,
    render_template, wait_for_mysql
)
from upgrade import check_upgrade
from bootstrap import is_https, init_letsencrypt, generate_local_nginx_conf, init_seafile_server


shared_seafiledir = '/shared/seafile'
ssl_dir = '/shared/ssl'
generated_dir = '/bootstrap/generated'
installdir = get_install_dir()
topdir = dirname(installdir)

def watch_controller():
    maxretry = 4
    retry = 0
    while retry < maxretry:
        controller_pid = get_command_output('ps aux | grep seafile-controller | grep -v grep || true').strip()
        garbage_collector_pid = get_command_output('ps aux | grep /scripts/gc.sh | grep -v grep || true').strip()
        if not controller_pid and not garbage_collector_pid:
            retry += 1
        else:
            retry = 0
        time.sleep(5)
    print 'seafile controller exited unexpectedly.'
    sys.exit(1)

def prepare():
    call('. /etc/init.d/create_data_links.sh')
    call('. /etc/init.d/mysql_setup.sh')
    call('adduser -u 1000 --no-create-home www-data')
    call('chown www-data:www-data /var/lib/nginx -R')
    call('/etc/service/nginx/run &')
    call('/usr/bin/memcached -u root >> /var/log/memcached.log 2>&1 &')


def main():
    prepare()
    if not exists(shared_seafiledir):
        os.mkdir(shared_seafiledir)

    if is_https():
        init_letsencrypt()
    generate_local_nginx_conf()
    call('nginx -s reload')
    call('mysqld_safe &')

    wait_for_mysql()

    os.chdir(installdir)
    init_seafile_server()

    with open('/shared/seafile/ccnet/seafile.ini', 'w') as f:
        f.write('/opt/seafile/seafile-data')
    call('{} start'.format(get_script('seafile.sh')))
    call('{} start'.format(get_script('seahub.sh')))

    print 'seafile server is running now.'
    try:
        watch_controller()
    except KeyboardInterrupt:
        print 'Stopping seafile server.'
        sys.exit(0)

if __name__ == '__main__':
    main()
