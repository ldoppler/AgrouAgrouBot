# -*- coding: utf-8 -*-
import time
import random
import telepot
from game import*
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

class Role(object):
    text='Villageois 🙃'

    def __init__ (self):
        self=self

    def firstNight(self, game, me):
        pass

    def atNight(self, game, me):
        pass

    def atNight2(self, game, me):
        pass

    def atDay(self, game, me):
        pass

    def death(self, game, player, comment):
        if player in game.alive_players+game.alive_bots:
            game.bot.sendMessage(game.chat_id, '%s %s' %(player.name, comment))

            if player.isBot():
                game.alive_bots.remove(player)
                game.dead_bots.append(player)
            else:
                game.alive_players.remove(player)
                game.dead_players.append(player)
                if player.death=='loup':
                    game.bot.sendDocument(player.id, open('files/loup.gif'), caption="Tu t'es fait dévorer par les loups... RIP ☠", disable_notification=None, reply_to_message_id=None, reply_markup=None)
                if player.death=='vote':
                    game.bot.sendDocument(player.id, open('files/vote.gif'), caption="Le village ne t'aimait pas spécialement on dirait... RIP ☠", disable_notification=None, reply_to_message_id=None, reply_markup=None)
                if player.death=='love':
                    game.bot.sendDocument(player.id, open('files/love.gif'), caption="L'amour est une terrible chose... RIP ☠", disable_notification=None, reply_to_message_id=None, reply_markup=None)
                if player.death=='chasseur':
                    game.bot.sendDocument(player.id, open('files/hunter.gif'), caption="Le chasseur a visé et a tiré... RIP ☠", disable_notification=None, reply_to_message_id=None, reply_markup=None)
                if player.death=='sorciere':
                    game.bot.sendDocument(player.id, open('files/sorciere.gif'), caption="Tu t'es fait empoisonner par la sorcière... RIP ☠", disable_notification=None, reply_to_message_id=None, reply_markup=None)


            #Enfant sauvage
            if player.modele != None and player.modele in game.alive_players+game.alive_bots:
                player.modele.role=Loupgarou()
                
                all_loups='Tes nouveaux coéquipiers sont: '
                for p in game.alive_players+game.alive_bots:
                    if isinstance(p.role, Loupgarou) and p is not player.modele:
                        if not p.isBot():
                            game.bot.sendMessage(p.id, "%s était l'enfant sauvage, il se transforme en loup et rejoint la meute"%player.modele.name)
                        if all_loups != 'Tes nouveaux coéquipiers sont: ':
                            all_loups += ', '+ p.name
                        else:
                            all_loups += p.name
                if not player.modele.isBot():
                    game.bot.sendMessage(player.modele.id, "Ton modèle %s est décédé...\nTu te transformes en Loup-Garou 🐺"%player.name)
                    game.bot.sendMessage(player.modele.id, all_loups)

            #Copycat
            if player.copy != None and player.copy in game.alive_players+game.alive_bots:
                player.copy.role=player.role
                if not player.copy.isBot():
                    game.bot.sendMessage(player.copy.id,"Tu reprends le rôle de %s"%player.name)
                    game.bot.sendMessage(player.copy.id,player.copy.role.description())


            #amoureux
            if (player.lover != None) and (player.lover in game.alive_players+game.alive_bots):
                player.lover.death='love'
                player.lover.role.death(game, player.lover, 'meurt de chagrin intense...')

            #maire
            if player.maire and len(game.alive_players)>0:
                game.nb_expected+=1
                game.decide(player, game.alive_players, "Qui juges-tu digne de reprendre tes responsabilités de Maire🎖?")
                game.waitOnResponses(game.VOTE_TIME)
                game.cleanUp("Temps écoulé")


    def winCondition(self, game, me): #Condition de victoire classique pour les gentils et lovers
        if me.lover != None:
            if (len(game.alive_players+game.alive_bots) == 2) and (me in game.alive_players+game.alive_bots):
                return 'Victoire'
            else:
                return 'Défaite'
        else:
            if game.nb_loups() == 0 and len(game.alive_players+game.alive_bots)>0:
                return 'Victoire'
            else:
                return 'Défaite'

    def description(self):
        return "Tu n'es rien de spécial mais c'est pas grave :D"

    def handle(self, game, me, choice):
        if me.maire and (me in game.dead_players) and len(game.alive_players)>0:
            choice.maire=True
            me.maire=False
            game.bot.sendMessage(game.chat_id, "%s a annoncé son successeur: %s\nVive le nouveau Maire!🎖" %(me.name, choice.name))
            return False
        return True



class Loupgarou (Role):
    text='Loup-Garou 🐺'
    def __init__ (self):
        self.loups=[]
        self.bots=[]
        self.victim=None

    def atNight(self, game, me):
        self.loups=[]
        self.bots=[]
        if game.noAttack == True:
            if not me.isBot():
                game.bot.sendMessage(me.id, "Le joaillier a répandu de la poussière d'argent cette journée, tu ne peux pas sortir de chez toi cette nuit...")
        else:
            victims=[]
            for p in game.alive_players+game.alive_bots:
                if p is not me:
                    if isinstance(p.role, Loupgarou):  
                        if p in game.alive_players:
                            self.loups.append(p)
                        elif p in game.alive_bots:
                            self.bots.append(p)
                    elif p is not me.lover:
                        victims.append(p)

            choice=game.decide(me, victims, 'Qui souhaites tu dévorer cette nuit?')
            if me.isBot():
                if len(self.loups)>0:
                    for l in self.loups:
                        game.bot.sendMessage(l.id, "%s est un loup"%me.name)
                else:
                    self.handle(game, me, choice)
                    for b in self.bots:
                        b.role.handle(game, b, choice)

    def handle(self, game, me, choice):
        print "[LG] %s veut tuer %s" %(me.name, choice.name)
        if super(Loupgarou, self).handle(game, me, choice):
            if self.victim is not None:
                self.victim.vote=self.victim.vote-1
            choice.vote+=1
            self.victim=choice

            if len(self.loups)>0:
                for loup in self.loups:
                    game.bot.sendMessage(loup.id, '%s veut dévorer %s' %(me.name, choice.name))
                
            if not me.isBot(): #Changement de vote?
                victims=[]
                self.loups=[]
                for p in game.alive_players+game.alive_bots:
                    if p is not me:
                        if isinstance(p.role, Loupgarou):   
                            self.loups.append(p)
                        elif p is not self.victim:
                            victims.append(p)

                game.decide(me, victims, "Veux-tu changer d'avis?")

    def winCondition(self, game, me):
        if me.lover != None:
            return super(Loupgarou, self).winCondition(game, me)
        else:
            if game.nb_loups() == len(game.alive_players+game.alive_bots) and len(game.alive_players+game.alive_bots)>0:
                return 'Victoire'
            else:
                return 'Défaite'

    def description(self):
        return 'Tu es un %s! Agrou agrou\nChaque nuit, tu décideras avec ta meute qui sera votre prochaine victime' %self.text


class Chasseur (Role):
    text='Chasseur 🎯'

    def death(self, game, player, comment):
        super(Chasseur, self).death(game, player, comment)
        vivants = []
        for p in game.alive_players+game.alive_bots:
            if p is not player:
                vivants.append(p)
       
        choice=game.decide(player, vivants, 'A qui veux tu mettre une balle entre les 2 yeux ?')
        if player.isBot():
            self.handle(game, player, choice)
        else:
            game.nb_expected+=1
            game.waitOnResponses(game.VOTE_TIME)
            game.cleanUp("Tu as raté ton tir...")


    def handle(self, game, me, choice):
        if super(Chasseur, self).handle(game, me, choice):
            choice.death='chasseur'
            choice.role.death(game, choice, "meurt d'un tir du chasseur %s rendant son dernier souffle" %me.name)

    def description(self):
        return "Tu es le %s, en mourant tu pourras tuer la personne de ton choix avant de te reposer éternellement"%self.text



class Cupidon (Role):
    text='Cupidon 🏹❤'
    def __init__ (self):
        self.nb_vote=0
        self.lover1=None
        self.lover2=None

    def firstNight(self, game, me):
        self.nb_vote+=1
        if not me.isBot():
            game.nb_expected+=2
        choice=game.decide(me, game.alive_players+game.alive_bots, 'Choix du couple 1/2') #others
        if me.isBot():
            self.handle(game, me, choice)            

    def handle(self, game, me, choice):
        if super(Cupidon, self).handle(game, me, choice):
            if self.nb_vote==1:
                others=game.alive_players+game.alive_bots
                others.remove(choice)
                self.lover1=choice

                self.nb_vote+=1
                choice2=game.decide(me, others, 'Choix du couple 2/2') #others
                if me.isBot():
                    self.handle(game, me, choice2)
                else:
                    game.waitOnResponses(game.VOTE_TIME)
                    game.cleanUp("Tu as raté tes flèches...")

            elif self.nb_vote==2:
                self.lover2=choice
                if not self.lover1.isBot():
                    game.bot.sendMessage(self.lover1.id, 'Ton amour éternel est %s ❤' %self.lover2.name)
                if not self.lover2.isBot():
                    game.bot.sendMessage(self.lover2.id, 'Ton amour éternel est %s ❤' %self.lover1.name)
                self.lover1.lover=self.lover2
                self.lover2.lover=self.lover1

    def description(self):
        return 'Tu es %s! Définis un couple'%self.text

class Voyante(Role):
    text='Voyante 👁'
    def atNight(self, game, me):
        vivants = []
        for p in game.alive_players+game.alive_bots:
            if p is not me:
                vivants.append(p)
        game.nb_expected+=1
        choice=game.decide(me, vivants, 'De qui veux tu connaître le rôle ?')

        if me.isBot():
            msg="%s clame être la Voyante 👁 et dit qu'une des personnes suivantes est %s:\n"%(me.name, choice.role.text)
            
            others=game.alive_players+game.alive_bots
            others.remove(me)
            others.remove(choice)

            choices=[choice]
            if len(others)>0:
                rand1=random.choice(others)
                choices.append(rand1)
                others.remove(rand1)
            if len(others)>0:
                choices.append(random.choice(others))
            random.shuffle(choices)

            for p in choices:
                msg+="• "+p.name+"\n"

            game.bot.sendMessage(game.chat_id, msg)

    def handle(self, game, me, choice):
        if super(Voyante, self).handle(game, me, choice):
            game.bot.sendMessage(me.id, 'Le rôle de %s est %s'  %(choice.name, choice.role.text))

    def description(self):
        return "Tu es la %s! Chaque nuit tu découvriras la véritable identité de la personne de ton choix"%self.text

class Fou(Role):
    text='Fou 🃏👁‍🗨'
    def atNight(self, game, me):
        vivants = []
        for p in game.alive_players+game.alive_bots:
            if p is not me:
                vivants.append(p)
        game.nb_expected+=1
        choice=game.decide(me, vivants, 'De qui veux tu connaître le rôle ?')

        if me.isBot():
            msg="%s clame être la Voyante 👁 et dit qu'une des personnes suivantes est %s:\n"%(me.name, random.choice(game.alive_players+game.alive_bots).role.text)
            
            others=game.alive_players+game.alive_bots
            others.remove(me)
            others.remove(choice)
            
            choices=[choice]
            if len(others)>0:
                rand1=random.choice(others)
                choices.append(rand1)
                others.remove(rand1)
            if len(others)>0:
                choices.append(random.choice(others))
            random.shuffle(choices)

            for p in choices:
                msg+="• "+p.name+"\n"

            game.bot.sendMessage(game.chat_id, msg)

    def handle(self, game, me, choice):
        if super(Fou, self).handle(game, me, choice):
            game.bot.sendMessage(me.id, 'Le rôle de %s est %s'  %(choice.name, random.choice(game.alive_players+game.alive_bots).role.text))

    def description(self):
        return "Tu es la Voyante 👁! Chaque nuit tu découvriras la véritable identité de la personne de ton choix"

class Sorciere(Role):
    text='Sorcière 🔮'
    VIE=-1
    MORT=0
    RIEN=1
    def __init__ (self):
        self.vie=True
        self.mort=True
        self.action=None
    def atNight2(self, game, me):
        if me.isBot():
            rand=random.randint(0,2)
            if self.vie or self.mort:
                if self.vie and len(game.victims)!=0 and rand==0:
                    saved=game.decide(me, game.victims, 'Qui veux-tu sauver?')
                    game.victims.remove(saved)
                    print "%s potion de vie sur %s"%(me.name, saved.name)
                    self.vie=False
                if self.mort and rand==1:
                    kill=[]
                    for p in game.alive_players+game.alive_bots:
                        if p not in game.victims:
                            kill.append(p)
                    victim=game.decide(me, kill, 'Qui veux-tu empoisoner?')
                    game.victims.append(victim)
                    print "%s potion de mort sur %s"%(me.name, victim.name)
                    self.mort=False
        else:
            buttons= []
            if self.vie and len(game.victims)!=0:
                buttons.append([InlineKeyboardButton(text="Potion de vie 💉", callback_data=str(game.chat_id)+' '+str(self.VIE))]) #str(self.chat_id)+' '+str(choice.id))
            if self.mort:
                buttons.append([InlineKeyboardButton(text="Potion de mort 💀", callback_data=str(game.chat_id)+' '+str(self.MORT))])
            buttons.append([InlineKeyboardButton(text="Retourner se coucher 💤", callback_data=str(game.chat_id)+' '+str(self.RIEN))])
            inline = InlineKeyboardMarkup(inline_keyboard=buttons)

            listeVictimes='Liste de victime(s) de cette nuit:\n'
            for p in game.victims:
                if listeVictimes != 'Liste de victime(s) de cette nuit:\n':
                    listeVictimes += ', '+ p.name
                else:
                    listeVictimes += p.name
            if listeVictimes == 'Liste de victime(s) de cette nuit:\n':
                listeVictimes+= 'Pas de victime cette nuit'
            listeVictimes+='\nQue veux-tu faire?'

            if self.vie or self.mort:
                game.nb_expected+=1
                game.keyboards.append(telepot.message_identifier(game.bot.sendMessage(me.id, listeVictimes, reply_markup=inline)))

    def handle(self, game, me, choice):
        if super(Sorciere, self).handle(game, me, choice):
            if choice == self.VIE:
                self.vie=False
                self.action=choice
                game.nb_expected+=1
                game.decide(me, game.victims, 'Qui veux-tu sauver?')
                
            elif choice == self.MORT:
                self.mort=False
                self.action=choice
                game.nb_expected+=1

                kill=[]
                for p in game.alive_players+game.alive_bots:
                    if p not in game.victims:
                        kill.append(p)
                game.decide(me, kill, 'Qui veux-tu empoisoner?')

            elif not choice == self.RIEN:
                if self.action == self.VIE:
                    game.victims.remove(choice)
                if self.action == self.MORT:
                    choice.death='sorciere'
                    game.victims.append(choice)
                self.action=None    
                self.atNight2(game, me)

    def description(self):
        return "Tu es la %s! Tu as deux potions à disposition, une de vie (pour sauver quelqu'un), une de mort (pour empoisonner quelqu'un). Elles ne peuvent être utilisées qu'une seule fois chacune"%self.text

class Maudit (Role):
    text='Maudit 👹'
    def death(self, game, player, comment):
        if player.death=='loup':
            player.role=Loupgarou()
            all_loups='Tes nouveaux coéquipiers sont: '
            for p in game.alive_players+game.alive_bots:
                if isinstance(p.role, Loupgarou) and p is not player :
                    if not p.isBot():
                        game.bot.sendMessage(p.id, "%s était le %s, il se transforme en loup et rejoint la meute"%(player.name,self.text))
                    if all_loups != 'Tes nouveaux coéquipiers sont: ':
                        all_loups += ', '+ p.name
                    else:
                        all_loups += p.name
            if not player.isBot():
                game.bot.sendMessage(player.id, "Les loups t'ont rendu(e) visite cette nuit... Tu as rejoint la meute 🐺\n %s"%all_loups)
        else:
            super(Maudit, self).death(game, player, comment)        

    def description(self):
        return "Tu es le %s, tu es un villageois normal sauf si tu te fait mordre par les loups, dans quel cas tu rejoins leurs rangs 🐺"%self.text


class Ange(Role):
    text = 'Ange Gardien 👼'
    
    def __init__ (self):
        self.protected=None

    def atNight(self, game, me):
        game.nb_expected+=1
    
        others=game.alive_players+game.alive_bots
        if self.protected != None and self.protected in game.alive_players+game.alive_bots:
		    others.remove(self.protected)
        
        choice=game.decide(me, others, 'Qui veux-tu protéger cette nuit?')

        if me.isBot():
            game.nb_expected-=1
            self.handle(game,me,choice)

    def handle(self, game, me, choice):
        if super(Ange, self).handle(game, me, choice):
            game.protected=(choice,me)
            self.protected=choice

    def description(self):
        return "Tu es l'%s! Chaque nuit tu peux protéger un joueur de ton choix qui sera immunisé contre les attaques de loups-garous"%self.text


class Joaillier(Role):
    text = 'Joaillier ✨💍✨'
    NON=0
    OUI=1

    def __init__ (self, nb_poussiere):
        self.nb_poussiere=nb_poussiere

    def atDay(self, game, me):
        if self.nb_poussiere>0:
            if me.isBot():
                if random.randint(0,1)==0:
                    self.handle(game, me, self.OUI)
            else:
                buttons= []
                buttons.append([InlineKeyboardButton(text="Répandre de la poussière ✨ (x%d)" %self.nb_poussiere, callback_data=str(game.chat_id)+' '+str(self.OUI))]) 
                buttons.append([InlineKeyboardButton(text="Pas aujourd'hui...", callback_data=str(game.chat_id)+' '+str(self.NON))])
                inline = InlineKeyboardMarkup(inline_keyboard=buttons)
                game.nb_expected+=1
                game.keyboards.append(telepot.message_identifier(game.bot.sendMessage(me.id, "Veux-tu répandre de la poussière?", reply_markup=inline)))

    def handle(self, game, me, choice):
        if super(Joaillier, self).handle(game, me, choice):
            if choice == self.OUI:
                self.nb_poussiere-=1
                game.noAttack=True
                game.bot.sendDocument(game.chat_id, open('files/silver.gif'), caption="%s, le %s, fait le tour du village et répand de la poussière d'argent. Il n'y aura pas d'attaques des loups cette nuit." %(me.name,self.text), disable_notification=None, reply_to_message_id=None, reply_markup=None)
                #game.bot.sendMessage(game.chat_id, "%s, le %s, fait le tour du village et répand de la poussière d'argent. Il n'y aura pas d'attaques des loups cette nuit." %(me.name,self.text))

    def description(self):
        return "Tu es le %s! Tu peux disperser les restes de poudre d'argent de ton atelier ce qui empêchera les loups d'attaquer la nuit suivante."%self.text


class Juge(Role):
    text = 'Juge 🎓'
    NON=0
    OUI=1

    def __init__ (self):
        self.extraVote=True

    def atDay(self, game, me):
        if self.extraVote:
            if me.isBot():
                if random.randint(0,1)==0:
                    self.handle(game, me, self.OUI)

            else:
                buttons= []
                buttons.append([InlineKeyboardButton(text="Oui", callback_data=str(game.chat_id)+' '+str(self.OUI))]) 
                buttons.append([InlineKeyboardButton(text="Pas aujourd'hui...", callback_data=str(game.chat_id)+' '+str(self.NON))])
                inline = InlineKeyboardMarkup(inline_keyboard=buttons)
                game.nb_expected+=1
                game.keyboards.append(telepot.message_identifier(game.bot.sendMessage(me.id, "Veux-tu enclencher un double vote?", reply_markup=inline)))

    def handle(self, game, me, choice):
        if super(Juge, self).handle(game, me, choice):
            if choice == self.OUI:
                self.extraVote=False
                game.doubleVote=True
                game.bot.sendDocument(game.chat_id, open('files/juge.gif'), caption="%s, le %s, avance sur la place du village et déclare qu'il y aura deux votes aujourd'hui!" %(me.name,self.text), disable_notification=None, reply_to_message_id=None, reply_markup=None)
                #game.bot.sendMessage(game.chat_id, "%s, le %s, avance sur la place du village et déclare qu'il y aura deux votes aujourd'hui!" %(me.name,self.text))

    def description(self):
        return "Tu es le %s! Tu peux enclencher un double-vote le jour de ton choix. Ce pouvoir est à usage unique et dévoilera ton rôle aux autres villageois"%self.text

class Emo(Role):
    text = 'Emo 👨‍🎤'

    def winCondition(self, game, me):
        if me.lover != None:
            return super(Emo, self).winCondition(game, me)
        else:
            if me.death=='vote':
                return 'Victoire'
            else:
                return 'Défaite'

    def description(self):
        return "Tu es l'%s! Tu détestes tout le monde, ton unique but est de te faire lyncher par le village, si tu réussis, tu gagnes!"%self.text

class Maladroit(Role):
    text = 'Maladroit 🤕'

    def description(self):
        return "Tu es le %s! Tu es vraiment pas doué et tes votes ont une chance sur deux de finir sur quelqu'un d'autre...!"%self.text

class EnfantSauvage(Role):
    text='Enfant sauvage 🌲🚼🌲'

    def firstNight(self, game, me):
        others=game.alive_players+game.alive_bots
        others.remove(me)
        choice=game.decide(me, others, 'Qui est ce modèle?')
        if me.isBot():
            self.handle(game, me, choice)
        else:
            game.nb_expected+=1
            game.waitOnResponses(game.VOTE_TIME)
            game.cleanUp("Trop tard...")          

    def handle(self, game, me, choice):
        print "%s modèle de l'enfant sauvage %s"%(choice.name,me.name)
        if super(EnfantSauvage, self).handle(game, me, choice):
            choice.modele=me

    def description(self):
        return "Tu es l'%s! Tu as grandi dans la forêt sauvage au milieu des animaux, tu es incertain de vouloir vivre en société... Un être plein de bonté t'a tout offert et t'a permis une intégration parfaite dans le village.\nSi cette personne venait à mourir, ton chagrin serait si grand que toute ta jeunnesse sauvage reviendra à la surface et tu te transformeras en Loup-Garou 🐺"%self.text

class Copycat(Role):
    text='Copycat 🎭😼'

    def firstNight(self, game, me):
        others=game.alive_players+game.alive_bots
        others.remove(me)
        choice=game.decide(me, others, 'Le rôle de qui veux-tu incarner après sa mort?')
        if me.isBot():
            self.handle(game, me, choice)
        else:
            game.nb_expected+=1
            game.waitOnResponses(game.VOTE_TIME)
            game.cleanUp("Trop tard...")          

    def handle(self, game, me, choice):
        print "%s sera emplacé par %s"%(choice.name,me.name)
        if super(Copycat, self).handle(game, me, choice):
            choice.copy=me

    def description(self):
        return "Tu es le %s! Au début de la partie, tu pourras choisir quelqu'un et lors de la mort de cette personne, tu prendras son rôle."%self.text

class Idiot (Role):
    text='Idiot du village 😲'

    def __init__ (self):
        self.firstTime=True

    def death(self, game, player, comment):
        if player.death=='vote' and self.firstTime:
            game.bot.sendMessage(game.chat_id, "%s est l'%s... Tout le monde a honte de le tuer juste parce qu'il est stupide, il sera gracié... cette fois..."%(player.name,self.text))
            self.firstTime=False
        else:
            super(Idiot, self).death(game, player, comment)        

    def description(self):
        return "Tu es l'%s, les villageois te gracieront si tu te fais lyncher au vote (une seule fois)"%self.text
