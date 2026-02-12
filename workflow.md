# 🚁 FLUJO DE TRABAJO COMPLETO DE FLY-IN

> **Documentación Ultra Detallada del Sistema de Enrutamiento de Drones**

Este documento describe paso a paso cómo funciona el programa cuando se ejecuta el comando:

```bash
python main_solver.py maps/easy/01_linear_path.txt
```

El sistema resuelve el problema de enrutamiento de múltiples drones desde un punto **START** hasta un punto **END**, respetando restricciones de capacidad en nodos y aristas, utilizando un **grafo expandido en el tiempo** y el **algoritmo de Dijkstra**.

---

## 📑 ÍNDICE

1. [Punto de Entrada: main_solver.py](#1--punto-de-entrada-main_solverpy)
2. [Fase 1: Parseo del Archivo](#2--fase-1-parseo-del-archivo)
3. [Fase 2: Estimación del Tiempo Máximo](#3--fase-2-estimación-del-tiempo-máximo)
4. [Fase 3: Construcción del Grafo Temporal](#4--fase-3-construcción-del-grafo-temporal)
5. [Fase 4: Resolución con Dijkstra](#5--fase-4-resolución-con-dijkstra)
6. [Fase 5: Generación del Output](#6--fase-5-generación-del-output)
7. [Estructuras de Datos Clave](#7--estructuras-de-datos-clave---resumen)

---

## 1. 🚀 PUNTO DE ENTRADA: main_solver.py

**Archivo:** `main_solver.py`

### Descripción General

El archivo `main_solver.py` es el punto de entrada del programa. Cuando el usuario ejecuta el comando, este archivo coordina todo el flujo de trabajo:

1. Parsea los argumentos de línea de comandos
2. Invoca al parser para leer el archivo de mapa
3. Verifica que existe un camino válido
4. Estima el tiempo máximo necesario
5. Construye el grafo temporal y resuelve con reintentos
6. Imprime el resultado en el formato requerido

### Constantes Globales

> ℹ️ **Nota:** No hay constantes globales. La lógica es determinista gracias a la estimación matemáticamente óptima.

---

### 📌 Función `main()`

```python
def main() -> None:
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| — | — | Lee de `sys.argv` |

| Retorno | Descripción |
|---------|-------------|
| `None` | Imprime resultado o termina con error |

#### Paso a Paso:

**Paso 1: Validación de argumentos**
```python
if len(sys.argv) < 2:
    print("Usage: python3 main_solver.py <map_file.txt>", file=sys.stderr)
    sys.exit(1)
```
- Lee `sys.argv` para obtener el path del archivo de mapa
- Si no hay argumentos, imprime mensaje de uso y sale con código 1

**Paso 2: Instanciación del parser**
```python
parser = FileParser()
```
- Crea una nueva instancia de la clase `FileParser`
- `FileParser` internamente inicializa un `SimulationMap` vacío
- `FileParser` configura los procesadores para cada tipo de línea

**Paso 3: Parseo del archivo**
```python
simulation = parser.parse(map_file)
```
- Llama al método `parse()` pasando el path del archivo
- Retorna un objeto `SimulationMap` completamente poblado
- Si hay errores de formato, el programa termina aquí

**Paso 4: Verificación de camino existente**
```python
if not has_path_to_end(simulation):
    print("ERROR: No path exists from START to END", file=sys.stderr)
    sys.exit(1)
```
- Usa BFS para verificar que existe al menos un camino
- Si no hay camino posible, el programa termina con error

**Paso 5: Estimación del tiempo máximo**
```python
initial_max_time = estimate_max_time(simulation)
```
- Calcula cuántos turnos necesitaremos como máximo
- Fórmula: `min_path_length + (nb_drones - 1)`

**Paso 6: Creación del solver**
```python
solver, _ = create_solver(simulation, initial_max_time)
```
- Construye el grafo temporal y resuelve todos los drones
- Garantizado encontrar solución a la primera (matemáticamente óptimo)
- Retorna el solver con todas las rutas calculadas

**Paso 7: Output**
```python
solver.print_simulation_output()
```
- Imprime el resultado en formato requerido

---

### 📌 Función `create_solver()`

```python
def create_solver(
    simulation: SimulationMap, initial_max_time: int
) -> Tuple[FlowSolver, int]:
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `simulation` | `SimulationMap` | Mapa con toda la configuración |
| `initial_max_time` | `int` | Tiempo máximo calculado |

| Retorno | Tipo | Descripción |
|---------|------|-------------|
| Tupla | `Tuple[FlowSolver, int]` | Solver resuelto y tiempo usado |

#### Funcionamiento:

```python
time_graph = TimeGraph(simulation, max_time=initial_max_time)
time_graph.build_graph()

solver = FlowSolver(time_graph, simulation.nb_drones)
solver.solve_all_drones()

return solver, initial_max_time
```

1. Construye un `TimeGraph` con `initial_max_time`
2. Llama a `time_graph.build_graph()` para poblar el grafo
3. Crea un `FlowSolver` con el grafo
4. Llama a `solver.solve_all_drones()` para encontrar rutas
5. Retorna el solver y el tiempo usado

> 💡 **Garantía de éxito a la primera:** A diferencia del enfoque anterior, aquí no hay bucle de reintentos. La fórmula `min_path + (nb_drones - 1)` es matemáticamente óptima y garantiza solución incluso en el peor caso (flujo máximo de 1 drone por turno).

---

## 2. 📄 FASE 1: PARSEO DEL ARCHIVO

**Archivo:** `src/parser/file_parser.py`
**Clase:** `FileParser`

### Descripción General

`FileParser` es responsable de leer un archivo de texto con el formato específico del mapa y convertirlo en un objeto `SimulationMap` estructurado. Utiliza un **patrón de diseño basado en procesadores especializados** para cada tipo de entidad.

---

### 🏗️ Clase `FileParser`

#### Constructor `__init__()`

```python
def __init__(self) -> None:
```

**Inicialización del mapa vacío:**
```python
self.simulation_map = SimulationMap(
    nb_drones=0,
    hubs={},
    connections={},
)
```

**Configuración del diccionario de procesadores:**
```python
self.processors = {
    "hub": HubProcessor(NodeCategory.INTERMEDIATE),
    "start_hub": HubProcessor(NodeCategory.START),
    "end_hub": HubProcessor(NodeCategory.END),
    "connection": ConnectionProcessor(),
    "nb_drones": DroneProcessor(),
}
```

> 💡 Cada procesador sabe cómo parsear un tipo específico de línea.

---

#### Método `parse()`

```python
def parse(self, filename: str) -> SimulationMap:
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `filename` | `str` | Path al archivo de mapa |

| Retorno | Tipo | Descripción |
|---------|------|-------------|
| `SimulationMap` | `SimulationMap` | Mapa completamente poblado |

#### Paso a Paso:

**Paso 1: Abrir el archivo**
```python
with open(filename, "r") as f:
```
- Abre el archivo en modo lectura
- Si el archivo no existe, captura `OSError` y termina

**Paso 2: Iterar línea por línea**
```python
for line_num, line in enumerate(f, start=1):
    line = line.strip()
```
- `enumerate()` proporciona número de línea para mensajes de error
- `strip()` elimina espacios y saltos de línea

**Paso 3: Ignorar líneas vacías y comentarios**
```python
if not line or line.startswith("#"):
    continue
```
- Las líneas vacías se ignoran
- Las líneas que empiezan con `#` son comentarios

**Paso 4: Validar formato básico**
```python
if ":" not in line:
    print(f"[ERROR] Line {line_num}: Missing ':' separator.")
    sys.exit(1)
```
- Toda línea válida debe tener el formato `"tipo: datos"`

**Paso 5: Extraer tipo y datos**
```python
key, content = line.split(":", 1)
key = key.strip().lower()
data = content.lower().strip().split(" ", 3)
```

**Ejemplo:**
```
Entrada: "Hub: waypoint1 10 20 [zone=priority]"
Resultado:
  - key = "hub"
  - data = ["waypoint1", "10", "20", "[zone=priority]"]
```

**Paso 6: Seleccionar procesador**
```python
processor = self.processors.get(key)
```
- Busca el procesador correspondiente al tipo
- Si no existe, imprime error y termina

**Paso 7: Procesar la línea**
```python
processor.process(data, self.simulation_map)
```
- Delega el procesamiento al procesador específico
- El procesador modifica `self.simulation_map` directamente

**Paso 8: Validaciones finales**

Después de procesar todas las líneas:

```python
# a. Buscar START y END
for hub in self.simulation_map.hubs.values():
    if hub.category == NodeCategory.START:
        start_hub = hub
        start_hub.current_drones = self.simulation_map.nb_drones
    elif hub.category == NodeCategory.END:
        end_hub = hub

# b. Validar que existen
if start_hub is None:
    # Error: Map is missing a Start Hub
if end_hub is None:
    # Error: Map is missing an End Hub

# c. Validar capacidades
# START debe poder contener todos los drones
# END debe poder contener todos los drones

# d. Retornar el mapa completo
return self.simulation_map
```

---

### 🔧 PROCESADORES DE LÍNEA

#### 📌 Clase `DroneProcessor`

**Archivo:** `src/parser/processors/drone_processor.py`

Procesa líneas del tipo: `"nb_drones: 5"`

```python
def _do_process(self, data: list[str], current_map: SimulationMap) -> None:
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `data` | `list[str]` | Lista con el valor del número de drones |
| `current_map` | `SimulationMap` | Mapa a modificar |

**Funcionamiento:**
- ✅ Valida que solo hay un valor numérico
- ✅ Valida que el número es mayor que 0
- ✅ Valida que no se ha definido antes
- ✅ Asigna: `current_map.nb_drones = int(data[0])`

---

#### 📌 Clase `HubProcessor`

**Archivo:** `src/parser/processors/hub_processor.py`

Procesa líneas del tipo: `"Hub: waypoint1 10 20 [zone=priority max_drones=3]"`

**Constantes:**
```python
ALLOWED_KEYS = {"zone", "color", "max_drones"}
```

**Constructor:**
```python
def __init__(self, category: NodeCategory = NodeCategory.INTERMEDIATE) -> None:
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `category` | `NodeCategory` | Categoría del hub (START, END, INTERMEDIATE) |

**Método `_do_process()`:**

```python
def _do_process(self, data: list[str], current_map: SimulationMap) -> None:
```

| Paso | Descripción |
|------|-------------|
| 1 | Validar que `nb_drones` está definido |
| 2 | Validar que hay al menos 3 parámetros (nombre, x, y) |
| 3 | Extraer nombre y verificar que no está duplicado |
| 4 | Verificar que coordenadas no están duplicadas |
| 5 | Parsear parámetros opcionales si existen |
| 6 | Crear objeto `Hub` con pydantic y añadirlo al mapa |

**Formato de parámetros opcionales:**
```
[key1=value1 key2=value2]
```

**Valores de `zone`:**
- `normal` - Sin restricciones
- `blocked` - Intransitable
- `restricted` - Requiere 2 turnos
- `priority` - Preferido en la selección

---

#### 📌 Clase `ConnectionProcessor`

**Archivo:** `src/parser/processors/connection_processor.py`

Procesa líneas del tipo: `"Connection: waypoint1-waypoint2 [max_link_capacity=2]"`

**Constantes:**
```python
ALLOWED_KEYS = {"max_link_capacity"}
```

**Método `_do_process()`:**

```python
def _do_process(self, data: list[str], current_map: SimulationMap) -> None:
```

| Paso | Descripción |
|------|-------------|
| 1 | Validar que `nb_drones` está definido |
| 2 | Parsear el formato `"source-target"` (exactamente un guión) |
| 3 | Verificar que source y target son diferentes |
| 4 | Verificar que ambos hubs existen |
| 5 | Verificar que la conexión no está duplicada |
| 6 | Parsear parámetros opcionales |
| 7 | Crear objeto `Connection` y añadirlo a `connections` |

> 📝 `connections` es un dict de dicts: `connections[source][target]`

---

### 📊 ESQUEMAS DE DATOS

#### 📌 Clase `SimulationMap`

**Archivo:** `src/schemas/simulation_map.py`

```python
class SimulationMap(BaseModel):
    """Map class with map file settings"""

    nb_drones: int
    hubs: dict[str, Any]
    connections: dict[str, Any]
```

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `nb_drones` | `int` | Número total de drones a enrutar |
| `hubs` | `dict[str, Hub]` | Diccionario de hubs indexado por nombre |
| `connections` | `dict[str, dict[str, Connection]]` | Conexiones bidimensionales |

---

#### 📌 Clase `Hub`

**Archivo:** `src/schemas/hubs.py`

```python
class Hub(MapEntity):
    """Hub Class Validation"""

    name: str
    category: NodeCategory
    type: ZoneType
    x: int
    y: int
    max_drones: int = Field(ge=1, default=1)
    current_drones: int = Field(ge=0, default=0)
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: str | None = Field(default=None)
```

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `name` | `str` | Identificador único del hub |
| `category` | `NodeCategory` | Rol: START, END, INTERMEDIATE |
| `type` | `ZoneType` | Tipo de zona (legacy, usar zone) |
| `zone` | `ZoneType` | Tipo: NORMAL, BLOCKED, RESTRICTED, PRIORITY |
| `x` | `int` | Coordenada X en el mapa |
| `y` | `int` | Coordenada Y en el mapa |
| `max_drones` | `int` | Capacidad máxima (default=1) |
| `current_drones` | `int` | Drones actualmente en el hub |
| `color` | `str \| None` | Color opcional para visualización |

---

#### 📌 Clase `Connection`

**Archivo:** `src/schemas/connection.py`

```python
class Connection(MapEntity):
    """Class for links between Hubs"""

    source: str
    target: str
    max_link_capacity: int = Field(ge=1, default=1)
    current_drones: int = Field(ge=0, default=0)
    cost: int = Field(default=1)
```

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `source` | `str` | Nombre del hub origen |
| `target` | `str` | Nombre del hub destino |
| `max_link_capacity` | `int` | Drones simultáneos permitidos (default=1) |
| `current_drones` | `int` | Drones actualmente en tránsito |
| `cost` | `int` | Costo base del viaje |

---

#### 📌 Enums: `ZoneType` y `NodeCategory`

**Archivo:** `src/schemas/definitions.py`

```python
class ZoneType(str, Enum):
    """Allowed areas"""
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class NodeCategory(str, Enum):
    """Node role on simulation"""
    START = "start"
    END = "end"
    INTERMEDIATE = "intermediate"
```

| ZoneType | Descripción |
|----------|-------------|
| `NORMAL` | Sin restricciones |
| `BLOCKED` | Intransitable |
| `RESTRICTED` | Requiere 2 turnos para atravesar |
| `PRIORITY` | Preferido en la selección de rutas |

| NodeCategory | Descripción |
|--------------|-------------|
| `START` | Punto de partida de todos los drones |
| `END` | Punto de llegada/objetivo |
| `INTERMEDIATE` | Waypoint intermedio |

---

## 3. ⏱️ FASE 2: ESTIMACIÓN DEL TIEMPO MÁXIMO

**Archivo:** `src/solver/time_estimator.py`

### Descripción General

Este módulo contiene funciones para estimar cuántos turnos necesitará la simulación. El grafo temporal necesita un límite de tiempo para construirse, y estas funciones calculan una estimación razonable.

---

### 📌 Función `has_path_to_end()`

```python
def has_path_to_end(simulation: SimulationMap) -> bool:
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `simulation` | `SimulationMap` | Mapa parseado |

| Retorno | Tipo | Descripción |
|---------|------|-------------|
| `bool` | `bool` | `True` si existe camino, `False` si no |

**Propósito:**
> 🎯 Detección temprana de mapas imposibles antes de gastar recursos construyendo el grafo temporal.

**Algoritmo:** BFS (Breadth-First Search) en el grafo estático

```python
# Paso 1: Identificar hubs de inicio y fin
start_hubs = [hubs con categoría START y zona != BLOCKED]
end_hubs = {hubs con categoría END y zona != BLOCKED}

# Paso 2: Si no hay start o end válidos, retornar False

# Paso 3: BFS desde el START
visited = set()
queue = deque([start_hub])

while queue:
    current = queue.popleft()

    if current in end_hubs:
        return True  # ¡Encontramos camino!

    if current in visited:
        continue
    visited.add(current)

    # Añadir vecinos no bloqueados
    for neighbor in connections[current]:
        if neighbor not in visited and not blocked:
            queue.append(neighbor)

return False  # No hay camino
```

---

### 📌 Función `estimate_min_path_length()`

```python
def estimate_min_path_length(simulation: SimulationMap) -> int:
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `simulation` | `SimulationMap` | Mapa parseado |

| Retorno | Tipo | Descripción |
|---------|------|-------------|
| `int` | `int` | Longitud mínima del camino más corto |

**Propósito:**
> 🎯 Conocer el mínimo absoluto de turnos necesarios para que un drone llegue al destino, considerando que zonas RESTRICTED cuestan 2 turnos.

**Algoritmo:** BFS modificado con peso de aristas

**Diferencia con `has_path_to_end()`:**
- Lleva cuenta de la distancia acumulada
- Zonas RESTRICTED suman 2 al costo, otras suman 1

```python
# Paso 1: Inicializar
visited = {}  # hub -> distancia mínima para llegar
queue = deque([(start_hub, 0)])

# Paso 2: BFS con distancias
while queue:
    current, distance = queue.popleft()

    if current in end_hubs:
        return distance  # Distancia mínima encontrada

    if current in visited:
        continue
    visited[current] = distance

    for neighbor in connections[current]:
        if neighbor not in visited and not blocked:
            cost = 2 if neighbor.zone == RESTRICTED else 1
            queue.append((neighbor, distance + cost))

return -1  # No hay camino
```

---

### 📌 Función `estimate_max_time()`

```python
def estimate_max_time(simulation: SimulationMap) -> int:
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `simulation` | `SimulationMap` | Mapa parseado |

| Retorno | Tipo | Descripción |
|---------|------|-------------|
| `int` | `int` | Tiempo máximo estimado para la simulación |

**Propósito:**
> 🎯 Proporcionar un límite de tiempo razonable para construir el grafo temporal. Debe ser suficiente para todos los drones considerando colas y congestión.

**Fórmula:**
```python
estimated_time = min_path_length + nb_drones
```

**Lógica:**

| Componente | Propósito |
|------------|-----------|
| `min_path_length` | Tiempo mínimo para UN drone sin congestión |
| `nb_drones` | Margen para colas en cuellos de botella |

**Ejemplo:**
```
min_path = 4 turnos
nb_drones = 10
estimated_time = 4 + 10 - 1 = 13 turnos
```

> 💡 Esta estimación garantiza solución a la primera en `create_solver()` porque cubre incluso el peor caso: drones en fila india esperando uno por uno.

---

## 4. 🕸️ FASE 3: CONSTRUCCIÓN DEL GRAFO TEMPORAL

**Archivo:** `src/solver/time_graph.py`
**Clase:** `TimeGraph`

### Descripción General

`TimeGraph` implementa un **"Time-Expanded Graph"** (Grafo Expandido en el Tiempo). Este es un concepto fundamental del sistema.

---

### ❓ ¿Qué es un Grafo Expandido en el Tiempo?

En un **grafo normal**, cada nodo representa una ubicación física.

En un **grafo expandido en el tiempo**, cada nodo representa una ubicación física **EN UN MOMENTO ESPECÍFICO DEL TIEMPO**.

**Ejemplo visual:**

```
Grafo normal:
    [A] ---> [B] ---> [C]

Grafo temporal (max_time=3):
    t=0: [A,0] ---> [B,1] ---> [C,2]
    t=1: [A,1] ---> [B,2] ---> [C,3]
    t=2: [A,2] ---> [B,3]
    t=3: [A,3]

    También hay "wait edges" (aristas de espera):
    [A,0] ---> [A,1] ---> [A,2] ---> [A,3]
    [B,1] ---> [B,2] ---> [B,3]
    etc.
```

**Esto permite modelar:**
1. ⏱️ El tiempo de viaje entre nodos
2. ⏸️ La espera en un nodo
3. ⚠️ Conflictos temporales (dos drones en el mismo lugar/momento)

---

### 🏗️ Clase `TimeGraph`

#### Constructor `__init__()`

```python
def __init__(self, simulation: SimulationMap, max_time: int) -> None:
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `simulation` | `SimulationMap` | El mapa parseado con hubs y conexiones |
| `max_time` | `int` | Límite temporal del grafo |

**Inicialización:**
```python
self.max_time = max_time
self.nodes: Dict[Tuple[str, int], TimeNode] = {}
self.edges: List[TimeEdge] = []
self.simulation: SimulationMap = simulation
```

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `nodes` | `Dict[Tuple[str, int], TimeNode]` | Diccionario indexado por `(nombre_hub, tiempo)` |
| `edges` | `List[TimeEdge]` | Lista plana de todas las aristas temporales |

---

#### Método `_add_node()`

```python
def _add_node(self, hub: Hub, turn: int) -> None:
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `hub` | `Hub` | Hub físico |
| `turn` | `int` | Instante temporal |

**Funcionamiento:**

```python
# Paso 1: Crear clave única
key = (hub.name, turn)  # Ej: ("waypoint1", 3)

# Paso 2: Verificar condiciones
# - Si la clave ya existe, no hacer nada
# - Si el hub está BLOCKED, no crear nodo

# Paso 3: Calcular drones iniciales
initial_drones = 0
if hub.category == NodeCategory.START and turn == 0:
    initial_drones = self.simulation.nb_drones
# ⚠️ El nodo START en t=0 comienza con todos los drones

# Paso 4: Crear y almacenar
self.nodes[key] = TimeNode(hub, turn, initial_drones)
```

---

#### Método `_add_edge()`

```python
def _add_edge(
    self, source: TimeNode, target: TimeNode, max_capacity: int = 1
) -> None:
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `source` | `TimeNode` | Nodo origen |
| `target` | `TimeNode` | Nodo destino |
| `max_capacity` | `int` | Capacidad máxima de drones simultáneos |

**Funcionamiento:**
```python
new_edge = TimeEdge(source, target, max_capacity)
self.edges.append(new_edge)
```

> 💡 La arista conecta un nodo en tiempo T1 con otro en tiempo T2. `max_capacity` limita cuántos drones pueden usar la arista simultáneamente.

---

#### Método `_get_travel_time()`

```python
def _get_travel_time(self, target_hub: Hub) -> int:
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `target_hub` | `Hub` | Hub de destino |

| Retorno | Tipo | Descripción |
|---------|------|-------------|
| `int` | `int` | Turnos necesarios para llegar |

**Funcionamiento:**
```python
if target_hub.zone == ZoneType.RESTRICTED:
    return 2  # Zonas restringidas tardan 2 turnos
return 1  # Todo lo demás tarda 1 turno
```

---

#### Método `build_graph()`

```python
def build_graph(self) -> None:
```

**Construye el grafo temporal completo. Este es el método principal.**

**Paso 1: Filtrar hubs válidos**
```python
hubs_dict = self.simulation.hubs
valid_hubs: Dict[str, Hub] = {
    name: hub for name, hub in hubs_dict.items()
    if hub.zone != ZoneType.BLOCKED
}
```
> ⚠️ Los hubs BLOCKED se excluyen completamente.

**Paso 2: Crear todos los nodos**
```python
for t in range(self.max_time + 1):
    for hub in valid_hubs.values():
        self._add_node(hub, t)
```
> 📊 Esto crea la "rejilla" de nodos temporales. Para `max_time=10` y 5 hubs, crea `11 * 5 = 55` nodos.

**Paso 3: Crear aristas de movimiento**
```python
for t in range(self.max_time):
    for source_name, targets in connections.items():
        for target_name, connection in targets.items():
            # Saltar si origen o destino no son válidos
            if source_name not in valid_hubs:
                continue
            if target_name not in valid_hubs:
                continue

            # Calcular tiempo de llegada
            target_hub = valid_hubs[target_name]
            travel_time = self._get_travel_time(target_hub)
            arrival_time = t + travel_time

            # Saltar si la llegada excede max_time
            if arrival_time > self.max_time:
                continue

            # Obtener nodos origen y destino
            source_node = self.nodes.get((source_name, t))
            target_node = self.nodes.get((target_name, arrival_time))

            # Crear la arista
            if source_node and target_node:
                self._add_edge(
                    source_node,
                    target_node,
                    connection.max_link_capacity
                )
```

**Paso 4: Crear aristas de espera (wait edges)**
```python
for hub in valid_hubs.values():
    wait_source = self.nodes.get((hub.name, t))
    wait_target = self.nodes.get((hub.name, t + 1))

    if wait_source and wait_target:
        self._add_edge(
            wait_source,
            wait_target,
            wait_source.hub.max_drones  # ⚠️ IMPORTANTE
        )
```

> ⚠️ **IMPORTANTE:** Las aristas de espera conectan el mismo hub en tiempos consecutivos. Su capacidad es la capacidad del hub (`max_drones`), **NO 1**. Esto permite que múltiples drones esperen en el mismo hub.

---

### 📊 MODELOS DE DATOS DEL GRAFO TEMPORAL

**Archivo:** `src/solver/models.py`

---

#### 📌 Clase `TimeNode`

Representa un hub físico en un momento específico del tiempo.

```python
class TimeNode:
    def __init__(self, hub: Hub, time: int, initial_drones: int = 0) -> None:
        self.hub: Hub = hub
        self.time: int = time
        self.is_priority: bool = self.hub.zone == ZoneType.PRIORITY
        self.is_end: bool = hub.category == NodeCategory.END
        self.current_drones: int = initial_drones
```

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `hub` | `Hub` | Referencia al hub físico |
| `time` | `int` | Instante temporal |
| `is_priority` | `bool` | Si es zona prioritaria |
| `is_end` | `bool` | Si es nodo final |
| `current_drones` | `int` | Drones en este nodo |

**Método `can_enter()`:**
```python
def can_enter(self) -> bool:
    """Verifica si hay espacio para un drone más."""
    return self.current_drones < self.hub.max_drones
```

**Método `add_drone()`:**
```python
def add_drone(self) -> None:
    """Registra un drone entrando al nodo."""
    self.current_drones += 1
```

**Métodos `__eq__` y `__hash__`:**
> 💡 Dos `TimeNodes` son iguales si tienen mismo `hub.name` y mismo `time`. Esto permite usarlos como claves de diccionario.

---

#### 📌 Clase `TimeEdge`

Representa una conexión entre dos `TimeNodes`.

```python
class TimeEdge:
    def __init__(
        self, source: TimeNode, target: TimeNode, max_capacity: int = 1
    ) -> None:
        self.source = source
        self.target = target
        self.duration = target.time - source.time
        self.max_capacity = max_capacity
```

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `source` | `TimeNode` | Nodo origen |
| `target` | `TimeNode` | Nodo destino |
| `duration` | `int` | Duración del viaje (`time_target - time_source`) |
| `max_capacity` | `int` | Capacidad máxima |

**Método `is_traversable()`:**
```python
def is_traversable(self, tracker: EdgeTracker) -> bool:
    """Verifica si la arista tiene capacidad disponible para todo el viaje."""
    for turn in range(self.duration):
        current_drones = tracker.get_current_drones(
            self, self.source.time + turn
        )
        if current_drones >= self.max_capacity:
            return False
    return True
```
> ⚠️ Para aristas de duración 2 (zonas RESTRICTED), verifica **AMBOS** turnos.

**Método `use_edge()`:**
```python
def use_edge(self, tracker: EdgeTracker) -> None:
    """Registra que un drone está usando esta arista."""
    for turn in range(self.duration):
        tracker.add_drone(self, self.source.time + turn)
```

---

#### 📌 Clase `EdgeTracker`

Gestiona la ocupación de aristas a través del tiempo.

```python
class EdgeTracker:
    def __init__(self) -> None:
        self.edge_drones: dict[tuple[TimeEdge, int], int] = defaultdict(int)
```

**Estructura interna:**
> La clave es `(arista, turno)`, el valor es el número de drones.

**Método `get_current_drones()`:**
```python
def get_current_drones(self, edge: TimeEdge, time: int) -> int:
    """Retorna cuántos drones están usando esta arista en este turno."""
    return self.edge_drones[(edge, time)]
```

**Método `add_drone()`:**
```python
def add_drone(self, edge: TimeEdge, time: int) -> None:
    """Incrementa el contador de drones en la arista/turno."""
    self.edge_drones[(edge, time)] += 1
```

---

## 5. 🧮 FASE 4: RESOLUCIÓN CON DIJKSTRA

**Archivo:** `src/solver/flow_solver.py`
**Clase:** `FlowSolver`

### Descripción General

`FlowSolver` resuelve el problema de enrutamiento de múltiples drones. Usa el **algoritmo de Dijkstra modificado** para encontrar el camino óptimo para cada drone, respetando las restricciones de capacidad.

### Estrategia

> 🎯 Los drones se procesan **SECUENCIALMENTE** (uno por uno). Cuando un drone reserva un camino, ese camino queda "ocupado" y los siguientes drones deben buscar alternativas o esperar.

---

### 🏗️ Clase `FlowSolver`

#### Constructor `__init__()`

```python
def __init__(self, time_graph: TimeGraph, nb_drones: int) -> None:
    self.time_graph = time_graph
    self.nb_drones = nb_drones
    self.tracker = EdgeTracker()
    self.adjacency: Dict[TimeNode, List[TimeEdge]] = self._build_adjacency()
    self.drone_paths: Dict[int, List[TimeNode]] = {}
```

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `time_graph` | `TimeGraph` | Grafo temporal construido |
| `nb_drones` | `int` | Número de drones a enrutar |
| `tracker` | `EdgeTracker` | Rastrea ocupación de aristas |
| `adjacency` | `Dict[TimeNode, List[TimeEdge]]` | Lista de adyacencia |
| `drone_paths` | `Dict[int, List[TimeNode]]` | Rutas encontradas |

---

#### Método `_build_adjacency()`

```python
def _build_adjacency(self) -> Dict[TimeNode, List[TimeEdge]]:
```

| Retorno | Tipo | Descripción |
|---------|------|-------------|
| `Dict[TimeNode, List[TimeEdge]]` | `Dict` | Lista de adyacencia |

**Funcionamiento:**
```python
adjacency: Dict[TimeNode, List[TimeEdge]] = {
    node: [] for node in self.time_graph.nodes.values()
}
for edge in self.time_graph.edges:
    if edge.source in adjacency:
        adjacency[edge.source].append(edge)
return adjacency
```

> 📊 **Resultado:** Para cada nodo, una lista de aristas salientes.

---

#### Método `find_start_node()` ⚠️ ACTUALIZADO

```python
def find_start_node(self) -> TimeNode:
```

| Retorno | Tipo | Descripción |
|---------|------|-------------|
| `TimeNode` | `TimeNode` | El único nodo START en tiempo 0 |

**Funcionamiento:**
```python
for node in self.time_graph.nodes.values():
    if node.time == 0 and node.hub.category == NodeCategory.START:
        return node
raise ValueError("No START node found at time=0")
```

> ⚠️ **CAMBIO IMPORTANTE:** Este método ahora devuelve un **único `TimeNode`** en lugar de una lista, ya que el parseo garantiza que solo existe exactamente un START hub.

---

#### Método `solve_all_drones()` ⚠️ ACTUALIZADO

```python
def solve_all_drones(self) -> Dict[int, List[TimeNode]]:
```

| Retorno | Tipo | Descripción |
|---------|------|-------------|
| `Dict[int, List[TimeNode]]` | `Dict` | Diccionario de rutas por drone ID |

**Método principal que coordina la resolución de todos los drones:**

```python
start_node = self.find_start_node()  # ⚠️ Ya no es una lista

for drone_id in range(1, self.nb_drones + 1):
    # Encontrar ruta para este drone
    path = self.solve_for_drone(drone_id, start_node)

    if path:
        # Guardar la ruta
        self.drone_paths[drone_id] = path
        # Reservar recursos (nodos y aristas)
        self._reserve_path(path)
    else:
        print(f"Drone {drone_id}: No valid path found!")

return self.drone_paths
```

**Orden de procesamiento:**
```
Drone 1 → Drone 2 → Drone 3 → ... → Drone N
```
> Cada drone tiene "prioridad" sobre los siguientes porque reserva primero los recursos.

---

#### Método `solve_for_drone()`

```python
def solve_for_drone(
    self, drone_id: int, start_node: TimeNode
) -> Optional[List[TimeNode]]:
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `drone_id` | `int` | ID del drone a resolver |
| `start_node` | `TimeNode` | Nodo de inicio |

| Retorno | Tipo | Descripción |
|---------|------|-------------|
| `Optional[List[TimeNode]]` | `Optional[List[TimeNode]]` | Ruta encontrada o `None` |

**Encuentra el mejor camino para UN drone usando Dijkstra modificado.**

##### Criterio de Optimización

Tupla `(turns, -priorities)` donde:
- `turns`: Tiempo total para llegar (**MINIMIZAR**)
- `priorities`: Zonas prioritarias visitadas (**MAXIMIZAR**)

> 💡 Al usar `-priorities`, el heap de Python (min-heap) prefiere caminos con más prioridades cuando el tiempo es igual.

##### Estructuras de Datos

| Variable | Tipo | Descripción |
|----------|------|-------------|
| `best` | `Dict[TimeNode, Tuple[int, int]]` | Mejor (distancia, prioridades) conocida para cada nodo |
| `parents` | `Dict[TimeNode, Optional[TimeNode]]` | Nodo padre en el camino óptimo (para reconstruir ruta) |
| `pq` | `List[Tuple[...]]` | Cola de prioridad: `((distancia, -prioridades), id_unico, nodo)` |
| `visited` | `set[TimeNode]` | Nodos ya procesados |

##### Algoritmo Paso a Paso

**Paso 1: Inicialización**
```python
start_priority = 1 if start_node.hub.zone == ZoneType.PRIORITY else 0

best = {start_node: (0, start_priority)}
parents = {start_node: None}
pq = [((0, -start_priority), id(start_node), start_node)]
visited = set()
```

**Paso 2: Bucle principal**
```python
while pq:
    # Extraer nodo con menor costo
    (current_dist, neg_priority), _, current_node = heapq.heappop(pq)
    current_priority = -neg_priority

    # Saltar si ya visitamos este nodo
    if current_node in visited:
        continue
    visited.add(current_node)

    # ¿Llegamos al END?
    if current_node.hub.category == NodeCategory.END:
        path = self._reconstruct_path(parents, current_node)
        return path
```

**Paso 3: Explorar vecinos**
```python
for edge in self.adjacency.get(current_node, []):
    neighbor = edge.target

    # Saltar nodos ya visitados
    if neighbor in visited:
        continue

    # Verificar capacidad de la arista
    if not edge.is_traversable(self.tracker):
        continue

    # Verificar capacidad del nodo destino
    is_start_at_zero = (
        neighbor.hub.category == NodeCategory.START
        and neighbor.time == 0
    )
    if not is_start_at_zero and not neighbor.can_enter():
        continue

    # Calcular nuevo costo
    new_dist = current_dist + edge.duration
    neighbor_priority = (
        1 if neighbor.hub.zone == ZoneType.PRIORITY else 0
    )
    new_priority = current_priority + neighbor_priority

    # Comparar con el mejor conocido
    current_best = best.get(neighbor)
    new_cost = (new_dist, -new_priority)
    best_cost = (
        (current_best[0], -current_best[1])
        if current_best
        else None
    )

    # Actualizar si es mejor
    if best_cost is None or new_cost < best_cost:
        best[neighbor] = (new_dist, new_priority)
        parents[neighbor] = current_node
        heapq.heappush(
            pq,
            (new_cost, id(neighbor), neighbor)
        )
```

**Paso 4: Si no se encontró camino**
```python
return None
```

##### Ejemplo de Comparación de Costos

| Camino | Turnos | Prioridades | Costo (tuple) |
|--------|--------|-------------|---------------|
| A | 5 | 2 | `(5, -2)` |
| B | 5 | 1 | `(5, -1)` |
| C | 4 | 0 | `(4, 0)` |

**Orden de preferencia:** C < A < B

> C es mejor porque `4 < 5`, A es mejor que B porque `-2 < -1`

---

#### Método `_reconstruct_path()`

```python
def _reconstruct_path(
    self, parents: Dict[TimeNode, Optional[TimeNode]], end_node: TimeNode
) -> List[TimeNode]:
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `parents` | `Dict[TimeNode, Optional[TimeNode]]` | Diccionario de padres |
| `end_node` | `TimeNode` | Nodo final |

| Retorno | Tipo | Descripción |
|---------|------|-------------|
| `List[TimeNode]` | `List[TimeNode]` | Ruta reconstruida |

**Funcionamiento:**
```python
path = []
current = end_node
while current is not None:
    path.append(current)
    current = parents.get(current)
path.reverse()
return path
```

> 📊 **Resultado:** Lista ordenada `[start, ..., ..., end]`

---

#### Método `_reserve_path()`

```python
def _reserve_path(self, path: List[TimeNode]) -> None:
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `path` | `List[TimeNode]` | Ruta a reservar |

**Reserva todos los recursos usados por un camino:**

**Paso 1: Reservar aristas**
```python
edges = self._get_path_edges(path)
for edge in edges:
    edge.use_edge(self.tracker)
```
> Esto marca la arista como ocupada en los turnos correspondientes.

**Paso 2: Reservar nodos**
```python
for node in path:
    is_start_at_zero = (
        node.hub.category == NodeCategory.START and node.time == 0
    )
    if not is_start_at_zero:
        node.add_drone()
```

> ⚠️ **Excepción:** El nodo START en t=0 ya tiene los drones contabilizados, por lo que no se incrementa.

---

## 6. 📤 FASE 5: GENERACIÓN DEL OUTPUT

**Archivo:** `src/solver/flow_solver.py`
**Métodos de output en FlowSolver**

### Descripción General

Después de resolver las rutas, el sistema genera la salida en el formato específico requerido: una línea por turno, con los movimientos de todos los drones separados por espacios.

### Formato de Salida

```
D1-waypoint2 D2-waypoint1
D1-end D2-waypoint2
D2-end
```

| Elemento | Formato | Descripción |
|----------|---------|-------------|
| Línea | `movimiento1 movimiento2...` | Un turno completo |
| Movimiento normal | `D<id>-<destino>` | Drone moviéndose |
| Movimiento RESTRICTED | `D<id>-<origen>-<destino>` | Drone en tránsito a zona restringida |

---

### 📌 Método `get_simulation_output()`

```python
def get_simulation_output(self) -> List[str]:
```

| Retorno | Tipo | Descripción |
|---------|------|-------------|
| `List[str]` | `List[str]` | Lista de líneas de salida |

**Genera la lista completa de líneas de salida:**

**Paso 1: Verificar que hay rutas**
```python
if not self.drone_paths:
    return []
```

**Paso 2: Calcular tiempo máximo**
```python
max_time = max(
    path[-1].time for path in self.drone_paths.values() if path
)
```
> El último nodo de cada path (el END) determina cuándo termina.

**Paso 3: Iterar por cada turno**
```python
output_lines: List[str] = []
delivered: set[int] = set()  # Drones que ya llegaron al END

for t in range(max_time):
    movements: List[str] = []
```

**Paso 4: Para cada drone en este turno**
```python
for drone_id, path in sorted(self.drone_paths.items()):
    if drone_id in delivered:
        continue  # Ya llegó, no reportar
```

**Paso 5: Encontrar posición actual del drone**
```python
current_node = None
next_node = None

for i, node in enumerate(path):
    if node.time == t:
        current_node = node
        if i + 1 < len(path):
            next_node = path[i + 1]
        break
```

**Paso 6: Manejar casos especiales**
```python
# Caso: Drone en vuelo hacia zona RESTRICTED
if current_node is None:
    in_flight = self._is_in_flight_to_restricted(drone_id, t)
    if in_flight:
        movements.append(f"D{drone_id}-{in_flight}")
    continue

# Caso: Drone esperando (mismo nodo en t y t+1)
if next_node and next_node.hub.name == current_node.hub.name:
    continue  # No reportar esperas
```

**Paso 7: Generar movimiento**
```python
if next_node:
    destination = next_node.hub.name

    if next_node.hub.zone == ZoneType.RESTRICTED:
        # Formato especial para zonas restringidas
        connection = self._get_connection_name(
            current_node.hub.name, next_node.hub.name
        )
        movements.append(f"D{drone_id}-{connection}")
    else:
        # Formato normal
        movements.append(f"D{drone_id}-{destination}")

    # Marcar como entregado si llegó al END
    if next_node.hub.category == NodeCategory.END:
        delivered.add(drone_id)
```

**Paso 8: Añadir línea si hay movimientos**
```python
if movements:
    output_lines.append(" ".join(movements))
```

**Paso 9: Retornar resultado**
```python
return output_lines
```

---

### 📌 Método `_is_in_flight_to_restricted()`

```python
def _is_in_flight_to_restricted(
    self, drone_id: int, current_time: int
) -> Optional[str]:
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `drone_id` | `int` | ID del drone |
| `current_time` | `int` | Turno actual |

| Retorno | Tipo | Descripción |
|---------|------|-------------|
| `Optional[str]` | `Optional[str]` | Formato de conexión o `None` |

**Detecta si un drone está en tránsito hacia una zona RESTRICTED:**

> 🚁 Las zonas RESTRICTED tardan 2 turnos. Durante el turno intermedio, el drone no está en ningún nodo (está "en el aire").

```python
for i, node in enumerate(path):
    if i + 1 < len(path):
        next_node = path[i + 1]
        if (
            node.time < current_time
            and next_node.time > current_time
            and next_node.hub.zone == ZoneType.RESTRICTED
        ):
            return f"{node.hub.name}-{next_node.hub.name}"
return None
```

---

### 📌 Método `print_simulation_output()`

```python
def print_simulation_output(self) -> None:
```

**Imprime el resultado final a stdout:**

```python
output = self.get_simulation_output()
for line in output:
    print(line)
```

---

## 7. 📊 ESTRUCTURAS DE DATOS CLAVE - RESUMEN

### 🗂️ Esquemas de Entrada

**Ubicación:** `src/schemas/`

```
SimulationMap
├── nb_drones: int
├── hubs: dict[str, Hub]
└── connections: dict[str, dict[str, Connection]]

Hub
├── name: str
├── category: NodeCategory (START/END/INTERMEDIATE)
├── zone: ZoneType (NORMAL/BLOCKED/RESTRICTED/PRIORITY)
├── x, y: int (coordenadas)
├── max_drones: int (capacidad)
└── current_drones: int

Connection
├── source: str
├── target: str
├── max_link_capacity: int
└── current_drones: int
```

---

### ⏱️ Modelos del Grafo Temporal

**Ubicación:** `src/solver/models.py`

```
TimeNode
├── hub: Hub (referencia al hub físico)
├── time: int (instante temporal)
├── is_priority: bool
├── is_end: bool
├── current_drones: int
├── can_enter() -> bool
└── add_drone() -> None

TimeEdge
├── source: TimeNode
├── target: TimeNode
├── duration: int (time_target - time_source)
├── max_capacity: int
├── is_traversable(tracker) -> bool
└── use_edge(tracker) -> None

EdgeTracker
├── edge_drones: dict[(TimeEdge, int), int]
├── get_current_drones(edge, time) -> int
└── add_drone(edge, time) -> None
```

---

### 🕸️ Grafo Temporal

**Ubicación:** `src/solver/time_graph.py`

```
TimeGraph
├── max_time: int
├── nodes: dict[(str, int), TimeNode]
├── edges: list[TimeEdge]
├── simulation: SimulationMap
└── build_graph() -> None
```

---

### 🧮 Solver

**Ubicación:** `src/solver/flow_solver.py`

```
FlowSolver
├── time_graph: TimeGraph
├── nb_drones: int
├── tracker: EdgeTracker
├── adjacency: dict[TimeNode, list[TimeEdge]]
├── drone_paths: dict[int, list[TimeNode]]
├── find_start_node() -> TimeNode           # ⚠️ ACTUALIZADO: retorna único nodo
├── solve_all_drones() -> dict[int, list[TimeNode]]
├── solve_for_drone(id, start) -> list[TimeNode]
├── get_simulation_output() -> list[str]
└── print_simulation_output() -> None
```

---

## 📈 DIAGRAMA DE FLUJO COMPLETO

```
┌─────────────────────────────────────────────────────────────────┐
│                    python main_solver.py map.txt                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. PARSEO                                                      │
│     FileParser.parse(map.txt)                                   │
│     ├── DroneProcessor -> nb_drones                             │
│     ├── HubProcessor -> hubs dict                               │
│     └── ConnectionProcessor -> connections dict                 │
│     Resultado: SimulationMap                                    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. VALIDACIÓN                                                  │
│     has_path_to_end(simulation)                                 │
│     └── BFS: ¿Existe camino START → END?                        │
│     Si no existe → ERROR y salir                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. ESTIMACIÓN TEMPORAL                                         │
│     estimate_max_time(simulation)                               │
│     ├── estimate_min_path_length() → BFS con pesos              │
│     └── max_time = min_path + nb_drones                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. CONSTRUCCIÓN DEL SOLVER (create_solver)                      │
│                                                                 │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │  4a. CONSTRUCCIÓN DEL GRAFO                             │ │
│     │      TimeGraph(simulation, max_time)                    │ │
│     │      build_graph()                                      │ │
│     │      ├── Crear TimeNodes para cada (hub, t)             │ │
│     │      ├── Crear TimeEdges de movimiento                  │ │
│     │      └── Crear TimeEdges de espera                      │ │
│     └─────────────────────────────────────────────────────────┘ │
│                          │                                      │
│                          ▼                                      │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │  4b. RESOLUCIÓN                                         │ │
│     │      FlowSolver(time_graph, nb_drones)                  │ │
│     │      solve_all_drones()                                 │ │
│     │                                                         │ │
│     │      Para cada drone 1..N:                              │ │
│     │      ├── solve_for_drone() → Dijkstra modificado        │ │
│     │      │   ├── Heap con (turns, -priorities)              │ │
│     │      │   ├── Verificar capacidad aristas (tracker)      │ │
│     │      │   └── Verificar capacidad nodos (can_enter)      │ │
│     │      └── _reserve_path() → Marcar recursos usados       │ │
│     └─────────────────────────────────────────────────────────┘ │
│                          │                                      │
│                          ▼               ✅ ÉXITO GARANTIZADO   │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │  4c. RETORNO                                            │ │
│     │      Todos los drones tienen ruta → Continuar a paso 5 │ │
│     │      (Sin reintentos, gracias a estimación óptima)      │ │
│     └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. GENERACIÓN DE OUTPUT                                        │
│     get_simulation_output()                                     │
│     ├── Para cada turno t:                                      │
│     │   ├── Para cada drone:                                    │
│     │   │   ├── Encontrar posición en t                         │
│     │   │   └── Generar "D<id>-<destino>"                       │
│     │   └── Unir movimientos con espacios                       │
│     └── Retornar lista de líneas                                │
│                                                                 │
│     print_simulation_output()                                   │
│     └── Imprimir cada línea a stdout                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  OUTPUT FINAL                                                   │
│  D1-waypoint1 D2-waypoint1 D3-waypoint1                         │
│  D1-waypoint2 D2-waypoint2 D3-waypoint2                         │
│  D1-end D2-waypoint3 D3-waypoint3                               │
│  D2-end D3-end                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### 📝 Estimación Matemáticamente Óptima

| Fórmula | Valor | Descripción |
|---------|-------|-------------|
| `min_path + (nb_drones - 1)` | Dinámico | Tiempo máximo garantizado |

> ✅ **Sin reintentos:** Con esta fórmula, `create_solver()` siempre encuentra solución a la primera. No hay bucle de reintentos.

---

> 📄 **FIN DE LA DOCUMENTACIÓN**
