import pygame
import json
import math

"""
how many pixel = actual distance in cm
70px = 360cm --> 360/70 = MAP_SIZE_COEFF
"""
MAP_SIZE_COEFF = 5.14

pygame.init()
screen = pygame.display.set_mode([720, 720])
screen.fill((255, 255, 255))
running = True


class Background(pygame.sprite.Sprite):
    def __init__(self, image, location, scale):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image)
        self.image = pygame.transform.rotozoom(self.image, 0, scale)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


def get_dist_btw_pos(pos0, pos1):
    """
    Get distance between 2 mouse position.
    """
    x = abs(pos0[0] - pos1[0])
    y = abs(pos0[1] - pos1[1])
    return int(x), int(y)


def get_angle_btw_line(pos0, pos1, posref):
    """
    Get angle between two lines respective to 'posref'
    NOTE: using dot product calculation.
    """
    ax = posref[0] - pos0[0]
    ay = posref[1] - pos0[1]
    bx = posref[0] - pos1[0]
    by = posref[1] - pos1[1]
    # Get dot product of pos0 and pos1.
    _dot = (ax * bx) + (ay * by)
    # Get magnitude of pos0 and pos1.
    _magA = math.sqrt(ax**2 + ay**2)
    _magB = math.sqrt(bx**2 + by**2)
    _rad = math.acos(_dot / (_magA * _magB))
    # Angle in degrees.
    angle = (_rad * 180) / math.pi
    return int(angle)


"""
Main capturing mouse program.
"""
# Load background image.
bground = Background('path_planning/Picture1.png', [0, 0], 1.6)
screen.blit(bground.image, bground.rect)

path_wp = []
index = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            path_wp.append(pos)
            if index > 0:
                pygame.draw.line(screen, (255, 0, 0), path_wp[index-1], pos, 2)
            index += 1
    pygame.display.update()

"""
Compute the waypoints (distance and angle).
"""
# Append first pos ref. (dummy)
path_wp.insert(0, (path_wp[0][0], path_wp[0][1] - 10))

path_dist_x = []
path_dist_y = []
path_angle = []
for index in range(len(path_wp)):
    # Skip the first and second index.
    if index > 1:
        dist_x, dist_y = get_dist_btw_pos(path_wp[index-1], path_wp[index])
        path_dist_x.append(dist_x)
        path_dist_y.append(dist_y)

    # Skip the first and last index.
    if index > 0 and index < (len(path_wp) - 1):
        angle = get_angle_btw_line(path_wp[index-1], path_wp[index+1], path_wp[index])
        path_angle.append(angle)

# Print out the information.
print('path_wp: {}'.format(path_wp))
print('dist_cm: {}'.format(path_dist_x))
print('dist_px: {}'.format(path_dist_y))
print('dist_angle: {}'.format(path_angle))

"""
Save waypoints into JSON file.
"""
waypoints = []
for index in range(len(path_dist_x)):
    waypoints.append({
        "dist_x": path_dist_x[index],
        "dist_y": path_dist_y[index],
        "angle_deg": path_angle[index]
    })

# Save to JSON file.
f = open('waypoint.json', 'w+')
path_wp.pop(0)
json.dump({
    "wp": waypoints,
    "pos": path_wp
}, f, indent=4)
f.close()