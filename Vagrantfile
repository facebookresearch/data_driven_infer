# -*- mode: ruby -*-
# vi: set ft=ruby :

# Copyright (c) Meta, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

unless Vagrant.has_plugin?("vagrant-disksize")
    raise  Vagrant::Errors::VagrantError.new, "vagrant-disksize plugin is missing. Please install it using 'vagrant plugin install vagrant-disksize' and rerun 'vagrant up'"
end

Vagrant.configure("2") do |config|
  config.disksize.size = '200GB'
  config.ssh.insert_key = false
  config.vm.define "default" do |main|
    main.vm.box = "ubuntu/bionic64"
    main.vm.synced_folder ".", "/vagrant"

    main.vm.provider "virtualbox" do |vb|
      vb.memory = 16384  # recommended 16384
      vb.cpus = 4 # not recommended more than 4. 
      # When it uses more than 4 cpus, at 'Building native(opt) infer' stage, the compilation may take a long time.
      # In that case, just terminate the compilation, reduce the # of cpus to 4, and run "make opt" again.
    end

    main.vm.provision "shell", inline: <<-SHELL
    # swap file: 40Gb
    swapoff -a
    dd if=/dev/zero of=/swapfile bs=1G count=40
    swapon -s
    chmod 0600 /swapfile
    mkswap /swapfile
    swapon /swapfile

    apt-get update && \
        mkdir -p /usr/share/man/man1 && \
        apt-get install --yes --no-install-recommends \
          nodejs \
          autoconf \
          automake \
          bubblewrap \
          bzip2 \
          cmake \
          curl \
          chrony \
          g++ \
          gcc \
          git \
          libc6-dev \
          libgmp-dev \
          libmpfr-dev \
          libsqlite3-dev \
          make \
          openjdk-11-jdk-headless \
          patch \
          patchelf \
          pkg-config \
          python3.7 \
          libpython3.7 \
          python3-distutils \
          unzip \
          xz-utils \
          python3-pip \
          zlib1g-dev && \
        rm -rf /var/lib/apt/lists/*
    
    chronyd -q

    curl -sL https://github.com/ocaml/opam/releases/download/2.0.6/opam-2.0.6-x86_64-linux > /usr/bin/opam && \
        chmod +x /usr/bin/opam
    
    opam init --reinit --bare --disable-sandboxing --yes --auto-setup
    
    apt-get update && apt-get install --yes --no-install-recommends sqlite3

    update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1

    apt remove --purge --yes cmake
    hash -r
    snap install cmake --classic
  SHELL

  main.vm.provision "shell", privileged: false, inline: <<-SHELL
    python -m pip install --upgrade pip
    python -m pip install wheel Cython
    wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo python
    python -m pip install numpy sklearn scipy
    python -m pip install pandas
    python -m pip install xgboost matplotlib
    python -m pip install scikit-learn==0.24.2
    echo "export PATH=/home/vagrant/infer/infer/bin:\$PATH:/vagrant/bin:/home/vagrant/.local/bin" >> ~/.bashrc
    echo "export PROJECT_ROOT=/vagrant" >> ~/.bashrc

    # Prepare the infer source code
    pushd /home/vagrant
    git clone /vagrant/infer
    pushd infer

    # Apply a patch for the data-driven Infer
    git reset --hard 3df3ca9eacdf2e7a697b69a716896bbee7419a7a
    git apply /vagrant/patches/0001-ddinfer-Data-driven-Infer-Initial-commit.patch
    
    # infer compilation
    ./build-infer.sh --only-setup-opam

    eval $(opam env) && \
        ./autogen.sh && \
        ./configure --disable-java-analyzers && \
        ./facebook-clang-plugins/clang/setup.sh

    facebook-clang-plugins/clang/src/prepare_clang_src.sh

    # Generate a release
    make BUILD_MODE=opt \
         PATCHELF=patchelf \
         DESTDIR="/home/vagrant/infer/infer-release" \
         libdir_relative_to_bindir="../lib"

    source ~/.bashrc
  SHELL
  end
end
