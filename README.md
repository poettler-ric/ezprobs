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
pip install --upgrade numpy
pip install --upgrade matplotlib
pip install --upgrade svgwrite

# only on windows
pip install --upgrade py2exe
```

## User directory

Install the needed packages:

``` shell
pip install --user --upgrade pip
pip install --user --upgrade flask
pip install --user --upgrade numpy
pip install --user --upgrade matplotlib
pip install --user --upgrade svgwrite

# only on windows
pip install --user --upgrade py2exe
```

# Build

The Windows executable is build with the following command:

``` shell
python setup.py py2exe
```

# Deploy

## Debian

``` shell
apt install nginx python3
apt install python3-flask python3-numpy python3-matplotlib python3-svgwrite
```

