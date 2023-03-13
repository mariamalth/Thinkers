import pygame, sys
pygame.init()
clock = pygame.time.Clock()
#Code that can be used potentially for stick figure in environment background
    # def put_array(surface, myarr):          # put array into surface
    #     bv = surface.get_view("0")
    #     bv.write(myarr.tostring())
    # if results.segmentation_mask is not None:
    #     mask = results.segmentation_mask
    #     put_array(screen,mask)

background_image = pygame.image.load("linescape_stopmotion/Linescape1.0.0.png")
SCREEN_WIDTH = background_image.get_width()
SCREEN_HEIGHT = background_image.get_height()

class Player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.width=110
		self.height=340
		self.pos_x = SCREEN_WIDTH/2 - self.width/3
		self.pos_y = 340
		self.current_position = "center"
		self.attack_animation = False
		self.sprites = []
		self.sprites.append(pygame.image.load('0001.png'))
		# self.sprites.append(pygame.image.load('0002.png'))
		# self.sprites.append(pygame.image.load('0003.png'))
		# self.sprites.append(pygame.image.load('0004.png'))
		# self.sprites.append(pygame.image.load('0005.png'))
		# self.sprites.append(pygame.image.load('0006.png'))
		# self.sprites.append(pygame.image.load('0007.png'))
		# self.sprites.append(pygame.image.load('0008.png'))
		# self.sprites.append(pygame.image.load('0009.png'))
		# self.sprites.append(pygame.image.load('0010.png'))
		# self.sprites.append(pygame.image.load('0011.png'))
		# self.sprites.append(pygame.image.load('0012.png'))
		# self.sprites.append(pygame.image.load('0013.png'))
		# self.sprites.append(pygame.image.load('0014.png'))
		# self.sprites.append(pygame.image.load('0015.png'))
		# self.sprites.append(pygame.image.load('0016.png'))
		# self.sprites.append(pygame.image.load('0017.png'))
		# self.sprites.append(pygame.image.load('0018.png'))
		# self.sprites.append(pygame.image.load('0019.png'))
		# self.sprites.append(pygame.image.load('0020.png'))
		# self.sprites.append(pygame.image.load('0021.png'))
		# self.sprites.append(pygame.image.load('0022.png'))
		# self.sprites.append(pygame.image.load('0023.png'))
		# self.sprites.append(pygame.image.load('0024.png'))
		self.current_sprite = 0
		self.image = self.sprites[self.current_sprite]
		self.rect = pygame.Rect(self.get_position_x(), SCREEN_HEIGHT-50, self.width, self.image.get_rect().height)
		self.rect.topleft = [self.pos_x,self.pos_y]
		
		#smaller hitbox - only detects collision if obstacle hits feet
		self.hitbox = pygame.Rect( self.get_position_x(), SCREEN_HEIGHT-50, 80, 80)
		self.hitbox.topleft = [self.pos_x+15,SCREEN_HEIGHT-120]

	def get_position_x(self):
		if self.current_position == "left":
			return SCREEN_WIDTH // 2.5 - self.width
            # return WIDTH // 4 - self.pos_y 
		elif self.current_position == "right":
			return SCREEN_WIDTH * 2.5 // 4 - self.width // 2
            # return WIDTH * 3 // 4 - self.pos_x // 2
		else:  # center
			# return SCREEN_WIDTH / 2 - self.width / 2
			return SCREEN_WIDTH/2 - self.width/3
	def move_left(self):
		if self.current_position == "center":
			self.current_position = "left"
			self.rect.x = self.get_position_x()
			self.hitbox.x =  self.get_position_x()
		elif self.current_position == "right":
			self.current_position = "center"
			self.rect.x = self.get_position_x() 
			self.hitbox.x =  self.get_position_x()
	def move_right(self):
		if self.current_position == "center":
			self.current_position = "right"
			self.rect.x = self.get_position_x() 
			self.hitbox.x =  self.get_position_x()	
		elif self.current_position == "left":
			self.current_position = "center"
			self.rect.x = self.get_position_x()
			self.hitbox.x =  self.get_position_x()
	def attack(self):
		self.attack_animation = True

	def update(self,speed):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_LEFT]:
			self.move_left()
		elif keys[pygame.K_RIGHT]:
			self.move_right()
		if self.attack_animation == True:
			self.current_sprite += speed
			if int(self.current_sprite) >= len(self.sprites):
				self.current_sprite = 0
				self.attack_animation = False

		self.image = self.sprites[int(self.current_sprite)]

# General setup

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Endless Runner")

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))

# Creating the sprites and groups
moving_sprites = pygame.sprite.Group()
player = Player()
moving_sprites.add(player)

while True:
	player.attack()
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		# if event.type == pygame.KEYDOWN:
		

	# Drawing
	n = 0
	# while n !=121:
	# 	background_image = pygame.image.load(f"linescape_stopmotion/Linescape1.0.{n}.png")
	# 	screen.blit(background_image, (0, 0))
	# 	if n !=120:
	# 		n+=1
	# 	else: 
	# 		n=0
	screen.blit(background_image, (0, 0))
	pygame.draw.rect(screen, (255,0,0), player.hitbox)
	# pygame.draw.rect(screen,(255,0,255),player.rect)
	moving_sprites.draw(screen)
	moving_sprites.update(1)
	pygame.display.flip()
	clock.tick(60)