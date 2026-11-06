# Connectors of SoS

| ID | Source → Target | Nature | Coupling | Information carried | Boundary |
|----|-----------------|--------|----------|---------------------|----------|
| SoS_K1a | Road Gateway → Caribbean Port Gateway | Dependency | Blocking | Solicitud de cita portuaria y programación de camión y conductor | Yes |
| SoS_K1b | Caribbean Port Gateway → Road Gateway | Data flow | Blocking | Confirmación de cita, ventana horaria y carril, o rechazo | Yes |
| SoS_K2a | Road Gateway → Pacific Port Gateway | Dependency | Blocking | Solicitud de cita portuaria y programación de camión y conductor | Yes |
| SoS_K2b | Pacific Port Gateway → Road Gateway | Data flow | Blocking | Confirmación de cita, ventana horaria y carril, o rechazo | Yes |
| SoS_K3a | Road Gateway → Rail Gateway | Dependency | Blocking | Solicitud de capacidad y turno de transferencia camión-tren | Yes |
| SoS_K3b | Rail Gateway → Road Gateway | Data flow | Blocking | Confirmación de programación y plataforma, o rechazo | Yes |
| SoS_K4a | Road Gateway → Fluvial Gateway | Dependency | Blocking | Solicitud de capacidad y turno de transferencia camión-barcaza | Yes |
| SoS_K4b | Fluvial Gateway → Road Gateway | Data flow | Blocking | Confirmación de muelle fluvial y horario, o rechazo | Yes |
| SoS_K5 | Road Gateway → National Coordination Gateway | Event notification | Sink | Custodia recibida por el transportador; v3: ETA al despachar | Yes |
| SoS_K6 | Road Gateway → National Coordination Gateway | Event notification | Supply | Posición del vehículo, estado del tránsito y eventos en ruta | Yes |
| SoS_K7a | Pacific Port Gateway → Rail Gateway | Dependency | Blocking | Unidades listas para transferencia patio-tren y solicitud de vagones | Yes |
| SoS_K7b | Rail Gateway → Pacific Port Gateway | Data flow | Blocking | Confirmación de convoy, capacidad, plataforma y ventana, o rechazo | Yes |
| SoS_K8 | Pacific Port Gateway → National Coordination Gateway | Event notification | Sink | Arribo/zarpe de motonave y manifiesto en puertos del Pacífico | Yes |
| SoS_K9a | Pacific Port Gateway → National Coordination Gateway | Dependency | Blocking | Solicitud de validación de levante previa a la salida por portería | Yes |
| SoS_K9b | National Coordination Gateway → Pacific Port Gateway | Data flow | Blocking | Estado de levante: concedido, inspección requerida o retenido | Yes |
| SoS_K10a | Fluvial Gateway → Caribbean Port Gateway | Dependency | Blocking | Arribo de barcaza y solicitud de muelle de transferencia | Yes |
| SoS_K10b | Caribbean Port Gateway → Fluvial Gateway | Data flow | Blocking | Asignación de muelle de transferencia y ventana, o rechazo | Yes |
| SoS_K11 | Caribbean Port Gateway → National Coordination Gateway | Event notification | Sink | Arribo/zarpe de motonave y manifiesto en puertos del Caribe | Yes |
| SoS_K12a | Caribbean Port Gateway → National Coordination Gateway | Dependency | Blocking | Solicitud de validación de levante previa a la salida por portería | Yes |
| SoS_K12b | National Coordination Gateway → Caribbean Port Gateway | Data flow | Blocking | Estado de levante: concedido, inspección requerida o retenido | Yes |
| SoS_K13 | Rail Gateway → National Coordination Gateway | Event notification | Sink | Custodia recibida por el concesionario y composición del tren | Yes |
| SoS_K14 | Rail Gateway → National Coordination Gateway | Event notification | Supply | Posición del convoy, estado del corredor y eventos de vía | Yes |
| SoS_K15 | Fluvial Gateway → National Coordination Gateway | Event notification | Sink | Custodia recibida por el operador fluvial | Yes |
| SoS_K16 | Fluvial Gateway → National Coordination Gateway | Event notification | Supply | Posición de barcaza o remolcador y estado de navegación | Yes |
| SoS_K17a | Road Gateway → National Coordination Gateway | Dependency | Blocking | Consulta de estado consolidado de la carga en la que participa el transportador | Yes |
| SoS_K17b | National Coordination Gateway → Road Gateway | Data flow | Blocking | Estado consolidado limitado a su carga; v3: posición y ETA estimadas | Yes |
| SoS_K18a | Rail Gateway → National Coordination Gateway | Dependency | Blocking | Consulta de estado consolidado de la carga en la que participa el concesionario | Yes |
| SoS_K18b | National Coordination Gateway → Rail Gateway | Data flow | Blocking | Estado consolidado limitado a su carga; v3: posición y ETA estimadas | Yes |
| SoS_K19a | Fluvial Gateway → National Coordination Gateway | Dependency | Blocking | Consulta de estado consolidado de la carga en la que participa el operador fluvial | Yes |
| SoS_K19b | National Coordination Gateway → Fluvial Gateway | Data flow | Blocking | Estado consolidado limitado a su carga; v3: posición y ETA estimadas | Yes |
| SoS_K20a | Pacific Port Gateway → National Coordination Gateway | Dependency | Blocking | Consulta de estado consolidado de la carga en la que participa el operador portuario | Yes |
| SoS_K20b | National Coordination Gateway → Pacific Port Gateway | Data flow | Blocking | Estado consolidado limitado a su carga; v3: posición y ETA estimadas | Yes |
| SoS_K21a | Caribbean Port Gateway → National Coordination Gateway | Dependency | Blocking | Consulta de estado consolidado de la carga en la que participa el operador portuario | Yes |
| SoS_K21b | National Coordination Gateway → Caribbean Port Gateway | Data flow | Blocking | Estado consolidado limitado a su carga; v3: posición y ETA estimadas | Yes |
| SoS_K22a | Rail Gateway → Pacific Port Gateway | Dependency | Blocking | Aviso de convoy de exportación y solicitud de zona y ventana de descargue | Yes |
| SoS_K22b | Pacific Port Gateway → Rail Gateway | Data flow | Blocking | Zona de patio, punto y ventana de descargue, o rechazo | Yes |
| SoS_K23a | Rail Gateway → Road Gateway | Dependency | Blocking | Solicitud de camiones para retirar unidades en terminal férrea | Yes |
| SoS_K23b | Road Gateway → Rail Gateway | Data flow | Blocking | Vehículos asignados y cita de retiro, o rechazo | Yes |
| SoS_K24a | Caribbean Port Gateway → Rail Gateway | Dependency | Blocking | Unidades listas para transferencia patio-tren y solicitud de vagones | Yes |
| SoS_K24b | Rail Gateway → Caribbean Port Gateway | Data flow | Blocking | Confirmación de convoy, capacidad, plataforma y ventana, o rechazo | Yes |
| SoS_K25a | Rail Gateway → Caribbean Port Gateway | Dependency | Blocking | Aviso de convoy de exportación y solicitud de zona y ventana de descargue | Yes |
| SoS_K25b | Caribbean Port Gateway → Rail Gateway | Data flow | Blocking | Zona de patio, punto y ventana de descargue, o rechazo | Yes |
| SoS_K26a | Caribbean Port Gateway → Road Gateway | Dependency | Blocking | Solicitud de camiones para retirar unidades liberadas en el Caribe | Yes |
| SoS_K26b | Road Gateway → Caribbean Port Gateway | Data flow | Blocking | Vehículos asignados y cita de retiro, o rechazo | Yes |
| SoS_K27a | Pacific Port Gateway → Road Gateway | Dependency | Blocking | Solicitud de camiones para retirar unidades liberadas en el Pacífico | Yes |
| SoS_K27b | Road Gateway → Pacific Port Gateway | Data flow | Blocking | Vehículos asignados y cita de retiro, o rechazo | Yes |
| SoS_K28a | Fluvial Gateway → Road Gateway | Dependency | Blocking | Solicitud de camiones para retirar unidades en puerto fluvial | Yes |
| SoS_K28b | Road Gateway → Fluvial Gateway | Data flow | Blocking | Vehículos asignados y cita de retiro, o rechazo | Yes |
| SoS_K29 | Caribbean Port Gateway → National Coordination Gateway | Event notification | Sink | Custodia recibida por el puerto del Caribe | Yes |
| SoS_K30 | Pacific Port Gateway → National Coordination Gateway | Event notification | Sink | Custodia recibida por el puerto del Pacífico | Yes |
| SoS_K31a | Caribbean Port Gateway → Fluvial Gateway | Dependency | Blocking | Unidades liberadas para transferencia patio-barcaza y solicitud de capacidad | Yes |
| SoS_K31b | Fluvial Gateway → Caribbean Port Gateway | Data flow | Blocking | Barcazas asignadas, muelle y ventana de cargue, o rechazo | Yes |
| SoS_K32 | National Coordination Gateway → Caribbean Port Gateway | Event notification | Sink | Cambio de levante en puertos del Caribe; v3: estado de servicio | Yes |
| SoS_K33 | National Coordination Gateway → Pacific Port Gateway | Event notification | Sink | Cambio de levante en puertos del Pacífico; v3: estado de servicio | Yes |
| SoS_K34 | National Coordination Gateway → Rail Gateway | Event notification | Sink | Estado de servicio de un constituyente: degradado o restablecido | Yes |
| SoS_K35 | National Coordination Gateway → Fluvial Gateway | Event notification | Sink | Estado de servicio de un constituyente: degradado o restablecido | Yes |
| SoS_K36 | Road Gateway → National Coordination Gateway | Event notification | Sink | Paso por peaje: vehículo, peaje, fecha y hora | Yes |
