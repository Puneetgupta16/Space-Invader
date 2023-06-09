import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invader")

#load images
RED_SPACESHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACESHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACESHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# main player ship
YELLOW_SPACESHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

#lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

#Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets","background-black.png")), (WIDTH, HEIGHT))

class Laser:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.mask = pygame.mask.from_surface(self.image)
        
    def draw(self, window):
        window.blit(self.image, (self.x, self.y))
        
    def move(self, vel):
        self.y += vel
        
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)
    
    def collision(self, obj):
        return collide(obj, self)

class Ship:
    COOLDOWN = 30
    
    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_image = None
        self.laser_image = None
        self.laser = []
        self.cooldown_counter = 0
    
    def cooldown(self):
        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter += 1 
            
    
    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x, self.y, self.laser_image)
            self.laser.append(laser)
            self.cooldown_counter = 1
    
    def draw(self, window):
        window.blit(self.ship_image,(self.x,self.y))
        for laser in self.laser:
            laser.draw(window)
            
    def move_laser(self, vel, obj):
        self.cooldown()
        for laser in self.laser:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.laser.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.laser.remove(laser)
            
    
    def get_width(self):
        return self.ship_image.get_width()
    
    def get_height(self):
        return self.ship_image.get_height()

class Player(Ship):
    def __init__(self, x, y, health = 100):
        super().__init__(x, y, health)
        self.ship_image = YELLOW_SPACESHIP
        self.laser_image = YELLOW_LASER 
        self.mask = pygame.mask.from_surface(self.ship_image)
        self.max_health = health
        
    def move_laser(self, vel, objs):
        self.cooldown()
        for laser in self.laser:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.laser.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.laser.remove(laser)
    
    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_image.get_height() + 10, self.ship_image.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_image.get_height() + 10, self.ship_image.get_width() * (self.health/self.max_health), 10))

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)

class Enemy(Ship):
    COLOR_MAP = {
                "red" : (RED_SPACESHIP, RED_LASER),
                "blue" : (BLUE_SPACESHIP, BLUE_LASER),
                "green": (GREEN_SPACESHIP, GREEN_LASER) 
                }

    def __init__(self, x, y, color, health = 100):
        super().__init__(x, y, health)
        self.ship_image, self.laser_image = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_image)
    
    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_image)
            self.laser.append(laser)
            self.cooldown_counter = 1
    
    def move(self, vel):
        self.y += vel

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    lost = False
    lost_count = 0
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 40)# the last argumrnt is for the size of the text.
    lost_font = pygame.font.SysFont("comicsans", 60)
    
    enemies = []
    wave_length = 5
    enemy_vel = 1
    
    player_vel = 5
    laser_vel = 4
    
    player = Player(300, 630)
    
    clock = pygame.time.Clock()     # helps to stablize the game so that it can run at 60FPS at any device
    
    def redraw_window():
        WIN.blit(BG, (0,0))
        # Draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))  # the last argument is the color of the text in rgb
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        
        for enemy in enemies:
            enemy.draw(WIN)
        
        player.draw(WIN)   
        
        if lost:
            lost_label = lost_font.render("You lost!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))  
        
        pygame.display.update()
    
    while run:     
        clock.tick(FPS)
        redraw_window()
        
        if lives <= 0 or player.health <=0:
            lost = True
            lost_count += 1
            
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(30, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)
                
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
           player.x += player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
            
        if keys[pygame.K_SPACE]:
            player.shoot()
        
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_laser(laser_vel, player)
            
            if random.randrange(0, 2*FPS) == 1:
                enemy.shoot()
            
            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1 
                enemies.remove(enemy)
            
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            
        player.move_laser(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame. MOUSEBUTTONDOWN:
                main()
                
    pygame.quit()              

main_menu()