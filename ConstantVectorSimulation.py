from vpython import *

# Set up scene
scene = canvas(width=800, height=800, background=color.white)
scene.caption = "Uniform Circular Motion: |v| = ω, |a| = ω²"

# Angular frequency
omega = 1.0  # radians per second

# Create circular path
circle = curve(color=color.blue, radius=0.01)
for angle in range(100):
    circle.append(pos=vector(cos(angle * 0.0628), sin(angle * 0.0628), 0))

# Create particle
particle = sphere(pos=vector(1, 0, 0), radius=0.05, color=color.blue)

# Create vectors
pos_vector = arrow(pos=vector(0, 0, 0), axis=particle.pos, color=color.blue)
vel_vector = arrow(pos=particle.pos, axis=vector(0, omega, 0), color=color.red)
acc_vector = arrow(pos=particle.pos, axis=vector(-omega ** 2, 0, 0), color=color.green)

# Animation loop
t = 0
dt = 0.01

while True:
    rate(100)
    t += dt

    # Position: r = cos(ωt)i + sin(ωt)j
    x = cos(omega * t)
    y = sin(omega * t)

    # Velocity: v = -ω·sin(ωt)i + ω·cos(ωt)j
    vx = -omega * sin(omega * t)
    vy = omega * cos(omega * t)

    # Acceleration: a = -ω²·cos(ωt)i - ω²·sin(ωt)j
    ax_val = -omega ** 2 * x
    ay_val = -omega ** 2 * y

    # Update positions and vectors
    particle.pos = vector(x, y, 0)
    pos_vector.axis = particle.pos
    vel_vector.pos = particle.pos
    vel_vector.axis = vector(vx, vy, 0) * 0.3
    acc_vector.pos = particle.pos
    acc_vector.axis = vector(ax_val, ay_val, 0) * 0.15
