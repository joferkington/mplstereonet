import matplotlib.pyplot as plt
import mplstereonet

# Datos del talud y los planos de discontinuidad
talud_rumbo, talud_buzamiento = 210, 80
planes = [
    {"rumbo": 214, "buzamiento": 60, "nombre": "P1"},
    {"rumbo": 240, "buzamiento": 70, "nombre": "P2"},
    {"rumbo": 350, "buzamiento": 66, "nombre": "P3"},
    {"rumbo": 24, "buzamiento": 85, "nombre": "P4"},
    {"rumbo": 50, "buzamiento": 76, "nombre": "P5"}
]

# Ángulo de fricción interna
angulo_friccion = 40

# Crear la figura y el diagrama estereográfico
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='stereonet'))

# Graficar el talud en rojo
ax.plane(talud_rumbo, talud_buzamiento, 'red', linewidth=1.5, label="Talud")

# Graficar cada plano de discontinuidad
for plano in planes:
    color = 'green' if 190 <= plano["rumbo"] <= 230 and 40 <= plano["buzamiento"] <= 80 else 'blue'
    ax.plane(plano["rumbo"], plano["buzamiento"], color=color, linewidth=1, label=f"{plano['nombre']}")

# Configuración de la leyenda y el estilo
ax.legend(loc='upper right')
plt.title("Diagrama Estereográfico: Talud y Planos de Discontinuidad")
plt.show()
