# CachaTuMusica 🎵 — Edición Pro

**CachaTuMusica** es una solución profesional para la organización y optimización de metadatos de bibliotecas musicales. Diseñada para transformar el caos en orden, esta suite combina extracción inteligente basada en rutas, identificación acústica (AcoustID) y potencia de IA (GPT-4) para garantizar que cada canción esté perfectamente etiquetada y nombrada.

> � **Edición Pro**: Máxima precisión, automatización refinada y seguridad total.

---

## ✨ Características Premium

- 🖥️ **Interfaz Vanguardista**: UI optimizada con **CustomTkinter**, diseñada para la eficiencia.
- 🧹 **Edición Ordenaito**: Renombrado automático bajo el estándar estricto `NN - Artista - Título.ext`.
- 🔍 **Prevalidación Diagnóstica**: Escaneo profundo que predice cada cambio antes de que ocurra.
- 🎯 **Audio Fingerprinting**: Tecnología AcoustID para identificación sin errores.
- 🤖 **IA Fallback Engine**: GPT-4o-mini para resolver metadatos desde contextos complejos si el fingerprint falla.
- 📊 **Taxonomía de Casos (A-D)**: Clasificación inteligente para aplicar la acción exacta necesaria.
- 🧪 **Sandbox Real-File**: Suite de pruebas que opera sobre tu biblioteca real en modo simulación (Dry-run).
- �️ **Seguridad Bancaria**: Backups automáticos `.backup_YYMMDD/` y reportes CSV/MD detallados.

---

## 📁 Inteligencia de Rutas (Edición Ordenaito)

La lógica de extracción ha sido refinada para interpretar tu estructura de carpetas de forma humana:

1.  🎹 **Banda / Artista**: Localizado en la carpeta **N-2** (dos niveles arriba del archivo).
2.  💿 **Disco & Año**: Extraídos de la carpeta **N-1** (padre directo). Soporta el patrón `(YYYY) Nombre del Álbum`.
3.  🎵 **Pista & Título**: Parseados dinámicamente desde el nombre del archivo, eliminando el "ruido" de caracteres especiales.

**Estructura Ideal:**
`Musica/Metal/Caliban/(2006) The Undying Darkness/01 - Intro.mp3`

---

## 📊 Matriz de Clasificación (Casos A-D)

El motor centralizado en `audio_tagger.py` opera bajo un sistema de 4 estados:

| Caso | Diagnóstico | Acción del Motor |
| :--- | :--- | :--- |
| **Caso A** | Nombre/Ruta válidos pero Tags incompletos. | **Escribe Tags**: Sincroniza la info del disco con los metadatos internos. |
| **Caso B** | Tags válidos pero Nombre inconsistente. | **Renombra Archivo**: Aplica el patrón `NN - Artista - Título` al disco. |
| **Caso C** | Identidad desconocida (Nombre genérico y sin Tags). | **Lookup Externo**: Activa Fingerprinting o IA para descubrir la identidad. |
| **Caso D** | Archivo en estado perfecto. | **Verificación**: Solo valida consistencia y emite reporte de éxito. |

---

## 🚀 Guía de Inicio Rápido

### Instalación
```bash
git clone https://github.com/Iyov/CachaTuMusica.git
cd CachaTuMusica
pip install -r requirements.txt
```

### Uso Recomendado (GUI)
Lanza la interfaz principal para un control total:
```bash
python gui.py
```

### Verificación Segura (Sandbox)
Si querés ver qué haría el motor con tu música actual sin modificar nada:
```bash
python sandbox_test.py
```
*Este comando corre automáticamente en modo **--dry-run** sobre tu carpeta `test/`.*

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
