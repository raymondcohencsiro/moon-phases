# Phases of the Moon: interactive simulator

**Open it:** https://raymondcohencsiro.github.io/moon-phases/

An interactive 3D model of the Sun, Earth and Moon that shows why the Moon has phases.
It started from Oliver Cohen's (7D) school poster "Phases of the Moon".

It runs in any modern web browser on a computer, tablet or phone. On a VR headset
(e.g. Meta Quest 2 or 3), you can step inside the model. It also works offline and can be
installed as an app.

## What you can do

- **Watch a lunar month.** Press play, drag the slider, step day by day or jump to any of
  the eight phases. The square at the top right shows the Moon as someone on Earth sees it
  at that moment.
- **Drag the Moon** around its orbit and watch its phase change.
- **Northern or Southern Hemisphere.** The phase pictures flip (in the south, a waxing
  Moon is lit on the left). The main view also turns over to look up at the orbit from the
  south.
- **See the Earth from the Moon.** The Earth has phases too, always the opposite of the
  Moon's.
- **Real scale.** Shows true sizes and distances, with a zoom out to the Sun.
- **Tilted orbit and eclipses.** The Moon's orbit is tilted about 5° to the Earth's orbit,
  which is why there isn't an eclipse every month. Turn the tilt to see when New and Full
  Moons line up with the Sun, giving solar and lunar eclipses ("eclipse seasons", about
  every six months).
- **Quiz.** There are two kinds of question:
  - "Where must the Moon be to look like this?" Drag the Moon to the right spot.
  - "Which phase would we see from here?" Pick a phase.
- **VR.** On a headset, press **Enter VR** (top right of the 3D view). See the VR section
  below for the controls.

### Keyboard shortcuts

| Key | Action |
| --- | --- |
| Space | Play / pause |
| ← → | Step a day |
| Home | Back to New Moon |
| 1–8 | Jump to a phase (in the quiz: answer) |
| L | Loop on / off |
| V | View from Earth / from the Moon |
| H | Northern / Southern Hemisphere |
| E | Spin the Earth |
| C | Show the half of the Moon facing Earth |
| R | Real scale |
| O | Tilted orbit and eclipses |
| Q | Start / end the quiz |
| Z | Zoom to the Sun (real scale) |
| T, Esc | Reset the view |

Double-click the Sun, Earth or Moon to centre the view on it.

### VR controls

| Control | Action |
| --- | --- |
| Trigger | Press panel buttons; grab the Moon and move it |
| Grip | Move the whole model |
| Thumbstick ← → | Days backwards and forwards |
| Thumbstick ↑ ↓ | Make the model bigger or smaller |
| Thumbstick press, or **Recenter** on the panel | Bring the model in front of you at a comfortable height (sitting or standing) |

The panel shows the frame rate. If the view stutters, set **Quality** to Low (the default
in a headset).

## Offline and installing

The first visit stores everything the page needs. After that it works without internet.
On a Quest, use the browser's menu to **install** it as an app. On a phone or tablet, use
"Add to Home Screen".

The page itself is always fetched fresh when you're online, so updates show up straight
away. The build number is shown at the bottom of the left panel, and on the VR panel.

## How it's built

There is one source file, `src/index.html`: HTML, CSS and JavaScript using
[three.js](https://threejs.org/) 0.170. `build.py` turns it into two copies:

| Output | What it is |
| --- | --- |
| `index.html`, `assets/`, `vendor/`, `icons/`, `sw.js`, `manifest.webmanifest` (top level) | The website served by GitHub Pages: separate WebP images, a local copy of three.js, an offline service worker and an app manifest. |
| `dist/moon_phases.html` | A single self-contained file (images embedded, three.js from the jsDelivr CDN), for places that need one file, such as a claude.ai artifact. VR is blocked there, so it shows a link to the website instead. |

`vr/index.html` redirects the old `/vr/` address to the main page.

### Making a change

```sh
npm install                 # once: downloads three.js 0.170.0 into node_modules/
pip install pillow          # once: used to convert the images to WebP
# edit src/index.html (never the built index.html at the top level)
python3 build.py            # rebuilds the website and dist/moon_phases.html
```

Bump `BUILD_NO` in `build.py` for each release. This changes the build label and the
offline cache name, so browsers fetch the new files. To redraw the app icons, run
`python3 make_icons.py` (needs `pip install playwright` and `playwright install chromium`).

### Files

| Path | Contents |
| --- | --- |
| `src/index.html` | The simulator (all the code) |
| `src/sw.js` | Service worker template (offline support) |
| `src/assets/` | Source images (JPEG) and Natural Earth coastlines (`land.json`) |
| `src/icons/` | App icons (drawn by `make_icons.py`) |
| `build.py` | Builds the website and the single-file copy |

## Credits

- Idea and poster: Oliver Cohen (7D)
- Earth: NASA Blue Marble (public domain)
- Moon: [Solar System Scope](https://www.solarsystemscope.com/textures/), based on NASA
  data ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/))
- Coastlines: [Natural Earth](https://www.naturalearthdata.com/) (public domain)
- 3D: [three.js](https://threejs.org/) (MIT licence, copy included in `vendor/three/`)

## Notes on accuracy

- Not to scale (the default): the Moon is drawn much bigger and closer, and the orbit's
  tilt is drawn three times too big so you can see it. Real scale shows true sizes and
  distances.
- The eclipse calculations always use the real 5.1° tilt and real sizes. The Moon's orbit
  is treated as a circle, so they are approximate near the limits.
- The view from Earth is from latitude 35° (north or south) when the Moon is highest in
  the sky.
