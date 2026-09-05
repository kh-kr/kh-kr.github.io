/* Light/dark toggle.
 *
 * The research figures ship as two SVGs picked by a <picture> media query, so
 * an explicit theme choice has to override that query too: forcing a <source>
 * media to "all" or "not all" makes the browser re-pick without downloading
 * both variants. */
(function () {
    "use strict";

    var root = document.documentElement;
    var button = document.querySelector(".theme-toggle");
    var darkSources = document.querySelectorAll("picture source[data-dark]");
    var SYSTEM = "(prefers-color-scheme: dark)";

    function syncFigures(theme) {
        var media = theme === "dark" ? "all" : theme === "light" ? "not all" : SYSTEM;
        for (var i = 0; i < darkSources.length; i++) {
            darkSources[i].media = media;
        }
    }

    function stored() {
        try {
            return localStorage.getItem("theme");
        } catch (e) {
            return null;
        }
    }

    function apply(theme) {
        if (theme) {
            root.dataset.theme = theme;
        } else {
            delete root.dataset.theme;
        }
        syncFigures(theme);
        if (button) {
            button.setAttribute("aria-pressed", String(theme === "dark"));
        }
        try {
            if (theme) {
                localStorage.setItem("theme", theme);
            } else {
                localStorage.removeItem("theme");
            }
        } catch (e) { /* private mode: the choice just will not persist */ }
    }

    function prefersDark() {
        return window.matchMedia && window.matchMedia(SYSTEM).matches;
    }

    syncFigures(stored());

    if (button) {
        button.addEventListener("click", function () {
            var current = root.dataset.theme || (prefersDark() ? "dark" : "light");
            apply(current === "dark" ? "light" : "dark");
        });
    }
})();
