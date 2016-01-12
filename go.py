from ast import literal_eval
import random

def Adjacent (position, n) :
	neighbors = []
	if (position[0] > 1) :
		neighbors += [(position[0]-1, position[1],)]
	if (position[0] < n) :
		neighbors += [(position[0]+1, position[1],)]
	if (position[1] > 1) :
		neighbors += [(position[0], position[1]-1,)]
	if (position[1] < n) :
		neighbors += [(position[0], position[1]+1,)]
	return neighbors

def GetGroups (pieces, n) :
	groups = []
	while pieces :
		cluster = []
		queue = [pieces[0]]
		while queue :
			elem = queue.pop()
			if elem in pieces :
				pieces.remove(elem)
				cluster += [elem]
				queue += Adjacent (elem, n)
		groups += [cluster]
	return groups

def Serialize (groups, n) :
	return [x for y in groups for x in y]

def GetBorder (group, n) :
	border = []
	for x in group :
		neighbors = Adjacent (x, n)
		for y in neighbors :
			if y not in group :
				border += [y]
	return border

def PrintBoard (pieces1, pieces2, n) :
	for x in range (1,n+1) :
		line = str (x) + ' '
		for y in range (1, n+1) :
			if (x,y,) in pieces1 :
				line += '[1]'
			elif (x,y,) in pieces2 :
				line += '[2]'
			else :
				line += '[ ]'
		print line

def CountLiberties (group, piecesEnemy, n) :
	border = GetBorder (group[:], n)
	liberties = [x for x in border if x not in piecesEnemy]
	return len(liberties)

def CountBorder (group, n) :
	border = GetBorder (group[:], n)
	return len(border)
	
def Capture (piecesPlayer, piecesEnemy, n) :
	captured = []
	groups = GetGroups (piecesEnemy[:], n)
	for x in groups :
		if CountLiberties (x, piecesPlayer, n) == 0 :
			captured += [x]
	return captured

def LegitMoves (piecesPlayer, piecesEnemy, n) :
	moves = ['Pass',]
	moves += [(x,y,) for x in range (1, n+1) for y in range (1, n+1) if (x,y,) not in piecesPlayer and (x,y,) not in piecesEnemy]
	return moves	

def LibertyRatio (group, piecesEnemy, n) :
	return float(CountLiberties (group, piecesEnemy, n))/CountBorder(group, n)

def AverageLibertyRatio (groups, piecesEnemy, n) :
	s = 0
	for group in groups :
		s += LibertyRatio (group, piecesEnemy, n)
	return s/len(groups)

def ReadMove (piecesPlayer, piecesEnemy, n) :
	mInput = raw_input ()
	if mInput == 'Pass' :
		return 'Pass'
	else :
		return literal_eval (mInput)


def BestOffensiveMove (piecesPlayer, piecesEnemy, n) :
	groups = GetGroups (piecesEnemy[:], n)
	level1 = []
	level2 = []
	for g in groups :
		x = CountLiberties (g, piecesPlayer, n)
		if x == 1 :
			border = GetBorder (g[:], n)
			liberties = [y for y in border if y not in piecesPlayer]
			level1 += [(liberties[0],len(g))]
		elif x <= 3 :
			border = GetBorder (g[:], n)
			liberties = [y for y in border if y not in piecesPlayer]
			collector = []
			for y in liberties :
				collector += [(y,CountLiberties(g+[y], piecesPlayer, n))]
			bestchoice = max(collector,key=lambda item:item[1])[0]
			level2 += [(bestchoice,len(g))]
	if level1 :
		return (max(level1,key=lambda item:item[1])[0],1)
	elif level2 :
		return (max(level2,key=lambda item:item[1])[0],2)
	else :
		return None

def Width (group) :
	diameters = [abs(x[0]-y[0])+abs(x[1]-y[1]) for x in group for y in group]
	return max(diameters)

def Diameter (group) :
	xm = sum([x[0] for x in group])/len(group)
	ym = sum([x[1] for x in group])/len(group)
	divergences = [abs(x[0]-xm)+abs(x[1]-ym) for x in group]
	return sum(divergences)

def BestDefensiveMove (piecesPlayer, piecesEnemy, n) :
	groups = GetGroups (piecesPlayer[:], n)
	level1 = []
	level2 = []
	for g in groups :
		x = CountLiberties (g, piecesEnemy, n)
		if x == 1 :
			border = GetBorder (g[:], n)
			liberties = [y for y in border if y not in piecesEnemy]
			if CountLiberties (g+[liberties[0]], piecesEnemy, n) > 1:
				level1 += [(liberties[0],len(g))]
			else : #getting desperate, counterattack
				engroups = GetGroups (piecesEnemy[:], n)
				for eng in engroups :
					flag = False
					for i in eng :
						if i in border :
							flag = True
					if flag == True and CountLiberties (eng, piecesPlayer, n) == 1 :
						return BestOffensiveMove (piecesPlayer, eng, n)
		elif x <= 3 :
			border = GetBorder (g[:], n)
			liberties = [y for y in border if y not in piecesEnemy]
			collector = []
			for y in liberties :
				collector += [(y,CountLiberties(g+[y], piecesEnemy, n))]
			bestchoice = max(collector,key=lambda item:item[1])[0]
			level2 += [(bestchoice,len(g))]
	if level1 :
		return (max(level1,key=lambda item:item[1])[0],1)
	elif level2 :
		return (max(level2,key=lambda item:item[1])[0],2)
	else :
		return None

def BestExpansiveMove (piecesPlayer, piecesEnemy, n) :
	if piecesPlayer :
		groups = GetGroups (piecesPlayer[:], n)
		valgroups = [(g,LibertyRatio) for g in groups]
		gv = min(valgroups,key=lambda item:item[1])
		g = gv[0]
		border = GetBorder (g[:], n)
		gval = []
		for x in border :
			if x not in piecesEnemy :
				temp = piecesPlayer+[x]
				tempgroup = [tgroup for tgroup in GetGroups (temp[:], n) if x in tgroup][0]
				if gv[1] >= 0.8 :
					val = Diameter (tempgroup)
				else :
					val = Width (tempgroup)
				gval += [(x,val)]
		return max(gval,key=lambda item:item[1])[0]
	else :
		legit = [(x,y,) for x in range (1, n+1) for y in range (1, n+1) if (x,y,) not in piecesEnemy]
		if legit :
			return random.choice(legit)
		else :
			return None

def DecideMoveGreedy (piecesPlayer, piecesEnemy, n) :
	offence = BestOffensiveMove (piecesPlayer, piecesEnemy, n)
	defence = BestDefensiveMove (piecesPlayer, piecesEnemy, n)
	expand = BestExpansiveMove (piecesPlayer, piecesEnemy, n)
	if defence != None and defence[1] == 1 :
		print 'Defence'
		return defence[0]
	elif offence != None and offence[1] == 1 :
		print 'Offence'
		return offence[0]
	elif defence != None and defence[1] == 2 :
		print 'Defence'
		return defence[0]
	elif offence != None and offence[1] == 2 :
		print 'Offence'
		return offence[0]
	else :
		return expand

def CountScore1 (pieces) :
	return len(pieces)

def CountScore2 (captured) :
	s = 0
	for x in captured :
		s += len(x)
	return s

class Game :
	def __init__ (self, n, controlP1, controlP2) :
		self.turn = 1
		self.n = n
		self.controlP1 = controlP1
		self.controlP2 = controlP2
		self.piecesP1 = []
		self.piecesP2 = []
		self.capturedP1 = []
		self.capturedP2 = []
		random.seed()
	def Play (self) :
		self.passSeq = 0
		while self.passSeq < 2 :
			print '-----------------------------------------'
			print '-----------------------------------------'
			print '-----------------------------------------'
			print 'ROUND: ', self.turn
			print '-----------------------------------------'
			print '-----------------------------------------'
			print '-----------------------------------------'
			PrintBoard (self.piecesP1, self.piecesP2, self.n)
			if self.turn % 2 == 1 :
				move = self.controlP1 (self.piecesP1, self.piecesP2, self.n)
				while move in self.piecesP1 or move in self.piecesP2 :
					print 'A stone is already there!'
					move = self.controlP1 (self.piecesP1, self.piecesP2, self.n)
			else :
				move = self.controlP2 (self.piecesP2, self.piecesP1, self.n)
				while move in self.piecesP1 or move in self.piecesP2 :
					print 'A stone is already there!'
					move = self.controlP2 (self.piecesP2, self.piecesP1, self.n)
			print 'Player chose : ', move
			if move == 'Pass' :
				self.passSeq += 1
			else :
				self.passSeq = 0
				if self.turn % 2 == 1 :
					self.piecesP1 += [move]
					
				else :
					self.piecesP2 += [move]
				captureEvent = Capture (self.piecesP1, self.piecesP2, self.n)
				if captureEvent :
					self.capturedP1 += captureEvent
					capturedStones = Serialize (captureEvent, self.n)
					for x in capturedStones :
						self.piecesP2.remove (x)
				captureEvent = Capture (self.piecesP2, self.piecesP1, self.n)
				if captureEvent :
					self.capturedP2 += captureEvent
					capturedStones = Serialize (captureEvent, self.n)
					for x in capturedStones :
						self.piecesP1.remove (x)
			self.turn += 1
		print '------GAME OVER------'
		print 'P1 SCORE: ', CountScore1 (self.piecesP1)+CountScore2(self.capturedP1)
		print 'P2 SCORE: ', CountScore1 (self.piecesP2)+CountScore2(self.capturedP2)



game = Game(9, ReadMove, DecideMoveGreedy)
game.Play ()
