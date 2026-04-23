# -*- coding: utf-8 -*-
"""Custom branded Swagger UI HTML."""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

SWAGGER_CSS_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui.css"
SWAGGER_JS_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui-bundle.js"


def render_branded_docs(app: FastAPI, openapi_url: str, brand_css_url: str) -> HTMLResponse:
    title = app.title
    tagline = "Find the Vibe. <b>Go tonight.</b>"
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} — API</title>
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='%23A260FF'/><stop offset='1' stop-color='%23FF3BA7'/></linearGradient></defs><path d='M32 6c-10 0-18 8-18 18 0 13 18 34 18 34s18-21 18-34c0-10-8-18-18-18z' fill='url(%23g)'/><text x='32' y='32' font-family='Arial Black' font-size='20' text-anchor='middle' fill='white'>V</text></svg>" />
  <link rel="stylesheet" href="{SWAGGER_CSS_URL}">
  <link rel="stylesheet" href="{brand_css_url}">
</head>
<body>
  <header class="v2n-header">
    <h1 class="v2n-logo">VIBE<span class="v2n-2">2</span>NITE</h1>
    <p class="v2n-tagline">{tagline}</p>
    <div class="v2n-pills">
      <span class="v2n-pill primary">Real-Time Vibe Scores</span>
      <span class="v2n-pill pink">Top 3. Every Time.</span>
      <span class="v2n-pill teal">Bars · Clubs · Live Music</span>
      <span class="v2n-pill amber">Crowd Signals</span>
    </div>
  </header>

  <div id="swagger-ui"></div>

  <footer class="v2n-footer">
    <span><span class="dot"></span><b>VIBE2NITE API</b> · v1 · powered by FastAPI + Postgres</span>
    <span>© Vibe2Nite — Don't guess where to go. <b>Know.</b></span>
  </footer>

  <script src="{SWAGGER_JS_URL}"></script>
  <script>
    window.ui = SwaggerUIBundle({{
      url: "{openapi_url}",
      dom_id: "#swagger-ui",
      deepLinking: true,
      docExpansion: "list",
      defaultModelsExpandDepth: 1,
      tryItOutEnabled: true,
      syntaxHighlight: {{ theme: "obsidian" }},
    }});
  </script>
</body>
</html>"""
    return HTMLResponse(html)
