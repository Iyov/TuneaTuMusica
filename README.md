# <img src="img/TuneaTuMusica_Logo_SF.png" width="40" height="40" valign="middle"> TuneaTuMusica 🎵

**TuneaTuMusica** es la solución definitiva para acabar con el caos de los nombres de archivos genéricos en tu biblioteca musical. ¿Cansado de ver `Track 01.mp3` o `descarga_final_12.mp3`? Esta suite combina extracción inteligente, identificación acústica e IA para **renombrar y etiquetar** tus canciones de forma impecable.

>  **TuneaTuMusica**: Máxima precisión, automatización refinada y seguridad total.

---

## ✨ Características Principales

![Interfaz Gráfica de TuneaTuMusica](img/TuneaTuMusica_GUI.png)

- 🖥️ **Interfaz Vanguardista**: UI intuitiva diseñada para visualizar y corregir nombres masivamente.
- 🧹 **Legibilidad Total**: Renombrado automático bajo el estándar estricto `NN - Artista - Título.ext`.
- 🔍 **Prevalidación Diagnóstica**: Escaneo profundo que predice cada cambio antes de que ocurra.
- 🎯 **Audio Fingerprinting**: Tecnología AcoustID para identificación sin errores.
- 🤖 **IA Fallback Engine**: GPT-4o-mini para resolver metadatos desde contextos complejos si el fingerprint falla.
- 📊 **Taxonomía de Casos (A-D)**: Clasificación inteligente para aplicar la acción exacta necesaria.
- 🧪 **Sandbox Real-File**: Suite de pruebas que opera sobre tu biblioteca real en modo simulación (Dry-run).
- ️ **Seguridad Bancaria**: Backups automáticos `.backup_YYMMDD/` y reportes CSV/MD detallados.

---

## 📁 Inteligencia de Rutas

La lógica de extracción ha sido refinada para interpretar tu estructura de carpetas de forma humana:

1.  🎹 **Banda / Artista**: Localizado en la carpeta **N-2** (dos niveles arriba del archivo).
2.  💿 **Disco & Año**: Extraídos de la carpeta **N-1** (padre directo). Soporta el patrón `(YYYY) Nombre del Álbum`.
3.  🎵 **Pista & Título**: Parseados dinámicamente desde el nombre del archivo, eliminando el "ruido" de caracteres especiales.

**Estructura Ideal:**
`Musica/Metal/Caliban/(2006) The Undying Darkness/01 - Intro.mp3`
---

## ⚡ Lógica de Decisión: Los 4 Casos de Clasificación

TuneaTuMusica aplica lógica de ingeniería para resolver el estado de cada archivo:

### 🟢 Caso A: "La Carpeta manda" (Ruta ➝ Tags)
El nombre del archivo o su ubicación son perfectos, pero los "Tags" internos están vacíos. El motor extrae la info de la ruta, **escribe los Tags** y asegura el formato estricto.

### 🔵 Caso B: "Los Tags mandan" (Tags ➝ Ruta)
El archivo tiene metadatos internos correctos, pero la ruta es un caos. El motor usa los Tags para **mover y renombrar el archivo** al estándar estricto.

### 🟡 Caso C: "Búsqueda de Identidad" (Cloud ➝ All)
Ni la ruta ni los Tags sirven. El motor "escucha" el audio (**AcoustID**) o usa **IA** para descubrir quién es, arreglando todo bajo el estándar.

### ⚪ Caso D: "Estado Perfecto"
El nombre está ordenado, los Tags coincidan y la carpeta es la correcta. Solo se valida y se marca como impecable.

---

## 📐 Estándar de Nomenclatura Estricta

Independientemente del caso detectado, el resultado final siempre será:

`/[Nombre Banda]/([Año]) [Nombre del Disco]/[NumTrack] - [Nombre Canción].[Ext]`

### Especificación:
- **Banda (N-2)**: Carpeta abuela en *Title Case*.
- **Disco (N-1)**: Carpeta padre como `(AAAA) Titulo`.
- **Pista**: Formato `XX - `.
- **Género**: Forzado globalmente a `Metal`.

---

## 📊 La Inteligencia Detrás: Los 4 Casos de Clasificación

TuneaTuMusica no "adivina", aplica lógica de ingeniería para resolver el estado de cada archivo. Aquí explicamos cómo decide qué hacer:

### 🟢 Caso A: "La Carpeta manda"
*   **Diagnóstico**: El nombre del archivo o su ubicación son perfectos, pero los "Tags" internos están vacíos o dicen "Desconocido".
    - *Ejemplo*: `Caliban/(2006) The Undying Darkness/01 - Intro.mp3` (pero el archivo por dentro no tiene info).
*   **Acción**: El motor extrae la info de la ruta y **escribe los Tags** internos.

### 🔵 Caso B: "Los Tags mandan"
*   **Diagnóstico**: El archivo tiene los metadatos internos (Artista, Título) correctos, pero el nombre del archivo es un desastre.
    - *Ejemplo*: `asdf_123_descarga.mp3` (pero al abrirlo dice "Metallica - Enter Sandman").
*   **Acción**: El motor usa los Tags para **renombrar el archivo** al estándar: `01 - Metallica - Enter Sandman.mp3`.

### 🟡 Caso C: "Búsqueda de Identidad" (Fingerprinting/IA)
*   **Diagnóstico**: Ni el nombre del archivo ni los Tags internos sirven. El archivo es un completo desconocido.
    - *Ejemplo*: `track01.mp3` y sin metadatos.
*   **Acción**: El motor "escucha" el audio (**AcoustID**) o le pregunta a la **IA** para descubrir quién es, y luego **arregla tanto Tags como Nombre**.

### ⚪ Caso D: "Estado Perfecto"
*   **Diagnóstico**: El nombre está ordenado y los Tags coinciden perfectamente.
*   **Acción**: No hace nada. Solo te informa que el archivo está **100% Correcto**. ¡Misión cumplida!

---

## 🚀 Guía de Inicio Rápido

### 1. Clonar el Repositorio
```bash
git clone https://github.com/Iyov/TuneaTuMusica.git
cd TuneaTuMusica
```

### 2. Instalación según tu Sistema Operativo

#### 🪟 Windows

```powershell
# Verificar que Python está instalado (debe ser 3.8 o superior)
python --version

# Si no tienes Python, descárgalo desde:
# https://www.python.org/downloads/windows/
# ⚠️ IMPORTANTE: Durante la instalación, marca "Add Python to PATH"

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Instalar dependencias de Python
pip install -r requirements.txt
```

**Notas para Windows:**
- Si `python` no funciona, intenta con `py` o `python3`
- Tkinter viene incluido con Python en Windows, no requiere instalación adicional
- Si tienes problemas con permisos, ejecuta PowerShell como Administrador

#### 🐧 Linux (Ubuntu/Debian)

```bash
# Instalar Python y dependencias del sistema
sudo apt update
sudo apt install python3 python3-venv python3-pip python3-tk

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias de Python
pip install -r requirements.txt
```

**Notas para Linux:**
- `python3-tk` es esencial para la interfaz gráfica
- En otras distribuciones: Fedora/RHEL usa `python3-tkinter`, Arch usa `tk`

#### 🍎 macOS

```bash
# Instalar Python (si no lo tienes)
# Opción 1: Usando Homebrew (recomendado)
brew install python3 python-tk

# Opción 2: Descargar desde python.org
# https://www.python.org/downloads/macos/

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias de Python
pip install -r requirements.txt
```

**Notas para macOS:**
- Si usas el Python del sistema, puede que necesites instalar Tkinter por separado
- Homebrew es la forma más sencilla de tener todo configurado correctamente

### 3. Configurar Variables de Entorno

Crea un archivo `.env` o `config.json` con tus credenciales:

#### Opción A: Usando archivo .env
```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar con tu editor favorito
nano .env  # o vim, code, etc.
```

Contenido del archivo `.env`:
```bash
# API Key de AcoustID (REQUERIDA)
# Obtén una gratuita en: https://acoustid.org/
ACOUSTID_API_KEY=tu_api_key_aqui

# Credenciales de MusicBrainz (opcional)
MUSICBRAINZ_USER=tu_usuario
MUSICBRAINZ_PASSWORD=tu_password

# API Key de OpenAI (opcional, para fallback con IA)
OPENAI_API_KEY=sk-tu_api_key_aqui
IA_ENABLED=true
```

#### Opción B: Usando archivo config.json
```bash
# Copiar el archivo de ejemplo
cp config.example.json config.json

# Editar con tu editor favorito
nano config.json
```

Contenido del archivo `config.json`:
```json
{
  "acoustid_api_key": "tu_api_key_aqui",
  "openai_api_key": "sk-tu_api_key_aqui",
  "ia_enabled": true,
  "musicbrainz_user": "tu_usuario",
  "musicbrainz_password": "tu_password"
}
```

### 4. Obtener API Keys

#### 🔑 AcoustID API Key (REQUERIDA)
1. Visita: https://acoustid.org/
2. Crea una cuenta gratuita
3. Ve a "Applications" y crea una nueva aplicación
4. Copia tu API Key y pégala en tu archivo de configuración

#### 🤖 OpenAI API Key (OPCIONAL)
1. Visita: https://platform.openai.com/api-keys
2. Crea una cuenta o inicia sesión
3. Genera una nueva API Key
4. Copia la key y pégala en tu archivo de configuración
5. Establece `IA_ENABLED=true` para activar el fallback con IA

### 5. Ejecutar la Aplicación

#### Interfaz Gráfica (Recomendado)

**Windows:**
```powershell
# Asegúrate de tener el entorno virtual activado
venv\Scripts\activate

# Ejecutar la aplicación GUI
python gui.py
```

**Linux/macOS:**
```bash
# Asegúrate de tener el entorno virtual activado
source venv/bin/activate

# Ejecutar la aplicación GUI
python gui.py
```

#### Modo Línea de Comandos

**Windows:**
```powershell
# Procesar una carpeta específica
python audio_tagger.py C:\Users\TuUsuario\Musica

# Modo simulación (no modifica archivos)
python audio_tagger.py C:\Users\TuUsuario\Musica --dry-run
```

**Linux/macOS:**
```bash
# Procesar una carpeta específica
python audio_tagger.py /ruta/a/tu/musica

# Modo simulación (no modifica archivos)
python audio_tagger.py /ruta/a/tu/musica --dry-run
```

### 6. Verificación Segura (Sandbox)
Si querés ver qué haría el motor con tu música sin modificar nada:
```bash
python sandbox_test.py
```
*Este comando corre automáticamente en modo **--dry-run** sobre tu carpeta `test/`.*

### 7. Uso Diario

Para ejecutar la aplicación después de la instalación inicial:

**Windows:**
```powershell
# Navegar al directorio del proyecto
cd TuneaTuMusica

# Activar el entorno virtual
venv\Scripts\activate

# Ejecutar la aplicación
python gui.py

# Cuando termines, desactivar el entorno virtual
deactivate
```

**Linux/macOS:**
```bash
# Navegar al directorio del proyecto
cd TuneaTuMusica

# Activar el entorno virtual
source venv/bin/activate

# Ejecutar la aplicación
python gui.py

# Cuando termines, desactivar el entorno virtual
deactivate
```

---

## 🔧 Solución de Problemas Comunes

### Windows
- **Error: "python no se reconoce"**: Reinstala Python y marca "Add Python to PATH"
- **Error de permisos**: Ejecuta PowerShell como Administrador
- **Tkinter no encontrado**: Reinstala Python desde python.org (viene incluido)

### Linux
- **Error: "No module named '_tkinter'"**: Instala `python3-tk` con `sudo apt install python3-tk`
- **Error de permisos**: Usa `sudo` solo para instalar paquetes del sistema, no para pip
- **Python no encontrado**: Instala con `sudo apt install python3 python3-pip`

### macOS
- **Tkinter no funciona**: Instala con Homebrew: `brew install python-tk`
- **Certificados SSL**: Ejecuta `/Applications/Python\ 3.x/Install\ Certificates.command`
- **Permisos denegados**: Usa `sudo` solo si es necesario, prefiere Homebrew

---

## �️ Stack Tecnológico

- **Core Logic**: `mutagen` (Meta-tagging), `acoustid` (Chromaprint).
- **IA**: `openai` (GPT-4o-mini).
- **GUI**: `customtkinter` & `tkinter`.
- **Reporting**: Reportes CSV compatibles con Excel y reportes Markdown para GitHub.

---

## 📄 Licencia & Créditos

Distribuido bajo la Licencia MIT.
**Innovación impulsada por Iyov.**
*"Vamos a dejar tu música impecable."*
