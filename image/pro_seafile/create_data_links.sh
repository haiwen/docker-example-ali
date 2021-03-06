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
    pro-data
)

for d in ${dirs[*]}; do
    if [[ ! -e /shared/seafile/$d ]]; then
        echo "No /shared/seafile/$d file was found."
        exit 0
    fi
    src=/opt/seafile/$d
    if [[ ! -e $src ]]; then
        ln -sf /shared/seafile/$d $src
    fi
done

options_dirs=(
    bootstrap.conf
    seafile-license.txt
)
for d in ${options_dirs[*]}; do
    src=/opt/seafile/$d
    if [[ ! -e $src ]]; then
        ln -sf /shared/seafile/$d $src
    fi
done


current_version_dir=/opt/seafile/seafile-pro-server-${SEAFILE_VERSION}
latest_version_dir=/opt/seafile/seafile-server-latest
seahub_data_dir=/shared/seafile/seahub-data
help_html_dir=/shared/help/html
help_img_dir=/shared/help/img

if [[ ! -e $latest_version_dir ]]; then
    ln -sf $current_version_dir $latest_version_dir
fi

source_avatars_dir=${current_version_dir}/seahub/media/avatars
rm -rf $source_avatars_dir
ln -sf ${seahub_data_dir}/avatars $source_avatars_dir

source_custom_dir=${current_version_dir}/seahub/media/custom
rm -rf $source_custom_dir
ln -sf ${seahub_data_dir}/custom $source_custom_dir

if [[ ! -e /shared/logs/seafile ]]; then
    mkdir -p /shared/logs/seafile
fi

if [[ -e $help_html_dir ]]; then
    seahub_help_dir=$latest_version_dir/seahub/seahub/help/templates/help
    rm -rf $seahub_help_dir
    ln -sf $help_html_dir $seahub_help_dir
fi

if [[ -e $help_img_dir ]]; then
    media_dir=$latest_version_dir/seahub/media/img/help/
    cp -f $help_img_dir/* $media_dir
fi

rm -rf /opt/seafile/logs && ln -sf /shared/logs/seafile /opt/seafile/logs
