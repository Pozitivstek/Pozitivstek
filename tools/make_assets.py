"""Генерирует SVG для профиля GitHub: баннер с «печатающимся» текстом, терминал и разделитель.

Запуск из корня репозитория:  python3 tools/make_assets.py
Всё самодостаточно (без внешних шрифтов и сервисов), анимация — SMIL, работает в <img> на GitHub."""
import math
import random
from html import escape
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
BG, LIME, CYAN, VIOLET, TEXT, MUTED = "#07080c", "#b8ff4a", "#3de0ff", "#8b5cff", "#e9edf4", "#98a1b3"
CHAR_W = 0.6   # ширина символа моноширинного шрифта в долях размера


def sphere_dots(cx: float, cy: float, radius: float, count: int, yaw: float, pitch: float) -> str:
    rng = random.Random(2026)
    golden = math.pi * (3 - math.sqrt(5))
    colors = [LIME, CYAN, VIOLET]
    out = []
    for i in range(count):
        y = 1 - (i / (count - 1)) * 2
        ring = math.sqrt(1 - y * y)
        a = golden * i
        x, z = math.cos(a) * ring, math.sin(a) * ring
        x1 = x * math.cos(yaw) + z * math.sin(yaw)
        z1 = -x * math.sin(yaw) + z * math.cos(yaw)
        y2 = y * math.cos(pitch) - z1 * math.sin(pitch)
        z2 = y * math.sin(pitch) + z1 * math.cos(pitch)
        p = 3.2 / (3.2 + z2)
        depth = (z2 + 1) / 2                                    # 0 — ближе, 1 — дальше
        color = colors[0] if rng.random() < 0.5 else colors[1] if rng.random() < 0.7 else colors[2]
        opacity = round(0.95 - depth * 0.72, 2)
        size = round(0.7 + p * 1.1, 2)
        px, py = round(cx + x1 * p * radius, 1), round(cy + y2 * p * radius, 1)
        if rng.random() < 0.16:
            dur = round(rng.uniform(2.2, 4.6), 1)
            begin = round(rng.uniform(0, 4), 1)
            twinkle = (f'<animate attributeName="opacity" values="{opacity};{min(1, opacity + 0.05)};'
                       f'0.12;{opacity}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>')
            out.append(f'<circle cx="{px}" cy="{py}" r="{size}" fill="{color}" opacity="{opacity}">{twinkle}</circle>')
        else:
            out.append(f'<circle cx="{px}" cy="{py}" r="{size}" fill="{color}" opacity="{opacity}"/>')
    return "\n".join(out)


def typing(clip_id: str, x: float, y: float, size: int, text: str, begin: float, per_char: float,
           fill: str, prefix: str = "") -> tuple[str, str, float]:
    """Текст, открываемый ступенчато слева направо, и курсор. Возвращает (defs, body, время окончания)."""
    step = size * CHAR_W
    total = len(text) + len(prefix)
    widths = [round(step * i, 1) for i in range(total + 1)]
    widths[-1] += 12                                            # запас на другой шрифт
    times = [round(i / total, 4) for i in range(total + 1)]
    dur = round(total * per_char, 2)
    cursor_x = [round(x + step * i, 1) for i in range(total + 1)]
    values = ";".join(str(w) for w in widths)
    key_times = ";".join(str(t) for t in times)
    xs = ";".join(str(c) for c in cursor_x)
    defs = (f'<clipPath id="{clip_id}"><rect x="{x}" y="{y - size}" height="{round(size * 1.4)}" width="0">'
            f'<animate attributeName="width" values="{values}" keyTimes="{key_times}" calcMode="discrete" '
            f'dur="{dur}s" begin="{begin}s" fill="freeze"/></rect></clipPath>')
    pre = f'<tspan fill="{LIME}">{escape(prefix)}</tspan>' if prefix else ""
    body = (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" fill="{fill}" '
            f'clip-path="url(#{clip_id})" xml:space="preserve">{pre}{escape(text)}</text>\n'
            f'<rect y="{y - size + 4}" width="{round(size * 0.5)}" height="{round(size * 1.05)}" fill="{LIME}" opacity="0">'
            f'<set attributeName="opacity" to="1" begin="{begin}s" dur="{dur}s"/>'
            f'<animate attributeName="x" values="{xs}" keyTimes="{key_times}" calcMode="discrete" '
            f'dur="{dur}s" begin="{begin}s" fill="freeze"/>'
            f'</rect>')
    return defs, body, begin + dur


def banner() -> str:
    w, h = 1280, 340
    sub = "Telegram bots · Websites · AI products"
    defs1, line1, end1 = typing("t1", 80, 232, 34, "Python & Full-Stack developer", 0.5, 0.05, TEXT)
    defs2, line2, end2 = typing("t2", 80, 284, 22, sub, end1 + 0.3, 0.04, CYAN, prefix="> ")
    cursor_x = round(80 + 22 * CHAR_W * (len(sub) + 2), 1)
    blink = (f'<rect x="{cursor_x}" y="{284 - 22 + 4}" width="11" height="23" fill="{LIME}" opacity="0">'
             f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.01;0.5;0.51" dur="1s" '
             f'begin="{round(end2, 2)}s" repeatCount="indefinite"/></rect>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Pozitiv — Python and Full-Stack developer">
<defs>
<radialGradient id="glow" cx="80%" cy="50%" r="55%"><stop offset="0" stop-color="{CYAN}" stop-opacity="0.16"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>
<radialGradient id="glow2" cx="10%" cy="100%" r="50%"><stop offset="0" stop-color="{LIME}" stop-opacity="0.10"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>
<linearGradient id="line" x1="0" x2="1"><stop offset="0" stop-color="{LIME}"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>
{defs1}
{defs2}
</defs>
<rect width="{w}" height="{h}" rx="18" fill="{BG}"/>
<rect width="{w}" height="{h}" rx="18" fill="url(#glow)"/>
<rect width="{w}" height="{h}" rx="18" fill="url(#glow2)"/>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="18" fill="none" stroke="#ffffff" stroke-opacity="0.10"/>
<ellipse cx="1010" cy="170" rx="190" ry="52" fill="none" stroke="{CYAN}" stroke-opacity="0.22" stroke-dasharray="3 9"
  transform="rotate(-18 1010 170)"><animate attributeName="stroke-dashoffset" values="0;-96" dur="9s" repeatCount="indefinite"/></ellipse>
<g>
{sphere_dots(1010, 170, 128, 820, 0.7, 0.38)}
</g>
<text x="80" y="76" font-family="{MONO}" font-size="16" fill="{MUTED}" letter-spacing="2">// github.com/pozitivstek</text>
<text x="80" y="168" font-family="{MONO}" font-size="88" font-weight="700" fill="{TEXT}" letter-spacing="1">Pozitiv<tspan fill="{LIME}">.</tspan></text>
<rect x="82" y="188" width="260" height="3" rx="1.5" fill="url(#line)"/>
{line1}
{line2}
{blink}
</svg>
'''


def terminal() -> str:
    w, h = 560, 256
    lines = [
        (0.4, [("$ ", LIME), ("whoami", TEXT)], 78),
        (1.0, [("pozitiv", CYAN), (" · python &amp; full-stack developer", MUTED)], 104),
        (1.9, [("$ ", LIME), ("ls projects/", TEXT)], 140),
        (2.5, [("fodmap-compass  people-vision  doc-chat", CYAN)], 166),
        (2.5, [("coffee-shop-bot  daily-digest-bot", CYAN)], 190),
        (3.4, [("$ ", LIME), ("cat status.txt", TEXT)], 226),
    ]
    rows = []
    for begin, parts, y in lines:
        spans = "".join(f'<tspan fill="{color}">{text}</tspan>' for text, color in parts)
        rows.append(f'<text x="28" y="{y}" font-family="{MONO}" font-size="15" opacity="0" xml:space="preserve">'
                    f'{spans}<set attributeName="opacity" to="1" begin="{begin}s"/></text>')
    joined = "\n".join(rows)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h + 34}" viewBox="0 0 {w} {h + 34}" role="img" aria-label="Terminal: whoami">
<rect x="0.5" y="0.5" width="{w - 1}" height="{h + 33}" rx="14" fill="#0c0e15" stroke="#ffffff" stroke-opacity="0.12"/>
<rect x="0.5" y="0.5" width="{w - 1}" height="38" rx="14" fill="#ffffff" fill-opacity="0.04"/>
<circle cx="24" cy="20" r="6" fill="#ff5f56"/><circle cx="46" cy="20" r="6" fill="#ffbd2e"/><circle cx="68" cy="20" r="6" fill="#27c93f"/>
<text x="{w // 2}" y="25" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{MUTED}">pozitiv — zsh</text>
<g>
{joined}
<text x="28" y="252" font-family="{MONO}" font-size="15" opacity="0" xml:space="preserve"><tspan fill="{LIME}">open to work</tspan><tspan fill="{MUTED}"> · team roles · freelance</tspan><set attributeName="opacity" to="1" begin="4.1s"/></text>
<rect x="28" y="262" width="9" height="17" fill="{LIME}" opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.01;0.5;0.51" dur="1s" begin="4.6s" repeatCount="indefinite"/></rect>
</g>
</svg>
'''


def divider() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="6" viewBox="0 0 1200 6" role="presentation">
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{LIME}" stop-opacity="0"/><stop offset="0.25" stop-color="{LIME}"/><stop offset="0.75" stop-color="{CYAN}"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient></defs>
<rect y="2" width="1200" height="2" rx="1" fill="url(#g)"/>
</svg>
'''


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    for name, content in (("banner.svg", banner()), ("terminal.svg", terminal()), ("divider.svg", divider())):
        (ASSETS / name).write_text(content, encoding="utf-8")
        print(f"{name}: {len(content) // 1024} КБ")


if __name__ == "__main__":
    main()
