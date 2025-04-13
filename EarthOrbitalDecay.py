import pygame
import numpy as np
import sys
import math

# Initialize Pygame
pygame.init()

# Initial window size
default_width, default_height = 1000, 800

# Get display info for fullscreen
display_info = pygame.display.Info()
screen_width, screen_height = display_info.current_w, display_info.current_h

# Set up display initially in windowed mode
fullscreen = False
if fullscreen:
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    width, height = screen_width, screen_height
else:
    screen = pygame.display.set_mode((default_width, default_height), pygame.RESIZABLE)
    width, height = default_width, default_height

pygame.display.set_caption("Earth Orbital Decay Simulation")

# Colors
BLACK = (0, 0, 0)
RED = (255, 80, 80)  # Brighter red for better visibility
GREEN = (80, 255, 80)  # Brighter green for better visibility
BLUE = (100, 100, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

# Sun and Earth properties
sun_radius = 30
earth_radius = 10
initial_orbit_radius = 300

# Initial conditions
angle = 0
orbit_radius = initial_orbit_radius
decay_rate = 0.05  # Controls how quickly Earth spirals inward

# Initial velocity and angular velocity
initial_velocity = 0.5
omega = initial_velocity / initial_orbit_radius  # Initial angular velocity

# Font initialization
font = pygame.font.SysFont('Arial', 20)


def toggle_fullscreen():
    """Toggle between fullscreen and windowed modes"""
    global screen, fullscreen, width, height
    fullscreen = not fullscreen

    if fullscreen:
        width, height = screen_width, screen_height
        screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
    else:
        width, height = default_width, default_height
        screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

    # Recalculate center based on new dimensions
    update_dimensions()


def update_dimensions():
    """Update dimensions and centers when screen size changes"""
    global center_x, center_y, font
    center_x, center_y = width // 2, height // 2

    # Scale font size based on screen width
    font_size = int(20 * (width / default_width))
    font = pygame.font.SysFont('Arial', max(12, font_size))


def draw_vector(start, direction, color, scale=1.0, thickness=2):
    try:
        # Calculate end point
        end_x = start[0] + direction[0] * scale
        end_y = start[1] + direction[1] * scale

        # Check for invalid values
        if np.isnan(end_x) or np.isinf(end_x) or np.isnan(end_y) or np.isinf(end_y):
            return

        # Convert to integers
        start_pos = (int(start[0]), int(start[1]))
        end_pos = (int(end_x), int(end_y))

        # Draw the line with specified thickness
        pygame.draw.line(screen, color, start_pos, end_pos, thickness)

        # Calculate arrowhead
        vector_length = np.sqrt(direction[0] ** 2 + direction[1] ** 2)
        if vector_length * scale > 5:  # Only draw arrowhead if vector is long enough
            arrow_angle = np.arctan2(direction[1], direction[0])
            arrow_size = 12 * (width / default_width)  # Scale arrowhead with screen size

            point1_x = end_x - arrow_size * np.cos(arrow_angle - np.pi / 6)
            point1_y = end_y - arrow_size * np.sin(arrow_angle - np.pi / 6)
            point2_x = end_x - arrow_size * np.cos(arrow_angle + np.pi / 6)
            point2_y = end_y - arrow_size * np.sin(arrow_angle + np.pi / 6)

            # Draw the arrowhead
            pygame.draw.polygon(screen, color, [
                (int(end_x), int(end_y)),
                (int(point1_x), int(point1_y)),
                (int(point2_x), int(point2_y))
            ])
    except Exception as e:
        print(f"Error drawing vector: {e}")


# Initialize dimensions
update_dimensions()

# Track Earth's orbit
earth_trail = []
max_trail_length = 500

# Main loop
clock = pygame.time.Clock()
running = True
paused = False
show_vector_field = False

# Time step
dt = 0.1

# Vector magnitude history for plotting
velocity_history = []
acceleration_history = []
radius_history = []
max_history = 100

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_v:
                show_vector_field = not show_vector_field
            elif event.key == pygame.K_UP:
                decay_rate *= 1.2
            elif event.key == pygame.K_DOWN:
                decay_rate /= 1.2
            elif event.key == pygame.K_f:  # F key toggles fullscreen
                toggle_fullscreen()
                earth_trail = []  # Clear trail when changing resolution
            elif event.key == pygame.K_ESCAPE and fullscreen:
                # Exit fullscreen with Escape key
                toggle_fullscreen()
        elif event.type == pygame.VIDEORESIZE and not fullscreen:
            # Handle manual window resizing
            width, height = event.size
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            update_dimensions()
            earth_trail = []  # Clear trail when resizing

    if not paused:
        # Update angular position
        angle += omega * dt

        # Calculate current acceleration magnitude using inverse square law (closer = stronger)
        # This makes acceleration increase as Earth gets closer to Sun
        acc_magnitude = initial_velocity ** 2 * (initial_orbit_radius / orbit_radius) ** 2

        # Calculate current velocity (decreases as orbit decays)
        # This simulates orbital decay where velocity decreases as radius decreases
        vel_magnitude = initial_velocity * np.sqrt(orbit_radius / initial_orbit_radius)

        # Update omega based on new velocity and radius
        omega = vel_magnitude / orbit_radius

        # Reduce orbit radius (simulating the Earth being pulled toward the Sun)
        orbit_radius -= decay_rate * acc_magnitude * dt

        # Store history for plotting
        velocity_history.append(vel_magnitude)
        acceleration_history.append(acc_magnitude)
        radius_history.append(orbit_radius)

        if len(velocity_history) > max_history:
            velocity_history = velocity_history[-max_history:]
            acceleration_history = acceleration_history[-max_history:]
            radius_history = radius_history[-max_history:]

        # Check if Earth has hit the Sun
        if orbit_radius <= sun_radius + earth_radius:
            print("Earth has collided with the Sun! Simulation ending.")
            running = False

    # Clear the screen
    screen.fill(BLACK)

    # Scale orbit radius and vector display based on screen size
    display_scale = min(width, height) / 800
    display_orbit_radius = initial_orbit_radius * display_scale
    scaled_sun_radius = sun_radius * display_scale
    scaled_earth_radius = earth_radius * display_scale

    # Draw the vector field if enabled
    if show_vector_field:
        n_points = 72  # More points for a denser field like in the image
        for i in range(n_points):
            field_angle = 2 * np.pi * i / n_points
            # Create vector field at multiple radii
            for radius_factor in [0.5, 1.0, 1.5]:
                field_radius = display_orbit_radius * radius_factor
                field_x = center_x + field_radius * np.cos(field_angle)
                field_y = center_y + field_radius * np.sin(field_angle)
                field_pos = (field_x, field_y)

                # Position vector from center
                pos_vector = np.array([field_x - center_x, field_y - center_y])

                # Calculate field point velocity and acceleration based on radius
                field_vel = initial_velocity * np.sqrt(field_radius / display_orbit_radius)
                field_acc = initial_velocity ** 2 * (display_orbit_radius / field_radius) ** 2

                # Velocity vector (tangential)
                vel_vector = np.array([-pos_vector[1], pos_vector[0]])
                vel_vector = vel_vector / np.linalg.norm(vel_vector) * field_vel

                # Acceleration vector (toward center)
                acc_vector = -pos_vector / np.linalg.norm(pos_vector) * field_acc

                # Draw vectors - scale with display size
                field_vel_scale = 100.0 * display_scale
                field_acc_scale = 200.0 * display_scale
                draw_vector(field_pos, vel_vector, RED, field_vel_scale, 1)
                draw_vector(field_pos, acc_vector, GREEN, field_acc_scale, 1)

    # Calculate Earth position - scaled by display size
    display_orbit = orbit_radius * display_scale
    x = center_x + display_orbit * np.cos(angle)
    y = center_y + display_orbit * np.sin(angle)
    earth_pos = (x, y)

    # Add to Earth's trail
    earth_trail.append(earth_pos)
    if len(earth_trail) > max_trail_length:
        earth_trail = earth_trail[-max_trail_length:]

    # Draw Earth's trail to show spiral
    if len(earth_trail) > 1:
        pygame.draw.lines(screen, BLUE, False, earth_trail, max(1, int(2 * display_scale)))

    # Calculate position vector (from Sun to Earth)
    pos_vector = np.array([x - center_x, y - center_y])

    # Calculate velocity vector (tangential to orbit)
    # |v| decreases as orbit decreases
    vel_magnitude = initial_velocity * np.sqrt(orbit_radius / initial_orbit_radius)
    vel_vector = np.array([-pos_vector[1], pos_vector[0]])
    vel_vector = vel_vector / np.linalg.norm(vel_vector) * vel_magnitude

    # Calculate acceleration vector (pointing to Sun)
    # |a| increases as orbit decreases (inverse square)
    acc_magnitude = initial_velocity ** 2 * (initial_orbit_radius / orbit_radius) ** 2
    acc_vector = -pos_vector / np.linalg.norm(pos_vector) * acc_magnitude

    # Draw position vector - scaled with screen size
    draw_vector((center_x, center_y), pos_vector, WHITE, 1.0, max(2, int(2 * display_scale)))

    # Draw velocity vector - adaptive scaling to keep it visible
    vel_scale = 50.0 * display_scale
    draw_vector(earth_pos, vel_vector, RED, vel_scale, max(3, int(3 * display_scale)))

    # Draw acceleration vector - adaptive scaling to keep it visible
    acc_scale = 20.0 * display_scale
    draw_vector(earth_pos, acc_vector, GREEN, acc_scale, max(3, int(3 * display_scale)))

    # Draw Sun and Earth - scaled with screen size
    pygame.draw.circle(screen, YELLOW, (center_x, center_y), scaled_sun_radius)
    pygame.draw.circle(screen, BLUE, (int(x), int(y)), scaled_earth_radius)

    # Draw reference orbit (initial orbit) - scaled with screen size
    pygame.draw.circle(screen, (50, 50, 50), (center_x, center_y), display_orbit_radius, max(1, int(display_scale)))

    # Draw vector magnitude plot in bottom right corner - scaled with screen size
    plot_width, plot_height = int(200 * display_scale), int(100 * display_scale)
    plot_x, plot_y = width - plot_width - int(20 * display_scale), height - plot_height - int(20 * display_scale)

    # Draw plot background
    pygame.draw.rect(screen, (30, 30, 30), (plot_x, plot_y, plot_width, plot_height))
    pygame.draw.rect(screen, (80, 80, 80), (plot_x, plot_y, plot_width, plot_height), 1)

    # Draw plot title
    plot_title = font.render("Vector Magnitudes", True, WHITE)
    screen.blit(plot_title, (plot_x + plot_width // 2 - plot_title.get_width() // 2, plot_y - 25))

    # Draw plot if we have history
    if len(velocity_history) > 1:
        # Normalize values to plot height
        max_vel = max(velocity_history) or 1
        max_acc = max(acceleration_history) or 1

        # Draw velocity history (red)
        points = []
        for i, vel in enumerate(velocity_history):
            x_pos = plot_x + (i / len(velocity_history)) * plot_width
            y_pos = plot_y + plot_height - (vel / max_vel) * plot_height * 0.9
            points.append((x_pos, y_pos))

        if len(points) > 1:
            pygame.draw.lines(screen, RED, False, points, max(2, int(2 * display_scale)))

        # Draw acceleration history (green)
        points = []
        for i, acc in enumerate(acceleration_history):
            x_pos = plot_x + (i / len(acceleration_history)) * plot_width
            y_pos = plot_y + plot_height - (acc / max_acc) * plot_height * 0.9
            points.append((x_pos, y_pos))

        if len(points) > 1:
            pygame.draw.lines(screen, GREEN, False, points, max(2, int(2 * display_scale)))

    # Draw current radius and magnitudes with better formatting
    y_offset = int(80 * display_scale)
    line_spacing = int(30 * display_scale)

    current_radius_text = font.render(f'Current orbit radius: {orbit_radius:.1f}', True, WHITE)
    screen.blit(current_radius_text, (width // 2 - current_radius_text.get_width() // 2, y_offset))

    # Draw velocity magnitude with dynamic color based on change
    vel_color = (255, 100, 100) if vel_magnitude < initial_velocity * 0.95 else WHITE
    vel_text = font.render(f'Velocity magnitude: {vel_magnitude:.3f} (Decreasing)', True, vel_color)
    screen.blit(vel_text, (width // 2 - vel_text.get_width() // 2, y_offset + line_spacing))

    # Draw acceleration magnitude with dynamic color based on change
    acc_color = (100, 255, 100) if acc_magnitude > initial_velocity ** 2 * 1.05 else WHITE
    acc_text = font.render(f'Acceleration magnitude: {acc_magnitude:.3f} (Increasing)', True, acc_color)
    screen.blit(acc_text, (width // 2 - acc_text.get_width() // 2, y_offset + line_spacing * 2))

    # Draw title and legend
    title = font.render('Earth Orbital Decay Simulation', True, WHITE)
    screen.blit(title, (width // 2 - title.get_width() // 2, int(20 * display_scale)))

    # Legend for vectors - scaled with screen size
    legend_y = height - int(150 * display_scale)
    legend_x = int(50 * display_scale)
    legend_spacing = int(30 * display_scale)

    # Position vector
    pygame.draw.line(screen, WHITE, (legend_x, legend_y), (legend_x + int(30 * display_scale), legend_y),
                     max(2, int(2 * display_scale)))
    text = font.render('Position Vector (r)', True, WHITE)
    screen.blit(text, (legend_x + int(40 * display_scale), legend_y - int(10 * display_scale)))

    # Velocity vector
    pygame.draw.line(screen, RED, (legend_x, legend_y + legend_spacing),
                     (legend_x + int(30 * display_scale), legend_y + legend_spacing), max(3, int(3 * display_scale)))
    text = font.render(f'Velocity Vector (v), |v| = {vel_magnitude:.3f}', True, RED)
    screen.blit(text, (legend_x + int(40 * display_scale), legend_y + legend_spacing - int(10 * display_scale)))

    # Acceleration vector
    pygame.draw.line(screen, GREEN, (legend_x, legend_y + legend_spacing * 2),
                     (legend_x + int(30 * display_scale), legend_y + legend_spacing * 2),
                     max(3, int(3 * display_scale)))
    text = font.render(f'Acceleration Vector (a), |a| = {acc_magnitude:.3f}', True, GREEN)
    screen.blit(text, (legend_x + int(40 * display_scale), legend_y + legend_spacing * 2 - int(10 * display_scale)))

    # Decay rate info
    decay_text = font.render(f'Decay rate: {decay_rate:.4f} (UP/DOWN to adjust)', True, WHITE)
    screen.blit(decay_text, (width // 2 - decay_text.get_width() // 2, y_offset + line_spacing * 3))

    # Controls info - include fullscreen toggle info
    controls = font.render('SPACE: Pause, V: Toggle vector field, F: Toggle fullscreen', True, WHITE)
    screen.blit(controls, (width // 2 - controls.get_width() // 2, int(50 * display_scale)))

    # Draw fullscreen indicator
    fs_text = font.render("Fullscreen: ON" if fullscreen else "Fullscreen: OFF (Press F)", True, WHITE)
    screen.blit(fs_text, (width - fs_text.get_width() - int(20 * display_scale), int(20 * display_scale)))

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()