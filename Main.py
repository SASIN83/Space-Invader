import os
import random
import time

import pygame

pygame.font.init()

WIDTH,HEIGHT=800,765    
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invader")
#1
# Loan Assets
#Load Enemy
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

#Load Main Player
IRONMAN = pygame.image.load(os.path.join("assets", "Ironman.png"))

#Load Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

#Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

#6

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self,obj)

#3
class Ship:
    COOLDOWN = 30
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        #10
        for laser in self.lasers:
            laser.draw(window)
        
    #11
    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
    #9
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
    #8
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
#4
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = IRONMAN
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img) # Pixel perfect collision
        self.max_health = health

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    
    #13
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
    
    #12
    def healthbar(self,window):
        pygame.draw.rect(WIN, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(WIN, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width()*(self.health/self.max_health), 10))
    
#5
class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img,self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img) # Pixel perfect collision
    
    def move(self,vel):
        self.y += vel

    def get_height(self):
        return self.ship_img.get_height()
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-17, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

#7
def collide(obj1,obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

#2
def main():
    run = True
    FPS= 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 40)
    loss_font = pygame.font.SysFont("comicsans", 60)

    loss_count = 0

    enemies = []
    wave_length = 5
    enemy_vel = 1
    laser_vel = 4

    player_vel = 5
    player = Player(300,650)
    loss = False
    clock = pygame.time.Clock()
    def redraw_window():
        WIN.blit(BG, (0,0))
        #text
        lives_label = main_font.render(f"Lives: {lives}", 1, (0,255,0)) #(Text, antialias, color{RGB})
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        WIN.blit(lives_label, (10,10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)
        if loss:
            loss_label = loss_font.render("You Lost!!", 1, (255,0,0))
            WIN.blit(loss_label, (WIDTH/2 - loss_label.get_width()/2, HEIGHT/2 - loss_label.get_height()/2))
        pygame.display.update()


    while run:
        clock.tick(FPS)
        redraw_window()
        # Event Loop
        if lives <=0 or player.health<=0:
            loss = True
            loss_count += 1

        if loss:
            if loss_count > FPS * 3:
                run = False
            else:
                continue


        if len(enemies) == 0:
            level+=1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy) 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: #left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: #up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() +15 < HEIGHT: #down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            if collide(enemy, player):
                player.health-=10
                enemies.remove(enemy)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel,enemies)


#last
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 50)
    run=True
    WIN.blit(BG, (0,0))
    title_label = title_font.render("Press the Mouse button to begin...", 1, (255,255,255))
    WIN.blit(title_label,(WIDTH/2 - title_label.get_width()/2, HEIGHT/2 - title_label.get_height()/2))
    pygame.display.update()
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()   

    pygame.quit()

main_menu()    
