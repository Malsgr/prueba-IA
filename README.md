
# Proyecto Hackaton

## El juego
### La Idea
La idea es crear un juego de consola basado en el clásico buscaminas, pero con un 'twist'.

En vez de una cuadrícula e ir marcando las minas con el ratón, el jugador tendrá un avatar en el mapa, con visión limitada, y deberá usar un sistema de radar para localizar donde están las minas.

### Detalles
#### Mapa
El mapa será una cuadrícula, el tamaño base será de 33x33, pero podrá variar según la dificultad elegida. El número de minas se calculará multiplicando el número de cuadrados totales menos uno (1088) por 0.05, de forma que cada cuadrado tiene una probabilidad del 5% de contener una mina (54 minas para 1089 cuadrados). Las minas se colocan por el mapa al principio de la partida, los detalles en la generación se explican más adelante, pero nunca en la casilla central (ese será el punto de aparición del jugador). 

#### Gameplay

El jugador se podrá mover por el mapa con las flechas del teclado. Las minas solo explotan si te mueves a su espacio y después fuera de él (sin desactivarla). Para desactivar una mina, deberá moverse a su espacio y pulsar la tecla 'W', lo que evitará que explote al moverte fuera de el y mostrará ese cuadrado de color rojo. El cuadrado que ocupa el jugador se mostrará de color azul.

De forma similar al buscaminas original, todo cuadrado sin ninguna mina en un area de 3x3 (alrededor suya) al que el jugador tenga acceso directo (moviendose solamente a traveś de otros cuadrados seguros), será llamado 'seguro', aparecerá de color blanco y se 'propagará' a los cuadros adyacentes, obligandolos a revelarse si tambien son 'seguros'. Los detalles de como operará esta mecánica los describiré más adelante, en el apartado "Como hacerlo". 

Todo cuadrado que **si** tenga alguna mina adyacente (o cuadro naranja), serán los llamados "cuadros naranjas", también se mostraran blancos para el jugador, pero no obligarán a los cuadros 'seguros' de alrededor a mostrarse.

En lugar de que cada cuadrado contenga un número que indique cuantas minas hay adyacentes, el jugador podrá pulsar la tecla 'Q', que reproducirá un sonido cuyo tono varie según el número de minas alrededor. Do si solo hay una mina, Re si hay dos, Mi si hay tres y así hasta Sol para cinco o más minas.

Para una capa extra de dificultad, el jugador solo podrá ver los cuadros blancos y minas descubiertas en un area de 11x11 a su alrededor (que se moverá con el jugador), todos los demás cuadrados se mostrarán grises claro.

Existe un fallo de diseño que el jugador podría explotar, pulsar 'W' cada vez que se mueve a una nueva casilla. Si tiene una mina, los cuadros 'naranjas' de alrededor pasarán a ser 'seguros' y revelarán parte del mapa. Si no tiene una mina, no ocurrirá nada y puede moverse al siguiente cuadrado y hacer lo mismo hasta ganar el juego. Para evitar esto implementaremos un sistema de vidas, intentar desactivar una casilla sin una mina significará perder una (de tres) vidas.

El jugador tendrá libertad para moverse por todo el mapa en todo momento, pero no revelará los cuadros blancos no descubiertos si se encuentra con ellos de casualidad. Y por supuesto, pasar por encima de una mina sin desactivarla revelará todas las minas restantes y el jugador perderá todas sus vidas restantes, terminando el juego al instante. La victoria se obtiene cuando todas las minas hayan sido desactivadas.

#### Como hacerlo

Los cuadrados pueden ser 'activo', 'seguros', 'naranjas', o 'no descubiertos' y pueden ser 'visibles' o no. Todas estás serán variables que tendrán cada uno de los cuadrados, esto es exactamente lo que significa cada una:

- Activo: Si el cuadrado contiene una mina no desactivada por el jugador.

- Seguro: No tienen ninguna mina ni cuadrado 'naranja' adyacente. Se muestra de color blanco para el jugador y obliga a otros cuadrados 'seguros' de alrededor a mostrarse. Cuando una mina es marcada por el jugador, su estado cambia a este.

- Naranja: Son aquellos cuadrados que si tienen alguna mina o cuadrado 'naranja' adyacente. También se muestran blancos pero no obligan a los cuadrados de alrededor a mostrarse.

- No descubierto: Son aquellos cuadrados que no han sido obligados a mostrarse por un cuadrado 'seguro' ni contiene una mina. Se muestran se color gris oscuro, al igual que las minas no marcadas.

- Visibles: Todos los cuadrados son de color gris claro a menos que tengan esta propiedad. Esta propiedad la obtienen los cuadrados cuando el jugador se mueve de forma que los incluya en el area de 11x11 de la que hablamos antes.

Todas estas propiedades se comprueban para todos los cuadrados cada vez que un nuevo cuadrado obtiene la propiedad de seguro. Excepto la propiedad 'visible', que se actualiza cada vez que le jugador se mueve.

Pulsar 'W' en una casilla siempre la marcará como segura, pero si esa casilla no tiene una mina el jugador perderá una vida.

El cuadrado central en el que aparece el jugador siempre tiene la propiedad de 'seguro' desde el principio, para que siempre se tenga un area inicial.

 ---

Finalmente, hay un problema importante que se debe solucionar. El buscaminas original está diseñado de forma que no tengas que tomar ningún riesgo para encontrar todas las minas, parecido a un puzzle. Pero en esta variación, dado que el jugador tiene que moverse a través del mapa, existen muchas posiciones en las que podrían aparecer las minas que obligarían al jugador a entrar en una casilla que podría tener una mina. Obligandole a morir o, al menos, perder una vida. No queremos eso, queremos castigar solo los errores, no someter al jugador a la alaetoriedad.

Para solucionarlo, las minas no se posicionarán en el mapa aleatoriamente. ChatGPT ha creado el siguiente algoritmo

```
Generación de Minas (Sin Riesgo Obligatorio)

FASE 1 — Crear Región Segura Inicial

1. Inicializar el mapa vacío.
2. Marcar la casilla central como `segura`.
3. Generar una región segura conectada mediante flood-fill desde el centro:
   - Expandir a casillas adyacentes con probabilidad controlada.
   - Garantizar que toda la región resultante sea un único componente conectado.
4. La región segura debe ocupar aproximadamente entre 35% y 45% del mapa.
5. Ninguna mina puede colocarse dentro de esta región.

---

FASE 2 — Construir la Frontera

1. Definir la `frontera` como todas las casillas no seguras que sean adyacentes a al menos una casilla segura.
2. Solo se podrán colocar minas en casillas pertenecientes a la frontera.
3. No se permite colocar minas:
   - En el interior de la región segura.
   - En zonas completamente aisladas del área segura.
   - De forma que creen muros cerrados sin caminos alternativos.

---

FASE 3 — Colocación Controlada de Minas

Mientras `minas_colocadas < objetivo`:

1. Seleccionar una casilla aleatoria de la frontera.
2. Simular la colocación de una mina en esa casilla.
3. Verificar que:
   - La región segura siga siendo un único componente conectado.
   - No se cree un cuello de botella de ancho 1 que conecte regiones amplias.
   - Exista al menos un camino alternativo entre zonas seguras grandes.
4. Si la colocación rompe alguna condición:
   - Descartar la casilla.
5. Si la colocación es válida:
   - Confirmar la mina.
6. Actualizar la frontera tras cada colocación.

La conectividad puede comprobarse mediante BFS o DFS sobre las casillas seguras.

---

FASE 4 — Validación Lógica del Tablero

1. Simular un solver lógico determinista desde la casilla central.
2. Aplicar iterativamente:
   - Si una casilla tiene N minas posibles y exactamente N sin marcar → marcar como mina.
   - Si ya están marcadas todas las minas posibles alrededor → el resto son seguras.
3. Repetir hasta que no haya cambios.
4. Si en algún punto el solver requiere adivinación:
   - Rechazar el tablero completo.
   - Regenerar desde la FASE 1.

```
