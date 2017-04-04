#!/usr/bin/env python
import sys, os

def saveAllEnvVar(fname):
    import pickle
    f = open(fname, 'w')
    pickle.dump(os.environ, f)
    f.close()

def diffDict(d1, d2):
    result = {}
    for k,v2 in d2.iteritems():
        if k in d1:
            v1 = d1[k]
            if not v1==v2:
                result[k] = v2      # existing key is updated
        else:
            result[k] = v2          # new key added
    return result

def diffEnvVar(fname1, fname2):
    '''open environment variables stored in pickle files (fname1 and fname2),
    find out the difference from 1 to 2, and returns the difference as a dict.
    '''
    import pickle
    f1 = open(fname1)
    f2 = open(fname2)
    env1 = pickle.load(f1)
    env2 = pickle.load(f2)
    f1.close()
    f2.close()
    return diffDict(env1, env2)

def diffAlias(fname1, fname2, format='csh'):
    '''open CHS alias definitions stored in text files (fname1 and fname2),
    find out the difference from 1 to 2, and returns the difference as a dict.
    '''
    import re
    if format=='csh':
        reAlias = re.compile(r'(?P<name>[A-Za-z0-9_-]+)\s+(?P<value>.*)')
    else:
        reAlias = re.compile(r"alias (?P<name>[A-Za-z0-9_-]+)='(?P<value>.*)'")
    als1, als2 = {}, {}

    for fn,dAls in zip([fname1,fname2], [als1,als2]):
        f = open(fn)
        for line in f:
            match = reAlias.match(line)
            if match is None:
                continue
            match = match.groupdict()
            name = match['name'].strip()
            value = match['value'].strip()
            if value.startswith('('):
                value = value[1:-1] # remove the () at the beginning/end
            dAls[name] = value
    return diffDict(als1, als2)

def sourceScript(fnIn, format='csh', binShell=None):
    '''source the CSH/BASH script with the path fnIn,
    find out its changes to environment varaibles and aliases.
    '''
    import pickle, tempfile, subprocess, shutil

    dTMP = tempfile.mkdtemp()
    if format=='csh':
        fnScript = os.path.join(dTMP, 'do.csh')
        if binShell is None:
            binShell = '/bin/csh'
    elif format=='bash':
        fnScript = os.path.join(dTMP, 'do.sh')
        if binShell is None:
            binShell = '/bin/bash'
    else:
        raise ValueError

    # prepare the shell script to check environment variables and aliases
    # incidentally, this script works for both bash and csh
    script = '''#!{binShell}
{fnThis} -e {dTMP}/envBefore.pkl
alias >     {dTMP}/alsBefore.txt
source  {fnIn}
{fnThis} -e {dTMP}/envAfter.pkl
alias >     {dTMP}/alsAfter.txt
'''.format(fnThis=__file__,
           fnIn=os.path.abspath(fnIn),
           dTMP=dTMP,
           binShell=binShell,
           )
    fScript = open(fnScript, 'w')
    fScript.write(script)
    fScript.close()
    os.chmod(fnScript, 0755)

    #print 'xxxxxxxxxxxxxxxxxx', dTMP
    subprocess.check_call(fnScript, shell=True, executable=binShell)

    # difference in environment variables
    dEnv = diffEnvVar(os.path.join(dTMP, 'envBefore.pkl'),
                      os.path.join(dTMP, 'envAfter.pkl'),
                      )
    # difference in alias definitions
    dAls = diffAlias (os.path.join(dTMP, 'alsBefore.txt'),
                      os.path.join(dTMP, 'alsAfter.txt'),
                      format=format,
                      )
    shutil.rmtree(dTMP)
    return dEnv, dAls

def outputScript(dEnv, dAls, fnOut, format='bash'):
    def formatBash():
        fout.write('#!/bin/bash\n')
        for name,value in dEnv.iteritems():
            fout.write('export {name}="{value}"\n'.format(
                            name=name,
                            value=value,
                            ))
        for name,value in dAls.iteritems():
            fout.write('alias {name}="{value}"\n'.format(
                            name=name,
                            value=value,
                            ))
    def formatCsh():
        fout.write('#!/bin/csh\n')
        for name,value in dEnv.iteritems():
            fout.write("setenv {name} '{value}'\n".format(
                            name=name,
                            value=value,
                            ))
        for name,value in dAls.iteritems():
            fout.write('alias {name} {value}\n'.format(
                            name=name,
                            value=value,
                            ))

    if hasattr(fnOut, 'write'):
        fout = fnOut
        doClose = False
    else:
        fout = open(fnOut, 'w')
        doClose = True

    if format=='bash':
        formatBash()
    elif format=='csh':
        formatCsh()
    else:
        raise ValueError

    if doClose:
        fout.close()

def main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-e", "--env", dest="env",
                      help="export environment variables to FILE",
                      metavar="FILE")
    parser.add_option("-c", "--csh",    dest="csh",
                      help="source the csh script file SCRIPT",
                      metavar="SCRIPT")
    parser.add_option("-s", "--sh",    dest="sh",
                      help="source the bash script file SCRIPT",
                      metavar="SCRIPT")
    parser.add_option("-o", "--out",    dest="out",
                      help="write the converted output to file SCRIPT",
                      metavar="SCRIPT")
    (options, args) = parser.parse_args()

    if options.env is not None:
        fname = options.env
        saveAllEnvVar(fname)

    elif options.csh is not None:
        fname = options.csh
        dEnv, dAls = sourceScript(fname, format='csh')

        if options.out is not None:
            fname = options.out
            outputScript(dEnv, dAls, fname, format='bash')
        else:
            outputScript(dEnv, dAls, sys.stdout, format='bash')

    elif options.sh is not None:
        fname = options.sh
        dEnv, dAls = sourceScript(fname, format='bash')

        if options.out is not None:
            fname = options.out
            outputScript(dEnv, dAls, fname, format='csh')
        else:
            outputScript(dEnv, dAls, sys.stdout, format='csh')

if __name__=='__main__':
    main()
