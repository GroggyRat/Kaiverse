#!/usr/bin/env python3
"""Narrator for the KaiTech brain rot cut, made with Piper (open-source text to speech, MIT licence).

Each line has: what the captions show, what the voice says (spelled for pronunciation), and the scene it belongs to.
Writes media/kaitech-rot-voice.wav and src/video/rot_timeline.json, which the film reads so captions follow the voice.
Run: python3 src/video/rot_voice.py /path/to/en_US-amy-medium.onnx"""
import json, pathlib, sys, wave
import numpy as np
from piper import PiperVoice
from piper.config import SynthesisConfig

LINES = [
    # caption, spoken, scene
    ("POV: you still do payroll in EXCEL 💀", "P O V. You still do pay roll, in Excel.", "excel"),
    ("it's so over 😭", "It's so over.", "excel"),
    ("nah. KaiTech just pulled up", "Nah. Kye Tech just pulled up.", "logo"),
    ("KaiWorkforce does your FNPF and PAYE", "Kye Workforce does your F N P F, and P A Y E.", "workforce"),
    ("payslips? emailed. +1000 aura", "Payslips? Emailed. Plus one thousand aura.", "workforce"),
    ("BillZilla: invoices with ZERO gaps", "Bill Zilla. Invoices with zero gaps.", "billzilla"),
    ("they pay with M-PAiSA? say less", "They pay with em pie sa? Say less.", "billzilla"),
    ("Excel could NEVER", "Excel could never.", "billzilla"),
    ("KaiInspect: photo or it didn't happen 📸", "Kye Inspect. Photo, or it didn't happen.", "inspect"),
    ("Drivo turns invoices into delivery routes", "Dree-vo turns your invoices into delivery routes.", "drivo"),
    ("driver lost? not in this economy 🚚", "Driver lost? Not in this economy.", "drivo"),
    ("4 apps. 1 company. made for FIJI 🇫🇯", "Four apps. One company. Made for Fiji.", "fiji"),
    ("we're so back. book a demo, no cap 🧢", "We're so back. Book a demo. No cap.", "end"),
]
SR_OUT, GAP, LEAD, LIFT = 44100, 0.1, 0.3, 1.07   # LIFT: play 7% faster, which also raises the pitch a little

voice = PiperVoice.load(sys.argv[1])
cfg = SynthesisConfig(length_scale=0.8, noise_scale=0.6, noise_w_scale=0.7)
root = pathlib.Path(__file__).resolve().parents[2]
tmp = root / 'media' / '.voice-line.wav'
chunks, timeline, t = [], [], LEAD
for caption, spoken, scene in LINES:
    with wave.open(str(tmp), 'wb') as w:
        voice.synthesize_wav(spoken, w, syn_config=cfg)
    with wave.open(str(tmp)) as w:
        sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(float) / 32768
    # trim silence at both ends so lines land tight, then resample to 44.1 kHz
    on = np.where(np.abs(x) > 0.02)[0]; x = x[max(0, on[0] - int(0.02 * sr)): on[-1] + int(0.05 * sr)]
    x = np.interp(np.arange(0, len(x), sr * LIFT / SR_OUT), np.arange(len(x)), x)
    dur = len(x) / SR_OUT
    # word timings: spread over the line by word length (Piper gives no word times, this is close enough for pop-up captions)
    words = caption.split(); weights = np.array([max(2, len(w.strip('?.!,:'))) + 1.5 for w in words]); cum = np.concatenate([[0], np.cumsum(weights)]) / weights.sum()
    timeline.append({'scene': scene, 'start': round(t, 3), 'end': round(t + dur, 3), 'caption': caption,
                     'words': [[w, round(t + cum[i] * dur * 0.92, 3)] for i, w in enumerate(words)]})
    chunks.append((t, x)); t += dur + GAP
total = t + 1.6
out = np.zeros(int(total * SR_OUT))
for start, x in chunks:
    i = int(start * SR_OUT); out[i:i + len(x)] += x
out = out / np.abs(out).max() * 0.89
with wave.open(str(root / 'media' / 'kaitech-rot-voice.wav'), 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR_OUT); w.writeframes((out * 32767).astype('<i2').tobytes())
tmp.unlink()
(root / 'src' / 'video' / 'rot_timeline.json').write_text(json.dumps({'duration': round(total, 2), 'lines': timeline}, ensure_ascii=False, indent=1))
print(f'voice {total:.1f}s, {len(timeline)} lines')
for l in timeline: print(f"  {l['start']:6.2f}-{l['end']:6.2f}  {l['scene']:9s} {l['caption']}")
