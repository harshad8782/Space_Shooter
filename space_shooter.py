import pygame
from os.path import join
from random import randint , uniform


class Player(pygame.sprite.Sprite):
    
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join("images", "player.png")).convert_alpha()
        self.rect = self.image.get_frect(center=(display_width/2,display_height/2)) 
        self.direction = pygame.math.Vector2()
        self.speed = 300

        # cooldown for firing
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400
        

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks() 
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser((all_sprites,laser_sprite),laser_image, self.rect.midtop)
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        self.laser_timer()

class Stars(pygame.sprite.Sprite):
    def __init__(self,groups,surface):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(center=(randint(0,display_width),randint(0,display_height)))
                                         
class Laser(pygame.sprite.Sprite):
    def __init__(self,groups,surface,position):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(midbottom=position)
    
    def update(self,dt):
        self.rect.centery -= 400 * dt

        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self,groups,surface,position):
        super().__init__(groups)
        self.original_image = surface
        self.image = surface
        self.rect = self.image.get_frect(center = position)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 2000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5),1).normalize()
        self.speed = randint(400,500)
        self.rotation_speed = randint(40,80)
        self.rotation = 0

    def update(self,dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_image,self.rotation,1)
        self.rect = self.image.get_frect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, groups, frames,position):
        super().__init__(groups)
        self.frames = frames
        self.frames_index = 0
        self.image = self.frames[self.frames_index]
        self.rect = self.image.get_frect(center=position)
    
    def update(self, dt):
        self.frames_index += 30*dt
        if self.frames_index < len(self.frames):
            self.image = self.frames[int(self.frames_index)]
        else:
            self.kill()
        

def collision():
    global running

    collision_occ = pygame.sprite.spritecollide(player,meteor_sprites,True,pygame.sprite.collide_mask)
    if collision_occ:
        damage_sound.play(loop = 1)
        running = False
    # test collision 
    for laser in laser_sprite:
        collided_sprites = pygame.sprite.spritecollide(laser,meteor_sprites,True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(all_sprites, explosion_frames, laser.rect.center)
            explosion_sound.play()

def display_score():
    current_time = pygame.time.get_ticks() // 100
    text_surface = font.render(str(current_time),True,("white"))
    text_rect = text_surface.get_frect(midbottom=(display_width/2, display_height - 50) )
    display_surfate.blit(text_surface, text_rect)
    pygame.draw.rect(display_surfate,("white"),text_rect.inflate(20,10).move(0,-7),5,10)


pygame.init()
display_width = 1000
display_height = 700
pygame.display.set_caption("Space Shooter")
display_surfate = pygame.display.set_mode((display_width, display_height))

running = True
clock = pygame.time.Clock()


star_surface = pygame.image.load(join("images","star.png")).convert_alpha()
laser_image = pygame.image.load(join("images", "laser.png")).convert_alpha()
meteor_image = pygame.image.load(join("images", "meteor.png")).convert_alpha()
font = pygame.font.Font(join('images','Oxanium-Bold.ttf'),40)
explosion_frames = [pygame.image.load(join("images","explosion",f'{i}.png')).convert_alpha() for i in range(21)]

laser_sound = pygame.mixer.Sound(join('audio','laser.wav'))
laser_sound.set_volume(0.5)

explosion_sound = pygame.mixer.Sound(join('audio','explosion.wav'))
explosion_sound.set_volume(0.5)

damage_sound = pygame.mixer.Sound(join('audio','damage.ogg'))


all_sprites =  pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprite = pygame.sprite.Group() 
for i in range(20):
    star = Stars(all_sprites,star_surface)
player = Player(all_sprites)


# PLAYER SETUP 
# player_image = pygame.image.load(join("images", "player.png")).convert_alpha()
# player_rect = player_image.get_frect(center=(display_width/2,display_height/2))
# player_direction = pygame.math.Vector2()
# player_speed = 300


# custom events
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

test_rect = pygame.FRect(0,0,300,600)

while running:
    # event handling
    dt = clock.tick() /1000  # Set the frame rate to 60 FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x,y = randint(0,display_width), randint(-100,-10)
            Meteor((all_sprites,meteor_sprites),meteor_image,(x,y))

    display_surfate.fill("#414a4c")  # Fill the screen with black
    all_sprites.update(dt)
    collision()
    
    display_score()
    all_sprites.draw(display_surfate)
    pygame.display.update()
pygame.quit()
