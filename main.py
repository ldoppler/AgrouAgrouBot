# -*- coding: utf-8 -*-
import time
import sys
import os
import telepot
import random
import thread
import unicodedata
from game import Game
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

games = []
reboot=False

def on_chat_message(msg):
    chat_id = msg['chat']['id']
    user_id = msg['from']['id']
    name = msg['from']['first_name']
    command = msg['text']


    print 'Got command: %s' % command

    if command == '/startgame' or command == '/startgame@AgrouAgrouBot':
        game = isGame(chat_id)
        if game:
            if game.isOver():
                games.remove(game)
                try:
                    games.append(Game(bot, chat_id, user_id, name))
                    bot.sendMessage(chat_id, 'Partie créée')
                except telepot.exception.TelepotException:
                    bot.sendMessage(chat_id, 'Il faut ouvrir un chat privé avec @AgrouAgrouBot avant de rejoindre une partie')
            else:
                bot.sendMessage(chat_id, 'Déjà une partie en cours')
        else:
            try:
                games.append(Game(bot, chat_id, user_id, name))
                bot.sendMessage(chat_id, 'Partie créée')
            except telepot.exception.TelepotException:
                bot.sendMessage(chat_id, 'Il faut ouvrir un chat privé avec @AgrouAgrouBot avant de rejoindre une partie')
        print games

    elif command == '/cancelgame' or command == '/cancelgame@AgrouAgrouBot':
        game = isGame(chat_id)
        if game:
            games.remove(game)
            bot.sendMessage(chat_id, 'Partie annulée')
        else:
            bot.sendMessage(chat_id, 'Pas de partie à annuler...')

        print games

    elif command == '/join' or command == '/join@AgrouAgrouBot':
        game = isGame(chat_id)
        if game:
            try:
                game.add_player(user_id, name)
                if user_id in game.ids:
                    bot.sendMessage(user_id, "Tu as rejoint la partie")
            except telepot.exception.TelepotException:
                bot.sendMessage(chat_id, 'Il faut ouvrir un chat privé avec @AgrouAgrouBot avant de rejoindre une partie')
        else:
            bot.sendMessage(chat_id, 'Pas de partie à rejoindre, merci de /startgame...')

    elif command == '/leave' or command == '/leave@AgrouAgrouBot':
        game = isGame(chat_id)
        if game:
            game.remove_player(user_id)
        else:
            bot.sendMessage(chat_id, 'Pas de partie à quitter...')

    elif command =='/launch' or command == '/launch@AgrouAgrouBot':
        game = isGame(chat_id)
        if game:
            if (user_id==game.ids[0]):
                try:
                    thread.start_new_thread(Game.launch, (game,))

                    bot.sendMessage(chat_id, 'Lancement de la partie')
                except:
                    bot.sendMessage(chat_id, 'Une erreur est subvenue... Si nécessaire utiliser /kill')
            else:
                bot.sendMessage(chat_id, "%s doit lancer la partie"%game.names[0])
        else:
            bot.sendMessage(chat_id, 'Pas de partie à lancer...')

    elif command == '/players' or command == '/players@AgrouAgrouBot':
        game = isGame(chat_id)
        if game:
            game.players()


    elif command == '/addbot' or command == '/addbot@AgrouAgrouBot':
        game = isGame(chat_id)
        if game:
            game.add_bot()
        else:
            bot.sendMessage(chat_id, "Il faut créer une partie avant d'ajouter des bots")

    elif command == '/removebot' or command == '/removebot@AgrouAgrouBot':
        game = isGame(chat_id)
        if game:
            game.remove_bot()
        else:
            bot.sendMessage(chat_id, "...")

    elif command == '/kill' or command == '/kill@AgrouAgrouBot':
        game = isGame(chat_id)
        if game:
            game.kill()
            bot.sendMessage(chat_id, 'Tout le monde a été tué :D')
            games.remove(game)
            
    elif command == '/ping' or command == '/ping@AgrouAgrouBot':
        game = isGame(chat_id)
        if game:
            bot.sendMessage(chat_id, '%s - Cycle n°%d'%(game.moment, game.day))
    
    elif command == '/reboot' or command == '/reboot@AgrouAgrouBot':
        if user_id==40831342:
            bot.sendMessage(chat_id, "Restarting...")
            time.sleep(2)
            bot.sendMessage(chat_id, "Done!")
            os.execv(sys.executable, ['python'] + sys.argv)
        else:
            bot.sendMessage(chat_id, "Merci de demander à @limegreen de le faire")
            
    elif command == '/pls' or command == '/pls@AgrouAgrouBot' or command == '/PLS' or command == '/PLS@AgrouAgrouBot':
        bot.sendPhoto(chat_id, open('files/pls.jpg'), caption="PLS LICORNE!")
        
    elif command == '/wtf' or command == '/wtf@AgrouAgrouBot' or command == '/WTF' or command == '/WTF@AgrouAgrouBot':
        bot.sendDocument(chat_id, open('files/wtf.mp4'))

    elif command == '/ah' or command == '/ah@AgrouAgrouBot':
        bot.sendVoice(chat_id, open('files/ah.mp3'))
        
    elif command == '/dab' or command == '/dab@AgrouAgrouBot':
        nb=random.randint(1,13)
        if nb==1:
            bot.sendDocument(chat_id, open('files/dab/dab1.mp4'))
        elif nb==2:
            bot.sendDocument(chat_id, open('files/dab/dab2.mp4'))
        elif nb==3:
            bot.sendDocument(chat_id, open('files/dab/dab3.mp4'))
        elif nb==4:
            bot.sendDocument(chat_id, open('files/dab/dab4.mp4'))
        elif nb==5:
            bot.sendDocument(chat_id, open('files/dab/dab5.mp4'))
        elif nb==6:
            bot.sendDocument(chat_id, open('files/dab/dab6.mp4'))
        elif nb==7:
            bot.sendDocument(chat_id, open('files/dab/dab7.mp4'))
        elif nb==8:
            bot.sendDocument(chat_id, open('files/dab/dab8.mp4'))
        elif nb==9:
            bot.sendDocument(chat_id, open('files/dab/dab9.mp4'))
        elif nb==10:
            bot.sendDocument(chat_id, open('files/dab/dab10.mp4'))
        elif nb==11:
            bot.sendDocument(chat_id, open('files/dab/dab11.mp4'))
        elif nb==12:
            bot.sendDocument(chat_id, open('files/dab/dab12.mp4'))
        elif nb==13:
            bot.sendDocument(chat_id, open('files/dab/dab13.mp4'))
            
    elif command == '/delayvote' or command == '/delayvote@AgrouAgrouBot':
        game = isGame(chat_id)
        if game:
            if game.delayvote:
                game.delayvote=False
                bot.sendMessage(chat_id, "Délai avant le vote desactivé")
            else:
                game.delayvote=True
                bot.sendMessage(chat_id, 'Délai avant le vote activé')
        else:
            bot.sendMessage(chat_id, "Il faut d'abord démarrer une partie avec /startgame, ensuite on peut utiliser /delayvote")
        
    #elif command == '/html' or command == '/html@AgrouAgrouBot':
        #bot.sendMessage(parse_mode='Markdown',chat_id=chat_id, text='*gras* normal')
                
    elif command == '/update' or command == '/update@AgrouAgrouBot':
        update="*28/03/2017*\n• Correction du bug empêchant plusieurs parties d'être jouées en même temps sur différents groupes\n• Temps pour prendre des décisions réduit de 25 à 20 secondes\n\n"
        update+="*29/03/2017*\n• Augmentation du temps entre les différents moments de la partie (votes, nuits, etc) pour permettre un suivi plus facile du jeu\n• Changement du gif pour l'élection du maire à la majorité\n• Modifs non visibles sur la gestion d'une partie terminée et le relancement d'une nouvelle\n• IA des bots: les bots loups ne votent (de jour) plus contre les autres loups\n• Correction de bugs mineurs sur l'Ange Gardien\n• Correction d'un bug avec le maire humain mort et que des bots restants, le dernier vote du maire faussait les votes\n• Ajout de /ah, /wtf et /pls parce que voilà :D\n\n"
        update+="*30/03/2017*\n• Correction de l'envoi du message envoyé en privé sur un /join d'une partie déjà lancée\n• Mise en place de la reprise d'une partie en cas d'erreur Python (à tester)\n• Ajout de la commande /delayvote pour activer un délai avant les votes pour lancer des accusations. Est désactivé par défaut et doit être activé à chaque partie. Réappeler la commande une deuxième fois désactive l'option\n\n"
        update+="*12/05/2017*\n• Ajout du /dab pour célébrer sa victoire correctement\n• La gestion d'erreur ne génère plus d'erreur elle-même, il y a donc une chance qu'une partie reprenne après avoir planté (sans garantie...)"
        bot.sendMessage(parse_mode='Markdown',chat_id=chat_id, text=update)

def on_callback_query(msg):
    msg_identifier=telepot.origin_identifier(msg)
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

    print 'got callback: %r' %query_data
    query_data=unicodedata.normalize('NFKD',query_data).encode('ascii','ignore')
    vote_id=''
    chat_id=''
    for char in query_data:
        if char == ' ':
            chat_id=vote_id
            vote_id=''
        else:
            vote_id+=str(char)
    game=isGame(int(chat_id))
    vote_id=int(vote_id)
    from_id=int(from_id)

    if vote_id not in [-1,0,1] and game:
        bot.answerCallbackQuery(query_id, text=game.name_of(vote_id))
    
    bot.editMessageReplyMarkup(msg_identifier, reply_markup=None) #delete inline keyboard
    if vote_id not in [-1,0,1]:
        bot.editMessageText(msg_identifier, 'Choix: %s'%game.name_of(vote_id))
    game.keyboards.remove(msg_identifier)
    thread.start_new_thread(Game.handle_response, (game, vote_id, from_id))

bot = telepot.Bot('PUT_YOUR_TOKEN_HERE')
bot.message_loop({'chat': on_chat_message,'callback_query': on_callback_query})
print 'I am listening ...'

def isGame(chat_id):
    for game in games:
            if chat_id==game.chat_id:
                return game
    return False

while 1:
    for g in games:
        if g.isOver():
            games.remove(g)
    time.sleep(5)
