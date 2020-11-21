import pygame as pg
import time
import os
import random

from pygame.constants import K_SPACE

pg.font.init()
#Loading background
width,height=750,750
Window = pg.display.set_mode((width,height))
pg.display.set_caption("Space Invader")

#Loading Ships
R_Ship = pg.image.load(os.path.join("assets","pixel_ship_red_small.png"))
G_Ship = pg.image.load(os.path.join("assets","pixel_ship_green_small.png"))
B_Ship = pg.image.load(os.path.join("assets","pixel_ship_blue_small.png"))

#Main player
M_Ship = pg.image.load(os.path.join("assets","pixel_ship_yellow.png"))

R_Laser = pg.image.load(os.path.join("assets","pixel_laser_red.png"))
G_Laser = pg.image.load(os.path.join("assets","pixel_laser_green.png"))
B_Laser = pg.image.load(os.path.join("assets","pixel_laser_blue.png"))

#Laser on main player
M_Laser = pg.image.load(os.path.join("assets","pixel_laser_yellow.png"))

#Loading Background
BG = pg.transform.scale(pg.image.load(os.path.join("assets","background-black.png")),(width,height))


#Laser class

class Laser:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pg.mask.from_surface(self.img)

    def draw(self,window):
        window.blit(self.img, (self.x,self.y))

    def move(self,vel):
        self.y += vel

    def off_screen(self,height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj) 
#Ships class
class Ship:
    CD = 30
    def __init__(self,x,y,health=100):
        self.x = x
        self.y= y
        self.health=health
        self.ship_img = None
        self.laser_img = None
        self.CD_counter = 0
        self.lasers = [] 

    def draw(self,window):
        window.blit(self.ship_img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_L(self,vel,obj):
        self.cd()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)


    def cd(self):
        if self.CD_counter >= self.CD:
            self.CD_counter = 0

        elif self.CD_counter > 0:
            self.CD_counter +=1

    def shoot(self):
        if self.CD_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.CD_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self,x,y,health=100):
        super().__init__(x,y,health)
        self.ship_img = M_Ship
        self.laser_img = M_Laser
        self.mask = pg.mask.from_surface(self.ship_img)
        self.max_health = health
        self.CD_counter = 0
    def move_L(self,vel,objs):
        self.cd()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        #obj.health -=10
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    
    def healthBar(self,window):
        pg.draw.rect(window,(255,0,0),(self.x,self.y + self.ship_img.get_height()+10,self.ship_img.get_width(),10))
        pg.draw.rect(window,(0,255,0),(self.x,self.y + self.ship_img.get_height()+10,self.ship_img.get_width()*(self.health/self.max_health),10))

    def draw(self,window):
        super().draw(window)
        self.healthBar(window)

class Enemy(Ship):
    Color_Map = {
        "red":(R_Ship,R_Laser),
        "green":(G_Ship,G_Laser),
        "blue":(B_Ship,B_Laser)
    }
    def __init__(self,x,y,color,health=100):
        super().__init__(x,y,health)
        self.ship_img, self.laser_img = self.Color_Map[color]
        self.mask = pg.mask.from_surface(self.ship_img)

    def move(self,vel):
        self.y+=vel+1

    def shoot(self):
        if self.CD_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.CD_counter = 1     

def collide(obj1, obj2):
    off_x = obj2.x - obj1.x
    off_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (off_x, off_y)) != None

#Main function
def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    font = pg.font.SysFont("Comicsans",50)
    velocity = 5
    E_vel = 2
    laser_vel = 4
    Lost_font = pg.font.SysFont("Comicsans",60)
    lost = False
    lost_count=0
    #Initialize Enemies
    enemies = []
    wave_length = 5
    

    #Initialize Main player
    player = Player(350,651)

    clock = pg.time.Clock()

    def replay():
        Window.blit(BG,(0,0))
        #Texts
        lives_text = font.render(f'Lives:{lives}',1,(0,255,0))
        level_text = font.render(f'Levels:{level}',1,(0,0,255))

        Window.blit(lives_text,(10,10))
        Window.blit(level_text,(width-level_text.get_width()-10,10))

        for enemy in enemies:
            enemy.draw(Window)

        player.draw(Window)
        if lost:
            lost_text = Lost_font.render("Game Over",1,(255,0,0))
            Window.blit(lost_text,(width/2-lost_text.get_width()/2, 350))
        pg.display.update()
        
        

    while run:
        clock.tick(FPS)
        
        if lives<=0 or player.health<=0:
            lost=True
            lost_count+=1

        if lost:
            if lost_count>FPS*2:
                if pg.event.get()== pg.QUIT:
                    quit()

                else:
                    run = False

            else:
                continue


        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50,width-100),random.randrange(-1500,-100),random.choice(["red","green","blue"]))
                enemies.append(enemy)
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run= False
            
            #if event.type == pg.QUIT:

            #if event.type == pg.QUIT:

        keys=pg.key.get_pressed()
        if (keys[pg.K_a] or keys[pg.K_LEFT]) and player.x - velocity > 0:
            player.x-=velocity

        if (keys[pg.K_d] or keys[pg.K_RIGHT]) and player.x + velocity + player.get_width() < width:
            player.x+=velocity
        
        if (keys[pg.K_w] or keys[pg.K_UP]) and player.y - velocity > 0:
            player.y-=velocity
        
        if (keys[pg.K_s] or keys[pg.K_DOWN]) and player.y + velocity + player.get_height() + 15 < height:
            player.y+=velocity

        if (keys[pg.K_SPACE] or keys[pg.MOUSEBUTTONDOWN]):
            player.shoot()
        
        for enemy in enemies[:]:
            enemy.move(E_vel)
            enemy.move_L(laser_vel,player)
            if random.randrange(0,240) ==1:
                enemy.shoot()

            if collide(enemy,player):
                player.health-=10
                enemies.remove(enemy)
            
            elif enemy.y + enemy.get_height()>height:
                lives -= 1
                enemies.remove(enemy)
            
            

        player.move_L(-laser_vel,enemies)
                
        replay()
def menu():
    run = True
    title_font = pg.font.SysFont("Comicsans",60)
    while run:
        Window.blit(BG,(0,0))
        Title_text = title_font.render("Click the mouse button to invade...",1,(255,255,255))
        Window.blit(Title_text,(width/2-Title_text.get_width()/2, 350))
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False

            if event.type == pg.MOUSEBUTTONDOWN:
                main()

    pg.quit()
menu()
