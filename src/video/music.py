#!/usr/bin/env python3
"""Original background music for the KaiTech intro film, composed in code so it is ours to use anywhere.

28 seconds at 75 beats a minute, so one bar is 3.2 s and every scene change in the film lands on a new bar:
  0.0  pad swells in while the points gather        6.0  Dm9   KaiWorkforce, pulse and arpeggio start
  2.4  a soft chime as the name appears              9.2  Bbmaj9 BillZilla
  4.4  a rise into the first product                12.4  Fmaj9 KaiInspect, light percussion joins
                                                    15.6  C/E   Drivo
                                                    18.8  Gm9   Made for Fiji, then a rise
                                                    22.4  Fmaj9 the end card: a low hit and a long ring-out
Run: python3 src/video/music.py  -> media/kaitech-intro-music.wav"""
import numpy as np, wave, pathlib

SR, DUR = 44100, 28.0
N = int(SR * DUR)
rng = np.random.default_rng(2026)
BEAT = 0.8
hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)
L, R = np.zeros(N), np.zeros(N)

def add(sig, start, pan=0.0, gain=1.0):
    i = int(start * SR); sig = sig[: max(0, N - i)] * gain
    if i >= N or not len(sig): return
    L[i:i + len(sig)] += sig * np.cos((pan + 1) * np.pi / 4)
    R[i:i + len(sig)] += sig * np.sin((pan + 1) * np.pi / 4)

def lowpass(x, cutoff):
    """One-pole low-pass; cutoff may be a number or an array the length of x."""
    if np.ndim(cutoff) == 0:   # fixed cutoff: same filter, applied in one go through the FFT
        a = 1 - np.exp(-2 * np.pi * cutoff / SR); size = 1 << int(np.ceil(np.log2(len(x) * 2)))
        w = np.exp(-2j * np.pi * np.fft.rfftfreq(size))
        return np.fft.irfft(np.fft.rfft(x, size) * a / (1 - (1 - a) * w), size)[: len(x)]
    c = np.broadcast_to(np.asarray(cutoff, float), x.shape)
    a = 1 - np.exp(-2 * np.pi * c / SR)
    y = np.empty_like(x); acc = 0.0
    for k in range(len(x)):   # plain loop: clear, and fast enough for 28 s
        acc += a[k] * (x[k] - acc); y[k] = acc
    return y

def env(n, a, r, sustain=1.0):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4)) * sustain
    tail = int(r * SR); e[-tail:] *= np.linspace(1, 0, tail) ** 2 if tail else 1
    return e

def saw(f, t, harmonics=14):
    return sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, harmonics + 1) if f * k < 9000) * 0.6

# ── chords: bass note, then the voicing ──
CH = {
    'Fadd9': (41, [57, 60, 64, 67]), 'Dm9': (38, [53, 57, 60, 64]), 'Bbmaj9': (34, [50, 53, 57, 60]),
    'Fmaj9': (41, [57, 60, 64, 67]), 'C/E': (40, [55, 60, 62, 64]), 'Gm9': (43, [58, 62, 65, 69]),
    'Csus': (36, [53, 55, 60, 65]), 'Fend': (29, [41, 48, 57, 64, 67, 72])}
PLAN = [(0.0, 6.0, 'Fadd9'), (6.0, 9.2, 'Dm9'), (9.2, 12.4, 'Bbmaj9'), (12.4, 15.6, 'Fmaj9'),
        (15.6, 18.8, 'C/E'), (18.8, 21.2, 'Gm9'), (21.2, 22.4, 'Csus'), (22.4, 28.0, 'Fend')]

# pad: detuned saws, filter opening across the film
for s, e, name in PLAN:
    bass, notes = CH[name]; ln = e - s + 0.9; n = int(ln * SR); t = np.arange(n) / SR
    for m in notes:
        for det, pan in ((-0.07, -0.5), (0.0, 0.0), (0.07, 0.5)):
            v = saw(hz(m + det), t + rng.random())
            cut = 900 + 1800 * min(1, s / 22.4) + 900 * (name == 'Fend')
            v = lowpass(v, cut) * env(n, 0.9 if s else 1.6, 0.9)
            add(v, s, pan, 0.024 if s else 0.034)
    # sub bass, from the first product on
    if s >= 6.0:
        b = np.sin(2 * np.pi * hz(bass) * t) + 0.25 * np.sin(4 * np.pi * hz(bass) * t)
        add(b * env(n, 0.15, 0.8), s, 0, 0.07 if name != 'Fend' else 0.11)

# arpeggio: eighth notes up through the chord, getting a little stronger each bar
def pluck(m, length=0.9):
    n = int(length * SR); t = np.arange(n) / SR; f = hz(m)
    x = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)) * np.exp(-t / 0.28)
    return x * np.minimum(1, t / 0.004)
for bar, (s, e, name) in enumerate(p for p in PLAN if 6.0 <= p[0] < 22.4):
    notes = CH[name][1] + [x + 12 for x in CH[name][1]]
    pattern = [0, 2, 4, 6, 3, 5, 7, 4]
    for k in range(int(round((e - s) / (BEAT / 2)))):
        tt = s + k * BEAT / 2
        add(pluck(notes[pattern[k % 8] % len(notes)]), tt, -0.45 if k % 2 else 0.45, 0.045 + 0.008 * bar)

# pulse: a soft low thump on beats one and three
def thump():
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 46 + 70 * np.exp(-t / 0.035)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
for k in range(int((22.4 - 6.0) / (2 * BEAT))):
    add(thump(), 6.0 + k * 2 * BEAT, 0, 0.24)

# light percussion from KaiInspect on: a short filtered tick on the off-beats
for k in range(int((22.4 - 12.4) / (BEAT / 2))):
    if k % 2:
        n = int(0.06 * SR); x = rng.standard_normal(n) * np.exp(-np.arange(n) / SR / 0.012)
        x = x - lowpass(x, 6000)
        add(x, 12.4 + k * BEAT / 2, 0.3 if k % 4 == 1 else -0.3, 0.05)

# rises: filtered noise and a climbing tone into 6.0 and 22.4
def rise(length):
    n = int(length * SR); t = np.arange(n) / SR; p = t / length
    noise = lowpass(rng.standard_normal(n), 300 + 6000 * p ** 2) * p ** 3
    tone = np.sin(2 * np.pi * np.cumsum(220 + 440 * p ** 2) / SR) * p ** 4 * 0.25
    return noise + tone
add(rise(1.6), 4.4, -0.2, 0.22); add(rise(1.6), 20.8, 0.2, 0.26)

# chimes: as the name appears, and on the end card
def bell(m, length=3.0):
    n = int(length * SR); t = np.arange(n) / SR; f = hz(m)
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.4)) * np.exp(-t / 1.1) * np.minimum(1, t / 0.003)
for m, d, p in ((84, 0.0, -0.3), (91, 0.12, 0.3), (88, 0.24, 0.0)):
    add(bell(m), 2.4 + d, p, 0.05)
for m, d, p in ((77, 0.0, -0.4), (84, 0.1, 0.4), (88, 0.2, -0.2), (91, 0.3, 0.2)):
    add(bell(m), 22.4 + d, p, 0.06)

# low hit on the end card
n = int(3.0 * SR); t = np.arange(n) / SR
add(np.sin(2 * np.pi * np.cumsum(38 + 50 * np.exp(-t / 0.06)) / SR) * np.exp(-t / 0.9), 22.4, 0, 0.5)

# room: a long, soft reverb from decaying noise, different in each ear
def reverb(x, seed):
    g = np.random.default_rng(seed); n = int(2.8 * SR); t = np.arange(n) / SR
    ir = g.standard_normal(n) * np.exp(-t / 0.75); ir = lowpass(ir, 5000); ir /= np.sqrt(np.sum(ir ** 2))
    size = 1 << int(np.ceil(np.log2(len(x) + n)))
    return np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x)]
wetL, wetR = reverb(L, 1), reverb(R, 2)
outL, outR = L * 0.78 + wetL * 0.42, R * 0.78 + wetR * 0.42

# master: fade in and out, gentle saturation, peak at -1 dB
t = np.arange(N) / SR
fade = np.minimum(1, t / 0.8) * np.clip((DUR - t) / 2.5, 0, 1) ** 1.5
outL, outR = np.tanh(outL * fade * 1.4) / 1.4, np.tanh(outR * fade * 1.4) / 1.4
peak = max(np.abs(outL).max(), np.abs(outR).max()); g = 10 ** (-1 / 20) / peak
pcm = (np.stack([outL, outR], 1) * g * 32767).astype('<i2')
out = pathlib.Path(__file__).resolve().parents[2] / 'media' / 'kaitech-intro-music.wav'
out.parent.mkdir(exist_ok=True)
with wave.open(str(out), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote', out.relative_to(out.parents[1]))
