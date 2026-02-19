#!/usr/bin/env python3
"""
TuneaTuMusica
=================================

Este script recorre directorios buscando archivos de audio y actualiza
sus metadatos ID3 utilizando audio fingerprinting (AcoustID/MusicBrainz)
y como fallback, APIs de IA.

Requisitos:
    - Python 3.8+
    - API Key de AcoustID (https://acoustid.org/)
    - API Key de OpenAI u otro proveedor LLM (opcional)

Uso:
    python audio_tagger.py --dir /ruta/a/musica --backup

Autor: Developed by Iyov
"""

import os
import sys
import csv
import json
import shutil
import argparse
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Procesamiento de audio
import mutagen
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.wavpack import WavPack
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TIT1, TIT2, TPE1, TALB, TDRC, TCON

# Barra de progreso
from tqdm import tqdm

# Fingerprinting
import acoustid
import musicbrainzngs

# Logging
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Géneros estandarizados (Simplificado por requerimiento: Metal u Otros)
GENEROS_ESTANDARIZADOS = {
    'metal': 'Metal',
    'heavy metal': 'Metal',
    'death metal': 'Metal',
    'black metal': 'Metal',
    'thrash metal': 'Metal',
    'power metal': 'Metal',
    'doom metal': 'Metal'
}


@dataclass
class AudioTags:
    """Estructura para almacenar metadatos de audio"""
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    year: Optional[str] = None
    genre: Optional[str] = None
    track: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioTags':
        return cls(**data)


@dataclass
class ResultadoActualizacion:
    """Estructura para reporte de resultados"""
    archivo: str
    estado: str  # 'Actualizado', 'No encontrado', 'Error'
    datos_previos: AudioTags
    datos_nuevos: AudioTags
    fuente: str  # 'MusicBrainz', 'IA', 'N/A'
    caso: str = ""  # 'A'|'B'|'C'|'D' u otro
    mensaje: str = ""


class Configuracion:
    """Gestión de configuración y API keys"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.acoustid_api_key: str = ""
        self.musicbrainz_user: str = ""
        self.musicbrainz_password: str = ""
        self.openai_api_key: str = ""
        self.ia_enabled: bool = False
        self.cargar_configuracion()
    
    def cargar_configuracion(self):
        """Carga configuración desde .env.local (opcional), archivo JSON o variables de entorno"""
        # Intentar cargar .env.local manualmente si existe para evitar dependencia de python-dotenv
        env_path = Path(".env.local")
        if env_path.exists():
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            key, _, value = line.partition('=')
                            os.environ[key.strip()] = value.strip()
                logger.info("Cargadas variables desde .env.local")
            except Exception as e:
                logger.warning(f"Error cargando .env.local: {e}")

        # Primero intentar desde archivo
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.acoustid_api_key = config.get('acoustid_api_key', '')
                    self.musicbrainz_user = config.get('musicbrainz_user', '')
                    self.musicbrainz_password = config.get('musicbrainz_password', '')
                    self.openai_api_key = config.get('openai_api_key', '')
                    self.ia_enabled = config.get('ia_enabled', False)
            except Exception as e:
                logger.warning(f"No se pudo cargar config.json: {e}")
        
        # Variables de entorno tienen prioridad
        self.acoustid_api_key = os.getenv('ACOUSTID_API_KEY', self.acoustid_api_key)
        self.musicbrainz_user = os.getenv('MUSICBRAINZ_USER', self.musicbrainz_user)
        self.musicbrainz_password = os.getenv('MUSICBRAINZ_PASSWORD', self.musicbrainz_password)
        self.openai_api_key = os.getenv('OPENAI_API_KEY', self.openai_api_key)
        self.ia_enabled = os.getenv('IA_ENABLED', str(self.ia_enabled)).lower() == 'true'
        
        # Configurar MusicBrainz
        musicbrainzngs.set_useragent(
            "TuneaTuMusica",
            "1.0",
            "contact@example.com"
        )
        if self.musicbrainz_user and self.musicbrainz_password:
            musicbrainzngs.auth(self.musicbrainz_user, self.musicbrainz_password)
    
    def validar(self) -> bool:
        """Valida que las configuraciones necesarias estén presentes"""
        if not self.acoustid_api_key:
            logger.error("ACOUSTID_API_KEY es requerida. Obtén una en https://acoustid.org/")
            return False
        return True


class BackupManager:
    """Gestiona copias de seguridad de archivos de audio"""
    
    def __init__(self, directorio_raiz: str):
        self.directorio_raiz = Path(directorio_raiz)
        self.backup_dir = self.directorio_raiz / f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.archivos_backup: List[Path] = []
    
    def crear_backup(self, archivo: Path) -> Path:
        """Crea backup de un archivo de audio"""
        # Calcular ruta relativa para mantener estructura
        ruta_relativa = archivo.relative_to(self.directorio_raiz)
        destino = self.backup_dir / ruta_relativa
        destino.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(archivo, destino)
        self.archivos_backup.append(destino)
        return destino
    
    def restaurar_backup(self):
        """Restaura todos los archivos desde el backup"""
        logger.info("Restaurando archivos desde backup...")
        for backup_file in self.archivos_backup:
            ruta_relativa = backup_file.relative_to(self.backup_dir)
            original = self.directorio_raiz / ruta_relativa
            shutil.copy2(backup_file, original)
        logger.info(f"Restaurados {len(self.archivos_backup)} archivos")


class IATagger:
    """Integración con APIs de IA para inferir metadatos"""
    
    def __init__(self, api_key: str, enabled: bool = True):
        self.api_key = api_key
        self.enabled = enabled and bool(api_key)
    
    def inferir_desde_nombre(self, nombre_archivo: str, tags_actuales: AudioTags) -> Optional[AudioTags]:
        """Usa IA para inferir metadatos desde el nombre del archivo"""
        if not self.enabled:
            return None
        
        try:
            import os
            if os.environ.get('SANDBOX_TEST') == '1':
                return AudioTags(
                    title='Demo Title IA',
                    artist='Demo Artist IA',
                    album='Demo Album IA',
                    year='2021',
                    genre='Rock'
                )
            # Implementación básica usando OpenAI (compatible con openai>=1.0.0 y versiones antiguas)
            import openai

            prompt = f"""Analiza este nombre de archivo de audio e intenta inferir los metadatos musicales.

Archivo: {nombre_archivo}
Metadatos actuales (pueden estar vacíos):
- Título: {tags_actuales.title or 'Desconocido'}
- Artista: {tags_actuales.artist or 'Desconocido'}
- Álbum: {tags_actuales.album or 'Desconocido'}
- Año: {tags_actuales.year or 'Desconocido'}
- Género: {tags_actuales.genre or 'Desconocido'}

Responde SOLO en formato JSON con esta estructura exacta:
{{
    "title": "nombre de la canción",
    "artist": "nombre del artista",
    "album": "nombre del álbum",
    "year": "año",
    "genre": "género",
    "confidence": "alta/media/baja"
}}

Si no puedes determinar algún campo, usa null.
"""

            try:
                # Nueva interfaz (openai>=1.0.0)
                if hasattr(openai, 'OpenAI'):
                    client = openai.OpenAI(api_key=self.api_key)
                    # En la nueva interfaz, usar chat.completions.create
                    try:
                        resp = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "Eres un experto en metadatos musicales. Analiza nombres de archivos de audio y extrae información precisa."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.3,
                            max_tokens=300
                        )
                    except Exception:
                        # Alternativa: usar responses API como fallback
                        resp = client.responses.create(
                            model="gpt-4o-mini",
                            input=prompt,
                            temperature=0.3,
                            max_output_tokens=300
                        )
                    # Extraer posible contenido de varias formas
                    try:
                        contenido = resp.choices[0].message.content.strip()
                    except Exception:
                        try:
                            contenido = resp.choices[0].message['content'].strip()
                        except Exception:
                            contenido = str(resp)
                else:
                    # Interfaz antigua
                    openai.api_key = self.api_key
                    response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Eres un experto en metadatos musicales. Analiza nombres de archivos de audio y extrae información precisa."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        max_tokens=300
                    )
                    contenido = response.choices[0].message.content.strip()
            except Exception as e:
                raise
            
            # Extraer JSON de la respuesta
            if '```json' in contenido:
                contenido = contenido.split('```json')[1].split('```')[0].strip()
            elif '```' in contenido:
                contenido = contenido.split('```')[1].split('```')[0].strip()
            
            datos = json.loads(contenido)
            
            # Solo usar si la confianza es suficiente
            if datos.get('confidence') in ['alta', 'media']:
                return AudioTags(
                    title=datos.get('title'),
                    artist=datos.get('artist'),
                    album=datos.get('album'),
                    year=str(datos.get('year')) if datos.get('year') else None,
                    genre=self._estandarizar_genero(datos.get('genre'))
                )
            
            return None
            
        except Exception as e:
            logger.warning(f"Error en IA tagging: {e}")
            return None
    
    def _estandarizar_genero(self, genero: Optional[str]) -> Optional[str]:
        """Estandariza el género musical"""
        if not genero:
            return None
        
        genero_lower = genero.lower()
        return GENEROS_ESTANDARIZADOS.get(genero_lower, genero.title())


class AudioTagger:
    """Clase principal para etiquetado de audio"""
    
    FORMATOS_SOPORTADOS = {'.mp3', '.flac', '.wav', '.m4a', '.ogg', '.wma'}
    
    def __init__(self, config: Configuracion, backup: bool = True):
        self.config = config
        self.backup_manager: Optional[BackupManager] = None
        self.hacer_backup = backup
        self.dry_run: bool = False
        self.ia_tagger = IATagger(config.openai_api_key, config.ia_enabled)
        self.resultados: List[ResultadoActualizacion] = []
    
    def escanear_directorio(self, directorio: str) -> List[Path]:
        """Escanea recursivamente un directorio buscando archivos de audio"""
        archivos_audio = []
        directorio_path = Path(directorio)
        
        logger.info(f"Escaneando directorio: {directorio}")
        
        for ruta in directorio_path.rglob('*'):
            if ruta.is_file() and ruta.suffix.lower() in self.FORMATOS_SOPORTADOS:
                archivos_audio.append(ruta)
        
        logger.info(f"Encontrados {len(archivos_audio)} archivos de audio")
        return archivos_audio
    
    def leer_tags_actuales(self, archivo: Path) -> AudioTags:
        """Lee los tags ID3 actuales del archivo"""
        try:
            audio = File(archivo)
            if audio is None:
                return AudioTags()
            
            # Usar EasyID3 para MP3 si está disponible
            if isinstance(audio, MP3):
                if audio.tags is None:
                    audio.add_tags()
                try:
                    easy = EasyID3(archivo)
                    return AudioTags(
                        title=easy.get('title', [None])[0],
                        artist=easy.get('artist', [None])[0],
                        album=easy.get('album', [None])[0],
                        year=easy.get('date', [None])[0],
                        genre=easy.get('genre', [None])[0],
                        track=easy.get('tracknumber', [None])[0]
                    )
                except:
                    pass
            
            # Fallback genérico
            return AudioTags(
                title=str(audio.get('TIT2', '')),
                artist=str(audio.get('TPE1', '')),
                album=str(audio.get('TALB', '')),
                year=str(audio.get('TDRC', '')),
                genre=str(audio.get('TCON', ''))
            )
            
        except Exception as e:
            logger.warning(f"Error leyendo tags de {archivo}: {e}")
            return AudioTags()
    
    def identificar_con_fingerprint(self, archivo: Path) -> Optional[Dict[str, Any]]:
        """Identifica una canción usando audio fingerprinting"""
        try:
            # Sandbox: bypass fingerprinting for tests
            import os
            if os.environ.get('SANDBOX_TEST') == '1':
                return {
                    'title': 'Demo Title',
                    'artist': 'Demo Artist',
                    'album': 'Demo Album',
                    'year': '2020',
                    'genre': 'Rock'
                }
            # Generar fingerprint con AcoustID
            duracion, fingerprint = acoustid.fingerprint_file(str(archivo))
            
            # Buscar en AcoustID
            resultados = acoustid.lookup(
                self.config.acoustid_api_key,
                fingerprint,
                duracion,
                meta='recordings releases tracks'
            )
            
            if resultados['status'] != 'ok':
                return None
            
            results = resultados.get('results', [])
            if not results:
                return None
            
            # Tomar el mejor resultado (mayor score)
            mejor_resultado = max(results, key=lambda x: x.get('score', 0))
            
            if mejor_resultado.get('score', 0) < 0.7:  # Score mínimo de confianza
                return None
            
            # Extraer información de MusicBrainz
            recordings = mejor_resultado.get('recordings', [])
            if not recordings:
                return None
            
            recording = recordings[0]
            
            # Obtener información detallada de MusicBrainz
            recording_id = recording.get('id')
            if recording_id:
                try:
                    mb_result = musicbrainzngs.get_recording_by_id(
                        recording_id,
                        includes=['artists', 'releases', 'tags']
                    )
                    return self._procesar_mb_result(mb_result)
                except:
                    # Fallback a datos básicos de AcoustID
                    return self._procesar_acoustid_result(recording)
            
            return self._procesar_acoustid_result(recording)
            
        except Exception as e:
            logger.warning(f"Error en fingerprinting de {archivo.name}: {e}")
            return None
    
    def _procesar_mb_result(self, result: Dict) -> Dict[str, Any]:
        """Procesa resultado de MusicBrainz"""
        recording = result.get('recording', {})
        
        # Artista
        artist_credit = recording.get('artist-credit', [])
        artist = artist_credit[0].get('artist', {}).get('name') if artist_credit else None
        
        # Lanzamientos (álbumes)
        releases = recording.get('release-list', [])
        release = releases[0] if releases else {}
        
        # Géneros de tags
        tags = recording.get('tag-list', [])
        genre = None
        if tags:
            # Tomar el tag más popular
            sorted_tags = sorted(tags, key=lambda x: int(x.get('count', 0)), reverse=True)
            genre = sorted_tags[0].get('name') if sorted_tags else None
        
        return {
            'title': recording.get('title'),
            'artist': artist,
            'album': release.get('title'),
            'year': release.get('date', '')[:4] if release.get('date') else None,
            'genre': genre
        }
    
    def _procesar_acoustid_result(self, recording: Dict) -> Dict[str, Any]:
        """Procesa resultado básico de AcoustID"""
        artist = recording.get('artists', [{}])[0].get('name') if recording.get('artists') else None
        
        releases = recording.get('releases', [])
        release = releases[0] if releases else {}
        
        return {
            'title': recording.get('title'),
            'artist': artist,
            'album': release.get('title'),
            'year': None,  # AcoustID no proporciona año directamente
            'genre': None
        }
    
    def estandarizar_genero(self, genero: Optional[str]) -> Optional[str]:
        """Estandariza el género musical según lista predefinida"""
        if not genero:
            return None
        
        genero_lower = genero.lower()
        return GENEROS_ESTANDARIZADOS.get(genero_lower, genero.title())

    def _parse_path_info(self, archivo: Path, directorio_raiz: Path) -> Tuple[AudioTags, Dict[str, Optional[str]]]:
        """Extrae información basada en la ruta y el nombre de archivo siguiendo las reglas estrictas:
        - Banda: Dos carpetas anteriores (N-2) -> Title Case
        - Disco/Año: Carpeta anterior (N-1) con formato (Año) Nombre -> Title Case
        - Track/Título: Nombre del archivo XX - Título -> Title Case
        """
        metadata = {
            'artist_dir': None,
            'album_dir': None,
            'year_dir': None,
            'track_from_name': None,
            'title_from_name': None,
            'ext': archivo.suffix.lstrip('.')
        }

        try:
            def to_title_case(text: str) -> str:
                if not text: return text
                # Eliminar comas completamente para evitar conflictos en CSV
                clean_text = text.replace(',', '').replace('_', ' ')
                return ' '.join(word.capitalize() for word in clean_text.split())

            # Padre (N-1): (Año) Disco
            parent_dir = archivo.parent.name
            import re
            m_album = re.match(r'^\((\d{4,})\)\s*(.+)$', parent_dir)
            if m_album:
                metadata['year_dir'] = m_album.group(1)
                metadata['album_dir'] = to_title_case(m_album.group(2))
            else:
                metadata['album_dir'] = to_title_case(parent_dir)

            # Abuelo (N-2): Banda
            try:
                # Verificamos que no sea el directorio raíz
                if archivo.parent.parent != directorio_raiz and archivo.parent != directorio_raiz:
                    metadata['artist_dir'] = to_title_case(archivo.parent.parent.name)
            except Exception:
                pass

            # Nombre de archivo: NN - Título
            name = archivo.stem
            m_name = re.match(r'^\s*(?P<track>\d{1,2})\s*[-_.\s]+\s*(?P<title>.+)$', name)
            if m_name:
                metadata['track_from_name'] = m_name.group('track').zfill(2)
                metadata['title_from_name'] = to_title_case(m_name.group('title'))
            else:
                metadata['title_from_name'] = to_title_case(name)

        except Exception as e:
            logger.debug(f"Error parseando ruta {archivo}: {e}")

        derived = AudioTags(
            title=metadata.get('title_from_name'),
            artist=metadata.get('artist_dir'),
            album=metadata.get('album_dir'),
            year=metadata.get('year_dir'),
            genre='Metal',
            track=metadata.get('track_from_name')
        )

        return derived, metadata
    
    def escribir_tags(self, archivo: Path, tags: AudioTags) -> bool:
        """Escribe los tags en el archivo de audio"""
        try:
            # Si estamos en modo dry-run, no escribir, solo simular éxito
            if getattr(self, 'dry_run', False):
                logger.info(f"DRY-RUN: simulando escritura de tags en {archivo} -> {tags.to_dict()}")
                return True
            audio = File(archivo)
            if audio is None:
                return False
            
            # MP3 con ID3
            if isinstance(audio, MP3):
                if audio.tags is None:
                    audio.add_tags()
                
                # Usar ID3 directamente para más control
                id3 = ID3(archivo)
                
                if tags.title:
                    id3['TIT2'] = TIT2(encoding=3, text=tags.title)
                if tags.artist:
                    id3['TPE1'] = TPE1(encoding=3, text=tags.artist)
                if tags.album:
                    id3['TALB'] = TALB(encoding=3, text=tags.album)
                if tags.year:
                    id3['TDRC'] = TDRC(encoding=3, text=tags.year)
                # Si no hay género, usar 'Metal' por defecto según requerimiento
                genre_value = tags.genre or 'Metal'
                if genre_value:
                    id3['TCON'] = TCON(encoding=3, text=genre_value)
                
                id3.save(archivo)
            
            # FLAC
            elif isinstance(audio, FLAC):
                if tags.title:
                    audio['TITLE'] = tags.title
                if tags.artist:
                    audio['ARTIST'] = tags.artist
                if tags.album:
                    audio['ALBUM'] = tags.album
                if tags.year:
                    audio['DATE'] = tags.year
                audio['GENRE'] = tags.genre or 'Metal'
                
                audio.save()
            
            # Otros formatos
            else:
                if hasattr(audio, 'tags'):
                    if tags.title:
                        audio.tags['title'] = tags.title
                    if tags.artist:
                        audio.tags['artist'] = tags.artist
                    if tags.album:
                        audio.tags['album'] = tags.album
                    if tags.year:
                        audio.tags['date'] = tags.year
                    audio.tags['genre'] = tags.genre or 'Metal'
                    
                    audio.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error escribiendo tags en {archivo}: {e}")
            return False
    
    def procesar_archivo(self, archivo: Path, directorio_raiz: Path) -> ResultadoActualizacion:
        """Procesa un archivo integrando los Casos A-D con la Nomenclatura Estricta.
        Garantiza la estructura: /Banda/(Año) Disco/NN - Titulo.ext
        """
        def es_valido(v: Optional[str]) -> bool:
            if not v: return False
            lv = v.lower().strip()
            return lv not in ['', 'unknown', 'untitled', 'track', 'artista desconocido', 'desconocido']

        def to_title_case(text: str) -> str:
            if not text: return text
            return ' '.join(word.capitalize() for word in text.replace('_', ' ').split())

        def sanitize(name: str) -> str:
            import re
            return re.sub(r'[\\/:*?"<>|,]', '', name).strip()

        # 1. Análisis Inicial
        tags_previos = self.leer_tags_actuales(archivo)
        derived_path, _ = self._parse_path_info(archivo, directorio_raiz)

        # 2. Evaluación de Estados
        path_has_info = es_valido(derived_path.artist) and es_valido(derived_path.title)
        tags_have_info = es_valido(tags_previos.artist) and es_valido(tags_previos.title)

        # 3. Determinación de Metadatos Finales y Caso
        caso = 'D'
        fuente = 'N/A'
        
        # CASO D: Todo bien (en teoría). Validamos si la estructura física es perfecta.
        if path_has_info and tags_have_info:
            f_artist, f_album, f_year, f_track, f_title = derived_path.artist, derived_path.album, derived_path.year, derived_path.track, derived_path.title
            caso = 'D'
            fuente = 'Estructura'
        
        # CASO A: La ruta tiene la verdad, los tags no.
        elif path_has_info and not tags_have_info:
            f_artist, f_album, f_year, f_track, f_title = derived_path.artist, derived_path.album, derived_path.year, derived_path.track, derived_path.title
            caso = 'A'
            fuente = 'Ruta'
            
        # CASO B: Los tags tienen la verdad, la ruta no.
        elif not path_has_info and tags_have_info:
            f_artist, f_album, f_year, f_track, f_title = tags_previos.artist, tags_previos.album, tags_previos.year, tags_previos.track, tags_previos.title
            caso = 'B'
            fuente = 'Tags'
            
        # CASO C: Nadie tiene la verdad. Buscamos fuera.
        else:
            caso = 'C'
            datos_web = self.identificar_con_fingerprint(archivo)
            if datos_web:
                f_artist = datos_web.get('artist') or derived_path.artist or tags_previos.artist
                f_album = datos_web.get('album') or derived_path.album or tags_previos.album
                f_year = datos_web.get('year') or derived_path.year or tags_previos.year
                f_title = datos_web.get('title') or derived_path.title or tags_previos.title
                f_track = datos_web.get('track') or derived_path.track or tags_previos.track
                fuente = 'Internet'
            elif self.ia_tagger.enabled:
                datos_ia = self.ia_tagger.inferir_desde_nombre(archivo.name, tags_previos)
                if datos_ia:
                    f_artist, f_album, f_year, f_track, f_title = datos_ia.artist, datos_ia.album, datos_ia.year, datos_ia.track, datos_ia.title
                    fuente = 'IA'
                else:
                    f_artist, f_album, f_year, f_track, f_title = derived_path.artist, derived_path.album, derived_path.year, derived_path.track, derived_path.title
                    fuente = 'Inferencia Fallida'
            else:
                f_artist, f_album, f_year, f_track, f_title = derived_path.artist, derived_path.album, derived_path.year, derived_path.track, derived_path.title
                fuente = 'N/A'

        # 4. Normalización Estricta
        f_artist = to_title_case(f_artist) or "Otros"
        f_album = to_title_case(f_album) or "Otros"
        f_title = to_title_case(f_title) or archive.stem if 'archive' in locals() else to_title_case(archivo.stem)
        f_year = f_year or "0000"
        f_track = (f_track or "00").zfill(2)
        f_genre = "Metal"

        nuevos = AudioTags(
            title=f_title, artist=f_artist, album=f_album,
            year=f_year, genre=f_genre, track=f_track
        )

        # 5. Definición de Destino
        sub_path = Path(sanitize(f_artist)) / f"({f_year}) {sanitize(f_album)}"
        nombre_final = f"{f_track} - {sanitize(f_title)}{archivo.suffix}"
        path_destino = directorio_raiz / sub_path / nombre_final

        # 6. Evaluación Real de Cambios
        tags_distintos = (
            tags_previos.title != nuevos.title or
            tags_previos.artist != nuevos.artist or
            tags_previos.album != nuevos.album or
            tags_previos.year != nuevos.year or
            tags_previos.track != nuevos.track or
            tags_previos.genre != nuevos.genre
        )
        ruta_distinta = str(archivo.absolute()) != str(path_destino.absolute())

        if not tags_distintos and not ruta_distinta:
            return ResultadoActualizacion(
                archivo=str(archivo), estado="Sin cambios",
                datos_previos=tags_previos, datos_nuevos=nuevos,
                fuente="N/A", caso='D', mensaje='Estructura y tags perfectos'
            )

        # 7. Ejecución de Cambios
        try:
            # Backup
            if self.hacer_backup and (tags_distintos or ruta_distinta):
                if self.backup_manager is None:
                    self.backup_manager = BackupManager(directorio_raiz)
                self.backup_manager.crear_backup(archivo)

            # Escribir Tags
            ok_tags = True
            if tags_distintos:
                ok_tags = self.escribir_tags(archivo, nuevos)

            # Mover Archivo
            if ruta_distinta:
                if not getattr(self, 'dry_run', False):
                    path_destino.parent.mkdir(parents=True, exist_ok=True)
                    archivo.rename(path_destino)
                mensaje = f"Movido a {sub_path}"
            else:
                mensaje = "Tags actualizados en misma ruta"

            return ResultadoActualizacion(
                archivo=str(path_destino if ruta_distinta else archivo),
                estado="Actualizado" if (tags_distintos or ruta_distinta) else "Sin cambios",
                datos_previos=tags_previos, datos_nuevos=nuevos,
                fuente=fuente, caso=caso, mensaje=mensaje
            )

        except Exception as e:
            return ResultadoActualizacion(
                archivo=str(archivo), estado="Error",
                datos_previos=tags_previos, datos_nuevos=nuevos,
                fuente=fuente, mensaje=f"Error: {e}"
            )
    
    def procesar_directorio(self, directorio: str, max_workers: int = 4):
        """Procesa todos los archivos de audio en un directorio"""
        directorio_path = Path(directorio)
        archivos = self.escanear_directorio(directorio)
        
        if not archivos:
            logger.info("No se encontraron archivos de audio")
            return
        
        logger.info(f"Procesando {len(archivos)} archivos...")
        
        # Procesar archivos con barra de progreso
        with tqdm(total=len(archivos), desc="Etiquetando") as pbar:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self.procesar_archivo, archivo, directorio_path): archivo
                    for archivo in archivos
                }
                
                for future in as_completed(futures):
                    resultado = future.result()
                    self.resultados.append(resultado)
                    pbar.update(1)
        
        logger.info(f"Procesamiento completado. {len(self.resultados)} archivos procesados.")
    
    def generar_reporte_csv(self, archivo_salida: str = "log_actualizacion.csv"):
        """Genera reporte en formato CSV"""
        # Asegurar que el directorio de salida exista
        out_path = Path(archivo_salida)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # Usar 'utf-8-sig' para incluir BOM y mejorar compatibilidad con Excel en Windows
        # Usar ';' como delimitador para evitar conflictos con comas y por compatibilidad regional
        with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = [
                'Archivo', 'Estado', 'Fuente', 'Caso',
                'Titulo_Previo', 'Artista_Previo', 'Album_Previo', 'Año_Previo', 'Genero_Previo',
                'Titulo_Nuevo', 'Artista_Nuevo', 'Album_Nuevo', 'Año_Nuevo', 'Genero_Nuevo',
                'Mensaje'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            
            for resultado in self.resultados:
                # Asegurar que no haya valores None y quitar comas para evitar conflictos
                def s(v):
                    if v is None: return ''
                    return str(v).replace(',', '')

                row = {
                    'Archivo': s(resultado.archivo),
                    'Estado': s(resultado.estado),
                    'Fuente': s(resultado.fuente),
                    'Caso': s(resultado.caso),
                    'Titulo_Previo': s(resultado.datos_previos.title),
                    'Artista_Previo': s(resultado.datos_previos.artist),
                    'Album_Previo': s(resultado.datos_previos.album),
                    'Año_Previo': s(resultado.datos_previos.year),
                    'Genero_Previo': s(resultado.datos_previos.genre),
                    'Titulo_Nuevo': s(resultado.datos_nuevos.title),
                    'Artista_Nuevo': s(resultado.datos_nuevos.artist),
                    'Album_Nuevo': s(resultado.datos_nuevos.album),
                    'Año_Nuevo': s(resultado.datos_nuevos.year),
                    'Genero_Nuevo': s(resultado.datos_nuevos.genre),
                    'Mensaje': s(resultado.mensaje)
                }
                writer.writerow(row)
        
        logger.info(f"Reporte CSV generado: {out_path}")
    
    def generar_reporte_md(self, archivo_salida: str = "reporte.md"):
        """Genera reporte en formato Markdown"""
        out_path = Path(archivo_salida)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write("# Reporte de Etiquetado de Audio\n\n")
            f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total de archivos procesados:** {len(self.resultados)}\n\n")
            
            # Estadísticas
            actualizados = sum(1 for r in self.resultados if r.estado == "Actualizado")
            no_encontrados = sum(1 for r in self.resultados if r.estado == "No encontrado")
            errores = sum(1 for r in self.resultados if r.estado == "Error")
            
            f.write("## Resumen\n\n")
            f.write(f"- ✅ Actualizados: {actualizados}\n")
            f.write(f"- ❌ No encontrados: {no_encontrados}\n")
            f.write(f"- ⚠️ Errores: {errores}\n\n")
            
            # Detalles por fuente
            fuentes = {}
            for r in self.resultados:
                if r.estado == "Actualizado":
                    fuentes[r.fuente] = fuentes.get(r.fuente, 0) + 1
            
            if fuentes:
                f.write("### Fuentes de Información\n\n")
                for fuente, count in fuentes.items():
                    f.write(f"- {fuente}: {count} archivos\n")
                f.write("\n")
            
            # Detalles
            f.write("## Detalles\n\n")
            for resultado in self.resultados:
                f.write(f"### {Path(resultado.archivo).name}\n\n")
                f.write(f"- **Ruta:** `{resultado.archivo}`\n")
                f.write(f"- **Estado:** {resultado.estado}\n")
                f.write(f"- **Fuente:** {resultado.fuente}\n")
                if resultado.caso:
                    f.write(f"- **Caso detectado:** {resultado.caso}\n")
                
                if resultado.mensaje:
                    f.write(f"- **Mensaje:** {resultado.mensaje}\n")
                
                if resultado.estado == "Actualizado":
                    f.write("\n**Cambios realizados:**\n\n")
                    
                    if resultado.datos_previos.title != resultado.datos_nuevos.title:
                        f.write(f"- Título: `{resultado.datos_previos.title or 'Vacío'}` → `{resultado.datos_nuevos.title}`\n")
                    if resultado.datos_previos.artist != resultado.datos_nuevos.artist:
                        f.write(f"- Artista: `{resultado.datos_previos.artist or 'Vacío'}` → `{resultado.datos_nuevos.artist}`\n")
                    if resultado.datos_previos.album != resultado.datos_nuevos.album:
                        f.write(f"- Álbum: `{resultado.datos_previos.album or 'Vacío'}` → `{resultado.datos_nuevos.album}`\n")
                    if resultado.datos_previos.year != resultado.datos_nuevos.year:
                        f.write(f"- Año: `{resultado.datos_previos.year or 'Vacío'}` → `{resultado.datos_nuevos.year}`\n")
                    if resultado.datos_previos.genre != resultado.datos_nuevos.genre:
                        f.write(f"- Género: `{resultado.datos_previos.genre or 'Vacío'}` → `{resultado.datos_nuevos.genre}`\n")
                
                f.write("\n---\n\n")
        
        logger.info(f"Reporte Markdown generado: {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Automatizador de Etiquetado Masivo de Audio con IA y Fingerprinting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Ejecutar con backup automático
  python audio_tagger.py --dir /ruta/a/musica --backup

  # Sin backup, solo reporte
  python audio_tagger.py --dir /ruta/a/musica --no-backup

  # Especificar archivo de configuración
  python audio_tagger.py --dir /ruta/a/musica --config mi_config.json

  # Solo generar reporte Markdown
  python audio_tagger.py --dir /ruta/a/musica --format md
        """
    )
    
    parser.add_argument(
        '--dir', '-d',
        required=True,
        help='Directorio raíz con archivos de audio'
    )
    
    parser.add_argument(
        '--backup', '-b',
        action='store_true',
        default=True,
        help='Crear backup antes de modificar (por defecto: True)'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Deshabilitar backup automático'
    )
    
    parser.add_argument(
        '--config', '-c',
        default='config.json',
        help='Archivo de configuración JSON (por defecto: config.json)'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['csv', 'md', 'both'],
        default='both',
        help='Formato del reporte (por defecto: both)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simular cambios sin escribir tags ni renombrar archivos'
    )

    parser.add_argument(
        '--out-csv',
        default='log_actualizacion.csv',
        help='Nombre del archivo CSV detallado de salida (por defecto: log_actualizacion.csv)'
    )

    parser.add_argument(
        '--out-md',
        default='reporte.md',
        help='Nombre del archivo Markdown consolidado de salida (por defecto: reporte.md)'
    )

    parser.add_argument(
        '--clean-reports',
        action='store_true',
        help='Eliminar reportes antiguos antes de generar los nuevos ( conserva los archivos indicados en --out-csv y --out-md )'
    )
    
    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=4,
        help='Número de workers paralelos (por defecto: 4)'
    )
    
    parser.add_argument(
        '--restore',
        action='store_true',
        help='Restaurar archivos desde el último backup'
    )
    
    args = parser.parse_args()
    
    # Validar directorio
    if not os.path.isdir(args.dir):
        logger.error(f"El directorio no existe: {args.dir}")
        sys.exit(1)
    
    # Cargar configuración
    config = Configuracion(args.config)
    if not config.validar():
        sys.exit(1)
    
    # Inicializar tagger
    hacer_backup = args.backup and not args.no_backup
    tagger = AudioTagger(config, backup=hacer_backup)
    # Propagar dry-run al tagger
    if getattr(args, 'dry_run', False):
        tagger.dry_run = True

    # Asegurar carpeta de logs y añadir file handler de logging
    logs_dir = Path('logs')
    logs_dir.mkdir(parents=True, exist_ok=True)
    try:
        # Crear un handler de fichero con timestamp
        ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_file = logs_dir / f"audio_tagger_{ts}.log"
        fh = logging.FileHandler(str(log_file), encoding='utf-8')
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        # Evitar añadir múltiples handlers si ya existe uno similar
        if not any(isinstance(h, logging.FileHandler) and getattr(h, 'baseFilename', None) == str(log_file) for h in logger.handlers):
            logger.addHandler(fh)
            logger.info(f"Logging to file: {log_file}")
    except Exception as e:
        logger.warning(f"No se pudo crear handler de logging en logs/: {e}")
    
    # Restaurar backup si se solicita
    if args.restore:
        backup_dir = Path(args.dir)
        backups = sorted(backup_dir.glob('.backup_*'))
        if backups:
            logger.info(f"Restaurando desde: {backups[-1]}")
            # Implementar lógica de restauración
        else:
            logger.warning("No se encontraron backups")
        return
    
    # Procesar archivos
    try:
        tagger.procesar_directorio(args.dir, max_workers=args.workers)
        
        # Determinar nombres de salida; si el usuario no especificó --out-csv
        # generamos un nombre con fecha/hora: log_YYYY-MM-DD_hh-mm-ss.csv
        if getattr(args, 'out_csv', None) is None or args.out_csv == 'log_actualizacion.csv':
            out_csv_name = f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        else:
            out_csv_name = args.out_csv

        out_csv = logs_dir / out_csv_name
        # Generar nombre para MD si no se proporcionó uno explícito
        if getattr(args, 'out_md', None) is None or args.out_md == 'reporte.md':
            out_md_name = f"reporte_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"
        else:
            out_md_name = args.out_md
        out_md = logs_dir / out_md_name

        # Limpiar reportes antiguos si se solicitó
        if getattr(args, 'clean_reports', False):
            patterns = ['reporte*.md', 'reporte*.csv', 'log_*.csv', 'reporte_*_tuneatumusica*.csv']
            removed = 0
            for p in patterns:
                for f in logs_dir.glob(p):
                    try:
                        # No borrar los archivos destino
                        if f.resolve() == out_csv.resolve() or f.resolve() == out_md.resolve():
                            continue
                        f.unlink()
                        removed += 1
                    except Exception:
                        pass
            logger.info(f"Se eliminaron {removed} reportes antiguos en logs/ (si existían)")

        # Generar reportes (solo CSV detallado y MD consolidado)
        if args.format in ['csv', 'both']:
            tagger.generar_reporte_csv(archivo_salida=str(out_csv))
        
        if args.format in ['md', 'both']:
            tagger.generar_reporte_md(archivo_salida=str(out_md))
        
        logger.info("Proceso completado exitosamente!")
        
    except KeyboardInterrupt:
        logger.info("\nProceso interrumpido por el usuario")
        if tagger.backup_manager:
            logger.info("Los archivos modificados pueden restaurarse desde el backup")
    
    except Exception as e:
        logger.error(f"Error durante el procesamiento: {e}")
        if tagger.backup_manager:
            logger.info("Restaurando archivos desde backup...")
            tagger.backup_manager.restaurar_backup()
        raise


if __name__ == '__main__':
    main()
