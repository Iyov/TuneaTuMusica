import { ID3Writer } from 'https://unpkg.com/browser-id3-writer@6.3.1/dist/browser-id3-writer.mjs';

let directoryHandle = null;
let files = [];
const btnSelect = document.getElementById('btnSelect');
const btnProcess = document.getElementById('btnProcess');
const btnDownloadReport = document.getElementById('btnDownloadReport');
const chkDryRun = document.getElementById('chkDryRun');
const logContent = document.getElementById('logContent');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const countUpdated = document.getElementById('countUpdated');
const countError = document.getElementById('countError');

let reportData = []; // Para el CSV

const log = (msg, type = 'info') => {
    const div = document.createElement('div');
    div.className = `p-2 rounded border-l-2 bg-white/5 ${type === 'success' ? 'border-emerald-500 text-emerald-400' : type === 'error' ? 'border-red-500 text-red-500' : 'border-slate-500 text-slate-400'}`;
    div.innerHTML = `<span class="opacity-50">[${new Date().toLocaleTimeString()}]</span> ${msg}`;
    logContent.prepend(div);
};

// Verificación de Compatibilidad y Seguridad
if (!window.showDirectoryPicker) {
    log("❌ El 'File System Access API' no está disponible.", "error");
    log("👉 Esto ocurre si usas un navegador no compatible (usa Chrome/Edge) o si abres el archivo como 'file://'.", "warning");
    log("💡 SOLUCIÓN: Ejecuta un servidor local (ej: 'npx serve .') o entra vía HTTPS.", "info");
    btnSelect.disabled = true;
    btnSelect.classList.add('opacity-50', 'cursor-not-allowed');
} else {
    log("🚀 TuneaTuMusica Web listo. Selecciona tu carpeta de música local.", "success");
    console.log("File System Access API detected successfully.");
}

// Capture global errors for debugging
window.addEventListener('error', (e) => {
    log(`🐞 Error detectado: ${e.message}`, 'error');
    console.error("Global error caught:", e);
});

btnSelect.onclick = async () => {
    console.log("Button 'Seleccionar Carpeta' clicked.");
    try {
    if (!window.showDirectoryPicker) throw new Error("API not supported in this context");
    
    directoryHandle = await window.showDirectoryPicker({ mode: 'readwrite' });
    console.log("Directory handle obtained:", directoryHandle.name);
    
    log(`📂 Escaneando carpeta: ${directoryHandle.name}...`, 'info');
    document.getElementById('folderInfo').classList.remove('hidden');
    document.getElementById('folderName').innerText = directoryHandle.name;
    
    files = [];
    
    // Recursive scan helper
    async function scanDirectory(handle, pathParts = []) {
        for await (const entry of handle.values()) {
        if (entry.kind === 'file' && /\.(mp3|flac)$/i.test(entry.name)) {
            files.push({handle: entry, pathParts: pathParts});
            if (files.length % 10 === 0) {
            document.getElementById('countUpdated').innerText = files.length;
            }
        } else if (entry.kind === 'directory') {
            await scanDirectory(entry, [...pathParts, entry.name]);
        }
        }
    }

    await scanDirectory(directoryHandle);
    
    btnProcess.disabled = files.length === 0;
    document.getElementById('countUpdated').innerText = files.length;
    log(`✨ Escaneo completado. ${files.length} archivos de audio listos.`, 'success');
    
    if (files.length === 0) {
        log("⚠️ No se encontraron archivos MP3 o FLAC en esta carpeta.", "warning");
    } else {
        log("👉 Presiona 'Tunea Tu Música' para comenzar el proceso.", "info");
    }
    } catch (err) {
    if (err.name !== 'AbortError') log(err.message, 'error');
    }
};

const esValido = (v) => {
    if (!v) return false;
    const lv = v.toLowerCase().trim();
    return !['', 'unknown', 'untitled', 'track', 'artista desconocido', 'desconocido'].includes(lv);
};

const sanitize = (name) => name ? name.replace(/[\\/:*?"<>|,]/g, '').trim() : '';

const toTitleCase = (text) => {
    if (!text) return text;
    // Eliminar comas completamente para evitar conflictos en CSV
    const cleanText = text.replace(/,/g, '').replace(/_/g, ' ');
    const exceptions = ['a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'from', 'by', 'of'];
    return cleanText.split(/\s+/).map((word, index) => {
    if (index > 0 && exceptions.includes(word.toLowerCase())) return word.toLowerCase();
    return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    }).join(' ');
};

btnProcess.onclick = async () => {
    const isDryRun = chkDryRun.checked;
    btnProcess.disabled = true;
    btnSelect.disabled = true;
    btnDownloadReport.disabled = true;
    
    // Header CSV más completo
    reportData = [["Ruta Original", "Artista", "Álbum", "Año", "Track", "Título", "Caso", "Resultado", "Mensaje"]];
    
    let okCount = 0;
    let errCount = 0;

    log(isDryRun ? "🧪 Iniciando SIMULACIÓN..." : "⚡ Iniciando PROCESO REAL...", isDryRun ? 'info' : 'warning');

    for (let i = 0; i < files.length; i++) {
    const item = files[i];
    const handle = item.handle;
    const pathParts = item.pathParts;
    const fullPath = [...pathParts, handle.name].join('/');

    try {
        const file = await handle.getFile();
        
        let tagsPrevios = { artist: null, album: null, year: null, track: null, title: null };
        let metadataError = null;

        // Intento de lectura de Metadatos (Búsqueda exhaustiva de la global)
        try {
        const mm = window.musicMetadata || window.mm || window.MusicMetadata;
        if (!mm) throw new Error("Librería de metadatos no cargada (Global not found)");
        const metadata = await mm.parseBlob(file);
        tagsPrevios = {
            artist: metadata.common.artist,
            album: metadata.common.album,
            year: metadata.common.year ? String(metadata.common.year) : null,
            track: metadata.common.track?.no ? String(metadata.common.track.no) : null,
            title: metadata.common.title
        };
        } catch (mErr) {
        metadataError = mErr.message;
        console.warn(`No se pudo leer metadata de ${handle.name}: ${mErr.message}`);
        }

        // Análisis de Ruta (N-1, N-2)
        let artistDir = null, albumDir = null, yearDir = null, trackName = null, titleName = null;

        if (pathParts.length >= 1) {
        const parentName = pathParts[pathParts.length - 1];
        const mAlbum = parentName.match(/^\((\d{4,})\)\s*(.+)$/);
        if (mAlbum) {
            yearDir = mAlbum[1];
            albumDir = toTitleCase(mAlbum[2]);
        } else {
            albumDir = toTitleCase(parentName);
        }
        }

        if (pathParts.length >= 2) {
        artistDir = toTitleCase(pathParts[pathParts.length - 2]);
        }

        const stem = handle.name.replace(/\.[^/.]+$/, "");
        const mName = stem.match(/^\s*(\d{1,2})\s*[-_.\s]+\s*(.+)$/);
        if (mName) {
        trackName = mName[1].padStart(2, '0');
        titleName = toTitleCase(mName[2]);
        } else {
        titleName = toTitleCase(stem);
        }

        const derivedPath = { artist: artistDir, album: albumDir, year: yearDir, track: trackName, title: titleName };

        // Evaluación de Casos según audio_tagger.py
        const pathHasInfo = esValido(derivedPath.artist) && esValido(derivedPath.title);
        const tagsHaveInfo = esValido(tagsPrevios.artist) && esValido(tagsPrevios.title);
        
        let f_artist, f_album, f_year, f_track, f_title, caso;

        if (pathHasInfo && tagsHaveInfo) {
        ({ artist: f_artist, album: f_album, year: f_year, track: f_track, title: f_title } = derivedPath);
        caso = 'D';
        } else if (pathHasInfo) {
        ({ artist: f_artist, album: f_album, year: f_year, track: f_track, title: f_title } = derivedPath);
        caso = 'A';
        } else if (tagsHaveInfo) {
        ({ artist: f_artist, album: f_album, year: f_year, track: f_track, title: f_title } = tagsPrevios);
        caso = 'B';
        } else {
        // Fallback total (Caso C/E)
        ({ artist: f_artist, album: f_album, year: f_year, track: f_track, title: f_title } = derivedPath);
        caso = metadataError ? 'E (Error Meta)' : 'C'; 
        }

        f_artist = toTitleCase(f_artist) || "Otros";
        f_album = toTitleCase(f_album) || "Otros";
        f_title = toTitleCase(f_title);
        f_year = f_year || "0000";
        f_track = (f_track || "00").padStart(2, '0');

        const extension = handle.name.split('.').pop();
        const newName = `${f_track} - ${sanitize(f_artist)} - ${sanitize(f_title)}.${extension}`;

        if (!isDryRun) {
        if (handle.name !== newName && handle.move) {
            await handle.move(newName);
        }
        if (handle.name.toLowerCase().endsWith('.mp3')) {
            const buffer = await file.arrayBuffer();
            const writer = new ID3Writer(buffer);
            writer.setFrame('TPE1', [f_artist]).setFrame('TIT2', f_title).setFrame('TCON', ['Metal']).setFrame('TALB', f_album).setFrame('TDRC', f_year).setFrame('TRCK', f_track);
            writer.addTag();
            const writable = await handle.createWritable();
            await writable.write(writer.arrayBuffer);
            await writable.close();
        }
        log(`✅ [Caso ${caso}] ${newName}`, 'success');
        } else {
        log(`🔍 [Simulado] ${fullPath} ➝ ${newName}`, 'info');
        }

        reportData.push([fullPath, f_artist, f_album, f_year, f_track, f_title, caso, "OK", isDryRun ? "Simulado" : "Actualizado"]);
        okCount++;
        countUpdated.innerText = okCount;
    } catch (err) {
        log(`❌ Error en ${handle.name}: ${err.message}`, 'error');
        reportData.push([fullPath, "-", "-", "-", "-", "-", "-", "ERROR", err.message]);
        errCount++;
        countError.innerText = errCount;
    }
    const pct = Math.round(((i + 1) / files.length) * 100);
    progressBar.style.width = `${pct}%`;
    progressText.innerText = `${pct}%`;
    }

    btnProcess.disabled = false;
    btnSelect.disabled = false;
    btnDownloadReport.disabled = false;
    log('✨ ¡Tuning completado! Ya podís bajar el reporte.', 'success');
};

btnDownloadReport.onclick = () => {
    // Usar punto y coma como separador para mayor compatibilidad en regiones de habla hispana
    const csvContent = reportData.map(e => e.map(cell => {
    let val = (cell || "").toString().replace(/"/g, '""');
    // Remover comas residuales por seguridad extrema
    val = val.replace(/,/g, '');
    return `"${val}"`;
    }).join(";")).join("\n");
    // Agregar BOM (\uFEFF) para que Excel reconozca UTF-8 con tildes y ñ
    const blob = new Blob(["\uFEFF", csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    const now = new Date();
    const pad = (n) => String(n).padStart(2, '0');
    const datePart = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
    const timePart = `${pad(now.getHours())}-${pad(now.getMinutes())}-${pad(now.getSeconds())}`;
    const ts = `${datePart}_${timePart}`;
    link.setAttribute("href", url);
    link.setAttribute("download", `Reporte_TuneaTuMusica_${ts}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    log("📥 Reporte descargado (UTF-8 OK).", "success");
};

// Scroll to Top Button Functionality
(function() {
  const scrollToTopBtn = document.getElementById('scrollToTop');
  
  if (scrollToTopBtn) {
    // Show/hide button based on scroll position
    window.addEventListener('scroll', function() {
      if (window.pageYOffset > 300) {
        scrollToTopBtn.classList.add('visible');
      } else {
        scrollToTopBtn.classList.remove('visible');
      }
    });
    
    // Smooth scroll to top when clicked
    scrollToTopBtn.addEventListener('click', function() {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }
})();