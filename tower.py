import math
import random
import sys
import time
import pygame
import pygame as pg
from pygame.sprite import AbstractGroup

WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ

pthp = 10
ethp = 10

def check_bound(obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数 obj：オブジェクSurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < 0 or WIDTH < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < 0 or HEIGHT < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate





class Pltower(pg.sprite.Sprite):
    """
    ゲームキャラクター（塔）に関するクラス
    """
    def __init__(self, xy: tuple[int, int]):
        """
        塔画像Surfaceを生成する
        引数1 xy：塔画像の位置座標タプル
        """
        super().__init__()
        
        self.image = pg.transform.rotozoom(pg.image.load(f"ex05/fig/landmark_tower_babel.png"), 0, 0.5)
        self.dire = (+1, 0)
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10
        self.state = "normal"
        self.hyper_life = -1




    def update(self,screen: pg.Surface):
        
        
        screen.blit(self.image, self.rect)
    
    def get_direction(self) -> tuple[int, int]:
        return self.dire



class Entower(pg.sprite.Sprite):
    def __init__(self, xy: tuple[int, int]):
        """
        塔画像Surfaceを生成する
        引数1 xy：塔画像の位置座標タプル
        """
        super().__init__()
        
        self.image = pg.transform.rotozoom(pg.image.load(f"ex05/fig/landmark_tower_babel.png"), 0, 0.5)
        self.dire = (-1, 0)
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10
        self.state = "normal"
        self.hyper_life = -1





    def update(self,screen: pg.Surface):
        
        screen.blit(self.image, self.rect)
    
    def get_direction(self) -> tuple[int, int]:
        return self.dire


class Bomb(pg.sprite.Sprite):
    """
    爆弾に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    def __init__(self, emy: "Enemy", pltower: Pltower):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 pltower：攻撃対象のこうかとん
        """
        super().__init__()
        rad = random.randint(30, 50)  # 爆弾円の半径：30以上50以下の乱数
        color = random.choice(__class__.colors)  # 爆弾円の色：クラス変数からランダム選択
        self.image = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のpltowerの方向を計算
        self.vx, self.vy = -1, 0
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery
        self.speed = 6

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Plchara(pg.sprite.Sprite):
    """
    こうかとんキャノンに関するクラス
    """
    def __init__(self, pltower: Pltower):
        """
        ビーム画像Surfaceを生成する
        引数 pltower：こうかとんキャノンを放つ塔
        """
        super().__init__()
        self.vx, self.vy = pltower.get_direction()
        img0 = pg.transform.rotozoom(pg.image.load(f"ex05/fig/3.png"), 0, 1.0)
        self.image = pg.transform.flip(img0, True, False)
        
        self.rect = self.image.get_rect()
        self.rect.centery = HEIGHT/2
        self.rect.centerx = pltower.rect.centerx
        self.speed = 10

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    def __init__(self, obj: "Bomb|Enemy", life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombまたは敵機インスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        img = pg.image.load("ex05/fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()






class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    imgs = [pg.image.load(f"ex05/fig/alien{i}.png") for i in range(1, 4)]
    
    def __init__(self):
        super().__init__()
        self.image = random.choice(__class__.imgs)
        self.rect = self.image.get_rect()
        self.rect.center = WIDTH-100, HEIGHT/2
        self.state = "stop"  # 降下状態or停止状態
        self.vx = -5
        self.interval = random.randint(50, 300)  # 爆弾投下インターバル

    def update(self):
        """
        敵機を速度ベクトルself.vyに基づき移動（降下）させる
        ランダムに決めた停止位置_boundまで降下したら，_stateを停止状態に変更する
        引数 screen：画面Surface
        """
        self.rect.centerx += self.vx
        


class Score:
    """
    打ち落とした爆弾，敵機の数をスコアとして表示するクラス
    爆弾：1点
    敵機：10点
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.score = 0
        self.image = self.font.render(f"Score: {self.score}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def score_up(self, add):
        self.score += add

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.score}", 0, self.color)
        screen.blit(self.image, self.rect)


def main():
    pg.display.set_caption("プロトタワー")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("ex05/fig/pg_bg.jpg")
    score = Score()

    pltower = Pltower((100, HEIGHT/2-100))
    
    entower = Entower((WIDTH-100, HEIGHT/2-100))
    bombs = pg.sprite.Group()
    plcharas = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()

    gbb = pg.sprite.Group()


    tmr = 0
    clock = pg.time.Clock()
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:    
                if score.score>= 100:
                    score.score-=100
                    plcharas.add(Plchara(pltower))
            
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                score.score += 100
            if event.type == pg.KEYDOWN and event.key == pg.K_BACKSPACE:
                emys.add(Enemy())
        if tmr%200 == 0:  # 200フレームに1回，敵機を出現させる
                emys.add(Enemy())    
    
        screen.blit(bg_img, [0, 0])


        score.score_up(1)
        if score.score> 1000:
            score.score = 1000

        for emy in emys:
            pass
            #bombs.add(Bomb(emy, pltower))

        for emy in pg.sprite.groupcollide(emys, plcharas, True, True).keys():
            exps.add(Explosion(emy, 100))  # 爆発エフェクト

        for bomb in pg.sprite.groupcollide(bombs, plcharas, True, True).keys():
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト

        for bomb in pg.sprite.spritecollide(pltower, bombs, True):
            if pltower.state == "hyper":
                exps.add(Explosion(bomb, 50))  # 爆発エフェクト
                score.score_up(1)  # 1up
            else:
                score.update(screen)
                pg.display.update()
                time.sleep(2)
                return
        if len(pg.sprite.spritecollide(pltower, emys, True)) != 0:
            font1 = pygame.font.SysFont("hg正楷書体pro", 400)  # 敗北ロゴ生成
            font2 = pygame.font.SysFont(None, 300)
            
            text1 = font1.render("敗北", True, (255,0,0))
            text2 = font2.render("LOSE", True, (255,0,0))
            screen.blit(text1, (WIDTH/2-400,HEIGHT/2-400))
            screen.blit(text2, (WIDTH/2-300,HEIGHT/2+100))
        
            pygame.display.update() #描画処理を実行
            score.update(screen)
            pg.display.update()       
            pygame.display.update() #描画処理を実行
            time.sleep(2)
            return
        if len(pg.sprite.spritecollide(entower, plcharas, True)) != 0:
            font1 = pygame.font.SysFont("hg正楷書体pro", 400)  # 勝利ロゴ生成
            font2 = pygame.font.SysFont(None, 300)
            
            text1 = font1.render("勝利", True, (255,255,0))
            text2 = font2.render("WIN", True, (255,255,0))
            screen.blit(text1, (WIDTH/2-400,HEIGHT/2-400))
            screen.blit(text2, (WIDTH/2-200,HEIGHT/2+100))
        
            pygame.display.update() #描画処理を実行
            score.update(screen)
            pg.display.update()
            time.sleep(2)
            return
        gbb.update(pltower)
        gbb.draw(screen)

        
        entower.update(screen)
        pltower.update(screen)
        plcharas.update()
        plcharas.draw(screen)
        emys.update()
        emys.draw(screen)
        bombs.update()
        bombs.draw(screen)
        exps.update()
        exps.draw(screen)
        score.update(screen)
        
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()