# NeuroEcosistema · Julián Pulido

Proyecto final integrador de Inteligencia Artificial, Universidad Santo Tomás, Seccional Tunja. El informe técnico, la bitácora y las gráficas están en **Informe_Julian_Pulido.pdf**.

## Ejecutar en Windows

Extraiga el ZIP completo. Abra una terminal en la carpeta que contiene app.py. Requiere Python 3.10 o posterior con Tkinter (incluido en la instalación habitual de Python para Windows).

~~~powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python app.py
~~~

En Linux o macOS use python3 para crear el entorno y .venv/bin/python para los siguientes comandos. La distribución de Python debe incluir Tk.

Seleccione escenario, política y semilla, pulse **Reiniciar** y luego **Iniciar**. Puede pausar o avanzar un paso. Reiniciar aplica los cambios de controles. El inspector muestra el primer agente activo de cada especie en la decisión previa al movimiento. La energía mostrada en su vector está normalizada por 80.

## Reproducir el análisis

Desde el entorno, ejecute **python experimento.py** y después **python informe.py**. El primer comando vuelve a crear los cuatro archivos NPZ y los dos CSV; el segundo vuelve a generar el PDF. Los modelos ya incluidos permiten iniciar la demo directamente. ecosistema.py define las configuraciones, las reglas y la inferencia. Los resultados pueden presentar pequeñas diferencias numéricas según la plataforma.

## Guion para la sustentación

1. Abra Abundancia, Red 24, semilla 101. Pulse Un paso. Lea los cuatro puntajes de una presa y señale el mayor. Los índices 0, 1, 2 y 3 corresponden a derecha, abajo, izquierda y arriba.
2. Ejecute un episodio, anote capturas y alimento. Cambie a Inicial 24, reinicie con idéntica semilla y compare. Explique que ambas especies cambian de política simultáneamente.
3. Vuelva a Red 24 y cambie únicamente a Presión. El número inicial de depredadores pasa de dos a cinco. Compare lo observado con las diez repeticiones de la página 3 del informe.
4. Muestre la curva de entrenamiento. La regla genera etiquetas durante el entrenamiento. Durante la demo neuronal el agente elige el mayor puntaje calculado por sus pesos.
5. Si preguntan qué red ganó, indique primero la métrica. Red 48 consiguió más alimento que Red 24 en los tres escenarios. En presión la red inicial dio mayor vida media a las presas, con muchos menos éxitos de caza.
6. Si preguntan qué mejoraría, proponga mantener fija la política rival y repetir el entrenamiento con varias inicializaciones. Así se distinguen efectos del rival, del entorno y de los pesos de partida.

## Repositorio de entrega

El paquete contiene los archivos para la raíz de un repositorio GitHub. Para publicarlo desde una cuenta propia cree un repositorio vacío y cargue los archivos de esta carpeta mediante Add file → Upload files. Incluya los modelos, el informe y los CSV junto al código. Comparta el enlace con el docente.
