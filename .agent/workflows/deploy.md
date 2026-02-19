---
description: Cómo probar y desplegar los cambios en GitHub Pages
---

# 🚀 Workflow de Despliegue

Sigue estos pasos para verificar y subir los cambios sin errores.

## 1. Verificación Local (Crítico para la Web Edition)
La Web Edition usa APIs modernas que requieren un contexto seguro (HTTPS o localhost). Para probarla:
1. Abre una terminal en la raíz del proyecto.
2. Ejecuta: `npx serve .` (si tienes Node.js) o usa la extensión "Live Server" de VS Code.
3. Entra a `http://localhost:3000/web.html`.
4. Verifica que el botón "Seleccionar Carpeta" abra el selector del sistema.

## 2. Checklist de GitHub Pages
- [ ] **Rutas**: Verifica que el logo sea `img/TuneaTuMusica_Logo_SF.png`.
- [ ] **Consola**: Abre F12 y revisa que no haya errores de "404 Not Found" en imágenes o scripts.
- [ ] **SEO**: Valida que el `<title>` y las `<meta>` tags aparezcan correctamente en el código fuente.

## 3. Comandos de Git para el Despliegue
// turbo
```powershell
# 1. Añadir cambios
git add .

# 2. Commit con descripción de la Web Edition
git commit -m "feat: implement Web Edition (No-Install), update logo SF & SEO"

# 3. Subir a GitHub
git push origin main
```

Una vez hecho el push, GitHub Pages se actualizará automáticamente en un par de minutos.
