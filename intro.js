// First-visit photo intro: hard cuts every HOLD_MS, a short hold on the last
// frame, then the overlay fades out to reveal the page. The inline script in
// <head> sets html[data-intro="play"] only on the first load in a tab when
// arriving from outside the site (and never with reduced motion); otherwise
// the overlay stays hidden.
(function () {
    var HOLD_MS = 200;
    var FINAL_HOLD_MS = 700;
    var LOAD_TIMEOUT_MS = 4000;

    var root = document.documentElement;
    if (root.dataset.intro !== 'play') return;

    var frames = Array.prototype.slice.call(document.querySelectorAll('.intro-frame'));
    var finished = false;
    function finish() {
        if (finished) return;
        finished = true;
        root.dataset.intro = 'done';
    }
    if (!frames.length) return finish();

    // Frames load only when the intro plays (data-src), so repeat visits don't
    // download them.
    frames.forEach(function (img) { img.src = img.dataset.src; });

    // Background tabs pause requestAnimationFrame and can stall image decoding,
    // so the load timeout and the roll only start once the tab is on screen.
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

    // Every frame must be decoded before the first cut, or a 200ms slot shows a blank.
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

    function roll() {
        var last = frames.length - 1;
        var start = null;
        var current = -1;
        function show(index) {
            if (index === current) return;
            if (current >= 0) frames[current].classList.remove('is-active');
            frames[index].classList.add('is-active');
            current = index;
        }
        function tick(now) {
            if (start === null) start = now;
            var index = Math.floor((now - start) / HOLD_MS);
            if (index >= last) {
                show(last);
                setTimeout(finish, FINAL_HOLD_MS);
                return;
            }
            show(index);
            requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    }

    whenVisible().then(decodeAll).then(roll, finish);
})();
