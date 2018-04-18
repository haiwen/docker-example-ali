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
    render_template
)
from upgrade import check_upgrade
from bootstrap import is_https, init_letsencrypt, generate_local_nginx_conf, init_seafile_server


shared_seafiledir = '/shared/seafile'
ssl_dir = '/shared/ssl'
generated_dir = '/bootstrap/generated'
installdir = get_install_dir()
topdir = dirname(installdir)

def main():
    call('. /etc/init.d/create_data_links.sh')
    os.chdir(installdir)

    call('{} start'.format(get_script('seafile.sh')))
    call('{} start'.format(get_script('seahub.sh')))

    print 'seafile server is running now.'
    sys.exit(0)

if __name__ == '__main__':
    main()
