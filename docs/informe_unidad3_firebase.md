# Informe Unidad 3 — Firebase en Android

**Asignatura:** Programación Android (IEI-093)
**Actividades:** 3.1 Manejo de base de datos externa – Firebase · 3.2 Desarrollo de funcionalidades avanzadas con Firebase
**Proyecto:** `ProyectoFirebase` — paquete `com.stomas.proyectofirebase`
**Entorno:** Android Studio, Java 17, Gradle 8.14.6, compileSdk 34, Cloud Firestore

---

## 1. Actividad 3.1 — Base de datos externa con Firebase

### 1.1 Investigación

**¿Qué es Firebase?**
Firebase es una plataforma de servicios de backend (BaaS) de Google. Entrega infraestructura ya
operativa para que la app no tenga que implementar servidores propios: base de datos en tiempo real
(Realtime Database), base de datos documental (Cloud Firestore), autenticación de usuarios
(Authentication), almacenamiento de archivos (Cloud Storage), notificaciones push (Cloud Messaging),
analítica de uso (Analytics), hosting web (Hosting) y lógica en el servidor (Cloud Functions).

**¿Cómo se conecta una aplicación Android a Firebase?**
1. Crear un proyecto en la consola de Firebase (`console.firebase.google.com`).
2. Registrar la app Android indicando el nombre del paquete, que debe coincidir exactamente con el
   `applicationId` del proyecto (`com.stomas.proyectofirebase`). Para Authentication con proveedores
   federados además se registra la huella SHA-1 de la firma.
3. Descargar `google-services.json` y ubicarlo en la carpeta `app/` del proyecto.
4. Declarar el plugin de Google Services en Gradle: en el `build.gradle` del proyecto
   `id 'com.google.gms.google-services' version '4.4.3' apply false`, y en el `build.gradle` del
   módulo `app` el mismo plugin sin versión, junto con las dependencias de Firebase y el BOM que
   alinea sus versiones.
5. Sincronizar Gradle. El SDK se inicializa solo: el plugin genera valores de recursos a partir del
   JSON y la librería `firebase-common` los lee al arrancar la app, sin código de inicialización
   manual en `MainActivity`.
6. En la consola, crear la base de datos (Firestore) y ajustar las reglas de acceso.

**¿Qué tipos de datos se pueden enviar a Firebase?**
En Cloud Firestore un documento es un mapa de campos, con estos tipos: texto (`String`), números
enteros y decimales (`long`/`double`), booleanos, fecha y hora (`Timestamp`), coordenadas
(`GeoPoint`), referencia a otro documento (`DocumentReference`), arreglos (`List`), mapas anidados
(`Map`) y datos binarios (`Blob`/`byte[]`). El documento completo no puede superar 1 MiB y no admite
arreglos dentro de arreglos. En Realtime Database el modelo es un árbol JSON, por lo que solo se
envían objetos, arreglos, textos, números y booleanos.

**¿Qué es el protocolo MQTT?**
MQTT (Message Queuing Telemetry Transport) es un protocolo de mensajería del tipo publicador /
suscriptor pensado para dispositivos con poco ancho de banda y energía. Un *broker* central recibe
los mensajes y los entrega a quienes están suscritos a un *tópico*. Trabaja sobre TCP en los puertos
1883 (sin cifrar) y 8883 (TLS), y define tres niveles de calidad de servicio: QoS 0 (como máximo una
vez), QoS 1 (al menos una vez) y QoS 2 (exactamente una vez). Es el estándar de facto en IoT.

**¿Cómo se envían datos a través de ese protocolo?**
Se necesita un cliente MQTT en el dispositivo, por ejemplo Eclipse Paho o HiveMQ para Android. El
cliente se conecta al broker con un identificador y credenciales, publica en un tópico con
`publish(topico, payload, qos, retained)` y se suscribe con `subscribe(topico, qos)`. El payload es
texto libre, por lo que en la práctica se envía un JSON con las lecturas del sensor.

**¿Qué aplicaciones se pueden diseñar uniendo Firebase con MQTT?**
Sistemas de monitoreo y control: huerto o invernadero inteligente (sensores de humedad y temperatura
que publican por MQTT, un servicio intermedio guarda las lecturas en Firestore y la app las muestra),
domótica, telemetría de vehículos, control de riego, medidores de consumo eléctrico y agricultura de
precisión. La regla general es MQTT para el tramo dispositivo → servidor, porque es liviano y
bidireccional, y Firebase para el tramo servidor → app, porque aporta persistencia, autenticación y
consultas.

**¿Qué es un WebSocket?**
Es un protocolo de comunicación bidireccional y persistente sobre una única conexión TCP. Se abre con
un handshake HTTP (`Upgrade: websocket`) y, una vez establecido, cliente y servidor envían tramas en
cualquier momento sin volver a negociar. Firestore usa esta familia de canales para sus escuchas en
tiempo real: por eso una app puede recibir cambios sin recargar la pantalla ni hacer sondeos
periódicos.

### 1.2 Modelo de datos usado en la app

Base de datos: **Cloud Firestore**, en modo de producción, con reglas abiertas solo para la etapa de
pruebas de la asignatura.

```
mascotas (colección)
└── {idAutomático} (documento)
    ├── codigo:    string
    ├── nombre:    string
    ├── dueno:     string   (el docente la escribe "dueño"; Firestore admite tildes,
    └── direccion: string    se dejó sin tilde para evitar problemas de codificación)
```

Equivalencia entre los ejemplos de la pauta (JavaScript, API web) y el código Android entregado:

| Ejemplo de la pauta | Implementación en `MainActivity.java` |
| --- | --- |
| `firebase.database()` | `FirebaseFirestore.getInstance()` |
| `ref('users/' + userId).set({...})` | `db.collection("mascotas").add(mascota)` — devuelve el ID automático |
| `update(updates)` con dos rutas | No usado: escribir en dos colecciones es innecesario con un solo documento |
| `push().key` | `DocumentReference.getId()` del `addOnSuccessListener` |
| Lectura de datos | `db.collection("mascotas").get()` + `QueryDocumentSnapshot` |

La diferencia de fondo: la pauta muestra la sintaxis de la API web, que se ejecuta en un navegador.
En Android el flujo es el mismo (referencia → escritura → lectura), pero cambian el objeto de acceso
(`FirebaseFirestore`), el tipo de tarea (`Task`) y el hecho de que las llamadas son asíncronas y
devuelven `onSuccess`/`onFailure`.
### 1.3 Preguntas de cierre — Actividad 3.1

**¿Qué aprendiste de la actividad realizada?**
Que integrar una base de datos externa no empieza en el código: empieza en la consola, registrando el
paquete exacto de la app y bajando un archivo de configuración. Si el `applicationId` y el
`package_name` del `google-services.json` no coinciden letra por letra, el plugin falla al compilar
con *"File google-services.json is missing"* o con un error de coincidencia de paquete. También
aprendí que las escrituras y lecturas son asíncronas y que por eso la interfaz se actualiza en
callbacks, no en la línea siguiente a la llamada.

**¿En qué ámbitos puedes utilizar o aplicar lo realizado?**
En cualquier app que necesite datos compartidos entre dispositivos sin montar un servidor propio:
registro de clientes, inventario, pedidos, asistencia, catálogos, encuestas. Es directamente aplicable
al proyecto de huerto inteligente, donde la app debe guardar lecturas de sensores y registros de riego
consultables desde varios teléfonos.

**¿Qué aprendiste de Firebase y los conceptos estudiados?**
Que Firebase es un conjunto de servicios y no solo una base de datos, y que elegir el servicio correcto
importa: Firestore para registros estructurados con consultas, Realtime Database para datos que cambian
muchas veces por segundo, Storage para archivos, Authentication para identidad y Cloud Messaging para
avisos. Sobre las tecnologías de transporte: MQTT es el protocolo del mundo de los sensores, WebSocket
el del tiempo real en la web, y Firestore esconde ambos detrás de su SDK.

---

## 2. Actividad 3.2 — Funcionalidades avanzadas con Firebase

### 2.1 Procedimiento ejecutado

1. Proyecto Android nuevo, lenguaje Java, paquete `com.stomas.proyectofirebase`.
2. `google-services.json` en la carpeta `app/`.
3. Plugins y dependencias en Gradle:

```gradle
// build.gradle (proyecto)
plugins {
    id 'com.android.application' version '8.13.2' apply false
    id 'com.google.gms.google-services' version '4.4.3' apply false
}

// app/build.gradle
plugins {
    id 'com.android.application'
    id 'com.google.gms.google-services'
}
dependencies {
    implementation platform('com.google.firebase:firebase-bom:32.6.0')
    implementation 'com.google.firebase:firebase-firestore'
    implementation 'com.google.firebase:firebase-analytics'
}
```

4. `activity_main.xml`: cuatro `EditText` (`edtCodigo`, `edtNombre`, `edtDueno`, `edtDireccion`), dos
   `Button` conectados por `android:onClick` y un `ListView` (`listaMascotas`).
5. `MainActivity.java`: `enviarDatos(View)` escribe con `add(mascota)` y muestra un `Toast` de
   confirmación; `CargarLista(View)` delega en `cargarListaFirestore()`, que lee la colección con
   `get()`, arma una línea por documento y la publica en el `ListView` con `ArrayAdapter` sobre
   `android.R.layout.simple_list_item_1`.
6. Reglas de Firestore para la etapa de pruebas:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /mascotas/{documento} {
      allow read, write: if true;   // solo para pruebas de la asignatura
    }
  }
}
```

> Advertencia: `allow read, write: if true` deja la base abierta a cualquiera que conozca el proyecto.
> Sirve para la demostración, no para producción; el paso siguiente es exigir `request.auth != null`.

### 2.2 Diferencias respecto del paso a paso de la pauta

| Punto de la pauta | Decisión tomada | Motivo |
| --- | --- | --- |
| `firebase-firestore:23.0.0` fijado a mano | Se dejó sin versión, administrado por el BOM 32.6.0 | Fijar una versión de 2021 junto al BOM crea dos fuentes de verdad y conflictos de dependencias |
| `com.android.support:multidex:1.0.3` | Se omitió | Es la biblioteca antigua, incompatible con AndroidX, y con `minSdk 24` la multidex es nativa |
| Cambiar `compileSdkVersion` de 33 a 34 | Se usó `compileSdk 34` desde el inicio | Evita el error de compilación que la pauta corrige a mitad de camino |
| `Toast` con texto literal | Se usaron recursos en `strings.xml` | Permite traducir y centralizar los mensajes |
| Sin validación del formulario | Se valida que los cuatro campos tengan contenido | Evita documentos con campos vacíos, que luego se ven como filas incompletas |

### 2.3 Funcionalidades avanzadas: estado dentro de la entrega

La descripción de la actividad menciona autenticación, almacenamiento de archivos, notificaciones
push y analítica. El paso a paso entregado por el docente solo desarrolla Firestore, y eso es lo que
está implementado y verificado con compilación real. Estado por funcionalidad:

- **Cloud Firestore (implementado):** escritura y lectura de la colección `mascotas`.
- **Analytics (incluido):** la dependencia `firebase-analytics` queda activa; los eventos se registran
  en la consola sin código adicional.
- **Authentication (documentado, no implementado):** requiere registrar la huella SHA-1 en la consola
  y un formulario de acceso; queda como siguiente paso del proyecto.
- **Cloud Storage (documentado, no implementado):** requiere habilitar el *bucket* y permisos de
  lectura de archivos; se aplica a la foto de la mascota o de la planta.
- **Cloud Messaging (documentado, no implementado):** requiere un servidor o Cloud Function que emita
  la notificación; se aplica a la alerta de heladas del proyecto de huerto.

### 2.4 Preguntas de cierre — Actividad 3.2

**¿Qué aprendiste de la actividad realizada?**
Que la parte difícil de Firebase no es la base de datos sino la configuración: plugin de Google
Services, archivo JSON, BOM de versiones y reglas de seguridad. También que el resultado de una
escritura se confirma en un callback, y que refrescar la lista exige volver a consultar o mantener un
escucha activo con `addSnapshotListener`.

**¿En qué ámbitos puedes utilizar o aplicar lo realizado?**
En inventarios y registros de cualquier tipo donde varias personas deban ver los mismos datos al
instante: bodega de una empresa, control de asistencia, catálogo de productos, registro de riegos de
un huerto. El mismo patrón formulario + lista sirve como base de cualquier CRUD en la nube.

**¿Pudiste realizar toda la actividad con los ejemplos entregados?**
Sí, con tres ajustes: la versión de Firestore se dejó al BOM, se omitió la biblioteca antigua de
multidex y se usó `compileSdk 34` desde el principio para no repetir el error que la propia pauta
corrige. La conexión contra la base real exige reemplazar `app/google-services.json`, que es un
archivo generado con la cuenta del estudiante; mientras no se reemplace, la app compila pero no puede
autenticarse contra el proyecto de Firebase.

---

## Anexo — Repaso final del material: necesidad técnica y componente

| Necesidad | Componente |
| --- | --- |
| Subir la foto en alta resolución de la tomatera | Cloud Storage |
| Avisarme al móvil si hay riesgo de heladas | Cloud Messaging |
| Ver la humedad actual cambiando en pantalla sin recargar | Realtime Database |
| Entrar a la app con mi correo electrónico | Authentication |
| Guardar el registro estructurado de riegos de cada mes | Cloud Firestore |
