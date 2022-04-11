from os import stat
import pygame, random
from pygame import image
import math
from pygame import sprite
from pygame.locals import *
from pytmx.pytmx import AnimationFrame
from Map import collide_hit_rect
from SpriteStripAnim import SpriteStripAnim, spritesheet
from Settings import *

bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
tower_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
Player_group = pygame.sprite.Group()
turret_group = pygame.sprite.Group()

font = "Asset/Font/MinimalPixelFont.ttf"

class AudioManager :
    boom_audio = None
    gun_audio = None
    coin_audio = None
    def __init__(self, boom, gun, coin):
        AudioManager.boom_audio = boom
        AudioManager.gun_audio = gun
        AudioManager.coin_audio = coin
        
def LoadAndScaleSheet(image_name, scale_x, scale_y, IsFlip = False):
    img = pygame.image.load(image_name)
    img = pygame.transform.scale(img, (int(img.get_width() * scale_x), int(img.get_height() * scale_y)))
    img = pygame.transform.flip(img, IsFlip, False)
    return img

def SpawnItem(x, y, screen):
    randNum = random.randint(0, 2)
    if randNum == 0 :
        while True :
            randNum = random.randint(0, 10)
            if randNum >= 3 :
                break
            if Player.Item[randNum] <= 1 :
                break
        if randNum == 0 :
            Item(x, y,  screen, itemType=Item.ItemType['SpeedUp'])
            Player.Item[0] += 1
        elif randNum == 1 :
            Item(x, y,   screen, itemType=Item.ItemType['DamageUp'])
            Player.Item[1] += 1
        elif randNum == 2:
            Item(x, y,  screen,  itemType=Item.ItemType['PowerUp'])
            Player.Item[2] += 1
        else:
            Item(x, y,  screen, itemType=Item.ItemType['Coin'])

class Actor(pygame.sprite.Sprite):
    actor_list = []
    actor_type = {'Player':0, 'Monster':1, 'Tower':2, 'Item':3, 'Turret':4}
    NumOfActor = 0

    def __init__(self, type):
        pygame.sprite.Sprite.__init__(self)
        # append(midbottom, self)
        self.type = type
        Actor.actor_list.append([self.rect.midbottom[0], self])
        if type == Actor.actor_type['Monster'] :
            enemy_group.add(self)

    @ staticmethod
    def reset():
        Actor.actor_list.clear()
        Actor.NumOfActor = 0
        Enemy.numberOfEnemy = 0
        bullet_group.empty()
        enemy_group.empty()
        tower_group.empty()
        item_group.empty()
        Player_group.empty()
        turret_group.empty()
        Player.LOSE_HP = False
        Player.Item = [0, 0, 0]
        Player.GetItemNum = -1
        Base.hp = 100
        HUD.ScreenShake = False
        HUD.Score = 0

    def draw(self, dt, scroll):
        pass

    def update(self, dt, scroll):
        pass

    @staticmethod
    def draw(dt, scroll):
        # Actor의 위치 update
        index = 0
        for actor in Actor.actor_list:
            actor[1].update(dt, scroll)
            actor[0] = actor[1].rect.midbottom[0]
            # 몬스터인 경우
            if actor[1].type == Actor.actor_type['Monster'] :
                # 몬스터가 타워에 닿았는가?
                for tower in tower_group :
                    if pygame.sprite.spritecollide(actor[1], tower_group, False):
                        if actor[1].explosion == None :
                            actor[1].attack()
                # 몬스터가 플레이어에 닿았는가?
                if pygame.sprite.spritecollide(actor[1], Player_group, False):
                    if actor[1].explosion == None :
                        actor[1].attack()
                # 몬스터가 사망?
                if actor[1].hp <= 0 and actor[1].CanHurt :
                    index = Actor.actor_list.index(actor)
                    if actor[1].explosion == None :
                        HUD.updateScore(actor[1].score)
                    Enemy.numberOfEnemy -= 1
                    SpawnItem(actor[1].rect.centerx, actor[1].rect.centery, actor[1].screen)
                    actor[1].destroy(index)
            # 아이템인 경우
            if actor[1].type == Actor.actor_type['Item']:
                if pygame.sprite.spritecollide(actor[1], Player_group, False):
                    Player.GetItemNum = actor[1].ItemType
                    if Player.GetItemNum == 3 :
                        AudioManager.coin_audio.play()
                    index = Actor.actor_list.index(actor)
                    actor[1].destroy(index)
        # 위치 순으로 정렬
        Actor.actor_list = sorted(Actor.actor_list, key=lambda actor : actor[0])
        # blit
        for i in range(len(Actor.actor_list)):
            Actor.actor_list[i][1].draw(dt, scroll)

    def destroy(self, index):
        del Actor.actor_list[index]
        self.kill()

class Player(Actor):
    LOSE_HP = False
    Item = [0, 0, 0]
    GetItemNum = -1
    player_x = 0
    player_y = 0
    direction = {'North':0, 'South':1, 'West':2, 'East':3}
    sprite = {'North':0,'NorthEast':1,'East':2,'SouthEast':3,'South':4,'SouthWest':5,'West':6,'NorthWest':7}
    
    def __init__(self, x, y, scale, speed, screen):
        pygame.mouse.set_visible(False)
        self.alive = True
        self.speed = speed
        self.CanFire = False
        self.screen = screen
        # Mouse Cursor Sprite 설정
        self.Cursor_sprite = [
            LoadAndScaleSheet('Asset/Cursor/6crosshair.png', 2, 2),
            LoadAndScaleSheet('Asset/Cursor/6crosshair2.png', 2, 2)
        ]

        # Sprite 설정
        self.animation_sprite = [
            SpriteStripAnim('Asset/Player/3_north.png', (0,0,48,66), 4, (255, 0, 255), True, 10, 3, 3, False),
            SpriteStripAnim('Asset/Player/3_diagup.png', (0,0,48,66), 4, (255, 0, 255), True, 10, 3, 3, False),
            SpriteStripAnim('Asset/Player/3_side.png', (0,0,48,66), 4, (255, 0, 255), True, 10, 3, 3, False),
            SpriteStripAnim('Asset/Player/3_diagdown.png', (0,0,48,66), 4, (255, 0, 255), True, 10, 3, 3, False),
            SpriteStripAnim('Asset/Player/3_south.png', (0,0,48,66), 4, (255, 0, 255), True, 10, 3, 3, False),
            SpriteStripAnim('Asset/Player/3_diagdown.png', (0,0,48,66), 4, (255, 0, 255), True, 10, 3, 3, True),
            SpriteStripAnim('Asset/Player/3_side.png', (0,0,48,66), 4, (255, 0, 255), True, 10, 3, 3, True),
            SpriteStripAnim('Asset/Player/3_diagup.png', (0,0,48,66), 4, (255, 0, 255), True, 10, 3, 3, True),
        ]
      
        self.direction = Player.sprite['South']
        self.sprite_iter = self.animation_sprite[self.direction].iter()
        self.image = self.sprite_iter.next()

        self.rect = self.image.get_rect()
        self.rect.center = (x,y)    
        Player.player_x = x
        Player.player_y = y

        self.move_dir = [0, 0, 0, 0]
        self.coin = 0
        # Cannon 설정
        self.cannon = Cannon(self.rect.x, self.rect.y, self.screen)

        # Shot 설정
        self.shot_start_x = 0
        self.shot_start_y = 0
        self.cannon_elapsed = 0
        self.cannon_period = 120
        self.bulletType = 0
        self.bulletDamage = 1
        self.bulletSpeed = 0.5
        # Heart 설정
        self.HP = PlayerHP(3, 40, 40, self.screen)

        # Actor __init__
        super().__init__(Actor.actor_type['Player'])

        Player_group.add(self)

    def SetSprite(self):
        self.sprite_iter = self.animation_sprite[self.direction].iter()
        self.image = self.sprite_iter.next()
    
    def Shoot(self, dt, scroll):
        self.cannon_elapsed += dt
        if self.cannon_elapsed >= self.cannon_period :
            self.cannon_elapsed = 0
            if self.CanFire == True :
                start_x = self.rect.centerx + self.shot_start_x
                start_y = self.rect.centery + self.shot_start_y
                bullet = PlayerBullet( start_x, start_y , start_x - scroll[0], start_y-scroll[1], pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1] , self.screen, bullet_type=self.bulletType, damage=self.bulletDamage, speed=self.bulletSpeed)
                bullet_group.add(bullet)
                AudioManager.gun_audio.play()

    def move(self, x, y, dt):
        newX = x * dt * self.speed
        newY = y * dt * self.speed      
        if self.rect.x + newX > -100 and self.rect.x + newX < 900 : 
            self.rect.x += newX
        if self.rect.y + newY > -200 and self.rect.y + newY < 800 : 
            self.rect.y += newY
        
        Player.player_x = self.rect.x
        Player.player_y = self.rect.y

    def draw(self, dt, scroll):
        # 캐논 표시
        if self.direction == Player.sprite['North'] or self.direction == Player.sprite['NorthWest'] or self.direction == Player.sprite['NorthEast']:
            self.cannon.draw(self.rect.x, self.rect.y, self.direction, scroll)
        # 플레이어 이미지 표시
        self.screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))
        # 캐논 표시
        if self.direction != Player.sprite['North'] and self.direction != Player.sprite['NorthWest'] and self.direction != Player.sprite['NorthEast']:
            self.cannon.draw(self.rect.x, self.rect.y, self.direction, scroll)

    def update_bullet(self, dt, scroll):
        # 마우스 커서 위치 조정
        coord = pygame.mouse.get_pos()
        if self.CanFire :
            self.screen.blit(self.Cursor_sprite[0], coord)
        else :
            self.screen.blit(self.Cursor_sprite[1], coord)
        # 총알 이동
        self.Shoot(dt, scroll)
        bullet_group.update(dt, scroll)
        # 목숨 감소
        if Player.LOSE_HP :
            self.HP.lose_hp()
            Player.LOSE_HP = False
    def SetDirection(self, scroll):
        cursor_x, cursor_y = pygame.mouse.get_pos()
        prev_dir = self.direction
        x = cursor_x - self.rect.x + scroll[0]
        y = cursor_y - self.rect.y + scroll[1]
        if -60 < x < 60 and y < 0 :
            self.direction = Player.sprite['North']
            self.shot_start_x = 0
            self.shot_start_y = -30
        elif-60 < x < 60 and y > 0 :
            self.direction = Player.sprite['South']
            self.shot_start_x = 0
            self.shot_start_y = 30
        elif x > 0 and -60 < y < 60 :
            self.direction = Player.sprite['East']
            self.shot_start_x = 30
            self.shot_start_y = 15
        elif x < 0 and -60 < y < 60 :
            self.direction = Player.sprite['West']
            self.shot_start_x = -30
            self.shot_start_y = 15
        elif x > 0 and y < 0 :
            self.direction = Player.sprite['NorthEast']
            self.shot_start_x = 30
            self.shot_start_y = -10
        elif x > 0 and y > 0 :
            self.direction = Player.sprite['SouthEast']
            self.shot_start_x = 30
            self.shot_start_y = 20
        elif x < 0 and y < 0 :
            self.direction = Player.sprite['NorthWest']
            self.shot_start_x = -30
            self.shot_start_y = -10
        elif x < 0 and y > 0 :
            self.direction = Player.sprite['SouthWest']
            self.shot_start_x = -30
            self.shot_start_y = 20

        if prev_dir != self.direction :
            self.SetSprite()

    def update(self, dt, scroll):
        #update sprite and player status
        dir_x = self.move_dir[Player.direction['East']] - self.move_dir[Player.direction['West']]
        dir_y = self.move_dir[Player.direction['South']] - self.move_dir[Player.direction['North']]
        if abs(dir_x) == 1 and abs(dir_y) == 1:
            dir_x = float(dir_x)/math.sqrt(2)
            dir_y = float(dir_y)/math.sqrt(2)
        self.move(dir_x, dir_y, dt)
        
        # 바라보는 방향 수정
        self.SetDirection(scroll)
        self.image = self.sprite_iter.next()

        # 아이템
        if Player.GetItemNum != -1 :
            if Player.GetItemNum == Item.ItemType['SpeedUp'] :
                self.speed += 0.05
            elif Player.GetItemNum == Item.ItemType['DamageUp'] :
                self.bulletType += 1
                self.bulletDamage += 1
            elif Player.GetItemNum == Item.ItemType['PowerUp'] :
                self.cannon_period -= 5
                self.bulletSpeed += 0.1
            else :
                HUD.Score += 10
            Player.GetItemNum = -1

class Cannon(pygame.sprite.Sprite):
    def __init__(self, x, y, screen):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.Cannon_sprite = [
            LoadAndScaleSheet('Asset/Cannon/cannon_up.png', 3, 3, False),
            LoadAndScaleSheet('Asset/Cannon/cannon_diagup.png', 3, 3, False),
            LoadAndScaleSheet('Asset/Cannon/cannon_side.png', 3, 3, False),
            LoadAndScaleSheet('Asset/Cannon/cannon_diagdown.png', 3, 3, False),
            LoadAndScaleSheet('Asset/Cannon/cannon_down.png', 3, 3, False),
            LoadAndScaleSheet('Asset/Cannon/cannon_diagdown.png', 3, 3, True),
            LoadAndScaleSheet('Asset/Cannon/cannon_side.png', 3, 3, True),
            LoadAndScaleSheet('Asset/Cannon/cannon_diagup.png', 3, 3, True),
        ]
        self.image = self.Cannon_sprite[Player.sprite['South']]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)  

    def draw(self, player_x, player_y, direction, scroll):
        if direction == Player.sprite['North'] :
            self.image = self.Cannon_sprite[Player.sprite['North']]
            self.rect.x = player_x + 6
            self.rect.y = player_y - 6
        elif direction == Player.sprite['South'] :
            self.image = self.Cannon_sprite[Player.sprite['South']]
            self.rect.x = player_x + 6
            self.rect.y = player_y + 30
        elif direction == Player.sprite['East'] :
            self.image = self.Cannon_sprite[Player.sprite['East']]
            self.rect.x = player_x + 25
            self.rect.y = player_y + 35
        elif direction == Player.sprite['West'] :
            self.image = self.Cannon_sprite[Player.sprite['West']]
            self.rect.x = player_x - 25
            self.rect.y = player_y + 35
        elif direction == Player.sprite['NorthEast'] :
            self.image = self.Cannon_sprite[Player.sprite['NorthEast']]
            self.rect.x = player_x + 10
            self.rect.y = player_y + 15
        elif direction == Player.sprite['NorthWest'] :
            self.image = self.Cannon_sprite[Player.sprite['NorthWest']]
            self.rect.x = player_x - 10
            self.rect.y = player_y + 15
        elif direction == Player.sprite['SouthEast'] :
            self.image = self.Cannon_sprite[Player.sprite['SouthEast']]
            self.rect.x = player_x + 20
            self.rect.y = player_y + 35
        elif direction == Player.sprite['SouthWest'] :
            self.image = self.Cannon_sprite[Player.sprite['SouthWest']]
            self.rect.x = player_x - 20
            self.rect.y = player_y + 35
        self.screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, User_x, User_y, tar_x, tar_y, speed, bullet_type, screen):
        self.screen = screen
        pygame.sprite.Sprite.__init__(self)

        self.Bullet_sprite = [
            LoadAndScaleSheet('Asset/Bullet/bulleta.png', 2, 2),
            LoadAndScaleSheet('Asset/Bullet/bulletb.png', 2, 2),
            LoadAndScaleSheet('Asset/Bullet/bulletc.png', 2, 2)
        ]
        self.image = self.Bullet_sprite[bullet_type]
        #set direction
        angle = math.atan2(tar_y-User_y, tar_x-User_x)
        #angle += 0.15
        self.dx = math.cos(angle)*speed
        self.dy = math.sin(angle)*speed

        if bullet_type == 1 or bullet_type == 2:
            angle = math.degrees(angle)
            self.image = pygame.transform.rotate(self.image, -1*angle)
        self.rect = self.image.get_rect()
        self.rect.center = (start_x, start_y)  

    def move(self, dt, scroll):
        self.rect.x += self.dx * dt
        self.rect.y += self.dy * dt
        self.screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

    def destroy(self):
        self.kill()

    def border_reached(self):
        if self.rect.x < -500 or self.rect.x > 1200 or self.rect.y < -500 or self.rect.y > 900 :
            self.destroy()

class PlayerBullet(Bullet):

    def __init__(self, start_x, start_y, User_x, User_y, tar_x, tar_y, screen,speed =0.5, bullet_type = 0, damage = 1):
        self.damage = damage
        super().__init__(start_x, start_y,User_x, User_y, tar_x, tar_y, speed, bullet_type, screen)

    def destroy(self):
        super().destroy()

    def update(self, dt, scroll):
        self.move(dt, scroll)
        self.border_reached()

        for enemy in enemy_group :
            if pygame.sprite.spritecollide(enemy, bullet_group, dokill=True):
                enemy.hp -= self.damage
                enemy.Ishurt = True

class EnemySpawner :
    def __init__(self):
        self.level = 0
        self.spawn_timer = 3000
        self.elapsed_time = 0
        self.SpawnOn = False
        self.SpawnPoint = [[1100, 300], [-300, 300], [400, 1100], [400, -400]]
        self.spawn_count = 0

    def update(self, dt, screen):
        if self.elapsed_time > self.spawn_timer and Enemy.numberOfEnemy < 1:
            self.level += 1
            self.spawn_timer = 0
            self.SpawnOn = True
            self.spawn_count = 0
        else :
            self.elapsed_time += dt

        if self.SpawnOn and self.elapsed_time > 2000:
            for i in range(0, 4):
                if self.spawn_count >= self.level :
                    self.SpawnOn = False
                    break
                index = i % 4
                if index <= 1 :
                    offset = random.randint(-100, 100)
                    Slime(self.SpawnPoint[index][0], self.SpawnPoint[index][1] + offset, screen, speed=0.15)
                else :
                    offset = random.randint(-100, 100)
                    Slime(self.SpawnPoint[index][0] + offset, self.SpawnPoint[index][1], screen, speed=0.15)      
                self.spawn_count += 1
            self.elapsed_time = 0

class Enemy(Actor):
    numberOfEnemy = 0
    EnemyType = {'FeildMonster':0, 'BossMonster':1}
    MoveType = {'Tower':0, 'Player':1}
    Direction = {'North':0, 'South':1, 'East':2, 'West':3}
    
    def __init__(self, x, y, image, sprite_iter ,screen, speed = 0.2, hp = 5, monster_type = 0, Move_type = 0, score = 10):
        # Sprite Settings
        self.sprite_iter = sprite_iter
        self.image = self.sprite_iter.next()
        self.rect = self.image.get_rect()
        self.rect.center = (x,y) 
        # Other Settings
        self.Enemy_type = monster_type 
        self.Move_type = Move_type
        self.score = score
        self.screen = screen
        self.hp = hp
        self.Ishurt = False
        self.CanHurt = True 
        # Move Setting
        self.velocity = [0, 0]
        self.speed = speed
        self.max_force = 0.3
        self.max_velocity = 0.5
        self.direction_hori = Enemy.Direction['East']
        self.direction_up = False
        # Actor에 추가
        Enemy.numberOfEnemy += 1
        super().__init__(Actor.actor_type['Monster'])

    @staticmethod
    def truncate(vector, m):
        magnitude = math.sqrt(math.pow(vector[0],2) + math.pow(vector[1],2))
        if magnitude > m:
            vector = [vector[0]*m/magnitude, vector[1]*m/magnitude]
        return vector

    def direction_change(self, newX, newY):
        if newX > 0 :
            self.direction_hori = Enemy.Direction['East']
        elif newX < 0 :
            self.direction_hori = Enemy.Direction['West']
        if newY > 0 :
            self.direction_up = False
        elif newY < 0 :
            self.direction_up = True

    def move(self, dt):
        #Move
        newX = 0
        newY = 0
        if self.Move_type == Enemy.MoveType['Tower']:
            distance = [Base.base_x - self.rect.x, Base.base_y - self.rect.y]
            steering = [distance[0]-self.velocity[0], distance[1] - self.velocity[1]]
            steering = Enemy.truncate(steering, self.max_force)
            self.velocity = Enemy.truncate([self.velocity[0] + steering[0], self.velocity[1] + steering[1]], self.max_velocity)
            newX = self.velocity[0] * self.speed * dt
            newY = self.velocity[1] * self.speed * dt
            self.direction_change(newX, newY)
        elif self.Move_type == Enemy.MoveType['Player'] :
            distance = [Player.player_x - self.rect.x, Player.player_y - self.rect.y]
            steering = [distance[0]-self.velocity[0], distance[1] - self.velocity[1]]
            steering = Enemy.truncate(steering, self.max_force)
            self.velocity = Enemy.truncate([self.velocity[0] + steering[0], self.velocity[1] + steering[1]], self.max_velocity)
            newX = self.velocity[0] * self.speed * dt
            newY = self.velocity[1] * self.speed * dt
            self.direction_change(newX, newY)
        self.rect.x += newX
        self.rect.y += newY

    def attack(self):
        pass

    def hurt(self):
        pass

    def update(self, dt, scroll):
        if self.Ishurt == True :
            self.Move_type = Enemy.MoveType['Player']
            self.hurt()
            self.Ishurt = False
        if self.Move_type == Enemy.MoveType['Player'] :
            dest =  math.sqrt(math.pow(Player.player_x - self.rect.x,2) + math.pow(Player.player_y - self.rect.y,2))
            if dest > 400 :
                self.Move_type = Enemy.MoveType['Tower']
        self.move(dt)

    def draw(self, dt, scroll):
        self.image = self.sprite_iter.next()
        self.screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, screen, IsGetScore = False):
        pygame.sprite.Sprite.__init__(self)
        self.explostion_sprite = SpriteStripAnim('Asset/Other/explode2.png', (0,0,84,84), 3, None, True, 10, 7, 7, True)
        self.sprite_iter = self.explostion_sprite.iter()
        self.image = self.sprite_iter.next()
        self.IsGetScore = IsGetScore
        self.screen = screen
        self.rect = self.image.get_rect()
        self.rect.center = (x + 42,y + 60) 
        self.IsOver = False       

    def draw(self, dt, scroll):
        if self.explostion_sprite.IsEnd() and self.IsOver == False:
            if pygame.sprite.spritecollide(self, tower_group, False):
                Base.hp -= 10
            if pygame.sprite.spritecollide(self, Player_group, False):
                Player.LOSE_HP = True
            HUD.ScreenShake = True
            self.IsOver = True
            AudioManager.boom_audio.play()
        self.image = self.sprite_iter.next()
        self.screen.blit(self.image,  (self.rect.x - scroll[0], self.rect.y - scroll[1]))

    def destroy(self):
        self.kill()

class Slime(Enemy):
    Slime_direction = {'East':0, 'West':1}

    def __init__(self, x, y, screen, speed = 0.2):
        self.Slime_sprite = [
            SpriteStripAnim('Asset/Slime/slime1_side.png', (0,0,48,48), 4, None, True, 10, 3, 3, True),
            SpriteStripAnim('Asset/Slime/slime1_side.png', (0,0,48,48), 4, None, True, 10, 3, 3, False),
            SpriteStripAnim('Asset/Slime/slime_explode.png', (0,0,111,123), 8, None, True, 4, 3, 3, False)
        ]
        self.explosion = None
        self.IsAttack = False
        self.sprite = Enemy.Direction['East']
        sprite_iter = self.Slime_sprite[Slime.Slime_direction['East']].iter()
        image = sprite_iter.next()
        super().__init__(x, y, image, sprite_iter, screen, speed=speed, hp = 3, monster_type=Enemy.EnemyType['FeildMonster'])

    def attack(self):
        if self.IsAttack == False :
            self.IsAttack = True
            self.sprite_iter = self.Slime_sprite[2].iter()
            self.rect.x -= 31.5
            self.rect.y -= 75
        return super().attack()

    def update(self, dt, scroll):
        if self.IsAttack and self.Slime_sprite[2].IsEnd() :
            self.CanHurt = False
            if self.explosion == None :
                self.explosion = Explosion(self.rect.centerx, self.rect.centery, self.screen)
            else :
                self.CanHurt = self.explosion.IsOver
                if self.CanHurt :
                    self.hp = 0
        return super().update(dt, scroll)

    def draw(self, dt, scroll):
        #sprite update
        if self.IsAttack == False :
            if self.direction_hori == Enemy.Direction['East'] and self.sprite != Enemy.Direction['East']:
                self.sprite = Enemy.Direction['East']
                self.sprite_iter = self.Slime_sprite[Slime.Slime_direction['East']].iter()
            elif self.direction_hori == Enemy.Direction['West'] and self.sprite != Enemy.Direction['West'] :
                self.sprite = Enemy.Direction['West']
                self.sprite_iter = self.Slime_sprite[Slime.Slime_direction['West']].iter()
        super().draw(dt, scroll)
        #Explosion update
        if self.explosion != None :
            self.explosion.draw(dt, scroll)  

    def destroy(self, index):
        if self.explosion != None :
            self.explosion.destroy()
        super().destroy(index)

class CatNPC(pygame.sprite.Sprite):
    def __init__(self, x, y, screen):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.Cat_sprite =  SpriteStripAnim('Asset/Other/catscratch.png', (0,0,54,54), 4, None, True, 10, 3, 3, False)
        self.sprite_iter = self.Cat_sprite.iter()
        self.image = self.sprite_iter.next()

        self.rect = self.image.get_rect()
        self.rect.center = (x,y)  

    def draw(self, scroll):
        self.image = self.sprite_iter.next()
        self.screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

    def interact(self):
        print("interact")

class Heart(pygame.sprite.Sprite):
    def __init__(self, x, y, screen):
        pygame.sprite.Sprite.__init__(self)
        self.heart_sprite = [
            LoadAndScaleSheet('Asset/Other/full_heart.png', 3, 3, False),
            LoadAndScaleSheet('Asset/Other/emptyl_heart.png', 3, 3, False),
            SpriteStripAnim('Asset/Other/give_heart_animation-Sheet.png', (0,0,48,48), 5, None, True, 10, 3, 3, False),
            SpriteStripAnim('Asset/Other/loss_heart_animation-Sheet.png', (0,0,48,48), 5, None, True, 10, 3, 3, False)
        ]
        self.num = 0
        self.count = 0
        self.image = self.heart_sprite[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)  
        self.screen = screen

    def change_sprite(self, num):
        self.num = num
        if num == 1 or num == 0 :
            self.image = self.heart_sprite[num]
            self.rect = self.image.get_rect()
            self.rect.center()
        elif num == 2 or num == 3:
            self.image = self.heart_sprite[num]
            self.sprite_iter = self.image.iter()
            self.count = 0

    def lose_heart(self):
        self.change_sprite(3)

    def get_heart(self):
        self.change_sprite(2)

    def draw(self):
        if self.num == 0 or self.num == 1:
            self.screen.blit(self.image, self.rect)
        elif self.num == 2 :
            if self.count >= 4 :
                self.num = 0
                self.image = self.heart_sprite[self.num]
                self.screen.blit(self.image, self.rect)
            else :
                self.image = self.sprite_iter.next()
                self.screen.blit(self.image, self.rect)
                self.count += 1
        elif self.num == 3 :
            if self.count >= 4 :
                self.num = 1
                self.image = self.heart_sprite[self.num]
                self.screen.blit(self.image, self.rect)
            else :
                self.image = self.sprite_iter.next()
                self.screen.blit(self.image, self.rect)
                self.count += 1

class PlayerHP:
    def __init__(self, numOfHeart, start_x, start_y, screen):
        self.PlayerHP_ = []
        self.current_hp = numOfHeart-1
        self.start_x = start_x
        self.start_y = start_y
        self.screen = screen
        for i in range(numOfHeart):
            self.PlayerHP_.append(Heart(start_x+50*i, start_y, self.screen))

    def lose_hp(self):
        if self.IsAlive() == False :
            self.current_hp = -1
        else :
            self.PlayerHP_[self.current_hp].lose_heart()
            self.current_hp -= 1

    def gain_hp(self):
        self.current_hp += 1
        if self.current_hp >= len(self.PlayerHP_):
            self.PlayerHP_.append(Heart(self.start_x+50*self.current_hp, self.start_y, self.screen))
        else :
            self.PlayerHP_[self.current_hp] = Heart(self.start_x+50*self.current_hp, self.start_y, self.screen)

    def IsAlive(self):
        # hp가 남아있는가의 여부를 bool값으로 return
        if self.current_hp < 0 :
            return False
        return True

    def draw(self):
        for heart in self.PlayerHP_ :
            heart.draw()

class Base(pygame.sprite.Sprite):
    base_x = 0
    base_y = 0
    hp = 100
    def __init__(self, x, y, screen):
        pygame.sprite.Sprite.__init__(self)
        self.base_image = LoadAndScaleSheet('Asset/Other/base.png', 3, 3, False)
        self.rect = self.base_image.get_rect()
        self.sprite_iter = SpriteStripAnim('Asset/Other/crystal1.png',(0,0,30,72), 4, None, True, 10, 3, 3, False).iter()
        self.crystal_image = self.sprite_iter.next()        
        self.rect.center = (x,y)  
        Base.base_x = x
        Base.base_y = y
        self.screen = screen
        tower_group.add(self)

    def draw(self, scroll):
        self.crystal_image = self.sprite_iter.next()
        self.screen.blit(self.base_image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))
        self.screen.blit(self.crystal_image,(self.rect.centerx - 15 - scroll[0], self.rect.y - scroll[1] - 15))
        
class HUD(pygame.sprite.Sprite):
    ScreenShake = False
    Score = 0
    item = {'Speed':0,  'DamageUp':1, 'PowerUp':2}

    def __init__(self, player, base, screen):
        pygame.sprite.Sprite.__init__(self)
        self.item = [
            LoadAndScaleSheet('Asset/Other/icon1.png', 3, 3, False),
            LoadAndScaleSheet('Asset/Other/icon2.png', 3, 3, False),
            LoadAndScaleSheet('Asset/Other/icon3.png', 3, 3, False)
        ]
        self.screen = screen
        self.player = player
        self.base = base
        # Score
        self.newFont=pygame.font.Font(font, 50)
        self.scoreText=self.newFont.render("SCORE", 0, (255, 255, 255))
        self.scoreNum=self.newFont.render(str(HUD.Score), 0, (255, 255, 255))
        # Base HP BAR
        self.Base_HpBar = LoadAndScaleSheet('Asset/Other/HP_bar_1.png', 2.5, 2.5, False)
        self.hpBar = LoadAndScaleSheet('Asset/Other/filler_big.png',15.6 ,2.8,False)
        self.Hp_Rect = pygame.Rect(70, 532, self.Base_HpBar.get_width()-55, 35)
        
    @ staticmethod
    def updateScore(score):
        HUD.Score += score

    def draw(self):
        scale = Base.hp / 100 * 15.6
        if scale < 0 :
            scale = 0
        self.hpBar = LoadAndScaleSheet('Asset/Other/filler_big.png',scale,2.8,False)
        self.scoreNum=self.newFont.render(str(HUD.Score), 0, (255, 255, 255))
        self.screen.blit(self.scoreText, (800/2 - (self.scoreText.get_rect()[2]/2), 20))
        self.screen.blit(self.scoreNum, (800/2 - (self.scoreNum.get_rect()[2]/2), 60))
        # base hp bar
        pygame.draw.rect(self.screen, (255, 255, 255), self.Hp_Rect)       
        self.screen.blit(self.hpBar, (70, 535))
        self.screen.blit(self.Base_HpBar, (20 , 530))
        
    def draw_gameOver(self):
        overFont=pygame.font.Font(font, 200)
        self.gameOverText = overFont.render("GAMEOVER", 0, (255, 255, 255))

class Item(Actor):
    ItemType = {'SpeedUp':0, 'DamageUp':1, 'PowerUp':2, 'Coin':3}
    def __init__(self, x, y, screen, type = Actor.actor_type['Item'], itemType = 0):
        self.item_sprite = [
            SpriteStripAnim('Asset/Other/Powerup.png', (0,0,32,32), 4, None, True, 10, 2, 2, True),
            SpriteStripAnim('Asset/Other/coin2.png', (0,0,32,32), 8, None, True, 10, 2, 2, False)
        ]
        self.ItemType = itemType
        if self.ItemType == 3 :
            self.sprite_iter = self.item_sprite[1]
        else :
            self.sprite_iter = self.item_sprite[0]
        self.image = self.sprite_iter.next()
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)  
        self.screen = screen
        super().__init__(type)

    def update(self, dt, scroll):
        return super().update(dt, scroll)

    def draw(self, dt, scroll):
        self.image = self.sprite_iter.next()
        self.screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

