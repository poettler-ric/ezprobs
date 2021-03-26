# Prerequisites

## Environment

Create the environment:

``` shell
# create environment
python3 -m venv ~/pyenv/ezprobs
# activate environment
source ~/pyenv/ezprobs/bin/activate
```

And install the needed packages:

``` shell
pip install --upgrade pip
pip install --upgrade flask
pip install --upgrade numpy
pip install --upgrade matplotlib
pip install --upgrade svgwrite
pip install --upgrade scipy
```

## User directory

Install the needed packages:

``` shell
pip install --user --upgrade pip
pip install --user --upgrade flask
pip install --user --upgrade numpy
pip install --user --upgrade matplotlib
pip install --user --upgrade svgwrite
pip install --user --upgrade scipy
```

# Deploy

## Debian

``` shell
apt install nginx python3
apt install python3-flask python3-numpy python3-matplotlib python3-svgwrite python3-scipy
```

