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

### Raspberry Pi

For lite version of Raspbian ensure that you have:

```sh
sudo apt-get install libblas3 liblapack3
```

Run
---

```bash
./acoustic_sight/webcam.py
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
