# CachaTuMusica 🎵

**Edición Pro** - Aplicación de escritorio con interfaz gráfica moderna para actualizar automáticamente los metadatos (tags ID3) de tu biblioteca musical.

Utiliza **audio fingerprinting** con AcoustID/MusicBrainz y, como fallback, APIs de Inteligencia Artificial para identificar y etiquetar tus canciones.

> 💬 *"El que sabe, sabe. Vamos a dejar tu música impeque."*

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## ✨ Características

- 🖥️ **Interfaz Gráfica Moderna**: GUI elegante con CustomTkinter (tema oscuro, controles intuitivos)
- 🎯 **Audio Fingerprinting**: Identifica canciones por su "huella digital" acústica con AcoustID (precisión ~99%)
- 🤖 **Fallback con IA**: Para archivos no reconocidos, usa LLMs (GPT-4o-mini) como respaldo
- 📊 **Progreso en Tiempo Real**: Barra de progreso con porcentaje, contador y log en vivo
- 🧪 **Modo Simulación (Dry Run)**: Prueba sin modificar archivos, solo genera reporte
- 💾 **Backup Automático**: Crea copias de seguridad antes de modificar cualquier archivo
- 📄 **Reportes Detallados**: Genera CSV con todos los cambios realizados
- ⚡ **Procesamiento Paralelo**: Usa múltiples workers para mayor velocidad
- 🎵 **Múltiples Formatos**: Soporta MP3, FLAC, WAV, M4A, OGG, WMA
- 🏷️ **Estandarización**: Normaliza géneros musicales (Rock, Pop, Electronic, etc.)

## 📋 Requisitos

- Python 3.8 o superior
- API Key de AcoustID (gratuita en https://acoustid.org/)
- Chromaprint instalado (biblioteca de fingerprinting)

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Iyov/CachaTuMusica.git
cd CachaTuMusica
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Instalar Chromaprint

#### Windows
```bash
# Usando chocolatey
choco install chromaprint

# O descargar desde:
# https://github.com/acoustid/chromaprint/releases
```

#### Linux
```bash
sudo apt-get install libchromaprint-tools
# o
sudo yum install chromaprint-tools
```

#### macOS
```bash
brew install chromaprint
```

### 5. Configurar API Keys

#### Opción A: Archivo config.json (Recomendado)
```bash
cp config.example.json config.json
# Edita config.json con tu API key de AcoustID
```

**Ejemplo de config.json:**
```json
{
    "acoustid_api_key": "tu_api_key_aqui",
    "musicbrainz_user": "",
    "musicbrainz_password": "",
    "openai_api_key": "",
    "ia_enabled": false
}
```

#### Opción B: Variables de entorno
```bash
cp .env.example .env.local
# Edita .env.local con tus credenciales
```

#### Obtener API Keys:
- **🔑 AcoustID** (GRATIS): https://acoustid.org/
  - Regístrate y genera una API Key
- **🤖 OpenAI** (Opcional): https://platform.openai.com/
  - Necesaria solo si quieres usar IA como fallback

---

## 🖥️ Uso con Interfaz Gráfica (Recomendado)

La forma más fácil y amigable de usar CachaTuMusica:

```bash
python gui.py
```

### Características de la GUI:

| Función | Descripción |
|---------|-------------|
| 📁 **Selección de Carpeta** | Botón "Explorar" para elegir tu biblioteca musical |
| 📊 **Progreso Visual** | Barra de progreso con % y contador (ej: "45% (23/50 archivos)") |
| 📝 **Log en Tiempo Real** | Ve cada archivo procesado con iconos descriptivos |
| ⚙️ **Opciones** | Modo simulación, backup automático, workers paralelos |
| 📄 **Reporte Automático** | Se abre el CSV al finalizar el proceso |

### Iconos del Log:
- ✅ **Actualizado**: Metadatos actualizados exitosamente
- 🤖 **Vía IA**: Identificado usando inteligencia artificial
- 🎵 **Vía AcoustID**: Identificado por fingerprinting
- ❓ **No encontrado**: No se pudo identificar el archivo
- ❌ **Error**: Ocurrió un error al procesar

---

## 💻 Uso en Línea de Comandos (CLI)

Para usuarios avanzados o automatización:

### Comando básico

```bash
python audio_tagger.py --dir /ruta/a/tu/musica
```

### Opciones disponibles

```bash
# Sin backup
python audio_tagger.py --dir /ruta/a/musica --no-backup

# Solo reporte CSV
python audio_tagger.py --dir /ruta/a/musica --format csv

# Solo reporte Markdown
python audio_tagger.py --dir /ruta/a/musica --format md

# Usar más workers (más rápido pero consume más CPU)
python audio_tagger.py --dir /ruta/a/musica --workers 8

# Configuración personalizada
python audio_tagger.py --dir /ruta/a/musica --config mi_config.json

# Restaurar backup
python audio_tagger.py --dir /ruta/a/musica --restore
```

---

## 📊 Reportes Generados

### CSV (`reporte_cachatumusica_YYYYMMDD_HHMMSS.csv`)
Archivo Excel-compatible que incluye:
- Ruta completa del archivo
- Estado (Actualizado/No encontrado/Error)
- Fuente de información (AcoustID/IA)
- Metadatos anteriores vs nuevos (Título, Artista, Álbum, Año, Género)

### Ejemplo de ejecución CLI

```bash
$ python audio_tagger.py --dir ~/Música --backup

2024-01-15 10:30:15 - INFO - Escaneando directorio: ~/Música
2024-01-15 10:30:18 - INFO - Encontrados 1,247 archivos de audio
2024-01-15 10:30:18 - INFO - Procesando 1,247 archivos...
Etiquetando: 100%|████████████████| 1247/1247 [08:45<00:00,  2.37archivo/s]
2024-01-15 10:39:03 - INFO - Reporte CSV generado: log_actualizacion.csv
2024-01-15 10:39:04 - INFO - Proceso completado exitosamente!
```

---

## 🏗️ Arquitectura del Proyecto

```
CachaTuMusica/
├── gui.py                  # Interfaz gráfica (CustomTkinter)
├── audio_tagger.py         # Versión CLI
├── requirements.txt        # Dependencias
├── config.json            # Configuración local (no subir a git)
├── config.example.json    # Plantilla de configuración
├── .env.example           # Plantilla de variables de entorno
├── .env.local             # Variables locales (no subir a git)
├── .gitignore            # Archivos ignorados por git
├── README.md             # Este archivo
│
└── Archivos generados (no subir a git):
    ├── reporte_cachatumusica_*.csv
    ├── log_actualizacion.csv
    ├── reporte.md
    └── .backup_*/
```

### Módulos principales

| Archivo | Descripción |
|---------|-------------|
| `gui.py` | Interfaz gráfica con CustomTkinter, threading y controles visuales |
| `audio_tagger.py` | Versión CLI con todas las funcionalidades de procesamiento |
| `Configuracion` | Gestión de API keys desde config.json o variables de entorno |
| `IATagger` | Integración con OpenAI para inferencia de metadatos |
| `AudioTagger` | Lógica principal de fingerprinting y escritura de tags |

---

## 🔒 Seguridad

⚠️ **IMPORTANTE: Siempre usa backup en la primera ejecución**

- ✅ Se crea automáticamente un directorio `.backup_YYYYMMDD_HHMMSS/` con copias de seguridad
- ✅ Los backups mantienen la estructura de carpetas original
- ✅ En caso de error durante el procesamiento, los archivos se restauran automáticamente
- ✅ Modo Dry Run disponible para probar sin modificar archivos

---

## ⚠️ Limitaciones

1. **Precisión del fingerprinting**: ~90-99% para música popular y conocida
2. **Canciones muy raras**: Pueden no estar en la base de datos de AcoustID
3. **API Rate Limits**: MusicBrainz limita solicitudes sin autenticación
4. **Costo IA**: Si usas OpenAI, tienen costo por tokens consumidos

---

## 🔧 Solución de Problemas

### Error: "chromaprint library not found"
```bash
# Windows: Reinstala con chocolatey
choco install chromaprint

# Linux
sudo apt-get install libchromaprint-tools

# macOS
brew install chromaprint
```

### Error: "ACOUSTID_API_KEY es requerida"
```bash
# Verifica que tengas configurada la API key en config.json
# o en la variable de entorno:
export ACOUSTID_API_KEY="tu_key_aqui"
```

### La GUI no abre o muestra errores
```bash
# Verifica que tengas customtkinter instalado
pip install customtkinter pillow

# Verifica que tengas config.json creado
cp config.example.json config.json
```

### Archivos no identificados
- Verifica que los archivos de audio no estén corruptos
- Canciones muy raras o nuevas pueden no estar en AcoustID
- Considera habilitar la opción IA en la configuración para estos casos

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Áreas de mejora:

- 🎵 Soporte para más formatos de audio (AAC, OGG, etc.)
- 🔗 Integración con más servicios (Shazam, Spotify, etc.)
- 🎨 Temas adicionales para la GUI (claro, personalizado)
- 🌍 Soporte multi-idioma
- 🧪 Mejor cobertura de tests

Para contribuir:
1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Add: nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📄 Licencia

MIT License - Libre para uso personal y comercial.

```
Copyright (c) 2024 CachaTuMusica

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

**Hecho con ❤️ por OpenCode**

¿Preguntas o sugerencias? Abre un [issue](https://github.com/Iyov/CachaTuMusica/issues) en el repositorio.

---

## 🙏 Agradecimientos

- [AcoustID](https://acoustid.org/) - Por el servicio de audio fingerprinting
- [MusicBrainz](https://musicbrainz.org/) - Por la base de datos musical abierta
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Por la librería de GUI moderna
- [Mutagen](https://mutagen.readthedocs.io/) - Por el manejo de metadatos de audio
