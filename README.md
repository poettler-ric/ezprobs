# Prerequisites

## Environment

Create the environment:

``` shell
# create environment
python3 -m venv ~/pyenv/hydraulicstrainer
# activate environment
source ~/pyenv/hydraulicstrainer/bin/activate
```

And install the needed packages:

``` shell
pip install --upgrade pip
pip install --upgrade flask

# only on windows
pip install --upgrade py2exe
```

## User directory

Install the needed packages:

``` shell
pip install --user --upgrade pip
pip install --user --upgrade flask

# only on windows
pip install --user --upgrade py2exe
```

# Build

The Windows executable is build with the following command:

``` shell
python setup.py py2exe
```

