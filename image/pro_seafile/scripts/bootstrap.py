#!/usr/bin/env python
#coding: UTF-8

"""
Bootstraping seafile server, letsencrypt (verification & cron job).
"""

import argparse
import os
from os.path import abspath, basename, exists, dirname, join, isdir
import shutil
import sys
import uuid
import time

from utils import (
    call, get_conf, get_install_dir, loginfo,
    get_script, render_template, get_seafile_version, eprint,
    cert_has_valid_days, get_version_stamp_file, update_version_stamp,
    wait_for_mysql, wait_for_nginx, read_version_stamp
)

seafile_version = get_seafile_version()
installdir = get_install_dir()
topdir = dirname(installdir)
shared_seafiledir = '/shared/seafile'
ssl_dir = '/shared/ssl'
generated_dir = '/bootstrap/generated'

def init_letsencrypt():
    loginfo('Preparing for letsencrypt ...')
    wait_for_nginx()

    if not exists(ssl_dir):
        os.mkdir(ssl_dir)

    domain = get_conf('server.hostname')
    context = {
        'ssl_dir': ssl_dir,
        'domain': domain,
    }
    render_template(
        '/templates/letsencrypt.cron.template',
        join(generated_dir, 'letsencrypt.cron'),
        context
    )

    ssl_crt = '/shared/ssl/{}.crt'.format(domain)
    if exists(ssl_crt):
        loginfo('Found existing cert file {}'.format(ssl_crt))
        if cert_has_valid_days(ssl_crt, 30):
            loginfo('Skip letsencrypt verification since we have a valid certificate')
            return

    loginfo('Starting letsencrypt verification')
    # Create a temporary nginx conf to start a server, which would accessed by letsencrypt
    context = {
        'https': False,
        'domain': domain,
    }
    render_template('/templates/seafile.nginx.conf.template',
                    '/etc/nginx/sites-enabled/seafile.nginx.conf', context)

    call('nginx -s reload')
    time.sleep(2)

    call('/scripts/ssl.sh {0} {1}'.format(ssl_dir, domain))
    # if call('/scripts/ssl.sh {0} {1}'.format(ssl_dir, domain), check_call=False) != 0:
    #     eprint('Now waiting 1000s for postmortem')
    #     time.sleep(1000)
    #     sys.exit(1)


def generate_local_nginx_conf():
    # Now create the final nginx configuratin
    domain = get_conf('server.hostname')
    context = {
        'https': is_https(),
        'domain': domain,
    }
    render_template(
        '/templates/seafile.nginx.conf.template',
        '/etc/nginx/sites-enabled/seafile.nginx.conf',
        context
    )


def is_https():
    return get_conf('server.letsencrypt', '').lower() == 'true'
