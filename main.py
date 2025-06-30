import pygame
from operator import itemgetter
from random import randint

offset = pygame.Vector2(0,0)

class Game:
    def __init__(self):
        pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode((640, 480), flags=pygame.RESIZABLE)
        self.r = 200
        self.clock = pygame.time.Clock()
        self.reset_button = Button("reset", (0, self.r + 128))
        self.reset()

    def reset(self):
        self.dragged = None
        self.piles = (Pile([randint(5, 50) for i in range(8)], (-self.r - 64, -self.r), 0),
                      Pile([randint(5, 50) for i in range(8)], (self.r + 64, -self.r), 1))
        self.player = 0
        self.score = [0, 0]
        self.pile = self.piles[self.player]
        self.board = []
        self.turn = 0
        self.update_message()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle(event)
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()

    def handle(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.WINDOWRESIZED:
            global offset
            offset = pygame.Vector2(event.x/2, event.y/2)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos - offset
            for c in self.pile:
                if pos in c:
                    self.dragged = c
                    c.dragged=True
                    return
            if pos in self.reset_button:
                self.reset()
        elif event.type == pygame.MOUSEBUTTONUP and self.dragged is not None:
            d = self.dragged
            if d.distance_to((0,0)) + d.r < self.r:
                self.pile.remove(d)
                self.board.append(d)
                d.place()
                self.end_turn()
            else:
                d.reset()
            self.dragged = None
    def update(self):
        d = self.dragged
        if d is not None:
            d.snap(pygame.mouse.get_pos() - offset, self.board)

    def draw(self):
        self.screen.fill("purple")
        pygame.draw.circle(self.screen, (0,0,0), offset, self.r, width=4)
        for c in self.board:
            c.draw(self.screen)
        if self.dragged is not None:
            self.dragged.draw(self.screen)
        for p in self.piles:
            p.draw(self.screen)
        self.screen.blit(self.message, (offset.x-self.message.get_width()/2, offset.y - self.r - 64))
        self.reset_button.draw(self.screen)
        pygame.display.flip()

    def update_message(self):
        font=pygame.font.Font(size=64)
        string=f"{self.score[0]} - {self.score[1]}"
        if not any(p.discs for p in self.piles):
            print("GAMEOVER")
            string += " white wins" if self.score[0] > self.score[1]\
                else " black wins" if self.score[0] < self.score[1]\
                else " draw"
        self.message = font.render(string, True, (128,128,128))

    def end_turn(self):
        self.player = (self.player + 1) % 2
        self.pile=self.piles[self.player]
        for c in self.board:
            if c.player != self.player and c.score < 0:
                c.remove()
                self.board.remove(c)
                self.score[self.player] += 1
        self.update_message()
        self.turn += 1


class Disc:
    def __init__(self, pos, r, player=None):
        self.home=pygame.Vector2(pos)
        self.r=r
        self.player = player
        self.colour = pygame.Color(0)
        self.colour.hsla = (0,100,0 if player else 100, 100)
        self.reset()
    def __contains__(self, pos):
        return self.pos.distance_to(pos) < self.r
    def draw(self,screen):
        screen_pos = self.pos + offset
        pygame.draw.circle(screen, self.colour, screen_pos, self.r)
        font=pygame.font.Font(size=24)
        string = str(self.score)
        if self.score < 0:
            string += '!'
        text = font.render(string, True, (128,128,128))
        screen.blit(text, (screen_pos.x, screen_pos.y))
    def move(self, disp):
        self.pos+=pygame.Vector2(disp)
    def move_to(self, pos):
        self.pos=pygame.Vector2(pos)
    def move_towards(self, pos, r):
        if isinstance(pos, Disc):
            pos = pos.pos
        self.pos = self.pos.move_towards(pos, r)
    def snap(self, pos, discs):
        old_pos = self.pos
        self.move_to(pos)
        contacts = self.get_contacts(discs)
        n = len(contacts)
        if n == 1:
            c,d = contacts[0]
            self.move_towards(c.pos, d - self.r - c.r)
        elif n > 1:
            c1,_ = contacts[0]
            c2,_ = contacts[1]
            x1 = c1.pos.x
            y1 = c1.pos.y
            x2 = c2.pos.x
            y2 = c2.pos.y
            r1 = c1.r
            r2 = c2.r
            pos1, pos2 = kissing_centre(x1,x2,y1,y2,r1,r2,self.r)
            self.move_to(min(pos1, pos2, key=self.distance_to))
        if self.get_contacts(discs):
            self.move_to(old_pos)
        self.contacts = [c[0] for c in contacts]


    def get_contacts(self,discs):
        """Return the discs overlapping self, sorted by distance."""
        contacts=[]
        for c in discs:
            d = self.distance_to(c)
            if d < self.r + c.r:
                contacts.append((c,d))
        contacts.sort(key=itemgetter(1))
        return contacts

    def distance_to(self, pos):
        if isinstance(pos, Disc):
            pos = pos.pos
        return self.pos.distance_to(pos)
    def place(self):
        self.score += sum([(1 if c.player == self.player else -1) for c in self.contacts])
        for c in self.contacts:
            c.contacts.append(self)
            c.score += 1 if c.player == self.player else -1
        self.dragged=False
        self.home=self.pos
    def remove(self):
        for c in self.contacts:
            c.contacts.remove(self)
            c.score -= (1 if c.player == self.player else -1)

    def reset(self):
        self.move_to(self.home)
        self.dragged=False
        self.contacts=[]
        self.score=0


class Pile:
    def __init__(self,discs, pos, player):
        self.margin = 6
        self.pos = pygame.Vector2(pos)
        self.end = self.pos.copy()
        self.discs = []
        for r in discs:
            self.append(Disc((0,0), r, player=player))

    def append(self, disc):
        self.end.y += disc.r + self.margin
        disc.move_to(self.end)
        disc.home=self.end.copy()
        self.end.y += disc.r + self.margin
        self.discs.append(disc)

    def remove(self, disc):
        i = self.discs.index(disc)
        disp = (0, -(2*disc.r + self.margin))
        del self.discs[i]
        for c in self.discs[i:]:
            c.move(disp)
            c.home=c.pos
    def __getitem__(self, i):
        return self.discs[i]
    def __iter__(self):
        return iter(self.discs)
    def draw(self,screen):
        for c in self:
            if not c.dragged:
                c.draw(screen)
    def move_to(self,pos):
        pos = pygame.Vector2(pos)
        disp = pos - self.pos
        print(self.pos)
        print(pos)
        for c in self.discs:
            c.home = c.home+disp
            if not c.dragged:
                c.move_to(c.home)
        self.pos=pos


def kissing_centre(x1,x2,y1,y2, r1,r2, r):
    "Find the center of a disc of radius r, which is tangent to two other discs"
    s1 = r+r1
    s2 = r+r2
    R= x1**2 -x2**2 +y1**2-y2**2 + s2**2 - s1**2
    xa = -(((y2 - y1) * ((4 * s1 ** 2 - 4 * y1 ** 2) * y2 ** 2
                            + (8 * y1 ** 3 + (-(8 * x1 * x2) + 8 * x1 ** 2 - 8 * s1 ** 2 - 4 * R) * y1) * y2
                            - 4 * y1 ** 4 + (8 * x1 * x2 - 8 * x1 ** 2 + 4 * s1 ** 2 + 4 * R) * y1 ** 2
                            + (4 * s1 ** 2 - 4 * x1 ** 2) * x2 ** 2
                            + (8 * x1 ** 3 + (-(8 * s1 ** 2) - 4 * R) * x1) * x2 - 4 * x1 ** 4
                            + (4 * s1 ** 2 + 4 * R) * x1 ** 2 - R ** 2)**0.5
           - 2 * x1 * y2 ** 2 + (2 * x2 + 2 * x1) * y1 * y2 - 2 * x2 * y1 ** 2 + R * x2 - R * x1) / (2 * y2 ** 2 - 4 * y1 * y2 + 2 * y1 ** 2 + 2 * x2 ** 2 - 4 * x1 * x2 + 2 * x1 ** 2))
    xb = ((y2 - y1) * ((4 * s1 ** 2 - 4 * y1 ** 2) * y2 ** 2
                          + (8 * y1 ** 3 + (-(8 * x1 * x2) + 8 * x1 ** 2 - 8 * s1 ** 2 - 4 * R) * y1) * y2
                          - 4 * y1 ** 4 + (8 * x1 * x2 - 8 * x1 ** 2 + 4 * s1 ** 2 + 4 * R) * y1 ** 2
                          + (4 * s1 ** 2 - 4 * x1 ** 2) * x2 ** 2 + (8 * x1 ** 3 + (-(8 * s1 ** 2) - 4 * R) * x1) * x2
                          - 4 * x1 ** 4 + (4 * s1 ** 2 + 4 * R) * x1 ** 2 - R ** 2)**0.5
         + 2 * x1 * y2 ** 2 + (-(2 * x2) - 2 * x1) * y1 * y2 + 2 * x2 * y1 ** 2 - R * x2 + R * x1) / (2 * y2 ** 2 - 4 * y1 * y2 + 2 * y1 ** 2 + 2 * x2 ** 2 - 4 * x1 * x2 + 2 * x1 ** 2)
    ya = (R - 2*xa*(x1-x2))/(2*(y1-y2))
    yb = (R - 2*xb*(x1-x2))/(2*(y1-y2))
    return (xa,ya),(xb,yb)

class Button:
    def __init__(self, text, pos):
        self.pos = pygame.Vector2(pos)
        font=pygame.font.Font(size=64)
        self.text = font.render(text, True, (255,255,255), (128,128,128))
        w = self.text.get_width()
        h = self.text.get_height()
        self.rect = pygame.Rect(self.pos.x-w/2, self.pos.y-h/2, w, h)
    def __contains__(self, pos):
        return self.rect.collidepoint(pos)
    def draw(self, screen):
        screen.blit(self.text, self.rect.move(offset))


if __name__ == '__main__':
    game = Game()
    game.run()