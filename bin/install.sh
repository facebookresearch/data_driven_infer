#!/bin/bash
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# 
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

# dns resolving issue
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf > /dev/null
sudo apt-get update

# for script and build
sudo apt-get install -y nodejs cloc npm  # npm conflicts with libcurl4-openssl-dev
sudo apt-get install -y libtool libtool-bin lzip

if [ ! -d ./bin/node_modules ];then
	pushd bin
	npm install
	popd
fi

sudo apt-get install -y gperf  # a2ps-4.14
sudo apt-get install -y libncurses5-dev  # aewan-1.0.01
sudo apt-get install -y libexpat-dev  # rnv-1.7.11
sudo apt-get install -y gnutls-dev  # wget-1.21.1
sudo apt-get install -y glib2.0 libdbus-1-dev libudev-dev libical-dev libreadline-dev  # bluez-5.55
sudo apt-get install -y docbook2x  # expat-2.2.10
sudo apt-get install -y libtalloc-dev libssl-dev  # freeradius-server-3.0.21
sudo apt-get install -y libapr1-dev libaprutil1-dev  # httpd-2.4.46
sudo apt-get install -y guile-2.2-dev  # patch-2.7.6, conflict with guile-2.0-dev
sudo apt-get install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libsdl2-gfx-dev cxxtest libglm-dev  # freedink-109.6
sudo apt-get install -y libgcrypt-dev  # freeipmi-1.6.6
sudo apt-get install -y liblcms2-dev  # gnu-ghostscript-9.14.1
sudo apt-get install -y gettext libtinfo-dev libacl1-dev libgpm-dev  # vim-8.2.2451
sudo apt-get install -y libgsl0-dev libcfitsio-dev wcslib-dev  # gnuastro-0.14
sudo apt-get install -y guile-2.0-dev freeglut3-dev libgtkglext1-dev  # gnubik-2.4.3
sudo apt-get install -y tcl-dev # sqlite-3.36.0

