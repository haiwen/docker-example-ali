#!/bin/bash

set -e 
set -o pipefail

if [[ $SEAFILE_BOOTSRAP != "" ]]; then
    exit 0
fi

dirs=(
    conf
    ccnet
    seafile-data
    seahub-data
    bootstrap.conf
    pro-data
)

for d in ${dirs[*]}; do
    src=/shared/seafile/$d
    if [[ -e $src ]]; then
        ln -sf $src /opt/seafile
    fi
done


current_version_dir=/opt/seafile/seafile-pro-server-${SEAFILE_VERSION}
latest_version_dir=/opt/seafile/seafile-server-latest
seahub_data_dir=/shared/seafile/seahub-data

if [[ -e /shared/license.txt ]]; then
    cp -f /shared/seafile-license.txt /opt/seafile/seafile-license.txt
fi

#if [[ ! -e $latest_version_dir ]]; then
#    ln -sf $current_version_dir $latest_version_dir
#fi

if [[ ! -e $seahub_data_dir ]]; then
    mkdir -p $seahub_data_dir
fi
source_avatars_dir=${current_version_dir}/seahub/media/avatars
if [[ ! -e ${seahub_data_dir}/avatars ]]; then
    mv $source_avatars_dir ${seahub_data_dir}/avatars
fi
rm -rf $source_avatars_dir && ln -sf ${seahub_data_dir}/avatars $source_avatars_dir

source_custom_dir=${current_version_dir}/seahub/media/custom
rm -rf $source_custom_dir
if [[ ! -e ${seahub_data_dir}/custom ]]; then
    mkdir -p ${seahub_data_dir}/custom
fi
rm -rf $source_custom_dir && ln -sf ${seahub_data_dir}/custom $source_custom_dir

if [[ ! -e /shared/logs/seafile ]]; then
    mkdir -p /shared/logs/seafile
fi
rm -rf /opt/seafile/logs && ln -sf /shared/logs/seafile /opt/seafile/logs


if [[ ! -e /shared/logs/var-log ]]; then
    mv /var/log /shared/logs/var-log
fi
rm -rf /var/log && ln -sf /shared/logs/var-log /var/log

nginxconf=/etc/nginx/sites-enabled
if [[ ! -e $nginxconf ]]; then
    mkdir -p $nginxconf
fi
