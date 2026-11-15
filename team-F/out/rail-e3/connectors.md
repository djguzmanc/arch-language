# Connectors of Rail

| ID | Source → Target | Nature | Coupling | Information carried | Boundary |
|----|-----------------|--------|----------|---------------------|----------|
| F_K1 | Consola del CCF → Servicio de planificación y despacho | Dependency | Blocking | Órdenes de planificación y despacho, y consultas de estado | No |
| F_K2 | Consola de terminal férrea → carga-ms; Consola de terminal férrea → trenes-ms; Consola de terminal férrea → reservas-ms | Dependency | Blocking | Registro de cargue, descargue y composición, y consultas de reservas | No |
| F_K3 | Servicio de planificación y despacho → reservas-ms | Dependency | Blocking | Reserva de capacidad de corredor y terminal para el surco planificado | No |
| F_K4 | Servicio de planificación y despacho → trenes-ms | Dependency | Blocking | Composición y disponibilidad de locomotoras y vagones | No |
| F_K5 | Servicio de planificación y despacho → Enclavamiento | Control command | Blocking | Solicitudes de ruta para el tren que se despacha | No |
| F_K6 | Enclavamiento → Servicio de planificación y despacho | Event notification | Supply | Resultado de las solicitudes de ruta, ocupación y alarma de secciones en falla segura | No |
| F_K7 | Enclavamiento → Servicio de autoridad de movimiento (SAM) | Event notification | Supply | Estado de rutas, agujas y señales cuando cambian | No |
| F_K8 | Enclavamiento → Aparatos de vía (agujas y señales) | Control command | Sink | Órdenes de posición de agujas y de aspecto de señales | No |
| F_K9 | Detectores de vía → Concentrador de equipos de campo | Data flow | Supply | Paso de trenes y ocupación de secciones, en el formato de cada fabricante | No |
| F_K10 | Lector de identificación de vagones → Concentrador de equipos de campo | Data flow | Supply | Identificación de vagones y contenedores al entrar y salir de la terminal | No |
| F_K11 | Concentrador de equipos de campo → Enclavamiento | Data flow | Supply | Resumen del estado cada 0,4 s con marca de tiempo, además de los cambios | No |
| F_K12 | Concentrador de equipos de campo → Broker de eventos férreos | Event notification | Sink | Paso de trenes; las lecturas de acceso van al canal crítico | No |
| F_K13a | Unidad a bordo → Radio tren–tierra → Servicio de autoridad de movimiento (SAM) | Data flow | Supply | Reportes de posición del tren, autenticados y cifrados | No |
| F_K13b | Servicio de autoridad de movimiento (SAM) → Radio tren–tierra → Unidad a bordo | Control command | Supply | Autoridades de movimiento, autenticadas y cifradas | No |
| F_K14 | Sensores de la locomotora → Unidad a bordo | Data flow | Supply | Velocidad, distancia recorrida y condiciones físicas del tren | No |
| F_K15 | Unidad a bordo → Actuador de freno | Control command | Sink | Órdenes de frenado | No |
| F_K16 | Unidad a bordo → Interfaz del maquinista (DMI) | Data flow | Supply | Velocidad permitida, límite de la autoridad e instrucciones a mostrar | No |
| F_K17 | Unidad a bordo → Registrador jurídico de a bordo (JRU) | Data flow | Sink | Datos de a bordo a registrar | No |
| F_K18 | Servicio de autoridad de movimiento (SAM) → Broker de eventos férreos | Event notification | Sink | Posición de los trenes y autoridades otorgadas | No |
| F_K19 | Servicio de planificación y despacho → Broker de eventos férreos; carga-ms → Broker de eventos férreos | Event notification | Sink | Custodia y composición despachada, por el canal crítico | No |
| F_K20 | Broker de eventos férreos → posicion-ms | Event notification | Supply | Posiciones, llegadas y salidas | No |
| F_K26 | Broker de eventos férreos → carga-ms | Event notification | Supply | Cargue, descargue y transferencias de custodia (CR1) | No |
| F_K27 | Broker de eventos férreos → Repositorio histórico operacional | Event notification | Sink | Eventos operacionales para el histórico (CR1) | No |
| F_K21 | Broker de eventos férreos → Traductor canónico → Rail Gateway | Event notification | Sink | Custodia y composición (canal crítico), posición y eventos de vía, en el modelo canónico | No |
| F_K22 | trenes-ms → trenes-db; carga-ms → carga-db; posicion-ms → posicion-db; reservas-ms → reservas-db | Dependency | Blocking | Lecturas y escrituras de los datos de cada servicio | No |
| F_K23a | Rail Gateway → Traductor canónico → reservas-ms; Rail Gateway → Traductor canónico → trenes-ms; Rail Gateway → Traductor canónico → posicion-ms | Dependency | Blocking | Solicitudes de capacidad, en paralelo, timeout de 300 ms y un reintento | No |
| F_K23b | reservas-ms → Traductor canónico → Rail Gateway; trenes-ms → Traductor canónico → Rail Gateway; posicion-ms → Traductor canónico → Rail Gateway | Data flow | Blocking | Capacidad, plataforma, ventana y arribo previsto; rechazo explícito si vence el reintento | No |
| F_K24a | Servicio de planificación y despacho → Traductor canónico → Rail Gateway | Dependency | Blocking | Avisos de convoy de exportación y solicitudes de camiones (SoS-K22a, SoS-K23a, SoS-K25a) | No |
| F_K24b | Rail Gateway → Traductor canónico → Servicio de planificación y despacho | Data flow | Blocking | Zona, ventana de descargue y citas de retiro (SoS-K22b, SoS-K23b, SoS-K25b) | No |
| F_K25a | carga-ms → Traductor canónico → Rail Gateway | Dependency | Blocking | Consulta de estado consolidado de la carga (sale por SoS-K18a) | No |
| F_K25b | Rail Gateway → Traductor canónico → carga-ms | Data flow | Supply | Estado consolidado de la carga consultada (llega por SoS-K18b) | No |
| F_K28a | arribos-ms → Traductor canónico → Rail Gateway | Dependency | Blocking | Consulta del estado de camiones con destino férreo (sale por SoS-K18a), máximo 2/s | No |
| F_K28b | Rail Gateway → Traductor canónico → arribos-ms | Data flow | Supply | Posición y ETA con fuente e incertidumbre (llega por SoS-K18b) | No |
| F_K29 | Rail Gateway → Traductor canónico → arribos-ms | Event notification | Supply | Estado de servicio de un constituyente (llega por SoS-K34) | No |
| F_K30 | arribos-ms → reservas-ms | Data flow | Supply | ETA e incertidumbre por ventana de transferencia | No |
| F_K31 | arribos-ms → Servicio de planificación y despacho | Event notification | Supply | Modo degradado activo o inactivo; unidades que no llegaron al cierre | No |
| F_K32 | Broker de eventos férreos → arribos-ms | Event notification | Supply | Lecturas de acceso que confirman la llegada física | No |
| F_K33 | arribos-ms → arribos-db | Dependency | Blocking | Lecturas y escrituras de ETA, unidades pendientes y modo degradado | No |
| F_K34a | Unidad a bordo → Radio tren–tierra B → Servicio de autoridad de movimiento (SAM) | Data flow | Supply | Reportes de posición por el camino B | No |
| F_K34b | Servicio de autoridad de movimiento (SAM) → Radio tren–tierra B → Unidad a bordo | Control command | Supply | Autoridades de movimiento por el camino B | No |
| F_K35 | Sensores de la locomotora B → Unidad a bordo | Data flow | Supply | Velocidad y distancia, segunda medición | No |
| F_K36 | Servicio de autoridad de movimiento (SAM) → SAM de respaldo (SAM-B) | Data flow | Supply | Latido cada 0,5 s y último estado de autoridad de cada tren | No |
| F_K37 | Enclavamiento → SAM de respaldo (SAM-B) | Event notification | Supply | Estado de rutas hacia el respaldo | No |
| F_K38a | reservas-ms → Caché de capacidad | Dependency | Blocking | Consulta de capacidad calculada | No |
| F_K38b | Caché de capacidad → reservas-ms | Data flow | Blocking | Capacidad calculada (respuesta de F-K38a) | No |
| F_K39 | reservas-ms → Caché de capacidad | Data flow | Supply | Actualización tras cada reserva o cambio de surco | No |
| SoS_K3a | Road Gateway → Rail Gateway | Dependency | Blocking | Solicitud de capacidad y turno de transferencia camión-tren | Yes |
| SoS_K3b | Rail Gateway → Road Gateway | Data flow | Blocking | Confirmación de programación y plataforma, o rechazo | Yes |
| SoS_K7a | Pacific Port Gateway → Rail Gateway | Dependency | Blocking | Unidades listas para transferencia patio-tren y solicitud de vagones | Yes |
| SoS_K7b | Rail Gateway → Pacific Port Gateway | Data flow | Blocking | Confirmación de convoy, capacidad, plataforma y ventana, o rechazo | Yes |
| SoS_K13 | Rail Gateway → National Coordination Gateway | Event notification | Sink | Custodia recibida por el concesionario y composición del tren | Yes |
| SoS_K14 | Rail Gateway → National Coordination Gateway | Event notification | Supply | Posición del convoy, estado del corredor y eventos de vía | Yes |
| SoS_K18a | Rail Gateway → National Coordination Gateway | Dependency | Blocking | Consulta de estado consolidado de la carga en la que participa el concesionario | Yes |
| SoS_K18b | National Coordination Gateway → Rail Gateway | Data flow | Blocking | Estado consolidado limitado a su carga; v3: posición y ETA estimadas | Yes |
| SoS_K22a | Rail Gateway → Pacific Port Gateway | Dependency | Blocking | Aviso de convoy de exportación y solicitud de zona y ventana de descargue | Yes |
| SoS_K22b | Pacific Port Gateway → Rail Gateway | Data flow | Blocking | Zona de patio, punto y ventana de descargue, o rechazo | Yes |
| SoS_K23a | Rail Gateway → Road Gateway | Dependency | Blocking | Solicitud de camiones para retirar unidades en terminal férrea | Yes |
| SoS_K23b | Road Gateway → Rail Gateway | Data flow | Blocking | Vehículos asignados y cita de retiro, o rechazo | Yes |
| SoS_K24a | Caribbean Port Gateway → Rail Gateway | Dependency | Blocking | Unidades listas para transferencia patio-tren y solicitud de vagones | Yes |
| SoS_K24b | Rail Gateway → Caribbean Port Gateway | Data flow | Blocking | Confirmación de convoy, capacidad, plataforma y ventana, o rechazo | Yes |
| SoS_K25a | Rail Gateway → Caribbean Port Gateway | Dependency | Blocking | Aviso de convoy de exportación y solicitud de zona y ventana de descargue | Yes |
| SoS_K25b | Caribbean Port Gateway → Rail Gateway | Data flow | Blocking | Zona de patio, punto y ventana de descargue, o rechazo | Yes |
| SoS_K34 | National Coordination Gateway → Rail Gateway | Event notification | Sink | Estado de servicio de un constituyente: degradado o restablecido | Yes |
| SoS_K5 | Road Gateway → National Coordination Gateway | Event notification | Sink | Custodia recibida por el transportador; v3: ETA al despachar | Yes |
