
(function () {
  "use strict";

  
  // Version query busts the 1-year immutable cache set in .htaccess when the
  // stylesheet changes.
  var ASSET_VERSION = "?v=20260924";
  var CSS_FILE     = "css/styles.css" + ASSET_VERSION;
  var FAVICON_FILE = "favicon.ico";
  // Self-hosted Font Awesome so the navbar / social / footer icons always render
  // (no CDN dependency, and every page uses the same icon version).
  var FONT_AWESOME = "assets/fontawesome/css/all.min.css" + ASSET_VERSION;

  var PARTIALS = {
    "navbar":         "partials/navbar.html",
    "footer":         "partials/footer.html"
  };

  var LAZY_CONFIG = {
    rootMargin: "200px 0px",
    threshold:  0.01
  };


  // Normalize paths only for active navigation highlighting.

  function cleanPath(path) {
    path = path.replace(/\/index\.html$/i, "");
    path = path.replace(/\/index$/i, "");
    if (path !== "/" && path.endsWith("/")) {
      path = path.slice(0, -1);
    }
    return path || "/";
  }

  // Preserve the browser's current URL so relative assets and links resolve
  // correctly on both custom domains and GitHub Pages project sites.

  function getBasePath() {
    var parts = location.pathname.split("/").filter(Boolean);
    if (location.hostname.endsWith("github.io") && parts.length > 0) {
      return "/" + parts[0] + "/";
    }
    return "/";
  }

  function buildPath(relativePath) {
    var base = getBasePath();
    return (base + relativePath.replace(/^\/+/, "")).replace(/\/+/g, "/");
  }


  function addFavicon() {
    if (document.querySelector("link[rel='icon']")) return;
    var link  = document.createElement("link");
    link.rel  = "icon";
    link.type = "image/x-icon";
    link.href = buildPath(FAVICON_FILE);
    document.head.appendChild(link);
  }

  function addGlobalCSS() {
    // Standalone pages (Timer, Sani) carry their own styles — never apply the site theme.
    if (document.documentElement.hasAttribute("data-standalone")) return;
    if (document.querySelector("link[data-global-css], link[href*='styles.css'], link[href*='styles.css?v=']")) return;
    var link  = document.createElement("link");
    link.rel  = "stylesheet";
    link.href = buildPath(CSS_FILE);
    link.setAttribute("data-global-css", "true");
    document.head.appendChild(link);
  }

  function addFontAwesome() {
    if (document.querySelector("link[data-font-awesome], link[href*='font-awesome'], link[href*='fontawesome'], link[href*='all.min.css']")) return;
    var link  = document.createElement("link");
    link.rel  = "stylesheet";
    link.href = buildPath(FONT_AWESOME);
    link.setAttribute("data-font-awesome", "true");
    document.head.appendChild(link);
  }


  async function loadSection(placeholderId, filePath) {
    var el = document.getElementById(placeholderId);
    if (!el) return;

    try {
      var resp = await fetch(buildPath(filePath));
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      el.innerHTML = await resp.text();
      // Partials use site-root paths; resolve them against the deployment base.
      el.querySelectorAll('a[href]').forEach(function (link) {
        var href = link.getAttribute('href');
        if (href && !/^(https?:|\/\/|#|mailto:|tel:|javascript:)/i.test(href)) {
          link.setAttribute('href', buildPath(href));
        }
      });
      // Mark the host element (but do not copy the component class onto it —
      // the partial already carries .navbar / .social-media / .footer and a
      // duplicated class would double up padding and backgrounds).
      el.classList.add("global-partial");
    } catch (err) {
      console.error("Failed to load partial '" + filePath + "':", err);
      el.classList.add("global-partial");
    }
  }


  function initNavbar() {
    var toggler = document.querySelector(".menu-toggle");
    var navMenu = document.querySelector(".nav-links");

    if (toggler && navMenu) {
      toggler.addEventListener("click", function () {
        navMenu.classList.toggle("show");
      });
    }

    var currentPath = cleanPath(location.pathname);
    var allLinks    = document.querySelectorAll(".nav-links a, .navbar a");

    for (var j = 0; j < allLinks.length; j++) {
      var href = allLinks[j].getAttribute("href");
      if (!href) continue;

      href = cleanPath(href);

      if (currentPath === href || (href !== "/" && currentPath.startsWith(href + "/"))) {
        allLinks[j].classList.add("active-link");
        allLinks[j].classList.add("active");
      }
    }
  }


  function initFooter() {
    var yearEl = document.getElementById("year");
    if (!yearEl) {
      // The footer partial could not be injected (offline / blocked fetch):
      // print a complete footer instead of leaving an empty strip at the bottom.
      var host = document.getElementById("footer");
      if (host && !host.querySelector(".footer")) {
        host.classList.add("global-partial", "footer");
        host.innerHTML =
          '<p>©<span id="year"></span> All rights reserved.<br>' +
          '<a href="' + buildPath("PrivacyPolicy.html") + '">Privacy Policy</a> | ' +
          '<a href="' + buildPath("TermsofService.html") + '">Terms of Service</a></p>';
      }
      yearEl = document.getElementById("year");
      if (!yearEl) return;
    }
    yearEl.textContent = new Date().getFullYear();
  }


  // Auto "Last updated" date — always shows the LAST DAY of the PREVIOUS month,
  // i.e. September 30 while it is October, then October 31 while it is November.
  // Any <time data-auto-date="previous-month-end"> element rolls over automatically
  // as the calendar month changes. Also keeps page JSON-LD dateModified in sync.

  function getPreviousMonthEndDates(now) {
    var lastDay = new Date(now.getFullYear(), now.getMonth(), 0);
    var mm = String(lastDay.getMonth() + 1);
    if (mm.length < 2) mm = "0" + mm;
    var dd = String(lastDay.getDate());
    if (dd.length < 2) dd = "0" + dd;
    var iso = lastDay.getFullYear() + "-" + mm + "-" + dd;
    var long = lastDay.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
    return { iso: iso, long: long };
  }

  function initAutoLastUpdated() {
    var dates;
    try {
      dates = getPreviousMonthEndDates(new Date());
    } catch (err) {
      return; // keep the static fallback text in the HTML
    }

    var times = document.querySelectorAll('time[data-auto-date="previous-month-end"]');
    for (var i = 0; i < times.length; i++) {
      times[i].setAttribute("datetime", dates.iso);
      times[i].textContent = dates.long;
    }

    var schemaEl = document.getElementById("page-schema");
    if (schemaEl) {
      try {
        var data = JSON.parse(schemaEl.textContent);
        data.dateModified = dates.iso;
        schemaEl.textContent = JSON.stringify(data);
      } catch (err) {
        // keep the static fallback JSON-LD
      }
    }
  }


  // Lazy loading — images, iframes, videos, background images, and HTML sections
  
  function initLazyLoading() {

    var mediaElements   = document.querySelectorAll("img.lazy, iframe.lazy, video.lazy");
    var sectionElements = document.querySelectorAll(".lazy-section[data-page]");
    var bgElements      = document.querySelectorAll(".lazy-bg[data-bg]");

    if (!("IntersectionObserver" in window)) {
      fallbackLoadAll(mediaElements, sectionElements, bgElements);
      return;
    }

    
    if (mediaElements.length) {
      var mediaObserver = new IntersectionObserver(function (entries, observer) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var el = entry.target;

          if (el.dataset.src)    { el.src    = el.dataset.src;    el.removeAttribute("data-src");    }
          if (el.dataset.srcset) { el.srcset = el.dataset.srcset; el.removeAttribute("data-srcset"); }

          el.addEventListener("load", function () { el.classList.add("loaded"); }, { once: true });
          observer.unobserve(el);
        });
      }, LAZY_CONFIG);

      mediaElements.forEach(function (el) { mediaObserver.observe(el); });
    }

    
    if (sectionElements.length) {
      var sectionObserver = new IntersectionObserver(function (entries, observer) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var section = entry.target;
          var pageURL = section.dataset.page;

          if (pageURL) {
            fetch(buildPath(pageURL))
              .then(function (resp) {
                if (!resp.ok) throw new Error("HTTP " + resp.status);
                return resp.text();
              })
              .then(function (html) {
                section.innerHTML = html;
                section.classList.add("loaded");
                fixAllLinks();
              })
              .catch(function () {
                section.innerHTML = "<p>Content unavailable.</p>";
              });
          }

          observer.unobserve(section);
        });
      }, LAZY_CONFIG);

      sectionElements.forEach(function (el) { sectionObserver.observe(el); });
    }

    
    if (bgElements.length) {
      var bgObserver = new IntersectionObserver(function (entries, observer) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var el = entry.target;

          if (el.dataset.bg) {
            el.style.backgroundImage = "url('" + el.dataset.bg + "')";
            el.removeAttribute("data-bg");
            el.classList.add("loaded");
          }

          observer.unobserve(el);
        });
      }, LAZY_CONFIG);

      bgElements.forEach(function (el) { bgObserver.observe(el); });
    }
  }

  
  function fallbackLoadAll(mediaEls, sectionEls, bgEls) {
    mediaEls.forEach(function (el) {
      if (el.dataset.src)    el.src    = el.dataset.src;
      if (el.dataset.srcset) el.srcset = el.dataset.srcset;
      el.classList.add("loaded");
    });

    sectionEls.forEach(function (section) {
      var pageURL = section.dataset.page;
      if (pageURL) {
        fetch(buildPath(pageURL))
          .then(function (resp) { return resp.text(); })
          .then(function (html) {
            section.innerHTML = html;
            section.classList.add("loaded");
          });
      }
    });

    bgEls.forEach(function (el) {
      if (el.dataset.bg) {
        el.style.backgroundImage = "url('" + el.dataset.bg + "')";
        el.classList.add("loaded");
      }
    });
  }


  document.addEventListener("DOMContentLoaded", async function () {
    addFavicon();
    addGlobalCSS();
    addFontAwesome();

    var keys     = Object.keys(PARTIALS);
    var promises = [];
    for (var i = 0; i < keys.length; i++) {
      promises.push(loadSection(keys[i], PARTIALS[keys[i]]));
    }
    await Promise.all(promises);

    initNavbar();
    initFooter();
    initAutoLastUpdated();
    initLazyLoading();
  });

})();
