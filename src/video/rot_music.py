#!/usr/bin/env python3
"""Sound for the KaiTech brain rot cut: an original trap beat, sound effects matched to the picture, and the narrator on top.
Everything is synthesised here, so it is ours to post anywhere.

Reads  src/video/rot_timeline.json   narrator lines and scenes (from rot_voice.py)
       media/kaitech-rot-voice.wav   the narrator
       media/.rot-events.json        ball bounces, ring pops, punchlines and scene changes (written by render.js)
Writes media/kaitech-rot-music.wav   the full mix, which render.js puts on the video"""
import json, pathlib, wave
import numpy as np

root = pathlib.Path(__file__).resolve().parents[2]
TL = json.loads((root / 'src/video/rot_timeline.json').read_text())
EV = json.loads((root / 'media/.rot-events.json').read_text())
SR, DUR = 44100, TL['duration']
N = int(SR * DUR); rng = np.random.default_rng(67)
BPM = 140; BEAT = 60 / BPM; BAR = 4 * BEAT
hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)
music = np.zeros((N, 2)); sfx = np.zeros((N, 2))

def put(buf, x, at, pan=0.0, gain=1.0):
    i = int(at * SR)
    if i >= N or i + len(x) <= 0: return
    if i < 0: x = x[-i:]; i = 0
    x = x[: N - i] * gain
    buf[i:i + len(x), 0] += x * np.cos((pan + 1) * np.pi / 4) * 1.414
    buf[i:i + len(x), 1] += x * np.sin((pan + 1) * np.pi / 4) * 1.414

def tvec(sec): return np.arange(int(sec * SR)) / SR
def lp(x, cutoff):   # one-pole low-pass, done in the frequency domain
    a = 1 - np.exp(-2 * np.pi * cutoff / SR); size = 1 << int(np.ceil(np.log2(len(x) * 2))); w = np.exp(-2j * np.pi * np.fft.rfftfreq(size))
    return np.fft.irfft(np.fft.rfft(x, size) * a / (1 - (1 - a) * w), size)[: len(x)]

# ── when things happen ──
scenes = {}
for l in TL['lines']: scenes.setdefault(l['scene'], l['start'])
drop = scenes['logo'] - 0.08            # the beat drops on "nah"
end_t = scenes['end'] - 0.08
# chord roots per scene (E minor, darker in the Excel intro, lifting at the end)
ROOT = {'excel': 28, 'logo': 28, 'workforce': 28, 'billzilla': 24, 'inspect': 31, 'drivo': 26, 'fiji': 24, 'end': 28}
order = sorted(scenes.items(), key=lambda kv: kv[1])
def root_at(t):
    r = ROOT['excel']
    for name, at in order:
        if t >= at - 0.1: r = ROOT[name]
    return r

# ── drums and 808 from the drop to the end ──
def kick():
    t = tvec(0.5); f = 48 + 140 * np.exp(-t / 0.03)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22) * 2.2)
def b808(m, length):
    t = tvec(length); f = hz(m) * (1 + 0.6 * np.exp(-t / 0.04))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t / 0.005) * np.exp(-t / (length * 0.7))
    return np.tanh(x * 3.2) * 0.8   # distorted, the "bass boosted" crunch
def clap():
    t = tvec(0.3); n = rng.standard_normal(len(t)); n = n - lp(n, 900)
    e = sum(np.exp(-np.maximum(0, t - d) / 0.012) * (t >= d) for d in (0, 0.011, 0.022)) + 0.6 * np.exp(-t / 0.09)
    return n * e * 0.5
def hat(open_=False):
    t = tvec(0.25 if open_ else 0.05); n = rng.standard_normal(len(t)); n = n - lp(n, 7000)
    return n * np.exp(-t / (0.07 if open_ else 0.012)) * 0.35

bar_start = drop
k = 0
while bar_start + k * BEAT < DUR - 0.6:
    t = bar_start + k * BEAT; beat_in_bar = k % 4; bar = k // 4
    if t >= end_t and t < end_t + BAR * 0.5: k += 1; continue   # a short gap before the end hit
    if beat_in_bar in (0,) or (beat_in_bar == 2 and bar % 2): put(music, kick(), t, 0, 0.9)
    if beat_in_bar in (0, 2) or (beat_in_bar == 3 and bar % 2 == 1):
        put(music, b808(root_at(t) + (7 if beat_in_bar == 3 else 0), BEAT * (2 if beat_in_bar == 0 else 1)), t, 0, 0.7)
    if beat_in_bar == 2: put(music, clap(), t, 0, 0.75)
    # hats: eighths, with a fast roll at the end of every second bar
    roll = beat_in_bar == 3 and bar % 2 == 1
    for h in range(8 if roll else 2):
        put(music, hat(), t + h * BEAT / (8 if roll else 2), 0.25 * (-1) ** h, 0.6 if not roll else 0.45)
    k += 1
# before the drop: a dark, filtered pad and ticking hats over the Excel intro
for h in range(int(drop / (BEAT / 2))): put(music, hat(), 0.05 + h * BEAT / 2, 0.2 * (-1) ** h, 0.35)
t = tvec(drop + 0.2); pad = sum(np.sin(2 * np.pi * hz(m) * t + rng.random() * 6) for m in (40, 43, 47, 50)) / 4
put(music, lp(pad * np.minimum(1, t / 0.6), 600), 0, 0, 0.35)
# a melody bed after the drop: a simple minor hook on a bright pluck
HOOK = [64, 67, 71, 67, 64, 62, 64, 59]
def pluck(m, length=0.35):
    t = tvec(length); f = hz(m)
    return (np.sign(np.sin(2 * np.pi * f * t)) * 0.3 + np.sin(2 * np.pi * f * t)) * np.exp(-t / 0.12) * np.minimum(1, t / 0.003)
k = 0
while drop + k * BEAT / 2 < DUR - 1:
    t = drop + k * BEAT / 2
    if not (end_t <= t < end_t + BAR * 0.5): put(music, lp(pluck(HOOK[k % 8] + (root_at(t) - 28)), 3500), t, 0.35 * (-1) ** k, 0.16)
    k += 1

# ── sound effects ──
def boom():   # deep hit for punchlines
    t = tvec(1.4); f = 38 + 90 * np.exp(-t / 0.05)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.45) * 3) * 0.9
def scratch():
    t = tvec(0.35); f = 900 * (1 + 0.8 * np.sin(2 * np.pi * 6 * t)); n = rng.standard_normal(len(t))
    return (lp(n, 2500) * 0.8 + np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3) * np.exp(-t / 0.12)
def whoosh(length=0.45):
    t = tvec(length); p = t / length; n = rng.standard_normal(len(t))
    return lp(n, 4000) * np.sin(np.pi * p) ** 2 * 0.7
def pop():
    t = tvec(0.25); f = 1800 * np.exp(-t / 0.03) + 500
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.05) + rng.standard_normal(len(t)) * np.exp(-t / 0.01) * 0.3) * 0.7
def ding(m):
    t = tvec(0.5); f = hz(m)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.0 * t)) * np.exp(-t / 0.14) * np.minimum(1, t / 0.002)
def horn(length):
    t = tvec(length); x = 0
    for m, det in ((70, 0), (70, 0.12), (77, -0.08), (74, 0.05)):
        f = hz(m + det) * (1 - 0.03 * np.exp(-t / 0.05)); x = x + sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 9))
    return np.tanh(x * 0.5) * np.minimum(1, t / 0.01) * np.minimum(1, (length - t) / 0.03) * 0.5

put(sfx, scratch(), drop - 0.35, 0, 0.7)
put(sfx, boom(), drop, 0, 1.0)
for p in EV['punch']: put(sfx, boom(), p, 0, 0.75)
for s in EV['scenes'][2:]: put(sfx, whoosh(), s - 0.3, 0, 0.5)
SCALE = [64, 67, 69, 71, 74, 76, 79, 81, 83, 86]   # bounces climb this scale, then start again
for i, b in enumerate(EV['bounces']): put(sfx, ding(SCALE[i % len(SCALE)]), b, 0.5 * np.sin(i), 0.13)
for p in EV['pops']: put(sfx, pop(), p, 0, 0.45)
for i, (a, ln) in enumerate(((0, 0.16), (0.2, 0.16), (0.4, 0.6))):   # the horn on "we're so back"
    put(sfx, horn(ln), end_t + a, 0, 0.5)
put(sfx, boom(), end_t, 0, 0.9)

# ── narrator: brighter and a touch crunchy, on top of everything ──
with wave.open(str(root / 'media/kaitech-rot-voice.wav')) as w:
    v = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(float) / 32768
v = np.pad(v, (0, max(0, N - len(v))))[:N]
v = v - lp(v, 140)                         # take out the mud
v = v + 0.6 * (v - lp(v, 2500))            # presence
v = np.tanh(v * 2.0) / np.tanh(2.0)
# the music ducks while the narrator talks
env = lp(np.abs(v), 6); env = env / (env.max() + 1e-9)
duck = 1 - 0.5 * np.clip(env * 4, 0, 1)
mix = music * duck[:, None] * 0.55 + sfx * 0.6 + np.stack([v, v], 1) * 0.95
fade = np.clip((DUR - np.arange(N) / SR) / 0.25, 0, 1)
mix = np.tanh(mix * fade[:, None] * 1.25)
mix = mix / np.abs(mix).max() * 0.94
with wave.open(str(root / 'media/kaitech-rot-music.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype('<i2').tobytes())
print(f"mix {DUR:.1f}s: drop at {drop:.2f}s, {len(EV['bounces'])} bounces, {len(EV['pops'])} pops, {len(EV['punch'])} punchlines")
