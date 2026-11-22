# Informe Actividad 3.1 — Manejo de base de datos externa (Firebase)

**Autor:** Samuel Eduardo Bugueno Vega
**Fecha:** 22 de noviembre de 2026
**Proyecto de Firebase:** `mascotas-firestore-u3`
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

### 1.2 Modelo de datos que usé en la app

Elegí **Cloud Firestore** como base de datos, en modo de producción, con reglas abiertas solo
para la etapa de pruebas de la asignatura. Diseñé la colección así:

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

Comparé la tabla anterior con lo que implementé: la pauta muestra la sintaxis de la API web, que se
ejecuta en un navegador. En Android el flujo es el mismo (referencia → escritura → lectura), pero
cambié el objeto de acceso (`FirebaseFirestore` en lugar de `firebase.database()`), el tipo de
resultado (`Task` en lugar de promesa) y acepté que las llamadas son asíncronas y me devuelven
`onSuccess`/`onFailure` en callbacks, no en la línea siguiente.
### 1.3 Preguntas de cierre — Actividad 3.1

**¿Qué aprendiste de la actividad realizada?**
Aprendí que integrar una base de datos externa no empieza en el código: empieza en la consola,
registrando el paquete exacto de la app y bajando un archivo de configuración. Comprobé que si el
`applicationId` y el `package_name` del `google-services.json` no coinciden letra por letra, el
plugin falla al compilar con *"File google-services.json is missing"* o con un error de coincidencia
de paquete. También aprendí que las escrituras y lecturas son asíncronas y que por eso actualicé la
interfaz en callbacks, no en la línea siguiente a la llamada.

**¿En qué ámbitos puedes utilizar o aplicar lo realizado?**
Lo puedo aplicar en cualquier app que necesite datos compartidos entre dispositivos sin montar un
servidor propio: registro de clientes, inventario, pedidos, asistencia, catálogos, encuestas. Me es
directamente aplicable al proyecto de huerto inteligente, donde la app debe guardar lecturas de
sensores y registros de riego consultables desde varios teléfonos.

**¿Qué aprendiste de Firebase y los conceptos estudiados?**
Aprendí que Firebase es un conjunto de servicios y no solo una base de datos, y que elegir el
servicio correcto importa: Firestore para registros estructurados con consultas, Realtime Database
para datos que cambian muchas veces por segundo, Storage para archivos, Authentication para
identidad y Cloud Messaging para avisos. Sobre las tecnologías de transporte: MQTT es el protocolo
del mundo de los sensores, WebSocket el del tiempo real en la web, y Firestore esconde ambos detrás
de su SDK.

---

## Anexo — Repaso final del material: necesidad técnica y componente

| Necesidad | Componente |
| --- | --- |
| Subir la foto en alta resolución de la tomatera | Cloud Storage |
| Avisarme al móvil si hay riesgo de heladas | Cloud Messaging |
| Ver la humedad actual cambiando en pantalla sin recargar | Realtime Database |
| Entrar a la app con mi correo electrónico | Authentication |
| Guardar el registro estructurado de riegos de cada mes | Cloud Firestore |
