import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from scipy.integrate import odeint
import tkinter as tk
from tkinter import ttk 
from mpl_toolkits.mplot3d import Axes3D

class CoupledSpringSystem:
    def __init__(self, m1, m2, k1, k2, c, initial_conditions):
        self.m1 = m1
        self.m2 = m2
        self.k1 = k1
        self.k2 = k2
        self.c = c
        self.initial_conditions = initial_conditions
        self.t = np.linspace(0, 20, 1000)
        self.solution = None

    def equations(self, y, t):
        x1, x2, v1, v2 = y
        dx1dt = v1
        dx2dt = v2
        dv1dt = (-self.k1 * x1 + self.k2 * (x2 - x1) - self.c * v1) / self.m1
        dv2dt = (-self.k2 * (x2 - x1) - self.c * v2) / self.m2
        return [dx1dt, dx2dt, dv1dt, dv2dt]

    def solve_system(self):
        self.solution = odeint(self.equations, self.initial_conditions, self.t)
        return self.solution

    def animate_masses_3D(self, canvas):
        fig = canvas.figure
        ax = fig.add_subplot(111, projection='3d')
        
        # Remover escalas antes da simulação
        ax.set_xticks([])  # Remove escala do eixo X
        ax.set_yticks([])  # Remove escala do eixo Y
        ax.set_zticks([])  # Remove escala do eixo Z
        
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_zlim(-2, 2)
        ax.set_title("Simulador de Oscilação de Molas Acopladas")  # Adicionando o título à animação 3D

        line1, = ax.plot([], [], [], 'o-', lw=2, color='blue')
        line2, = ax.plot([], [], [], 'o-', lw=2, color='red')


        def init():
            line1.set_data([], [])
            line1.set_3d_properties([])
            line2.set_data([], [])
            line2.set_3d_properties([])
            return line1, line2,

        def update(frame):
            x1 = self.solution[frame, 0]
            x2 = self.solution[frame, 1]
            z1 = np.sin(self.t[frame])
            z2 = np.cos(self.t[frame])

            line1.set_data([0, x1], [0, x1])
            line1.set_3d_properties([0, z1])

            line2.set_data([0, x2], [0, x2])
            line2.set_3d_properties([0, z2])

            return line1, line2,

        ani = FuncAnimation(fig, update, frames=len(self.t), init_func=init, blit=True, interval=20)
        canvas.draw()
        return ani

    def animate_graphs(self, ax1, ax2):
        # Linhas para as oscilacoes das molas 1 e 2
        line1, = ax1.plot([], [], 'b-', label="Mola 1 (Oscilação)")
        line2, = ax1.plot([], [], 'r-', label="Mola 2 (Oscilação)")

        # Linhas para os erros das molas 1 e 2 (pontilhadas)
        line_error, = ax2.plot([], [], 'k--', label="Erro entre Molas")

        # Configurações do gráfico de oscilação
        ax1.set_xlim(0, self.t[-1])
        ax1.set_ylim(-2, 2)
        ax1.set_xlabel('Tempo (s)')
        ax1.set_ylabel('Deslocamento (m)')
        ax1.set_title('Gráfico de Oscilação das Molas')  # Título do gráfico de oscilação

        # Configurações do gráfico de erro
        ax2.set_xlim(0, self.t[-1])
        ax2.set_ylim(-2, 2)
        ax2.set_xlabel('Tempo (s)')
        ax2.set_ylabel('Erro (m)')
        ax2.set_title('Erro baseado nas Massas')  # Título do gráfico de erro

        def update(frame):
        # Oscilação das molas
            x1 = self.solution[frame, 0]
            x2 = self.solution[frame, 1]

            # Atualizando o gráfico de oscilação
            line1.set_data(self.t[:frame], self.solution[:frame, 0])
            line2.set_data(self.t[:frame], self.solution[:frame, 1])

            # Calculando o erro como a diferença entre as duas molas
            error = self.solution[:frame, 0] - self.solution[:frame, 1]
            line_error.set_data(self.t[:frame], error)

            return line1, line2, line_error,

        ani = FuncAnimation(ax1.figure, update, frames=len(self.t), blit=True, interval=20)
        ax1.figure.canvas.draw()
        return ani

class SimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Molas Acopladas")

        self.m1 = tk.DoubleVar(value=1.0)
        self.m2 = tk.DoubleVar(value=1.0)
        self.k1 = tk.DoubleVar(value=1.0)
        self.k2 = tk.DoubleVar(value=1.0)
        self.c = tk.DoubleVar(value=0.05)
        self.initial_conditions = [1.0, 0.0, 0.0, 0.0]

        self.animation_masses = None
        self.animation_graphs = None

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self.create_widgets()

    def create_widgets(self):
        # Alterar o fundo da interface para branco
        self.root.configure(bg='white')
         
        frame_parameters = ttk.Frame(self.root)
        frame_parameters.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")

        param_frame = ttk.Frame(frame_parameters)
        param_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Campos de entrada para massa e amortecimento com quadradinhos de cor
        self.create_labeled_entry_with_color(param_frame, "Massa 1 (kg):", self.m1, 0, "blue")  # Texto azul
        self.create_labeled_entry_with_color(param_frame, "Massa 2 (kg):", self.m2, 1, "red")   # Texto vermelho
        self.create_labeled_entry(param_frame, "Amortecimento:", self.c, 4)

        # Sliders para constantes das molas
        self.create_slider(param_frame, "Constante da Mola 1 (N/m):", self.k1, 2, 0.0, 2.0, 0.1)
        self.create_slider(param_frame, "Constante da Mola 2 (N/m):", self.k2, 3, 0.0, 2.0, 0.1)

        # Frame para os botões
        button_frame = ttk.Frame(param_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        # Botões lado a lado
        start_button = ttk.Button(button_frame, text="Iniciar Simulação", command=self.start_simulation)
        start_button.grid(row=0, column=0, padx=5)

        reset_button = ttk.Button(button_frame, text="Resetar", command=self.reset_simulation)
        reset_button.grid(row=0, column=1, padx=20)  # Espaçamento ajustado para mover o botão para a direita

        self.frame_error = ttk.Frame(self.root)
        self.frame_error.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.frame_graphs = ttk.Frame(self.root)
        self.frame_graphs.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.frame_animation = ttk.Frame(self.root)
        self.frame_animation.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.initialize_graphs()

    def create_labeled_entry(self, parent, text, variable, row):
        label = ttk.Label(parent, text=text)
        label.grid(row=row, column=0, sticky="e", pady=5)
        entry = ttk.Entry(parent, textvariable=variable)
        entry.grid(row=row, column=1, pady=5)

    def create_labeled_entry_with_color(self, parent, text, variable, row, color):
        label = ttk.Label(parent, text=text, foreground=color)  # Define a cor do texto
        label.grid(row=row, column=0, sticky="e", pady=5)
        entry = ttk.Entry(parent, textvariable=variable)
        entry.grid(row=row, column=1, pady=5)


    def create_slider(self, parent, text, variable, row, min_value, max_value, increment):
        # Rótulo simples sem detalhes extras
        label = ttk.Label(parent, text=text)
        label.grid(row=row, column=0, sticky="w")
        
        # Slider com estilo básico e funcional
        slider = tk.Scale(parent, from_=min_value, to=max_value, orient=tk.HORIZONTAL, 
                        variable=variable, resolution=increment, command=self.update_simulation)
        slider.grid(row=row, column=1, sticky="e")

    def initialize_graphs(self):
        # Configuração da animação 3D das massas
        self.fig_animation = Figure(figsize=(5, 4), dpi=100)
        self.canvas_animation = FigureCanvasTkAgg(self.fig_animation, master=self.frame_animation)
        self.canvas_animation.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Adicionar o título à animação 3D antes de iniciar a simulação
        ax = self.fig_animation.add_subplot(111, projection='3d')
        ax.set_title("Simulador de Oscilação de Molas Acopladas")  # Título fixo adicionado
        ax.set_xticks([])  # Remove escala do eixo X
        ax.set_yticks([])  # Remove escala do eixo Y
        ax.set_zticks([])  # Remove escala do eixo Z

        # Remover os limites de visualização até que a simulação comece
        ax.set_xlim(auto=True)
        ax.set_ylim(auto=True)
        ax.set_zlim(auto=True)

        # Configuração do gráfico de deslocamento
        self.fig_graphs = Figure(figsize=(5, 4), dpi=100)
        self.ax1 = self.fig_graphs.add_subplot(111)
        self.ax1.set_xlim(0, 20)
        self.ax1.set_ylim(-2, 2)
        self.ax1.set_xlabel("Tempo (s)")
        self.ax1.set_ylabel("Deslocamento (m)")
        self.ax1.set_title('Gráfico de Oscilação das Molas')  # Título fixo adicionado

        self.canvas_graphs = FigureCanvasTkAgg(self.fig_graphs, master=self.frame_graphs)
        self.canvas_graphs.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Configuração do gráfico de erro
        self.fig_error = Figure(figsize=(5, 4), dpi=100)
        self.ax2 = self.fig_error.add_subplot(111)
        self.ax2.set_xlim(0, 20)
        self.ax2.set_ylim(-2, 2)
        self.ax2.set_xlabel("Tempo (s)")
        self.ax2.set_ylabel("Erro (m)")
        self.ax2.set_title('Erro baseado nas Massas')  # Título fixo adicionado

        self.canvas_error = FigureCanvasTkAgg(self.fig_error, master=self.frame_error)
        self.canvas_error.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def start_simulation(self):
        m1 = self.m1.get()
        m2 = self.m2.get()
        k1 = self.k1.get()
        k2 = self.k2.get()
        c = self.c.get()

        system = CoupledSpringSystem(m1, m2, k1, k2, c, self.initial_conditions)
        solution = system.solve_system()

        if self.animation_masses:
            self.animation_masses.event_source.stop()
        if self.animation_graphs:
            self.animation_graphs.event_source.stop()

        self.animation_masses = system.animate_masses_3D(self.canvas_animation)
        self.animation_graphs = system.animate_graphs(self.ax1, self.ax2)

        self.fig_animation.tight_layout()
        self.canvas_animation.draw()
        self.fig_graphs.tight_layout()
        self.canvas_graphs.draw()
        self.fig_error.tight_layout()
        self.canvas_error.draw()

    def reset_simulation(self):
        # Interrompe e remove completamente as animações
        if self.animation_masses is not None:
            self.animation_masses.event_source.stop()
            self.animation_masses = None
        if self.animation_graphs is not None:
            self.animation_graphs.event_source.stop()
            self.animation_graphs = None

        # Redefine as variáveis para seus valores padrão
        self.m1.set(1.0)
        self.m2.set(1.0)
        self.k1.set(1.0)
        self.k2.set(1.0)
        self.c.set(0.05)
        self.initial_conditions = [1.0, 0.0, 0.0, 0.0]

        # Limpa os gráficos antigos para garantir que não haja sobreposição
        self.ax1.clear()
        self.ax2.clear()
        self.fig_animation.clear()

        # Reconfigura os limites e os títulos dos gráficos
        self.ax1.set_xlim(0, 20)
        self.ax1.set_ylim(-2, 2)
        self.ax1.set_xlabel("Tempo (s)")
        self.ax1.set_ylabel("Deslocamento (m)")
        self.ax1.set_title('Gráfico de Oscilação das Molas')

        self.ax2.set_xlim(0, 20)
        self.ax2.set_ylim(-2, 2)
        self.ax2.set_xlabel("Tempo (s)")
        self.ax2.set_ylabel("Erro (m)")
        self.ax2.set_title('Gráfico de Erro das Molas')

        # Redesenha as figuras
        self.canvas_graphs.draw()
        self.canvas_error.draw()

        # Reconfigura a área de animação 3D
        ax = self.fig_animation.add_subplot(111, projection='3d')
        ax.set_title("Simulador de Oscilação de Molas Acopladas")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_zlim(-2, 2)

        # Redesenha o canvas de animação
        self.canvas_animation.draw()


    def update_simulation(self, event=None):
        if hasattr(self, 'animation_masses'):
            self.start_simulation()

if __name__ == "__main__":
    root = tk.Tk()
    app = SimulatorApp(root)
    root.mainloop()
