import tkinter as tk
from tkinter import ttk, messagebox
from ecosistema import World, MODES, SCENARIOS, load_models


class Demo:
    def __init__(self, root):
        self.root = root
        root.title("NeuroEcosistema · Julián Pulido")
        bar = ttk.Frame(root, padding=10)
        bar.pack(fill="x")
        self.scenario = tk.StringVar(value="Abundancia")
        self.mode = tk.StringVar(value="Red 24")
        self.seed = tk.StringVar(value="101")
        for label, var, options in [("Escenario",self.scenario,SCENARIOS),("Control",self.mode,MODES)]:
            ttk.Label(bar,text=label).pack(side="left")
            ttk.Combobox(bar,textvariable=var,values=list(options),width=12,state="readonly").pack(side="left",padx=4)
        ttk.Label(bar,text="Semilla").pack(side="left")
        ttk.Entry(bar,textvariable=self.seed,width=7).pack(side="left")
        ttk.Button(bar,text="Reiniciar",command=self.reset).pack(side="left",padx=4)
        self.play = ttk.Button(bar,text="Iniciar",command=self.toggle)
        self.play.pack(side="left")
        ttk.Button(bar,text="Un paso",command=self.step).pack(side="left")
        self.canvas = tk.Canvas(root,width=440,height=440,bg="#102e34",highlightthickness=0)
        self.canvas.pack(pady=8)
        ttk.Label(root,text="● Alimento (verde)     ● Presa (azul)     ▲ Depredador (naranja)").pack()
        self.stats = ttk.Label(root, padding=8,justify="left")
        self.stats.pack()
        self.job = None
        self.reset()

    def reset(self):
        try:
            seed = int(self.seed.get())
            self.world = World(self.scenario.get(),seed,load_models(self.mode.get()))
        except ValueError:
            messagebox.showerror("Semilla","Escribe un entero mayor o igual a cero.")
            return
        self.stop()
        self.draw()

    def stop(self):
        if self.job is not None:
            self.root.after_cancel(self.job)
        self.job = None
        self.play.config(text="Iniciar")

    def toggle(self):
        if self.job is not None:
            self.stop()
        elif not self.world.done:
            self.play.config(text="Pausar")
            self.tick()

    def tick(self):
        self.job = None
        self.step()
        if not self.world.done:
            self.job = self.root.after(110,self.tick)
        else:
            self.stop()

    def step(self):
        self.world.step()
        self.draw()

    def draw(self):
        w = self.world
        self.canvas.delete("all")
        for k,(points,color,r) in enumerate([(w.food,"#9de39b",3),(w.pos[0][w.energy[0]>0],"#69cfff",5),(w.pos[1][w.energy[1]>0],"#ffa354",6)]):
            for x,y in points*11:
                if k == 2:
                    self.canvas.create_polygon(x,y-r,x-r,y+r,x+r,y+r,fill=color)
                else:
                    self.canvas.create_oval(x-r,y-r,x+r,y+r,fill=color,outline="")
        lines = [f"Paso {w.time}/100   ·   Presas vivas {(w.energy[0]>0).sum()}/12   ·   Alimento {w.meals}   ·   Capturas {w.kills}"]
        for s,(i,x,scores,a) in w.trace.items():
            out = "regla" if scores is None else str(scores)
            lines.append(f"{s.capitalize()} {i}   Entrada {x}   Salida {out}   → {['derecha','abajo','izquierda','arriba'][a]}")
        if w.done:
            lines.append("Episodio finalizado")
        self.stats.config(text="\n".join(lines))


if __name__ == "__main__":
    window = tk.Tk()
    Demo(window)
    window.mainloop()
