# Source csh scripts in bash

## Objectives

Many 3rd party software in Linux come with environment setup scripts,
which typically detect OS platform and version, and set up environment
variables and shell aliases.

Traditionally, csh is popular among EDA software users and a lot of
environment setup scripts were written in csh.
Although bash has long become the de facto shell in most Linux distros,
and csh considered archaic, many legacy csh scripts survived today.

This little script attempts to allow bash users to source legacy environment
setup scripts written in csh.
Conversely, it allows old-school csh users to source environment setup
scripts written in bash.

## Usage

The following script reads an `.csh` script and
write a `.sh` script that produces the same environment.
```
$ ./sourceAny.py -c "/sw/intel/bin/iccvars.csh intel64" -o ./setenv.sh
$ source ./setenv.sh
$ icc hello.c
```

The following script does the trick in the other direction.
```
% ./sourceAny.py -s "/opt/cogenda/current/bin/setenv.sh" -o ./setenv.csh
% source ./setenv.csh
% VisualTCAD
```

To list all available options, type
```
$ ./sourceAny.py -h
```

## How it works

- Save all environment variables, source the input script, save all
environment variables again.
- Compare the environment variables before and after.
- Write a script in the output format that produces the equivalent changes.
- Tada

## Limitations

Many. Your mileages vary. Patch welcomed.
