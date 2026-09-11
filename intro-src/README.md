# Intro source

The homepage intro folds a square sheet of paper into an origami model, one real fold per photo. The fold geometry is generated here and embedded into `index.html` as JSON (`#fold-data`); `intro.js` animates it.

Three models are kept. **dart** is the one currently installed.

| Model | File | Finale |
| --- | --- | --- |
| dart | `dart.py` | classic paper dart, turns nose-right at the half-fold |
| delta | `delta.py` | swept delta wing, turns nose-right at the half-fold |
| crane | `crane.py` | traditional crane, wings open at the end |

## Switching the model

```
python3 intro-src/<model>.py intro-src/<model>.json   # regenerate the fold data
python3 intro-src/install.py <model>                  # write it into index.html / intro.js / styles.css
```

`install.py` only touches the intro block; the page content is left alone. The nav logo is a separate silhouette (`gen_logo.py <model>.json` prints it) that lives inline in every page's `<a class="nav-logo">`, so switch that by hand if you change the model.

## Checking a model

```
python3 intro-src/render_fold.py intro-src/<model>.json /tmp/<model>-steps.png
```

renders every step three times (start of the fold, mid-fold, finished) so you can see each fold read.

## How a model is written

`engine.py` has the pieces: a step is the list of visible paper layers after that fold, each with its polygon, its sheet count (rendered as opacity), and where it moved from. Interpolating from → to sweeps a flap through its crease line, which is the top-down view of paper turning over. `recenter()` keeps the model centred on screen as the folds shift its balance. Read `crane.py` first; it comments every technique.
