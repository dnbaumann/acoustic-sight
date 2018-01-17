acoustic-sight
==============

Video [sonification](https://en.wikipedia.org/wiki/Sonification) scripts and tools inspired by sight-via-sound
[study](http://phy.ucsf.edu/~houde/coleman/sur2.pdf).

Only Python 3.4+ is supported.

Install
-------

First of all we suggest to create a virtual environment:

```bash
mkvirtualenv --python=`which python3` acoustic-sight
workon acoustic-sight
```

```bash
pip3 install -r requirements.txt
```

Since [supriya](https://github.com/josiah-wolf-oberholtzer/supriya) PyPI package is currently broken we suggest to
install it from sources as it [described in it's manual](http://supriya.mbrsi.org/installation.html).

### SuperCollider

Bu default we use [SuperCollider](http://supercollider.github.io/) which produce much smoother sound due to it's float
precision nature opposing to PyGame which is faster but at higher dimensions (> 8*8) produces noise.

OS X users can install SuperCollider by Homebrew Cask:

```sh
brew cask install supercollider
```

Don't forget to create a symlink to `scsynth` executable:

```sh
cd /usr/local/bin/
ln -s /Applications/SuperCollider.app/Contents/Resources/scsynth scsynth
```

Users with other operation systems can find a proper distribution on the [download page](http://supercollider.github.io/download).

### NumPy dependencies on Raspberry Pi

To use numpy ensure that you have:

```sh
sudo apt install libblas3 liblapack3
```

### PyGame

While PyGame requires:

```sh
sudo apt install python3-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsdl1.2-dev libsmpeg-dev subversion libportmidi-dev ffmpeg libswscale-dev libavformat-dev libavcodec-dev
```

### Node.JS

`SocketIO` RPiClient requires Node.js (you can avoid that by using `Direct` client mode):

```sh
curl -sL https://deb.nodesource.com/setup_9.x | sudo -E bash -
sudo apt install nodejs
```

Run
---

```sh
manage runserver
```

### Running via [Supervisor](http://supervisord.org/)

First of all, you should install Supervisor:

```sh
sudo apt-get install supervisor
```

Then create configuration file:

```sh
manage server_supervisor_conf [--args="arguments for server app>"]
```

For example to for direct connection to local RPiCamera you can configure it as:

```sh
manage server_supervisor_conf --args="--remote-host=127.0.0.1 --remote-port=80 --synth-type=PyGame --rpi-cam-client-type=Direct"
```

Copy it into Supervisor configuration directory:

```sh
sudo cp acoustic_sight_server-supervisor.conf /etc/supervisor/conf.d/acoustic_sight_server-supervisor.conf
```

And restart the service:

```sh
sudo service supervisor restart
```

Roadmap
-------

- [ ] Adjust maximum resolution (PyPeg fails on > 4, SuperCollider have to be tuned to process more synthdefs). 
- [ ] Look for more efficient ways of sound synthesis (optimize PyGame code by calculating patches manually, use other
      libraries/tools?). 
- [ ] Define different maps from pixel intensity to tone amplitude.
- [ ] Apply image filters (sharpness, contrast).
- [ ] Stream video from other sources (smartphones, webcams). 
- [ ] Record video (simpler) and audio (harder with SuperCollider).
- [ ] Adopt for Arduino (as a standalone or just use it as a source of videostream and audio output system).
- [ ] Port to iOS/Android.
