# Manual de Usuario

## Proyecto de Robot Móvil en Entorno de Construcción

### 1. ¿Cómo funciona el sistema?

El programa permite que un robot Pioneer P3DX en CoppeliaSim transporte sacos de construcción desde una zona de carga hasta un punto de entrega.

Mediante la ejecución del archivo `codigo_control.py` desde la terminal, se inicia la simulación y el control del robot en CoppeliaSim.

El ciclo de trabajo para cada saco es el siguiente:

1. **Carga:** El robot toma automáticamente un saco de la pila.
2. **Viaje de ida:** El robot avanza siguiendo una ruta generada mediante un algoritmo BiTRRT (Bidirectional Transition-based Rapidly-exploring Random Tree).
3. **Descarga:** El robot deposita el saco en el punto de entrega.
4. **Viaje de regreso:** El robot retorna a la zona de carga para recoger el siguiente saco.
5. **Recuperación:** En caso de detectar obstáculos, quedar atorado o encontrar una situación anómala, el robot ejecuta un procedimiento de reincorporación antes de continuar.

---

## 2. Requisitos Previos

Antes de ejecutar el sistema, asegúrate de cumplir con los siguientes requisitos:

1. Tener instalado CoppeliaSim.
2. Abrir el archivo `escena_construccion.ttt` dentro de CoppeliaSim.
3. Ejecutar el archivo `codigo_control.py` desde una terminal.
4. No es necesario iniciar manualmente la simulación desde CoppeliaSim; el programa se encargará de ello automáticamente.

---

## 3. Instrucciones de Uso

### Paso 1: Iniciar el programa

Ejecuta el siguiente comando desde la terminal:

```bash
python codigo_control.py
```

Al iniciar, aparecerá el mensaje:

```text
Número de sacos a transportar (1-6):
```

### Paso 2: Seleccionar la cantidad de sacos

Introduce un número entre 1 y 6 y presiona Enter.

El programa valida la entrada y detecta automáticamente:

* Valores negativos.
* Ceros.
* Texto no numérico.
* Valores fuera del rango permitido.

Si ocurre algún error, el sistema solicitará nuevamente un valor válido.

### Paso 3: Observar la simulación

Una vez ingresado el número de sacos:

* La simulación comenzará automáticamente en CoppeliaSim.
* Los sacos aparecerán en la zona de carga.
* El robot Pioneer P3DX iniciará sus desplazamientos de manera autónoma.
* La terminal mostrará información en tiempo real sobre el estado del robot.

---

## 4. Interpretación de los Mensajes del Sistema

### Mensajes de Progreso

#### Cargando saco de la pila...

El robot está colocando virtualmente un saco sobre su plataforma de transporte.

#### Iniciando viaje hacia el punto de entrega...

La ruta ha sido calculada y el robot se dirige al objetivo.

#### ¡Llegada al punto de entrega! Descargando saco.

El robot alcanzó exitosamente el punto de descarga.

#### Descarga completada. El robot regresa vacío por el siguiente saco...

El robot retorna a la zona de carga para continuar la tarea.

#### Todos los sacos han sido transportados. Finalizando tarea.

La misión ha concluido satisfactoriamente.

---

### Mensajes de Alerta

#### ¡ALERTA! Robot atorado...

El robot no ha mostrado un desplazamiento significativo durante un intervalo determinado de tiempo y activará su procedimiento de recuperación.

#### ¡ALERTA! Obstáculo detectado...

Los sensores frontales detectaron un obstáculo que impide continuar la trayectoria planificada.

#### [RECUPERACIÓN] El robot se está reincorporando al camino. Girando hacia el objetivo...

El robot ha ejecutado una maniobra correctiva y está retomando su ruta.

---

## 5. Fin de la Misión

Cuando el último saco haya sido transportado, el sistema mostrará el mensaje:

```text
¡Misión cumplida! Todos los sacos han sido transportados.
Finalizando tarea.
```

Posteriormente:

* La simulación se detendrá automáticamente.
* CoppeliaSim quedará en estado de pausa.
* El sistema estará listo para una nueva ejecución.
