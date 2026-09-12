// First-visit intro: a square sheet of paper is folded, one real fold per
// photo. Photos hard-cut every HOLD_MS. The flat sheet sits on the first
// photo; fold k plays over the first FOLD_MS of photo k+1's slot, so the
// model is finished on the last photo. It holds briefly, then the overlay
// fades out to reveal the page. The inline script in <head> sets
// html[data-intro="play"] when the page is opened fresh from outside the site
// or via the nav logo (never with reduced motion); reloads, back/forward and
// the site's own links play nothing.
//
// Fold data (#fold-data, JSON): steps[0] is the flat sheet; steps[k] lists
// every visible paper layer after fold k as {to, from|null, op}. Layers with
// `from` move during the step; interpolating from -> to sweeps a flap through
// its crease line, which is exactly how a fold looks from above.
(function () {
    var HOLD_MS = 200;
    var FOLD_MS = 190;
    var FINAL_HOLD_MS = 800;
    var LOAD_TIMEOUT_MS = 4000;

    var root = document.documentElement;
    if (root.dataset.intro !== 'play') return;

    var overlay = document.querySelector('.intro');
    var frames = Array.prototype.slice.call(document.querySelectorAll('.intro-frame'));
    var stage = document.querySelector('.intro-mark .fold-stage');
    var dataEl = document.getElementById('fold-data');
    var steps = [];
    try { steps = JSON.parse(dataEl.textContent).steps; } catch (e) {}

    var finished = false;
    function finish() {
        if (finished) return;
        finished = true;
        root.dataset.intro = 'done';
        // Take the overlay out of the page once it has faded. A full-screen
        // fixed element that stays in the layout keeps iOS Safari in its
        // collapsed-toolbar state, which leaves the page sitting shifted down
        // by the toolbar height until you scroll.
        var drop = function () {
            if (overlay && overlay.parentNode) overlay.parentNode.removeChild(overlay);
            try {
                root.style.scrollBehavior = 'auto';
                window.scrollTo(0, 0);
                root.style.scrollBehavior = '';
            } catch (e) {}
        };
        if (overlay) overlay.addEventListener('animationend', drop, { once: true });
        setTimeout(drop, 700);
    }
    if (!frames.length || !stage || !steps.length) return finish();

    frames.forEach(function (img) { img.src = img.dataset.src; });

    function whenVisible() {
        if (!document.hidden) return Promise.resolve();
        return new Promise(function (resolve) {
            document.addEventListener('visibilitychange', function onChange() {
                if (document.hidden) return;
                document.removeEventListener('visibilitychange', onChange);
                resolve();
            });
        });
    }

    function decodeAll() {
        var timeout;
        var decoded = Promise.all(frames.map(function (img) {
            return (img.decode ? img.decode() : Promise.resolve()).catch(function () {});
        }));
        var timedOut = new Promise(function (resolve, reject) {
            timeout = setTimeout(reject, LOAD_TIMEOUT_MS);
        });
        return Promise.race([decoded, timedOut]).then(function () { clearTimeout(timeout); });
    }

    // --- paper rendering
    var SVG = 'http://www.w3.org/2000/svg';
    var shown = -1;
    var polys = [];
    function pointsAt(layer, p) {
        var to = layer.to, from = layer.from, out = '';
        for (var i = 0; i < to.length; i++) {
            var x = to[i][0], y = to[i][1];
            if (from) { x = from[i][0] + (x - from[i][0]) * p; y = from[i][1] + (y - from[i][1]) * p; }
            out += x.toFixed(2) + ',' + y.toFixed(2) + ' ';
        }
        return out;
    }
    function ease(p) { return (1 - Math.cos(Math.max(0, Math.min(1, p)) * Math.PI)) / 2; }
    function render(k, p) {
        var step = steps[k];
        if (k !== shown) {
            while (stage.firstChild) stage.removeChild(stage.firstChild);
            polys = step.map(function (layer) {
                var el = document.createElementNS(SVG, 'polygon');
                el.setAttribute('fill-opacity', layer.op);
                stage.appendChild(el);
                return el;
            });
            shown = k;
        }
        for (var i = 0; i < step.length; i++) polys[i].setAttribute('points', pointsAt(step[i], p));
    }

    function roll() {
        var last = frames.length - 1;
        var lastStep = steps.length - 1;
        // Photo index -> fold step. With one more photo than folds the sheet
        // gets the first photo to itself; with equal counts fold 1 starts at once.
        var offset = Math.max(0, lastStep - last);
        var start = null;
        var current = -1;
        var ending = false;
        function showFrame(index) {
            if (index === current) return;
            if (current >= 0) frames[current].classList.remove('is-active');
            frames[index].classList.add('is-active');
            current = index;
        }
        function tick(now) {
            if (finished) return;
            if (start === null) start = now;
            var t = now - start;
            var index = Math.min(Math.floor(t / HOLD_MS), last);
            showFrame(index);
            var k = Math.min(index + offset, lastStep);
            render(k, ease((t - index * HOLD_MS) / FOLD_MS));
            if (index === last && !ending) {
                ending = true;
                setTimeout(finish, FINAL_HOLD_MS);
            }
            requestAnimationFrame(tick);
        }
        stage.parentNode.classList.add('is-live');
        requestAnimationFrame(tick);
    }

    whenVisible().then(decodeAll).then(roll, finish);
})();
