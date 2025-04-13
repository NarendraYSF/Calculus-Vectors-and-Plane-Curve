import pygame
import numpy as np
import sys
import datetime
import math
import os
from urllib.request import urlretrieve

# Initialize Pygame
pygame.init()
width, height = 800, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Earth Rotation Simulation with Vectors")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (100, 100, 255)
RED = (255, 80, 80)
GREEN = (80, 255, 80)
YELLOW = (255, 255, 0)

# Earth parameters
center_x, center_y = width // 2, height // 2
earth_radius = 250  # Pixels

# Earth's rotation parameters
sidereal_day = 23.9344696 * 60 * 60  # Earth's sidereal day in seconds
omega_earth = 2 * np.pi / sidereal_day  # Angular velocity in radians/second


# Load Earth texture
def load_earth_texture():
    texture_file = "earth_texture.jpg"
    if not os.path.exists(texture_file):
        print("Downloading Earth texture...")
        # NASA Blue Marble image URL (or use another source)
        url = "https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74393/world.topo.200412.3x5400x2700.jpg"
        urlretrieve(url, texture_file)

    # Load and scale the image
    earth_img = pygame.image.load(texture_file)
    earth_img = pygame.transform.scale(earth_img, (earth_radius * 2, earth_radius * 2))
    return earth_img


try:
    earth_img = load_earth_texture()
    use_texture = True
except Exception as e:
    print(f"Could not load Earth texture: {e}")
    use_texture = False

# Font for displaying information
font = pygame.font.SysFont('Arial', 20)
title_font = pygame.font.SysFont('Arial', 28, bold=True)

# Initialize simulation parameters
angle = 0  # Will be set based on current time
trail = []
max_trail_length = 100
show_vectors = True
show_trail = True
paused = False
time_scale = 1000  # Speed up factor (1000x real-time by default)


# Function to calculate Earth's current rotation angle
def get_earth_angle():
    # Get current UTC time
    now = datetime.datetime.utcnow()

    # Calculate seconds since midnight
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    seconds_since_midnight = (now - midnight).total_seconds()

    # Convert to angle (Earth rotates 360° in one sidereal day)
    angle = (seconds_since_midnight / sidereal_day) * 2 * np.pi

    # Add longitude offset (Greenwich at 0°)
    return angle


# Main loop
clock = pygame.time.Clock()
running = True

# Initial angle based on current time
angle = get_earth_angle()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                time_scale *= 1.5
            elif event.key == pygame.K_DOWN:
                time_scale /= 1.5
            elif event.key == pygame.K_v:
                show_vectors = not show_vectors
            elif event.key == pygame.K_t:
                show_trail = not show_trail
            elif event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_r:
                # Reset to real-time
                angle = get_earth_angle()
                time_scale = 1000

    if not paused:
        # Update angle based on Earth's actual rotation rate and timescale
        dt = clock.get_time() / 1000.0  # Time since last frame in seconds
        angle += omega_earth * dt * time_scale

        # Keep angle within 0-2π range
        angle %= 2 * np.pi

    # Calculate position of a point on Earth's equator
    x = center_x + earth_radius * np.cos(angle)
    y = center_y + earth_radius * np.sin(angle)

    # Calculate velocity vector (tangential)
    vx = -earth_radius * omega_earth * time_scale * np.sin(angle)
    vy = earth_radius * omega_earth * time_scale * np.cos(angle)

    # Calculate acceleration vector (radial inward)
    ax = -earth_radius * (omega_earth * time_scale) ** 2 * np.cos(angle)
    ay = -earth_radius * (omega_earth * time_scale) ** 2 * np.sin(angle)

    # Add to trail
    if show_trail:
        trail.append((int(x), int(y)))
        if len(trail) > max_trail_length:
            trail = trail[-max_trail_length:]

    # Clear screen
    screen.fill(BLACK)

    # Draw stars in background
    for _ in range(100):
        star_x = np.random.randint(0, width)
        star_y = np.random.randint(0, height)
        brightness = np.random.randint(100, 255)
        pygame.draw.circle(screen, (brightness, brightness, brightness), (star_x, star_y), 1)

    # Draw Earth
    if use_texture:
        # Create a rotated copy of the Earth image
        rotated_earth = pygame.transform.rotate(earth_img, math.degrees(-angle))
        # Get the rect of the rotated image and center it
        rect = rotated_earth.get_rect()
        rect.center = (center_x, center_y)
        screen.blit(rotated_earth, rect)
    else:
        # Fallback: draw a blue circle
        pygame.draw.circle(screen, BLUE, (center_x, center_y), earth_radius)
        # Draw a simple grid to show rotation
        for i in range(12):
            grid_angle = i * np.pi / 6 + angle
            gx = center_x + earth_radius * np.cos(grid_angle)
            gy = center_y + earth_radius * np.sin(grid_angle)
            pygame.draw.line(screen, WHITE, (center_x, center_y), (gx, gy), 1)

    # Draw reference circle
    pygame.draw.circle(screen, WHITE, (center_x, center_y), earth_radius, 1)

    # Draw trail if enabled
    if show_trail and len(trail) > 1:
        pygame.draw.lines(screen, YELLOW, False, trail, 2)

    # Draw vectors if enabled
    if show_vectors:
        # Draw position vector
        pygame.draw.line(screen, BLUE, (center_x, center_y), (x, y), 2)

        # Draw velocity vector (scaled for visibility)
        vel_scale = 0.2
        pygame.draw.line(screen, RED, (x, y),
                         (x + vx * vel_scale, y + vy * vel_scale), 3)

        # Draw acceleration vector (scaled for visibility)
        acc_scale = 0.0002
        pygame.draw.line(screen, GREEN, (x, y),
                         (x + ax * acc_scale, y + ay * acc_scale), 3)

        # Draw point on Earth's surface
        pygame.draw.circle(screen, WHITE, (int(x), int(y)), 5)

    # Calculate real-time values
    real_omega = omega_earth * time_scale
    real_velocity = earth_radius * real_omega
    real_acceleration = earth_radius * real_omega ** 2

    # Display title
    title = title_font.render("Earth Rotation Simulation", True, WHITE)
    screen.blit(title, (width // 2 - title.get_width() // 2, 20))

    # Display information
    info_text = font.render(
        f"ω = {real_omega:.8f} rad/s, |v| = {real_velocity:.2f} m/s, |a| = {real_acceleration:.2f} m/s²",
        True, WHITE)
    screen.blit(info_text, (20, height - 100))

    # Display time scale
    time_text = font.render(f"Time scale: {time_scale:.1f}x real-time", True, WHITE)
    screen.blit(time_text, (20, height - 70))

    # Calculate and display Earth time
    hours = (angle / (2 * np.pi)) * 24
    h = int(hours)
    m = int((hours - h) * 60)
    s = int(((hours - h) * 60 - m) * 60)
    time_str = f"Earth time (at Greenwich): {h:02d}:{m:02d}:{s:02d} UTC"
    time_display = font.render(time_str, True, WHITE)
    screen.blit(time_display, (20, height - 40))

    # Display controls
    controls = font.render("UP/DOWN: Change speed | V: Toggle vectors | T: Toggle trail | SPACE: Pause | R: Reset",
                           True, WHITE)
    screen.blit(controls, (20, height - 140))

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()