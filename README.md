# Data-driven Infer Research

This repository is the official data-driven infer implementation of [Learning to Boost Disjunctive Static Bug-Finders (ICSE2023)](https://conf.researchr.org/details/icse-2023/icse-2023-artifact-evaluation/37/Learning-to-Boost-Disjunctive-Static-Bug-Finders).

## Installation Guides
In this installation guide, we use VirtualBox and Vagrant to replicate the experiments presented in the paper. However, these are not mandatory for running the data-driven Infer tool. You may also try building the artifact by following the [instructions](https://github.com/facebook/infer/blob/main/INSTALL.md).

### Requirements:
* CPU: 64-bit processor with at least an i686-class processor and 8 cores.
* 32Gb Memory
* 250Gb free disk space
* Virtualbox (>= 5.2)
* Vagrant (>= 2.2.14)

### Download a submodule
This repository uses a submodule to build the data-driven infer on top of the original Infer. Please make sure to download the submodule.
```bash
git submodule update --init
```

### Preparing the benchmark programs
* We provide [a pre-captured data and pre-trained models](http://prl.korea.ac.kr/~pronto/icse23-ddinfer-data.tar.gz) for the benchmark programs presented in our paper. 
```bash
wget http://prl.korea.ac.kr/~pronto/icse23-ddinfer-data.tar.gz
# Uncompress it on the root folder of this project.
tar zxvf icse23-ddinfer-data.tar.gz
```

### Building Instructions
* Initialize the virtual machine (creating a new VM, installing necessary packages, and compiling `infer`)
```bash
vagrant plugin install vagrant-disksize
vagrant up  # It may take a long time (>12hr)
```

## Getting Started
All the experiments must be done in the virtual machine.
```bash
vagrant ssh

# The pre-captured database must be located in its home folder:
cd /vagrant
cp -r infer-outs ~
```

### How to use Infer and DDInfer
We use the [two phases of an Infer run](https://fbinfer.com/docs/infer-workflow#the-two-phases-of-an-infer-run). 

**Infer and DDInfer**: Capture the target program.
```bash
# Run the following command in the target project folder.
$ infer capture -o "/home/vagrant/infer-outs/project_name" -- make
```

**Infer**: Run Infer to analyze the captured program:
```bash
$ infer analyze --pulse-only -o /home/vagrant/infer-outs/project_name
```

**DDInfer**: Run DDInfer to analyze the captured program with the best model `/vagrant/best_models`:
```bash
$ DDInfer.sh /home/vagrant/infer-outs/project_name
```

#### Example
After the "preparing the benchmark programs" step,
```bash
# Run the original infer
$ infer analyze --pulse-only -o /home/vagrant/infer-outs/openssl-3.1.0
# Run the DDInfer
$ DInfer.sh /home/vagrant/infer-outs/openssl-3.1.0
```

### Experiment results:
* [Table1](Table1)
* [Table2](Table2)
* [Table3](Table3)


## Troubleshooting
##### * `Uncaught Internal Error: ("IBase.SqliteUtils.Error(\"exec: synchronous=OFF: IOERR (disk I/O error) (disk I/O error)\")")`
The captured folder must be located in the VM local storage (`/home/vagrant/...`) due to a limitation of the database library that Infer uses.

##### * PyML dynamic library load issue
Sometimes PyML fails to load a dynamic library due to its heuristic algorithm to find the library path.
The algorithm is run the following command and use the path to load the dynamic library:
```bash
Printf.sprintf "python%d.%d-config --ldflags" version_major version_minor in
```

For example,
```bash
$ python3.9-config --ldflags
-L/path_name/config-3.9-darwin -ldl -framework CoreFoundation
```
Make sure that there exists a file `/path_name/config-3.9-darwin/libpython3.9.dylib`.

## License
Data-driven Infer is CC-BY-4.0 licensed, as found in the [LICENSE](LICENSE) file.
