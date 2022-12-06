# bd-iptool

## Install guide
### Clone/download the project
Open a terminal and navigate to where you want to put the files,
recommended location is in your home folder (so where the terminal opens by default).
Then, simply run:

    git clone https://github.com/boldi-kdg/bd-iptool.git

Enter the directory that git created:

    cd bd-iptool

### Make sure python3 is installed
This tool requires the python3 interpreter to run, make sure it is installed by running:

    python3

If you see an interactive prompt python is installed, just exit:

    >>> exit()

Otherwise:
- On **Windows**: Microsoft Store should open for you and you can just install it from there.  
- On **Linux**: You should automatically receive the command to install it with.  

## How to run
Open the terminal inside the bd-iptool directory or navigate there via _cd_, then:

    python3 bd-iptool.py -h

alternatively on **Linux**:

    ./bd-iptool.py -h

**You should receive the following output:**

    usage: bd-iptool.py [-h] [-v] {convert,subnet} ...
    
    A tool for working with IP adresses. Certifiably better than a KdG calculator.*
    
    positional arguments:
      {convert,subnet}
    
    options:
      -h, --help        show this help message and exit
      -v, --version     show program's version number and exit

## How to use
To see all the currently available subcommands run:

    python3 bd-iptool.py -h

To see subcommand specific help:

    python3 bd-iptool.py <subcommand> -h

_If you seem to be missing some subcommands or they show a different help message,  
check what version of the program you have installed with:_

    python3 bd-iptool.py -v

