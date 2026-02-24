"""
CSS stylesheet for the rendered HTML preview.
Uses CSS custom properties + @media (prefers-color-scheme) for automatic
light/dark theme following — no hardcoded theme selection.
"""


def ucitaj_css() -> str:
    """Return the full HTML <style> block for the preview."""
    return """
    <style>
        /* ── CSS custom properties ─────────────────────────── */
        :root {
            /* GitHub Light defaults */
            --bg:               #ffffff;
            --bg2:              #f6f8fa;
            --fg:               #24292f;
            --fg-muted:         #57606a;
            --border:           #d0d7de;
            --link:             #0969da;
            --pre-bg:           #f6f8fa;
            --code-bg:          rgba(175,184,193,0.2);
            --heading:          #24292f;
            --blockquote-border:#d0d7de;
            --hr:               #d0d7de;
            --table-header:     #f6f8fa;
            --table-border:     #d0d7de;
            --mark-bg:          rgba(255,229,100,0.5);
            --mark-fg:          #24292f;
            --kbd-bg:           #f6f8fa;
            --kbd-border:       #d0d7de;
            --kbd-fg:           #24292f;
            --adm-note-bg:      rgba(9,105,218,0.1);
            --adm-note-border:  #0969da;
            --adm-warn-bg:      rgba(154,103,0,0.1);
            --adm-warn-border:  #9a6700;
            --adm-danger-bg:    rgba(207,34,46,0.1);
            --adm-danger-border:#cf222e;
            --adm-tip-bg:       rgba(26,127,55,0.1);
            --adm-tip-border:   #1a7f37;
            --toc-bg:           #f6f8fa;
            --splitter-bg:      #d0d7de;
            --splitter-hover:   #0969da;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --bg:               #0d1117;
                --bg2:              #161b22;
                --fg:               #e6edf3;
                --fg-muted:         #8b949e;
                --border:           #30363d;
                --link:             #58a6ff;
                --pre-bg:           #161b22;
                --code-bg:          rgba(110,118,129,0.4);
                --heading:          #ffffff;
                --blockquote-border:#3d444d;
                --hr:               #3d444d;
                --table-header:     #161b22;
                --table-border:     #3d444d;
                --mark-bg:          rgba(187,128,9,0.4);
                --mark-fg:          #c9d1d9;
                --kbd-bg:           #21262d;
                --kbd-border:       #30363d;
                --kbd-fg:           #c9d1d9;
                --adm-note-bg:      rgba(88,166,255,0.1);
                --adm-note-border:  #58a6ff;
                --adm-warn-bg:      rgba(210,153,34,0.1);
                --adm-warn-border:  #d29922;
                --adm-danger-bg:    rgba(248,81,73,0.1);
                --adm-danger-border:#f85149;
                --adm-tip-bg:       rgba(63,185,80,0.1);
                --adm-tip-border:   #3fb950;
                --toc-bg:           #161b22;
                --splitter-bg:      #30363d;
                --splitter-hover:   #58a6ff;
            }
        }

        /* ── Reset and base ─────────────────────────────────── */
        * { box-sizing: border-box; color-scheme: light dark; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica,
                         Arial, sans-serif;
            font-size: 16px;
            line-height: 1.6;
            word-wrap: break-word;
            background-color: var(--bg);
            color: var(--fg);
            padding: 32px;
            max-width: 980px;
            margin: 0 auto;
        }

        /* ── Headings ───────────────────────────────────────── */
        h1, h2, h3, h4, h5, h6 {
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
            color: var(--heading);
        }
        h1 { font-size: 2em;    border-bottom: 1px solid var(--border); padding-bottom: .3em; }
        h2 { font-size: 1.5em;  border-bottom: 1px solid var(--border); padding-bottom: .3em; }
        h3 { font-size: 1.25em; }
        h4 { font-size: 1em; }

        /* ── Paragraphs and text ────────────────────────────── */
        p  { margin-top: 0; margin-bottom: 16px; }
        a  { color: var(--link); text-decoration: none; }
        a:hover { text-decoration: underline; }
        strong { font-weight: 600; }
        em { font-style: italic; }

        /* ── Code ───────────────────────────────────────────── */
        code {
            padding: .2em .4em;
            margin: 0;
            font-size: 85%;
            background-color: var(--code-bg);
            border-radius: 6px;
            font-family: 'SF Mono', 'Fira Code', Consolas, monospace;
        }
        pre {
            padding: 16px;
            overflow: auto;
            font-size: 85%;
            line-height: 1.45;
            background-color: var(--pre-bg);
            border-radius: 6px;
            border: 1px solid var(--border);
        }
        pre code {
            padding: 0;
            margin: 0;
            background-color: transparent;
            border: none;
        }

        /* ── Blockquote ─────────────────────────────────────── */
        blockquote {
            padding: 0 1em;
            color: var(--fg-muted);
            border-left: .25em solid var(--blockquote-border);
            margin: 0 0 16px 0;
        }

        /* ── Lists ──────────────────────────────────────────── */
        ul, ol { padding-left: 2em; margin-top: 0; margin-bottom: 16px; }
        li { margin-top: 4px; }
        li + li { margin-top: 4px; }

        /* Task lists */
        .task-list-item { list-style-type: none; }
        .task-list-item input[type="checkbox"] {
            margin-right: 8px;
            margin-left: -1.5em;
        }

        /* ── Images ─────────────────────────────────────────── */
        img { max-width: 100%; height: auto; }

        /* ── Tables ─────────────────────────────────────────── */
        table {
            border-spacing: 0;
            border-collapse: collapse;
            margin-bottom: 16px;
            width: 100%;
            display: block;
            overflow: auto;
        }
        table th, table td { padding: 6px 13px; border: 1px solid var(--table-border); }
        table th { font-weight: 600; background-color: var(--table-header); }
        table tr { background-color: var(--bg); border-top: 1px solid var(--border); }
        table tr:nth-child(2n) { background-color: var(--bg2); }

        /* ── Horizontal rule ────────────────────────────────── */
        hr {
            height: .25em;
            padding: 0;
            margin: 24px 0;
            background-color: var(--hr);
            border: 0;
        }

        /* ── Admonitions ────────────────────────────────────── */
        .admonition {
            padding: 12px 16px;
            margin-bottom: 16px;
            border-left: 4px solid;
            border-radius: 4px;
        }
        .admonition.note    { background-color: var(--adm-note-bg);   border-color: var(--adm-note-border); }
        .admonition.warning { background-color: var(--adm-warn-bg);   border-color: var(--adm-warn-border); }
        .admonition.danger  { background-color: var(--adm-danger-bg); border-color: var(--adm-danger-border); }
        .admonition.tip     { background-color: var(--adm-tip-bg);    border-color: var(--adm-tip-border); }
        .admonition-title { font-weight: 600; margin-bottom: 4px; }

        /* ── Definition Lists ───────────────────────────────── */
        dt { font-weight: 600; margin-top: 16px; }
        dd { margin-left: 2em; margin-bottom: 16px; }

        /* ── Footnotes ──────────────────────────────────────── */
        .footnote { font-size: 0.875em; color: var(--fg-muted); }
        .footnote-ref { text-decoration: none; }

        /* ── Strikethrough ──────────────────────────────────── */
        del { text-decoration: line-through; color: var(--fg-muted); }

        /* ── Mark / Highlight ───────────────────────────────── */
        mark {
            background-color: var(--mark-bg);
            color: var(--mark-fg);
            padding: 2px 4px;
            border-radius: 2px;
        }

        /* ── Keyboard keys ──────────────────────────────────── */
        kbd {
            background-color: var(--kbd-bg);
            border: 1px solid var(--kbd-border);
            border-bottom-color: var(--kbd-border);
            border-radius: 6px;
            box-shadow: inset 0 -1px 0 var(--kbd-border);
            padding: 3px 6px;
            font-family: 'SF Mono', Consolas, monospace;
            font-size: 11px;
            color: var(--kbd-fg);
        }

        /* ── Syntax Highlighting — GitHub Dark (base) ────────── */
        .highlight { background-color: var(--pre-bg); border-radius: 6px; }
        .highlight pre { margin: 0; background-color: transparent; border: none; }
        .highlight .hll { background-color: #21262d; }
        .highlight .c, .highlight .ch, .highlight .cm, .highlight .cpf,
        .highlight .c1, .highlight .cs { color: #8b949e; font-style: italic; }
        .highlight .k, .highlight .kc, .highlight .kd, .highlight .kn,
        .highlight .kp, .highlight .kr, .highlight .kt { color: #ff7b72; }
        .highlight .o, .highlight .ow { color: #ff7b72; }
        .highlight .p { color: #c9d1d9; }
        .highlight .n, .highlight .nb, .highlight .nc, .highlight .no,
        .highlight .nd, .highlight .ni, .highlight .ne, .highlight .nf,
        .highlight .nl, .highlight .nn, .highlight .nt, .highlight .nv { color: #c9d1d9; }
        .highlight .na { color: #79c0ff; }
        .highlight .nc { color: #f0883e; }
        .highlight .nf, .highlight .fm { color: #d2a8ff; }
        .highlight .s, .highlight .sa, .highlight .sb, .highlight .sc,
        .highlight .dl, .highlight .sd, .highlight .s2, .highlight .se,
        .highlight .sh, .highlight .si, .highlight .sx, .highlight .sr,
        .highlight .s1, .highlight .ss { color: #a5d6ff; }
        .highlight .m, .highlight .mb, .highlight .mf, .highlight .mh,
        .highlight .mi, .highlight .mo, .highlight .il { color: #79c0ff; }
        .highlight .bp { color: #79c0ff; }
        .highlight .vc, .highlight .vg, .highlight .vi, .highlight .vm { color: #ffa657; }
        .highlight .err { color: #f85149; }

        /* ── Syntax Highlighting overrides for Light theme ───── */
        @media (prefers-color-scheme: light) {
            .highlight .hll { background-color: #eac55f; }
            .highlight .c, .highlight .ch, .highlight .cm, .highlight .cpf,
            .highlight .c1, .highlight .cs { color: #6e7781; font-style: italic; }
            .highlight .k, .highlight .kc, .highlight .kd, .highlight .kn,
            .highlight .kp, .highlight .kr, .highlight .kt { color: #cf222e; }
            .highlight .o, .highlight .ow { color: #cf222e; }
            .highlight .p { color: #24292f; }
            .highlight .n, .highlight .nb, .highlight .no,
            .highlight .nd, .highlight .ni, .highlight .ne,
            .highlight .nl, .highlight .nn, .highlight .nt, .highlight .nv { color: #24292f; }
            .highlight .na { color: #0550ae; }
            .highlight .nc { color: #953800; }
            .highlight .nf, .highlight .fm { color: #8250df; }
            .highlight .s, .highlight .sa, .highlight .sb, .highlight .sc,
            .highlight .dl, .highlight .sd, .highlight .s2, .highlight .se,
            .highlight .sh, .highlight .si, .highlight .sx, .highlight .sr,
            .highlight .s1, .highlight .ss { color: #0a3069; }
            .highlight .m, .highlight .mb, .highlight .mf, .highlight .mh,
            .highlight .mi, .highlight .mo, .highlight .il { color: #0550ae; }
            .highlight .bp { color: #0550ae; }
            .highlight .vc, .highlight .vg, .highlight .vi, .highlight .vm { color: #953800; }
            .highlight .err { color: #cf222e; }
        }

        /* ── Line numbers ───────────────────────────────────── */
        .linenodiv { padding-right: 10px; color: var(--fg-muted); border-right: 1px solid var(--border); }
        .linenodiv pre { background: transparent; border: none; }

        /* ── Emoji ──────────────────────────────────────────── */
        .emoji, .gemoji { font-size: 1.2em; vertical-align: middle; }

        /* ── TOC ────────────────────────────────────────────── */
        .toc {
            background-color: var(--toc-bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 16px;
            margin-bottom: 16px;
        }
        .toc ul { list-style-type: none; padding-left: 1em; }
        .toc > ul { padding-left: 0; }
    </style>
    """
