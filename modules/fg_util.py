import Director
import VS

ccp=VS.getCurrentPlayer()

def MaxNumFlightgroupsInSystem ():
	return 10

def MakeFactionKey (faction):
	return 'FF:'+str(VS.GetFactionIndex(faction))
def MakeFGKey (fgname,faction):
	return 'FG:'+str(fgname)+'|'+str(VS.GetFactionIndex(faction))
def MakeStarSystemFGKey (starsystem):
	return 'SS:'+str(starsystem)
def ShipListOffset ():
	return 3
def PerShipDataSize ():
	return 3
def AllFactions ():
	facs =[]
	for i in range (VS.GetNumFactions()):
		facs+= [VS.GetFactionName(i)]
	return facs
def GetRandomFGNames (numflightgroups, faction):
	rez=[]
	for i in range (numflightgroups):
		rez.append(str(i))
	return rez
origfgoffset=0
def TweakFGNames (origfgnames):
	global origfgoffset
	tweaker=str(origfgoffset)
	tweaktuple = ('prime','double_prime','triple_prime','quad_prime','quint_prime')
	if (origfgoffset<len(tweaktuple)):
		tweaker = tweaktuple[origfgoffset]
	rez=[]
	for i in origfgnames:
		rez.append (i+'_'+tweaker)
	origfgoffset+=1
	return rez
		
def WriteStringList(cp,key,tup):
	siz = Director.getSaveStringLength (cp,key)
	s_size=siz;
	lentup= len(tup)
	if (lentup<siz):
		siz=lentup
	for i in range(siz):
		Director.putSaveString(cp,key,i,tup[i])
	for i in range (s_size,lentup):
		Director.pushSaveString(cp,key,tup[i])
	for i in range (lentup,s_size):
		Director.eraseSaveString(cp,key,lentup)
def ReadStringList (cp,key):
	siz = Director.getSaveStringLength (cp,key)
	tup =[]
	for i in range (siz):
		tup += [Director.getSaveString(cp,key,i)]
	return tup

def ListToPipe (tup):
	fina=''
	if (len(tup)):
		fina=tup[0]
	for i in range (1,len(tup)):
		fina+='|'+tup[i]
	return fina

def _MakeFGString (starsystem,typenumlist):
	totalships = 0
	ret = []
	damage=0
	strlist=[]
	for tt in typenumlist:
		totalships+=int(tt[1])
		strlist+=[str(tt[0]),str(tt[1]),str(tt[1])]
	return [str(totalships),str(starsystem),str(damage)]+strlist

def _AddShipToKnownFG(key,tn):
	leg = Director.getSaveStringLength (ccp,key)
	try:
		numtotships =int(Director.getSaveString(ccp,key,0))
		numtotships+=int(tn[1])
		Director.putSaveString(ccp,key,0,str(numtotships))
	except:
		print 'error adding ship to flightgroup'
	for i in range (ShipListOffset()+1,leg,PerShipDataSize()):
		if (Director.getSaveString(ccp,key,i-1)==str(tn[0])):
			numships=0
			numactiveships=0
			try:
				numships+= int(tn[1])
				numactiveships+= int(tn[1])
				numships+= int (Director.getSaveString(ccp,key,i))
				numactiveships+= int (Director.getSaveString(ccp,key,i+1))
			except:
				pass
			Director.putSaveString(ccp,key,i,str(numships))
			Director.putSaveString(ccp,key,i+1,str(numactiveships))
			return
	Director.pushSaveString(ccp,key,str(tn[0]))
	Director.pushSaveString(ccp,key,str(tn[1]))
	Director.pushSaveString(ccp,key,str(tn[1]))#add to number active ships

def _AddFGToSystem (fgname,faction,starsystem):
	key = MakeStarSystemFGKey (starsystem)
	leg = Director.getSaveStringLength (ccp,key)
	index = VS.GetFactionIndex (faction)
	if (leg>index):
		st=Director.getSaveString (ccp,key,index)
		if (len(st)>0):
			st+='|'
		Director.putSaveString(ccp,key,index,st+fgname)
	else:
		for i in range (leg,index):
			Director.pushSaveString(ccp,key,'')
		Director.pushSaveString(ccp,key,fgname)


def _RemoveFGFromSystem (fgname,faction,starsystem):
	key = MakeStarSystemFGKey( starsystem)
	leg = Director.getSaveStringLength(ccp,key)
	index = VS.GetFactionIndex(faction)
	if (leg>index):
		tup = Director.getSaveString (ccp,key,index).split('|')
		try:
			del tup[tup.index(fgname)]
			Director.putSaveString(ccp,key,index,ListToPipe(tup))			
		except:
			print 'fg '+fgname+' not found in '+starsystem
	else:
		print 'no ships of faction '+faction+' in '+starsystem

def _AddFGToFactionList(fgname,faction):
	key = MakeFactionKey(faction)
	Director.pushSaveString (ccp,key,fgname)
		
def _RemoveFGFromFactionList (fgname,faction):
	key = MakeFactionKey(faction)
	lun=Director.getSaveStringLength(ccp,key)
	for i in range (lun):
		if (Director.getSaveString(ccp,key,i)==fgname):
			Director.eraseSaveString(ccp,key,i)
			return 1
	return 0

def CheckFG (fgname,faction):
	key = MakeFGKey (fgname,faction)
	leg = Director.getSaveStringLength (ccp,key)
	totalships=0
	try:
		for i in range (ShipListOffset()+1,leg,PerShipDataSize()):
			shipshere=Director.getSaveString(ccp,key,i)
			totalships+=int(shipshere)
			Director.putSaveString(ccp,key,i+1,shipshere)#set num actives to zero
		if (totalships!=int(Director.getSaveString(ccp,key,0))):
			print 'mismatch on flightgroup '+fgname+' faction '+faction
			return 0
	except:
		print 'nonint readingo n flightgroup '+fgname+'faction '+faction
		return 0
	return 1
def PurgeZeroShips (faction):
	key=MakeFactionKey(faction)
	for i in range (Director.getSaveStringLength (ccp,key)):
		curfg=Director.getSaveString(ccp,key,i)
		CheckFG (curfg,faction)
		numships=NumShipsInFG(curfg,faction)
		if (numships==0):
			DeleteFG(curfg,faction)
		
def NumShipsInFG (fgname,faction):
	key = MakeFGKey (fgname,faction)
	len = Director.getSaveStringLength (ccp,key)
	if (len==0):
		return 0
	else:
		try:
			return int(Director.getSaveString(ccp,key,0))
		except:
			print 'fatal: flightgroup without size'
def DeleteFG(fgname,faction):
	key = MakeFGKey (fgname,faction)
	len = Director.getSaveStringLength (ccp,key)
	if (len>=ShipListOffset()):
		starsystem=Director.getSaveString(ccp,key,1)
		_RemoveFGFromSystem(fgname,faction,starsystem)
		_RemoveFGFromFactionList(fgname,faction)
		WriteStringList (ccp,MakeFGKey(fgname,faction),[] )
def DeleteAllFG (faction):
	for fgname in ReadStringList (ccp,MakeFactionKey (faction)):
		DeleteFG (fgname,faction)

def AddShipsToFG (fgname,faction,typenumbertuple,starsystem):
	key = MakeFGKey(fgname,faction)	
	len = Director.getSaveStringLength (ccp,key)
	if (len<ShipListOffset()):
		WriteStringList(ccp,key,_MakeFGString( starsystem,typenumbertuple) )
		_AddFGToSystem (fgname,faction,starsystem)
		_AddFGToFactionList (fgname,faction)
	else:
		for tn in typenumbertuple:
			_AddShipToKnownFG(key,tn)
	
def RemoveShipFromFG (fgname,faction,type):
	key = MakeFGKey (fgname,faction)
	leg = Director.getSaveStringLength (ccp,key)
	for i in range (ShipListOffset()+1,leg,PerShipDataSize()):
		if (Director.getSaveString(ccp,key,i-1)==str(type)):
			numships=0
			try:
				numships = int (Director.getSaveString (ccp,key,i))
			except:
				pass
			if (numships>0):
				numships-=1
				Director.putSaveString (ccp,key,i,str(numships))
			else:
				Director.eraseSaveString(ccp,key,i)
				Director.eraseSaveString(ccp,key,i-1)
	print 'cannot find ship to delete in '+faction+' fg ' + fgname
def FGsInSystem(faction,system):
	key = MakeStarSystemFGKey (system)
	leg = Director.getSaveStringLength (ccp,key)
	facnum = VS.getFactionIndex (faction)
	ret=[]
	if (leg>facnum):
		st=Director.getSaveString(ccp,key,facnum)
		if (len(st)>0):
			ret = st.split('|')
	return ret
def CountFactionShipsInSystem(faction,system):
	count=0
	for fgs in FGsInSystem (faction,system):
		ships=ReadStringList (ccp,MakeFGKey (fgs,faction))
		for num in range(ShipListOffset()+2,len(ships),PerShipDataSize()):
			try:
				count+= int(ships[num])
			except:
				print 'number ships '+ships[num] + ' not read'
	return count
def _prob_round(curnum):
	import vsrandom
	ret = int(curnum)
	diff = curnum-int(curnum)
	if (diff>0):
		if (vsrandom.uniform (0,1)<diff):
			ret+=1
	else:
		if (vsrandom.uniform (0,1)<-diff):
			ret-=1
	return ret

def GetShipsInFG(fgname,faction):
	import vsrandom
	ships = ReadStringList (ccp,MakeFGKey(fgname,faction))
	count=0
	for num in range(ShipListOffset()+2,len(ships),PerShipDataSize()):
		count+=int(ships[num])
	launchnum = vsrandom.randrange(1,6)
	if (launchnum>count):
		launchnum=count
	ret = []
	for num in range(ShipListOffset(),len(ships),PerShipDataSize()):
		curnum=int(ships[num+2])
		cnum = _prob_round(curnum*float(launchnum)/count)
		if (cnum>0):
			ret+=[(ships[num],cnum)]
	return ret

def LaunchLandShip(fgname,faction,typ,numlaunched=1):
	key = MakeFGKey (fgname,faction)
	ships=ReadStringList (cpp,key)
	for num in range (ShipListOffset(),len(ships),PerShipDataSize()):
		if (typ == ships[num]):
			try:
				ntobegin=int(ships[num+1])
				nactive=int(ships[num+2])
				nactive-=numlaunched
				if (nactive<0):
					nactive=0
					print 'error more ships launched than in FG '+fgname
				if (nactive>ntobegin):
					nactive=ntobegin
					print 'error ships '+typ+'landed that never launched'
				Director.putSaveString(ccp,key,num+2,str(nactive))
			except:
				print 'error in FG data (str->int)'
def LaunchShip (fgname,faction,typ,num=1):
	LaunchLandDestroyShip (fgname,faction,typ,num)
def LandShip (fgname,faction,typ,num=1):
	LaunchLandDestroyShip(fgname,faction,typ,-num)
