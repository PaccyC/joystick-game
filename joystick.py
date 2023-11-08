import pygame
import serial
import random

# Initialize Pygame
pygame.init()

# Set up the drawing window
WIDTH, HEIGHT = 900, 900
screen = pygame.display.set_mode([WIDTH, HEIGHT])

# Initialize the serial connection
ser = serial.Serial('/dev/ttyACM0', baudrate=9600)

# Load the superhero character image
superhero_image = pygame.image.load("./joystick_game/Superman.jpeg")
# Define the scaling factor to make the image smaller (e.g., 0.5 for 50% reduction)
scaling_factor = 0.5
# Resize the image
superhero_image = pygame.transform.scale(superhero_image, (int(superhero_image.get_width() * scaling_factor), int(superhero_image.get_height() * scaling_factor)))
superhero_rect = superhero_image.get_rect()

animation_frames = []
frame_count = 5  # Adjust this based on the number of animation frames you have

for i in range(frame_count):
    frame = pygame.image.load(f"./joystick_game/Superman{i+1}.jpeg")
    animation_frames.append(frame)

# Define obstacle properties
OBSTACLE_COLOR = (255, 0, 0)
OBSTACLE_WIDTH = 30
OBSTACLE_HEIGHT = 30
OBSTACLE_SPEED = 5  # Adjust the speed as needed
obstacles = []

# Game variables
score = 0
WINNING_SCORE = 100  # Define the winning score
LOSE_SCORE = 75  # Define the score threshold for losing

# Font for displaying the score
font = pygame.font.Font(None, 36)

# Load sound effects
pygame.mixer.init()
engine_sound = pygame.mixer.Sound('./joystick_game/engine.mp3')
whoosh_sound = pygame.mixer.Sound('./joystick_game/whoosh.mp3')

# Create a particle system for explosions
class Particle:
    def __init__(self, position, velocity, size, color):
        self.position = list(position)
        self.velocity = list(velocity)
        self.size = size
        self.color = color

    def update(self):
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        self.size -= 0.2

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.position[0]), int(self.position[1])), int(self.size))

particles = []

# Create game-over screen
game_over_font = pygame.font.Font(None, 100)
game_over_text = game_over_font.render("Game Over", True, (255, 0, 0))
game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# Create HUD elements
hud_font = pygame.font.Font(None, 36)

# Main game loop
running = True
clock = pygame.time.Clock()
frame_index = 0
animation_speed = 10  # Adjust the speed based on your desired animation rate
game_over = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read the data from Arduino
    data = ser.readline().decode().strip()
    print("Received:", data)  # Print raw data for debugging

    # Check if data is empty
    if not data:
        continue

    try:
        # Split the received data into x and y values
        x_value, y_value = map(int, data.split(','))

        # Clear the screen
        screen.fill((255, 255, 255))

        # Draw the animated superhero image at the specified position
        superhero_rect.center = (x_value, y_value)
        screen.blit(animation_frames[frame_index], superhero_rect)

        if not game_over:
            # Spawn obstacles
            if random.randint(0, 100) < 5:  # Adjust the probability as needed
                obstacle_x = random.randint(0, WIDTH - OBSTACLE_WIDTH)
                obstacles.append(pygame.Rect(obstacle_x, 0, OBSTACLE_WIDTH, OBSTACLE_HEIGHT))

            # Move obstacles
            for obstacle in obstacles:
                obstacle.y += OBSTACLE_SPEED
                pygame.draw.rect(screen, OBSTACLE_COLOR, obstacle)

            # Remove obstacles that are out of the screen
            obstacles = [obstacle for obstacle in obstacles if obstacle.y < HEIGHT]

            # Check for collisions with obstacles
            for obstacle in obstacles:
                if superhero_rect.colliderect(obstacle):
                    # Play sound effect
                    whoosh_sound.play()

                    # Create a particle effect
                    for _ in range(20):
                        particles.append(Particle(obstacle.center, (random.uniform(-2, 2), random.uniform(-2, 2)), 5, (255, 0, 0)))

                    obstacles.remove(obstacle)  # Remove the obstacle
                    score += 10  # Increase the score

            # Control animation speed
            clock.tick(animation_speed)

            # Increment the frame index to switch to the next frame
            frame_index = (frame_index + 1) % frame_count

            # Check for winning and losing conditions
            if score >= WINNING_SCORE:
              font = pygame.font.Font(None, 72)
              text = font.render("You Win!", True, (0, 255, 0))
              text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
              screen.blit(text, text_rect)
              pygame.display.flip()
              pygame.time.delay(2000)  # Display the winning message for 2 seconds
              running = False
            # elif score < LOSE_SCORE:
            #     game_over = True

        # Display the score on the screen
        score_text = hud_font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        # Update and draw the particle system
        for particle in particles:
            particle.update()
            if particle.size > 0:
                particle.draw(screen)
        particles = [particle for particle in particles if particle.size > 0]

        if game_over:
            screen.blit(game_over_text, game_over_rect)

        # Update the display
        pygame.display.flip()

    except ValueError as e:
        print("Error processing data:", e)

# Clean up
pygame.quit()
