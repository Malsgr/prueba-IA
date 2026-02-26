
# Proyecto Hackaton

## El juego
### La Idea
La idea es crear un juego de consola basado en el clásico buscaminas, pero con un 'twist'.

En vez de una cuadrícula e ir marcando las minas con el ratón, el jugador tendrá un avatar en el mapa, con visión limitada, y deberá usar un sistema de radar para localizar donde están las minas.

### Detalles
#### Mapa
El mapa será una cuadrícula, el tamaño base será de 33x33, pero podrá variar según la dificultad elegida. El número de minas se calculará multiplicando el número de cuadrados totales menos uno (1088) por 0.05, de forma que cada cuadrado tiene una probabilidad del 5% de contener una mina (54 minas para 1089 cuadrados). Las minas se colocarán aleatoriamente por todo el mapa al empezar la partida, con la única excepción del cuadrado central (porque será el punto de aparición del jugador). 

#### Gameplay

El jugador se podrá mover por el mapa con las flechas del teclado. Las minas solo explotan si te mueves a su espacio y después fuera de él sin desactivarla. Para desactivar una mina, deberá moverse a su espacio y pulsar la tecla 'W', lo que evitará que explote al moverte fuera de el y mostrará ese cuadrado de color rojo.

De forma similar al buscaminas original, todo cuadrado sin ninguna mina en un area de 3x3 (alrededor suya) al que el jugador tenga acceso directo (moviendose solamente a traveś de otros cuadrados seguros), será llamado 'seguro', aparecerá de color blanco y se 'propagará' a los cuadros adyacentes, obligandolos a revelarse si tambien son 'seguros'. Los detalles de como operará esta mecánica los describiré más adelante, en el apartado "Como hacerlo". 

Todo cuadrado que **si** tenga alguna mina adyacente (o cuadro naranja), serán los llamados "cuadros naranjas", también se mostraran blancos para el jugador, pero no obligarán a los cuadros blancos de alrededor a mostrarse.

En lugar de que cada cuadrado contenga un número que indique cuantas minas hay adyacentes, el jugador podrá pulsar la tecla 'Q', que reproducirá un sonido cuyo tono varie según el número de minas alrededor. Un tono bajo si solo hay una y uno ligeramente más alto (pero claramente distinguible) si hay dos, y otro más alto si hay tres y etc etc.

Para una capa extra de dificultad, el jugador solo podrá ver los cuadros blancos y minas descubiertas en un area de 11x11 a su alrededor (que se moverá con el jugador), todos los demás cuadrados se mostrarán grises.

Finalmente, el jugador tendrá libertad para moverse por todo el mapa en todo momento, pero no revelará los cuadros blancos no descubiertos si se encuentra con ellos de casualidad. Y por supuesto, pasar por encima de una mina sin desactivarla revelará todas las minas restantes y terminará el juego.

#### Como hacerlo

Los cuadrados pueden ser una mina o no, pueden ser 'seguros' o 'naranjas', pueden ser 'visibles' o no
