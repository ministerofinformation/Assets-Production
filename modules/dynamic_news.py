import string
import VS
import vsrandom
import dynamic_news_content

# Here are functions that retrieve and format the news from the dictionary
# returned by the dynamic_news_content.allNews() function



def makeDynamicNews	(type_event,stage_event,aggressor,defender,success
			,scale_event,system,keyword):
# retrieves a relevant news item from the dynamic_news_content.allNews()
# list, and formats it
	global allUsefullVariables
	allUsefullVariables =	{"type_event"	: type_event
				,"stage_event"	: stage_event
				,"aggressor"	: aggressor
				,"defender"	: defender
				,"success"	: getSuccessStr(success)
				,"dockedat"	: getDockFaction()
				,"scale_event"	: scale_event
				,"system"	: system
				,"keyword"	: keyword
				}

	return formatNewsItem (getNewsItem(getDockFaction(),type_event,stage_event,success
					 ,getPOV(getDockFaction(),defender,aggressor,success)
					 ,scale_event,keyword))

# ------------------------------------------------------------------------------
# String Formatting functions
# ------------------------------------------------------------------------------

def splitPunWord(word):
# splits a word into a list containing any prefix punctuation,
# the word, any suffix punctuation, and any trailing characters
	pre_pun = word[:word.find("VAR_")]
	word_2 = word[len(pre_pun):]
	excess_pun = ""
	for i in range(len(word_2)):
		if word_2[i] in string.punctuation and word_2[i] != "_":
			excess_pun+=word_2[i]
	if len(excess_pun) > 0:
		middle = word_2[:word_2.find(excess_pun[0])]
		end_pun = word_2[word_2.find(excess_pun[0]):word_2.find(excess_pun[len(excess_pun)-1])+1]
		end_alpha = word_2[word_2.find(excess_pun[len(excess_pun)-1])+1:]
		return [pre_pun,middle,end_pun,end_alpha]
	else:
		return [pre_pun,word_2,"",""]

#	for i in range(len(word)):
#		if word[i] == "_" or word[i] not in string.punctuation:
#			middle+=word[i]
#	wordsplit+= [middle]
#	end = word[len(wordsplit[0])+len(wordsplit[1]):]
#	end_pun = ""
#	for i in range(len(end)):
#		if end[i] in string.punctuation:
#			end_pun+= [word[i]]
#	end_alpha = end[len(end_pun)]
#	return wordsplit

def formatNewsItem(item):
# returns the formatted news item built from the relevant data
	lines = item.split("\n")
	for i in range (len(lines)):
		words = lines[i].split()
		for j in range (len(words)):
			if words[j].find("VAR_") != -1:
				word = splitPunWord(words[j])
				words[j] = word[0] + formatNameTags(word[1],dynamic_news_content.allFactionNames()) + word[2] + word[3]
		lines[i] = string.join(words)
	return string.join(lines,"\n")

def formatNameTags(word,names):
# formats a news tag to be the string so desired
# valid tags include "system_sector", "aggressor_nick", "defender_homeplanet"
	[pre,var,tag] = string.split(word,"_")	
	var_string = allUsefullVariables[var]
	if var == "system":
		if tag == "system":
			return formatProperTitle(allUsefullVariables["system"][allUsefullVariables["system"].index("/")+1:])
		if tag == "sector":
			return formatProperTitle(allUsefullVariables["system"][:allUsefullVariables["system"].index("_")])
	if tag in names["alltags"]:
		return names[var_string][tag]
	else:
		print "Error. Invalid news tag."
		return "blah"

def formatProperTitle(str):
# puts capital letters at the start of every word in string
# while preserving caps for all other letters!!!
	words = str.split()
	for i in range (len(words)):
		if words[i][0] in string.lowercase:
			words[i] = words[i][0].capitalize() + words[i][1:]
	return string.join(words)

# ------------------------------------------------------------------------------
# Dictionary and Validation functions
# ------------------------------------------------------------------------------

def validateDictKeys(listkeys,dict):
# checks to see if the keys given are available in the dictionary in the specified order

	dicto = dict
	listo = listkeys
	count_true = 0
	for i in range (len(listkeys)):
		if type(dicto) == type(dict):
			if dicto.has_key(listkeys[i]):
				dicto = dicto[listkeys[i]]
				count_true = count_true + 1
	if count_true == len(listkeys):
		return 1
	else:
		return 0

def validateNewsItem(faction_base,type_event,stage_event,success,pov,keyword):
# validates that a news item with the specified variables (or a neutral one) exists)
# returns the faction for which it does exist (if any)
	neutral_list = 0
	neutral_keyword = 0
	specific_list = 0
	specific_keyword = 0
	if validateDictKeys(["neutral",type_event,stage_event,success,pov],dynamic_news_content.allNews()):
		neutral_list = 1
		if validateNewsKeyword(dynamic_news_content.allNews()["neutral"][type_event][stage_event][success][pov],keyword):
			neutral_keyword = 1

	if validateDictKeys([faction_base,type_event,stage_event,success,pov],dynamic_news_content.allNews()):
		specific_list = 1
		if validateNewsKeyword(dynamic_news_content.allNews()[faction_base][type_event][stage_event][success][pov],keyword):
			specific_keyword = 1
	if (not neutral_list) and (not specific_list):
		print "Error.  Specified news variables do not match news dictionary. Returning barf."
		return "barf"
	if (not neutral_keyword) and (not specific_keyword):
		print "Error.  Specified news keyword do not exist. Returning lots of barf."
		return "barfbarfbarfbarfbarfbarfbarfbarf"
	else:
		if specific_keyword:
			return faction_base
		else:
			return "neutral"

def validateNewsKeyword(newslist,keyword):
# validates that a keyword exists for a specified news list
	for i in range (len(newslist)):
		if newslist[i][1] == keyword:
			return 1

# ------------------------------------------------------------------------------
# Miscellaneous functions
# ------------------------------------------------------------------------------

def povCutOff():
# the "cutoff" value for neutral/good/bad in the getPOV function
	return 0.15

def getPOV(facmy,defender,aggressor,success):
# returns a rough string approximation of the relation between two functions
	relatdef = VS.GetRelation(facmy,defender)
	relatagg = VS.GetRelation(facmy,aggressor)

	if (relatdef <= -povCutOff() and relatagg <= -povCutOff()) or (relatdef >= povCutOff() and relatagg >= povCutOff()):
		return "neutral"
	elif relatdef > relatagg:
		if success:
			return "bad"
		elif not success:
			return "good"
	elif relatdef < relatagg:
		if success:
			return "good"
		elif not success:
			return "bad"
	else:
		print "Error, one or more values out of range"
		return "neutral"

def getDockFaction():
# returns the faction of the place the player is docked at
	return "aera" # FIXME -- actually return a useful value!
#	i=0
#	playa=VS.GetPlayer()
#	un=VS.GetUnit(i)
#	while(un):
#		i+=1
#		if (un.isDocked(plr)):
#			break
#		un=VS.GetUnit(i)
#	if un.isPlanet() or (un.getFactionName() == "neutral"):
#		return VS.GetGalaxyFaction(allUsefullVariables["system"])
#	else:
#		return un.getFactionName()

def getSuccessStr(success):
# returns a string either "success" or "loss" based on the arg success
	if success:
		return "success"
	elif not success:
		return "loss"

def getNewsItem(faction_base,type_event,stage_event,success,pov,scale,keyword):
# finds a suitable news string from the dynamic_news_content.allNews() dictionary
	listnews = dynamic_news_content.allNews()[validateNewsItem(faction_base,type_event,stage_event,getSuccessStr(success),pov,keyword)][type_event][stage_event][getSuccessStr(success)][pov]
	return getClosestScaleNews(listnews,scale)

def getClosestScaleNews(listof,scale):
# returns the closest scaled news item from a list of news items
	relscalelist = []
	for i in range (len(listof)):
		relscalelist.append(listof[i] + (abs(scale - listof[i][0]),))
	final_list = [relscalelist[0]]
	for i in range (len(relscalelist)):
		if relscalelist[i][3] < final_list[0][0]:
			final_list = [relscalelist[i]]
		elif relscalelist[i][3] == final_list[0][0]:
			final_list = final_list.append(relscalelist[i])
	return final_list[vsrandom.randrange(0,len(final_list), step=1)][2]

