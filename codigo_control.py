import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

def solicitar_cantidad_sacos():
    while True:
        try:
            n = int(input("Número de sacos a transportar (1-6): "))

            if 1 <= n <= 6:
                return n

            print("Error: el valor debe estar entre 1 y 6.")

        except ValueError:
            print("Error: ingresa un número válido.")

    
def conectar_simulador():
    """Establece la conexión con CoppeliaSim."""
    client = RemoteAPIClient()
    sim = client.getObject('sim')
    print("Conectado exitosamente a CoppeliaSim.")
    return sim

def cambiar_variable_en_lua(sim, robot_handle, nombre_var, valor_bool):
    """Función auxiliar para enviar variables a Lua de forma segura."""
    valor_int = 1 if valor_bool else 0
    
    sim.callScriptFunction(
        "modificarVariablesDesdePython",
        sim.getScript(sim.scripttype_childscript, robot_handle),
        [valor_int], [], [nombre_var], ""
    )

def leer_variable_de_lua(sim, robot_handle, nombre_var):
    """Lee una variable desde Lua y devuelve un booleano (True/False)."""
    script_handle = sim.getScript(sim.scripttype_childscript, robot_handle)
    
    # Llamar puente de lectura en Lua
    regreso_ints, _, _, _ = sim.callScriptFunction(
        "leerVariablesDesdePython",
        script_handle,
        [], [], [nombre_var], ""
    )
    
    # Si el primer entero devuelto es 1, significa True. Si es 0, False.
    return regreso_ints[0] == 1

def monitorear_viaje_hasta_meta(sim, robot_handle):
    """Bucle de monitoreo activo que lee los sensores y estados de recuperación en tiempo real."""
    ultimo_estado_impreso = 0
    
    while True:
        # 1. Verificar si ya llegamos a la meta definitiva del tramo actual
        if leer_variable_de_lua(sim, robot_handle, "metaAlcanzada"):
            break # Rompe el ciclo de monitoreo porque el viaje terminó
            
        # 2. Leer el estado de los sensores y recuperación desde Lua
        script_handle = sim.getScript(sim.scripttype_childscript, robot_handle)
        regreso_ints, _, _, _ = sim.callScriptFunction("leerVariablesDesdePython", script_handle, [], [], ["estadoRobot"], "")
        estado_actual = regreso_ints[0]
        
        # 3. Imprimir el resultado de los sensores y la recuperación si hubo un cambio
        if estado_actual != ultimo_estado_impreso:
            if estado_actual == 1:
                print("¡ALERTA! robot atorado\nEmpezando proceso de recuperación")
            elif estado_actual == 3:
                print("¡ALERTA! Obstáculo detectado\nEmpezando proceso de recuperación...")
            elif estado_actual == 2:
                print("[RECUPERACIÓN] El robot se está reincorporando al camino. Girando hacia el objetivo...")
            elif estado_actual == 0:
                print("Zona despejada. Reanudando navegación normal.")
            
            ultimo_estado_impreso = estado_actual
            
        time.sleep(0.05) # Muestreo rápido de 50ms para no perder alertas


def generar_sacos(sim, cantidad):
    """Paso 2: Clona y posiciona los sacos en la zona de carga inicial."""
    handle_plantilla = sim.getObject('/Saco_plantilla')
    dum_back= sim.getObject('/DummyBack')
    pos_carga = sim.getObjectPosition(dum_back, -1) #Coordenadas de la zona de construccion
    sacos_handles = []

    for i in range(cantidad):
        # Generar nuevo saco
        nuevo_saco = sim.copyPasteObjects([handle_plantilla], 0)[0]
        #Posicionar cerca del dummy de origen
        pos_actual = [pos_carga[0]+.05, pos_carga[1]+.05, pos_carga[2] + (i * 0.15)]
        sim.setObjectPosition(nuevo_saco, -1, pos_actual)
        sacos_handles.append(nuevo_saco)
        
    print(f"Se han generado {cantidad} sacos en la zona de carga.")
    return sacos_handles

def simular_viaje_redondo(sim, robot_handle, saco_handle,z):
    """Maneja el ciclo logístico: Carga inmediata, viaje a meta, descarga y retorno vacío."""
    

    # PASO 1: RECOGER EL SACO INMEDIATAMENTE (Antes de avanzar)

    print("Cargando saco de la pila actual directamente al chasis del Pioneer...")
    
    # Colocamos el saco de forma local encima del robot (Z = 0.2 metros de altura)
    sim.setObjectPosition(saco_handle, robot_handle, [0.0, 0.0, 0.2])
    
    # Hacemos hijo del pioneer para que se mueve con este
    sim.setObjectParent(saco_handle, robot_handle, True)
    
    time.sleep(1.0)
    
    
    # PASO 2: VIAJE DE IDA CON CARGA (Hacia la Meta de Descarga)

    print("Saco asegurado. Viajando a punto de descarga...")

    cambiar_variable_en_lua(sim, robot_handle, "metaAlcanzada", False)
    cambiar_variable_en_lua(sim, robot_handle, "goingBack", False)
    cambiar_variable_en_lua(sim, robot_handle, "path", False)
    
    monitorear_viaje_hasta_meta(sim, robot_handle)
    # El script de Python se queda esperando pacientemente a que el robot físico termine la ruta
    while not leer_variable_de_lua(sim, robot_handle, "metaAlcanzada"):
        time.sleep(0.1)
        
 
    # PASO 3: DESCARGAR EL SACO EN LA META

    print("¡Llegada al punto de entrega! Descargando saco...")
    
    # Rompemos el parentesco con el robot para que el saco se quede fijo en el mundo (-1)
    sim.setObjectParent(saco_handle, -1, True)
    
    # Obtenemos la ubicación actual del robot y dejamos el saco medio metro adelante (X + 0.5) en el suelo (Z = 0.1)
    #pos_actual_robot = sim.getObjectPosition(robot_handle, -1)
    #sim.setObjectPosition(saco_handle, -1, [pos_actual_robot[0] + 0.5, pos_actual_robot[1], z])
    dummy_goal = sim.getObject('/GoalDummy')
    pos_goal = sim.getObjectPosition(dummy_goal , -1)
    sim.setObjectPosition(saco_handle, -1,  [pos_goal[0] + 0.5, pos_goal[1], z])
  
    
    time.sleep(1.0) # Pausa de descarga
    
    # -----------------------------------------------------------------
    # PASO 4: VIAJE DE REGRESO VACÍO (Hacia el Punto de Origen)
    # -----------------------------------------------------------------
    print("Descarga completada. El robot regresa vacío por el siguiente saco...")
    cambiar_variable_en_lua(sim, robot_handle, "metaAlcanzada", False)
    cambiar_variable_en_lua(sim, robot_handle, "goingBack", True)
    cambiar_variable_en_lua(sim, robot_handle, "path", False)
    # Esperamos a que el robot llegue de vuelta a la pila de carga
    while not leer_variable_de_lua(sim, robot_handle, "metaAlcanzada"):
        time.sleep(0.1)
        
    print("¡Robot de vuelta en la base y listo para el siguiente ciclo!") # Reset final

#Flujo principal: 
if __name__ == "__main__":
    # 1. Obtener la cantidad de sacos
    cantidad_sacos = solicitar_cantidad_sacos()

    print("\n[SISTEMA] Iniciando conexión con el simulador...")
    #Abrimos la comunicación con CoppeliaSim y obtenemos el objeto del robot
    sim = conectar_simulador()
    robot_handle = sim.getObject('/PioneerP3DX')

    sim.startSimulation()
    
    #Generar sacos en el mapa
    lista_sacos = generar_sacos(sim, cantidad_sacos)
    
    # 4. Bucle para control el viaje mientras hayan sacos
    sacos_transportados = len(lista_sacos) - 1
    
    z = 0
    while sacos_transportados >= 0:
        saco_actual = lista_sacos[sacos_transportados]
        print(f"\n--- Iniciando transporte del Saco {cantidad_sacos - sacos_transportados + 1} de {cantidad_sacos} ---")
        
        # Ejecutar un viaje para transporar un saco
        simular_viaje_redondo(sim, robot_handle, saco_actual,z)
        z = z + .20
        
        sacos_transportados -= 1
        
    print("\nTodos los sacos han sido transportados finalizando tarea")
    sim.stopSimulation()