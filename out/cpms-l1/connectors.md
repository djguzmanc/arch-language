# Connectors of CPMS

| ID | Source → Target | Nature | Coupling | Information carried | Boundary |
|----|-----------------|--------|----------|---------------------|----------|
| A-K1 | T5.6 Lectores OCR/RFID → T2.5 Gateway IoT de campo | Data flow | Supply | Placa, código de contenedor o precinto recién leídos | No |
| A-K2 | T5.5 Básculas de camiones → T2.5 Gateway IoT de campo | Data flow | Supply | Peso del camión y de la unidad | No |
| A-K3 | T5.7 Sensores de patio y refrigerados → T2.5 Gateway IoT de campo | Data flow | Supply | Temperatura y estado de unidades refrigeradas y del patio | No |
| A-K4 | T5.9 Cámaras de seguridad perimetral → T2.5 Gateway IoT de campo | Data flow | Supply | Detecciones de las cámaras | No |
| A-K5 | T2.5 Gateway IoT de campo → T2.2 Broker de eventos interno | Event notification | Sink | Lecturas normalizadas y alarmas de campo | No |
| A-K6 | T5.8 Computadores a bordo de grúas → T2.4 Adaptador de equipos del terminal | Data flow | Supply | Posición, estado y confirmación de movimientos de cada grúa | No |
| A-K7 | T5.10 Computadores a bordo de vehículos → T2.4 Adaptador de equipos del terminal | Data flow | Supply | Posición, estado y confirmación de movimientos de cada vehículo | No |
| A-K8 | T2.4 Adaptador de equipos del terminal → T2.2 Broker de eventos interno | Event notification | Sink | Avance de órdenes y estado de los equipos, en formato común | No |
| A-K9 | T3.10 Coordinador de operaciones del terminal → T3.5 Despacho de transporte interno | Control command | Supply | Movimientos internos que deben despacharse | No |
| A-K10 | T3.10 Coordinador de operaciones del terminal → T2.4 Adaptador de equipos del terminal | Control command | Supply | Órdenes de trabajo para grúas | No |
| A-K11 | T3.5 Despacho de transporte interno → T2.4 Adaptador de equipos del terminal | Control command | Supply | Asignación de movimientos a vehículos internos | No |
| A-K12 | T2.4 Adaptador de equipos del terminal → T5.8 Computadores a bordo de grúas | Control command | Supply | Órdenes de grúa traducidas al lenguaje del equipo (autoridad: T3.10) | No |
| A-K13 | T2.4 Adaptador de equipos del terminal → T5.10 Computadores a bordo de vehículos | Control command | Supply | Órdenes de vehículo traducidas al lenguaje del equipo (autoridad: T3.5) | No |
| A-K14 | T5.8 Computadores a bordo de grúas → T5.1 Grúas de muelle | Control command | Supply | Accionamiento de izaje y traslación de la grúa de muelle; parada | No |
| A-K15 | T5.1 Grúas de muelle → T5.8 Computadores a bordo de grúas | Data flow | Supply | Posición, carga y límites medidos en la grúa de muelle | No |
| A-K16 | T5.8 Computadores a bordo de grúas → T5.2 Grúas de patio | Control command | Supply | Accionamiento de izaje y traslación de la grúa de patio; parada | No |
| A-K17 | T5.2 Grúas de patio → T5.8 Computadores a bordo de grúas | Data flow | Supply | Posición, carga y límites medidos en la grúa de patio | No |
| A-K18 | T5.10 Computadores a bordo de vehículos → T5.3 Vehículos de transporte interno | Control command | Supply | Accionamiento de tracción, dirección y frenado del vehículo | No |
| A-K19 | T5.3 Vehículos de transporte interno → T5.10 Computadores a bordo de vehículos | Data flow | Supply | Posición y velocidad medidas del vehículo | No |
| A-K20 | T2.4 Adaptador de equipos del terminal → T1.4 Terminal de cabina de equipos | Data flow | Supply | Órdenes que debe ver el operador | No |
| A-K21 | T1.4 Terminal de cabina de equipos → T2.4 Adaptador de equipos del terminal | Data flow | Supply | Confirmaciones e incidentes reportados por el operador | No |
| A-K22 | T2.2 Broker de eventos interno → T3.6 Gestión de portería y citas | Event notification | Supply | Hechos de portería: lectura de placa, peso, llegada de camión | No |
| A-K23 | T2.2 Broker de eventos interno → T3.4 Gestión de patio | Event notification | Supply | Hechos de patio y de unidades refrigeradas | No |
| A-K24 | T2.2 Broker de eventos interno → T3.10 Coordinador de operaciones del terminal | Event notification | Supply | Avance de órdenes y estado de los equipos | No |
| A-K25 | T2.2 Broker de eventos interno → T3.11 Seguridad y control de acceso | Event notification | Supply | Hechos de acceso y de seguridad perimetral | No |
| A-K26 | T2.2 Broker de eventos interno → T4.8 Histórico de eventos | Event notification | Sink | Todos los eventos operativos, para el histórico | No |
| A-K27 | T2.2 Broker de eventos interno → T1.1 Panel de control operativo | Event notification | Sink | Eventos en tiempo real para el panel | No |
| A-K28 | T2.6 Receptor AIS de buques → T3.1 Gestión de escalas | Event notification | Supply | Posición y aproximación de buques | No |
| A-K29 | T2.3 Adaptador de navieras y agentes → T3.1 Gestión de escalas | Data flow | Supply | Preaviso de escala, manifiesto e instrucciones de naviera o agente | No |
| A-K30 | T3.1 Gestión de escalas → T3.2 Asignación de atraque | Dependency | Blocking | Solicitud de atraque para una escala | No |
| A-K31 | T3.2 Asignación de atraque → T3.1 Gestión de escalas | Data flow | Supply | Muelle y ventana asignados | No |
| A-K32 | T3.2 Asignación de atraque → T3.3 Planificación de grúas de muelle | Data flow | Supply | Ventana de atraque para planificar grúas | No |
| A-K33 | T3.3 Planificación de grúas de muelle → T3.10 Coordinador de operaciones del terminal | Data flow | Supply | Plan de grúas y secuencia de carga y descarga | No |
| A-K34 | T3.4 Gestión de patio → T3.10 Coordinador de operaciones del terminal | Data flow | Supply | Plan de patio: posición destino de cada unidad | No |
| A-K35 | T1.2 Consola de planificación → T3.2 Asignación de atraque | Control command | Supply | Ajustes manuales del planificador al plan de atraque | No |
| A-K36 | T1.2 Consola de planificación → T3.4 Gestión de patio | Control command | Supply | Ajustes manuales del planificador al plan de patio | No |
| A-K37 | T3.2 Asignación de atraque → T1.2 Consola de planificación | Data flow | Supply | Propuesta de atraque y ocupación de muelles, para revisión | No |
| A-K38 | T3.1 Gestión de escalas → T3.7 Gestión de unidades de carga | Data flow | Supply | Unidades declaradas en el manifiesto (alta de unidades) | No |
| A-K39 | T3.6 Gestión de portería y citas → T3.7 Gestión de unidades de carga | Event notification | Supply | Entrada o salida de una unidad por portería | No |
| A-K40 | T3.7 Gestión de unidades de carga → T3.4 Gestión de patio | Event notification | Supply | Unidad que requiere posición en patio | No |
| A-K41 | T3.4 Gestión de patio → T3.7 Gestión de unidades de carga | Data flow | Supply | Posición de patio asignada a la unidad | No |
| A-K42 | T3.6 Gestión de portería y citas → T3.9 Estado aduanero y retenciones | Dependency | Blocking | Consulta del estado aduanero de una unidad en portería | No |
| A-K43 | T3.9 Estado aduanero y retenciones → T3.6 Gestión de portería y citas | Data flow | Supply | Respuesta: unidad liberada o retenida | No |
| A-K44 | T1.6 Consola de inspección → T3.9 Estado aduanero y retenciones | Data flow | Supply | Ejecución y resultado de inspección física en puerto | No |
| A-K45 | T3.9 Estado aduanero y retenciones → T3.7 Gestión de unidades de carga | Event notification | Supply | Estado aduanero aplicado a la unidad | No |
| A-K46 | T3.6 Gestión de portería y citas → T3.8 Custodia y transferencia | Event notification | Supply | Entrega o recepción física en portería que genera cambio de custodia | No |
| A-K47 | T3.11 Seguridad y control de acceso → T3.6 Gestión de portería y citas | Data flow | Supply | Permisos de acceso vigentes | No |
| A-K48 | T3.6 Gestión de portería y citas → T2.5 Gateway IoT de campo | Control command | Supply | Abrir o cerrar barrera | No |
| A-K49 | T2.5 Gateway IoT de campo → T5.4 Carriles y barreras de portería | Control command | Supply | Orden de apertura o cierre enviada a la barrera | No |
| A-K50 | T3.10 Coordinador de operaciones del terminal → T3.8 Custodia y transferencia | Event notification | Supply | Carga o descarga de tren, barcaza o buque completada | No |
| A-K51 | T3.7 Gestión de unidades de carga → T3.12 Planificación intermodal | Event notification | Supply | Unidades liberadas listas para evacuación intermodal | No |
| A-K52 | T1.3 Portal de agentes y transportistas → T2.7 Backend para clientes externos (BFF) | Dependency | Blocking | Solicitudes de cita y consultas | No |
| A-K53 | T2.7 Backend para clientes externos (BFF) → T3.6 Gestión de portería y citas | Dependency | Blocking | Petición de cita o consulta hacia portería | No |
| A-K54 | T3.6 Gestión de portería y citas → T2.7 Backend para clientes externos (BFF) | Data flow | Supply | Resultado de la cita o consulta | No |
| A-K55 | T2.7 Backend para clientes externos (BFF) → T1.3 Portal de agentes y transportistas | Data flow | Supply | Respuesta adaptada al portal | No |
| A-K56 | T1.5 Kiosco de portería → T2.7 Backend para clientes externos (BFF) | Dependency | Blocking | Registro de llegada del conductor | No |
| A-K57 | T2.7 Backend para clientes externos (BFF) → T1.5 Kiosco de portería | Data flow | Supply | Instrucciones de carril y turno | No |
| A-K58 | T3.7 Gestión de unidades de carga → T4.1 BD de unidades de carga | Dependency | Blocking | Estado, posición y documentos de las unidades | No |
| A-K59 | T3.1 Gestión de escalas → T4.2 BD de escalas y atraques | Dependency | Blocking | Escalas y plan de atraque vigente | No |
| A-K60 | T3.6 Gestión de portería y citas → T4.3 BD de citas | Dependency | Blocking | Citas de portería | No |
| A-K61 | T3.8 Custodia y transferencia → T4.4 Registro de custodia | Dependency | Blocking | Registros de cambio de custodia | No |
| A-K62 | T3.1 Gestión de escalas → T4.5 Repositorio documental | Dependency | Blocking | Manifiestos y documentos de la escala | No |
| A-K63 | T3.4 Gestión de patio → T4.6 BD de ocupación de patio | Dependency | Blocking | Ocupación y reservas de patio | No |
| A-K64 | T3.9 Estado aduanero y retenciones → T4.7 BD de retenciones | Dependency | Blocking | Retenciones y liberaciones | No |
| A-K65 | T3.11 Seguridad y control de acceso → T4.9 BD de permisos de acceso | Dependency | Blocking | Permisos de personas y vehículos | No |
| A-K66 | T3.12 Planificación intermodal → T3.4 Gestión de patio | Dependency | Blocking | Reserva de zona de patio para convoy o barcaza | No |
| A-K67 | T3.4 Gestión de patio → T3.12 Planificación intermodal | Data flow | Supply | Zona y punto de patio reservados | No |
| A-K68 | T3.12 Planificación intermodal → T3.10 Coordinador de operaciones del terminal | Data flow | Supply | Ventanas de cargue y descargue acordadas con otros modos | No |
| A-K69 | T3.12 Planificación intermodal → T3.6 Gestión de portería y citas | Data flow | Supply | Citas de retiro acordadas con transportadores | No |
| A-K70 | Caribbean Port Gateway → T3.6 Gestión de portería y citas | Dependency | Blocking | Solicitud de cita de camión recibida (SoS_K1a) | No |
| A-K71 | T3.6 Gestión de portería y citas → Caribbean Port Gateway | Data flow | Supply | Confirmación o rechazo de la cita (SoS_K1b) | No |
| A-K72 | Caribbean Port Gateway → T3.2 Asignación de atraque | Dependency | Blocking | Solicitud de muelle de transferencia para barcaza (SoS_K10a) | No |
| A-K73 | T3.2 Asignación de atraque → Caribbean Port Gateway | Data flow | Supply | Muelle y ventana asignados a la barcaza (SoS_K10b) | No |
| A-K74 | T3.1 Gestión de escalas → Caribbean Port Gateway | Event notification | Sink | Arribo/zarpe de buque y manifiesto (SoS_K11) | No |
| A-K75 | T3.9 Estado aduanero y retenciones → Caribbean Port Gateway | Dependency | Blocking | Solicitud de validación de levante (SoS_K12a) | No |
| A-K76 | Caribbean Port Gateway → T3.9 Estado aduanero y retenciones | Data flow | Supply | Estado de levante recibido (SoS_K12b) | No |
| A-K77 | T3.8 Custodia y transferencia → Caribbean Port Gateway | Dependency | Blocking | Consulta de estado consolidado, verificación de la contraparte (SoS_K21a) | No |
| A-K78 | Caribbean Port Gateway → T3.8 Custodia y transferencia | Data flow | Supply | Estado consolidado recibido (SoS_K21b) | No |
| A-K79 | T3.12 Planificación intermodal → Caribbean Port Gateway | Dependency | Blocking | Unidades listas y solicitud de vagones (SoS_K24a) | No |
| A-K80 | Caribbean Port Gateway → T3.12 Planificación intermodal | Data flow | Supply | Confirmación de convoy y ventana de cargue (SoS_K24b) | No |
| A-K81 | Caribbean Port Gateway → T3.12 Planificación intermodal | Dependency | Blocking | Aviso de convoy de exportación y solicitud de zona (SoS_K25a) | No |
| A-K82 | T3.12 Planificación intermodal → Caribbean Port Gateway | Data flow | Supply | Zona, punto y ventana de descargue asignados (SoS_K25b) | No |
| A-K83 | T3.12 Planificación intermodal → Caribbean Port Gateway | Dependency | Blocking | Solicitud de capacidad de camiones para retiro (SoS_K26a) | No |
| A-K84 | Caribbean Port Gateway → T3.12 Planificación intermodal | Data flow | Supply | Vehículos y cita de retiro confirmados, o rechazo (SoS_K26b) | No |
| A-K85 | T3.8 Custodia y transferencia → Caribbean Port Gateway | Event notification | Sink | Custodia recibida por el puerto (SoS_K29) | No |
| A-K86 | T3.12 Planificación intermodal → Caribbean Port Gateway | Dependency | Blocking | Unidades listas y solicitud de capacidad fluvial (SoS_K31a) | No |
| A-K87 | Caribbean Port Gateway → T3.12 Planificación intermodal | Data flow | Supply | Barcazas, muelle y ventana confirmados, o rechazo (SoS_K31b) | No |
| A-K88 | Caribbean Port Gateway → T3.9 Estado aduanero y retenciones | Event notification | Supply | Cambio de levante recibido (SoS_K32) | No |
| SoS_K1a | Road Gateway → Caribbean Port Gateway | Dependency | Blocking | Solicitud de cita portuaria y programación de camión y conductor | Yes |
| SoS_K1b | Caribbean Port Gateway → Road Gateway | Data flow | Blocking | Confirmación de cita, ventana horaria y carril, o rechazo | Yes |
| SoS_K10a | Fluvial Gateway → Caribbean Port Gateway | Dependency | Blocking | Arribo de barcaza y solicitud de muelle de transferencia | Yes |
| SoS_K10b | Caribbean Port Gateway → Fluvial Gateway | Data flow | Blocking | Asignación de muelle de transferencia y ventana, o rechazo | Yes |
| SoS_K11 | Caribbean Port Gateway → National Coordination Gateway | Event notification | Sink | Arribo/zarpe de motonave y manifiesto en puertos del Caribe | Yes |
| SoS_K12a | Caribbean Port Gateway → National Coordination Gateway | Dependency | Blocking | Solicitud de validación de levante previa a la salida por portería | Yes |
| SoS_K12b | National Coordination Gateway → Caribbean Port Gateway | Data flow | Blocking | Estado de levante: concedido, inspección requerida o retenido | Yes |
| SoS_K21a | Caribbean Port Gateway → National Coordination Gateway | Dependency | Blocking | Consulta de estado consolidado de la carga en la que participa el operador portuario | Yes |
| SoS_K21b | National Coordination Gateway → Caribbean Port Gateway | Data flow | Blocking | Estado consolidado limitado a su carga; v3: posición y ETA estimadas | Yes |
| SoS_K24a | Caribbean Port Gateway → Rail Gateway | Dependency | Blocking | Unidades listas para transferencia patio-tren y solicitud de vagones | Yes |
| SoS_K24b | Rail Gateway → Caribbean Port Gateway | Data flow | Blocking | Confirmación de convoy, capacidad, plataforma y ventana, o rechazo | Yes |
| SoS_K25a | Rail Gateway → Caribbean Port Gateway | Dependency | Blocking | Aviso de convoy de exportación y solicitud de zona y ventana de descargue | Yes |
| SoS_K25b | Caribbean Port Gateway → Rail Gateway | Data flow | Blocking | Zona de patio, punto y ventana de descargue, o rechazo | Yes |
| SoS_K26a | Caribbean Port Gateway → Road Gateway | Dependency | Blocking | Solicitud de camiones para retirar unidades liberadas en el Caribe | Yes |
| SoS_K26b | Road Gateway → Caribbean Port Gateway | Data flow | Blocking | Vehículos asignados y cita de retiro, o rechazo | Yes |
| SoS_K29 | Caribbean Port Gateway → National Coordination Gateway | Event notification | Sink | Custodia recibida por el puerto del Caribe | Yes |
| SoS_K31a | Caribbean Port Gateway → Fluvial Gateway | Dependency | Blocking | Unidades liberadas para transferencia patio-barcaza y solicitud de capacidad | Yes |
| SoS_K31b | Fluvial Gateway → Caribbean Port Gateway | Data flow | Blocking | Barcazas asignadas, muelle y ventana de cargue, o rechazo | Yes |
| SoS_K32 | National Coordination Gateway → Caribbean Port Gateway | Event notification | Sink | Cambio de levante en puertos del Caribe; v3: estado de servicio | Yes |
| SoS_K5 | Road Gateway → National Coordination Gateway | Event notification | Sink | Custodia recibida por el transportador; v3: ETA al despachar | Yes |
