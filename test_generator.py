#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)

def create_dummy_mp3(path):
    # Create a tiny dummy file. Real MP3 bytes are not necessary for sandbox, just an empty file with .mp3 extension.
    Path(path).write_bytes(b"")

def main():
    sandbox = Path('test_sandbox')
    ensure_dir(sandbox)
    (sandbox / '01 - Cancion Sin Artista.mp3').parent.mkdir(parents=True, exist_ok=True)
    create_dummy_mp3(sandbox / '01 - Cancion Sin Artista.mp3')
    create_dummy_mp3(sandbox / '02 - BandaTest - Cancion Completa.mp3')
    create_dummy_mp3(sandbox / 'track_random_sin_formato.mp3')

    env = os.environ.copy()
    env['SANDBOX_TEST'] = '1'
    # Ejecutar CLI para sandbox
    proc = subprocess.run(["python", "audio_tagger.py", "--dir", str(sandbox)], env=env, capture_output=True, text=True, timeout=120)
    print(proc.stdout)
    print(proc.stderr)

    reports = sorted(Path('.').glob('reporte_final_tuneatumusica.csv'))
    if reports:
        print("Reporte generado:", reports[-1].as_posix())
        with open(reports[-1], 'r', encoding='utf-8') as f:
            header = f.readline().strip()
            print("Cabecera:", header)
            # Simple validation: no empty Artista/Título en la primera data line si existe
            lines = f.readlines()
            if lines:
                first = lines[0].split(',')
                _ruta, _nuevo, estado, fuente, tprev, aprev, tnew, anew, alb, year, gen = first
                ok = tprev and tnew
                print("Validation básica de Campos: TítuloAnterior/TítuloNuevo presentes? ", bool(tprev) and bool(tnew))
    else:
        print("No se encontró reporte final para validar.")

if __name__ == '__main__':
    main()
