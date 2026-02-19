#!/usr/bin/env python3
"""
TuneaTuMusica (GUI)
=================================

Aplicación de escritorio moderna para actualización de metadatos musicales.
Usando CustomTkinter para una interfaz elegante y profesional.

Autor: Developed by Iyov
"""

import os
import sys
import csv
import json
import shutil
import threading
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
# Integración con el motor de etiquetado
from audio_tagger import Configuracion, AudioTagger
import subprocess
import re

# CustomTkinter - Interfaz moderna
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

# Procesamiento de audio
import mutagen
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON

# Fingerprinting
import acoustid
import musicbrainzngs

# Configuración de tema
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class TuneaTuMusicaGUI:
    """Interfaz gráfica principal de TuneaTuMusica"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("TuneaTuMusica")
        self.root.geometry("900x750")
        self.root.minsize(850, 700)
        
        # Variables de estado
        self.carpeta_seleccionada = ctk.StringVar(value="")
        self.progreso = ctk.DoubleVar(value=0)
        self.total_archivos = 0
        self.procesados = 0
        self.en_ejecucion = False
        self.dry_run = False
        self.config = self._cargar_config()
        
        # Colores y estilos
        self.colores = {
            "success": "#2ecc71",
            "warning": "#f39c12",
            "error": "#e74c3c",
            "info": "#3498db",
            "bg": "#1a1a1a",
            "fg": "#ffffff"
        }
        
        self._crear_widgets()
        self._mostrar_bienvenida()
    
    def _cargar_config(self) -> Dict:
        """Carga configuración desde archivo"""
        config = {
            'acoustid_api_key': '',
            'openai_api_key': '',
            'ia_enabled': False
        }
        
        # Cargar desde archivo
        if os.path.exists('config.json'):
            try:
                with open('config.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    config['acoustid_api_key'] = data.get('acoustid_api_key', '')
                    config['openai_api_key'] = data.get('openai_api_key', '')
                    config['ia_enabled'] = data.get('ia_enabled', False)
            except:
                pass
        
        # Variables de entorno tienen prioridad
        config['acoustid_api_key'] = os.getenv('ACOUSTID_API_KEY', config['acoustid_api_key'])
        config['openai_api_key'] = os.getenv('OPENAI_API_KEY', config['openai_api_key'])
        
        # Configurar MusicBrainz
        musicbrainzngs.set_useragent(
            "TuneaTuMusica",
            "1.0",
            "contact@example.com"
        )
        
        return config
    
    def _crear_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Frame principal con padding
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ========== HEADER ==========
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 20))

        # Logo Frame (Left)
        self.logo_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.logo_frame.pack(side="left", padx=(0, 20))

        # Logo
        try:
            logo_path = os.path.join("img", "TuneaTuMusica_Logo_SF.png")
            if os.path.exists(logo_path):
                # Reducimos un poco más el tamaño para optimizar espacio
                logo_img = ctk.CTkImage(light_image=Image.open(logo_path),
                                       dark_image=Image.open(logo_path),
                                       size=(150, 90))
                self.logo_label = ctk.CTkLabel(self.logo_frame, image=logo_img, text="")
                self.logo_label.pack()
        except Exception as e:
            print(f"Error cargando logo: {e}")
        
        # Info Frame (Right)
        self.info_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.info_frame.pack(side="left", fill="both", expand=True)

        # Título
        self.titulo = ctk.CTkLabel(
            self.info_frame,
            text="TuneaTuMusica",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#3498db"
        )
        self.titulo.pack(anchor="w")
        
        # Subtítulo
        self.subtitulo = ctk.CTkLabel(
            self.info_frame,
            text="Actualizador de Metadatos Musicales",
            font=ctk.CTkFont(size=14),
            text_color="#7f8c8d"
        )
        self.subtitulo.pack(anchor="w")

        # Mensaje de bienvenida (Slogan)
        self.welcome_label = ctk.CTkLabel(
            self.info_frame,
            text="Dejando tus archivos más ordenados. ¡Vamos por esa biblioteca impecable!",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="#27ae60"
        )
        self.welcome_label.pack(anchor="w", pady=(5, 0))
        
        # ========== SECCIÓN DE CARPETA ==========
        self.folder_frame = ctk.CTkFrame(self.main_frame)
        self.folder_frame.pack(fill="x", pady=10)
        
        self.folder_label = ctk.CTkLabel(
            self.folder_frame,
            text="📁 Carpeta de Música:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.folder_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Frame para entrada y botón
        self.folder_input_frame = ctk.CTkFrame(self.folder_frame, fg_color="transparent")
        self.folder_input_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.folder_entry = ctk.CTkEntry(
            self.folder_input_frame,
            textvariable=self.carpeta_seleccionada,
            font=ctk.CTkFont(size=12),
            height=35,
            state="readonly"
        )
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.browse_btn = ctk.CTkButton(
            self.folder_input_frame,
            text="Explorar...",
            font=ctk.CTkFont(size=12),
            height=35,
            width=120,
            command=self._seleccionar_carpeta
        )
        self.browse_btn.pack(side="right")
        
        # ========== OPCIONES ==========
        self.options_frame = ctk.CTkFrame(self.main_frame)
        self.options_frame.pack(fill="x", pady=10)
        
        self.options_label = ctk.CTkLabel(
            self.options_frame,
            text="⚙️ Opciones:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.options_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Checkbox para modo simulación
        self.dry_run_var = ctk.BooleanVar(value=False)
        self.dry_run_check = ctk.CTkCheckBox(
            self.options_frame,
            text="Modo Simulación (Dry Run) - No modificar archivos, solo generar reporte",
            variable=self.dry_run_var,
            font=ctk.CTkFont(size=12)
        )
        self.dry_run_check.pack(anchor="w", padx=15, pady=5)
        
        # Checkbox para backup
        self.backup_var = ctk.BooleanVar(value=True)
        self.backup_check = ctk.CTkCheckBox(
            self.options_frame,
            text="Crear backup antes de modificar",
            variable=self.backup_var,
            font=ctk.CTkFont(size=12)
        )
        self.backup_check.pack(anchor="w", padx=15, pady=5)
        
        # Workers
        self.workers_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.workers_frame.pack(anchor="w", padx=15, pady=5)
        
        self.workers_label = ctk.CTkLabel(
            self.workers_frame,
            text="Workers paralelos:",
            font=ctk.CTkFont(size=12)
        )
        self.workers_label.pack(side="left", padx=(0, 10))
        
        self.workers_var = ctk.StringVar(value="4")
        self.workers_combo = ctk.CTkComboBox(
            self.workers_frame,
            values=["1", "2", "4", "6", "8"],
            variable=self.workers_var,
            width=80
        )
        self.workers_combo.pack(side="left")
        
        # ========== BARRA DE PROGRESO ==========
        self.progress_frame = ctk.CTkFrame(self.main_frame)
        self.progress_frame.pack(fill="x", pady=10)
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="📊 Progreso:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.progress_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            height=25,
            corner_radius=10
        )
        self.progress_bar.pack(fill="x", padx=15, pady=5)
        self.progress_bar.set(0)
        
        self.progress_text = ctk.CTkLabel(
            self.progress_frame,
            text="0% (0/0 archivos)",
            font=ctk.CTkFont(size=12)
        )
        self.progress_text.pack(anchor="w", padx=15, pady=(0, 10))
        
        # ========== BOTONES DE CONTROL ==========
        self.buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e3a5f", height=70, corner_radius=10)
        self.buttons_frame.pack(fill="x", pady=(10, 5), side="bottom")
        self.buttons_frame.pack_propagate(False)
        
        self.start_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Tunea Tu Música",
            font=ctk.CTkFont(size=14),
            height=45,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            text_color="#ffffff",
            command=self._iniciar_proceso
        )
        self.start_btn.pack(side="left", expand=True, fill="both", padx=(0, 5))
        
        # Diagnóstico (Sandbox) - pruebas locales
        self.diagnostico_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Diagnóstico",
            font=ctk.CTkFont(size=14),
            height=45,
            fg_color="#f1c40f",
            hover_color="#f39c12",
            text_color="#000000",
            command=self._run_sandbox_tests
        )
        self.diagnostico_btn.pack(side="left", expand=True, fill="both", padx=(5, 5))
 
        self.open_report_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Ver Informe",
            font=ctk.CTkFont(size=14),
            height=45,
            state="disabled",
            command=self._abrir_reporte
        )
        self.open_report_btn.pack(side="right", expand=True, fill="both", padx=(5, 0))
        
        # ========== LOG ==========
        self.log_frame = ctk.CTkFrame(self.main_frame)
        self.log_frame.pack(fill="both", expand=True, pady=10)
        
        self.log_label = ctk.CTkLabel(
            self.log_frame,
            text="📝 Log de Actividad:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.log_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Text widget para el log con altura fija
        self.log_text = ctk.CTkTextbox(
            self.log_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word",
            corner_radius=10,
            height=200
        )
        self.log_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Status bar
        self.status_bar = ctk.CTkLabel(
            self.root,
            text="Listo para comenzar",
            font=ctk.CTkFont(size=11),
            fg_color="#2c3e50",
            corner_radius=0,
            height=25
        )
        self.status_bar.pack(fill="x", side="bottom")
    
    def _mostrar_bienvenida(self):
        """Muestra mensaje de bienvenida en el log"""
        self._log("=" * 60, "info")
        self._log("🎵 Bienvenido a TuneaTuMusica", "info")
        self._log("=" * 60, "info")
        self._log("", "info")
        self._log("✨ Funcionalidades:", "info")
        self._log("   • Identificación por huella digital (AcoustID)", "info")
        self._log("   • Fallback con IA para archivos desconocidos", "info")
        self._log("   • Actualización de metadatos ID3v1 e ID3v2", "info")
        self._log("   • Generación de reportes detallados", "info")
        self._log("", "info")
        self._log("👉 Selecciona una carpeta y presiona 'Iniciar Proceso'", "warning")
        self._log("", "info")
    
    def _seleccionar_carpeta(self):
        """Abre diálogo para seleccionar carpeta"""
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta de música")
        if carpeta:
            self.carpeta_seleccionada.set(carpeta)
            self._log(f"📁 Carpeta seleccionada: {carpeta}", "info")
            
            # Contar archivos
            self._contar_archivos(carpeta)
    
    def _contar_archivos(self, carpeta: str):
        """Cuenta archivos de audio en la carpeta"""
        formatos = {'.mp3', '.flac', '.wav', '.m4a', '.ogg', '.wma'}
        count = 0
        
        try:
            for root, dirs, files in os.walk(carpeta):
                for file in files:
                    if Path(file).suffix.lower() in formatos:
                        count += 1
            
            self._log(f"📊 Se encontraron {count} archivos de audio", "success")
            self.total_archivos = count
        except Exception as e:
            self._log(f"⚠️ Error contando archivos: {e}", "error")
    
    def _log(self, mensaje: str, tipo: str = "info"):
        """Agrega mensaje al log con color"""
        colores = {
            "success": "#2ecc71",
            "warning": "#f39c12",
            "error": "#e74c3c",
            "info": "#ffffff"
        }
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        linea = f"[{timestamp}] {mensaje}\n"
        
        self.log_text.configure(state="normal")
        self.log_text.insert("end", linea)
        self.log_text.configure(state="disabled")
        self.log_text.see("end")

    def _classify_case_for_file(self, archivo: Path) -> str:
        """Usa el motor AudioTagger para clasificar el archivo"""
        from audio_tagger import AudioTagger, Configuracion
        tagger = AudioTagger(Configuracion())
        res = tagger.procesar_archivo(archivo, Path(self.carpeta_var.get() or '.'))
        return res.caso

    def _prevalidate_directory(self, archivos: List[Path]) -> str:
        """Genera el reporte de prevalidación usando la lógica del motor"""
        import csv
        from audio_tagger import AudioTagger, Configuracion
        tagger = AudioTagger(Configuracion())
        dir_raiz = Path(self.carpeta_var.get() or '.')
        
        path = 'reporte_prevalidacion.csv'
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['Archivo','Caso','ArtistPath','AlbumPath','YearPath','TitleFromName'])
            for archivo in archivos:
                derived, _ = tagger._parse_path_info(archivo, dir_raiz)
                res = tagger.procesar_archivo(archivo, dir_raiz)
                w.writerow([
                    str(archivo), 
                    res.caso, 
                    derived.artist, 
                    derived.album, 
                    derived.year, 
                    derived.title
                ])
        self._log(f"Prevalidación generada: {path}", "info")
        return path
    
    def _update_progress_ui(self, porcentaje: float, actuales: int, total: int):
        """Actualiza la barra de progreso y el texto descriptivo"""
        self.progress_bar.set(porcentaje)
        self.progress_text.configure(text=f"{int(porcentaje*100)}% ({actuales}/{total} archivos)")
    
    def _iniciar_proceso(self):
        """Inicia el procesamiento en un hilo separado"""
        carpeta = self.carpeta_seleccionada.get()
        
        if not carpeta:
            messagebox.showwarning("Carpeta requerida", "Por favor selecciona una carpeta primero.")
            return
        
        if not os.path.isdir(carpeta):
            messagebox.showerror("Error", "La carpeta seleccionada no existe.")
            return
        
        if not self.config.get('acoustid_api_key'):
            messagebox.showerror("API Key requerida", 
                "ACOUSTID_API_KEY no configurada.\n\n"
                "Configúrala en config.json o en la variable de entorno.")
            return
        
        # Deshabilitar controles durante ejecución
        self._toggle_controles(False)
        self.dry_run = self.dry_run_var.get()
        self.en_ejecucion = True
        self.open_report_btn.configure(state="disabled")
        
        # Limpiar log
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        
        if self.dry_run:
            self._log("🔍 MODO SIMULACIÓN ACTIVADO - No se modificarán archivos", "warning")
            self._log("", "info")
        
        self._log("🚀 Iniciando proceso de etiquetado...", "success")
        self._log(f"📁 Carpeta: {carpeta}", "info")
        self._log("", "info")
        
        # Iniciar el AudioTagger en hilo separado
        thread = threading.Thread(target=self._start_audio_tagger, args=(carpeta,))
        thread.daemon = True
        thread.start()

    def _toggle_controles(self, habilitar: bool):
        """Habilita/deshabilita controles de la interfaz durante el proceso"""
        estado = "normal" if habilitar else "disabled"
        self.browse_btn.configure(state=estado)
        self.start_btn.configure(state=estado)
        self.dry_run_check.configure(state=estado)
        self.backup_check.configure(state=estado)
        self.workers_combo.configure(state=estado)

    def _start_audio_tagger(self, carpeta: str):
        """Inicializa y ejecuta `AudioTagger`, actualizando la UI con progreso y resultados."""
        try:
            config = Configuracion('config.json')
            config.acoustid_api_key = self.config.get('acoustid_api_key') or config.acoustid_api_key
            config.openai_api_key = self.config.get('openai_api_key') or config.openai_api_key
            config.ia_enabled = bool(self.config.get('ia_enabled')) or config.ia_enabled

            tagger = AudioTagger(config, backup=self.backup_var.get())
            tagger.dry_run = bool(self.dry_run_var.get())

            worker_thread = threading.Thread(target=tagger.procesar_directorio, args=(carpeta, int(self.workers_var.get())))
            worker_thread.start()

            archivos = tagger.escanear_directorio(carpeta)
            total = len(archivos)
            self.total_archivos = total
            
            procesados_vistos = 0

            while worker_thread.is_alive() or len(tagger.resultados) < total:
                actuales = len(tagger.resultados)
                
                # Mostrar logs de nuevos resultados
                while procesados_vistos < actuales:
                    res = tagger.resultados[procesados_vistos]
                    icon = "✅" if res.estado == "Actualizado" else "❓" if res.estado == "Sin cambios" else "❌"
                    msg = f"{icon} {res.archivo.split(os.sep)[-1]} -> {res.estado} [Caso {res.caso}]"
                    if res.fuente != "N/A":
                        msg += f" (Vía {res.fuente})"
                    self.root.after(0, lambda m=msg: self._log(m, "info"))
                    procesados_vistos += 1

                porcentaje = actuales / total if total > 0 else 1
                self.root.after(0, lambda p=porcentaje, a=actuales, t=total: self._update_progress_ui(p, a, t))
                threading.Event().wait(0.2)

            ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            out_csv = Path('logs') / f"log_{ts}.csv"
            out_md = Path('logs') / f"reporte_{ts}.md"
            tagger.generar_reporte_csv(str(out_csv))
            tagger.generar_reporte_md(str(out_md))

            self.root.after(0, lambda: self._proceso_completado(str(out_csv)))

        except Exception as e:
            self.root.after(0, lambda: self._log(f"❌ Error: {e}", 'error'))
        finally:
            self.root.after(0, lambda: self._toggle_controles(True))
            self.en_ejecucion = False
    
    def _proceso_completado(self, reporte_path: str):
        """Llamado cuando termina el proceso"""
        self._log("\n" + "=" * 60, "info")
        self._log("✨ ¡Proceso completado!", "success")
        self._log(f"📊 Reporte guardado en: {reporte_path}", "info")
        # Intentar abrir el reporte final automáticamente si existe
        final_path = os.path.abspath("reporte_final_tuneatumusica.csv")
        if os.path.exists(final_path):
            self._log(f"Abriendo reporte final: {final_path}", "info")
            self._open_path(final_path)
        self._log("=" * 60, "info")
        
        self.status_bar.configure(text="Proceso completado ✓")
        self.open_report_btn.configure(state="normal")
        self.reporte_path = reporte_path
        
        # Preguntar si abrir reporte
        if messagebox.askyesno("Proceso Completado", 
            "¡El proceso ha finalizado!\n\n¿Deseas abrir el reporte ahora?"):
            self._abrir_reporte()
        
        # Mensaje final pedido por prompt maestro
        self._log("¡Prueba superada! Tu música está en buenas manos, TuneaTuMusica está listo.", "success")
    
    def _abrir_reporte(self):
        """Abre el reporte CSV"""
        try:
            final_path = os.path.abspath("reporte_final_tuneatumusica.csv")
            path_to_open = final_path if os.path.exists(final_path) else getattr(self, 'reporte_path', None)
            if path_to_open and os.path.exists(path_to_open):
                if sys.platform == 'win32':
                    os.startfile(path_to_open)
                elif sys.platform == 'darwin':
                    subprocess.call(['open', path_to_open])
                else:
                    subprocess.call(['xdg-open', path_to_open])
            else:
                # Buscar reportes recientes
                reportes = sorted(Path('.').glob('reporte_tuneatumusica_*.csv'))
                if reportes:
                    reporte = reportes[-1]
                    if sys.platform == 'win32':
                        os.startfile(str(reporte))
                    elif sys.platform == 'darwin':
                        subprocess.call(['open', str(reporte)])
                    else:
                        subprocess.call(['xdg-open', str(reporte)])
                else:
                    messagebox.showwarning("No encontrado", "No se encontró ningún reporte.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el reporte: {e}")
    
    def run(self):
        """Inicia la aplicación"""
        self.root.mainloop()

    def _open_path(self, path: str):
        """Abre un archivo o ruta con la aplicación por defecto"""
        try:
            if sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform == 'darwin':
                subprocess.call(['open', path])
            else:
                subprocess.call(['xdg-open', path])
        except Exception as e:
            self._log(f"⚠️ No se pudo abrir el reporte automáticamente: {e}", "warning")

    def _run_sandbox_tests(self):
        """Ejecuta pruebas sandbox sin impactar archivos reales"""
        self._log("🔬 Ejecutando Diagnóstico (Sandbox)...", "info")
        t = threading.Thread(target=self._run_sandbox_worker, daemon=True)
        t.start()

    def _run_sandbox_worker(self):
        import subprocess
        env = dict(os.environ)
        env['SANDBOX_TEST'] = '1'
        try:
            proc = subprocess.run([sys.executable, 'sandbox_test.py'], env=env, capture_output=True, text=True, timeout=180)
            if proc.stdout:
                self._log(proc.stdout, 'info')
            if proc.stderr:
                self._log(proc.stderr, 'error')
            if proc.returncode == 0:
                self._log("✅ Diagnóstico completado con éxito.", 'success')
            else:
                self._log("🚫 Diagnóstico con errores. Revisa el log.", 'warning')
        except Exception as e:
            self._log(f"⚠️ Error en Diagnóstico: {e}", 'error')


def main():
    """Punto de entrada principal"""
    app = TuneaTuMusicaGUI()
    app.run()


if __name__ == '__main__':
    main()
