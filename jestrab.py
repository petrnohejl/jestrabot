#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Jestrabot

Copyright (C)2007 Petr Nohejl, jestrab.net

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

This program comes with ABSOLUTELY NO WARRANTY!
"""

# IRC HELP: http://www.irchelp.org/irchelp/misc/ccosmos.html
# IRC COMMANDS: NICK, USER, JOIN, PING, PRIVMSG, ACTION, NOTICE, MODE, QUIT
# TODO: vyjimky, korektni konec, admin prikazy na query, ping timeout vyhodi program!, kod rozdelit do modulu, vykoumat .pyc
# http://git.nomi.cz/?p=mars/ircbot;a=blobdiff;f=modules/usefull.py;h=3ffbd68c6d4befc1928d6be10ac00342669f205d;hp=b9fc0118e556098f4290a17c43e88b4f0af506bb;hb=71c5182dc11e4fd951cf7633c5412a340dd2ade4;hpb=b0cde73e12486a37395cbe450f59cd1e2ebde9b3

import socket
import string
import time
import random
import re
import cPickle

# GLOBALNI PROMENNE A KONSTANTY ################################################

network = "irc.felk.cvut.cz"	# adresa serveru
port = 6667						# port
channel = "#botnik"				# kanal
name = "Jestrab"				# jmeno bota
prefix = "-"					# prefix prikazu
log_out = 1						# vypis logu pri odesilani zprav
log_in = 0						# vypis logu pri ziskavani zprav
admin = "peno"					# nick spravce - pouzito u prikazu die
runtime = int(time.time())		# casova znamka pri spusteni bota - pouzito u prikazu flytime

# PRIVMSG ######################################################################

def irc_privmsg(text):
	irc.send ( "PRIVMSG " + channel + " :" + text + "\r\n" )
	if log_out == 1:
		print "LOG_OUT: PRIVMSG " + channel + " :" + text
	return 0
	
# CONNECT ######################################################################

def connect():
	print "STATUS:  Vypoustim Jestraba..."
	irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
	irc.connect ( ( network, port ) )
	
	irc.send ( "NICK " + name + "\r\n" )
	if log_out == 1:
		print "LOG_OUT: NICK " + name
	
	irc.send ( "USER " + name + " " + name + " " + name + " :" + name + "\r\n" )
	if log_out == 1:
		print "LOG_OUT: USER " + name + " " + name + " " + name + " :" + name
	
	irc.send ( "JOIN " + channel + "\r\n" )
	if log_out == 1:
		print "LOG_OUT: JOIN " + channel
	
	print "STATUS:  Jestrab leti..."
	print "------------------------------------------------------------------------------------------"
	return irc

# LISTEN #######################################################################

def listen():
	while True:
		data = irc.recv ( 4096 )														# ziskana data ve tvaru :Nick!user@host PRIVMSG destination :Message
		
		if log_in == 1:																	# kontrolni vypis ziskanych dat
			print "LOG_IN:  " + string.rstrip(data)
		
		if data.find ( "PING" ) != -1:													# osetreni ping timeout
			irc.send ( "PONG " + data.split() [ 1 ] + "\r\n" )
			if log_out == 1:
				print "LOG_OUT: PONG " + data.split() [ 1 ]

		if data.find ( "PRIVMSG" ) != -1:
			nick = data.split ( "!" ) [ 0 ].replace ( ":", "" )							# nick odesilatele
			destination = "".join ( data.split ( ":" ) [ :2 ] ).split ( " " ) [ -2 ]	# nick prijemce
			message = ":".join ( data.split ( ":" ) [ 2: ] )							# zprava
			message = message.strip()													# osetreni bilych znaku
			if do(nick, destination, message) != 0:										# zpracovani ziskanych dat
				break
				
		elif data.find ( "JOIN" ) != -1:
			nick = data.split ( "!" ) [ 0 ].replace ( ":", "" )							# nick odesilatele													# osetreni bilych znaku
			if nick.find ( name ) == -1:
				irc_privmsg(nick + ": Bud vitan " + nick + "!")
			
	return 0

# DO ###########################################################################

def do(nick, destination, message):
	
	message_cs = message				# case sensitive message
	message = message.lower()			# non case sensitive message
	
	# AI #######################################################################
	
	if (message.find(name.lower() + ": ") != -1) and (message.find("ahoj") != -1):
		irc_privmsg(nick + ": Ahoj " + nick + "!")
		
	if (message.find(name.lower() + ": ") != -1) and (message.find("jak se mas") != -1):
		irc_privmsg(nick + ": Mam se bajecne!")
		
	# CMD ######################################################################
	
	re_help = re.compile(r"^" + prefix + r"help.*$")
	if re_help.search(message):
		cmd_help(message)
		
	re_man = re.compile(r"^" + prefix + r"man.*$")
	if re_man.search(message):
		cmd_help(message)

	if message == prefix + "info":
		cmd_info()

	if message == prefix + "flytime":
		cmd_flytime()

	re_topic1 = re.compile(r"^" + prefix + r"topic .+$")
	re_topic2 = re.compile(r"" + prefix + r"[tT][oO][pP][iI][cC] ")
	if re_topic1.search(message):
		cmd_topic(re_topic2.sub("", message_cs))

	if message == prefix + "time":
		cmd_time()
	
	re_nameday1 = re.compile(r"^" + prefix + r"nameday.*$")
	re_nameday2 = re.compile(r"" + prefix + r"[nN][aA][mM][eE][dD][aA][yY]")
	if re_nameday1.search(message):
		cmd_nameday(re_nameday2.sub("", message_cs).strip())
	
	re_slap1 = re.compile(r"^" + prefix + r"slap .+$")
	re_slap2 = re.compile(r"" + prefix + r"[sS][lL][aA][pP] ")
	if re_slap1.search(message):
		cmd_slap(re_slap2.sub("", message_cs))

	if message == prefix + "die":
		if (cmd_die(nick) != 0):
			return 1
		
	return 0

# FUNCTIONS ####################################################################
################################################################################
################################################################################

# SALUTE #######################################################################

def salute():
	daytime = time.localtime()
	if (daytime[3] >= 0) and (daytime[3] <= 5):
		salute = "Bdelou noc"
	elif (daytime[3] >= 6) and (daytime[3] <= 8):
		salute = "Svezi rano"
	elif (daytime[3] >= 9) and (daytime[3] <= 10):
		salute = "Hezke dopoledne"
	elif (daytime[3] >= 11) and (daytime[3] <= 12):
		salute = "Pekne poledne"
	elif (daytime[3] >= 13) and (daytime[3] <= 16):
		salute = "Bre odpoledne"
	elif (daytime[3] >= 17) and (daytime[3] <= 19):
		salute = "Prijemny podvecer"
	elif (daytime[3] >= 20) and (daytime[3] <= 23):
		salute = "Dobreho vecera"
	irc_privmsg(salute + " vam preji!")
	return 0

# CMD_HELP #####################################################################

def cmd_help(message):
	if (message == prefix + "help help") or (message == prefix + "man help"):
		irc_privmsg(prefix + "help [prikaz] -> zobrazi seznam podporovanych prikazu, resp. napovedu k danemu prikazu")
	if (message == prefix + "help man") or (message == prefix + "man man"):
		irc_privmsg(prefix + "man [prikaz] -> zobrazi seznam podporovanych prikazu, resp. napovedu k danemu prikazu")
	elif (message == prefix + "help info") or (message == prefix + "man info"):
		irc_privmsg(prefix + "info -> zobrazi podrobne informace o botovi")
	elif (message == prefix + "help flytime") or (message == prefix + "man flytime"):
		irc_privmsg(prefix + "flytime -> zobrazi dobu behu bota")
	elif (message == prefix + "help topic") or (message == prefix + "man topic"):
		irc_privmsg(prefix + "topic (text) -> zmeni tema")
	elif (message == prefix + "help stats") or (message == prefix + "man stats"):
		irc_privmsg(prefix + "stats [nick] -> zobrazi statistiky uzivatele")
	elif (message == prefix + "help top") or (message == prefix + "man top"):
		irc_privmsg(prefix + "top -> zobrazi statistiky nejukecanejsich uzivatelu")
	elif (message == prefix + "help seen") or (message == prefix + "man seen"):
		irc_privmsg(prefix + "seen (nick) -> zobrazi kdy naposledy promluvil dany uzivatel a co rekl")
	elif (message == prefix + "help host") or (message == prefix + "man host"):
		irc_privmsg(prefix + "host (domena) -> zobrazi IP a domenove jmeno dane domeny")
	elif (message == prefix + "help google") or (message == prefix + "man google"):
		irc_privmsg("")
	elif (message == prefix + "help lastfm") or (message == prefix + "man lastfm"):
		irc_privmsg("")
	elif (message == prefix + "help weather") or (message == prefix + "man weather"):
		irc_privmsg("")
	elif (message == prefix + "help time") or (message == prefix + "man time"):
		irc_privmsg(prefix + "time -> zobrazi cas a datum")
	elif (message == prefix + "help nameday") or (message == prefix + "man nameday"):
		irc_privmsg(prefix + "nameday [jmeno | datum] -> zobrazi kdo ma dnes svatek, resp. zobrazi kdy ma dane jmeno svatek nebo kdo ma v dany den svatek, datum se zadava ve tvaru den.mesic., priklad pouziti: " + prefix + "nameday, " + prefix + "nameday Petr, " + prefix + "nameday 29.6.")
	elif (message == prefix + "help acro") or (message == prefix + "man acro"):
		irc_privmsg("")
	elif (message == prefix + "help wordgen") or (message == prefix + "man wordgen"):
		irc_privmsg(prefix + "wordgen [delka] [vzor] -> nahodne vygeneruje slovo, delka se zadava ve tvaru min:max, vzor tvori pismena ktera ma slovo obsahovat a *, vyjadrujici libovolne dlouhy retezec, priklad pouziti: " + prefix + "wordgen 6:10 *er*man")
	elif (message == prefix + "help passgen") or (message == prefix + "man passgen"):
		irc_privmsg("")
	elif (message == prefix + "help cz2en") or (message == prefix + "man cz2en"):
		irc_privmsg(prefix + "cz2en (slovo) -> cesko - anglicky slovnik")
	elif (message == prefix + "help en2cz") or (message == prefix + "man en2cz"):
		irc_privmsg(prefix + "en2cz (slovo) -> anglicko - cesky slovnik")
	elif (message == prefix + "help calc") or (message == prefix + "man calc"):
		irc_privmsg("")
	elif (message == prefix + "help ascii") or (message == prefix + "man ascii"):
		irc_privmsg(prefix + "ascii (znak) -> zobrazi ordinalni hodnotu daneho ascii znaku")
	elif (message == prefix + "help bin2dec") or (message == prefix + "man bin2dec"):
		irc_privmsg(prefix + "bin2dec (cislo) -> prevede cislo z binarni soustavy do desitkove")
	elif (message == prefix + "help dec2bin") or (message == prefix + "man dec2bin"):
		irc_privmsg(prefix + "dec2bin (cislo) -> prevede cislo z desitkove soustavy do binarni")
	elif (message == prefix + "help joke") or (message == prefix + "man joke"):
		irc_privmsg("")
	elif (message == prefix + "help hangman") or (message == prefix + "man hangman"):
		irc_privmsg("")
	elif (message == prefix + "help punish") or (message == prefix + "man punish"):
		irc_privmsg("")
	elif (message == prefix + "help slap") or (message == prefix + "man slap"):
		irc_privmsg("")
	elif (message == prefix + "help add") or (message == prefix + "man add"):
		irc_privmsg("")
	elif (message == prefix + "help del") or (message == prefix + "man del"):
		irc_privmsg("")
	elif (message == prefix + "help ???") or (message == prefix + "man ???"):
		irc_privmsg("")
	else:
		irc_privmsg("help | man, info, flytime, topic, stats, top, seen, host, google, lastfm, weather, time, nameday, acro, wordgen, passgen, cz2en, en2cz, calc, ascii, bin2dec, dec2bin, joke, hangman, punish, slap, add, del, ???")
	return 0
	
# CMD_INFO #####################################################################

def cmd_info():
	irc_privmsg("IRC BOT \x02Jestrab\x02: Copyright (c)2007 Petr Nohejl, \x02http://jestrab.net\x02, powered by Python")
	return 0
	
# CMD_FLYTIME ##################################################################

def cmd_flytime():
	import time
	act_runtime = int(time.time()) - runtime
	act_runtime_day = (act_runtime % 31104000) / 86400
	act_runtime_hour = (act_runtime % 86400) / 3600
	act_runtime_min = (act_runtime % 3600) / 60
	act_runtime_sec = act_runtime % 60
	if (act_runtime_min == 0) and (act_runtime_hour == 0) and (act_runtime_day == 0):
		irc_privmsg("Litam teprve " + str(act_runtime_sec) + " sekund" )
	elif (act_runtime_hour == 0) and (act_runtime_day == 0):
		irc_privmsg("Litam teprve " + str(act_runtime_min) + " minut a " + str(act_runtime_sec) + " sekund" )
	elif (act_runtime_day == 0):
		irc_privmsg("Litam uz " + str(act_runtime_hour) + " hodin, " + str(act_runtime_min) + " minut, " + str(act_runtime_sec) + " sekund" )
	else:
		irc_privmsg("Litam uz " + str(act_runtime_day) + " dnu, " + str(act_runtime_hour) + " hodin, " + str(act_runtime_min) + " minut, " + str(act_runtime_sec) + " sekund" )
	return 0

# CMD_TOPIC ####################################################################

def cmd_topic(text):
	irc.send ( "TOPIC " + channel + " :" + text + "\r\n" )
	if log_out == 1:
		print "LOG_OUT: TOPIC " + channel + " :" + text
	return 0

# CMD_TIME #####################################################################

def cmd_time():
	import time
	weeknumber = time.strftime("%W", time.gmtime())
	time = time.localtime()
	weekday_list = {0:"pondeli",1:"utery",2:"streda",3:"ctvrtek",4:"patek",5:"sobota",6:"nedele"}
	month_list = {1:"ledna",2:"unora",3:"brezna",4:"dubna",5:"kvetna",6:"cervna",7:"cervence",8:"srpna",9:"zari",10:"rijna",11:"listopadu",12:"prosince"}
	if len(str(time[4])) == 1:
		minutes = "0" + str(time[4])
	else:
		minutes = str(time[4])
	irc_privmsg(str(time[3]) + ":" + minutes + ", " + weekday_list[time[6]] + " " + str(time[2]) + ". " + month_list[time[1]] + " " + str(time[0]) + ", " + weeknumber + ". tyden, " + str(time[7]) + ". den v roce" )
	return 0
	
# CMD_NAMEDAY ##################################################################

def cmd_nameday(argument):
	import time
	time = time.localtime()
	month_list = {1:"ledna",2:"unora",3:"brezna",4:"dubna",5:"kvetna",6:"cervna",7:"cervence",8:"srpna",9:"zari",10:"rijna",11:"listopadu",12:"prosince"}
	nameday = [ \
	["Nový rok","Karina","Radmila","Diana","Dalimil","Tři králové","Vilma","Čestmír","Vladan","Břetislav","Bohdana","Pravoslav","Edita","Radovan","Alice","Ctirad","Drahoslav","Vladislav","Doubravka","Ilona","Běla","Slavomír","Zdeněk","Milena","Miloš","Zora","Ingrid","Otýlie","Zdislava","Robin","Marika"], \
	["Hynek","Nela","Blažej","Jarmila","Dobromila","Vanda","Veronika","Milada","Apolena","Mojmír","Božena","Slavěna","Věnceslav","Valentýn","Jiřina","Ljuba","Miloslava","Gizela","Patrik","Oldřich","Lenka","Petr","Svatopluk","Matěj","Liliana","Dorota","Alexandr","Lumír","Horymír"], \
	["Bedřich","Anežka","Kamil","Stela","Kazimir","Miroslav","Tomáš","Gabriela","Františka","Viktorie","Anděla","Řehoř","Růžena","Růt a Matylda","Ida","Elena a Herbert","Vlastimil","Eduard","Josef","Světlana","Radek","Leona","Ivona","Gabriel","Marian","Emanuel","Dita","Soňa","Taťána","Arnošt","Kvido"], \
	["Hugo","Erika","Richard","Ivana","Miroslava","Vendula","Heřman a Hermína","Ema","Dušan","Darja","Izabela","Julius","Aleš","Vincenc","Anastázie","Irena","Rudolf","Valérie","Rostislav","Marcela","Alexandra","Evženie","Vojtěch","Jiří","Marek","Oto","Jaroslav","Vlastislav","Robert","Blahoslav"], \
	["Svátek práce","Zikmund","Alexej","Květoslav","Klaudie","Radoslav","Stanislav","Den osvobozeni","Ctibor","Blažena","Svatava","Pankrác","Servác","Bonifác","Žofie","Přemysl","Aneta","Nataša","Ivo","Zbyšek","Monika","Emil","Vladimír","Jana","Viola","Filip","Valdemar","Vilém","Maxmilián","Ferdinand","Kamila"], \
	["Laura","Jarmil","Tamara","Dalibor","Dobroslav","Norbert","Iveta a Slavoj","Medard","Stanislava","Gita","Bruno","Antonie","Antonín","Roland","Vít","Zbyněk","Adolf","Milan","Leoš","Květa","Alois","Pavla","Zdeňka","Jan","Ivan","Adriana","Ladislav","Lubomír","Petr a Pavel","Šárka"], \
	["Jaroslava","Patricie","Radomír","Prokop","Cyril a Metoděj","Mistr Jan Hus","Bohuslava","Nora","Drahoslava","Libuše a Amálie","Olga","Bořek","Markéta","Karolína","Jindřich","Luboš","Martina","Drahomíra","Čeněk","Ilja","Vítězslav","Magdaléna","Libor","Kristýna","Jakub","Anna","Věroslav","Viktor","Marta","Bořivoj","Ignác"], \
	["Oskar","Gustav","Miluše","Dominik","Kristian","Oldřiška","Lada","Soběslav","Roman","Vavřinec","Zuzana","Klára","Alena","Alan","Hana","Jáchym","Petra","Helena","Ludvík","Bernard","Johana","Bohuslav","Sandra","Bartoloměj","Radim","Luděk","Otakar","Augustýn","Evelína","Vladěna","Pavlína"], \
	["Linda a Samuel","Adéla","Bronislav","Jindřiška","Boris","Boleslav","Regína","Mariana","Daniela","Irma","Denisa","Marie","Lubor","Radka","Jolana","Ludmila","Naděžda","Kryštof","Zita","Oleg","Matouš","Darina","Berta","Jaromír","Zlata","Andrea","Jonáš","Václav","Michal","Jeroným"], \
	["Igor","Olivie a Oliver","Bohumil","František","Eliška","Hanuš","Justýna","Věra","Štefan a Sára","Marina","Andrej","Marcel","Renáta","Agáta","Tereza","Havel","Hedvika","Lukáš","Michaela","Vendelín","Brigita","Sabina","Teodor","Nina","Beáta","Erik","Šarlota a Zoe","Den vzniku samostatného československého státu","Silvie","Tadeáš","Štěpánka"], \
	["Felix","Památka zesnulých","Hubert","Karel","Miriam","Liběna","Saskie","Bohumír","Bohdan","Evžen","Martin","Benedikt","Tibor","Sáva","Leopold","Otmar","Mahulena, Den boje za svobodu a demokracii","Romana","Alžběta","Nikola","Albert","Cecílie","Klement","Emílie","Kateřina","Artur","Xenie","René","Zina","Ondřej"], \
	["Iva","Blanka","Svatoslav","Barbora","Jitka","Mikuláš","Ambrož a Benjamín","Květoslava","Vratislav","Julie","Dana","Simona","Lucie","Lýdie","Radana a Radan","Albína","Daniel","Miloslav","Ester","Dagmar","Natálie","Šimon","Vlasta","Adam a Eva","Boží hod vánoční","Štěpán","Žaneta","Bohumila","Judita","David","Silvestr"]] \
	
	re_argument_date = re.compile(r"^[0-9]+\.[0-9]+\.$")
	re_argument_name = re.compile(r"^.+$")

	if argument == "":
			irc_privmsg("Dnes ma svatek: " + nameday[time[1]-1][time[2]-1])
	
	elif re_argument_date.search(argument):
		try:
			day = int(string.split(argument,".")[0])
			month = int(string.split(argument,".")[1])
			irc_privmsg(str(day) + ". " + month_list[month] + " ma svatek: " + nameday[month-1][day-1])
		except StandardError:
			irc_privmsg("Error: Neplatny format data!")
			
	elif re_argument_name.search(argument):
		if len(argument) < 3:
			irc_privmsg("Hledany retezec je prilis kratky! Zadejte alespon 3 znaky!")
		else:
			finded = []
			for x in range(len(nameday)):
				for y in range(len(nameday[x])):
					if nameday[x][y].find(argument) != -1:
						appendix = nameday[x][y] + " ma svatek " + str(y + 1) + ". " + month_list[x + 1]
						finded.append(appendix)
			result = string.join(finded, ", ")
			if result == "":
				result = "Hledane jmeno nenalezeno!"
			irc_privmsg(result)

	return 0
	
# CMD_SLAP #####################################################################

def cmd_slap(nick):
	if nick[-1] == "a":
		nick = nick[0:-1] + nick[-1].replace("a","u")
	elif (nick[-1] == "i") or (nick[-1] == "y"):
		nick = nick + "ho"
	elif nick[-1] == "o":
		nick = nick[0:-1] + nick[-1].replace("o","a")
	elif nick[-1] == "u":
		nick = nick[0:-1] + nick[-1].replace("u","a")
	elif (nick[-1] == "b") or (nick[-1] == "c") or (nick[-1] == "d") or (nick[-1] == "f") or (nick[-1] == "g") or (nick[-1] == "h") or (nick[-1] == "j") or (nick[-1] == "k") or (nick[-1] == "l") or (nick[-1] == "m") or (nick[-1] == "n") or (nick[-1] == "p") or (nick[-1] == "q") or (nick[-1] == "r") or (nick[-1] == "s") or (nick[-1] == "t") or (nick[-1] == "v") or (nick[-1] == "w") or (nick[-1] == "x") or (nick[-1] == "z"):
		nick = nick + "a"
	
	elif nick[-1] == "A":
		nick = nick[0:-1] + nick[-1].replace("A","U")
	elif (nick[-1] == "I") or (nick[-1] == "Y"):
		nick = nick + "HO"
	elif nick[-1] == "O":
		nick = nick[0:-1] + nick[-1].replace("O","A")
	elif nick[-1] == "U":
		nick = nick[0:-1] + nick[-1].replace("U","A")
	elif (nick[-1] == "B") or (nick[-1] == "C") or (nick[-1] == "D") or (nick[-1] == "F") or (nick[-1] == "G") or (nick[-1] == "H") or (nick[-1] == "J") or (nick[-1] == "K") or (nick[-1] == "L") or (nick[-1] == "M") or (nick[-1] == "N") or (nick[-1] == "P") or (nick[-1] == "Q") or (nick[-1] == "R") or (nick[-1] == "S") or (nick[-1] == "T") or (nick[-1] == "V") or (nick[-1] == "W") or (nick[-1] == "X") or (nick[-1] == "Z"):
		nick = nick + "A"
	
	action = {0:"klovnul",1:"klovnul",2:"znasilnil",3:"uderil",4:"pichnul",5:"dloubnul",6:"zmlatil",7:"lisknul",8:"majznul",9:"bouchnul",10:"prastil"}
	how = {0:"do xichtu",1:"do zadku",2:"do nejcitlivejsiho mista",3:"do oka",4:"s dabelskym smichem",5:"v amoku",6:"s zilou na cele",7:"rozzurene",8:"nekolikrat po sobe",9:"opakovane",10:"bleskurychlym pohybem"}
	thing = {0:"nabrousenym zobakem",1:"spicatym zobakem",2:"mohutnym klackem",3:"tezkotonaznim bagrem",4:"rezavou popelnici",5:"kapesnim nozikem",6:"hlucnym vysavacem",7:"stetkou od zachodu",8:"rozpalenou panvickou",9:"vychazkovou holi",10:"dlazebni kostkou"}	
	irc_privmsg("\x01ACTION " + action[random.randint(0,10)] + " " + nick + " " + how[random.randint(0,10)] + " " + thing[random.randint(0,10)] + "\x01")
	return 0

# CMD_DIE ######################################################################

def cmd_die(nick):
	if nick == admin:
		irc_privmsg("Sbohem!")
		print "------------------------------------------------------------------------------------------"
		print "STATUS:  Sestreluji Jestraba..."
		
		irc.send ( "QUIT Jestrab_byl_sestrelen\r\n" )
		if log_out == 1:
			print "LOG_OUT: QUIT Jestrab byl sestrelen"
		
		irc.close()
		return 1
	else:
		irc_privmsg("Access denied!")
		return 0
	
################################################################################
################################################################################
################################################################################

# MAIN #########################################################################

def main():
	global irc
	irc = connect()
	salute()
	listen()
	return 0

main()
