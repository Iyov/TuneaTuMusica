#!/usr/bin/env python3
import os
import json
import subprocess
from pathlib import Path

def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)

def create_silence_wav(path, duration_sec=5):
    # Creates a very small WAV with silence (16-bit mono, 44100 Hz)
    import wave
    import struct
    framerate = 44100
    nframes = int(duration_sec * framerate)
    with wave.open(path, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(framerate)
        silent = [0] * nframes
        w.writeframes(struct.pack('<' + 'h'*nframes, *silent))

def generate_samples(test_dir):
    ensure_dir(test_dir)
    # 3 samples: one with a non-descriptive name, one with a generic track01.mp3, one with NN - Artist - Title pattern
    samples = [
        ("unknown.mp3", 0),
        ("track01.mp3", 1),
        ("01 - DemoArtist - DemoTitle.mp3", 2)
    ]
    for fname, _ in samples:
        p = Path(test_dir) / fname
        create_silence_wav(str(p.with_suffix('.wav')), duration_sec=5)
        # leave as WAV disguised as MP3 for sandbox simplicity
        p = p.with_suffix('.mp3')
        p.write_bytes(p.with_suffix('.wav').read_bytes())

def run_test():
    test_dir = Path.cwd() / 'test_music'
    generate_samples(test_dir)
    # Run the CLI tool in sandbox mode if installed
    env = os.environ.copy()
    env['SANDBOX_TEST'] = '1'
    try:
        proc = subprocess.run(["python", "audio_tagger.py", "--dir", str(test_dir)], env=env, capture_output=True, text=True, timeout=120)
        print(proc.stdout)
        print(proc.stderr)
        # Basic validation: ensure report exists and contains required columns
        reports = sorted(Path('.').glob('reporte_final_cachatumusica.csv'))
        if reports:
            with open(reports[-1], 'r', encoding='utf-8') as f:
                header = f.readline()
                if 'Título Anterior' in header and 'Artista Anterior' in header:
                    print("[Sandbox] Reporte validado en cabecera.")
                    print("[Sandbox] Prueba superada.")
                else:
                    print("[Sandbox] Cabecera del reporte inesperada:", header)
        else:
            print("[Sandbox] No se encontró reporte final.")
    except Exception as e:
        print("[Sandbox] Error durante la prueba:", e)

if __name__ == '__main__':
    run_test()
