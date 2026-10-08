# 16. La foto del café

**Category**: OSINT
**Difficulty**: EASY
**Points**: 100

> **Estado: resuelto.** Flag confirmada por la plataforma del evento (veredicto `correct`).

## Description

> Encontraste esta foto en un foro anónimo. Alguien dice que está "cerca de donde trabaja el
> objetivo". Descubre la ciudad exacta donde se tomó la foto.
> Objetivo: encontrar la ciudad. Flag: `EVIL{ciudad}`

## Reconnaissance

La vía obvia es el EXIF, y aquí no hay nada:

```console
$ exiftool -a -u -g fotocafe.jpg | grep -iE 'gps|software|source|artist'
Artist                          : ffe2273b-e7e6-4919-a6dd-cd3ff448007a
Actions Software Agent          : Grok Imagine
Actions Digital Source Type     : http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia
```

No hay GPS, ni modelo de cámara, ni marcas temporales. La imagen está **generada por IA**
(manifiesto C2PA de Grok Imagine) y el propio manifiesto declara que es contenido algorítmico
entrenado. Tampoco hay bytes ocultos tras el marcador EOI.

Un intento anterior propuso `EVIL{santa_fe}` por correlación temática con otro reto del
evento (la "costanera"). **La plataforma lo rechazó.** La coherencia temática entre retos no
es evidencia: es la forma más rápida de perder tiempo.

## Analysis

El error de partida fue tratar esto como un problema de metadatos. La imagen es sintética,
así que los metadatos solo describen el generador. Pero *sintética* no significa *sin
referencia*: un generador de imágenes no inventa el anfiteatro Flavio con esa precisión
estructural por azar. El autor pidió esa vista, y la vista contiene la respuesta.

Mirando la imagen:

- Primer plano: un cappuccino con arte de latte sobre una mesa de madera, junto a una ventana.
- Fondo, a la izquierda y **a través del vidrio**: el anfiteatro Flavio, el Colosseo de Roma.
  Tres órdenes de arcos superpuestos, el segundo más bajo que el primero, la Solutions Curve
  de ladrillo coronando el conjunto. Es inconfundible y no es una estructura genérica.
- Al fondo a la derecha, colinas con vegetación y cielo despejado.

El enunciado encaja: un café con esa vista está en una ciudad y, por tanto, en el lugar donde
trabaja el objetivo. Ciudad: **Roma**.

## Exploitation

No hay nada que explotar; hay que mirar. El camino reproducible es:

1. Descartar los metadatos (EXIF/C2PA) como fuente de ubicación.
2. Mirar la imagen y describir lo que se ve, sin apoyarse en la temática del CTF.
3. Nombrar el monumento y derivar la ciudad.
4. Comprobar contra la plataforma:

```console
$ python3 scripts/lib/ctf_platform.py submit 16 'EVIL{roma}'
correct
$ python3 scripts/lib/ctf_platform.py claim 16 'EVIL{roma}'
#16 EVIL{roma} -> correct
[ok] registrado en challenges/16-la-foto-del-cafe/flag.txt
```

## Flag

```
EVIL{roma}
```

## Key Takeaways

- **Un manifiesto C2PA de imagen generada no elimina la pregunta**: cambia la fuente de la
  respuesta de los metadatos al contenido. Un generador reproduce la referencia que le
  pedimos; esa referencia es la pista.
- **La calidad JPEG delata el pipeline.** Esta imagen es calidad 95 (Grok); el reto #17 del
  mismo evento es una foto real en calidad 85. Comparar ese dato basta para separar las dos
  categorías de reto sin herramientas especiales.
- **La correlación temática entre retos es un sesgo peligroso.** La bandera del capybara
  empujaba a "Santa Fe" sin ninguna evidencia; la plataforma lo rechazó.
- Una imagen generada por IA no puede geolocalizarse por EXIF, pero sí puede identificar el
  monumento que el autor quiso mostrar.

## References

- Anfiteatro Flavio (Colosseo), Roma: https://es.wikipedia.org/wiki/Anfiteatro_Flavio
- Content Credentials / C2PA: https://c2pa.org/

## Solve Script

`python3 solve.py` — vuelca los metadatos que descartan la vía EXIF, expone la lectura visual
del encuadre y muestra la flag confirmada por la plataforma.