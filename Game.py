import pygame
import os
import random
import neat

ia_play = True
geracao = 0

#TAMANHO DA TELA
TELA_LARGURA = 500
TELA_ALTURA = 800

#IMAGENS DO GAME
IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'cano.png')))
IMAGEM_PISO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'piso.png')))
IMAGEM_FUNDO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'fundo.png')))
IMAGEM_FISH = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'peixe.png')))

pygame.font.init()
FONTE_SCORES = pygame.font.SysFont('Times', 30)

#DEFINIÇOES DO PEIXE
class Fish:
 IMGS = IMAGEM_FISH
 ROT_MAXIMA = 25
 VEL_ROT = 20
 TEMPO_ANIMACAO = 5

 def __init__(self, x, y):
     self.x = x
     self.y = y
     self.ang = 0
     self.vel = 0
     self.alt = self.y
     self.tempo = 0
     self.cont_img = 0
     self.img = self.IMGS

 def nadar(self):
     self.vel = -10.5
     self.tempo = 0
     self.alt = self.y

 def mover(self):
     #CALCULO DO DESLOCAMENTO
     self.tempo += 1
     desloc = 1.5 * (self.tempo**2) + self.vel * self.tempo

     if desloc > 16:
         desloc = 16
     elif desloc < 0:
         desloc -= 2

     self.y += desloc

     if desloc < 0 or self.y < (self.alt + 50):
         if self.ang < self.ROT_MAXIMA:
             self.ang = self.ROT_MAXIMA
     else:
         if self.ang > -90:
             self.ang -= self.VEL_ROT

 def desenhar(self, tela):

     img_rot = pygame.transform.rotate(self.img, self.ang)
     pos_centro_img = self.img.get_rect(topleft=(self.x, self.y)).center
     retang = img_rot.get_rect(center=pos_centro_img)
     tela.blit(img_rot, retang.topleft)

 def get_mask(self):
     return pygame.mask.from_surface(self.img)

#DEFINIÇOES DO CANO
class Cano:
 DIST = 200
 VEL = 5

 def __init__(self, x):
     self.x = x
     self.alt = 0
     self.pos_top = 0
     self.pos_bot = 0
     self.CANO_TOP = pygame.transform.flip(IMAGEM_CANO, False, True)
     self.CANO_BOT = IMAGEM_CANO
     self.passou = False
     self.def_alt()

 def def_alt(self):
     self.alt = random.randrange(50, 450)
     self.pos_top = self.alt - self.CANO_TOP.get_height()
     self.pos_bot = self.alt + self.DIST

 def mover(self):
     self.x -= self.VEL

 def desenhar(self, tela):
     tela.blit(self.CANO_TOP, (self.x, self.pos_top))
     tela.blit(self.CANO_BOT, (self.x, self.pos_bot))

 def colidir(self, fish):
     fish_mask = fish.get_mask()
     top_mask = pygame.mask.from_surface(self.CANO_TOP)
     bot_mask = pygame.mask.from_surface(self.CANO_BOT)

     dist_top = (self.x - fish.x, self.pos_top - round(fish.y))
     dist_bot = (self.x - fish.x, self.pos_bot - round(fish.y))

     top_score = fish_mask.overlap(top_mask, dist_top)
     bot_score = fish_mask.overlap(bot_mask, dist_bot)

     if bot_score or top_score:
         return True
     else:
         return False

#DEFINIÇOES DO CANO
class Piso:
 VEL = 5
 LARGURA = IMAGEM_PISO.get_width()
 IMAGEM = IMAGEM_PISO

 def __init__(self, y):
     self.y = y
     self.x1 = 0
     self.x2 = self.LARGURA

 def mover(self):
     self.x1 -= self.VEL
     self.x2 -= self.VEL

     if self.x1 + self.LARGURA < 0:
         self.x1 = self.x2 + self.LARGURA
     if self.x2 + self.LARGURA < 0:
         self.x2 = self.x1 + self.LARGURA

 def desenhar(self, tela):
     tela.blit(self.IMAGEM, (self.x1, self.y))
     tela.blit(self.IMAGEM, (self.x2, self.y))


def desenhar_tela(tela, fishs, canos, chao, scores):
 tela.blit(IMAGEM_FUNDO, (0, 0))
 for fish in fishs:
     fish.desenhar(tela)
 for cano in canos:
     cano.desenhar(tela)

 texto = FONTE_SCORES.render(f"SCORE: {scores}", 1, (255, 255, 255))
 tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))

 if ia_play:
     texto = FONTE_SCORES.render(f"GENERATION: {geracao}", 1, (255, 255, 255))
     tela.blit(texto, (10, 10))

 chao.desenhar(tela)
 pygame.display.update()


def main(genomas, config):
 global geracao
 geracao += 1

 if ia_play:
     redes = []
     lista_genomas = []
     fishs = []
     for _, genoma in genomas:
         rede = neat.nn.FeedForwardNetwork.create(genoma, config)
         redes.append(rede)
         genoma.fitness = 0
         lista_genomas.append(genoma)
         fishs.append(Fish(230, 350))
 else:
     fishs = [Fish(230, 350)]
 piso = Piso(730)
 canos = [Cano(700)]
 tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
 scores = 0
 relogio = pygame.time.Clock()

 rodando = True
 while rodando:
     relogio.tick(30)

     for evento in pygame.event.get():
         if evento.type == pygame.QUIT:
             rodando = False
             pygame.quit()
             quit()
         if not ia_play:
             if evento.type == pygame.KEYDOWN:
                 if evento.key == pygame.K_SPACE:
                     for fish in fishs:
                         fish.nadar()

     indice_cano = 0
     if len(fishs) > 0:
         if len(canos) > 1 and fishs[0].x > (canos[0].x + canos[0].CANO_TOP.get_width()):
             indice_cano = 1
     else:
         rodando = False
         break

     for i, fish in enumerate(fishs):
         fish.mover()
         lista_genomas[i].fitness += 0.1
         output = redes[i].activate((fish.y,
                                     abs(fish.y - canos[indice_cano].alt),
                                     abs(fish.y - canos[indice_cano].pos_bot)))
         if output[0] > 0.5:
             fish.nadar()
     piso.mover()

     add_cano = False
     rmv_cano = []
     for cano in canos:
         for i, fish in enumerate(fishs):
             if cano.colidir(fish):
                 fishs.pop(i)
                 if ia_play:
                     lista_genomas[i].fitness -= 1
                     lista_genomas.pop(i)
                     redes.pop(i)
             if not cano.passou and fish.x > cano.x:
                 cano.passou = True
                 add_cano = True
         cano.mover()
         if cano.x + cano.CANO_TOP.get_width() < 0:
             rmv_cano.append(cano)

     if add_cano:
         scores += 1
         canos.append(Cano(600))
         for genoma in lista_genomas:
             genoma.fitness += 5
     for cano in rmv_cano:
         canos.remove(cano)

     for i, fish in enumerate(fishs):
         if (fish.y + fish.img.get_height()) > piso.y or fish.y < 0:
             fishs.pop(i)
             if ia_play:
                 lista_genomas.pop(i)
                 redes.pop(i)

     desenhar_tela(tela, fishs, canos, piso, scores)

def rodar(caminho_config):
 config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, caminho_config)

 populacao = neat.Population(config)
 populacao.add_reporter(neat.StdOutReporter(True))
 populacao.add_reporter(neat.StatisticsReporter())

 if ia_play:
     populacao.run(main, 50)
 else:
     main(None, None)


if __name__ == '__main__':
 caminho = os.path.dirname(__file__)
 caminho_config = os.path.join(caminho, 'IA.txt')
 rodar(caminho_config)
