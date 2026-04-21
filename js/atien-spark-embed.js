(function () {
  if (!window.ATIEN_API_KEY) {
    window.ATIEN_API_KEY = 'atien_e245c580f02e4704254a88f229ef8aba';
  }

  // Fallback chain for extracting the API key:
  // 0. window.ATIEN_API_KEY (pre-set by host page, or fetch()+new Function() bypass)
  // 1. document.currentScript (standard <script> tags)
  // 2. querySelector for script with embed.js in src (tag still in DOM)
  // 3. Search ALL script tags for src containing both "embed.js" and "key="
  //    (Next.js afterInteractive creates a new script element without query params,
  //     but the original tag may still exist elsewhere in the DOM)
  // 4. Check link[rel="preload"] tags (Next.js preloads scripts with original URL)
  // 5. data-api-key attribute on the found script tag

  var apiKey = window.ATIEN_API_KEY || null;
  var currentScript = document.currentScript || document.querySelector('script[src*="embed.js"]');

  // Extract key from script src query params
  if (currentScript && currentScript.src && currentScript.src.includes('key=')) {
    var urlParams = new URLSearchParams(currentScript.src.split('?')[1]);
    apiKey = urlParams.get('key');
  }

  // Fallback: search all script tags for one with both "embed.js" and "key=" in src
  if (!apiKey) {
    var scripts = document.querySelectorAll('script[src*="embed.js"][src*="key="]');
    for (var i = 0; i < scripts.length; i++) {
      var params = new URLSearchParams(scripts[i].src.split('?')[1]);
      var key = params.get('key');
      if (key) {
        apiKey = key;
        currentScript = scripts[i];
        break;
      }
    }
  }

  // Fallback: check preload link tags (Next.js preloads scripts with original URL)
  if (!apiKey) {
    var preloads = document.querySelectorAll('link[rel="preload"][href*="embed.js"][href*="key="]');
    for (var j = 0; j < preloads.length; j++) {
      var preloadParams = new URLSearchParams(preloads[j].href.split('?')[1]);
      var preloadKey = preloadParams.get('key');
      if (preloadKey) {
        apiKey = preloadKey;
        break;
      }
    }
  }

  // Fallback: data-api-key attribute on the script tag
  if (!apiKey && currentScript) {
    apiKey = currentScript.getAttribute('data-api-key');
  }

  // If no API key found, log error and don't load widget
  if (!apiKey) {
    console.error('Atien Spark Widget: API key is required. Please use: <script src="https://api.atien.co.uk/embed.js?key=YOUR_API_KEY"></script>');
    return;
  }

  // Store API key globally for widget to use
  window.ATIEN_API_KEY = apiKey;

  // Pre-fetch widget config in parallel with CSS/JS loading for faster theme application
  window.ATIEN_CONFIG_PROMISE = fetch('https://api.atien.co.uk/api/widget/config?key=' + apiKey)
    .then(function (r) { return r.json(); }).catch(function () { return null; });

  // Load widget CSS
  var cssLink = document.createElement('link');
  cssLink.rel = 'stylesheet';
  cssLink.href = 'https://api.atien.co.uk/widget.css';
  document.head.appendChild(cssLink);

  // Load widget JavaScript via fetch to bypass Termly resource blocker
  fetch('https://api.atien.co.uk/widget.js')
    .then(function (r) { return r.text(); })
    .then(function (code) { (new Function(code))(); })
    .catch(function (err) { console.error('Atien Spark Widget: Failed to load widget.js', err); });
})();
