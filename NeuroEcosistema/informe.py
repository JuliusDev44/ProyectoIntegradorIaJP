"""Regenera el informe y sus gráficas a partir de los CSV."""
import csv
import textwrap
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from ecosistema import ROOT, MODES, SCENARIOS

rows = list(csv.DictReader((ROOT/"episodios.csv").open(encoding="utf8")))
training = list(csv.DictReader((ROOT/"entrenamiento.csv").open(encoding="utf8")))
pdf = PdfPages(ROOT/"Informe_Julian_Pulido.pdf")


def values(scene,mode,key):
    return np.array([float(r[key]) for r in rows if r["escenario"]==scene and r["politica"]==mode and r[key]])


def page(title, number):
    global fig, y
    fig = plt.figure(figsize=(8.27,11.69))
    fig.text(.09,.94,"USTA TUNJA   /   ELECTIVA I DE PROFUNDIZACIÓN",size=10,color="#22766d")
    fig.text(.09,.885,title,size=23,weight="bold",color="#173941")
    fig.text(.09,.045,f"Julián Pulido   ·   NeuroEcosistema                                      Inteligencia Artificial   /   {number}",size=9)
    y=.83


def section(title,body):
    global y
    fig.text(.09,y,title,size=13,weight="bold",color="#196b62")
    lines=textwrap.wrap(body,87)
    y-=.029
    fig.text(.09,y,"\n".join(lines),va="top",size=10.5,linespacing=1.45)
    y-=.019*len(lines)+.045


def finish():
    pdf.savefig(fig)
    plt.close(fig)


page("NeuroEcosistema",1)
section("Depredadores y presas  /  Julián Pulido","Universidad Santo Tomás, Seccional Tunja. Ingeniería de Sistemas. Docente Diego Alejandro Vela Beltrán. Noviembre de 2026.")
section("Pregunta y objetivo","¿En qué condiciones una política neuronal mejora la búsqueda, la evasión o la persecución frente a reglas explícitas? Se implementaron dos poblaciones y se contrastó su desempeño en episodios repetibles. La unidad experimental es un episodio completo.")
section("Entorno y balance energético","Tablero continuo de 40 × 40 con bordes conectados. Cada episodio inicia con 12 presas. Cada paso cuesta una unidad de energía y cada agente empieza con 45. La presa avanza 1 y el depredador 1,25. Ambos deciden sobre el mismo estado previo. Primero se mueve el conjunto, después come la presa a distancia ≤ 1,1 y finalmente captura el depredador a distancia ≤ 1,4. Una planta consumida reaparece en una posición aleatoria. Comer aporta 15 unidades y capturar aporta 24, con máximo de 80. El episodio termina al desaparecer las presas o al completar 100 pasos.")
section("De la percepción al movimiento","Cada presa recibe cinco números: dos desplazamientos hacia la planta más cercana, dos hacia el depredador vivo más cercano y energía dividida por 80. Los desplazamientos siguen el camino corto entre bordes y se dividen por 20. Sin amenaza se usa (1,1). El depredador recibe el vector a la presa más cercana, dos ceros y su energía. Cada especie tiene pesos propios. La acción es el índice del mayor de cuatro puntajes: derecha, abajo, izquierda y arriba.")
finish()
page("Diseño experimental",2)
section("Aprendizaje supervisado","La presa experta huye si la amenaza está a menos de seis unidades; en otro caso busca alimento. El depredador persigue a su presa. La regla elige el eje de mayor desplazamiento. Cada especie usa 4.096 estados sintéticos de entrenamiento y 1.024 distintos de validación. Se incluyen amenazas próximas en un tercio de los ejemplos. Los estados se etiquetan con la regla. La propagación hacia atrás minimiza entropía cruzada con descenso de gradiente, lotes de 128, tasa 0,07 y 60 épocas. Las dos capas ocultas usan ReLU y la salida tiene cuatro puntajes lineales.")
section("Controles y semillas","Se cruzan tres escenarios con cuatro políticas y diez semillas de entorno (101–110). Abundancia usa 24 plantas y 2 depredadores. Escasez cambia solamente las plantas a 5. Presión cambia solamente los depredadores a 5. Cada política recibe el mismo estado inicial que las otras para igual escenario y semilla. Tras consumir plantas las trayectorias divergen. Los datos usan semillas 410/411 y los pesos 70/71, en orden presa/depredador. Se reutilizan los ejemplos entre arquitecturas.")
section("Tres contrastes previstos","1. Entrenar la red 24–24 debería elevar el alimento y las capturas frente a sus mismos pesos iniciales. 2. Ampliar únicamente la primera capa a 48 debería mejorar la imitación y la búsqueda de alimento. 3. La política neuronal debería acercarse al desempeño de la regla docente. Se aplicó la misma política experimental a ambas especies; las diferencias miden el efecto conjunto.")
section("Cómo leer las medidas","Vida es el promedio de pasos activos de las 12 presas iniciales, limitado a 100. Alimento y capturas son totales por episodio. La energía se promedia por población inicial incluyendo los muertos con cero. Primera captura solo se promedia entre episodios con captura. Se informa dispersión entre mundos mediante desviación estándar muestral.")
finish()
page("Resultados por escenario",3)
data=[]
for scene in SCENARIOS:
    for mode in MODES:
        v=values(scene,mode,"vida")
        fields=[values(scene,mode,k) for k in ["alimento","capturas","energia_presa","energia_dep","primera_captura"]]
        data.append([scene,mode,f"{v.mean():.1f} ± {v.std(ddof=1):.1f}",*[f"{a.mean():.1f}" if len(a) else "—" for a in fields],str(len(fields[-1]))])
ax=fig.add_axes([.06,.51,.88,.31]); ax.axis("off")
table=ax.table(cellText=data,colLabels=["Entorno","Control","Vida ± DE","Alim.","Capt.","E presa","E dep.","1ª capt.","n capt."],loc="center",cellLoc="center",colWidths=[.14,.14,.16,.08,.08,.1,.1,.11,.09])
table.auto_set_font_size(False); table.set_fontsize(8); table.scale(1,1.45)
fig.text(.09,.46,"Cada fila resume 10 episodios. La última columna cuenta episodios con captura.",fontsize=9)
ax=fig.add_axes([.14,.14,.76,.24])
for i,mode in enumerate(MODES):
    arrays=[values(scene,mode,"alimento") for scene in SCENARIOS]
    ax.bar(np.arange(3)+(i-1.5)*.18,[a.mean() for a in arrays],width=.18,yerr=[a.std(ddof=1) for a in arrays],capsize=2,label=mode)
ax.set_xticks(range(3),SCENARIOS.keys()); ax.set_ylabel("Alimento por episodio"); ax.legend(ncol=2,fontsize=8); ax.set_title("Consumo medio y variabilidad entre semillas")
finish()
page("Interpretación y fallos",4)
section("Antes y después","En abundancia, entrenar la red 24 elevó el alimento de 28,2 a 47,2 y las capturas de 0,8 a 7,4. El mismo sentido se observa en escasez y presión. Sin embargo, con presión la vida bajó de 66,2 a 39,9 pasos. La persecución eficaz es una explicación plausible: las presas iniciales convivían con depredadores también inexpertos. Supervivencia aislada daría una lectura engañosa.")
section("Dos arquitecturas","La red 48 consiguió más alimento en los tres escenarios. En escasez pasó de 12,6 a 17,5 plantas y de 46,9 a 51,8 pasos de vida frente a la red 24. La validación de la presa mejoró de 82,2 % a 86,6 %, mientras que la del depredador pasó de 99,4 % a 98,9 %. Ampliar la capa benefició sobre todo a la presa en esta realización.")
section("Frente a las reglas","En abundancia la regla alcanzó 95,1 plantas frente a 66,5 de la mejor red en consumo. En presión la red 24 igualó las 11,1 capturas medias de la regla, aunque comió 24,2 plantas frente a 40,8. La aproximación al experto varía según la especie, el entorno y la métrica.")
section("Limitaciones y siguiente experimento","Los ejemplos sintéticos difieren de las visitas reales del agente y la regla cambia bruscamente al cruzar seis unidades. La menor exactitud de la presa justifica registrar errores cerca del umbral y añadir ejemplos de trayectorias reales. Después conviene fijar el depredador por reglas y variar solo la presa, e invertir el cruce. Una sola inicialización por especie y arquitectura limita la generalización; repetir el entrenamiento con nuevas semillas mediría esa incertidumbre.")
finish()
page("Bitácora de decisiones",5)
for title,body in [
("01   Bordes conectados","Alternativa: muros. Se eligió continuidad para que el agente solo necesite desplazamientos relativos. La distancia entre x=39 y x=1 es dos unidades. Se sacrifica la posibilidad de estudiar acorralamiento."),
("02   Objetivo más cercano","Alternativa: mapa completo. Cinco entradas mantienen tamaño constante en los tres escenarios. Se excluyeron coordenadas absolutas, memoria y agentes secundarios para comparar políticas con la misma percepción."),
("03   Dos capas y cuatro acciones","Alternativa: movimiento angular continuo. Cuatro acciones permiten contrastar exactamente la salida con una etiqueta. Dos capas satisfacen el alcance y permiten aproximar el cambio entre búsqueda y huida. Con 24–24 hay 844 parámetros; con 48–24 hay 1.564."),
("04   Imitación por especie","Alternativa: neuroevolución. Las etiquetas permiten medir aciertos en estados reservados y aislar el ajuste numérico. La norma del cambio de pesos de la red 24 fue 7,97 en presa y 6,83 en depredador. El criterio recompensa imitar al docente incluso si otra acción permitiría sobrevivir más."),
("05   Mundos emparejados","Alternativa: semillas diferentes por política. Repetir diez estados iniciales reduce la confusión por la distribución inicial de alimento. La tabla mantiene las tres condiciones separadas para no ocultar el efecto de la escasez."),
("06   Medir ambos objetivos","Alternativa: elegir por vida media. En presión la pareja sin entrenar prolongó la vida y casi no cazó. Se conserva un conjunto de métricas para reconocer ese conflicto antes de escoger un modelo.")]:
    section(title,body)
finish()
page("Entrenamiento y verificación",6)
ax=fig.add_axes([.13,.51,.76,.28])
for width in (24,48):
    for species in ("presa","depredador"):
        subset=[r for r in training if r["especie"]==species and int(r["ancho"])==width]
        ax.plot([int(r["epoca"]) for r in subset],[100*float(r["exactitud_validacion"]) for r in subset],label=f"{species} {width}–24")
ax.set_xlabel("Época"); ax.set_ylabel("Acierto en validación (%)"); ax.legend(fontsize=8)
y=.42
section("Trazabilidad","entrenamiento.csv registra exactitud y distancia de los pesos al inicio por época. episodios.csv conserva las diez semillas por condición y los valores sin redondear. La aplicación utiliza el mismo motor de evaluación y carga los pesos incluidos. El inspector muestra la entrada, los cuatro puntajes y la dirección elegida en el último paso.")
section("Declaración de uso de IA","Se utilizó ChatGPT con Codex para desarrollar el código, ejecutar los experimentos y redactar el análisis. Se adoptaron la evaluación con semillas compartidas y la conservación de pesos iniciales reproducibles. Se descartó declarar un ganador por la sola supervivencia. La validación incluyó ejecutar las 120 simulaciones y medir en datos reservados el cambio de exactitud durante el entrenamiento.")
finish()
pdf.close()
