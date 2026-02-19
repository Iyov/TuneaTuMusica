#!/usr/bin/env python3
import os
import json
import subprocess
from pathlib import Path

def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)

def run_test():
    # Establecer la carpeta 'test' oficial como el directorio de pruebas
    test_dir = Path.cwd() / 'test'
    
    if not test_dir.exists() or not any(test_dir.iterdir()):
        print(f"❌ Error: La carpeta '{test_dir}' no existe o está vacía.")
        print("Asegúrate de tener tus archivos reales en la carpeta 'test/' para esta prueba.")
        return
    
    env = os.environ.copy()
    # Mantenemos SANDBOX_TEST para el bypass de fingerprinting/IA si el usuario lo desea en modo test
    env['SANDBOX_TEST'] = '1'
    
    print(f"🚀 Ejecutando Sandbox Test sobre archivos REALES en: {test_dir}")
    print("ℹ️ Nota: Se ejecutará en modo DRY-RUN (Simulación) para proteger tus archivos.")
    
    try:
        # Ejecutamos con --dry-run y --no-backup para una prueba rápida y segura
        proc = subprocess.run([
            "python", "audio_tagger.py", 
            "--dir", str(test_dir), 
            "--dry-run", 
            "--no-backup"
        ], env=env, capture_output=True, text=True, timeout=300)
        
        print("STDOUT:", proc.stdout)
        
        # Validar reportes en carpeta logs/
        logs_dir = Path('logs')
        csv_files = list(logs_dir.glob('log_*.csv'))
        if csv_files:
            latest_report = max(csv_files, key=os.path.getmtime)
            print(f"✅ Reporte generado exitosamente: {latest_report.name}")
            print(f"\n[Sandbox] Prueba sobre archivos reales completada.")
            print(f"Revisa el log en: {latest_report}")
        else:
            print("❌ No se encontró ningún reporte generado en logs/")
            if proc.stderr:
                print("STDERR:", proc.stderr)
            
    except Exception as e:
        print(f"❌ Error en Sandbox: {e}")

if __name__ == '__main__':
    run_test()
