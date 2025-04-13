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
GRAY = (100, 100, 100)

# Earth parameters
center_x, center_y = width // 2, height // 2
earth_radius = 250  # Pixels

# Earth's rotation parameters
sidereal_day = 23.9344696 * 60 * 60  # Earth's sidereal day in seconds
omega_earth = 2 * np.pi / sidereal_day  # Angular velocity in radians/second
custom_omega = omega_earth * 1000  # Start with default value (scaled)


# Load Earth texture
def load_earth_texture():
    texture_file = "earth_texture.jpg"
    if not os.path.exists(texture_file):
        print("Downloading Earth texture...")
        # NASA Blue Marble image URL
        url = "https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74092/world.200407.3x5400x2700.jpg"
        urlretrieve(url, texture_file)

    # Load the image
    original_img = pygame.image.load(texture_file)

    # Scale the image to fit our Earth radius
    scaled_img = pygame.transform.scale(original_img, (earth_radius * 2, earth_radius * 2))

    # Create a surface with alpha channel for the circular crop
    earth_img = pygame.Surface((earth_radius * 2, earth_radius * 2), pygame.SRCALPHA)

    # Create a circular mask
    for x in range(earth_radius * 2):
        for y in range(earth_radius * 2):
            # Calculate distance from center
            distance = ((x - earth_radius) ** 2 + (y - earth_radius) ** 2) ** 0.5

            # If within radius, copy the pixel, otherwise leave transparent
            if distance <= earth_radius:
                earth_img.set_at((x, y), scaled_img.get_at((x, y)))

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
input_font = pygame.font.SysFont('Courier New', 22)

# Initialize simulation parameters
angle = 0  # Will be set based on current time
trail = []
max_trail_length = 100
show_vectors = True
show_trail = True
paused = False
time_scale = 1000  # Speed up factor (1000x real-time by default)

# Text input parameters
input_active = False
input_text = str(custom_omega)
input_rect = pygame.Rect(width - 220, height - 60, 200, 30)
cursor_visible = True
cursor_timer = 0
cursor_blink_time = 500  # milliseconds


# Function to calculate Earth's current rotation angle
def get_earth_angle():
    # Get current UTC time
    now = datetime.datetime.now(datetime.timezone.utc)

    # Calculate seconds since midnight
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    seconds_since_midnight = (now - midnight).total_seconds()

    # Convert to angle (Earth rotates 360° in one sidereal day)
    angle = (seconds_since_midnight / sidereal_day) * 2 * np.pi

    # Add longitude offset (Greenwich at 0°)
    return angle

def draw_stickman(screen, x, y, color=WHITE, scale=1.0):
    """
    Draw a stickman at the specified coordinates.

    Parameters:
    - screen: Pygame surface to draw on
    - x, y: Center position of the stickman
    - color: Color of the stickman (default: WHITE)
    - scale: Size scaling factor (default: 1.0)
    """
    # Calculate offset to center the stickman on the given coordinates
    x_offset = -4 * scale
    y_offset = -17 * scale

    # Head
    head_radius = 5 * scale
    pygame.draw.circle(screen, color, (int(x + x_offset + head_radius), int(y + y_offset + head_radius)),
                       int(head_radius))

    # Body
    pygame.draw.line(screen, color,
                     (int(x + x_offset + head_radius), int(y + y_offset + head_radius * 2)),
                     (int(x + x_offset + head_radius), int(y + y_offset + head_radius * 2 + 10 * scale)),
                     max(1, int(2 * scale)))

    # Arms
    pygame.draw.line(screen, color,
                     (int(x + x_offset + head_radius), int(y + y_offset + head_radius * 2 + 3 * scale)),
                     (int(x + x_offset), int(y + y_offset + head_radius * 2 + 8 * scale)),
                     max(1, int(1.5 * scale)))
    pygame.draw.line(screen, color,
                     (int(x + x_offset + head_radius), int(y + y_offset + head_radius * 2 + 3 * scale)),
                     (int(x + x_offset + head_radius * 2), int(y + y_offset + head_radius * 2 + 8 * scale)),
                     max(1, int(1.5 * scale)))

    # Legs
    pygame.draw.line(screen, color,
                     (int(x + x_offset + head_radius), int(y + y_offset + head_radius * 2 + 10 * scale)),
                     (int(x + x_offset), int(y + y_offset + head_radius * 2 + 18 * scale)),
                     max(1, int(1.5 * scale)))
    pygame.draw.line(screen, color,
                     (int(x + x_offset + head_radius), int(y + y_offset + head_radius * 2 + 10 * scale)),
                     (int(x + x_offset + head_radius * 2), int(y + y_offset + head_radius * 2 + 18 * scale)),
                     max(1, int(1.5 * scale)))


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
            if input_active:
                if event.key == pygame.K_RETURN:
                    # Apply the new omega value
                    try:
                        custom_omega = float(input_text)
                        input_active = False
                    except ValueError:
                        input_text = str(custom_omega)  # Revert to previous value if invalid
                        input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_ESCAPE:
                    input_active = False
                    input_text = str(custom_omega)  # Revert to previous value
                else:
                    # Only allow numbers, decimal point, and minus sign
                    if event.unicode in '0123456789.-' and len(input_text) < 15:
                        input_text += event.unicode
            else:
                if event.key == pygame.K_UP:
                    time_scale *= 1.5
                    custom_omega = omega_earth * time_scale  # Update omega based on new time scale
                    input_text = str(custom_omega)  # Update the display text as well
                elif event.key == pygame.K_DOWN:
                    time_scale /= 1.5
                    custom_omega = omega_earth * time_scale  # Update omega based on new time scale
                    input_text = str(custom_omega)  # Update the display text as well
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
                    custom_omega = omega_earth * time_scale
                    input_text = str(custom_omega)
                elif event.key == pygame.K_o:
                    # Activate omega input
                    input_active = True
                    input_text = str(custom_omega)
                    cursor_visible = True
                    cursor_timer = 0

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the user clicked on the input box
            if input_rect.collidepoint(event.pos):
                input_active = True
                input_text = str(custom_omega)
                cursor_visible = True
                cursor_timer = 0
            else:
                input_active = False

    if not paused:
        # Update angle based on custom omega value
        dt = clock.get_time() / 1000.0  # Time since last frame in seconds
        angle += custom_omega * dt

        # Keep angle within 0-2π range
        angle %= 2 * np.pi

    # Update cursor blink timer
    cursor_timer += clock.get_time()
    if cursor_timer >= cursor_blink_time:
        cursor_visible = not cursor_visible
        cursor_timer = 0

    # Calculate position of a point on Earth's equator
    x = center_x + earth_radius * np.cos(angle)
    y = center_y + earth_radius * np.sin(angle)

    # Calculate velocity vector (tangential)
    vx = -earth_radius * custom_omega * np.sin(angle)
    vy = earth_radius * custom_omega * np.cos(angle)

    # Calculate acceleration vector (radial inward)
    ax = -earth_radius * custom_omega ** 2 * np.cos(angle)
    ay = -earth_radius * custom_omega ** 2 * np.sin(angle)

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
        draw_stickman(screen, x, y, WHITE, 1.5)

    # Calculate real-time values
    real_omega = custom_omega
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

    # Draw omega input box
    input_color = WHITE if input_active else GRAY
    pygame.draw.rect(screen, input_color, input_rect, 2)

    # Draw input box label
    omega_label = font.render("Custom ω (rad/s):", True, WHITE)
    screen.blit(omega_label, (width - 220 - omega_label.get_width() - 10, input_rect.y + 5))

    # Render the input text
    text_surface = input_font.render(input_text, True, WHITE)
    # Ensure text fits within input box
    text_width = min(input_rect.w - 10, text_surface.get_width())
    screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

    # Draw cursor when input is active
    if input_active and cursor_visible:
        cursor_pos = input_rect.x + 5 + text_surface.get_width()
        pygame.draw.line(screen, WHITE,
                         (cursor_pos, input_rect.y + 5),
                         (cursor_pos, input_rect.y + input_rect.h - 5), 2)

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
    controls1 = font.render("UP/DOWN: Change speed | V: Toggle vectors | T: Toggle trail | SPACE: Pause", True, WHITE)
    controls2 = font.render("R: Reset | O: Enter custom omega value", True, WHITE)
    screen.blit(controls1, (20, height - 160))
    screen.blit(controls2, (20, height - 130))

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()