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

## 📁 Inteligencia de Extracción de Rutas

La lógica de extracción ha sido refinada para interpretar tu estructura de carpetas de forma inteligente y precisa:

### Reglas de Extracción:

1. 🎹 **Banda / Artista**: Localizado en la carpeta **N-2** (dos niveles arriba del archivo)
   - Se normaliza a Title Case (primera letra de cada palabra en mayúscula)
   - Ejemplo: `caliban` → `Caliban`

2. 💿 **Disco & Año**: Extraídos de la carpeta **N-1** (padre directo)
   - Soporta el patrón `(YYYY) Nombre del Álbum`
   - El año debe estar entre paréntesis al inicio
   - El nombre del álbum se normaliza a Title Case
   - Ejemplo: `(2006) the undying darkness` → Año: `2006`, Álbum: `The Undying Darkness`

3. 🎵 **Pista & Título**: Parseados dinámicamente desde el nombre del archivo
   - Soporta múltiples formatos: `XX-Titulo`, `XX - Titulo`, `XX_Titulo`, `XX.Titulo`
   - El número de pista se normaliza a dos dígitos (formato XX)
   - El título se normaliza a Title Case
   - Se eliminan caracteres especiales y guiones bajos
   - Ejemplo: `02-No Lo Podras Sostener.mp3` → Track: `02`, Título: `No Lo Podras Sostener`

### Estructura Ideal:

```
Musica/
└── Metal/
    └── Caliban/                                    ← N-2: Artista
        └── (2006) The Undying Darkness/            ← N-1: (Año) Álbum
            ├── 01 - Intro.mp3                      ← Archivo: XX - Título
            ├── 02 - I Rape Myself.mp3
            └── 03 - Song About Killing.mp3
```

### Variaciones Soportadas:

El sistema es inteligente y reconoce múltiples formatos de nombres de archivo:

| Formato Original | Track | Título Extraído |
|-----------------|-------|-----------------|
| `02-No Lo Podras Sostener.mp3` | `02` | `No Lo Podras Sostener` |
| `07 - Track 07.mp3` | `07` | `Track 07` |
| `05-bad_dream-ube.mp3` | `05` | `Bad Dream Ube` |
| `11 - one more lie.mp3` | `11` | `One More Lie` |
| `10-Track-10.mp3` | `10` | `Track 10` |

### Casos Especiales:

**Álbumes con paréntesis en el nombre:**
```
(2005) Caliban & H.S.B. - The Split program 2 (Caliban Tracks)
```
- Año: `2005` (primer paréntesis)
- Álbum: `Caliban & H.S.B. - The Split Program 2 (Caliban Tracks)` (todo lo demás)

**Nombres de archivo sin número de track:**
```
intro.mp3 → Se asigna track 00 y título "Intro"
```

**Carpetas sin año:**
```
Back To School/ → Año: 0000, Álbum: "Back To School"
```

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

TuneaTuMusica garantiza que el 100% de tu biblioteca siga un estándar profesional de nomenclatura:

```
/[Nombre Banda]/([Año]) [Nombre del Disco]/[NumTrack] - [Nombre Canción].[Ext]
```

### Especificación Detallada:

| Componente | Ubicación | Formato | Ejemplo |
|------------|-----------|---------|---------|
| **Nombre Banda** | Carpeta N-2 (dos niveles arriba) | Title Case | `Caliban` |
| **Año** | Carpeta N-1 (dentro de paréntesis) | AAAA | `2006` |
| **Nombre del Disco** | Carpeta N-1 (después del paréntesis) | Title Case | `The Undying Darkness` |
| **Número de Track** | Inicio del nombre de archivo | XX (dos dígitos) | `02` |
| **Nombre Canción** | Después de "XX - " | Title Case | `I Rape Myself` |
| **Extensión** | Final del archivo | .mp3, .flac, etc. | `.mp3` |

### Ejemplos de Transformación:

**Ejemplo 1: Caso con guiones**
```
Antes: test/2x/(2002) Pateando Craneos/02-No Lo Podras Sostener.mp3
Después: 2x/(2002) Pateando Craneos/02 - No Lo Podras Sostener.mp3
```

**Ejemplo 2: Caso con espacios**
```
Antes: test/BTS Discos/(2004) Back To School/07 - Track 07.mp3
Después: Bts Discos/(2004) Back To School/07 - Track 07.mp3
```

**Ejemplo 3: Caso con guiones bajos**
```
Antes: test/Caliban/(2003) Shadow Hearts/05-bad_dream-ube.mp3
Después: Caliban/(2003) Shadow Hearts/05 - Bad Dream Ube.mp3
```

**Ejemplo 4: Caso con paréntesis en el nombre del disco**
```
Antes: test/Caliban/(2005) Caliban & H.S.B. - The Split program 2 (Caliban Tracks)/11 - one more lie.mp3
Después: Caliban/(2005) Caliban & H.S.B. - The Split Program 2 (Caliban Tracks)/11 - One More Lie.mp3
```

### Reglas de Normalización:

1. **Title Case**: Primera letra de cada palabra en mayúscula
2. **Separador estándar**: Siempre "XX - " (número, espacio, guión, espacio)
3. **Sin caracteres especiales**: Se eliminan: `\ / : * ? " < > | ,`
4. **Guiones bajos**: Se convierten en espacios
5. **Género**: Siempre se establece como "Metal" (simplificado según requerimiento)

---

## 📊 Los 4 Casos de Clasificación Inteligente

TuneaTuMusica no "adivina", aplica lógica de ingeniería para resolver el estado de cada archivo. El sistema analiza cada canción y determina automáticamente qué caso aplicar:

### 🟢 Caso A: "La Ruta Manda" (Ruta → Tags)

**Diagnóstico**: El nombre del archivo y su ubicación son correctos, pero los Tags internos están vacíos o incorrectos.

**Ejemplo**:
```
Archivo: Caliban/(2006) The Undying Darkness/01 - Intro.mp3
Tags internos: [Vacíos o "Unknown"]
```

**Acción**: El motor extrae la información de la ruta y **escribe los Tags** internos (ID3v1 e ID3v2).

**Resultado**:
- Title: `Intro`
- Artist: `Caliban`
- Album: `The Undying Darkness`
- Year: `2006`
- Genre: `Metal`
- Track: `01`

---

### 🔵 Caso B: "Los Tags Mandan" (Tags → Ruta)

**Diagnóstico**: El archivo tiene metadatos internos correctos, pero el nombre del archivo o la ruta son un desastre.

**Ejemplo**:
```
Archivo: test/BTS Discos/(2004) Back To School/08 - Track 08.mp3
Tags internos: Artist="Back To School", Title="Graduation Day", Album="BTS Compilation"
```

**Acción**: El motor usa los Tags para **renombrar y mover el archivo** a la estructura estándar.

**Resultado**:
```
Nuevo archivo: Back To School/(2004) Bts Compilation/08 - Graduation Day.mp3
```

---

### 🟡 Caso C: "Búsqueda de Identidad" (Internet/IA → Todo)

**Diagnóstico**: Ni la ruta ni los Tags tienen información válida. El archivo es un completo desconocido.

**Ejemplo**:
```
Archivo: test/Caliban/(2007) The Awakening/10-Track-10.mp3
Tags internos: [Vacíos o "Track 10"]
```

**Acción**: El motor activa dos sistemas de búsqueda en cascada:

1. **AcoustID + MusicBrainz**: "Escucha" el audio mediante fingerprinting acústico
2. **IA (GPT-4o-mini)**: Si el fingerprinting falla, la IA analiza el contexto

**Resultado**: Identifica la canción real y actualiza tanto el nombre del archivo como los Tags.

**Fuentes de búsqueda**:
- 🎵 **AcoustID**: Base de datos de huellas digitales de audio
- 🎼 **MusicBrainz**: Enciclopedia musical abierta
- 🤖 **OpenAI GPT-4o-mini**: Análisis inteligente de contexto

---

### ⚪ Caso D: "Estado Perfecto" (Validación)

**Diagnóstico**: El nombre del archivo está ordenado, los Tags coinciden perfectamente y la estructura de carpetas es correcta.

**Ejemplo**:
```
Archivo: Caliban/(2009) Say Hello To The Tragedy/08 - The Denegation Of Humanity.mp3
Tags: Todos correctos y coinciden con la ruta
```

**Acción**: **No hace nada**. Solo valida y marca como ✅ **100% Correcto**.

**Resultado**: El archivo se reporta como "Sin cambios" - ¡Misión cumplida!

---

## 🔍 Cómo Funciona el Análisis

El sistema recorre todas las subcarpetas de tu biblioteca musical y para cada archivo:

1. **Escaneo**: Lee los Tags actuales (ID3v1 e ID3v2)
2. **Análisis de Ruta**: Extrae información de la estructura de carpetas
3. **Clasificación**: Determina automáticamente el caso (A, B, C o D)
4. **Acción**: Aplica la solución correspondiente
5. **Reporte**: Documenta todos los cambios en CSV y Markdown

### Flujo de Decisión:

```
¿La ruta tiene info válida? ─┬─ SÍ ─┬─ ¿Los tags tienen info válida? ─┬─ SÍ → Caso D
                              │      └─ NO → Caso A
                              │
                              └─ NO ─┬─ ¿Los tags tienen info válida? ─┬─ SÍ → Caso B
                                     └─ NO → Caso C (búsqueda externa)
```

### Validación de Información:

El sistema considera información **válida** cuando:
- ✅ No está vacía
- ✅ No es "Unknown", "Untitled", "Track XX"
- ✅ No es "Artista Desconocido" o similar
- ✅ Tiene contenido significativo

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
