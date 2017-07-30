# -*- coding: utf-8 -*-
import unicodedata
import telepot
import time
import thread
import random
import math
import traceback
from persos import *
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

class Game:
    """A game of werewolf"""
    VOTE_TIME=20
    def __init__(self, bot, chat_id, player_id, name):
        self.launched=False
        self.exception=False
        self.day=0
        self.bot = bot
        self.chat_id=chat_id
        self.ids = [player_id]
        self.names = [unicodedata.normalize('NFKD',name).encode('ascii','ignore')]
        self.alive_players =[]
        self.dead_players=[]
        self.dead_bots=[]
        self.alive_bots=[]
        self.keyboards=[]
        self.nb_expected=0
        self.nb_reponses=0
        self.victims=[]
        self.protected=(None, None)
        self.noAttack=False
        self.doubleVote=False
        self.moment=None
        # moment is used to know in which part of the game the bot is (night, day, vote,...)
        self.voteM=None
        self.bot_ids=[]
        self.delayvote=False
        self.NOMS_BOTS=['Albert','Bob','Hervé','Jean','Marie','André','Pierre','Bernard','Lucie','René','Jeannine','Marcel','Robert','Claude','Denise','Yvette','Paulette','Monique','Simone','Audette','Paul','Thérèse','Lucien','Colette','Huguette','Marguerite']
        self.bot.sendMessage(player_id, "Tu as rejoint la partie")

    # Get the name from a player ID
    def name_of(self, ofid):
        for p in self.alive_players+self.alive_bots:
            if p.id == ofid:
                return p.name

    def nb_players(self):
        return len(self.ids)

    def nb_bots(self):
        return len(self.alive_bots)

    # Finishes a game (game interruption, neither a win nor a lose)
    def kill(self):
        self.cleanUp("Partie interrompue...")
        for p in self.alive_players:
            self.alive_players.remove(p)
            self.dead_players.append(p)
        for b in self.alive_bots:
            self.alive_bots.remove(b)
            self.dead_bots.append(b)

    def players(self):
        all_names = ''
        if len(self.alive_players)==0 and len(self.dead_players)==0: 
            all_names+='Liste des personnes ayant join:\n'
            for name in self.names:
                if all_names != 'Liste des personnes ayant join:\n':
                    all_names += ', '+ name
                else:
                    all_names += name
            for b in self.alive_bots:
                all_names += ', ' + b.name
        elif self.isOver():
            all_names+='Fin de la partie:\n'
            for p in self.dead_players:
                if p.lover != None:
                    all_names+= '☠ %s 💘 - %s - %s\n'%(p.name, p.role.winCondition(self,p), p.role.text)
                else:
                    all_names+= '☠ %s - %s - %s\n'%(p.name, p.role.winCondition(self,p), p.role.text)
            for b in self.dead_bots:
                if b.lover != None:
                    all_names+= '☠ %s 💘 - %s - %s\n'%(b.name, b.role.winCondition(self,b), b.role.text)
                else:
                    all_names+= '☠ %s - %s - %s\n'%(b.name, b.role.winCondition(self,b), b.role.text)
            for p in self.alive_players:
                all_names+='👤'
                if p.maire:
                    all_names+='🎖'
                if p.lover != None:
                    all_names+= '%s 💘 - %s - %s\n'%(p.name, p.role.winCondition(self,p), p.role.text)
                else:
                    all_names+= '%s - %s - %s\n'%(p.name, p.role.winCondition(self,p), p.role.text)
            for b in self.alive_bots:
                if b.lover != None:
                    all_names+= '👤 %s 💘 - %s - %s\n'%(b.name, b.role.winCondition(self,b), b.role.text)
                else:
                    all_names+= '👤 %s - %s - %s\n'%(b.name, b.role.winCondition(self,b), b.role.text)

        else:
            all_names+='Jour n°%d - Joueurs:\n'%self.day
            for p in self.dead_players:
                all_names+='☠ %s'%p.name
                if p.lover!=None:
                    all_names+='💘'
                all_names+= ' - %s\n'%p.role.text
            for p in self.dead_bots:
                all_names+='☠ %s'%p.name
                if p.lover!=None:
                    all_names+='💘'
                all_names+= ' - %s\n'%p.role.text
            for p in self.alive_players:
                all_names+='👤'
                if p.maire:
                    all_names+='🎖'
                all_names+= ' %s\n'%p.name
            for b in self.alive_bots:
                all_names+= '👤 %s\n'%b.name

        self.bot.sendMessage(self.chat_id, all_names)        


    def add_player(self, id, name):
        if not self.launched:
            if id not in self.ids:
                self.ids.append(id)
                self.names.append(unicodedata.normalize('NFKD',name).encode('ascii','ignore'))
                self.bot.sendMessage(self.chat_id,"%s a rejoint la partie\nIl y a %d joueurs et %d bots"%(name,self.nb_players(),self.nb_bots()))
            else:
                self.bot.sendMessage(self.chat_id,"Pas besoin de rejoindre une partie plusieurs fois...")
        else:
            self.bot.sendMessage(self.chat_id,"Impossible de rejoindre une partie déjà lancée")

    def add_bot(self):
        if not self.launched:
            offset=self.nb_bots()+1
            if offset<25:
                name=random.choice(self.NOMS_BOTS)
                self.NOMS_BOTS.remove(name)
                self.alive_bots.append(Bot(Role(),self.chat_id+offset, name+"(🤖)"))
                self.bot_ids.append(self.chat_id+offset)
                self.bot.sendMessage(self.chat_id, 'Un bot a été ajouté, il y a %d joueurs et %d bots' % (self.nb_players(),self.nb_bots()))
            else:
                self.bot.sendMessage(self.chat_id, "Impossible d'ajouter plus de bots...")
        else:
            self.bot.sendMessage(self.chat_id, "Impossible d'ajouter des bots en cours de partie...")

    def remove_bot(self):
        if self.nb_bots()>0:
            if not self.launched:
                self.alive_bots.pop(0)
                self.bot.sendMessage(self.chat_id, 'Un bot été enlevé, il reste %d joueurs et %d bots' % (self.nb_players(),self.nb_bots()))
            else:
                self.bot.sendMessage(self.chat_id, "Partie en cours, impossible d'enlever des bots")
        else:
            self.bot.sendMessage(self.chat_id, "No bot to remove")

    def remove_player(self, id):
        if len(self.ids)==1:
            self.bot.sendMessage(self.chat_id, "Impossible de quitter s'il ne reste qu'un joueur. Merci d'utiliser /cancelgame")
        else:
            if id in self.ids:
                index=self.ids.index(id)
                del self.ids[index]
                del self.names[index]
                self.bot.sendMessage(self.chat_id,"Il reste %d joueurs et %d bots"%(self.nb_players(),self.nb_bots()))
            else:
                self.bot.sendMessage(self.chat_id,"On ne peut pas quitter des parties qu'on a pas rejoint... Boloss")

    def manual_setup(self):
        for i in range(len(self.ids)):
            if i == 0:
                self.alive_players.append(Player(Ange(), self.ids[i], self.names[i]))
            elif i == 1:
                self.alive_players.append(Player(Loupgarou(), self.ids[i], self.names[i]))
            elif i ==2:
                self.alive_players.append(Player(Voyante(), self.ids[i], self.names[i]))
            else:
                self.alive_players.append(Player(Chasseur(), self.ids[i], self.names[i]))

            self.bot.sendMessage(self.ids[i], self.alive_players[i].role.description())

    def automatic_setup(self):
        tot_players=self.nb_players()+self.nb_bots()
        nb_mechants=int(math.floor(tot_players/3.5))
        nb_gentils=int(tot_players-nb_mechants)

        roles=[]
        roles.append(Chasseur())
        if tot_players>3:
            roles.append(Cupidon())
        roles.append(Voyante())
        roles.append(Fou())
        roles.append(Sorciere())
        roles.append(Maudit())
        roles.append(Ange())
        roles.append(Joaillier(1))
        roles.append(Juge())
        roles.append(Emo())
        roles.append(Maladroit())
        roles.append(EnfantSauvage())
        roles.append(Copycat())
        roles.append(Idiot())

        if len(roles)>nb_gentils:
            while(len(roles)>nb_gentils):
                out=random.choice(roles)
                roles.remove(out)

        elif len(roles)<nb_gentils:
            while(len(roles)<nb_gentils):
                roles.append(Role())

        for i in range(nb_mechants):
            roles.append(Loupgarou())

        for i in range(len(self.ids)):
            rand=random.choice(roles)
            self.alive_players.append(Player(rand, self.ids[i], self.names[i]))
            roles.remove(rand)

        for b in self.alive_bots:
            rand=random.choice(roles)
            b.role=rand
            roles.remove(rand)

        for p in self.alive_players:
            self.bot.sendMessage(p.id, p.role.description())


    def launch(self):
        try:            
            if not self.launched:
                self.launched=True
                self.moment='setup'
                self.automatic_setup()
                #self.manual_setup()
            
            if self.day==0:
                print 'Liste des joueurs (en vie:)' #inutile
                for player in self.alive_players:
                    print 'Nom: %s role: %s' % (player.name, player.role)
                for player in self.alive_bots:
                    print 'Nom: %s role: %s' % (player.name, player.role)
                
                time.sleep(4)
                self.moment='firstNight'
                for player in self.alive_players+self.alive_bots:
                    player.role.firstNight(self, player)
                self.waitOnResponses(self.VOTE_TIME)
                self.cleanUp('Trop tard')
                
                time.sleep(1)
                self.voteMaire()
                self.waitOnResponses(self.VOTE_TIME)
                self.cleanUp('Trop tard')
                time.sleep(3)

            while(not self.isOver()):
                self.moment='night'
                for p in self.alive_players+self.alive_bots:
                    p.vote=0
                for player in self.alive_players+self.alive_bots:
                    player.role.atNight(self, player)

                time.sleep(self.VOTE_TIME)
                self.decisionLoup()

                self.moment='night2'
                for player in self.alive_players+self.alive_bots:
                    player.role.atNight2(self, player)

                self.waitOnResponses(self.VOTE_TIME)
                self.decisionSorciere()
                self.noAttack=False
                self.protected=(None, None)
                self.voteM=None

                if self.isOver():
                    break
                self.players()

                time.sleep(5)
                self.moment='day'
                self.day+=1
                for player in self.alive_players+self.alive_bots:
                    player.role.atDay(self, player)

                self.waitOnResponses(self.VOTE_TIME)
                self.cleanUp("Le vote va commencer...")
                time.sleep(5)
                
                if self.delayvote:
                    self.bot.sendMessage(self.chat_id, "Vous avez 20 secondes avant que le vote commence")
                    time.sleep(20)

                if self.doubleVote:
                    self.vote("Jour n°%d - Vote spécial" %self.day)
                    if self.isOver():
                        break
                    self.players()
                    self.doubleVote=False
                    time.sleep(4)

                self.vote("Jour n°%d - Vote - Qui parait le plus coupable?" %self.day)

                if self.isOver():
                    break
                self.players()
                time.sleep(3)
            
            
            print 'Game over'

            if self.nb_loups() == len(self.alive_players+self.alive_bots) and len(self.alive_players+self.alive_bots)>0:
                self.bot.sendDocument(self.chat_id, open('files/v_loup.gif'), caption="Les loups remportent cette partie", disable_notification=None, reply_to_message_id=None, reply_markup=None)
            elif len(self.alive_players+self.alive_bots)==2 and (self.alive_players+self.alive_bots)[0].lover!=None:
                self.bot.sendDocument(self.chat_id, open('files/v_love2.gif'), caption="L'amour c'est beau <3", disable_notification=None, reply_to_message_id=None, reply_markup=None)
            elif self.nb_loups() == 0 and len(self.alive_players+self.alive_bots)>0:
                self.bot.sendDocument(self.chat_id, open('files/v_village.gif'), caption="Les villageois ont vaillament défendu leur petit hameau", disable_notification=None, reply_to_message_id=None, reply_markup=None)
            elif len(self.alive_players+self.alive_bots)==0:
                self.bot.sendDocument(self.chat_id, open('files/v_dead.gif'), caption="Et bah bravo... Tout le monde est mort", disable_notification=None, reply_to_message_id=None, reply_markup=None)
            else:
                self.bot.sendDocument(self.chat_id, open('files/v_solo.gif'), caption="Fallait pas le lyncher...", disable_notification=None, reply_to_message_id=None, reply_markup=None)
            self.players()
        
        except Exception as e:
            print "error occured"
            print traceback.format_exc()
            self.bot.sendMessage(40831342, traceback.format_exc())
            
            if not self.exception:
                self.bot.sendMessage(self.chat_id, 'Une erreur est survenue, reprise de la partie')
                self.exception=True
                self.launch()
            else:
                self.bot.sendMessage(self.chat_id, 'Nope, ça a servi a rien...')


    def isOver(self):
        if self.launched:
            over=[]
            for p in self.alive_players+self.alive_bots+self.dead_bots+self.dead_players:
                over.append(p.role.winCondition(self, p))
            if (len(self.alive_players)+len(self.alive_bots))==0:
                over.append('Victoire')
            return ('Victoire' in over)
        else:
            return False

    def waitOnResponses(self, maxtime):
        seconds=0
        while (self.nb_reponses<self.nb_expected):
            time.sleep(0.5)
            seconds+=0.5
            if (seconds>=maxtime):
                break


    def handle_response(self, response, from_id):
        self.nb_reponses+=1
        player=None
        choice=None
        for p in (self.alive_players+self.alive_bots+self.dead_players):
                if p.id == from_id:
                    player = p
                if p.id == response:
                    choice = p

        if self.moment == 'firstNight':
            player.role.handle(self, player, choice)
        elif self.moment == 'maire':
            if response != 0:
                choice.vote+=1
        elif self.moment == 'night':
            player.role.handle(self, player, choice)
        elif self.moment == 'night2' or self.moment == 'day':
            if response in [-1,0,1]:
                player.role.handle(self, player, response)
            else:
                player.role.handle(self, player, choice)
        elif self.moment == 'vote':
            if isinstance(player.role, Maladroit):
                if (random.randint(0,1)==1):
                    choice=random.choice(self.alive_players+self.alive_bots)
            if player.maire:
                self.voteM=choice
            if response == 0:
                self.bot.sendMessage(self.chat_id, "%s s'est abstenu..." %player.name)
            else:
                choice.vote+=1
                self.bot.sendMessage(self.chat_id, '%s a voté contre %s' %(player.name,choice.name))
        elif self.moment == 'death':
            player.role.handle(self, player, choice)
            

    def decide(self, player, others, comment):
        if player.isBot() and len(others)>0:
            return random.choice(others)
        else:
            buttons= []
            for choice in others:
                buttons.append([InlineKeyboardButton(text=str(choice.name), callback_data=str(self.chat_id)+' '+str(choice.id))])
            inline = InlineKeyboardMarkup(inline_keyboard=buttons)
            
            if len(buttons)>0:
                self.keyboards.append(telepot.message_identifier(self.bot.sendMessage(player.id, comment, reply_markup=inline)))

    def decisionLoup(self):
        max=0
        rip=[]
        for player in self.alive_players+self.alive_bots:
            if player.vote>max:
                max=player.vote
        if max > 0:
            for player in self.alive_players+self.alive_bots:
                if player.vote == max:
                    rip.append(player)
        self.cleanUp("L'aube se lève...")

        if len(rip)==1:
            if rip[0] is self.protected[0]:
                print 'victime is protected'
                if not self.protected[0].isBot():
                    #self.bot.sendMessage(self.protected[0].id, "La protection d'un être de lumière t'as sauvé la vie cette nuit...")
                    self.bot.sendPhoto(self.protected[0].id, open('files/angel.jpg'),caption="Un être de lumière t'a protégé de l'attaque des loups cette nuit", disable_notification=None, reply_to_message_id=None, reply_markup=None)
                if not self.protected[1].isBot():
                    self.bot.sendMessage(self.protected[1].id, "Tu as sauvé %s cette nuit! GG" %self.protected[0].name)
                for p in self.alive_players:
                    if isinstance(p.role, Loupgarou):
                        self.bot.sendPhoto(p.id, open('files/angel.jpg'),caption="Un être de lumière a empêché la mise à mort de %s"%rip[0].name, disable_notification=None, reply_to_message_id=None, reply_markup=None)
            else:
                print 'not protected'
                if self.protected[0] != None and not self.protected[1].isBot():
                    self.bot.sendMessage(self.protected[1].id, "Tu t'es déplacé en vain... git gud!")
                self.victims.append(rip[0])
                rip[0].death='loup'
        else:
            print 'Loup égalités'
        self.protected=(None, None)

    def decisionSorciere(self):
        self.moment='death'
        for p in self.victims:
            p.role.death(self, p, "est retrouvé mort... du sang a coulé cette nuit")
        if len(self.victims)==0:
            self.bot.sendMessage(self.chat_id, "L'aube se lève sans victime")
        self.cleanUp("L'aube se lève...")
        self.victims=[]

    def voteMaire(self):
        self.moment='maire'

        for player in self.alive_players:
            self.nb_expected+=1
            self.send_keyboard(player, "Élection du maire (scrutin caché)")

        self.waitOnResponses(self.VOTE_TIME)
        self.cleanUp("Élection du maire (scrutin caché) - Trop tard")

        max=0
        maire= []
        for player in self.alive_players:
            if player.vote>max:
                max=player.vote
        for player in self.alive_players:
            if player.vote == max and max > 0:
                maire.append(player)
        if len(maire)!=1:
            elected=random.choice(self.alive_players)
            elected.maire=True
            #self.bot.sendMessage(self.chat_id, "Le village n'arrivant pas à se départager, l'honneur reviendra à %s. Parce que voilà..." %elected.name)
            self.bot.sendDocument(self.chat_id, open('files/maire.mp4'), caption="Le village n'arrivant pas à se départager, l'honneur reviendra à %s. Parce que...\nCE PROJET, C'EST NOTRE PROJET!!!" %elected.name, disable_notification=None, reply_to_message_id=None, reply_markup=None)
        else:
            #self.bot.sendMessage(self.chat_id, 'Le nouveau maire est... %s avec %d voix' %(maire[0].name,maire[0].vote))
            self.bot.sendDocument(self.chat_id, open('files/maireelu.mp4'), caption='Le nouveau maire est... %s avec %d voix' %(maire[0].name,maire[0].vote), disable_notification=None, reply_to_message_id=None, reply_markup=None)
            maire[0].maire=True

    def vote(self, comment):
        self.moment='vote'

        for p in self.alive_bots+self.alive_players:
            p.vote=0

        for player in self.alive_players:
            self.nb_expected+=1
            self.send_keyboard(player, comment)

        bot_votes='Votes des bots:\n'
        for b in self.alive_bots:
            rand=None
            
            others=self.alive_bots+self.alive_players
            others.remove(b)
            if b.lover != None:
                others.remove(b.lover)
            if isinstance(b.role, Loupgarou):
                for o in others:
                    if isinstance(o.role, Loupgarou):
                        others.remove(o)
            
            rand=random.choice(others)
            bot_votes+="• %s a voté contre %s\n"%(b.name,rand.name)
            rand.vote+=1
        if self.nb_bots()>0:
            self.bot.sendMessage(self.chat_id, bot_votes)

        if len(self.alive_players)>0:
            self.waitOnResponses(self.VOTE_TIME)
            self.cleanUp(comment+' - Trop tard')


        max=0
        rip= []
        for player in self.alive_players+self.alive_bots:
            if player.vote>max:
                max=player.vote
        if max > 0:
            for player in self.alive_players+self.alive_bots:
                if player.vote == max:
                    rip.append(player)

        self.moment='death'
        if len(rip)!=1:
            if self.voteM in rip:
                self.voteM.death='vote'
                self.bot.sendMessage(self.chat_id, "Le village n'a pas pu se départager, c'est donc le maire qui fait pencher la balance: %s sera executé!" %self.voteM.name)
                self.voteM.role.death(self, self.voteM, "- victime préférée du maire")
                self.voteM=None
            else:
                self.bot.sendMessage(self.chat_id, 'Pas de lynchage ce soir, il y a égalité...')
        else:
            rip[0].death='vote'
            rip[0].role.death(self, rip[0], '- RIP en paix petit ange 😇')

    def cleanUp(self, comment):
        self.nb_expected=0
        self.nb_reponses=0
        
        for kybrd in self.keyboards:
            self.bot.editMessageReplyMarkup(kybrd, reply_markup=None)
            self.bot.editMessageText(kybrd, comment)
            self.keyboards.remove(kybrd)

    def send_keyboard(self, player, comment):
        buttons= []
        for others in self.alive_players:
            if others is not player:
                buttons.append([InlineKeyboardButton(text=str(others.name), callback_data=str(self.chat_id)+' '+str(others.id))])
        if self.moment!='maire':
            for b in self.alive_bots:
                buttons.append([InlineKeyboardButton(text=str(b.name), callback_data=str(self.chat_id)+' '+str(b.id))])

        buttons.append([InlineKeyboardButton(text="Je m'abstiens", callback_data=str(self.chat_id)+' '+str(0))])

        inline = InlineKeyboardMarkup(inline_keyboard=buttons)
        self.keyboards.append(telepot.message_identifier(self.bot.sendMessage(player.id, comment, reply_markup=inline)))

    def nb_loups(self):
        nb=0
        for p in self.alive_players:
            if isinstance(p.role, Loupgarou):
                nb+=1
        for p in self.alive_bots:
            if isinstance(p.role, Loupgarou):
                nb+=1
        return nb

class Player:
    def __init__(self, role, user_id, name):
        self.role = role
        self.id = user_id
        self.name = name
        self.vote = 0
        self.lover = None
        self.death = None
        self.maire=False
        self.modele=None
        self.copy=None
    def isBot(self):
        return False

class Bot:
    def __init__(self, role, id, name):
        self.role = role
        self.id= id
        self.name = name
        self.vote = 0
        self.lover = None
        self.death = None
        self.maire=False
        self.modele=None
        self.copy=None
    def isBot(self):
        return True
