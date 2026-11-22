# ProyectoFirebase — Mascotas con Cloud Firestore

App Android en Java para las actividades 3.1 y 3.2 de Programación Android (IEI-093):
escritura y lectura de datos en Cloud Firestore.

- Paquete: `com.stomas.proyectofirebase`
- Colección: `mascotas`
- Campos por documento: `codigo`, `nombre`, `dueno`, `direccion`
- `compileSdk` 34 · `minSdk` 24 · Gradle 8.14.6 · AGP 8.13.2 · BOM de Firebase 32.6.0

## Qué hace la app

1. `activity_main.xml`: formulario con cuatro campos y dos botones, más un `ListView`.
2. Botón **Enviar** → `enviarDatos()` escribe un documento nuevo en `mascotas` y muestra un `Toast`.
3. Botón **Cargar lista** → `cargarListaFirestore()` lee la colección y la publica en el `ListView`.

## Conectar tu propio proyecto de Firebase

El archivo `app/google-services.json` incluido es una **plantilla** con valores falsos: permite
compilar, pero no conecta con ninguna base real. Para dejarlo operativo:

1. Crear el proyecto en <https://console.firebase.google.com>.
2. Agregar una app Android con el paquete `com.stomas.proyectofirebase`.
3. Descargar `google-services.json` y reemplazar `app/google-services.json`.
4. En la consola: **Compilación → Firestore Database → Crear base de datos**, en modo de producción.
5. Crear la colección `mascotas` (el ID del documento puede ser automático).
6. En **Reglas**, para pruebas de la asignatura:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /mascotas/{documento} {
      allow read, write: if true;
    }
  }
}
```

> `if true` deja la base abierta. Sirve para la demostración, no para producción.

## Compilar

```bash
./gradlew assembleDebug
```

APK resultante: `app/build/outputs/apk/debug/app-debug.apk`.

## Documentación

- `docs/informe_unidad3_firebase.md` — informe completo (investigación, modelo de datos, procedimiento, verificación).
- `docs/Informe_Unidad3_Firebase.docx` — mismo informe en Word, con las capturas embebidas.
- `docs/Informe_3.1_Firebase.docx` — entregable de la actividad 3.1 (investigación, modelo de datos, cierre y anexo).
- `docs/Informe_3.2_Firebase.docx` — entregable de la actividad 3.2 (procedimiento, verificación y prueba en el teléfono).
- `docs/evidencias/` — capturas de la prueba en el dispositivo.
- `tools/md2docx.py` — genera los DOCX a partir del Markdown (soporta imágenes).
- `tools/split_informe.py` — parte el informe completo en los dos entregables.
- `firestore.rules` — reglas desplegadas en el proyecto `mascotas-firestore-u3`.
