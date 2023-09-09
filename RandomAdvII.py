import tkinter as tk
from scipy.stats import norm
import numpy as np
from tkinter import messagebox 
from tkinter import simpledialog,filedialog,font
from PIL import Image,ImageTk
from tkinter import ttk
import math
import os
import copy
import time
import _pickle as CP

class ZoneInfo:
    def __init__(self):
        self.N=1
        self.ID=[]
        self.Name=[]
        self.BossIDgood=0
        self.BossIDbad=0
        self.BossFactor=1
        self.KillN=0
        self.Killed=0
        self.Completed=True

    def EnoughKill(self,Zid):
        return self.Killed[Zid]>=self.KillN[Zid]

    def AddKill(self,Zid):
        self.Killed[Zid]+=1

    def EmptyProgress(self,Zid):
        self.Killed[Zid]=0

    def Str_progress(self,Zid):
        return str(int(self.Killed[Zid]))+'/'+str(int(self.KillN[Zid]))

    def DisplayName(self):
        temp=copy.copy(self.Name)
        
        for ii in range(self.N):
            temp[ii]='Zone '+str(ii)+' (???)'
            if self.Completed[ii]:
                temp[ii]=self.Name[ii]
        
        foundit=False
        ii=0
        while not foundit and ii<len(temp):
            if '???' in temp[ii]:
                temp[ii]=self.Name[ii]
                foundit=True
            ii+=1
           
        
        return temp

    def Update_Boss(self,DeadID): #check if the dead monster is boss, if so, change complete 

        temp=-1
        for ii in range(self.N):
            if not self.Completed[ii]:  #only check zones not completed

                if DeadID==self.BossIDgood[ii] or DeadID==self.BossIDbad[ii]:
                    self.Completed[ii]=True
                    temp=ii  
        return temp  #return the ID of zone when you first beat it, else -1

class Remains:
    def __init__(self):
        self.Exp=0
        self.Money=0
        self.PT_equip=0
        self.PT_mag=0
        self.PT_stat=0
        self.Item=[]
        self.Equip=[]
    
    def To_string(self):
        temp_str='\n'
        temp_str+='Exp: '+str(self.Exp)+'\n'
        temp_str+='$: '+str(self.Money)+'\n'
        temp_str+='Equip Points: '+str(self.PT_equip)+'\n'
        temp_str+='Magic Points: '+str(self.PT_mag)+'\n'
        temp_str+='Stat Points: '+str(self.PT_stat)+'\n'
        #temp_str+='Items: '
        #if len(self.Item)>0:
        #    for ii in range(len(self.Item)):
        #        temp_str+=self.Item[ii].Name+', '
        #else:
        #    temp_str+='Nothing dropped'
        #temp_str+='\n'

        #temp_str+='Equipment: '
        #if len(self.Equip)>0:
        #    for ii in range(len(self.Equip)):
        #        temp_str+=self.Equip[ii].Name+', '
        #else:
        #    temp_str+='Nothing dropped'
        #temp_str+='\n'

        return temp_str

    def OutputGUI(self,GUIs):
        self.Exp=0

class Magic:
    def __init__(self):
        self.ID=0
        self.Name=''
        self.Align='None'
        self.Pic='mag0.png'
        self.Description='Not magic'
        self.Special='None'
        self.MPcost=0
        self.Tier=0
        self.UpgradeCost=0
        self.LV=1
        self.Zone=0
        self.Attack=np.zeros((7,1))
        self.Requirement=[0,0,0,0,0,0,0,0]
        self.Effects=np.zeros((1,3))
        self.Img=0
        self.PImg=0

    def LoadImg(self,filepath):
        self.Img=Image.open(filepath+self.Pic)
        self.PImg=ImageTk.PhotoImage(self.Img)

    def Set_string(self,str_data,str_desc):  #this function set up Magic using 2 lines of strings
        temp_str=str_data.split(',')

        self.ID=int(temp_str[0])
        self.Name=temp_str[1]
        self.Align=temp_str[2]
        self.Special=temp_str[3]
        self.Pic=temp_str[4]
        self.MPcost=int(temp_str[5])
        self.Tier=int(temp_str[6])
        self.UpgradeCost=int(temp_str[7])
        self.Zone=int(temp_str[8])
        self.Attack=[]
        for x in temp_str[9:16]:
            self.Attack=np.append(self.Attack,int(x))
        ii=0
        for x in temp_str[16:24]:            
            self.Requirement[ii]=int(x)
            ii+=1
        Nt=len(temp_str)
        if Nt>24:  # there are effects data
            if temp_str[24]!='':
                temp_str=temp_str[24:]  #take whatever is left, ind1, ind2, value
                Ne=int(len(temp_str)/3) #number of effects
               
                self.Effects=[-1,-1,-1]  #add first row so we can vstack
                for ii in range(Ne):
                    if temp_str[ii*3]!='':
                        self.Effects=np.vstack([self.Effects,[int(temp_str[ii*3]),int(temp_str[ii*3+1]),float(temp_str[ii*3+2])]])

                self.Effects=np.delete(self.Effects,0,0) #delete the first row

        self.Description=str_desc

    def Effect(self):  #this returns base effects of a magic at Level LV
        Factor=self.LV**1.5
        FactorE=self.LV**0.75
        eft=Effects()
        eft.Type='Magic'
        eft.V_Attack=self.Attack*Factor
        eft.V_EqRequirement=self.Requirement
        #eft.V_EqRequirement[0]=int(self.LV-1)#*self.Tier)  #hard level requirements

        for ii in range(len(self.Effects)):
            eft.SetEffect(self.Effects[ii,0],self.Effects[ii,1],self.Effects[ii,2]*FactorE)
        
        return eft
    
    def GetInfo(self):
        #Factor=self.LV**1.5
        
        temp_str='\n'
        temp_str=temp_str+self.Name+'  (LV='+str(self.LV)+')\n'+'MP cost='+str(int(self.Get_MPcost()))+'\n'
        temp_str=temp_str+self.Description+'\n\n'
        temp_str=temp_str+'Upgrade PT='+str(self.Get_UpgradePT())+'\n'
        temp_str=temp_str+'Requirements: \n'
        tempS=['LV>','S>','P>','E>','C>','I>','A>','L>']
        for ii in range(8):
            temp_str=temp_str+tempS[ii]+str(self.Requirement[ii])+'\n'

        return temp_str

    def Upgrade(self):
        if self.LV<30:
            self.LV+=1
            return True
        else:
            messagebox.showinfo('Upgrade Failed','This Magic skill has reached Max LV30 and cannot be upgraded anymore.')
            return False

    def Get_UpgradePT(self):
        return int(self.UpgradeCost*(self.LV**0.5))

    def Get_MPcost(self):
        return int(self.MPcost*(self.LV**0.5))

    def Meet_Requirement(self,P):
        eft=self.Effect()

        # see if you can use this magic at all

        # first see if requirements are met
        Success=P.LV>=eft.V_EqRequirement[0]
        Success=Success and P.S>=eft.V_EqRequirement[1]
        Success=Success and P.P>=eft.V_EqRequirement[2]
        Success=Success and P.E>=eft.V_EqRequirement[3]
        if eft.V_EqRequirement[4]>0:
            Success=Success and P.C>=eft.V_EqRequirement[4]
        elif eft.V_EqRequirement[4]<0:
            Success=Success and P.C<=eft.V_EqRequirement[4]
        else:  #equal to 0 means no C requirement
            Success=Success and True
        Success=Success and P.I>=eft.V_EqRequirement[5]
        Success=Success and P.A>=eft.V_EqRequirement[6]
        Success=Success and P.L>=eft.V_EqRequirement[7]

        return Success

    def Impact_HP(self): #returns impact on HP of the target (rough)
        atk=np.sum(self.Attack)
        hel=0
        for ii in range(len(self.Effects)):
            if self.Effects[ii,0]==1 and self.Effects[ii,1]==0:
                hel+=self.Effects[ii,2]
            if self.Effects[ii,0]==17:
                hel+=self.Effects[ii,2]*5  #this is regan, so about 5 times...
        hel-=atk  #finally combine attack and hel
        return hel  #+ is heal, - is attack

    def Get_Description(self):

        eft=self.Effect()        

        dd=self.Name +' (LV'+str(int(self.LV))+') MP Cost='+str(self.Get_MPcost())+'MP\n'
        
        temp='Damage:'
        code=['(Physical)','(Cold)','(Fire)','(Lightning)','(Poison)','(Holy)','(Dark)']
        for ii in range(7):
            if self.Attack[ii]!=0:
                temp=temp+str(int(eft.V_Attack[ii]))+code[ii]+','
        if temp!='Damage:':
            dd=dd+temp+'\n'
        else:
            dd=dd+'Not an Attack Magic.\n'
        
        temp='Effects:\n'
        
        temp=temp+eft.Description()
        dd=dd+temp+'\n'
        
        dd=dd+self.Description+'\n'
        dd=dd+'Upgrade Cost='+str(self.Get_UpgradePT())+'PT\n'

        temp='Requirements:'
        code=['LV:','S:','P:','E:','C:','I:','A:','L:']
        for ii in range(8):
            if self.Requirement[ii]!=0:
                temp=temp+code[ii]+str(int(self.Requirement[ii]))+','
        if temp!='Requirements:':
            dd=dd+temp+'\n'
        else:
            dd=dd+'No Requirements.\n'

        dd=dd+'Alignment: '+self.Align+'\n'       

        

        return dd

    def Is_Attack(self):
        if np.sum(self.Attack)>0:
            return True
        else:
            return False

class Item:
    def __init__(self):
        self.ID=0
        self.Name=''
        self.Pic='Item0.png'
        self.Description='Absolutely Nothing'
        self.Cost=0
        self.Tier=0
        self.LV=1
        self.Zone=0
        self.Special='None'   # Special effects other than attach and status, add useable PT, Money, escape, Nuke, treaty, etc.
        self.Img=0
        self.PImg=0
        self.Attack=np.zeros((7,1))
        self.Effects=np.zeros((1,3))
    
    def LoadImg(self,filepath):
        self.Img=Image.open(filepath+self.Pic)
        self.PImg=ImageTk.PhotoImage(self.Img)

    def Set_string(self,str_data,str_desc):  #this function set up Magic using 2 lines of strings
        temp_str=str_data.split(',')

        self.ID=int(temp_str[0])
        self.Name=temp_str[1]
        self.Pic=temp_str[2]
        self.Cost=int(temp_str[3])
        self.Tier=int(temp_str[4])
        self.Special=temp_str[5]
        self.Zone=int(temp_str[6])

        self.Attack=[]
        for x in temp_str[7:14]:
            self.Attack=np.append(self.Attack,int(x))
        
        Nt=len(temp_str)
        if Nt>14:  # there are effects data
            if temp_str[14]!='':
                temp_str=temp_str[14:]  #take whatever is left, ind1, ind2, value
                Ne=int(len(temp_str)/3) #number of effects

                self.Effects=[-1,-1,-1]  #add first row so we can vstack
                for ii in range(Ne):
                    if temp_str[ii*3]!='':
                        self.Effects=np.vstack([self.Effects,[int(temp_str[ii*3]),int(temp_str[ii*3+1]),float(temp_str[ii*3+2])]])

                self.Effects=np.delete(self.Effects,0,0) #delete the first row

        self.Description=str_desc

    def Effect(self):  #this returns base effects of a magic at Level LV
        Factor=self.LV**1.5
        FactorE=self.LV**0.5
        eft=Effects()
        eft.Type='Item'
        eft.V_Attack=self.Attack*Factor
        # eft.V_EqRequirement=self.Requirement No requirements for using Item
        # eft.V_EqRequirement[0]+=int((LV-1)*self.Tier)  #hard level requirements

        for ii in range(len(self.Effects)):
            eft.SetEffect(self.Effects[ii,0],self.Effects[ii,1],self.Effects[ii,2]*FactorE)
        
        return eft
    
    def GetInfo(self):
        
        temp_str='\n'
        temp_str=temp_str+self.Name +'\n'
        temp_str=temp_str+self.Description+'\n\n'
        temp_str=temp_str+'Cost=$'+str(self.Get_Cost())+'\n'

        return temp_str

    def Get_Cost(self):
        return int(self.Cost*self.LV)

    def Impact_HP(self): #returns impact on HP (rough)
        atk=np.sum(self.Attack)
        hel=0
        for ii in range(len(self.Effects)):
            if self.Effects[ii,0]==1 and self.Effects[ii,1]==0:
                hel+=self.Effects[ii,2]
            if self.Effects[ii,0]==17:
                hel+=self.Effects[ii,2]*5  #this is regan, so about 5 times...
        hel-=atk  #finally combine attack and hel
        return hel  #+ is heal, - is attack

    def Get_Description(self):

        eft=self.Effect()

        dd=self.Name +' (LV'+str(int(self.LV))+') Cost='+str(self.Get_Cost())+'\n'
        temp='Damage:'
        code=['(Physical)','(Cold)','(Fire)','(Lightning)','(Poison)','(Holy)','(Dark)']
        for ii in range(7):
            if self.Attack[ii]!=0:
                temp=temp+str(int(eft.V_Attack[ii]))+code[ii]+','
        if temp!='Damage:':
            dd=dd+temp+'\n'
        else:
            dd=dd+'Not an Attack Item.\n'


        temp='Effects:\n'        
        temp=temp+eft.Description()
        dd=dd+temp

        dd=dd+self.Description+'\n'
        dd=dd+' Tier='+str(int(self.Tier))

        dd=dd+'Special: '+self.Special+'\n'

       

        return dd

    def Is_Attack(self):
        if np.sum(self.Attack)>0:
            return True
        else:
            return False

class Equipment:
    def __init__(self):
        self.ID=0
        self.Name=''
        self.Loc=-1
        self.Special='None'
        self.Pic='eq0.png'
        self.Description='No euipment'
        self.Cost=0
        self.Tier=0
        self.UpgradeCost=0
        self.LV=1
        self.Zone=0
        self.Img=0
        self.PImg=0
        
        self.Requirement=np.zeros((8,1))
        self.Effects=np.zeros((1,3))
        self.Attack=np.zeros((7,1))
    
    def LoadImg(self,filepath):
        self.Img=Image.open(filepath+self.Pic)
        self.PImg=ImageTk.PhotoImage(self.Img)

    def Set_string(self,str_data,str_desc):  #this function set up Magic using 2 lines of strings
        temp_str=str_data.split(',')  

        self.ID=int(temp_str[0])
        self.Name=temp_str[1]
        self.Loc=int(temp_str[2])
        self.Immune=temp_str[3]
        self.Pic=temp_str[4]
        self.Cost=int(temp_str[5])
        self.Tier=int(temp_str[6])
        self.UpgradeCost=int(temp_str[7])
        self.Zone=int(temp_str[8])
        #self.LV=int(temp_str[8])   # all equipment from text file will be load at LV=1
        ii=0
        for x in temp_str[9:17]:
            self.Requirement[ii]=int(x)
            ii+=1
        Nt=len(temp_str)
        if Nt>18:  # there are effects data
            if temp_str[18]!='':
                temp_str=temp_str[17:]  #take whatever is left, ind1, ind2, value
                Ne=int(len(temp_str)/3) #number of effects

                self.Effects=[-1,-1,-1]  #add first row so we can vstack
                for ii in range(Ne):
                    if temp_str[ii*3]!='':
                        self.Effects=np.vstack([self.Effects,[int(temp_str[ii*3]),int(temp_str[ii*3+1]),float(temp_str[ii*3+2])]])

                self.Effects=np.delete(self.Effects,0,0) #delete the first row

        self.Description=str_desc

    def Effect_PutOn(self):  #this returns base effects of a magic at Level LV
        #Factor=self.LV**1.5
        FactorE=self.LV**0.75
        eft=Effects()
        eft.Type='Equip'
        eft.V_EqRequirement=self.Requirement # not link requirements to equipment levels, just to be fair and encourage upgrade
        #for ii in range(len(eft.V_EqRequirement)):
        #    if eft.V_EqRequirement[ii]>0:
        #        eft.V_EqRequirement[ii]=int(eft.V_EqRequirement[ii]*FactorE)

        #eft.V_EqRequirement+=int((self.LV-1)*self.Tier)  #hard level requirements
        

        for ii in range(len(self.Effects)):
            
            eft.SetEffect(self.Effects[ii,0],self.Effects[ii,1],self.Effects[ii,2]*FactorE)
        
        return eft

    def Effect_TakeOff(self):  #this returns base effects of a magic at Level LV
        
        FactorE=-self.LV**0.75  # only change is this, now negative
        eft=Effects()
        eft.Type='Equipoff'
        
        # no matter what you can always take it off. so no need to program requirements in
        # by default, all requirement Vector is 0 in Effect

        for ii in range(len(self.Effects)):
            eft.SetEffect(self.Effects[ii,0],self.Effects[ii,1],self.Effects[ii,2]*FactorE)
        
        return eft
    
    def GetInfo(self):
        
        temp_str='\n'
        temp_str=temp_str+self.Name+'  LV'+str(self.LV)+'\n'
        temp_str=temp_str+self.Description+'\n\n'
        temp_str=temp_str+'Cost=$'+str(self.Get_Cost())+', Need '+str(self.Get_UpgradePT())+' to upgrade\n\n'
        temp_str=temp_str+'Requirements: \n'
        tempS=['LV>','S>','P>','E>','C>','I>','A>','L>']
        ii=0
        for x in self.Requirement:
            temp_str=temp_str+tempS[ii]+str(x)+'\n'
            ii+=1

        return temp_str

    def Get_Cost(self):
        return int(self.Cost*self.LV)

    def Upgrade(self):
        if self.LV<30:
            self.LV+=1
            return True
        else:
            messagebox.showinfo('Upgrade Failed','This Equipment has reached Max LV30 and cannot be upgraded anymore.')
            return False

    def Get_UpgradePT(self):
        return int(self.UpgradeCost*(self.LV**0.5))

    def Get_Description(self):

        dd=self.Name +' (LV'+str(int(self.LV))+') Upgrade Cost='+str(self.Get_UpgradePT())+'\n'
        temp='Requirements:'
        code=['LV:','S:','P:','E:','C:','I:','A:','L:']
        for ii in range(8):
            if self.Requirement[ii]!=0:
                temp=temp+code[ii]+str(int(self.Requirement[ii]))+','
        if temp!='Requirements:':
            dd=dd+temp+'\n'
        else:
            dd=dd+'No Requirements.\n'
        
        temp='Effects:\n'
        eft=self.Effect_PutOn()
        temp=temp+eft.Description()
        dd=dd+temp
        
        dd=dd+self.Description+' Cost='+str(self.Get_Cost())+'\n'
        locT=['Head','Body','Wrist','Leg','Feet','Weapon','Glove','Neck','Finger1','Finger2','Ear','Misc1','Misc2','Pokeball','Bokepall']
        dd=dd+'Tier='+str(int(self.Tier))+' Location: '+locT[self.Loc]+'\n'

        

        #dd=dd+'Alignment: '+self.Align+'\n'


        

        return dd

class Effects:  #This should be just a huge variable, no calculation should be done inside this class

    def __init__(self):
        #self.Type='Attack'   # Attack, Equip
        self.Type='Attack'  # Attack, Magic, Item, Equip
        self.Method='Add'    # Add or Assign    
        self.V_Attack=np.zeros((7,1))
        self.V_OwnerStat=np.zeros((10,1))
        self.V_EqRequirement=np.zeros((8,1))
        self.M_basis=np.zeros((20,6))
        self.M_derived=np.zeros((24,6))
    
    def Nullify(self):  # this will make effect=Nothing
        if self.Method=='Add':
            self.V_Attack=np.zeros((7,1))
            self.V_OwnerStat=np.zeros((10,1))
            self.V_EqRequirement=np.zeros((8,1))
            self.M_basis=np.zeros((20,6))
            self.M_derived=np.zeros((24,6))
        
        if self.Method=='Assign':
            self.M_basis[:,:]=np.nan
            self.M_derived[:,:]=np.nan  #in apply effect in player, there will be a trigger on nan

        if self.Method!='Add' and self.Method!='Assign':
            messagebox.showerror('Effect Error','Method type not recognized: ' + self.Method)

    
    def SetEffect(self,Index1,Index2,Value):
        
        if Index2<=5:
            if Index1<=19:
                
                self.M_basis[int(Index1),int(Index2)]=Value
            elif Index1<=43:
                self.M_derived[int(Index1-20),int(Index2)]=Value
            else:
                messagebox.showerror('Effect Error','Effect Row index out of bound: '+str(Index1))
        else:
            messagebox.showerror('Effect Error','Effect Col index out of bound: '+str(Index2))

    def Description(self):
        text2=['LV',
        'HP',
        'MP',
        'S',
        'P',
        'E',
        'C',
        'I',
        'A',
        'L',
        'Drop Rate',
        'Steal Rate',
        'Exp Factor',
        'Money Factor',
        'Ptstat Factor',
        'Ptequip Factor',
        'Ptmag Factor',
        'HP Regan',
        'MP Regan',
        'Money Regan',
        'Max HP',
        'Max MP',
        'Physical Attack',
        'Cold Attack',
        'Fire Attack',
        'Lightning Attack',
        'Poison Attack',
        'Holy Attack',
        'Dark Attack',
        'Physical Defense',
        'Cold Defense',
        'Fire Defense',
        'Lightning Defense',
        'Poison Defense',
        'Holy Defense',
        'Dark Defense',
        'Physical Proficiency',
        'Cold Proficiency',
        'Fire Proficiency',
        'Lightning Proficiency',
        'Poison Proficiency',
        'Holy Proficiency',
        'Dark Proficiency',
        'Action Point']
        
        text1=['Permanently','While equiped','For this battle','Permanently','While equiped','For this battle']
        text3=['.\n','.\n','.\n','%.\n','%.\n','%.\n']
        dd=''
        for ii in range(44):
            for jj in range(6):
                if ii<=19:
                    id1=ii
                    id2=jj
                    if self.M_basis[id1,id2]>0:
                        dd=dd+text1[id2]+' increase '+text2[id1]+' by '+ str(int(self.M_basis[id1,id2]))+text3[id2]
                    elif self.M_basis[id1,id2]<0:
                        dd=dd+text1[id2]+' decrease '+text2[id1]+' by '+ str(int(-self.M_basis[id1,id2]))+text3[id2]
                else:
                    id1=ii-20
                    id2=jj
                    if self.M_derived[id1,id2]>0:
                        dd=dd+text1[id2]+' increase '+text2[ii]+' by '+ str(int(self.M_derived[id1,id2]))+text3[id2]
                    elif self.M_derived[id1,id2]<0:
                        dd=dd+text1[id2]+' decrease '+text2[ii]+' by '+ str(int(-self.M_derived[id1,id2]))+text3[id2]
        
        if dd=='':
            dd='No special effects'
        return dd

class GUIgroup:
    def __init__(self):
        self.List_Item=tk.Listbox()
        self.List_Magic=tk.Listbox()
        self.List_Equip=tk.Listbox()
        self.Canv_Equiped=[tk.Canvas()]*15  #array of 15 canvas
        self.Canv_Pic=tk.Canvas()
        self.Lab_Stat=[tk.Label()]*7  #array of 7 Labels
        self.Lab_Att=[tk.Label()]*7  #array of 7 Labels
        self.Lab_Def=[tk.Label()]*7  #array of 7 Labels
        self.Lab_Prof=[tk.Label()]*7  #array of 7 Labels
        self.Lab_HP=tk.Label()
        self.Lab_MP=tk.Label()
        self.Pbar_HP=ttk.Progressbar()
        self.Pbar_MP=ttk.Progressbar()
        self.Lab_Name=tk.Label()
        self.Lab_Nickname=tk.Label()
        self.Lab_Money=tk.Label()
        self.Lab_PTstat=tk.Label()
        self.Lab_PTmag=tk.Label()
        self.Lab_PTequip=tk.Label()
        self.Lab_ItemInv=tk.Label()
        self.Lab_MagicInv=tk.Label()
        self.Lab_EquipInv=tk.Label()

        self.Lab_LVexp=tk.Label()
        self.Lab_HPreg=tk.Label()
        self.Lab_MPreg=tk.Label()
        self.Lab_DropR=tk.Label()

        self.Lab_AP=tk.Label()

class Player:
    def __init__(self):
        #Basic Info
        self.Name=''
        self.NickName=''
        self.Desc=''
        self.ID=0  #this is empty default, need to change for monster, player can be -1
        self.Pic='/Adv2mon/mon0.png'
        self.Img=0  #this used to load file using Image
        self.PImg=0  #this used to output to canvas
        self.onDef=False
        self.ActPT=0
        self.Align='None'
        
        #Single variables
        self.N_total=0
        self.N_kill=0
        self.N_run=0
        self.N_convert=0
        self.HighestKill=0

        # Stock spaces  (these need to be upgraded in the game) by default you got one for each, good for Vstack
        self.N_ActionPT=1
        self.N_Magic=6
        self.N_Item=10
        self.N_Equip=10
        self.Value=0
        self.Zone=0
        self.Tier=0

        self.Exp=0
        self.ExpNext=500
        self.Angry=False  # hostile to player or not
        self.DeathImmune=False
        
        # Expendible resources points
        self.Money=0
        self.PT_stat=0
        self.PT_equip=0
        self.PT_mag=0

        #self.Prob_hit=0
        #self.Prob_stealE_inv=0
        #self.Prob_stealE_equip=0
        #self.Prob_stealI=0
        #self.Prob_Recruit=0
       
        # Item equipment and magic
        self.Item=[Item()]*self.N_Item  # Items
        #for ii in range(self.N_Item):
        #    self.Item[ii]=Item()

        self.Magic=[Magic()]*self.N_Magic # Magics
        self.Equipment=[Equipment()]*self.N_Equip # Equipments 

        # Equiped slots (these are always the same, 15 of them)
        self.Equiped=[Equipment()]*15 # Equipments on body (15 total), if it is number 0 nothing equiped.
        # 0-Head,1-body,2-belt,3-pants,4-shoes,5-weapon,6-glove,7-arlmet,8-left ring,9-right ring,10-ear ring,11-toe ring,12-nose ring,13-pokemon1, 14-pokemon2

        self.REM=Remains() #empty remains         
        
        self.Data_Base=np.zeros((20,6))
        self.Data_Base[0,0]=1  #set level =1

        self.Data_Base[10,0]=100  #set default drop to 100 for player, but monster need to update this
        self.Data_Base[11,0]=100  #set default steal to 100
        self.Data_Base[12:17,0]=100  #set rates to 100
        self.Data_Base[:,3]=100        
        self.Data_Derive=np.zeros((24,6))
        self.Data_Derive[:,3]=100
        # Base Stats
        self.LV=0
        self.HP=0
        self.MP=0

        self.S=0  
        self.P=0
        self.E=0
        self.C=0
        self.I=0
        self.A=0
        self.L=0

        self.DropRate=0
        self.StealRate=0
        self.F_exp=0
        self.F_money=0
        self.F_PTstat=0
        self.F_PTequip=0
        self.F_PTmag=0
        self.HPreg=0
        self.MPreg=0
        self.Moneyreg=0

        # Derived stats
        self.HPmax=0
        self.MPmax=0
        
        self.A_Phys=0
        self.A_Cold=0
        self.A_Fire=0
        self.A_Ligh=0
        self.A_Pois=0
        self.A_Holy=0
        self.A_Dark=0
        self.D_Phys=0
        self.D_Cold=0
        self.D_Fire=0
        self.D_Ligh=0
        self.D_Pois=0
        self.D_Holy=0
        self.D_Dark=0
        self.P_Phys=0
        self.P_Cold=0
        self.P_Fire=0
        self.P_Ligh=0
        self.P_Pois=0
        self.P_Holy=0
        self.P_Dark=0
    
    def Clone(self):
        N_P=Player()

        N_P.Desc=self.Desc
    

        N_P.ID=self.ID
        N_P.Name=self.Name
        N_P.Pic=self.Pic
        N_P.Data_Base[3,0]=self.Data_Base[3,0]
        N_P.Data_Base[4,0]=self.Data_Base[4,0]
        N_P.Data_Base[5,0]=self.Data_Base[5,0]
        N_P.Data_Base[6,0]=self.Data_Base[6,0]
        N_P.Data_Base[7,0]=self.Data_Base[7,0]
        N_P.Data_Base[8,0]=self.Data_Base[8,0]
        N_P.Data_Base[9,0]=self.Data_Base[9,0]
        N_P.Align=self.Align
        N_P.Zone=self.Zone
        N_P.Tier=self.Tier
        N_P.Data_Base[0,0]=self.Data_Base[0,0]

       
        N_P.Data_Derive[3,1]=self.Data_Derive[3,1]   #    ttack
        N_P.Data_Derive[10,1]=self.Data_Derive[10,1] #      efense
        N_P.Data_Derive[17,1]=self.Data_Derive[17,1] #      ncy
        N_P.Data_Derive[4,1]=self.Data_Derive[4,1]   #    ttack
        N_P.Data_Derive[11,1]=self.Data_Derive[11,1] #      efense
        N_P.Data_Derive[18,1]=self.Data_Derive[18,1] #      
        N_P.Data_Derive[5,1]=self.Data_Derive[5,1]   #    ttack
        N_P.Data_Derive[12,1]=self.Data_Derive[12,1] #      efense
        N_P.Data_Derive[19,1]=self.Data_Derive[19,1] #      
        N_P.Data_Derive[6,1]=self.Data_Derive[6,1]   #    ttack
        N_P.Data_Derive[13,1]=self.Data_Derive[13,1] #      efense
        N_P.Data_Derive[20,1]=self.Data_Derive[20,1] #      
        N_P.Data_Derive[7,1]=self.Data_Derive[7,1]   #    ttack
        N_P.Data_Derive[14,1]=self.Data_Derive[14,1] #      efense
        N_P.Data_Derive[21,1]=self.Data_Derive[21,1] #      
        N_P.Data_Derive[8,1]=self.Data_Derive[8,1]   #    ttack
        N_P.Data_Derive[15,1]=self.Data_Derive[15,1] #      efense
        N_P.Data_Derive[22,1]=self.Data_Derive[22,1] #      

        N_P.Update() # do initial calc
        # fill in default values here
        N_P.Data_Base[1,0]=self.Data_Base[1,0]
        N_P.Data_Base[2,0]=self.Data_Base[2,0]
        N_P.Data_Base[10,0]=self.Data_Base[10,0]  #drop rate default=25% for monsters
        N_P.Data_Base[11,0]=self.Data_Base[11,0]   #Steal rate default=100%, monster will not use this anyway
        N_P.Data_Base[12:17,0]=self.Data_Base[12:17,0]

        N_P.Money=self.Money
        N_P.Exp=self.Exp
        N_P.PT_mag=self.PT_mag
        N_P.PT_stat=self.PT_stat
        N_P.PT_equip=self.PT_equip

        N_P.Update() # do initial calc

        return N_P

    def ExtractData(self):
        Data=PlayerData()

        Data.Name=self.Name
        Data.NickName=self.NickName
        Data.Desc=self.Desc
        Data.ID=self.ID  
        Data.Pic=self.Pic        
        Data.onDef=self.onDef
        Data.ActPT=self.ActPT
        Data.Align=self.Align
        
        #Single variables
        Data.N_total=self.N_total
        Data.N_kill=self.N_kill
        Data.N_run=self.N_run
        Data.N_convert=self.N_convert
        Data.HighestKill=self.HighestKill

        # Stock spaces  (these need to be upgraded in the game) by default you got one for each, good for Vstack
        Data.N_ActionPT=self.N_ActionPT
        Data.N_Magic=self.N_Magic
        Data.N_Item=self.N_Item
        Data.N_Equip=self.N_Equip
        Data.Value=self.Value
        Data.Zone=self.Zone
        Data.Tier=self.Tier

        Data.Exp=self.Exp
        Data.ExpNext=self.ExpNext
        Data.Angry=self.Angry
        Data.DeathImmune=self.DeathImmune
        
        # Expendible resources points
        Data.Money=self.Money
        Data.PT_stat=self.PT_stat
        Data.PT_equip=self.PT_equip
        Data.PT_mag=self.PT_mag

        Data.N_Item=self.N_Item
        Data.ItemData=np.zeros((self.N_Item,2))

        Data.N_Magic=self.N_Magic
        Data.MagicData=np.zeros((self.N_Magic,2))

        Data.N_Equip=self.N_Equip
        Data.EquipmentData=np.zeros((self.N_Equip,2))

       
        # Item equipment and magic
        for ii in range(len(self.Item)):#self.N_Item):
            Data.ItemData[ii,0]=self.Item[ii].ID
            Data.ItemData[ii,1]=self.Item[ii].LV
        
        for ii in range(len(self.Magic)):
            Data.MagicData[ii,0]=self.Magic[ii].ID
            Data.MagicData[ii,1]=self.Magic[ii].LV

        for ii in range(len(self.Equipment)):
            Data.EquipmentData[ii,0]=self.Equipment[ii].ID
            Data.EquipmentData[ii,1]=self.Equipment[ii].LV 

        for ii in range(15):
            Data.EquipedData[ii,0]=self.Equiped[ii].ID
            Data.EquipedData[ii,1]=self.Equiped[ii].LV

        
        #self.REM=Remains() #empty remains         
        
        Data.Data_Base=self.Data_Base
            
        Data.Data_Derive=self.Data_Derive
        
        # Base Stats
        Data.LV=self.LV
        Data.HP=self.HP
        Data.MP=self.MP
        Data.S=self.S
        Data.P=self.P
        Data.E=self.E
        Data.C=self.C
        Data.I=self.I
        Data.A=self.A
        Data.L=self.L

        Data.DropRate=self.DropRate
        Data.StealRate=self.StealRate
        Data.F_exp=self.F_exp
        Data.F_money=self.F_money
        Data.F_PTstat=self.F_PTstat
        Data.F_PTequip=self.F_PTequip
        Data.F_PTmag=self.F_PTmag
        Data.HPreg=self.HPreg
        Data.MPreg=self.MPreg
        Data.Moneyreg=self.Moneyreg

        # Derived stats
        Data.HPmax=self.HPmax
        Data.MPmax=self.MPmax
        
        Data.A_Phys=self.A_Phys
        Data.A_Cold=self.A_Cold
        Data.A_Fire=self.A_Fire
        Data.A_Ligh=self.A_Ligh
        Data.A_Pois=self.A_Pois
        Data.A_Holy=self.A_Holy
        Data.A_Dark=self.A_Dark
        Data.D_Phys=self.D_Phys
        Data.D_Cold=self.D_Cold
        Data.D_Fire=self.D_Fire
        Data.D_Ligh=self.D_Ligh
        Data.D_Pois=self.D_Pois
        Data.D_Holy=self.D_Holy
        Data.D_Dark=self.D_Dark
        Data.P_Phys=self.P_Phys
        Data.P_Cold=self.P_Cold
        Data.P_Fire=self.P_Fire
        Data.P_Ligh=self.P_Ligh
        Data.P_Pois=self.P_Pois
        Data.P_Holy=self.P_Holy
        Data.P_Dark=self.P_Dark



        return Data

    def Import_from_Data(self,Data,Dict_I,Dict_M,Dict_E,CWDnow):

        self.Name=Data.Name
        self.NickName=Data.NickName
        self.Desc=Data.Desc
        self.ID=Data.ID
        self.Pic=Data.Pic
        self.onDef=Data.onDef
        self.ActPT=Data.ActPT
        self.Align=Data.Align
        
        #Single variables
        self.N_total=Data.N_total
        self.N_kill=Data.N_kill
        self.N_run=Data.N_run
        self.N_convert=Data.N_convert
        self.HighestKill=Data.HighestKill

        # Stock spaces  (these need to be upgraded in the game) by default you got one for each, good for Vstack
        self.N_ActionPT=Data.N_ActionPT
        self.N_Magic=Data.N_Magic
        self.N_Item=Data.N_Item
        self.N_Equip=Data.N_Equip
        self.Value=Data.Value
        self.Zone=Data.Zone
        self.Tier=Data.Tier

        self.Exp=Data.Exp
        self.ExpNext=Data.ExpNext
        self.Angry=Data.Angry
        self.DeathImmune=Data.DeathImmune
        
        # Expendible resources points
        self.Money=Data.Money
        self.PT_stat=Data.PT_stat
        self.PT_equip=Data.PT_equip
        self.PT_mag=Data.PT_mag

        for ii in range(len(self.Item)):#self.N_Item-1):
            
            self.Item[ii]=copy.copy(Dict_I[Data.ItemData[ii,0]])
            self.Item[ii].LV=Data.ItemData[ii,1]

        for ii in range(len(self.Magic)):#self.N_Magic-1):
            self.Magic[ii]=copy.copy(Dict_M[Data.MagicData[ii,0]])
            self.Magic[ii].LV=Data.MagicData[ii,1]

        for ii in range(len(self.Equipment)):#self.N_Equip-1):
            self.Equipment[ii]=copy.copy(Dict_E[Data.EquipmentData[ii,0]])
            self.Equipment[ii].LV=Data.EquipmentData[ii,1]

        for ii in range(15):
            self.Equiped[ii]=copy.copy(Dict_E[Data.EquipedData[ii,0]])
            self.Equiped[ii].LV=Data.EquipedData[ii,1]
        
        self.Data_Base=Data.Data_Base
            
        self.Data_Derive=Data.Data_Derive

        # Base Stats
        self.LV=Data.LV
        self.HP=Data.HP
        self.MP=Data.MP
        self.S=Data.S
        self.P=Data.P
        self.E=Data.E
        self.C=Data.C
        self.I=Data.I
        self.A=Data.A
        self.L=Data.L

        self.DropRate=Data.DropRate
        self.StealRate=Data.StealRate
        self.F_exp=Data.F_exp
        self.F_money=Data.F_money
        self.F_PTstat=Data.F_PTstat
        self.F_PTequip=Data.F_PTequip
        self.F_PTmag=Data.F_PTmag
        self.HPreg=Data.HPreg
        self.MPreg=Data.MPreg
        self.Moneyreg=Data.Moneyreg

        # Derived stats
        self.HPmax=Data.HPmax
        self.MPmax=Data.MPmax
        
        self.A_Phys=Data.A_Phys
        self.A_Cold=Data.A_Cold
        self.A_Fire=Data.A_Fire
        self.A_Ligh=Data.A_Ligh
        self.A_Pois=Data.A_Pois
        self.A_Holy=Data.A_Holy
        self.A_Dark=Data.A_Dark
        self.D_Phys=Data.D_Phys
        self.D_Cold=Data.D_Cold
        self.D_Fire=Data.D_Fire
        self.D_Ligh=Data.D_Ligh
        self.D_Pois=Data.D_Pois
        self.D_Holy=Data.D_Holy
        self.D_Dark=Data.D_Dark
        self.P_Phys=Data.P_Phys
        self.P_Cold=Data.P_Cold
        self.P_Fire=Data.P_Fire
        self.P_Ligh=Data.P_Ligh
        self.P_Pois=Data.P_Pois
        self.P_Holy=Data.P_Holy
        self.P_Dark=Data.P_Dark

        self.Update()
        self.LoadImg(CWDnow)

    def Vcalc(self,vector):
        return (vector[0]+vector[1]+vector[2])*(vector[3]+vector[4]+vector[5])/100

    def Update(self): #re-calculate parameters based on data, without modifying any source, need to be called if anything changed
        
               
        #update basis parameters
        self.LV=self.Vcalc(self.Data_Base[0][:])
        self.HP=self.Vcalc(self.Data_Base[1][:])
        self.MP=self.Vcalc(self.Data_Base[2][:])
        self.S= self.Vcalc(self.Data_Base[3][:]) 
        self.P= self.Vcalc(self.Data_Base[4][:])
        self.E= self.Vcalc(self.Data_Base[5][:])
        self.C= self.Vcalc(self.Data_Base[6][:])
        self.I= self.Vcalc(self.Data_Base[7][:])
        self.A= self.Vcalc(self.Data_Base[8][:])
        self.L= self.Vcalc(self.Data_Base[9][:])

        self.DropRate=self.Vcalc(self.Data_Base[10][:])
        self.StealRate=self.Vcalc(self.Data_Base[11][:])
        self.F_exp=self.Vcalc(self.Data_Base[12][:])
        self.F_money=self.Vcalc(self.Data_Base[13][:])
        self.F_PTstat=self.Vcalc(self.Data_Base[14][:])
        self.F_PTequip=self.Vcalc(self.Data_Base[15][:])
        self.F_PTmag=self.Vcalc(self.Data_Base[16][:])
        
        self.Moneyreg=self.Vcalc(self.Data_Base[19][:])

        # Update derived base data 
        self.Data_Derive[0][0]=self.E*10+100  #maxHP
        self.Data_Derive[1][0]=self.I*10+20  #maxMP
        self.Data_Derive[2][0]=self.S+self.A/2+5 #A-phy
        #self.Data_Derive[3][0]=0   # By default nobody can have natural elemental attack, we also don't want to update this everything in case some monster have it initially
        #self.Data_Derive[4][0]=0
        #self.Data_Derive[5][0]=0
        #self.Data_Derive[6][0]=0
        #self.Data_Derive[7][0]=0
        #self.Data_Derive[8][0]=0
        self.Data_Derive[9][0]=self.E/10+self.P/20  #D-phy
        self.Data_Derive[10][0]=self.I/50 #D-cold
        self.Data_Derive[11][0]=self.I/50 #D-fire
        self.Data_Derive[12][0]=self.I/50 #D-ligh
        self.Data_Derive[13][0]=self.I/50+self.E/10 #D-pois
        self.Data_Derive[14][0]=self.C/30 #D-Holy
        self.Data_Derive[15][0]=-self.C/30  #D-Dark
        self.Data_Derive[16][0]=100+self.S/500 
        self.Data_Derive[17][0]=50+self.I/500
        self.Data_Derive[18][0]=50+self.I/500
        self.Data_Derive[19][0]=50+self.I/500
        self.Data_Derive[20][0]=50+self.I/500+self.E/500
        self.Data_Derive[21][0]=50+self.C/300
        self.Data_Derive[22][0]=50-self.C/300

        # Update derived parameters
        self.HPmax=self.Vcalc(self.Data_Derive[0][:])
        self.MPmax=self.Vcalc(self.Data_Derive[1][:])

        # default regan
        self.Data_Base[17,0]=int(self.HPmax/20)
        self.Data_Base[18,0]=int(self.MPmax/100)
        self.HPreg=self.Vcalc(self.Data_Base[17][:])
        self.MPreg=self.Vcalc(self.Data_Base[18][:])

        
        self.A_Phys=self.Vcalc(self.Data_Derive[2][:])
        self.A_Cold=self.Vcalc(self.Data_Derive[3][:])
        self.A_Fire=self.Vcalc(self.Data_Derive[4][:])
        self.A_Ligh=self.Vcalc(self.Data_Derive[5][:])
        self.A_Pois=self.Vcalc(self.Data_Derive[6][:])
        self.A_Holy=self.Vcalc(self.Data_Derive[7][:])
        self.A_Dark=self.Vcalc(self.Data_Derive[8][:])
        self.D_Phys=self.Vcalc(self.Data_Derive[9][:])
        self.D_Cold=self.Vcalc(self.Data_Derive[10][:])
        self.D_Fire=self.Vcalc(self.Data_Derive[11][:])
        self.D_Ligh=self.Vcalc(self.Data_Derive[12][:])
        self.D_Pois=self.Vcalc(self.Data_Derive[13][:])
        self.D_Holy=self.Vcalc(self.Data_Derive[14][:])
        self.D_Dark=self.Vcalc(self.Data_Derive[15][:])
        self.P_Phys=self.Vcalc(self.Data_Derive[16][:])
        self.P_Cold=self.Vcalc(self.Data_Derive[17][:])
        self.P_Fire=self.Vcalc(self.Data_Derive[18][:])
        self.P_Ligh=self.Vcalc(self.Data_Derive[19][:])
        self.P_Pois=self.Vcalc(self.Data_Derive[20][:])
        self.P_Holy=self.Vcalc(self.Data_Derive[21][:])
        self.P_Dark=self.Vcalc(self.Data_Derive[22][:])

        # calculate Action Point limit based on A
        if self.A<100:
            self.Data_Derive[23,0]=1            
        else:
            self.Data_Derive[23,0]=int(math.log10(self.A))
        
        self.N_ActionPT=int(self.Vcalc(self.Data_Derive[23][:]))

        # try level up
        self.Levelup()

        # check if you are dead, if so, call dead to leave remains return False, then outside program will delete this player after salvage
        # if alive, return true (live person update is OK)
        if self.HP<=0:
            self.REM=self.Died()
            return False
        else:
            return True

    def Rest(self):
        # refill action points
        self.ActPT=self.N_ActionPT
        #HP and MP regan if you have it
        if self.HP<self.HPmax:
            self.Data_Base[1,0]+=self.HPreg
        if self.MP<self.MPmax:
            self.Data_Base[2,0]+=self.MPreg

    def Rest_Full(self):
        # refill action points
        self.ActPT=self.N_ActionPT
        #HP and MP regan if you have it
        self.Data_Base[1,0]=self.HPmax
        self.Data_Base[2,0]=self.MPmax

    def ApplyEffect(self,Effect: Effects): # recieve effects, good ,bad, everything, but will not update Player
        
        # first see if requirements are met  #this is only applicable to Equipments, magic and item eft should have 0 requirements
        if Effect.Type=='Equip':
            Success=self.LV>=Effect.V_EqRequirement[0]
            Success=Success and self.S>=Effect.V_EqRequirement[1]
            Success=Success and self.P>=Effect.V_EqRequirement[2]
            Success=Success and self.E>=Effect.V_EqRequirement[3]
            #Success=Success and self.C>=Effect.V_EqRequirement[4]
            if Effect.V_EqRequirement[4]>0:
                Success=Success and self.C>=Effect.V_EqRequirement[4]
            elif Effect.V_EqRequirement[4]<0:
                Success=Success and self.C<=Effect.V_EqRequirement[4]
            else:  #equal to 0 means no C requirement
                Success=Success and True

            Success=Success and self.I>=Effect.V_EqRequirement[5]
            Success=Success and self.A>=Effect.V_EqRequirement[6]
            Success=Success and self.L>=Effect.V_EqRequirement[7]
        else:
            Success=True
        # apply effect 
        if Success:
            # get prof vector
            V_Prof=np.array([self.P_Phys,self.P_Cold,self.P_Fire,self.P_Ligh,self.P_Pois,self.P_Holy,self.P_Dark])
            V_Def=np.array([self.D_Phys,self.D_Cold,self.D_Fire,self.D_Ligh,self.D_Pois,self.D_Holy,self.D_Dark])
            # do attack effect
            FinalAttack=0
            for ii in range(len(Effect.V_Attack)):
                FinalAttack+=max(0,Effect.V_Attack[ii]-V_Def[ii]*max(V_Prof[ii]/100,1))#*max((200-V_Prof[ii])/100,0.1)-V_Def[ii])  # no point increase Prof over 190 for Def
            
            #print(Effect.V_Attack)
            #print(FinalAttack)
            self.Data_Base[1][0]-=FinalAttack  # take final attach from Base HP, HP will be affected when Update

            if self.Data_Base[17,2]<0: # already poisoned
                if Effect.M_basis[17,2]<self.Data_Base[17,2]: #stronger poison
                    self.Data_Base[17,2]=0  #get rid of original poison
                else:
                    Effect.M_basis[17,2]=0  #do not apply new poison


            # do stats effect
            self.Data_Base+=Effect.M_basis
            self.Data_Derive+=Effect.M_derived
            # probably no need to update here, leave it to idle loop
            self.Update()

            # no need to do error msg here, the calling function will know Success and do it 

        # return Boolean success or not
        return Success

    def LoadImg(self,filepath):
        self.Img=Image.open(filepath+self.Pic)
        self.PImg=ImageTk.PhotoImage(self.Img.resize((60,60)))

        for ii in range(len(self.Item)):
            self.Item[ii].Img=Image.open(filepath+self.Item[ii].Pic)
            self.Item[ii].PImg=ImageTk.PhotoImage(self.Item[ii].Img)
        
        for ii in range(len(self.Magic)):
            self.Magic[ii].Img=Image.open(filepath+self.Magic[ii].Pic)
            self.Magic[ii].PImg=ImageTk.PhotoImage(self.Magic[ii].Img)
        
        for ii in range(len(self.Equipment)):
            self.Equipment[ii].Img=Image.open(filepath+self.Equipment[ii].Pic)
            self.Equipment[ii].PImg=ImageTk.PhotoImage(self.Equipment[ii].Img)

        for ii in range(len(self.Equiped)):
            self.Equiped[ii].Img=Image.open(filepath+self.Equiped[ii].Pic)
            self.Equiped[ii].PImg=ImageTk.PhotoImage(self.Equiped[ii].Img)

    def UpdateGUI(self,GUIs: GUIgroup): # Print out to GUIs
        # basic update
        GUIs.Canv_Pic.update()
        W=GUIs.Canv_Pic.winfo_width()
        H=GUIs.Canv_Pic.winfo_height()
        tempImg=self.Img.resize((W-4,H-4))
        self.PImg=ImageTk.PhotoImage(tempImg)
        GUIs.Canv_Pic.create_image(2,2,anchor=tk.NW,image=self.PImg)
        GUIs.Lab_Name.config(text=self.Name)#+'(AP'+str(self.ActPT)+'/'+str(self.N_ActionPT)+')')
        if self.Angry:
            GUIs.Lab_Name.config(bg='red')
        else:
            GUIs.Lab_Name.config(bg='green')
        GUIs.Lab_Nickname.config(text=self.NickName)

        GUIs.Lab_HP.config(text='HP:'+ str(int(self.HP))+'/'+str(int(self.HPmax)))
        GUIs.Pbar_HP.config(maximum=int(self.HPmax))
        GUIs.Pbar_HP['value']=int(self.HP)
        GUIs.Pbar_HP.update_idletasks()

        GUIs.Lab_MP.config(text='MP:'+ str(int(self.MP))+'/'+str(int(self.MPmax)))
        GUIs.Pbar_MP.config(maximum=int(self.MPmax))
        GUIs.Pbar_MP['value']=int(self.MP)
        GUIs.Pbar_MP.update_idletasks()

        GUIs.Lab_AP.config(text='AP '+str(int(self.ActPT))+'/'+str(int(self.N_ActionPT)))
        if self.ActPT>0:
            GUIs.Lab_AP.config(bg='springgreen')
        else:
            GUIs.Lab_AP.config(bg='red')

                                
        # updates in the Tab for active players
        for ii in range(15):
            if self.Equiped[ii].ID!=0:
                
                GUIs.Canv_Equiped[ii].update()
                W=GUIs.Canv_Equiped[ii].winfo_width()
                H=GUIs.Canv_Equiped[ii].winfo_height()
                tempImg=self.Equiped[ii].Img.resize((W-4,H-4))
                self.Equiped[ii].PImg=ImageTk.PhotoImage(tempImg)

                GUIs.Canv_Equiped[ii].create_image(2,2,anchor=tk.NW,image=self.Equiped[ii].PImg)  #will fix later
            else:
                GUIs.Canv_Equiped[ii].delete("all")
        
        GUIs.List_Equip.delete(0,'end')
        
        for ii in range(len(self.Equipment)):
            # get the ID from my Item
            if self.Equipment[ii].ID==0:
                temp_str=''
            else:
                temp_str=self.Equipment[ii].Name# + '(LV'+str(self.Equipment[ii].LV)+')'
            # put Item name in the list
            GUIs.List_Equip.insert('end',temp_str)

        GUIs.List_Item.delete(0,'end')
        for ii in range(len(self.Item)):
            # get the ID from my Item
            temp_str=self.Item[ii].Name
            # put Item name in the list
            GUIs.List_Item.insert('end',temp_str)

        GUIs.List_Magic.delete(0,'end')
        for ii in range(len(self.Magic)):
            # get the ID from my Item
            if self.Magic[ii].Name=='':
                temp_str=''
            else:
                temp_str=self.Magic[ii].Name# + '(LV'+str(self.Magic[ii].LV)+')'
            # put Item name in the list
            GUIs.List_Magic.insert('end',temp_str)

        temp=[self.S,self.P,self.E, self.C,self.I,self.A,self.L]
        for ii in range(7):
            GUIs.Lab_Stat[ii].config(text=str(int(temp[ii])))

        temp=[self.A_Phys,self.A_Cold,self.A_Fire, self.A_Ligh,self.A_Pois,self.A_Holy,self.A_Dark]
        for ii in range(7):
            GUIs.Lab_Att[ii].config(text=str(int(temp[ii])))

        temp=[self.D_Phys,self.D_Cold,self.D_Fire, self.D_Ligh,self.D_Pois,self.D_Holy,self.D_Dark]
        for ii in range(7):
            GUIs.Lab_Def[ii].config(text=str(int(temp[ii])))

        temp=[self.P_Phys,self.P_Cold,self.P_Fire, self.P_Ligh,self.P_Pois,self.P_Holy,self.P_Dark]
        for ii in range(7):
            GUIs.Lab_Prof[ii].config(text=str(int(temp[ii])))

        GUIs.Lab_Money.config(text='$ '+str(int(self.Money)))
        GUIs.Lab_PTstat.config(text='SP:'+str(int(self.PT_stat)))
        GUIs.Lab_PTequip.config(text='EP:'+str(int(self.PT_equip)))
        GUIs.Lab_PTmag.config(text='MgP:'+str(int(self.PT_mag)))

        if self.Exp>=0:
            GUIs.Lab_LVexp.config(text='LV'+str(int(self.LV))+'('+str(int(self.Exp))+'/'+str(int(self.ExpNext))+')')
        else:
            GUIs.Lab_LVexp.config(text='LV'+str(int(self.LV))+'('+str(int(-self.Exp))+')')
        GUIs.Lab_HPreg.config(text='HP-Reg:'+str(int(self.HPreg)))
        GUIs.Lab_MPreg.config(text='MP-Reg:'+str(int(self.MPreg)))
        GUIs.Lab_DropR.config(text='Dp:'+str(int(self.DropRate))+'%')


        N=0
        for ii in range(len(self.Item)):
            if self.Item[ii].ID!=0:
                N+=1
        GUIs.Lab_ItemInv.config(text='Item:'+str(N)+'/'+str(self.N_Item))
        N=0
        for ii in range(len(self.Magic)):
            if self.Magic[ii].ID!=0:
                N+=1
        GUIs.Lab_MagicInv.config(text='Magic:'+str(N)+'/'+str(self.N_Magic))
        N=0
        for ii in range(len(self.Equipment)):
            if self.Equipment[ii].ID!=0:
                N+=1
        GUIs.Lab_EquipInv.config(text='Equipment:'+str(N)+'/'+str(self.N_Equip))

    def UpdateGUI_Basic(self,GUIs): # Print out to GUIs
        # basic update
        GUIs.Canv_Pic.update()
        W=GUIs.Canv_Pic.winfo_width()
        H=GUIs.Canv_Pic.winfo_height()
        tempImg=self.Img.resize((W-4,H-4))
        self.PImg=ImageTk.PhotoImage(tempImg)

        GUIs.Canv_Pic.create_image(2,2,anchor=tk.NW,image=self.PImg)
        GUIs.Lab_Name.config(text=self.Name)#+'(AP'+str(self.ActPT)+'/'+str(self.N_ActionPT)+')')
        if self.Angry:
            GUIs.Lab_Name.config(bg='red')
        else:
            GUIs.Lab_Name.config(bg='green')
        GUIs.Lab_Nickname.config(text=self.NickName)

        GUIs.Lab_HP.config(text='HP:'+ str(int(self.HP))+'/'+str(int(self.HPmax)))
        GUIs.Pbar_HP.config(maximum=int(self.HPmax))
        GUIs.Pbar_HP['value']=int(self.HP)
        GUIs.Pbar_HP.update_idletasks()

        GUIs.Lab_MP.config(text='MP:'+ str(int(self.MP))+'/'+str(int(self.MPmax)))
        GUIs.Pbar_MP.config(maximum=int(self.MPmax))
        GUIs.Pbar_MP['value']=int(self.MP)
        GUIs.Pbar_MP.update_idletasks()

        GUIs.Lab_AP.config(text='AP '+str(int(self.ActPT))+'/'+str(int(self.N_ActionPT)))
        if self.ActPT>0:
            GUIs.Lab_AP.config(bg='springgreen')
        else:
            GUIs.Lab_AP.config(bg='red')

    def RemoveBuff(self): # Remove all temporary buff from Magic and Item use, Will not update effects 
        self.Data_Base[:,2]=0
        self.Data_Base[:,5]=0
        self.Data_Derive[:,2]=0
        self.Data_Derive[:,5]=0

        self.onDef=False

    def Attack(self): # normal attack, return Effect
        self.Update()  # need update here becaue will use SPECIAL
        eft=Effects()
        eft.Type='Attack'
        eft.Nullify()
        temp_v=np.array([self.LV,self.S,self.P,self.E,self.C,self.I,self.A,self.L,self.DropRate,self.DeathImmune])
        eft.V_OwnerStat=temp_v

        # should add prof impact
        V_Prof=np.array([self.P_Phys,self.P_Cold,self.P_Fire,self.P_Ligh,self.P_Pois,self.P_Holy,self.P_Dark])
        
        temp_v=np.array([self.A_Phys,self.A_Cold,self.A_Fire,self.A_Ligh,self.A_Pois,self.A_Holy,self.A_Dark])

        for ii in range(len(temp_v)):
            temp_v[ii]=int(temp_v[ii]*V_Prof[ii]/100)   #no upper bound on how high you can go

        eft.V_Attack=temp_v

        return eft

    def Defend(self):
        if not self.onDef:
            # increase temp def
            for ii in range(7):
                self.Data_Derive[9+ii,5]+=100

            self.Update()
            self.onDef=True
            return True
        else:
            return False

    def Magic_Use(self,index): #use magic [index] player has, return Effect
        
        eft=self.Magic[index].Effect()
        cost=self.Magic[index].Get_MPcost()

        # see if you can use this magic at all

        # first see if requirements are met
        Success=self.LV>=eft.V_EqRequirement[0]
        Success=Success and self.S>=eft.V_EqRequirement[1]
        Success=Success and self.P>=eft.V_EqRequirement[2]
        Success=Success and self.E>=eft.V_EqRequirement[3]
        #Success=Success and self.C>=eft.V_EqRequirement[4]
        if eft.V_EqRequirement[4]>0:
            Success=Success and self.C>=eft.V_EqRequirement[4]
        elif eft.V_EqRequirement[4]<0:
            Success=Success and self.C<=eft.V_EqRequirement[4]
        else:  #equal to 0 means no C requirement
            Success=Success and True

        Success=Success and self.I>=eft.V_EqRequirement[5]
        Success=Success and self.A>=eft.V_EqRequirement[6]
        Success=Success and self.L>=eft.V_EqRequirement[7]
        Success=Success and self.MP>cost

        if Success:
            # set the Owner stats 
            eft.V_OwnerStat=np.array([self.LV,self.S,self.P,self.E,self.C,self.I,self.A,self.L,self.DropRate,self.DeathImmune])

            # use self professioncy and special to adjust
            V_Prof=np.array([self.P_Phys,self.P_Cold,self.P_Fire,self.P_Ligh,self.P_Pois,self.P_Holy,self.P_Dark])

            for ii in range(len(V_Prof)):
                eft.V_Attack[ii]=int(eft.V_Attack[ii]*V_Prof[ii]/100)
            
            self.Data_Base[2,0]-=cost
            self.Update()
            
        else:
            eft.Nullify() #need to let outside know it failed
            
            messagebox.showinfo('Failed','Magic requirements not met or not enough MP!')

        return eft 

        #return effect

    def Magic_Forget(self,index): # forget magic to get Mag Points
        if index>=0 and index<=len(self.Magic)-1:
            self.Magic[index]=Magic()
        else:
            messagebox.showerror('Magic Error','Forget Magic out of bound index '+str(index))
                
    def Magic_Learn(self,NewMagic): # learn new magic with magic ID
        N=0
        for x in self.Magic:
            if x.ID==0:
                N+=1

        if N==0:
            messagebox.showinfo('Magic slot full','You reached maximum # of Magic.\nForget one Magic if you want to learn a new one!')
            
        else:
            foundit=False
            for ii in range(len(self.Magic)):
                if self.Magic[ii].ID==0 and not foundit:
                    index=ii
                    foundit=True
            
            self.Magic[index]=copy.copy(NewMagic)
            #messagebox.showinfo('New Magic','You learnt New Magic: '+ NewMagic.Name +'!')

    def Magic_EmptySlot(self):
        index=-1
        foundit=False
        
        for ii in range(len(self.Magic)):
            if self.Magic[ii].ID==0 and not foundit:
                index=ii
                foundit=True
        
        return index

    def Magic_Count(self):
        count=0

        for ii in range(len(self.Magic)):
            if self.Magic[ii].ID!=0:
                count+=1
        
        return count

    def Item_Use(self,index): # use Item [index], return Effect
        if index>=0 and index<=len(self.Item)-1:
            eft=self.Item[index].Effect()
            self.Item[index]=Item()
            # use ID and LV to go to ItemData to get effect
            # return effect
            return eft
        else:
            messagebox.showerror('Item Error','Use Item out of bound index '+str(index))

    def Item_Sell(self,index): # Sell an item for $
        if index>=0 and index<=len(self.Item)-1:
            cost=self.Item[index].Get_Cost()
            self.Item[index]=Item()
            # use ID and LV to go to ItemData to get $$
            # get $$
            self.Money+=cost
        else:
            messagebox.showerror('Item Error','Use Item out of bound index '+str(index))
    
    def Item_Obtain(self,NewItem): # get Item with item ID
        N=0
        for x in self.Item:
            if x.ID==0:
                N+=1

        if N==0:
            messagebox.showinfo('Inventory full','Your backpack is full.\nUse or throw away items if you want to get a new one!')
        else:
            foundit=False
            for ii in range(len(self.Item)):
                if self.Item[ii].ID==0 and not foundit:
                    index=ii
                    foundit=True
            
            self.Item[index]=copy.deepcopy(NewItem)

    def Item_EmptySlot(self):
        index=-1
        foundit=False
        
        for ii in range(len(self.Item)):
            if self.Item[ii].ID==0 and not foundit:
                index=ii
                foundit=True
        
        return index

    def Item_RemoveList(self,index):
            if index>=0 and index<=len(self.Item)-1:
                self.Item[index]=Item()

    def Item_Count(self):
        count=0

        for ii in range(len(self.Item)):
            if self.Item[ii].ID!=0:
                count+=1
        
        return count

    def Equipment_Equip(self,index): # put on Equipment and apply effects
        
        #self.Equipment[index]  #this is the equipment object
        location=self.Equipment[index].Loc
        
        if location<0:
            messagebox.showinfo('Cant Equip','Nothing to equip!')
            return False

        eft=self.Equipment[index].Effect_PutOn()
        
        if self.ApplyEffect(eft):  # if you can equip
            

            if self.Equiped[location].ID==0: #the slot is empty
                self.Equiped[location]=copy.copy(self.Equipment[index])
                
                self.Equipment_RemoveList(index)  # this ensures there is space in invertory                
            else:
                
                temp_eq=copy.copy(self.Equiped[location])
                self.Equiped[location]=copy.copy(self.Equipment[index])
                self.Equipment_RemoveList(index)  # this ensures there is space in invertory
                self.Equipment_Obtain(temp_eq)
            
            return True

            # self.Update()  #no need to do this as it will be in main recurring idle loop
        else:
            messagebox.showinfo('Cant Equip','Your status is not enough to equip this yet!')
            return False

    def Equipment_Takeoff(self,Loc): # Take off Equipment at Loc
        N=0
        for x in self.Equipment:
            if x.ID==0:
                N+=1

        if N==0:
            messagebox.showinfo('Inventory full','Cannot take off, inventory full.')
            return False
        else:
            
            if self.Equiped[Loc].ID!=0:
                eft=self.Equiped[Loc].Effect_TakeOff()
                if self.ApplyEffect(eft):
                    self.Equipment_Obtain(self.Equiped[Loc])
                    self.Equiped[Loc]=Equipment()

                    return True
                    #self.Update()
                else:
                    messagebox.showinfo('Unable to take off','For some reason you cannot take this equipment off!')
                    return False
            else:
                messagebox.showinfo('Unable to take off','Empty slot, nothing to take off!')
                return False

    def Equipment_RemoveList(self,index):
        if index>=0 and index<=len(self.Equipment)-1:
            self.Equipment[index]=Equipment()

    def Equipment_Sell(self,index): # Sell an eq for eq point, you can only sell when it is in inventory
        if index>=0 and index<=len(self.Equipment)-1:
            
            if self.Equipment[index].ID!=0:
                self.Money+=self.Equipment[index].Get_Cost()
                self.Equipment[index]=Equipment() 
            else:
                messagebox.showinfo('Cant sell','No item to sell')
                
        else:
            messagebox.showinfo('Cant sell','Item index not valid')
    
    def Equipment_Obtain(self,NewEquip:Equipment): # get eq with eq ID
        N=0
        for x in self.Equipment:
            if x.ID==0:
                N+=1

        if N==0:
            messagebox.showinfo('Inventory full','Your backpack is full.\nUse or throw away Equipment if you want to get a new one!')
            
        else:
            foundit=False
            for ii in range(len(self.Equipment)):
                if self.Equipment[ii].ID==0 and not foundit:
                    index=ii
                    foundit=True
            
            self.Equipment[index]=copy.copy(NewEquip)

    def Equipment_EmptySlot(self):
        index=-1
        foundit=False
        
        for ii in range(len(self.Equipment)):
            if self.Equipment[ii].ID==0 and not foundit:
                index=ii
                foundit=True
        
        return index

    def Equipment_Count(self):
        count=0

        for ii in range(len(self.Equipment)):
            if self.Equipment[ii].ID!=0:
                count+=1
        
        return count

    def Equiped_Set(self,SetIDs):  #return true if you have all IDs in Set ID equiped

        SetOn=True
        
        for theID in SetIDs:
            gotThis=False
            for ii in range(15):
                if self.Equiped[ii].ID==theID:
                    gotThis=True
            SetOn=SetOn and gotThis
        
        return SetOn

    def Died(self): # when player die, return Remains, it will be deposite on ground for pick up
        Rm=Remains()
        Rm.Exp=-self.Exp   #this turn monster exp to +
        Rm.Money=self.Money
        Rm.PT_stat=self.PT_stat
        Rm.PT_mag=self.PT_mag
        Rm.PT_equip=self.PT_equip

        for ii in range(len(self.Item)):  #only the real items are in
            if self.Item[ii].ID!=0:
                Rm.Item=np.append(Rm.Item,self.Item[ii])

        for ii in range(len(self.Equipment)):
            if self.Equipment[ii].ID!=0:
                Rm.Equip=np.append(Rm.Equip,self.Equipment[ii])
        
        for ii in range(15):
            if self.Equiped[ii].ID!=0:
                Rm.Equip=np.append(Rm.Equip,self.Equiped[ii])

        #X=np.random.uniform(size=3)
        #if (self.DropRate+Luck_player*5/self.L)/100>X[0]:  #get item  keep droprate<50
        #    
        #if (self.DropRate+Luck_player/self.L)/100>X[1]: #get equip
        #    
        #if (self.DropRate/5+Luck_player/2/self.L)/100>X[2]:  #get equip on player
            
        
        return Rm
    
    def Talk(self,monster): # return two Effects, one for self, one for monster
        
        isEnemy=self.C*monster.C<0
        C1=abs(self.C)
        C2=abs(monster.C)
        if (monster.I+C2)==0:
            temp=25
        else:
            temp=(self.I+C1+5)/(monster.I+C2)
        if temp<0.9:
            X=0.01 #you can recruit anyone with 1% chance
        elif temp<=1:
            X=0.01+1.9*(temp-0.9)  # 20% for equal 
        elif temp<=5:
            X=0.2+0.3/4*(temp-1)  # 50% if you are 4 times
        elif temp<=25:
            X=0.5+0.3/20*(temp-5) # 80% if you are 25 times or above
        else:
            X=0.8
        
        if isEnemy:
            X*=0.9  # your chance drop 80% if C is different

        # your sum need to be 3 times that of monster to have 50 50 chance, S added here to avoid easy recruit of Powerful M

        #X=10000000

        Nx=np.random.random()  #draw from 0-1

        if X>Nx:
            return True #, int(norm.cdf(X)*100)]
        else:
            return False #, int(norm.cdf(X)*100)]

    def ProbCalc(self,monster): #return probability if monster try to do things to self
        # be hit
        if self.P<=0:
            temp=30
        else:
            temp=(monster.A*1.5)/(self.P)  # A decide if you can hit, P decide if you can escape, 1.5 is for attack bonus

        if temp<0.1:
            X=0.1 #you can recruit anyone with 1% chance
        elif temp<=1:
            X=0.1+0.4/0.9*(temp-0.1)  # 50% for equal 
        elif temp<=5:
            X=0.5+0.4/4*(temp-1)  # 90% if you are 4 times
        elif temp<=25:
            X=0.9+0.09/20*(temp-5) # 99% if you are 25 times
        else:
            X=0.999  # always 1/1000 chance to miss
        P_hit=int(X*100)

        # attack
        if monster.P<=0:
            temp=30
        else:
            temp=(self.A*1.5)/(monster.P)  # A decide if you can hit, P decide if you can escape, 1.5 is for attack bonus

        if temp<0.1:
            X=0.1 #you can recruit anyone with 1% chance
        elif temp<=1:
            X=0.1+0.4/0.9*(temp-0.1)  # 50% for equal 
        elif temp<=5:
            X=0.5+0.4/4*(temp-1)  # 90% if you are 4 times
        elif temp<=25:
            X=0.9+0.09/20*(temp-5) # 99% if you are 25 times
        else:
            X=0.999  # always 1/1000 chance to miss
        P_attack=int(X*100)

        #recruit
        isEnemy=self.C*monster.C<0

        C1=abs(self.C)
        C2=abs(monster.C)
        if (self.I+C1+self.L+self.S)==0:
            temp=25
        else:
            temp=(monster.I+C2+monster.S+monster.L+5)/(self.I+C1+self.L+self.S)
        if temp<0.9:
            X=0.01 #you can recruit anyone with 1% chance
        elif temp<=1:
            X=0.01+1.9*(temp-0.9)  # 20% for equal 
        elif temp<=5:
            X=0.2+0.3/4*(temp-1)  # 50% if you are 4 times
        elif temp<=25:
            X=0.5+0.4/20*(temp-5) # 90% if you are 25 times or above
        else:
            X=0.9

        if isEnemy:
            X*=0.5  # your chance drop 50% if C is different

        P_recruit=int(X*100)

        # good talk outcome
        isEnemy=self.C*monster.C<0
        C1=abs(self.C)
        C2=abs(monster.C)
        if (monster.I+C2)==0:
            temp=25
        else:
            temp=(monster.I+C2)/(self.I+C1+5)
        if temp<0.9:
            X=0.01 #you can recruit anyone with 1% chance
        elif temp<=1:
            X=0.01+1.9*(temp-0.9)  # 20% for equal 
        elif temp<=5:
            X=0.2+0.3/4*(temp-1)  # 50% if you are 4 times
        elif temp<=25:
            X=0.5+0.3/20*(temp-5) # 80% if you are 25 times or above
        else:
            X=0.8
        
        if isEnemy:
            X*=0.9  # your chance drop 80% if C is different

        P_talk=int(X*100)

        return [P_hit,P_recruit,P_talk,P_attack]

    def Recruit(self,monster): # return success or not
        #if monster.C!=0:
        #    X=self.C*self.I*self.L/(monster.C*monster.I*monster.L)/50-1  #if opposite C there is no chance, if your CIL is 50 times bigger, your change is 50%
        #else:
        #    X=self.C*self.I*self.L/(monster.I*monster.L)/50-1 
        isEnemy=self.C*monster.C<0

        C1=abs(self.C)
        C2=abs(monster.C)
        if (monster.I+C2+monster.S+monster.L)==0:
            temp=25
        else:
            temp=(self.I+C1+self.L+self.S+5)/(monster.I+C2+monster.S+monster.L)
        if temp<0.9:
            X=0.01 #you can recruit anyone with 1% chance
        elif temp<=1:
            X=0.01+1.9*(temp-0.9)  # 20% for equal 
        elif temp<=5:
            X=0.2+0.3/4*(temp-1)  # 50% if you are 4 times
        elif temp<=25:
            X=0.5+0.4/20*(temp-5) # 90% if you are 25 times or above
        else:
            X=0.9
        
        if isEnemy:
            X*=0.5  # your chance drop 50% if C is different

        # your sum need to be 3 times that of monster to have 50 50 chance, S added here to avoid easy recruit of Powerful M

        #X=10000000

        Nx=np.random.random()  #draw from 0-1

        if X>Nx:
            return True #, int(norm.cdf(X)*100)]
        else:
            return False #, int(norm.cdf(X)*100)]

    def Success_Attack(self,monster): # return success or not
        if monster.P<=0:
            temp=30
        else:
            temp=(self.A*1.5)/(monster.P)  # A decide if you can hit, P decide if you can escape, 1.5 is for attack bonus

        if temp<0.9:
            X=0.01 #you can recruit anyone with 1% chance
        elif temp<=1:
            X=0.01+4.9*(temp-0.9)  # 50% for equal 
        elif temp<=5:
            X=0.5+0.4/4*(temp-1)  # 90% if you are 4 times
        elif temp<=25:
            X=0.9+0.09/20*(temp-5) # 99% if you are 25 times
        else:
            X=0.999  # always 1/1000 chance to miss

        # your sum need to be 3 times that of monster to have 50 50 chance, S added here to avoid easy recruit of Powerful M

        #X=10000000

        Nx=np.random.random()  #draw from 0-1

        if X>Nx:
            return True #, int(norm.cdf(X)*100)]
        else:
            return False #, int(norm.cdf(X)*100)]

    def Judge(self,monster): # initial look at opponent to see if angry or not
        if self.C*monster.C<0:
            self.Angry=True
        else:
            self.Angry=False
        
    def Calc_Value(self):
        self.Value=(self.S+self.P+self.E+self.C+self.I+self.A+self.L)*100

    def Set_string(self,str_data,str_desc): # generate monster using minimal inputs, spical monster can start with this and be changed later
        self.Desc=str_desc
        temp_str=str_data.split(',')

        self.ID=int(temp_str[0])
        self.Name=temp_str[1]
        self.Pic=temp_str[2]
        self.Data_Base[3,0]=int(temp_str[3])
        self.Data_Base[4,0]=int(temp_str[4])
        self.Data_Base[5,0]=int(temp_str[5])
        self.Data_Base[6,0]=int(temp_str[6])
        self.Data_Base[7,0]=int(temp_str[7])
        self.Data_Base[8,0]=int(temp_str[8])
        self.Data_Base[9,0]=int(temp_str[9])
        self.Align=temp_str[10]
        self.Zone=int(temp_str[11])
        self.Tier=int(temp_str[12])
        self.Data_Base[0,0]=1  #all txt loaded monster at LV1

        if self.Align=='Cold':
            self.Data_Derive[3,1]=int(self.Data_Base[3,0]/3)  # half S attack
            self.Data_Derive[10,1]=int(self.Data_Base[5,0]/3) # half E defense
            self.Data_Derive[17,1]=40                 # 50+60% professioncy

            self.Data_Derive[11,1]=-int(self.Data_Base[5,0]/3)
            self.Data_Derive[18,1]=-30

        if self.Align=='Fire':
            self.Data_Derive[4,1]=int(self.Data_Base[3,0]/3)  # half S attack
            self.Data_Derive[11,1]=int(self.Data_Base[5,0]/3) # half E defense
            self.Data_Derive[18,1]=40                 # 30% professioncy

            self.Data_Derive[10,1]=-int(self.Data_Base[5,0]/3)
            self.Data_Derive[17,1]=-30

        if self.Align=='Ligh':
            self.Data_Derive[5,1]=int(self.Data_Base[3,0]/3)  # half S attack
            self.Data_Derive[12,1]=int(self.Data_Base[5,0]/3) # half E defense
            self.Data_Derive[19,1]=40                 # 30% professioncy

            self.Data_Derive[13,1]=-int(self.Data_Base[5,0]/3)
            self.Data_Derive[20,1]=-30

        if self.Align=='Pois':
            self.Data_Derive[6,1]=int(self.Data_Base[3,0]/3)  # half S attack
            self.Data_Derive[13,1]=int(self.Data_Base[5,0]/3) # half E defense
            self.Data_Derive[20,1]=40                 # 30% professioncy

            self.Data_Derive[12,1]=-int(self.Data_Base[5,0]/3)
            self.Data_Derive[19,1]=-30

        if self.Align=='Holy':
            self.Data_Derive[7,1]=int(self.Data_Base[3,0]/3)  # half S attack
            self.Data_Derive[14,1]=int(self.Data_Base[5,0]/3) # half E defense
            self.Data_Derive[21,1]=40                 # 30% professioncy

            self.Data_Derive[15,1]=-int(self.Data_Base[5,0]/3)
            self.Data_Derive[22,1]=-30
        if self.Align=='Dark':
            self.Data_Derive[8,1]=int(self.Data_Base[3,0]/3)  # half S attack
            self.Data_Derive[15,1]=int(self.Data_Base[5,0]/3) # half E defense
            self.Data_Derive[22,1]=40                 # 30% professioncy

            self.Data_Derive[14,1]=-int(self.Data_Base[5,0]/3)
            self.Data_Derive[21,1]=-30

        self.Update() # do initial calc
        # fill in default values here
        self.Data_Base[1,0]=self.HPmax
        self.Data_Base[2,0]=self.MPmax
        self.Data_Base[10,0]=25  #drop rate default=25% for monsters
        self.Data_Base[11,0]=100   #Steal rate default=100%, monster will not use this anyway
        self.Data_Base[12:17,0]=100
        

        self.Money=self.Zone*1000
        self.Exp=self.Zone*100
        self.PT_mag=self.Zone*10
        self.PT_stat=int(self.Zone/5)
        self.PT_equip=self.Zone*10

        self.Update() # do initial calc
       
    def GotoLV(self,Level):  #this is only used for Monster to go to a given level from LV1
        if Level<=1:
            return

        self.Data_Base[0,0]=Level
        self.Update() # finalize all level calc

        #do Febinachi calc
        number=0
        for ii in range(Level):
            number+=ii
        
        #print(number)

        self.Data_Base[3,0]=int(self.Data_Base[3,0]+number*5)#*Level**0.5)
        self.Data_Base[4,0]=int(self.Data_Base[4,0]+number*5)#*Level**0.5)
        self.Data_Base[5,0]=int(self.Data_Base[5,0]+number*10)#*Level**0.5)  #more HP to play
        self.Data_Base[6,0]=int(self.Data_Base[6,0]+np.sign(self.Data_Base[6,0])*number*5)#*Level**0.5)
        self.Data_Base[7,0]=int(self.Data_Base[7,0]+number*5)#*Level**0.5)
        self.Data_Base[8,0]=int(self.Data_Base[8,0]+number*5)#*Level**0.5)
        self.Data_Base[9,0]=int(self.Data_Base[9,0]+number*5)#*Level**0.5)

        #note following is added Alignment bonus

        if self.Align=='Cold':
            self.Data_Derive[3,1]+=int(self.Data_Base[3,0]/20*Level)  # half S attack
            self.Data_Derive[10,1]+=int(self.Data_Base[5,0]/20*Level) # half E defense
            self.Data_Derive[17,1]+=1*Level                 # 50+60% professioncy
        if self.Align=='Fire':
            self.Data_Derive[4,1]+=int(self.Data_Base[3,0]/20*Level)  # half S attack
            self.Data_Derive[11,1]+=int(self.Data_Base[5,0]/20*Level) # half E defense
            self.Data_Derive[18,1]+=1*Level                 # 30% professioncy
        if self.Align=='Ligh':
            self.Data_Derive[5,1]+=int(self.Data_Base[3,0]/20*Level)  # half S attack
            self.Data_Derive[12,1]+=int(self.Data_Base[5,0]/20*Level) # half E defense
            self.Data_Derive[19,1]+=1*Level                 # 30% professioncy
        if self.Align=='Pois':
            self.Data_Derive[6,1]+=int(self.Data_Base[3,0]/20*Level)  # half S attack
            self.Data_Derive[13,1]+=int(self.Data_Base[5,0]/20*Level) # half E defense
            self.Data_Derive[20,1]+=1*Level                 # 30% professioncy
        if self.Align=='Holy':
            self.Data_Derive[7,1]=int(self.Data_Base[3,0]/20*Level)  # half S attack
            self.Data_Derive[14,1]=int(self.Data_Base[5,0]/20*Level) # half E defense
            self.Data_Derive[21,1]=1*Level                 # 30% professioncy
        if self.Align=='Dark':
            self.Data_Derive[8,1]+=int(self.Data_Base[3,0]/20*Level)  # half S attack
            self.Data_Derive[15,1]+=int(self.Data_Base[5,0]/20*Level) # half E defense
            self.Data_Derive[22,1]+=1*Level                 # 30% professioncy
            #print(self.Data_Derive[22,1])
        
        # now do some random generation here
        Rn=np.random.uniform(size=5)  # one sample from Uniform dist
        self.Money+=int((Level-1)*1000*Rn[0])
        self.Exp+=int((Level-1)*10*Rn[1])
        self.PT_mag+=int((Level-1)*10*Rn[2])
        self.PT_stat+=int((Level-1)*10*Rn[3])
        self.PT_equip+=int((Level-1)*10*Rn[4])

        self.Update()  #just to be sure, update everything

    def EquipmentOK(self,InputEQ: Equipment):

        Success=self.LV>=InputEQ.Requirement[0]
        Success=Success and self.S>=InputEQ.Requirement[1]
        Success=Success and self.P>=InputEQ.Requirement[2]
        Success=Success and self.E>=InputEQ.Requirement[3]
        #Success=Success and self.C>=InputEQ.Requirement[4]
        if InputEQ.Requirement[4]>0:
            Success=Success and self.C>=InputEQ.Requirement[4]
        elif InputEQ.Requirement[4]<0:
            Success=Success and self.C<=InputEQ.Requirement[4]
        else:  #equal to 0 means no C requirement
            Success=Success and True

        Success=Success and self.I>=InputEQ.Requirement[5]
        Success=Success and self.A>=InputEQ.Requirement[6]
        Success=Success and self.L>=InputEQ.Requirement[7]

        return Success
    
    def MagicOK(self,InputMag: Magic):

        Success=self.LV>=InputMag.Requirement[0]
        Success=Success and self.S>=InputMag.Requirement[1]
        Success=Success and self.P>=InputMag.Requirement[2]
        Success=Success and self.E>=InputMag.Requirement[3]
        #Success=Success and self.C>=InputMag.Requirement[4]
        if InputMag.Requirement[4]>0:
            Success=Success and self.C>=InputMag.Requirement[4]
        elif InputMag.Requirement[4]<0:
            Success=Success and self.C<=InputMag.Requirement[4]
        else:  #equal to 0 means no C requirement
            Success=Success and True

        Success=Success and self.I>=InputMag.Requirement[5]
        Success=Success and self.A>=InputMag.Requirement[6]
        Success=Success and self.L>=InputMag.Requirement[7]

        return Success

    def Randomize(self,Dict_Equip,Dict_Item,Dict_Mag,IsBoss=False): #only used for Monster to get random eqipment,Magic,and Item, equiped
        Nitem=len(Dict_Item)
        Nmag=len(Dict_Mag)
        Nequip=len(Dict_Equip)
        
        #print('initial count (should all be 0):')
        #print('Item--'+str(self.Item_Count()))
        #print('Mag--'+str(self.Magic_Count()))
        #print('EQ--'+str(self.Equipment_Count()))
        #print('Now start randomize in')
        # Pick Dicts so all things are same or lower tier than monster
        Pool_Item=[]
        for ii in range(Nitem):
            if Dict_Item[ii].Tier<=self.Tier and Dict_Item[ii].ID!=0:
                Pool_Item=np.append(Pool_Item,ii)
        
        Pool_Mag=[]
        for ii in range(Nmag):
            if Dict_Mag[ii].Tier<=self.Tier and Dict_Mag[ii].ID!=0:
                Pool_Mag=np.append(Pool_Mag,ii)

        Pool_Equip=[]
        for ii in range(Nequip):
            if Dict_Equip[ii].Tier<=self.Tier and Dict_Equip[ii].ID!=0:
                Pool_Equip=np.append(Pool_Equip,ii)
        

        N=np.random.randint(1,5)  #1-5 Items
        if IsBoss:
            N=7

        for ii in range(N):
            tempID=np.random.randint(0,len(Pool_Item)-1)
            self.Item_Obtain(Dict_Item[Pool_Item[tempID]])

        N=np.random.randint(1,3)  #1-3 chance to learn Magic, but if the magic has requirement higher than Monster stat, it will not happen
        if IsBoss:
            N=5

        for ii in range(N):
            tempID=np.random.randint(0,len(Pool_Mag)-1)
            if self.MagicOK(Dict_Mag[Pool_Mag[tempID]]):  
                self.Magic_Learn(Dict_Mag[Pool_Mag[tempID]])
        
        
        
        N=np.random.randint(1,5)  #1-5 Equipment
        if IsBoss:
            N=8

        for ii in range(N):
            tempID=np.random.randint(0,len(Pool_Equip)-1)
            self.Equipment_Obtain(Dict_Equip[Pool_Equip[tempID]])

        
        for ii in range(len(self.Equipment)):
            if self.Equipment[ii].ID>0 and self.EquipmentOK(self.Equipment[ii]):
                self.Equipment_Equip(ii)
                
        # now do some random generation here
        Rn=np.random.uniform(0,1,size=5)  # 5 samples from Uniform dist in 0-1
        if IsBoss:
            Rn=np.ones(5)*self.LV*5
            

        self.Money=20+int(self.Tier*500*Rn[0])
        self.Exp=-int(self.Tier*100*Rn[1]+10)  #this make sure the monsters will NOT level up
        self.PT_mag=int(self.Tier*2*Rn[2]+1)
        self.PT_stat=int(self.Tier*2*Rn[3]+1)
        self.PT_equip=int(self.Tier*2*Rn[4]+1)

    def PlayerRoll(self,Dict_Equip,Dict_Item,Dict_Mag):
        Nitem=len(Dict_Item)
        Nmag=len(Dict_Mag)
        Nequip=len(Dict_Equip)

        # randomize stats
        self.PT_stat=np.random.randint(10,20)
        for ii in range(7):
            self.Data_Base[ii+3,0]=np.random.randint(10,30)
        self.Data_Base[6,0]=np.random.randint(-10,10)

        #debughahaha
        #self.Data_Base[3,0]=200000
        #self.Data_Base[5,0]=200000
        #self.PT_mag=100000
        #self.PT_equip=100000

        # randomize item and equip
        N=np.random.randint(2,5)  #can have 2-5 items
        ii=0
        while ii<N:
            tempID=np.random.randint(1,Nitem-1)
            if Dict_Item[tempID].Tier<=2:  #cannot have tier more than 2 at start up
                self.Item_Obtain(Dict_Item[tempID])
                ii+=1
        
        N=3   #Always start with 3 magic
        ii=0
        while ii<N:
            tempID=np.random.randint(1,Nmag-1)
            if Dict_Mag[tempID].Tier<=2:
                self.Magic_Learn(Dict_Mag[tempID])                
                ii+=1
        
        N=np.random.randint(1,5)  #gen a random number 1<=N<=5
        ii=0
        while ii<N:
            tempID=np.random.randint(1,Nequip-1)
            if Dict_Equip[tempID].Tier<=2:
                self.Equipment_Obtain(Dict_Equip[tempID])                
                ii+=1
        
        self.Update()

    def Levelup(self):
        CurrentLV=self.LV
        RequiredExp=int(500*CurrentLV**1.5)
        
        if self.Exp>=RequiredExp:
            self.Exp-=RequiredExp
            self.Data_Base[0,0]+=1  #LV +1
            self.PT_stat+=10*CurrentLV
            self.PT_mag+=10*CurrentLV
            self.PT_equip+=10*CurrentLV
            #self.LV+=1
            if (CurrentLV+1)%5==0:
                self.N_Item+=1
                self.N_Magic+=1
                self.N_Equip+=1

                self.Item=np.append(self.Item,Item())
                self.Magic=np.append(self.Magic,Magic())
                self.Equipment=np.append(self.Equipment,Equipment())
            
            messagebox.showinfo('Level UP',self.Name+' Leveled up to LV'+str(CurrentLV+1)+'!')
        self.ExpNext=RequiredExp #updated this

    def AP_Down(self):
        self.ActPT-=1

    def Best_Attack(self):  # find the strongest attack possible
        eft=self.Attack()
        att1=np.sum(eft.V_Attack)

        att2=0
        IndxM=-1
        for ii in range(len(self.Magic)):
            if self.Magic[ii].ID!=0:
                cost=self.Magic[ii].Get_MPcost()
                HPi=-self.Magic[ii].Impact_HP()
                if self.MP>cost and HPi>att2:
                    att2=HPi
                    IndxM=ii
        
        att3=0
        IndxI=-1
        for ii in range(len(self.Item)):
            if self.Item[ii].ID!=0:
                
                HPi=-self.Item[ii].Impact_HP()
                if HPi>att3:
                    att3=HPi
                    IndxI=ii

        
        
        if att2>att1 and att2>att3:
            return ['Magic',IndxM]

        if att3>att2 and att3>att1:
            return ['Item',IndxI]

        
        return ['Attack',0]

    def Best_Heal(self):  # find the strongest attack possible
        
        att2=0
        IndxM=-1
        for ii in range(len(self.Magic)):
            if self.Magic[ii].ID!=0:
                cost=self.Magic[ii].Get_MPcost()
                HPi=self.Magic[ii].Impact_HP()
                if self.MP>cost and HPi>att2:
                    att2=HPi
                    IndxM=ii
        
        att3=0
        IndxI=-1
        for ii in range(len(self.Item)):
            if self.Item[ii].ID!=0:
                
                HPi=self.Item[ii].Impact_HP()
                if HPi>att3:
                    att3=HPi
                    IndxI=ii

        if max(att2,att3)<=0:  # no ability to heal
            return ['None',-1]
        else:

            if att2>=att3:
                return ['Magic',IndxM]
            else:
                return ['Item',IndxI]

    def Get_Description(self):
        dd=''
        dd=dd+self.Name+' (LV'+str(int(self.LV))+') '
        if self.C>=0:
            dd=dd+'Good('+str(int(self.C))+')\n'
        else:
            dd=dd+'Evil('+str(int(self.C))+')\n'
        dd=dd+'PTs:S='+str(int(self.PT_stat))+' M='+str(int(self.PT_mag))+' E='+str(int(self.PT_equip))+' Exp='+str(int(-self.Exp))+'\n'
        
        dd=dd+self.Desc+'\n'

        return dd

class PlayerData:  #this is for save and load to use pickel
    def __init__(self):
        #Basic Info
        self.Name=''
        self.NickName=''
        self.Desc=''
        self.ID=0  #this is empty default, need to change for monster, player can be -1
        self.Pic='mon0.png'
        #self.Img=0  #this used to load file using Image
        #self.PImg=0  #this used to output to canvas
        self.onDef=False
        self.ActPT=0
        self.Align='None'
        
        #Single variables
        self.N_total=0
        self.N_kill=0
        self.N_run=0
        self.N_convert=0
        self.HighestKill=0

        # Stock spaces  (these need to be upgraded in the game) by default you got one for each, good for Vstack
        self.N_ActionPT=1
        self.N_Magic=6
        self.N_Item=10
        self.N_Equip=10
        self.Value=0
        self.Zone=0
        self.Tier=0

        self.Exp=0
        self.ExpNext=500
        self.Angry=False  # hostile to player or not
        self.DeathImmune=False
        
        # Expendible resources points
        self.Money=0
        self.PT_stat=0
        self.PT_equip=0
        self.PT_mag=0

       
        # Item equipment and magic
        self.ItemData=np.zeros((self.N_Item,2))  # Items and LV
        

        self.MagicData=np.zeros((self.N_Magic,2)) # Magics and LV
        self.EquipmentData=np.zeros((self.N_Equip,2))

        # Equiped slots (these are always the same, 15 of them)
        self.EquipedData=np.zeros((15,2)) # Equipments on body (15 total), if it is number 0 nothing equiped.
        # 0-Head,1-body,2-belt,3-pants,4-shoes,5-weapon,6-glove,7-arlmet,8-left ring,9-right ring,10-ear ring,11-toe ring,12-nose ring,13-pokemon1, 14-pokemon2

        #self.REM=Remains() #empty remains         
        
        self.Data_Base=np.zeros((20,6))
            
        self.Data_Derive=np.zeros((24,6))
        
        # Base Stats
        self.LV=0
        self.HP=0
        self.MP=0

        self.S=0  
        self.P=0
        self.E=0
        self.C=0
        self.I=0
        self.A=0
        self.L=0

        self.DropRate=0
        self.StealRate=0
        self.F_exp=0
        self.F_money=0
        self.F_PTstat=0
        self.F_PTequip=0
        self.F_PTmag=0
        self.HPreg=0
        self.MPreg=0
        self.Moneyreg=0

        # Derived stats
        self.HPmax=0
        self.MPmax=0
        
        self.A_Phys=0
        self.A_Cold=0
        self.A_Fire=0
        self.A_Ligh=0
        self.A_Pois=0
        self.A_Holy=0
        self.A_Dark=0
        self.D_Phys=0
        self.D_Cold=0
        self.D_Fire=0
        self.D_Ligh=0
        self.D_Pois=0
        self.D_Holy=0
        self.D_Dark=0
        self.P_Phys=0
        self.P_Cold=0
        self.P_Fire=0
        self.P_Ligh=0
        self.P_Pois=0
        self.P_Holy=0
        self.P_Dark=0
    
    def To_String(self):
        return ''

class SaveData:
    def __init__(self):
        self.PlayerData=[PlayerData()]*3
        self.MonsterData=[PlayerData()]*3        

        self.Zones=ZoneInfo()
        #self.Dict_Monster={}
        #self.Dict_I={}
        #self.Dict_E={}
        #self.Dict_Magic={}

        self.Box_Item=np.zeros((40,2))
        self.Box_Equip=np.zeros((40,2))
        self.Drop_Item=np.zeros((40,2))
        self.Drop_Equip=np.zeros((40,2))

        self.Current_Zone=0  #G_Zone=0 #safe zone
        self.InBattle=False  #InBattle=False
        self.Turn='Player'  #MyTurn='Player' #or 'Monster'
        
        # G box variables
        self.G_Money=1   
        self.G_PTequip=2   
        self.G_PTmag=3   
        self.G_Box_ItemN=40   
        self.G_Box_Item_In=0   
        self.G_Box_EquipN=40   
        self.G_Box_Equip_In=0   
        self.Drop_ItemN=40   
        self.Drop_Item_In=0   
        self.Drop_EquipN=40   
        self.Drop_Equip_In=0   

        self.Btn_Roll='disabled'
        self.Btn_Start='disabled'
        self.Btn_Retreat='disabled'
        self.Btn_Boss='disabled'
        self.Btn_Go='disabled'
        self.Btn_PlayerAll='disabled'

        self.SpecialEvents=[0,0,0,0,0,0,0]

#region Define all gneral functions------------
def LoadFile_Magic(Filename):
    file1=open(Filename,'r')
    N=int(file1.readline())
    Dict_Magic={}
    for ii in range(N):
        temp_mag=Magic()
        temp_strData=file1.readline()
        temp_strDesc=file1.readline()
        temp_mag.Set_string(temp_strData,temp_strDesc)
        Dict_Magic[temp_mag.ID]=temp_mag
    file1.close
    return Dict_Magic

def LoadFile_Item(Filename):
    file1=open(Filename,'r')
    N=int(file1.readline())
    Dict_Item={}
    for ii in range(N):
        temp_Item=Item()
        temp_strData=file1.readline()
        temp_strDesc=file1.readline()
        temp_Item.Set_string(temp_strData,temp_strDesc)
        Dict_Item[temp_Item.ID]=temp_Item
    file1.close
    return Dict_Item

def LoadFile_Equipment(Filename):
    file1=open(Filename,'r')
    N=int(file1.readline())
    Dict_Equipment={}
    for ii in range(N):
        temp_eq=Equipment()
        temp_strData=file1.readline()
        temp_strDesc=file1.readline()
        temp_eq.Set_string(temp_strData,temp_strDesc)
        Dict_Equipment[temp_eq.ID]=temp_eq
    file1.close
    return Dict_Equipment

def LoadFile_Monster(Filename):
    file1=open(Filename,'r')
    N=int(file1.readline())
    Dict_Monster={}
    for ii in range(N):
        temp_mon=Player()
        temp_strData=file1.readline()
        temp_strDesc=file1.readline()
        temp_mon.Set_string(temp_strData,temp_strDesc)
        Dict_Monster[temp_mon.ID]=temp_mon
        #print('Dict initial item '+str(ii)+': '+str(Dict_Monster[temp_mon.ID].Item_Count()))
    file1.close
    return Dict_Monster

def LoadFile_Zones(Filename):
    file1=open(Filename,'r')
    N=int(file1.readline())
    Zinfo=ZoneInfo()

    Zinfo.N=N
    Zinfo.ID=range(N)
    Zinfo.Name=[str('')]*N
    Zinfo.KillN=np.zeros(N)
    Zinfo.Killed=np.zeros(N)
    Zinfo.BossFactor=np.zeros(N)
    Zinfo.Completed=[False]*N
    Zinfo.BossIDgood=np.zeros(N)
    Zinfo.BossIDbad=np.zeros(N)

    Zinfo.Completed[0]=True


    for ii in range(N):
        
        temp_strData=file1.readline()
        temp_str=temp_strData.split(',')

        Zinfo.Name[ii]=temp_str[1]
        Zinfo.KillN[ii]=int(temp_str[2])
        Zinfo.BossFactor[ii]=float(temp_str[3])
        Zinfo.BossIDgood[ii]=int(temp_str[4])
        Zinfo.BossIDbad[ii]=int(temp_str[5])
        
        
    file1.close()
    return Zinfo

def LoadFile_Talk(Filename):
    file1=open(Filename,'r')
    N=int(file1.readline())
    Dict_Talk={}
    Dict_Talk[0]=''
    for ii in range(N):
        temp_str=file1.readline()
        
        Dict_Talk[ii+1]=temp_str
    file1.close
    return Dict_Talk

def Show_Story(input_story,Mytag='T_black'):
    S_Story.config(state='normal')
    N=S_Story.count('1.0','end','displaylines')
    #print(N)
    if N[0]>=100:
        temp_str=S_Story.get('1.0','end')
        lines=temp_str.split('\n')
        S_Story.delete('1.0','end')
        S_Story.insert(tk.END,lines[-3]+'\n'+lines[-2]+'\n'+lines[-1]+'\n')
        #S_Story.see('end')

    
    S_Story.insert(tk.END,input_story,Mytag)
    S_Story.see('end')
    S_Story.config(state='disabled')

def Box_updateGUI():
    global G_Box_Item_In,G_Box_Equip_In
    NbPB_Item.delete(0,'end')
    N=0
    for ii in range(len(G_Box_Item)):
        # get the ID from my Item
        if G_Box_Item[ii].ID==0:
            temp_str=''
        else:
            temp_str=G_Box_Item[ii].Name
            N+=1 
        # put Item name in the list
        NbPB_Item.insert('end',temp_str)
    NbPB_Item0.config(text='Item:'+str(N)+'/'+str(G_Box_ItemN))
    G_Box_Item_In=N

    NbPB_Equip.delete(0,'end')
    N=0
    for ii in range(len(G_Box_Equip)):
        # get the ID from my Item
        if G_Box_Equip[ii].ID==0:
            temp_str=''
        else:
            temp_str=G_Box_Equip[ii].Name#+' (LV'+str(G_Box_Equip[ii].LV)+')'
            N+=1 
        # put Item name in the list
        NbPB_Equip.insert('end',temp_str)
    NbPB_Equip0.config(text='Equipment:'+str(N)+'/'+str(G_Box_EquipN))
    G_Box_Equip_In=N

    NbPB_Lab_Money.config(text='$ '+str(int(G_Money)))
    NbPB_Lab_PTmag.config(text=str(int(G_PTmag))+' PT')
    NbPB_Lab_PTequip.config(text=str(int(G_PTequip))+' PT')

def Box_Item_EmptySlot():
    global G_Box_ItemN
    indx=-1
    foundit=False
    ii=0
    while not foundit and ii<G_Box_ItemN-1:
        if G_Box_Item[ii].ID==0:
            indx=ii
            foundit=True
        ii+=1
    
    return indx

def Box_Equip_EmptySlot():
    global G_Box_EquipN
    indx=-1
    foundit=False
    ii=0
    while not foundit and ii<G_Box_EquipN-1:
        if G_Box_Equip[ii].ID==0:
            indx=ii
            foundit=True
        ii+=1
    
    return indx

def Remain_Kill_Drop(P:Player,M:Player): # drop due to player action, return total number of items dropped
    global Drop_Item,Drop_Equip
    Rm=M.REM
    P.Money+=int(Rm.Money*P.F_money/100)
    P.Exp+=int(Rm.Exp*P.F_exp/100)
    P.PT_equip+=int(Rm.PT_equip*P.F_PTequip/100)
    P.PT_mag+=int(Rm.PT_mag*P.F_PTmag/100)
    P.PT_stat+=int(Rm.PT_stat*P.F_PTstat/100)

    Closs=int(-M.C/10)
    P.Data_Base[6,0]+=Closs  # loss 1/10 of Monster Chrisma

    Prob=min(0.95,P.DropRate*M.DropRate/100/100) # Player drop rate default is 100, M rate is real prob
    #Prob=1
    LootN=0

    for ii in range(len(Rm.Item)):
        if Rm.Item[ii].ID!=0:
            #print(str(ii)+'--'+Rm.Item[ii].Name)
            Ux=np.random.random()
            #print(str(Prob)+' vs '+str(Ux))
            if Prob>Ux:
                LootN+=1
                insertIndx=-1
                foundit=False
                for jj in range(len(Drop_Item)):
                    if Drop_Item[jj].ID==0 and not foundit:
                        insertIndx=jj
                        foundit=True
                if insertIndx<0:
                    Drop_Item.pop(0)
                    Drop_Item=np.append(Drop_Item,Rm.Item([ii]))
                else:
                    Drop_Item[insertIndx]=copy.copy(Rm.Item[ii])
    #print('done with item, now equip:')
    for ii in range(len(Rm.Equip)):
        if Rm.Equip[ii].ID!=0:
            #print(str(ii)+'--'+Rm.Equip[ii].Name)
            Ux=np.random.random()
            #print(str(Prob)+' vs '+str(Ux))
            if Prob>Ux:
                LootN+=1
                insertIndx=-1
                foundit=False
                for jj in range(len(Drop_Equip)):
                    if Drop_Equip[jj].ID==0 and not foundit:
                        insertIndx=jj
                        foundit=True
                if insertIndx<0:
                    Drop_Equip.pop(0)
                    Drop_Equip=np.append(Drop_Equip,Rm.Equip([ii]))
                else:
                    Drop_Equip[insertIndx]=copy.copy(Rm.Equip[ii])
    return LootN

def Remain_self_Drop(M:Player): # drop due to poison
    global Drop_Item,Drop_Equip
    Rm=M.REM
    #P.Money+=int(Rm.Money*P.F_money/100)
    #P.Exp+=int(Rm.Exp*P.F_exp/100)
    #P.PT_equip+=int(Rm.PT_equip*P.F_PTequip/100)
    #P.PT_mag+=int(Rm.PT_mag*P.F_PTmag/100)
    #P.PT_stat+=int(Rm.PT_stat*P.F_PTstat/100)

    Prob=min(0.95,M.DropRate/100) # Player drop rate Ignored, M rate is real prob

    for ii in range(len(Rm.Item)):
        if Rm.Item[ii].ID!=0:
            Ux=np.random.random()
            if Prob>Ux:
                insertIndx=-1
                foundit=False
                for jj in range(len(Drop_Item)):
                    if Drop_Item[jj].ID==0 and not foundit:
                        insertIndx=jj
                        foundit=True
                if insertIndx<0:
                    Drop_Item.pop(0)
                    Drop_Item=np.append(Drop_Item,Rm.Item([ii]))
                else:
                    Drop_Item[insertIndx]=copy.copy(Rm.Item[ii])
    
    for ii in range(len(Rm.Equip)):
        if Rm.Equip[ii].ID!=0:
            Ux=np.random.random()
            if Prob>Ux:
                insertIndx=-1
                foundit=False
                for jj in range(len(Drop_Equip)):
                    if Drop_Equip[jj].ID==0 and not foundit:
                        insertIndx=jj
                        foundit=True
                if insertIndx<0:
                    Drop_Equip.pop(0)
                    Drop_Equip=np.append(Drop_Equip,Rm.Equip([ii]))
                else:
                    Drop_Equip[insertIndx]=copy.copy(Rm.Equip[ii])

def Drop_updateGUI():
    global Drop_Item_In,Drop_Equip_In
    
    NbMD_Item.delete(0,'end')
    N=0
    
    for ii in range(len(Drop_Item)):

        # get the ID from my Item
        if Drop_Item[ii].ID==0:
            temp_str=''
        else:
            temp_str=Drop_Item[ii].Name
            N+=1 
        # put Item name in the list
        NbMD_Item.insert('end',temp_str)
    NbMD_Item0.config(text='Item:'+str(N)+'/'+str(Drop_ItemN))
    Drop_Item_In=N

    NbMD_Equip.delete(0,'end')
    N=0
    for ii in range(len(Drop_Equip)):
        # get the ID from my Item
        if Drop_Equip[ii].ID==0:
            temp_str=''
        else:
            temp_str=Drop_Equip[ii].Name#+' (LV'+str(Drop_Equip[ii].LV)+')'
            N+=1 
        # put Item name in the list
        NbMD_Equip.insert('end',temp_str)
    NbMD_Equip0.config(text='Equipment:'+str(N)+'/'+str(Drop_EquipN))
    Drop_Equip_In=N

    #NbPB_Money.config(text='Public$:'+str(G_Money))

def Load_Monsters():
    global G_Zone,InBattle,Zone_info

    N_TotalM=len(Dict_Monster)
    # Pick group ID pool based on Zone
    MID_pool=[]
    
    #print('load monster function:'+str(G_Zone))
    for ii in range(N_TotalM):
        if Dict_Monster[ii].Zone>=G_Zone-1 and Dict_Monster[ii].Zone<=G_Zone and Dict_Monster[ii].ID!=0 and Dict_Monster[ii].ID!=Zone_info.BossIDbad[G_Zone] and Dict_Monster[ii].ID!=Zone_info.BossIDgood[G_Zone]:
            MID_pool=np.append(MID_pool,ii)
    
    #print(MID_pool)
    # how many?
    N_monster=np.random.randint(1,4)
    names='\n'
    for ii in range(N_monster):        
        
        Indx=np.random.randint(1,len(MID_pool)-1)
        #print(Indx)
        G_Monster[ii]=Dict_Monster[MID_pool[Indx]].Clone()
        
        G_Monster[ii].Randomize(Dict_Equipment,Dict_Item,Dict_Magic)
        # add level modifier (go to Level)
        LV_low=int(max(1,G_Player[0].LV*0.5*Zone_info.BossFactor[G_Zone]))
        LV_high=int(max(2,G_Player[0].LV*1*Zone_info.BossFactor[G_Zone],LV_low+1))
        LV_m=np.random.randint(LV_low,LV_high)
        G_Monster[ii].GotoLV(LV_m)  # get the LV of monsters to similar to Player
        
        G_Monster[ii].LoadImg(CWD)
        names+=G_Monster[ii].Name+', '
        
    # judge if they are Angry initially, it is based on total C comparison. You can persude individual Monsters to calm later by Talking
    if MonstersAngry():
        InBattle=True
        for ii in range(3):
            if G_Monster[ii].ID!=0:
                G_Monster[ii].Angry=True
        if N_monster>1:
            Show_Story(names+' appeared in front of you.\nThey are PISSED!')
        else:
            Show_Story(names+' appeared in front of you.\nIt is PISSED!')
    else:
        InBattle=False
        for ii in range(3):
            if G_Monster[ii].ID!=0:
                G_Monster[ii].Angry=False
        if N_monster>1:
            Show_Story(names+' appeared in front of you.\nThey are Very Calm.')
        else:
            Show_Story(names+' appeared in front of you.\nIt is Very Calm.')

    # prepare them to fully rested
    Monsters_RestFull()
    Update_Monsters()  #display

def Load_Boss():  # Load Boss in G_Zone
    global G_Zone,InBattle,Zone_info

    N_TotalM=len(Dict_Monster)
    # Pick group ID pool based on Zone
    MID_pool=[]
    
    #print('load monster function:'+str(G_Zone))
    for ii in range(N_TotalM):
        if Dict_Monster[ii].Zone==G_Zone and Dict_Monster[ii].ID!=0 and Dict_Monster[ii].ID!=Zone_info.BossIDbad[G_Zone] and Dict_Monster[ii].ID!=Zone_info.BossIDgood[G_Zone]:
            MID_pool=np.append(MID_pool,ii)
    
    for ii in range(3):
        G_Monster[ii]=Player()   # create empty slot to avoid pass by ref

    Indx=np.random.randint(1,len(MID_pool)-1)
    G_Monster[0]=Dict_Monster[MID_pool[Indx]].Clone()
    G_Monster[0].Randomize(Dict_Equipment,Dict_Item,Dict_Magic)

    if G_Player[0].C>=0:
        BossID=Zone_info.BossIDbad[G_Zone]
    else:
        BossID=Zone_info.BossIDgood[G_Zone]
    
    G_Monster[1]=Dict_Monster[BossID].Clone()
    G_Monster[1].Randomize(Dict_Equipment,Dict_Item,Dict_Magic,True)

    Indx=np.random.randint(1,len(MID_pool)-1)
    G_Monster[2]=Dict_Monster[MID_pool[Indx]].Clone()
    G_Monster[2].Randomize(Dict_Equipment,Dict_Item,Dict_Magic)



    #Zone_info.BossFactor[G_Zone]=0.5
    # add level modifier (go to Level)
    LV_low=int(max(1,G_Player[0].LV*0.9*Zone_info.BossFactor[G_Zone]))
    LV_high=int(max(2,G_Player[0].LV*1.3*Zone_info.BossFactor[G_Zone],LV_low+1))

       
    LV_m=np.random.randint(LV_low,LV_high)
    #print(Zone_info.BossFactor[G_Zone])
    #print([LV_low,LV_high,LV_m])

    for ii in range(3):
        G_Monster[ii].GotoLV(LV_m)  # get the LV of monsters to similar to Player
        G_Monster[ii].Angry=True
        G_Monster[ii].LoadImg(CWD)
        
    Show_Story('\n'+G_Monster[1].Name+' (Boss) is guarding the door to next Zone.\nIt leads a group of monsters charging at you.\nFight!','T_red')
    Monsters_RestFull()
    Update_Monsters()  #display

def MonstersAngry():  #judge if the monster group will be angry at the player group

    #debug
    

    Rep_P=0
    for ii in range(3):
        if G_Player[ii].ID!=0:
            Rep_P+=G_Player[ii].C
    Rep_M=0
    for ii in range(3):
        if G_Monster[ii].ID!=0:
            Rep_M+=G_Monster[ii].C
    
    return Rep_M*Rep_P<0

def Players_No_AP(): #check to see if Player has any free AP 
    totalAP=0
    for ii in range(3):
        totalAP+=G_Player[ii].ActPT
    return totalAP==0

def Players_Rest():  # small rest for all players, call after each Monster turn
    for ii in range(3):
        if G_Player[ii].ID!=0:
            G_Player[ii].Rest()

def Players_RemoveBuff():  # small rest for all players, call after each Monster turn
    for ii in range(3):
        if G_Player[ii].ID!=0:
            G_Player[ii].RemoveBuff()

def Players_RestFull():  # small rest for all players, call after each Monster turn
    for ii in range(3):
        if G_Player[ii].ID!=0:
            G_Player[ii].Rest_Full()

        if G_Player[ii].ID==0 and G_Player[ii].Equiped[7].ID==43: #only chance that ID is 0 and 43 equiped is if it died, so Nickname should have the original ID
            G_Player[ii].ID=G_Player[ii].NickName
            G_Player[ii].Rest_Full()

def Monsters_Rest():  # small rest for all players, call after each Monster turn
    for ii in range(3):
        if G_Monster[ii].ID!=0:
            G_Monster[ii].Rest()

def Monsters_RestFull():  # small rest for all players, call after each Monster turn
    for ii in range(3):
        if G_Monster[ii].ID!=0:
            G_Monster[ii].Rest_Full()

def Monster_WhosHurt():  # find the index of monster who needs heal
    indx=-1
    HPr=0.3  #only need heal if HP is below 30% of max
    for ii in range(3):
        if G_Monster[ii].ID!=0: #if monster not dead
            if HPr>G_Monster[ii].HP/G_Monster[ii].HPmax:
                HPr=G_Monster[ii].HP/G_Monster[ii].HPmax
                indx=ii
    return indx   # return Monster whose relative HP is lowest

def Rand_PlayerIndx():  # return a random player index that is alive
        
    temp=[0,1,2]
    for ii in range(3):
        if G_Player[ii].ID==0:
            temp[ii]=0
    
    indx=np.random.randint(0,2)
    return int(temp[indx])

def Update_Players(): #update GUI for all players
    global ActiveP_index

    activeID=-1

    for ii in range(3):
        if G_Player[ii].ID!=0:
            G_Player[ii].Update()
            #G_Player[ii].LoadImg(CWD)
            G_Player[ii].UpdateGUI_Basic(GUIs_player[ii])
            if activeID<0:
                activeID=ii
        else:
            P_canv[ii].delete('all')
            P_NameLV[ii].config(text='')
            P_HP[ii].config(text='0/0')
            P_MP[ii].config(text='0/0')
        P_canv[ii].config(highlightthickness=1,highlightbackground='red')
    
    if activeID>=0:
        ActiveP_index=activeID
        P_canv[activeID].config(highlightthickness=3,highlightbackground='yellow')
        G_Player[activeID].UpdateGUI(GUIs_player[activeID])

def Update_Monsters(): #update GUI for all monsters
    global ActiveM_index

    activeID=-1

    for ii in range(3):
        if G_Monster[ii].ID!=0:
            G_Monster[ii].Update()
            #G_Monster[ii].LoadImg(CWD)
            G_Monster[ii].UpdateGUI_Basic(GUIs_monster[ii])
            if activeID<0:
                activeID=ii
        else:
            M_canv[ii].delete('all')
            M_NameLV[ii].config(text='')
            M_HP[ii].config(text='0/0')
            M_MP[ii].config(text='0/0')
        M_canv[ii].config(highlightthickness=1,highlightbackground='red')
    
    if activeID>=0:
        ActiveM_index=activeID
        M_canv[activeID].config(highlightthickness=3,highlightbackground='yellow')
        G_Monster[activeID].UpdateGUI(GUIs_monster[activeID])

def Monsters_Dead():  #check if all M are dead
    N=0
    for x in G_Monster:
        if x.ID!=0:
            N+=1
    return N==0

def ItsOver(): # main character dies
    global G_Zone, MyTurn, Zone_info

    #clear monsters
    for ii in range(3):
        G_Monster[ii]=Player()
        G_Monster[ii].LoadImg(CWD)
    Update_Monsters()

    # Get rid of everything player has
    G_Player[0].Money=0
    G_Player[0].PT_stat=0
    G_Player[0].PT_mag=0
    G_Player[0].PT_equip=0

    for ii in range(G_Player[0].N_Item):
        G_Player[0].Item_RemoveList(ii)
    
    for ii in range(G_Player[0].N_Equip):
        G_Player[0].Equipment_RemoveList(ii)

    for ii in range(15):
        if G_Player[0].Equiped[ii].ID!=0:
            G_Player[0].Equipment_Takeoff(ii)
            for jj in range(G_Player[0].N_Equip):
                G_Player[0].Equipment_RemoveList(jj)
    
    #clear all zones
    Zone_info.Killed=np.zeros(Zone_info.N)
    # go back to Safe zone

    S_DropList.config(state='normal')  #enable buttons so the player can go or retreat
    S_Btn_Boss.config(state='disabled',text='No Boss')    
    S_Btn_Retreat.config(state='disabled')
    S_Btn_Go.config(state='disabled')
    G_Zone=0
    S_DropList.config(value=Zone_info.DisplayName())
    S_DropList.current(G_Zone)

    # Remove temp buff
    Players_RemoveBuff()  #this will happen between monster waves

    # let player rest
    Players_RestFull()   
    
    # Give control back to player
    MyTurn='Player'

    Show_Story('\nYou were defeated completely. Lost everything (except what is in stash).','T_red')
    Show_Story('\nFortunately you made it out alive. Back to the Camp Ground...Try again?','T_blue')

def Player_Disable(indx):
    global G_Player
    if indx<0 or indx>2:
        messagebox.showinfo('error','trying to disable player out of bound')
        return

    if indx==0:
        ItsOver()
    else:
        if G_Player[indx].Equiped[7].ID==43: # player has neclace of life equiped
            G_Player[indx].NickName=G_Player[indx].ID
            G_Player[indx].ID=0
        else:
            G_Player[indx]=Player()

def DisablePlayerButtons():
    NbPA_Btn_Attack.config(state='disabled')
    NbPA_Btn_Talk.config(state='disabled')
    NbPA_Btn_Recruit.config(state='disabled')
    NbPA_Btn_Run.config(state='disabled')
    NbPA_Btn_Defend.config(state='disabled')
    NbPA_Btn_item_Use.config(state='disabled')
    NbPA_Btn_mag_Use.config(state='disabled')

def EnablePlayerButtons():
    NbPA_Btn_Attack.config(state='normal')
    NbPA_Btn_Talk.config(state='normal')
    NbPA_Btn_Recruit.config(state='normal')
    NbPA_Btn_Run.config(state='normal')
    NbPA_Btn_Defend.config(state='normal')
    NbPA_Btn_item_Use.config(state='normal')
    NbPA_Btn_mag_Use.config(state='normal')

def MonsterTurnAction():
    global T_delay
    # only came here if there is still monster alive, dont know if they are angry or not individually, they come on loading having same Angry level, but can be changed along the way
    # refill Monster AP
    Monsters_Rest()
    DisablePlayerButtons()
    Update_Monsters()

    for ii in range(3):
        root.update()
        time.sleep(T_delay)

        if G_Monster[ii].ID!=0: #if monster not dead
            if G_Monster[ii].Angry:
                # attack
                #while it has AP
                while G_Monster[ii].ActPT>0:
                    G_Monster[ii].AP_Down()

                    # see if there is a need for heal
                    Mindx=Monster_WhosHurt()

                    root.update()
                    time.sleep(T_delay)

                    if Mindx>=0: #need heal
                        # can I heal?
                        X=np.random.random()
                        tempHel=G_Monster[ii].Best_Heal()
                        if tempHel[0]=='Magic' and X>0.5: # 50% chance to heal if Magic is the way
                            eft=G_Monster[ii].Magic_Use(tempHel[1])
                            if eft!=0:  # monster could use a magic they cannot use...can fix later...
                                HP_old=G_Monster[Mindx].HP
                                G_Monster[Mindx].ApplyEffect(eft)
                                G_Monster[Mindx].UpdateGUI_Basic(GUIs_monster[Mindx])
                                G_Monster[ii].UpdateGUI_Basic(GUIs_monster[ii])
                                HP_new=G_Monster[Mindx].HP
                                HP_Change=HP_new-HP_old

                                Show_Story('\n'+G_Monster[ii].Name+' casts'+G_Monster[ii].Magic[tempHel[1]].Name+' to heal '+G_Monster[Mindx].Name+' for '+str(int(HP_Change))+' HP!\n','T_blue')
                            else:
                                Show_Story('\n'+G_Monster[ii].Name+' tried to heal '+G_Monster[Mindx].Name+' but failed!\n','T_blue')
                        elif tempHel[0]=='Item' and X>0.7: # 30% chance to heal if Item is the way
                            temp_Item_Name=G_Monster[ii].Item[tempHel[1]].Name
                            eft=G_Monster[ii].Item_Use(tempHel[1])
                            
                            HP_old=G_Monster[Mindx].HP
                            G_Monster[Mindx].ApplyEffect(eft)
                            G_Monster[Mindx].UpdateGUI_Basic(GUIs_monster[Mindx])
                            G_Monster[ii].UpdateGUI(GUIs_monster[ii])
                            HP_new=G_Monster[Mindx].HP
                            HP_Change=HP_new-HP_old
                            Show_Story('\n'+G_Monster[ii].Name+' uses '+temp_Item_Name+' to heal '+G_Monster[Mindx].Name+' for '+str(int(HP_Change))+' HP!\n','T_blue')
                        else:
                            Pindx=Rand_PlayerIndx()
                            tempAtt=G_Monster[ii].Best_Attack()
                            X=np.random.random()  # 0-1 number to make sure they will not always use Item or Mag
                            if tempAtt[0]=='Attack':
                                if G_Monster[ii].Success_Attack(G_Player[Pindx]):
                                    eft=G_Monster[ii].Attack()

                                    HP_old=G_Player[Pindx].HP
                                    G_Player[Pindx].ApplyEffect(eft)
                                    HP_new=G_Player[Pindx].HP
                                    HP_Change=HP_old-HP_new

                                    Show_Story('\n'+G_Monster[ii].Name+' attacked '+ G_Player[Pindx].Name+' for '+str(int(HP_Change))+' HP!\n','T_red')
                                    if G_Player[Pindx].Update():
                                        G_Player[Pindx].UpdateGUI_Basic(GUIs_player[Pindx])
                                    else:
                                        Player_Disable(Pindx)                                
                                        #if Pindx==0: #main player died
                                        #    ItsOver()  #will not kill player, just 0 out all he has
                                        #else:
                                        #    G_Player[Pindx]=Player()
                                else:
                                    #attach failed
                                    Show_Story('\n'+G_Monster[ii].Name+' tried to attack '+ G_Player[Pindx].Name+' but failed!\n','T_red')
                                    
                            elif tempAtt[0]=='Magic' and X<0.6:
                                eft=G_Monster[ii].Magic_Use(tempAtt[1])

                                HP_old=G_Player[Pindx].HP
                                G_Player[Pindx].ApplyEffect(eft)
                                HP_new=G_Player[Pindx].HP
                                HP_Change=HP_old-HP_new

                                Show_Story('\n'+G_Monster[ii].Name+' attacked '+ G_Player[Pindx].Name+' with '+G_Monster[ii].Magic[tempAtt[1]].Name+' for '+str(int(HP_Change))+' HP!\n','T_red')
                                if G_Player[Pindx].Update():
                                    G_Player[Pindx].UpdateGUI_Basic(GUIs_player[Pindx])
                                else:
                                    Player_Disable(Pindx)                                
                                    #if Pindx==0: #main player died
                                    #    ItsOver()  #will not kill player, just 0 out all he has
                                    #else:
                                    #    G_Player[Pindx]=Player()
                                G_Monster[ii].UpdateGUI_Basic(GUIs_monster[ii])
                            elif tempAtt[0]=='Item' and X<0.4:
                                tempItemName=G_Monster[ii].Item[tempAtt[1]].Name
                                eft=G_Monster[ii].Item_Use(tempAtt[1])

                                HP_old=G_Player[Pindx].HP
                                G_Player[Pindx].ApplyEffect(eft)
                                HP_new=G_Player[Pindx].HP
                                HP_Change=HP_old-HP_new

                                Show_Story('\n'+G_Monster[ii].Name+' attacked '+ G_Player[Pindx].Name+' using '+tempItemName+' for '+str(int(HP_Change))+' HP!\n','T_red')
                                if G_Player[Pindx].Update():
                                    G_Player[Pindx].UpdateGUI_Basic(GUIs_player[Pindx])
                                else:
                                    Player_Disable(Pindx)

                                    #if Pindx==0: #main player died
                                    #    ItsOver()  #will not kill player, just 0 out all he has
                                    #else:
                                    #    G_Player[Pindx]=Player()
                                G_Monster[ii].UpdateGUI(GUIs_monster[ii])

                            else:
                                if G_Monster[ii].Success_Attack(G_Player[Pindx]):
                                    eft=G_Monster[ii].Attack()

                                    HP_old=G_Player[Pindx].HP
                                    G_Player[Pindx].ApplyEffect(eft)
                                    HP_new=G_Player[Pindx].HP
                                    HP_Change=HP_old-HP_new

                                    Show_Story('\n'+G_Monster[ii].Name+' attacked '+ G_Player[Pindx].Name+' for '+str(int(HP_Change))+' HP!\n','T_red')
                                    if G_Player[Pindx].Update():
                                        G_Player[Pindx].UpdateGUI_Basic(GUIs_player[Pindx])
                                    else:
                                        Player_Disable(Pindx)                                
                                        #if Pindx==0: #main player died
                                        #    ItsOver()  #will not kill player, just 0 out all he has
                                        #else:
                                        #    G_Player[Pindx]=Player()
                                else:
                                    #attach failed
                                    Show_Story('\n'+G_Monster[ii].Name+' tried to attack '+ G_Player[Pindx].Name+' but failed!\n','T_red')
                                    

                    else: #everyone is fine

                        # find a player and attack
                        Pindx=Rand_PlayerIndx()
                        tempAtt=G_Monster[ii].Best_Attack()
                        print([ii, tempAtt])

                        if tempAtt[0]=='Attack':
                            if G_Monster[ii].Success_Attack(G_Player[Pindx]):

                                eft=G_Monster[ii].Attack()

                                HP_old=G_Player[Pindx].HP
                                G_Player[Pindx].ApplyEffect(eft)
                                HP_new=G_Player[Pindx].HP
                                HP_Change=HP_old-HP_new

                                Show_Story('\n'+G_Monster[ii].Name+' attacked '+ G_Player[Pindx].Name+' for '+str(int(HP_Change))+' HP!\n','T_red')
                                if G_Player[Pindx].Update():
                                    G_Player[Pindx].UpdateGUI_Basic(GUIs_player[Pindx])
                                else:
                                    Player_Disable(Pindx)                                
                                    #if Pindx==0: #main player died
                                    #    ItsOver()  #will not kill player, just 0 out all he has
                                    #else:
                                    #    G_Player[Pindx]=Player()
                            else:
                                #attach failed
                                Show_Story('\n'+G_Monster[ii].Name+' tried to attack '+ G_Player[Pindx].Name+' but failed!\n','T_red')
                                    

                        elif tempAtt[0]=='Magic':
                            eft=G_Monster[ii].Magic_Use(tempAtt[1])

                            HP_old=G_Player[Pindx].HP
                            G_Player[Pindx].ApplyEffect(eft)
                            HP_new=G_Player[Pindx].HP
                            HP_Change=HP_old-HP_new

                            Show_Story('\n'+G_Monster[ii].Name+' attacked '+ G_Player[Pindx].Name+' with '+G_Monster[ii].Magic[tempAtt[1]].Name+' for '+str(int(HP_Change))+' HP!\n','T_red')
                            if G_Player[Pindx].Update():
                                G_Player[Pindx].UpdateGUI_Basic(GUIs_player[Pindx])
                            else:
                                Player_Disable(Pindx)                                
                                #if Pindx==0: #main player died
                                #    ItsOver()  #will not kill player, just 0 out all he has
                                #else:
                                #    G_Player[Pindx]=Player()
                            
                            G_Monster[ii].UpdateGUI_Basic(GUIs_monster[ii])
                        
                        elif tempAtt[0]=='Item':
                            tempItemName=G_Monster[ii].Item[tempAtt[1]].Name
                            eft=G_Monster[ii].Item_Use(tempAtt[1])

                            #print(eft.V_Attack)

                            HP_old=G_Player[Pindx].HP
                            G_Player[Pindx].ApplyEffect(eft)
                            HP_new=G_Player[Pindx].HP
                            HP_Change=HP_old-HP_new

                            Show_Story('\n'+G_Monster[ii].Name+' attacked '+ G_Player[Pindx].Name+' using '+tempItemName+' for '+str(int(HP_Change))+' HP!\n','T_red')
                            if G_Player[Pindx].Update():
                                G_Player[Pindx].UpdateGUI_Basic(GUIs_player[Pindx])
                            else:
                                Player_Disable(Pindx)                                
                                #if Pindx==0: #main player died
                                #    ItsOver()  #will not kill player, just 0 out all he has
                                #else:
                                #    G_Player[Pindx]=Player()
                            
                            G_Monster[ii].UpdateGUI(GUIs_monster[ii])

                        else:
                            messagebox.showinfo('error','something wrong this should not appear')
                Update_Monsters()
                    
               
            else:  #not angry
                #passive act
                #if it has AP
                if G_Monster[ii].ActPT>0: #will use all AP trying to walk away
           
                    X=np.random.random()
                    if X>0.5: #half chance
                        G_Monster[ii]=Player()  #empty monster, he walks away
                        Show_Story('\n'+G_Monster[ii].Name+' decided to just walk away...its gone!\n','T_blue')
                    else:
                        Show_Story('\n'+G_Monster[ii].Name+' Got noting to do here but still stick around!\n','T_blue')
                    G_Monster[ii].ActPT=0

                    root.update()
                    time.sleep(T_delay)
                
                #check if all monster is gone, if so, give buttons back to player
                if Monsters_Dead(): #all monsters are dead or gone
                    # check if boss dead, update new zone to the list
                    Stuff_When_Monster_Gone()

                # if cannot walk away, it will just stay and do nothing
    # update GUI monsters
    Update_Monsters()

    Players_Rest()
    Update_Players()
    EnablePlayerButtons()
    #update GUI players

def Stuff_When_Monster_Gone():
    global G_Zone,Zone_info,InBattle, MyTurn

    #cbtext=[]
    #lastZone=0
    #for ii in range(Zone_info.N):
    #    if Zone_info.Completed[ii]:
    #        lastZone=ii
    #        cbtext=np.append(cbtext,Zone_info.Name[ii])
    #    
    #if lastZone<Zone_info.N-1:
    #    cbtext=np.append(cbtext,Zone_info.Name[lastZone+1])
    #    cbtext=np.append(cbtext,'Next Zone ???')
    #else: #already completed the game
    #    messagebox.showinfo('Congratulations!','You have completed all Zones! Now just play for fun...if you choose to.')
    #S_DropList.config(values=cbtext)
    
    
    S_DropList.config(state='normal')  #enable buttons so the player can go or retreat
    if Zone_info.EnoughKill(G_Zone):
        S_Btn_Boss.config(state='normal',text='Boss Ready')
    else:
        S_Btn_Boss.config(state='disabled',text='Boss '+Zone_info.Str_progress(G_Zone))
    S_Btn_Retreat.config(state='normal')
    S_Btn_Go.config(state='normal')

    # Remove temp buff
    Players_RemoveBuff()  #this will happen between monster waves

    # let player rest
    Players_Rest()   #not full rest.
    
    # Give control back to player
    MyTurn='Player'

    #print('monster gone function: '+str(G_Zone))
    Show_Story('\nThis wave of Monsters are gone!\nNow your Zone Progress is '+Zone_info.Str_progress(G_Zone)+'.\nWill you keep going or retreat?\n','T_green')

    # update zones, note this wave might be boss, so... update droplist based on complete values, Notification of boss happens when kill happens
    temp=S_DropList.current()     
    S_DropList.config(value=Zone_info.DisplayName())
    S_DropList.current(temp)
       
def Stuff_After_Player_Action(): #stuff that will happen after player action done, last thing for all Actions that will cost AP (has potential to change turns)
    global G_Zone, InBattle, MyTurn, Zone_info

    if G_Zone==0:   # if in safe zone, your AP/HP/MP will be full all the time
        Players_RestFull()
        Update_Players()
        InBattle=False

    #print('Player action after function: '+str(G_Zone))
    if Monsters_Dead(): #all monsters are dead
            # check if boss dead, update new zone to the list
        Stuff_When_Monster_Gone()
    else:
        if Players_No_AP():
            MyTurn='Monster'
            MonsterTurnAction()  # they will do one round, let player rest, and pass control back to player
        # check if boss is found, update list
        #if Monsters_Dead(): #all monsters are dead
        #    # check if boss dead, update new zone to the list
        #    Stuff_When_Monster_Gone()

            #if messagebox.askquestion('What now?','Enemy destroyed!\nContinue fighting? (Yes-Next wave) or (No-Back to Safezone)?')=='yes':
            #    Load_Monsters()   #keep fighting
            #    Players_Rest()    #rest because you killed monster, and you got your turn
            #    MyTurn='Player'
            #else:
            #    # go back to safezone, you can only come out by hitting go
            #    InBattle=False
            #    G_Zone=0
            #    MyTurn='Player'
            #    S_DropList.current(0)
            #    Players_RestFull()
            #    # need to eliminate current level progress as you ran
        #else:
            
def Monsters_Angry():
    temp=False
    for ii in range(3):
        if G_Monster[ii].ID!=0:
            temp=temp or G_Monster[ii].Angry
    
    return temp

#endregion Finish of all gneral functions-------------

# Main program starts===================

#region Global Variables
CWD=os.getcwd()+'\\'

T_delay=0.5  #0.5 sec delay 
G_Player=[Player()]*3 #3 players, 
G_Monster=[Player()]*3 #3 Monsters,
G_Roll_N=7 # initial roll counter

SD=SaveData() #need to keep this guy around...

G_Zone=0 #safe zone
InBattle=False
MyTurn='Player' #or 'Monster'

ActiveP_index=0
ActiveM_index=0

ActivePI_index=-1
ActivePM_index=-1
ActivePE_index=-1
ActivePEq_index=-1

ActiveMI_index=-1
ActiveMM_index=-1
ActiveME_index=-1
ActiveMEq_index=-1
# G box variables
G_Money=1
G_PTequip=2
G_PTmag=3

G_Box_ItemN=40
G_Box_Item_In=0
G_Box_Item=[Item()]*G_Box_ItemN
ActiveBI_index=-1

G_Box_EquipN=40
G_Box_Equip_In=0
G_Box_Equip=[Equipment()]*G_Box_EquipN
ActiveBE_index=-1
# Global variables for Drop
Drop_ItemN=40
Drop_Item_In=0
Drop_Item=[Item()]*Drop_ItemN
ActiveDI_index=-1

Drop_EquipN=40
Drop_Equip_In=0
Drop_Equip=[Equipment()]*Drop_EquipN
ActiveDE_index=-1

# global Pimg pool 
PublicImg=[]
PublicPImg=[]
PImg_ME=[]
PImg_PE=[]

G_Events=[0,0,0,0,0,0,0]  #this one marks special global events that can only happen once
# 1- collect all earth dragon balls  2- collect all Nemic dragon balls

#endregion

#region Loading zone----------------
# Load Magic file into Dict: Mag
Dict_Magic=LoadFile_Magic(CWD+'MagicDataII.txt')
#print(len(Dict_Magic))
# Load Item file into Dict: Itm
Dict_Item=LoadFile_Item(CWD+'ItemDataII.txt')
#print(len(Dict_Item))
#print(Dict_Item[0])
#print(Dict_Item[1])
# Load Monster file into Dict: Monster
Dict_Monster=LoadFile_Monster(CWD+'MonsterDataII.txt')
#print(len(Dict_Monster))
# Load Equipment file into Dict: Monster
Dict_Equipment=LoadFile_Equipment(CWD+'EquipmentDataII.txt')
#print(len(Dict_Equipment))
# Load Area file 

Dict_Talk=LoadFile_Talk(CWD+'EmptyTalkII.txt')

Zone_info=LoadFile_Zones(CWD+'ZoneDataII.txt')

#endregion finish loading-----------------

#region Binding functions-------------------

#region Mechanism binding
def P1_Canv_Click(event):
    global ActiveP_index
    #Target_Action.set(0)
    #Target_Item.set(0)
    #Target_Magic.set(0)
    if G_Player[0].ID!=0:
        if ActiveP_index!=0:
            ActiveP_index=0
        P_canv[1].config(highlightthickness=1,highlightbackground='red')
        P_canv[2].config(highlightthickness=1,highlightbackground='red')
        P_canv[0].config(highlightthickness=3,highlightbackground='yellow')
        G_Player[0].UpdateGUI(GUIs_player[0])

def P2_Canv_Click(event):
    global ActiveP_index
    #Target_Action.set(1)
    #Target_Item.set(1)
    #Target_Magic.set(1)
    if G_Player[1].ID!=0:
        if ActiveP_index!=1:
            ActiveP_index=1
        P_canv[1].config(highlightthickness=3,highlightbackground='yellow')
        P_canv[2].config(highlightthickness=1,highlightbackground='red')
        P_canv[0].config(highlightthickness=1,highlightbackground='red')
        G_Player[1].UpdateGUI(GUIs_player[1])

def P3_Canv_Click(event):
    global ActiveP_index
    #Target_Action.set(2)
    #Target_Item.set(2)
    #Target_Magic.set(2)
    if G_Player[2].ID!=0:
        if ActiveP_index!=2:
            ActiveP_index=2
        P_canv[1].config(highlightthickness=1,highlightbackground='red')
        P_canv[2].config(highlightthickness=3,highlightbackground='yellow')
        P_canv[0].config(highlightthickness=1,highlightbackground='red')
        G_Player[2].UpdateGUI(GUIs_player[2])

def M1_Canv_Click(event):
    global ActiveM_index,PublicImg,PublicPImg,CWD,ActiveP_index
    
    #Target_Item.set(3)
    #Target_Magic.set(3)
    if G_Monster[0].ID!=0:
        Target_Action.set(3)
        if ActiveM_index!=0:
            ActiveM_index=0
        M_canv[1].config(highlightthickness=1,highlightbackground='red')
        M_canv[2].config(highlightthickness=1,highlightbackground='red')
        M_canv[0].config(highlightthickness=3,highlightbackground='yellow')            
        G_Monster[0].UpdateGUI(GUIs_monster[0])

        temp_str=G_Monster[ActiveM_index].Get_Description()
        if G_Player[ActiveP_index].ID!=0: #add probabilities
            prob=G_Monster[ActiveM_index].ProbCalc(G_Player[ActiveP_index])
            temp_str=temp_str+'Chances: Hit='+str(prob[0])+'% Attack you='+str(prob[3])+'% Recruit='+str(prob[1])+'% Talk='+str(prob[2])+'%'
        # disply info to textbox
        S_Info_text.config(state='normal')
        S_Info_text.delete(1.0,tk.END)
        S_Info_text.insert(1.0,temp_str)
        S_Info_text.config(state='disabled')

        # get canv size
        S_Info_Canvs.update()
        W=S_Info_Canvs.winfo_width()
        H=S_Info_Canvs.winfo_height()
        PublicImg=Image.open(CWD+G_Monster[ActiveM_index].Pic)
        PublicPImg=ImageTk.PhotoImage(PublicImg.resize((W-4,H-4)))

        S_Info_Canvs.create_image(2,2,anchor=tk.NW,image=PublicPImg)

def M2_Canv_Click(event):
    global ActiveM_index,PublicImg,PublicPImg,CWD,ActiveP_index
    
    #Target_Item.set(4)
    #Target_Magic.set(4)
    if G_Monster[1].ID!=0:
        Target_Action.set(4)
        if ActiveM_index!=1:
            ActiveM_index=1
        M_canv[1].config(highlightthickness=3,highlightbackground='yellow')
        M_canv[2].config(highlightthickness=1,highlightbackground='red')
        M_canv[0].config(highlightthickness=1,highlightbackground='red')
        G_Monster[1].UpdateGUI(GUIs_monster[1])

        temp_str=G_Monster[ActiveM_index].Get_Description()
        if G_Player[ActiveP_index].ID!=0: #add probabilities
            prob=G_Monster[ActiveM_index].ProbCalc(G_Player[ActiveP_index])
            temp_str=temp_str+'Chances: Hit='+str(prob[0])+'% Attack you='+str(prob[3])+'% Recruit='+str(prob[1])+'% Talk='+str(prob[2])+'%'
        # disply info to textbox
        S_Info_text.config(state='normal')
        S_Info_text.delete(1.0,tk.END)
        S_Info_text.insert(1.0,temp_str)
        S_Info_text.config(state='disabled')

        # get canv size
        S_Info_Canvs.update()
        W=S_Info_Canvs.winfo_width()
        H=S_Info_Canvs.winfo_height()
        PublicImg=Image.open(CWD+G_Monster[ActiveM_index].Pic)
        PublicPImg=ImageTk.PhotoImage(PublicImg.resize((W-4,H-4)))

        S_Info_Canvs.create_image(2,2,anchor=tk.NW,image=PublicPImg)

def M3_Canv_Click(event):
    global ActiveM_index,PublicImg,PublicPImg,CWD,ActiveP_index
    
    #Target_Item.set(5)
    #Target_Magic.set(5)

    if G_Monster[2].ID!=0:
        Target_Action.set(5)
        if ActiveM_index!=2:
            ActiveM_index=2
        M_canv[1].config(highlightthickness=1,highlightbackground='red')
        M_canv[2].config(highlightthickness=3,highlightbackground='yellow')
        M_canv[0].config(highlightthickness=1,highlightbackground='red')
        G_Monster[2].UpdateGUI(GUIs_monster[2])

        temp_str=G_Monster[ActiveM_index].Get_Description()
        if G_Player[ActiveP_index].ID!=0: #add probabilities
            prob=G_Monster[ActiveM_index].ProbCalc(G_Player[ActiveP_index])
            temp_str=temp_str+'Chances: Hit='+str(prob[0])+'% Attack you='+str(prob[3])+'% Recruit='+str(prob[1])+'% Talk='+str(prob[2])+'%'
        # disply info to textbox
        S_Info_text.config(state='normal')
        S_Info_text.delete(1.0,tk.END)
        S_Info_text.insert(1.0,temp_str)
        S_Info_text.config(state='disabled')

        # get canv size
        S_Info_Canvs.update()
        W=S_Info_Canvs.winfo_width()
        H=S_Info_Canvs.winfo_height()
        PublicImg=Image.open(CWD+G_Monster[ActiveM_index].Pic)
        PublicPImg=ImageTk.PhotoImage(PublicImg.resize((W-4,H-4)))

        S_Info_Canvs.create_image(2,2,anchor=tk.NW,image=PublicPImg)

def P_Inv_Item_Click(event):
    global ActiveP_index,ActivePI_index

    if NbPA_Inv_item.curselection()!=(): # get the index
        tempIdx=NbPA_Inv_item.curselection()[0]
        ActivePI_index=tempIdx
        if G_Player[ActiveP_index].Item[tempIdx].ID!=0:  # see if Item is empty
            
            temp_str=G_Player[ActiveP_index].Item[tempIdx].Get_Description()#GetInfo()
            # disply info to textbox
            S_Info_text.config(state='normal')
            S_Info_text.delete(1.0,tk.END)
            S_Info_text.insert(1.0,temp_str)
            S_Info_text.config(state='disabled')
            # get canv size
            S_Info_Canvs.update()
            W=S_Info_Canvs.winfo_width()
            H=S_Info_Canvs.winfo_height()
            tempImg=G_Player[ActiveP_index].Item[tempIdx].Img.resize((W-4,H-4))
            G_Player[ActiveP_index].Item[tempIdx].PImg=ImageTk.PhotoImage(tempImg)
            S_Info_Canvs.create_image(2,2,anchor=tk.NW,image=G_Player[ActiveP_index].Item[tempIdx].PImg)
            

            # Active Player Item.img resize, get Pimg, display

def P_Inv_Equip_Click(event):
    global ActiveP_index,ActivePE_index

    if NbPE_Inv.curselection()!=(): # get the index
        tempIdx=NbPE_Inv.curselection()[0]
        ActivePE_index=tempIdx
        if G_Player[ActiveP_index].Equipment[tempIdx].ID!=0:  # see if Item is empty
            #ActivePE_index=tempIdx
            temp_str=G_Player[ActiveP_index].Equipment[tempIdx].Get_Description()#GetInfo()
            # disply info to textbox
            S_Info_text.config(state='normal')
            S_Info_text.delete(1.0,tk.END)
            S_Info_text.insert(1.0,temp_str)
            S_Info_text.config(state='disabled')
            # get canv size
            S_Info_Canvs.update()
            W=S_Info_Canvs.winfo_width()
            H=S_Info_Canvs.winfo_height()
            tempImg=G_Player[ActiveP_index].Equipment[tempIdx].Img.resize((W-4,H-4))
            G_Player[ActiveP_index].Equipment[tempIdx].PImg=ImageTk.PhotoImage(tempImg)
            S_Info_Canvs.create_image(2,2,anchor=tk.NW,image=G_Player[ActiveP_index].Equipment[tempIdx].PImg)

def P_Inv_Magic_Click(event):
    global ActiveP_index,ActivePM_index

    if NbPA_Inv_mag.curselection()!=(): # get the index
        tempIdx=NbPA_Inv_mag.curselection()[0]
        ActivePM_index=tempIdx
        if G_Player[ActiveP_index].Magic[tempIdx].ID!=0:  # see if Item is empty
            #ActivePM_index=tempIdx
            temp_str=G_Player[ActiveP_index].Magic[tempIdx].Get_Description()#GetInfo()
            # disply info to textbox
            S_Info_text.config(state='normal')
            S_Info_text.delete(1.0,tk.END)
            S_Info_text.insert(1.0,temp_str)
            S_Info_text.config(state='disabled')
            # get canv size
            S_Info_Canvs.update()
            W=S_Info_Canvs.winfo_width()
            H=S_Info_Canvs.winfo_height()
            tempImg=G_Player[ActiveP_index].Magic[tempIdx].Img.resize((W-4,H-4))
            G_Player[ActiveP_index].Magic[tempIdx].PImg=ImageTk.PhotoImage(tempImg)
            S_Info_Canvs.create_image(2,2,anchor=tk.NW,image=G_Player[ActiveP_index].Magic[tempIdx].PImg)

def M_Inv_Item_Click(event):
    global ActiveM_index,ActiveMI_index

    if NbMI_Inv.curselection()!=(): # get the index
        tempIdx=NbMI_Inv.curselection()[0]
        ActiveMI_index=tempIdx
        if G_Monster[ActiveM_index].Item[tempIdx].ID!=0:  # see if Item is empty
            
            temp_str=G_Monster[ActiveM_index].Item[tempIdx].Get_Description()#GetInfo()
            # disply info to textbox
            S_Info_text.config(state='normal')
            S_Info_text.delete(1.0,tk.END)
            S_Info_text.insert(1.0,temp_str)
            S_Info_text.config(state='disabled')
            # get canv size
            S_Info_Canvs.update()
            W=S_Info_Canvs.winfo_width()
            H=S_Info_Canvs.winfo_height()
            tempImg=G_Monster[ActiveM_index].Item[tempIdx].Img.resize((W-4,H-4))
            G_Monster[ActiveM_index].Item[tempIdx].PImg=ImageTk.PhotoImage(tempImg)
            S_Info_Canvs.create_image(2,2,anchor=tk.NW,image=G_Monster[ActiveM_index].Item[tempIdx].PImg)
        
        

            # Active Player Item.img resize, get Pimg, display

def M_Inv_Equip_Click(event):
    global ActiveM_index,ActiveME_index

    if NbME_Inv.curselection()!=(): # get the index
        tempIdx=NbME_Inv.curselection()[0]
        ActiveME_index=tempIdx
        if G_Monster[ActiveM_index].Equipment[tempIdx].ID!=0:  # see if Item is empty
            
            temp_str=G_Monster[ActiveM_index].Equipment[tempIdx].Get_Description()#GetInfo()
            # disply info to textbox
            S_Info_text.config(state='normal')
            S_Info_text.delete(1.0,tk.END)
            S_Info_text.insert(1.0,temp_str)
            S_Info_text.config(state='disabled')
            # get canv size
            S_Info_Canvs.update()
            W=S_Info_Canvs.winfo_width()
            H=S_Info_Canvs.winfo_height()
            tempImg=G_Monster[ActiveM_index].Equipment[tempIdx].Img.resize((W-4,H-4))
            G_Monster[ActiveM_index].Equipment[tempIdx].PImg=ImageTk.PhotoImage(tempImg)
            S_Info_Canvs.create_image(2,2,anchor=tk.NW,image=G_Monster[ActiveM_index].Equipment[tempIdx].PImg)

def M_Inv_Magic_Click(event):
    global ActiveM_index,ActiveMM_index

    if NbMM_Inv.curselection()!=(): # get the index
        tempIdx=NbMM_Inv.curselection()[0]
        ActiveMM_index=tempIdx
        if G_Monster[ActiveM_index].Magic[tempIdx].ID!=0:  # see if Item is empty
            
            temp_str=G_Monster[ActiveM_index].Magic[tempIdx].Get_Description()#GetInfo()
            # disply info to textbox
            S_Info_text.config(state='normal')
            S_Info_text.delete(1.0,tk.END)
            S_Info_text.insert(1.0,temp_str)
            S_Info_text.config(state='disabled')
            # get canv size
            S_Info_Canvs.update()
            W=S_Info_Canvs.winfo_width()
            H=S_Info_Canvs.winfo_height()
            tempImg=G_Monster[ActiveM_index].Magic[tempIdx].Img.resize((W-4,H-4))
            G_Monster[ActiveM_index].Magic[tempIdx].PImg=ImageTk.PhotoImage(tempImg)
            S_Info_Canvs.create_image(2,2,anchor=tk.NW,image=G_Monster[ActiveM_index].Magic[tempIdx].PImg)

def M_Cav_Equip_Click(event,Indx):
    global ActiveM_index,ActiveMEq_index,PImg_ME

    tempIdx=Indx
    if G_Monster[ActiveM_index].Equiped[tempIdx].ID!=0:  # see if Item is empty
        ActiveMEq_index=tempIdx
        for ii in range(15):
            NbME_Canvs[ii].config(highlightthickness=1,highlightbackground='red')
        NbME_Canvs[tempIdx].config(highlightthickness=3,highlightbackground='yellow')
        temp_str=G_Monster[ActiveM_index].Equiped[tempIdx].Get_Description()#GetInfo()
        # disply info to textbox
        S_Info_text.config(state='normal')
        S_Info_text.delete(1.0,tk.END)
        S_Info_text.insert(1.0,temp_str)
        S_Info_text.config(state='disabled')
        # get canv size
        S_Info_Canvs.update()
        W=S_Info_Canvs.winfo_width()
        H=S_Info_Canvs.winfo_height()
        tempImg=G_Monster[ActiveM_index].Equiped[tempIdx].Img.resize((W-4,H-4))
        PImg_ME=ImageTk.PhotoImage(tempImg)
        S_Info_Canvs.create_image(2,2,anchor=tk.NW,image=PImg_ME)

def P_Cav_Equip_Click(event,Indx):
    global ActiveP_index,ActivePEq_index,PImg_PE

    tempIdx=Indx
    if G_Player[ActiveP_index].Equiped[tempIdx].ID!=0:  # see if Item is empty
        ActivePEq_index=tempIdx
        for ii in range(15):
            NbPE_Canvs[ii].config(highlightthickness=1,highlightbackground='red')
        NbPE_Canvs[tempIdx].config(highlightthickness=3,highlightbackground='yellow')
        temp_str=G_Player[ActiveP_index].Equiped[tempIdx].Get_Description()#GetInfo()
        # disply info to textbox
        S_Info_text.config(state='normal')
        S_Info_text.delete(1.0,tk.END)
        S_Info_text.insert(1.0,temp_str)
        S_Info_text.config(state='disabled')
        # get canv size
        S_Info_Canvs.update()
        W=S_Info_Canvs.winfo_width()
        H=S_Info_Canvs.winfo_height()
        tempImg=G_Player[ActiveP_index].Equiped[tempIdx].Img.resize((W-4,H-4))
        PImg_PE=ImageTk.PhotoImage(tempImg)
        S_Info_Canvs.create_image(2,2,anchor=tk.NW,image=PImg_PE)

def P_Btn_StatPlus(event,Indx):
    global ActiveP_index

    if G_Player[ActiveP_index].ID!=0 and G_Player[ActiveP_index].PT_stat>0:
        G_Player[ActiveP_index].Data_Base[Indx+3,0]+=1
        G_Player[ActiveP_index].PT_stat-=1
        G_Player[ActiveP_index].Update()
        G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])

def P_Btn_StatMinus():
    global ActiveP_index

    if G_Player[ActiveP_index].ID!=0 and G_Player[ActiveP_index].PT_stat>0:
        G_Player[ActiveP_index].Data_Base[6,0]-=1
        G_Player[ActiveP_index].PT_stat-=1
        G_Player[ActiveP_index].Update()
        G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])

def P_Btn_EqUpgrade_Click(event):
    global ActivePE_index,ActiveP_index

    if G_Player[ActiveP_index].ID!=0 and G_Player[ActiveP_index].PT_equip>0:
        if G_Player[ActiveP_index].Equipment[ActivePE_index].ID!=0:
            cost=G_Player[ActiveP_index].Equipment[ActivePE_index].Get_UpgradePT()
            if G_Player[ActiveP_index].PT_equip>=cost:
                if G_Player[ActiveP_index].Equipment[ActivePE_index].Upgrade():
                    G_Player[ActiveP_index].PT_equip-=cost

                    #update display
                    temp_str=G_Player[ActiveP_index].Equipment[ActivePE_index].Get_Description()#GetInfo()
                    # disply info to textbox
                    S_Info_text.config(state='normal')
                    S_Info_text.delete(1.0,tk.END)
                    S_Info_text.insert(1.0,temp_str)
                    S_Info_text.config(state='disabled')

                    G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])
                    NbPE_Inv.selection_set(ActivePE_index)

            else:
                messagebox.showinfo('Upgrade fail','You need at least '+str(cost) +' EQ points to upgrade this!')

def P_Btn_EqTakeoff_Click(event):
    global ActivePE_index,ActiveP_index,ActivePEq_index

    if G_Player[ActiveP_index].ID!=0 and G_Player[ActiveP_index].Equiped[ActivePEq_index].ID!=0:
        if G_Player[ActiveP_index].Equipment_Takeoff(ActivePEq_index):
            
            temp_str='Equipment was taken off and put back in Inventory.\n\nYou can now upgrade it if you want.'
            # disply info to textbox
            S_Info_text.config(state='normal')
            S_Info_text.delete(1.0,tk.END)
            S_Info_text.insert(1.0,temp_str)
            S_Info_text.config(state='disabled')
            #G_Player[ActiveP_index].Update()
            G_Player[ActiveP_index].LoadImg(CWD)
            G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])

def P_Btn_EqPuton_Click(event):  # cost AP, this limit the freedom to switch Equip freely in combat, do it in safe zone
    global ActivePE_index,ActiveP_index,ActivePEq_index, G_Events,Dict_Equipment

    if G_Player[ActiveP_index].ActPT<=0: # individual Player out of AP, try someone else
        messagebox.showinfo('Fail','You run out of your AP!\nWait for next turn.')
        return

    if G_Player[ActiveP_index].ID!=0 and G_Player[ActiveP_index].Equipment[ActivePE_index].ID!=0:
        if G_Player[ActiveP_index].Equipment_Equip(ActivePE_index):
            G_Player[ActiveP_index].AP_Down()
            temp_str='You slap this equipment on.\n\nReady to rock!!!.'
            # check special set event
            setID=[33,36,37,38,39,40,41]
            locID=[7,8,9,10,11,12,13,14]

            if G_Player[ActiveP_index].Equiped_Set(setID): #got balls 
                
                # get rid of all balls
                G_Player[ActiveP_index].N_Equip+=1  #get a temp slot open
                
                for jj in range(7):
                    G_Player[ActiveP_index].Equipment_Takeoff(locID[jj])
                    for ii in range(G_Player[ActiveP_index].N_Equip):
                        if G_Player[ActiveP_index].Equipment[ii].ID==setID[jj]:
                            G_Player[ActiveP_index].Equipment[ii]=Equipment()
                
                G_Player[ActiveP_index].N_Equip-=1


                if G_Events[0]==0: #first time
                    G_Events[0]=1  #mark the event off
                    G_Player[ActiveP_index].Equiped[7]=copy.copy(Dict_Equipment[43])
                    G_Player[ActiveP_index].Data_Derive[0,4]+=25
                    G_Player[ActiveP_index].Data_Base[17,4]+=15

                    temp_str='You completed all 7 dragon balls for the first time!\nYou obtained Necklace of Life!\nThis is a unique Item that can only be obtained using Dragon balls.'
                    Show_Story('\n'+temp_str,'T_green')

                else: #more times
                    G_Player[ActiveP_index].Data_Derive[0,3]+=5
                    G_Player[ActiveP_index].Data_Base[17,3]+=5

                    Show_Story('\nYou gathered all dragon balls again!\nUsing the balls, your HP and HP regan increased by 5% permenantly!','T_green')



                # put on reward


            # disply info to textbox
            S_Info_text.config(state='normal')
            S_Info_text.delete(1.0,tk.END)
            S_Info_text.insert(1.0,temp_str)
            S_Info_text.config(state='disabled')

            G_Player[ActiveP_index].LoadImg(CWD)

            G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])

            Stuff_After_Player_Action()
        
def P_Btn_EqSell_Click(event):
    global ActivePE_index,ActiveP_index,ActivePEq_index

    if G_Player[ActiveP_index].ID!=0 and G_Player[ActiveP_index].Equipment[ActivePE_index].ID!=0:
        G_Player[ActiveP_index].Equipment_Sell(ActivePE_index)
        
        temp_str='You get rid of this by selling it...\n\nMore space for better equipment!!!.'
        # disply info to textbox
        S_Info_text.config(state='normal')
        S_Info_text.delete(1.0,tk.END)
        S_Info_text.insert(1.0,temp_str)
        S_Info_text.config(state='disabled')
        G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])
        
def P_Btn_EqThrow_Click(event):
    global ActivePE_index,ActiveP_index,ActivePEq_index

    if G_Player[ActiveP_index].ID!=0 and G_Player[ActiveP_index].Equipment[ActivePE_index].ID!=0:
        
        if G_Box_EquipN==G_Box_Equip_In:
            #temp_str='You get rid of this by throwing it...\n\nMore space for better equipment!!!.'
            messagebox.showinfo('Fail','Your Box is full! You cannot store anymore.')
            return
        else:
            temp_str='You put this into public Box.'
            foundit=False
            indx=0
            for ii in range(G_Box_EquipN):
                if not foundit and G_Box_Equip[ii].ID==0:
                    foundit=True
                    indx=ii
            G_Box_Equip[indx]=copy.copy(G_Player[ActiveP_index].Equipment[ActivePE_index])
            Box_updateGUI()

        G_Player[ActiveP_index].Equipment_RemoveList(ActivePE_index)       

        # disply info to textbox
        S_Info_text.config(state='normal')
        S_Info_text.delete(1.0,tk.END)
        S_Info_text.insert(1.0,temp_str)
        S_Info_text.config(state='disabled')
        G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])
        
def P_Item_Throw_Click():
    global ActivePI_index,ActiveP_index

    #print(Target_Item.get())

    if G_Player[ActiveP_index].ID!=0 and G_Player[ActiveP_index].Item[ActivePI_index].ID!=0:
        
        if G_Box_ItemN==G_Box_Item_In:
            #temp_str='You get rid of this by throwing it...\n\nMore space for better Items!!!.'
            messagebox.showinfo('Full','Your Box is Full. Cannot store anymore.')
            return
        else:
            temp_str='You put this into public Box.'
            foundit=False
            indx=0
            for ii in range(G_Box_ItemN):
                if not foundit and G_Box_Item[ii].ID==0:
                    foundit=True
                    indx=ii
            G_Box_Item[indx]=copy.copy(G_Player[ActiveP_index].Item[ActivePI_index])
            Box_updateGUI()

        G_Player[ActiveP_index].Item_RemoveList(ActivePI_index)
                
        # disply info to textbox
        S_Info_text.config(state='normal')
        S_Info_text.delete(1.0,tk.END)
        S_Info_text.insert(1.0,temp_str)
        S_Info_text.config(state='disabled')
        G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])

def P_Item_Sell_Click():
    global ActivePI_index,ActiveP_index

    #print(Target_Item.get())

    if G_Player[ActiveP_index].ID!=0 and G_Player[ActiveP_index].Item[ActivePI_index].ID!=0:
        G_Player[ActiveP_index].Item_Sell(ActivePI_index)
        
        temp_str='You get rid of this by selling it...\nCash and More space for better Item!!!.'
        # disply info to textbox
        S_Info_text.config(state='normal')
        S_Info_text.delete(1.0,tk.END)
        S_Info_text.insert(1.0,temp_str)
        S_Info_text.config(state='disabled')
        G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])

def P_Item_Use_Click():   # cost AP--check turn
    global ActivePI_index,ActiveP_index,Zone_info

    if G_Player[ActiveP_index].ActPT<=0: # individual Player out of AP, try someone else
        messagebox.showinfo('Fail','You run out of your AP!\nWait for next turn.')
        return

    if G_Player[ActiveP_index].ID!=0 and G_Player[ActiveP_index].Item[ActivePI_index].ID!=0: #player and item exist
        tempIndx=Target_Action.get()
        if tempIndx<0 or tempIndx>5:
            messagebox.showinfo('Item Use Fail','No target selected. Select your target player first!')
        else:
            if tempIndx<=2: #target is player
                if G_Player[ActiveP_index].Item[ActivePI_index].Is_Attack():
                    MsgConfirm=messagebox.askquestion('Sure?','Are you sure you want to ATTACK your own team?')
                    if MsgConfirm=='no':
                        return

                tempItemName=G_Player[ActiveP_index].Item[ActivePI_index].Name
                HP_old=G_Player[tempIndx].HP
                eft=G_Player[ActiveP_index].Item_Use(ActivePI_index)
                G_Player[tempIndx].ApplyEffect(eft)
                HP_new=G_Player[tempIndx].HP
                HP_Change=HP_new-HP_old
                if tempIndx==ActiveP_index:
                    Show_Story('\n'+G_Player[ActiveP_index].Name +' used '+ tempItemName + ' on himself.\n')
                else:
                    Show_Story('\n'+G_Player[ActiveP_index].Name +' used '+ tempItemName + ' on '+ G_Player[tempIndx].Name+'.\n')
                if HP_Change>0:
                    Show_Story('HP restored by '+str(int(HP_Change))+'\n','T_green')
                if HP_Change<0:
                    Show_Story('Caused '+str(int(-HP_Change))+' Damage!\n','T_red')

                if G_Player[tempIndx].Update():
                    G_Player[tempIndx].UpdateGUI_Basic(GUIs_player[tempIndx])
                else: #killed
                    
                    
                    Show_Story(G_Player[tempIndx].Name+' was killed!\n','T_red')
                    
                    #put remain in drop...no, let it lost everything as you could planned the kill
                    G_Player[tempIndx]=Player()  #replace with an empty player
                    G_Player[tempIndx].LoadImg(CWD)
                    G_Player[tempIndx].UpdateGUI(GUIs_player[tempIndx])


                G_Player[ActiveP_index].Item_RemoveList(ActivePI_index)
                G_Player[ActiveP_index].AP_Down()
                G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])
            else:
                tempIndx-=3
                tempItemName=G_Player[ActiveP_index].Item[ActivePI_index].Name
                HP_old=G_Monster[tempIndx].HP
                eft=G_Player[ActiveP_index].Item_Use(ActivePI_index)
                G_Monster[tempIndx].ApplyEffect(eft)
                HP_new=G_Monster[tempIndx].HP
                HP_Change=HP_new-HP_old

                Show_Story('\n'+G_Player[ActiveP_index].Name +' used '+ tempItemName + ' on '+ G_Monster[tempIndx].Name+' and caused '+str(int(-HP_Change))+' Damage.\n','T_blue')

                if G_Monster[tempIndx].Update():
                    G_Monster[tempIndx].UpdateGUI_Basic(GUIs_monster[tempIndx])
                else:
                    #put remains in drop
                    LootN=Remain_Kill_Drop(G_Player[ActiveP_index],G_Monster[tempIndx])
                    Drop_updateGUI()
                    Show_Story('\n'+ G_Monster[tempIndx].Name+' was totally destroied.\n'+G_Player[ActiveP_index].Name+' obtained:'+G_Monster[tempIndx].REM.To_string()+'\nDont forget to Check Drop place for '+str(LootN)+' loots it dropped!')
                    Zone_info.AddKill(G_Monster[tempIndx].Zone)
                    temp=Zone_info.Update_Boss(G_Monster[tempIndx].ID)
                    if temp>0:
                        if temp<Zone_info.N-1:
                            messagebox.showinfo('Zone unlocked','You unlocked a New Zone: '+Zone_info.Name[temp+1]+'!')
                        else: #you just beat the last zone
                            messagebox.showinfo('Congratulations!','You just completed this Game!')

                    Show_Story(Zone_info.Name[G_Zone]+' Progress is: '+Zone_info.Str_progress(G_Zone) +'\n','T_blue')

                    G_Monster[tempIndx]=Player()
                    G_Monster[tempIndx].LoadImg(CWD)
                    G_Monster[tempIndx].UpdateGUI(GUIs_monster[tempIndx])

                G_Player[ActiveP_index].Item_RemoveList(ActivePI_index)
                G_Player[ActiveP_index].AP_Down()
                G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])

    Stuff_After_Player_Action()            

def P_Magic_Forget_Click():
    global ActivePM_index,ActiveP_index

    #print(Target_Item.get())

    if G_Player[ActiveP_index].ID!=0 and G_Player[ActiveP_index].Magic[ActivePM_index].ID!=0:
        if messagebox.askquestion('Forget Magic','Are you sure you wan to forget '+ G_Player[ActiveP_index].Magic[ActivePM_index].Name+'?\n\nThe skill will be totally LOST.\nNo regret?')=='yes':
            G_Player[ActiveP_index].Magic_Forget(ActivePM_index)

            temp_str='You concentrated and purged a Magic skill from your brain.\n\nMore space for better Magic!!!.'
            # disply info to textbox
            S_Info_text.config(state='normal')
            S_Info_text.delete(1.0,tk.END)
            S_Info_text.insert(1.0,temp_str)
            S_Info_text.config(state='disabled')
            G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])

def P_Magic_Upgrade_Click():
    global ActivePM_index,ActiveP_index

    #print(Target_Item.get())

    if G_Player[ActiveP_index].ID!=0 and G_Player[ActiveP_index].Magic[ActivePM_index].ID!=0:
        cost=G_Player[ActiveP_index].Magic[ActivePM_index].Get_UpgradePT()
        if G_Player[ActiveP_index].PT_mag>=cost:
            if G_Player[ActiveP_index].Magic[ActivePM_index].Upgrade():
                G_Player[ActiveP_index].PT_mag-=cost

                #update display
                temp_str=G_Player[ActiveP_index].Magic[ActivePM_index].Get_Description()#GetInfo()
                # disply info to textbox
                S_Info_text.config(state='normal')
                S_Info_text.delete(1.0,tk.END)
                S_Info_text.insert(1.0,temp_str)
                S_Info_text.config(state='disabled')
                G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])
                NbPA_Inv_mag.selection_set(ActivePM_index)
        else:
            messagebox.showinfo('Upgrade fail','You need at least '+str(cost) +' Magic points to upgrade this!')

def P_Magic_Use_Click():  # cost AP--check turn
    global ActivePM_index,ActiveP_index

    if G_Player[ActiveP_index].ActPT<=0: # individual Player out of AP, try someone else
        messagebox.showinfo('Fail','You run out of your AP!\nWait for next turn.')
        return

    if G_Player[ActiveP_index].ID!=0 and G_Player[ActiveP_index].Magic[ActivePM_index].ID!=0: #player and Magic exist
        tempIndx=Target_Action.get()
        cost=G_Player[ActiveP_index].Magic[ActivePM_index].Get_MPcost()
        if tempIndx<0 or tempIndx>5:
            messagebox.showinfo('Magic cast Fail','No target selected. Select your target player first!')
        else:
            if G_Player[ActiveP_index].MP<cost:
                messagebox.showinfo('Magic cast Fail','Not enough MP!\nYou need '+str(int(cost))+' MP for this. Try drink up a potion or something...')
            else:    
                if tempIndx<=2: #target is player
                    if G_Player[ActiveP_index].Magic[ActivePM_index].Is_Attack():
                        MsgConfirm=messagebox.askquestion('Sure?','Are you sure you want to ATTACK your own team?')
                        if MsgConfirm=='no':
                            return

                    eft=G_Player[ActiveP_index].Magic_Use(ActivePM_index)
                    if eft!=0:
                        HP_old=G_Player[tempIndx].HP
                        G_Player[tempIndx].ApplyEffect(eft)
                        HP_new=G_Player[tempIndx].HP
                        HP_Change=HP_new-HP_old

                        Show_Story('\n'+G_Player[ActiveP_index].Name +' used '+ G_Player[ActiveP_index].Magic[ActivePM_index].Name + ' on '+ G_Player[tempIndx].Name+'. HP change='+str(int(HP_Change))+'.\n','T_blue')

                        if G_Player[tempIndx].Update():
                            G_Player[tempIndx].UpdateGUI_Basic(GUIs_player[tempIndx])
                        else: #killed
                            Show_Story(G_Player[tempIndx].Name+' was killed!\n','T_red')
                            
                            #put remain in drop...no, let it lost everything as you could planned the kill
                            G_Player[tempIndx]=Player()  #replace with an empty player
                            G_Player[tempIndx].LoadImg(CWD)
                            G_Player[tempIndx].UpdateGUI(GUIs_player[tempIndx])


                        #G_Player[ActiveP_index].Item_RemoveList(ActivePI_index)
                        G_Player[ActiveP_index].Data_Base[2,0]-=cost
                        G_Player[ActiveP_index].Update()
                        G_Player[ActiveP_index].AP_Down()
                        G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])
                        NbPA_Inv_mag.selection_set(ActivePM_index)
                    else:
                        messagebox.showinfo('Magic cast Fail','Requirements for Magic not met')
                else:
                    tempIndx-=3
                    eft=G_Player[ActiveP_index].Magic_Use(ActivePM_index)
                    if eft!=0:

                        HP_old=G_Monster[tempIndx].HP
                        G_Monster[tempIndx].ApplyEffect(eft)
                        HP_new=G_Monster[tempIndx].HP
                        HP_Change=HP_new-HP_old

                        Show_Story('\n'+G_Player[ActiveP_index].Name +' used '+ G_Player[ActiveP_index].Magic[ActivePM_index].Name + ' on '+ G_Monster[tempIndx].Name+' and inflicted '+str(int(-HP_Change))+' Damage.\n','T_blue')

                        
                        if G_Monster[tempIndx].Update():
                            G_Monster[tempIndx].UpdateGUI_Basic(GUIs_monster[tempIndx])
                        else:
                            #put remains in drop
                            LootN=Remain_Kill_Drop(G_Player[ActiveP_index],G_Monster[tempIndx])
                            Drop_updateGUI()
                            Show_Story('\n'+ G_Monster[tempIndx].Name+' was totally destroied.\n'+G_Player[ActiveP_index].Name+' obtained:'+G_Monster[tempIndx].REM.To_string()+'\nDont forget to Check Drop place for '+str(LootN)+' loots it dropped!')

                            Zone_info.AddKill(G_Monster[tempIndx].Zone)
                            temp=Zone_info.Update_Boss(G_Monster[tempIndx].ID)
                            if temp>0:
                                if temp<Zone_info.N-1:
                                    messagebox.showinfo('Zone unlocked','You unlocked a New Zone: '+Zone_info.Name[temp+1]+'!')
                                else: #you just beat the last zone
                                    messagebox.showinfo('Congratulations!','You just completed this Game!')

                            Show_Story(Zone_info.Name[G_Zone]+' Progress is: '+Zone_info.Str_progress(G_Zone) +'\n','T_blue')

                            G_Monster[tempIndx]=Player()
                            G_Monster[tempIndx].LoadImg(CWD)
                            G_Monster[tempIndx].UpdateGUI(GUIs_monster[tempIndx])
                        #G_Player[ActiveP_index].Item_RemoveList(ActivePI_index)
                        G_Player[ActiveP_index].Data_Base[2,0]-=cost
                        G_Player[ActiveP_index].Update()
                        G_Player[ActiveP_index].AP_Down()
                        G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])
                        NbPA_Inv_mag.selection_set(ActivePM_index)
                    else:
                        messagebox.showinfo('Magic cast Fail','Requirements for Magic not met')

    Stuff_After_Player_Action()

def P_Attack_Click():    # Cost AP--Check Turn
    global ActiveP_index

    if G_Player[ActiveP_index].ActPT<=0: # individual Player out of AP, try someone else
        messagebox.showinfo('Fail','You run out of your AP!\nWait for next turn.')
        return

    if G_Player[ActiveP_index].ID!=0: #player exist, Do action, reduce player AP
        tempIndx=Target_Action.get()
        
        if tempIndx<0 or tempIndx>5:
            messagebox.showinfo('Attack Fail','No target selected. Select your target player first!')
        else:
            
            if tempIndx<=2 and G_Player[tempIndx].ID!=0: #target is player and he exist
                MsgConfirm=messagebox.askquestion('Sure?','Are you sure you want to ATTACK your own team?')
                if MsgConfirm=='no':
                    return

                eft=G_Player[ActiveP_index].Attack()
                HP_old=G_Player[tempIndx].HP
                G_Player[tempIndx].ApplyEffect(eft)
                HP_new=G_Player[tempIndx].HP
                HP_Change=HP_new-HP_old

                Show_Story('\n'+G_Player[ActiveP_index].Name +' attacked '+ G_Player[tempIndx].Name+' for '+str(int(-HP_Change))+' damage.\n','T_blue')
                
                if G_Player[tempIndx].Update():
                    G_Player[tempIndx].UpdateGUI_Basic(GUIs_player[tempIndx])
                else: #killed
                    #put remain in drop...no, let it lost everything as you could planned the kill
                    Show_Story(G_Player[tempIndx].Name+' was killed!\n','T_red')
                    
                    G_Player[tempIndx]=Player()  #replace with an empty player
                    G_Player[tempIndx].LoadImg(CWD)
                    G_Player[tempIndx].UpdateGUI(GUIs_player[tempIndx])

                G_Player[ActiveP_index].AP_Down()             
                G_Player[ActiveP_index].Update()
                G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])
                
            else:
                tempIndx-=3
                eft=G_Player[ActiveP_index].Attack()
                if G_Monster[tempIndx].ID!=0:  #if monster exist
                    if G_Player[ActiveP_index].Success_Attack(G_Monster[tempIndx]):
                        HP_old=G_Monster[tempIndx].HP
                        G_Monster[tempIndx].ApplyEffect(eft)
                        HP_new=G_Monster[tempIndx].HP
                        HP_Change=HP_new-HP_old

                        Show_Story('\n'+G_Player[ActiveP_index].Name +' attacked '+ G_Monster[tempIndx].Name+' for '+str(int(-HP_Change))+' damage.\n','T_blue')
                        if not G_Monster[tempIndx].Angry:
                            Show_Story(G_Monster[tempIndx].Name +' is now PISSED!\n','T_red')
                            G_Monster[tempIndx].Angry=True

                        if G_Monster[tempIndx].Update():
                            G_Monster[tempIndx].UpdateGUI_Basic(GUIs_monster[tempIndx])
                        else:
                            #put remains in drop
                            LootN=Remain_Kill_Drop(G_Player[ActiveP_index],G_Monster[tempIndx])
                            Drop_updateGUI()
                            Show_Story('\n'+ G_Monster[tempIndx].Name+' was totally destroied.\n'+G_Player[ActiveP_index].Name+' obtained:'+G_Monster[tempIndx].REM.To_string()+'\nDont forget to Check Drop place for '+str(LootN)+' loots it dropped!')

                            Zone_info.AddKill(G_Monster[tempIndx].Zone)
                            temp=Zone_info.Update_Boss(G_Monster[tempIndx].ID)
                            if temp>0:
                                if temp<Zone_info.N-1:
                                    messagebox.showinfo('Zone unlocked','You unlocked a New Zone: '+Zone_info.Name[temp+1]+'!')
                                else: #you just beat the last zone
                                    messagebox.showinfo('Congratulations!','You just completed this Game!\n\nYou can continue to play just for fun.')

                            Show_Story(Zone_info.Name[G_Zone]+' Progress is: '+Zone_info.Str_progress(G_Zone) +'\n','T_blue')

                            G_Monster[tempIndx]=Player()  #this clears the field, destroy remains
                            G_Monster[tempIndx].LoadImg(CWD)
                            G_Monster[tempIndx].UpdateGUI(GUIs_monster[tempIndx])


                        G_Player[ActiveP_index].AP_Down()
                        G_Player[ActiveP_index].Update()
                        G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])
                    else:
                        #attack failed miss
                        G_Player[ActiveP_index].AP_Down()
                        G_Player[ActiveP_index].Update()
                        G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])
                        Show_Story('\n'+G_Player[ActiveP_index].Name +' tried to attack '+ G_Monster[tempIndx].Name+' but missed!\n','T_red')
                    
                else:
                    messagebox.showinfo('Attack Fail','Selected Monster is not there')

    Stuff_After_Player_Action()

def P_Recruit_Click():  # cost AP--check turn
    global ActiveP_index

    if G_Player[ActiveP_index].ActPT<=0: # individual Player out of AP, try someone else
        messagebox.showinfo('Fail','You run out of your AP!\nWait for next turn.')
        return

    if G_Player[0].ID!=0 and G_Player[1].ID!=0 and G_Player[2].ID!=0:
        messagebox.showinfo('Recruit Fail','Your team has maximum number of members already!')
    else:
        if G_Player[ActiveP_index].ID!=0: #player exist
            tempIndx=Target_Action.get()
            if tempIndx<0 or tempIndx>5:
                messagebox.showinfo('Recruit Fail','No target selected. Select your target player first!')
            else:

                if tempIndx<=2 and G_Player[tempIndx].ID!=0: #target is player and he exist
                    messagebox.showinfo('Recruit fail',G_Player[tempIndx].Name+' is already in your team!')
                else:
                    tempIndx-=3
                    if G_Monster[tempIndx].ID!=0:  #if monster exist
                        G_Player[ActiveP_index].AP_Down()
                        if G_Player[ActiveP_index].Recruit(G_Monster[tempIndx]):

                            Show_Story('\n'+G_Player[ActiveP_index].Name +' recruited '+ G_Monster[tempIndx].Name+' into player team!\n','T_green')
                            for ii in range(3):
                                if G_Player[ii].ID==0:
                                    Eslot=ii
                            G_Player[Eslot]=copy.copy(G_Monster[tempIndx])
                            G_Player[Eslot].Data_Base[10,0]=100  #now M to P, initialize Drop rate to 1
                            G_Monster[tempIndx]=Player()
                            G_Monster[tempIndx].LoadImg(CWD)
                            G_Monster[tempIndx].UpdateGUI_Basic(GUIs_monster[tempIndx])
                            #G_Player[ActiveP_index].Item_RemoveList(ActivePI_index)

                            G_Player[Eslot].Update()
                            G_Player[Eslot].LoadImg(CWD)
                            G_Player[Eslot].UpdateGUI(GUIs_player[Eslot])
                        else:
                            Show_Story('\nYou tried to recruit '+G_Monster[tempIndx].Name+' but failed.','T_red')
                        G_Player[ActiveP_index].UpdateGUI_Basic(GUIs_player[ActiveP_index])  #show AP loss
                    else:
                        messagebox.showinfo('Recruit Fail','Selected Monster is not there')

    Stuff_After_Player_Action()

def P_Defend_Click():  # cost AP--check turn
    global ActiveP_index

    if G_Player[ActiveP_index].ActPT<=0: # individual Player out of AP, try someone else
        messagebox.showinfo('Fail','You run out of your AP!\nWait for next turn.')
        return

    if G_Player[ActiveP_index].ID!=0: #player exist
        G_Player[ActiveP_index].AP_Down()
        if G_Player[ActiveP_index].Defend():
            Show_Story('\n'+G_Player[ActiveP_index].Name + ' build up some defense.','T_green')
            G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])
        else:
            Show_Story('\n'+G_Player[ActiveP_index].Name + ' tried to "defense more" but there is no effect. You are already defending...\nYou wasted a turn!','T_red')
            G_Player[ActiveP_index].UpdateGUI_Basic(GUIs_player[ActiveP_index])
    
    Stuff_After_Player_Action()

def P_Talk_Click():  # cost AP--check turn
    global ActiveP_index

    if G_Player[ActiveP_index].ActPT<=0: # individual Player out of AP, try someone else
        messagebox.showinfo('Fail','You run out of your AP!\nWait for next turn.')
        return

    if G_Player[ActiveP_index].ID!=0: #player exist
        tempIndx=Target_Action.get()
        N=len(Dict_Talk)
        if tempIndx<0 or tempIndx>5:
            messagebox.showinfo('Talk Fail','No target selected. Select your target player first!')
        else:
            

            Show_Story('\n========Conversation========')
            if tempIndx<=2 and G_Player[tempIndx].ID!=0: #target is player and he exist

                if (G_Player[tempIndx].A+G_Player[tempIndx].I+G_Player[tempIndx].S)*3<(G_Player[0].A+G_Player[0].I+G_Player[0].S):
                    sure=messagebox.askyesno("Goodbye",'You talked with '+G_Player[tempIndx].Name+' to have him go home.\nThis is getting too dangerous for him...\nAre you sure you want remove him?')
                    if sure:
                        Show_Story('\nYou sent '+G_Player[tempIndx].Name+' home. This is getting to dangerous and he is not much help anymore.','T_blue')
                        G_Player[tempIndx]=Player()
                    else:
                        tid=np.random.randint(1,N-1)
                        if tempIndx==ActiveP_index:
                            Show_Story('\nWait...You talking to yourself? Well, that counts a turn, go ahead:\nYou told yourself:\n'+ Dict_Talk[tid]+'\n')
                        else:                
                            Show_Story('\n'+'You talked to '+ G_Player[tempIndx].Name+'.\n'+ G_Player[tempIndx].Name+' responded:\n'+ Dict_Talk[tid]+'\n')
                else:
                    tid=np.random.randint(1,N-1)
                    if tempIndx==ActiveP_index:
                        Show_Story('\nWait...You talking to yourself? Well, that counts a turn, go ahead:\nYou told yourself:\n'+ Dict_Talk[tid]+'\n')
                    else:                
                        Show_Story('\n'+'You talked to '+ G_Player[tempIndx].Name+'.\n'+ G_Player[tempIndx].Name+' responded:\n'+ Dict_Talk[tid]+'\n')


            else:
                tempIndx-=3
                if G_Monster[tempIndx].ID!=0:  #if monster exist

                    G_Player[ActiveP_index].AP_Down()  #only take AP if you talked with an existing monster
                    if G_Monster[tempIndx].Angry:
                        # do a roll to see if they can be calmed down
                        #X=((G_Player[ActiveP_index].I+G_Player[ActiveP_index].L-G_Monster[tempIndx].I-G_Monster[tempIndx].L)/(G_Monster[tempIndx].I+G_Monster[tempIndx].L))-2  #3 times sum to get 50/50 chance
                        #if G_Monster[tempIndx].C*G_Player[0].C>0 and abs(G_Player[0].C)>=abs(G_Monster[tempIndx].C): #only if the monster is same side as Main player [0] and main player is more famous than monster
                        #    X+=3  #may need to change later... we will see
                        #Nx=np.random.normal(0,1)  # draw from Standard Normal
                        if G_Player[ActiveP_index].Talk(G_Monster[tempIndx]):
                            G_Monster[tempIndx].Angry=False
                            tid=np.random.randint(1,N-1)
                            Show_Story('\n'+'You talked to '+ G_Monster[tempIndx].Name+'. You said:\n'+Dict_Talk[tid]+'\n\nAnd It worked! '+ G_Monster[tempIndx].Name+' Calmed down!','T_green')
                        else:
                            tid=np.random.randint(1,N-1)
                            Show_Story('\n'+'You talked to '+ G_Monster[tempIndx].Name+'. You said:\n'+Dict_Talk[tid]+'\n\nBut it does not work! '+ G_Monster[tempIndx].Name+' is still PISSED!','T_red')
                    else: 
                        # not angry
                        #random word
                        tid=np.random.randint(1,N-1)
                        tid1=np.random.randint(1,N-1)
                        Show_Story('\n'+'You talked to '+ G_Monster[tempIndx].Name+'. You said:\n'+Dict_Talk[tid]+'\n'+ G_Monster[tempIndx].Name+' responsed:\n'+Dict_Talk[tid1]+'\n')
                        # maybe some good stuff?
                        if G_Player[ActiveP_index].Talk(G_Monster[tempIndx]):
                            temp=np.random.random()
                            temp_x=int(temp*G_Monster[tempIndx].I)
                            Show_Story('Wow! thats SMART! it gave you '+str(temp_x)+'EXP!\n','T_green')
                            G_Player[ActiveP_index].Exp+=temp_x
                        else:
                            Show_Story('That does not make any sense...\n','T_red')

                    G_Player[ActiveP_index].UpdateGUI_Basic(GUIs_player[ActiveP_index])  #show AP loss
                else:
                    Show_Story('\nYou want to talk to...a dead or non-exist person?! Wired, Nothing happened.\n')

    Update_Players()

    Stuff_After_Player_Action()

def RunAway():
    global G_Zone,Zone_info,InBattle, MyTurn
    
    G_Player[ActiveP_index].AP_Down()

    X=np.random.random()
    if (G_Player[0].L+G_Player[1].L+G_Player[2].L)>0:
        lmt1=(G_Monster[0].L+G_Monster[1].L+G_Monster[2].L)/(G_Player[0].L+G_Player[1].L+G_Player[2].L)
    else:
        lmt1=0.8
    
    lmt=min(lmt1,0.8)  #no matter what you have 20% chance to escape, better luck 

    if not Monsters_Angry():
        lmt=-1  # certainly will be able to escape


    if X<lmt:
        Show_Story('\nGee!\nYou tried to escape but the monsters keep ganging up on you\nBad luck!!\nYour Escape Chance is '+str(int((1-lmt)*100))+'%\n','T_red')
        Stuff_After_Player_Action()

    else:
        for ii in range(3):
            G_Monster[ii]=Player()

        S_DropList.config(state='normal')  #enable buttons so the player can go or retreat
        if Zone_info.EnoughKill(G_Zone):
            S_Btn_Boss.config(state='normal',text='Boss Ready')
        else:
            S_Btn_Boss.config(state='disabled',text='Boss '+Zone_info.Str_progress(G_Zone))
        S_Btn_Retreat.config(state='normal')
        S_Btn_Go.config(state='normal')

        # Remove temp buff
        Players_RemoveBuff()  #this will happen between monster waves
        # let player rest
        Players_Rest()   #not full rest.    
        # Give control back to player
        MyTurn='Player'
        #print('monster gone function: '+str(G_Zone))
        Show_Story('\nPeww!!\nThat was close...but you escaped successfully.\nNow your Zone Progress is '+Zone_info.Str_progress(G_Zone)+'.\nWill you keep going or retreat?\n','T_green')
        # update zones, note this wave might be boss, so... update droplist based on complete values, Notification of boss happens when kill happens
        temp=S_DropList.current()     
        S_DropList.config(value=Zone_info.DisplayName())
        S_DropList.current(temp)

def B_Gather():
    global G_Money,G_PTmag,G_PTequip,Target_Box,ActiveP_index

    MyType=Target_Box.get()

    if MyType==0:        
        for ii in range(3):
            G_Money+=G_Player[ii].Money
            G_Player[ii].Money=0
    
    if MyType==1:        
        for ii in range(3):
            G_PTmag+=G_Player[ii].PT_mag
            G_Player[ii].PT_mag=0
    
    if MyType==2:        
        for ii in range(3):
            G_PTequip+=G_Player[ii].PT_equip
            G_Player[ii].PT_equip=0
        
    Box_updateGUI()
    G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])

def B_Take():
    global G_Money,G_PTmag,G_PTequip,Target_Box,ActiveP_index

    MyType=Target_Box.get()
    if not NbPB_Ent_amount.get().isnumeric():
        amount=-1
    else:
        amount=int(NbPB_Ent_amount.get())

    #print(int(NbPB_Ent_amount.get()))

    if MyType==0:
        if amount<0 or amount>G_Money:
            amount=G_Money
        G_Money-=amount
        G_Player[ActiveP_index].Money+=amount
    
    if MyType==1:
        if amount<0 or amount>G_PTmag:
            amount=G_PTmag
        G_PTmag-=amount
        G_Player[ActiveP_index].PT_mag+=amount

    if MyType==2:
        if amount<0 or amount>G_PTequip:
            amount=G_PTequip
        G_PTequip-=amount
        G_Player[ActiveP_index].PT_equip+=amount

        
    Box_updateGUI()
    G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])

def B_Inv_Item_Click(event):
    global ActiveBI_index

    if NbPB_Item.curselection()!=(): # get the index
        tempIdx=NbPB_Item.curselection()[0]
        ActiveBI_index=tempIdx
        if G_Box_Item[tempIdx].ID!=0:  # see if Item is empty
            G_Box_Item[tempIdx].LoadImg(CWD)
            
            temp_str=G_Box_Item[tempIdx].Get_Description() #GetInfo()
            # disply info to textbox
            S_Info_text.config(state='normal')
            S_Info_text.delete(1.0,tk.END)
            S_Info_text.insert(1.0,temp_str)
            S_Info_text.config(state='disabled')
            # get canv size
            S_Info_Canvs.update()
            W=S_Info_Canvs.winfo_width()
            H=S_Info_Canvs.winfo_height()
            tempImg=G_Box_Item[tempIdx].Img.resize((W-4,H-4))
            G_Box_Item[tempIdx].PImg=ImageTk.PhotoImage(tempImg)
            S_Info_Canvs.create_image(2,2,anchor=tk.NW,image=G_Box_Item[tempIdx].PImg)
            

            # Active Player Item.img resize, get Pimg, display

def B_Inv_Equip_Click(event):
    global ActiveBE_index

    if NbPB_Equip.curselection()!=(): # get the index
        tempIdx=NbPB_Equip.curselection()[0]
        ActiveBE_index=tempIdx
        if G_Box_Equip[tempIdx].ID!=0:  # see if Item is empty
            G_Box_Equip[tempIdx].LoadImg(CWD)
            
            temp_str=G_Box_Equip[tempIdx].Get_Description() #GetInfo()
            # disply info to textbox
            S_Info_text.config(state='normal')
            S_Info_text.delete(1.0,tk.END)
            S_Info_text.insert(1.0,temp_str)
            S_Info_text.config(state='disabled')
            # get canv size
            S_Info_Canvs.update()
            W=S_Info_Canvs.winfo_width()
            H=S_Info_Canvs.winfo_height()
            tempImg=G_Box_Equip[tempIdx].Img.resize((W-4,H-4))
            G_Box_Equip[tempIdx].PImg=ImageTk.PhotoImage(tempImg)
            S_Info_Canvs.create_image(2,2,anchor=tk.NW,image=G_Box_Equip[tempIdx].PImg)
            

            # Active Player Item.img resize, get Pimg, display

def B_Item_Sell_Click():
    global ActiveBI_index,G_Money

    if G_Box_Item[ActiveBI_index].ID!=0: 
        
        G_Money+=G_Box_Item[ActiveBI_index].Get_Cost()
        G_Box_Item[ActiveBI_index]=Item()
        Box_updateGUI()
       
def B_Equip_Sell_Click():
    global ActiveBE_index,G_Money

    if G_Box_Equip[ActiveBE_index].ID!=0: 
        G_Money+=G_Box_Equip[ActiveBE_index].Get_Cost()
        G_Box_Equip[ActiveBE_index]=Equipment()
        Box_updateGUI()       

def B_Item_Take_Click():
    global ActiveBI_index,ActiveP_index

    if G_Box_Item[ActiveBI_index].ID!=0 and G_Player[ActiveP_index].ID!=0: #both item and player exist
        index=G_Player[ActiveP_index].Item_EmptySlot()
        if index<0:
            messagebox.showinfo('Inventory Full','Player invetory full, cannot take Item.')
        else:
            G_Player[ActiveP_index].Item[index]=copy.copy(G_Box_Item[ActiveBI_index])
            G_Box_Item[ActiveBI_index]=Item()
            Box_updateGUI()
            G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])

def B_Equip_Take_Click():
    global ActiveBE_index,ActiveP_index

    if G_Box_Equip[ActiveBE_index].ID!=0 and G_Player[ActiveP_index].ID!=0: #both item and player exist
        index=G_Player[ActiveP_index].Equipment_EmptySlot()
        if index<0:
            messagebox.showinfo('Inventory Full','Player invetory full, cannot take Equipment.')
        else:
            G_Player[ActiveP_index].Equipment[index]=copy.copy(G_Box_Equip[ActiveBE_index])
            G_Box_Equip[ActiveBE_index]=Equipment()
            Box_updateGUI()
            G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])
       
def Buy_M_Equip(event):   #Need No AP
    global ActiveP_index,ActiveM_index,ActiveME_index

    if G_Player[ActiveP_index].ID==0:
        return
    
    #if G_Player[ActiveP_index].ActPT<=0: # individual Player out of AP, try someone else
    #    messagebox.showinfo('Fail','You run out of your AP!\nWait for next turn.')
    #    return

    # Check if Angry
    if G_Monster[ActiveM_index].Angry:
        messagebox.showinfo('Cannot Buy',G_Monster[ActiveM_index].Name+' is still Pissed and wont trade with you!')
    else:
        #check if selected
        if G_Monster[ActiveM_index].Equipment[ActiveME_index].ID!=0:
            cost=G_Monster[ActiveM_index].Equipment[ActiveME_index].Get_Cost()
            Pindx=G_Player[ActiveP_index].Equipment_EmptySlot()
            if Pindx<0:
                messagebox.showinfo('Cannot Buy','Your Equipment bag is full! Get rid of something before you buy.')
            else:
                if G_Player[ActiveP_index].Money>=cost:
                    G_Player[ActiveP_index].Equipment[Pindx]=copy.copy(G_Monster[ActiveM_index].Equipment[ActiveME_index])
                    G_Monster[ActiveM_index].Equipment[ActiveME_index]=Equipment()
                    G_Player[ActiveP_index].Money-=cost

                    Show_Story('\nYou bought '+G_Player[ActiveP_index].Equipment[Pindx].Name+' from '+G_Monster[ActiveM_index].Name+' for $'+str(int(cost))+'. Nice!','T_green')

                    #G_Player[ActiveP_index].AP_Down()
                    G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])
                    G_Monster[ActiveM_index].UpdateGUI(GUIs_monster[ActiveM_index])

                else:
                    messagebox.showinfo('Cannot Buy','You dont have enough Money to buy.\n$'+str(int(cost))+' Needed!')

    Stuff_After_Player_Action()

def Buy_M_Item(event):  #need No AP
    global ActiveP_index,ActiveM_index,ActiveMI_index

    if G_Player[ActiveP_index].ID==0:
        return

    #if G_Player[ActiveP_index].ActPT<=0: # individual Player out of AP, try someone else
    #    messagebox.showinfo('Fail','You run out of your AP!\nWait for next turn.')
    #    return

    # Check if Angry
    if G_Monster[ActiveM_index].Angry:
        messagebox.showinfo('Cannot Buy',G_Monster[ActiveM_index].Name+' is still Pissed and wont trade with you!')
    else:
        #check if selected
        if G_Monster[ActiveM_index].Item[ActiveMI_index].ID!=0:
            cost=G_Monster[ActiveM_index].Item[ActiveMI_index].Get_Cost()
            Pindx=G_Player[ActiveP_index].Item_EmptySlot()
            if Pindx<0:
                messagebox.showinfo('Cannot Buy','Your Item bag is full! Get rid of something before you buy.')
            else:
                if G_Player[ActiveP_index].Money>=cost:
                    G_Player[ActiveP_index].Item[Pindx]=copy.copy(G_Monster[ActiveM_index].Item[ActiveMI_index])
                    G_Monster[ActiveM_index].Item[ActiveMI_index]=Item()
                    G_Player[ActiveP_index].Money-=cost

                    Show_Story('\nYou bought '+G_Player[ActiveP_index].Item[Pindx].Name+' from '+G_Monster[ActiveM_index].Name+' for $'+str(int(cost))+'. Nice!','T_green')


                    #G_Player[ActiveP_index].AP_Down()
                    G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])
                    G_Monster[ActiveM_index].UpdateGUI(GUIs_monster[ActiveM_index])

                else:
                    messagebox.showinfo('Cannot Buy','You dont have enough Money to buy.\n$'+str(int(cost))+' Needed!')

    Stuff_After_Player_Action()

def Steal_M_Item(event):  # cost AP
    global ActiveP_index,ActiveM_index,ActiveMI_index

    if G_Player[ActiveP_index].ID==0:
        return
    
    if G_Player[ActiveP_index].ActPT<=0: # individual Player out of AP, try someone else
        messagebox.showinfo('Fail','You run out of your AP!\nWait for next turn.')
        return

    factor=1 #this factor will increase Monster perception if angry
    rate=G_Player[ActiveP_index].StealRate/100  # factor for your overall number

    # Check if Angry
    if G_Monster[ActiveM_index].Angry:
        factor=3      # 3 times Perception to do the roll  
    
    #check if selected
    if G_Monster[ActiveM_index].Item[ActiveMI_index].ID!=0:
        
        Pindx=G_Player[ActiveP_index].Item_EmptySlot()
        if Pindx<0:
            messagebox.showinfo('Cannot Steal','Your Item bag is full! Get rid of something before you do it.')
        else:

            G_Player[ActiveP_index].AP_Down()
            # do random check
            # same P+L to get 50/50 if not angry
            X=(G_Player[ActiveP_index].P*rate-G_Monster[ActiveM_index].P*factor+G_Player[ActiveP_index].L*rate-G_Monster[ActiveM_index].L)/(G_Monster[ActiveM_index].P*factor+G_Monster[ActiveM_index].L)
        
            Nx=np.random.normal(0,1)

            if X>Nx:

                G_Player[ActiveP_index].Item[Pindx]=copy.copy(G_Monster[ActiveM_index].Item[ActiveMI_index])
                G_Monster[ActiveM_index].Item[ActiveMI_index]=Item()
                
                G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])
                G_Monster[ActiveM_index].UpdateGUI(GUIs_monster[ActiveM_index])
                Show_Story('\nYou successfully stole '+G_Player[ActiveP_index].Item[Pindx].Name+'!','T_green')
            else:
                Show_Story('\nOops! You tried to steal '+G_Monster[ActiveM_index].Item[ActiveMI_index].Name +' but got Caught!\nNow '+G_Monster[ActiveM_index].Name+' is PISSED!!','T_red')
                G_Monster[ActiveM_index].Angry=True
                G_Player[ActiveP_index].UpdateGUI_Basic(GUIs_player[ActiveP_index])  #show AP loss

    Stuff_After_Player_Action()

def Steal_M_EquipInv(event):  # cost AP
    global ActiveP_index,ActiveM_index,ActiveME_index

    if G_Player[ActiveP_index].ID==0:
        return
    if G_Player[ActiveP_index].ActPT<=0: # individual Player out of AP, try someone else
        messagebox.showinfo('Fail','You run out of your AP!\nWait for next turn.')
        return

    factor=2 #this factor will increase Monster perception if angry, this is harder than stealing Item
    rate=G_Player[ActiveP_index].StealRate/100  # factor for your overall number

    # Check if Angry
    if G_Monster[ActiveM_index].Angry:
        factor=4      # 4 times Perception to do the roll  
    
    #check if selected
    if G_Monster[ActiveM_index].Equipment[ActiveME_index].ID!=0:
        
        Pindx=G_Player[ActiveP_index].Equipment_EmptySlot()
        if Pindx<0:
            messagebox.showinfo('Cannot Steal','Your Equipment bag is full! Get rid of something before you do it.')
        else:
            G_Player[ActiveP_index].AP_Down()
            # do random check
            # same P+L to get 50/50 if not angry
            X=(G_Player[ActiveP_index].P*rate-G_Monster[ActiveM_index].P*factor+G_Player[ActiveP_index].L*rate-G_Monster[ActiveM_index].L)/(G_Monster[ActiveM_index].P*factor+G_Monster[ActiveM_index].L)
            
            #X=-10000000
            Nx=np.random.normal(0,1)

            if X>Nx:

                G_Player[ActiveP_index].Equipment[Pindx]=copy.copy(G_Monster[ActiveM_index].Equipment[ActiveME_index])
                G_Monster[ActiveM_index].Equipment[ActiveME_index]=Equipment()
                
                G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])
                G_Monster[ActiveM_index].UpdateGUI(GUIs_monster[ActiveM_index])
                Show_Story('\nYou successfully stole '+G_Player[ActiveP_index].Equipment[Pindx].Name+'!','T_green')
            else:
                Show_Story('\nOops! You tried to steal '+G_Monster[ActiveM_index].Equipment[ActiveME_index].Name +' but got Caught!\nNow '+G_Monster[ActiveM_index].Name+' is PISSED!!','T_red')
                G_Monster[ActiveM_index].Angry=True
                G_Player[ActiveP_index].UpdateGUI_Basic(GUIs_player[ActiveP_index])  #show AP loss

    Stuff_After_Player_Action()

def Steal_M_Equiped(event):  # cost AP
    global ActiveP_index,ActiveM_index,ActiveMEq_index

    if G_Player[ActiveP_index].ID==0:
        return
    
    if G_Player[ActiveP_index].ActPT<=0: # individual Player out of AP, try someone else
        messagebox.showinfo('Fail','You run out of your AP!\nWait for next turn.')
        return

    factor=4 #this factor will increase Monster perception if angry, this is harder than stealing from inv
    rate=G_Player[ActiveP_index].StealRate/100  # factor for your overall number

    # Check if Angry
    if G_Monster[ActiveM_index].Angry:
        factor=8      # 8 times Perception to do the roll  
    
    #check if selected
    if G_Monster[ActiveM_index].Equiped[ActiveMEq_index].ID!=0:
        
        Pindx=G_Player[ActiveP_index].Equipment_EmptySlot()
        if Pindx<0:
            messagebox.showinfo('Cannot Steal','Your Equipment bag is full! Get rid of something before you do it.')
        else:
            G_Player[ActiveP_index].AP_Down()
            # do random check
            # same P+L to get 50/50 if not angry
            X=(G_Player[ActiveP_index].P*rate-G_Monster[ActiveM_index].P*factor+G_Player[ActiveP_index].L*rate-G_Monster[ActiveM_index].L)/(G_Monster[ActiveM_index].P*factor+G_Monster[ActiveM_index].L)
            
            #X=10000000
            Nx=np.random.normal(0,1)

            if X>Nx:

                G_Player[ActiveP_index].Equipment[Pindx]=copy.copy(G_Monster[ActiveM_index].Equiped[ActiveMEq_index])
                G_Monster[ActiveM_index].Equiped[ActiveMEq_index]=Equipment()  #need to take off...to be fixed later...
                
                G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])
                G_Monster[ActiveM_index].UpdateGUI(GUIs_monster[ActiveM_index])
                Show_Story('\nMaster thief! You somehow successfully strip off and stole '+G_Player[ActiveP_index].Equipment[Pindx].Name+'!','T_green')
            else:
                Show_Story('\nYou tried to steal '+G_Monster[ActiveM_index].Equiped[ActiveMEq_index].Name +' (seriously... its waring it!) but got Caught!\nNow '+G_Monster[ActiveM_index].Name+' is PISSED!!','T_red')
                G_Player[ActiveP_index].UpdateGUI_Basic(GUIs_player[ActiveP_index])  #show AP loss
                G_Monster[ActiveM_index].Angry=True

    Stuff_After_Player_Action()

def Learn_M_Magic(event):  # Cost AP, since Mag has a cap, let's make this relatively easy, if you can do Magic, you will have 75% chance to learn it, increase to 95% with your I P L
    global ActiveP_index,ActiveM_index,ActiveMM_index

    if G_Player[ActiveP_index].ID==0:
        return
    
    if G_Player[ActiveP_index].ActPT<=0: # individual Player out of AP, try someone else
        messagebox.showinfo('Fail','You run out of your AP!\nWait for next turn.')
        return
    
    if G_Monster[ActiveM_index].Angry:
        messagebox.showinfo('Cannot learn',G_Monster[ActiveM_index].Name+' is Pissed with you. Do NOT want to teach you anything!')
        return
    
    HasRoom=False
    indx=-1
    ii=0
    while not HasRoom and ii<=len(G_Player[ActiveP_index].Magic)-1:
        if G_Player[ActiveP_index].Magic[ii].ID==0:
            HasRoom=True
            indx=ii
        ii+=1
    
    if not HasRoom:
        messagebox.showinfo('Cannot learn','Cannot learn new magic if your Magic Slots are full. \n\nForget one Magic if needed.')
        return

    X=min(0.95,0.75+(G_Player[ActiveP_index].I+G_Player[ActiveP_index].L)/10000)  # after 2000+I and L, you max out at 95% chance
    Ux=np.random.random()

    if G_Monster[ActiveM_index].Magic[ActiveMM_index].Meet_Requirement(G_Player[ActiveP_index]):
        G_Player[ActiveP_index].AP_Down()
        if X>Ux:
            #learn it
            G_Player[ActiveP_index].Magic[indx]=copy.copy(G_Monster[ActiveM_index].Magic[ActiveMM_index])
            G_Player[ActiveP_index].Magic[indx].LV=1  #got to start from begining...

            G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])
            Show_Story('\nYou successfully learnt '+G_Player[ActiveP_index].Magic[indx].Name+'!\n','T_green')
        else:
            G_Player[ActiveP_index].UpdateGUI_Basic(GUIs_player[ActiveP_index])
            Show_Story('\nAlthough '+G_Monster[ActiveM_index].Name+' tried the best to teach you. Your attempt to learn the Magic failed!\nBad Luck!\n','T_blue')
    else:
        messagebox.showinfo('Cannot Learn','Your stats do not meet the Magic requirements!')
    
    Stuff_After_Player_Action()

def Drop_Inv_Item_Click(event):
    global ActiveDI_index

    if NbMD_Item.curselection()!=(): # get the index
        tempIdx=NbMD_Item.curselection()[0]
        ActiveDI_index=tempIdx
        if Drop_Item[tempIdx].ID!=0:  # see if Item is empty
            Drop_Item[tempIdx].LoadImg(CWD)
            
            temp_str=Drop_Item[tempIdx].Get_Description() #.GetInfo()
            # disply info to textbox
            S_Info_text.config(state='normal')
            S_Info_text.delete(1.0,tk.END)
            S_Info_text.insert(1.0,temp_str)
            S_Info_text.config(state='disabled')
            # get canv size
            S_Info_Canvs.update()
            W=S_Info_Canvs.winfo_width()
            H=S_Info_Canvs.winfo_height()
            tempImg=Drop_Item[tempIdx].Img.resize((W-4,H-4))
            Drop_Item[tempIdx].PImg=ImageTk.PhotoImage(tempImg)
            S_Info_Canvs.create_image(2,2,anchor=tk.NW,image=Drop_Item[tempIdx].PImg)

def Drop_Inv_Equip_Click(event):
    global ActiveDE_index

    if NbMD_Equip.curselection()!=(): # get the index
        tempIdx=NbMD_Equip.curselection()[0]
        ActiveDE_index=tempIdx
        if Drop_Equip[tempIdx].ID!=0:  # see if Item is empty
            Drop_Equip[tempIdx].LoadImg(CWD)
            
            temp_str=Drop_Equip[tempIdx].Get_Description() #.GetInfo()
            # disply info to textbox
            S_Info_text.config(state='normal')
            S_Info_text.delete(1.0,tk.END)
            S_Info_text.insert(1.0,temp_str)
            S_Info_text.config(state='disabled')
            # get canv size
            S_Info_Canvs.update()
            W=S_Info_Canvs.winfo_width()
            H=S_Info_Canvs.winfo_height()
            tempImg=Drop_Equip[tempIdx].Img.resize((W-4,H-4))
            Drop_Equip[tempIdx].PImg=ImageTk.PhotoImage(tempImg)
            S_Info_Canvs.create_image(2,2,anchor=tk.NW,image=Drop_Equip[tempIdx].PImg)

def Drop_Take_Item(event):
    global ActiveDI_index, G_Box_Item

    EpIndx=Box_Item_EmptySlot()
    if EpIndx<0:
        messagebox.showinfo('Cannot Take','Item Box is Full, get rid of some Item first!')
        return

    if Drop_Item[ActiveDI_index].ID!=0:
        G_Box_Item[EpIndx]=copy.copy(Drop_Item[ActiveDI_index])
        Drop_Item[ActiveDI_index]=Item()

        Box_updateGUI()
        Drop_updateGUI()

def Drop_Sell_Item(event):
    global ActiveDI_index, G_Money

    if Drop_Item[ActiveDI_index].ID!=0:
        cost=Drop_Item[ActiveDI_index].Get_Cost()        
        Drop_Item[ActiveDI_index]=Item()
        G_Money+=cost
        
        Box_updateGUI()
        Drop_updateGUI()

def Drop_Clear_Item(event):
    global G_Money,Drop_Item
    
    for ii in range(len(Drop_Item)):
        cost=Drop_Item[ii].Get_Cost()
        Drop_Item[ii]=Item()
        G_Money+=cost

    Drop_updateGUI()
    Box_updateGUI()

def Drop_TakeAll_Item():
    global G_Box_Item,G_Box_Item_In,G_Box_ItemN,Drop_Item_In

    if Drop_Item_In>=G_Box_ItemN-G_Box_Item_In:
        messagebox.showinfo('Warning','Cannot take ALL.\nYou dont have enough space in your Box.')
        return

    for ii in range(Drop_ItemN):
        if Drop_Item[ii].ID!=0:
            ItIndx=Box_Item_EmptySlot()
            G_Box_Item[ItIndx]=copy.copy(Drop_Item[ii])
            Drop_Item[ii]=Item()

    Box_updateGUI()
    Drop_updateGUI()

def Drop_Take_Equip(event):
    global ActiveDE_index, G_Box_Equip

    EpIndx=Box_Equip_EmptySlot()
    if EpIndx<0:
        messagebox.showinfo('Cannot Take','Equipment Box is Full, get rid of some Item first!')
        return

    if Drop_Equip[ActiveDE_index].ID!=0:
        G_Box_Equip[EpIndx]=copy.copy(Drop_Equip[ActiveDE_index])
        Drop_Equip[ActiveDE_index]=Equipment()

        Box_updateGUI()
        Drop_updateGUI()

def Drop_Sell_Equip(event):
    global ActiveDE_index, G_Money

    if Drop_Equip[ActiveDE_index].ID!=0:
        cost=Drop_Equip[ActiveDE_index].Get_Cost()        
        Drop_Equip[ActiveDE_index]=Equipment()
        G_Money+=cost
        
        Box_updateGUI()
        Drop_updateGUI()

def Drop_Clear_Equip(event):
    global G_Money,Drop_Equip
    
    for ii in range(len(Drop_Equip)):
        cost=Drop_Equip[ii].Get_Cost()
        Drop_Equip[ii]=Item()
        G_Money+=cost

    Drop_updateGUI()
    Box_updateGUI()

def Drop_TakeAll_Equip():
    global G_Box_Equip,G_Box_Equip_In,G_Box_EquipN,Drop_Equip_In

    if Drop_Equip_In>=G_Box_EquipN-G_Box_Equip_In:
        messagebox.showinfo('Warning','Cannot take ALL.\nYou dont have enough space in your Box.')
        return

    for ii in range(Drop_EquipN):
        if Drop_Equip[ii].ID!=0:
            EpIndx=Box_Equip_EmptySlot()
            G_Box_Equip[EpIndx]=copy.copy(Drop_Equip[ii])
            Drop_Equip[ii]=Equipment()

    Box_updateGUI()
    Drop_updateGUI()

#endregion

#region Game buttons binding

def PlayerRoll_Click():
    global G_Roll_N,CWD

    if G_Roll_N>0:
        G_Player[0]=Player()
        G_Player[0].ID=-1
        G_Player[0].Name='Dude'
        G_Player[0].Nickname='The ONE'
        G_Player[0].Pic='Player.png'
        G_Player[0].PlayerRoll(Dict_Equipment,Dict_Item,Dict_Magic)
        G_Player[0].LoadImg(CWD)
        G_Player[0].Rest_Full()
        G_Player[0].UpdateGUI(GUIs_player[0])
        G_Roll_N-=1
        S_Btn_Roll.config(text='ReRoll('+str(G_Roll_N)+')')
        if G_Roll_N==0:
            S_Btn_Roll.config(state='disabled')
            Show_Story('All Rolls Over. You have to "Start" game now...\n')

def Start_Click():
    global G_Zone,InBattle,MyTurn
    # disable roll button
    S_Btn_Roll.config(state='disabled')
    S_DropList.config(state='normal')
    S_Btn_Go.config(state='disabled')
    S_Btn_Retreat.config(state='disabled')

    #S_Btn_Boss.config(state='normal')
    # Load Monsters
    #Load_Monsters()
    Show_Story('Game starts!!\n\nYou are in "Safe Zone", where you can rest and adjust.\nSelect a zone and press "Go" to go there.\n')
    Show_Story('\nYou cannot switch Zones if you are in battle.\nYou will discover new Zones as you beat Bosses and advance.\nYou can go back to any earlier zones to grind and farm to get stronger.\nNow the story begins:\n=============ADV starts=======================\n')
    InBattle=False
    G_Zone=0
    MyTurn='Player'
    #S_Zone.config(text='Safe Zone')
    
    S_DropList.current(0)
    G_Player[0].Update()
    G_Player[0].Rest_Full()
    G_Player[0].Update()
    G_Player[0].UpdateGUI(GUIs_player[0])
    
    # disable itself
    S_Btn_Start.config(state='disabled')

def Go_Click():
    global G_Zone,InBattle,MyTurn
    
    #if '???' in S_DropList.get(): # note: it is not possible for go to be active when there is ??? in zone list name 
    #    messagebox.showinfo('Impossible','You must beat Area Boss to unlock this Zone!')
    #    temp=S_DropList.current()
    #    S_DropList.current(temp-1)  # get back to previous zone
    #    return
    
    temp=S_DropList.current()

    if temp==0:
        Retreat_Click()
        return

    if G_Zone!=temp:  #if changed zones
        if Zone_info.Completed[temp]:
            Show_Story('\nYou entered Zone: '+S_DropList.get()+'\nYou have beaten the Boss here Already.\n----------------------------\n')
        else:
            Show_Story('\nYou entered Zone: '+S_DropList.get()+'\nYour progress in this Zone is '+Zone_info.Str_progress(temp)+'\n----------------------------\n')
        #Zone_info.EmptyProgress(G_Zone)  Only Retreat empty progress, changing zone does not matter
    else:
        Show_Story('\nYou decided to keep moving forward in '+S_DropList.get()+'...\nNext group will be...?\n')
    
    G_Zone=temp  #update G_Zone
    MyTurn='Player'

    S_DropList.config(state='disabled')
    S_Btn_Boss.config(state='disabled')
    S_Btn_Retreat.config(state='disabled')
    S_Btn_Go.config(state='disabled')  #Nothing can be done until Monster wave is off
    
    root.update()
    time.sleep(1)   
    #root.after(1000,Load_Monsters)
    Load_Monsters()
    Update_Players()

def Retreat_Click():
    global G_Zone,InBattle,MyTurn,Zone_Kill
    
    Show_Story('\nYou retreated back to Safe Zone.\nYou are safe, but all progress in the Fighting Zones were lost.')
    temp=G_Zone

    G_Zone=0
    for ii in range(Zone_info.N):
        Zone_info.EmptyProgress(ii)
        

    for ii in range(3):
        G_Monster[ii]=Player()  #empty out all monsters
        if G_Player[ii].ID!=0:
            G_Player[ii].Rest_Full()
            G_Player[ii].Update()                
        InBattle=False
        MyTurn='Player'
    
    Update_Monsters()
    Update_Players()

    S_Btn_Boss.config(state='disabled',text='Boss '+Zone_info.Str_progress(temp))
    S_Btn_Retreat.config(state='disabled')
    S_Btn_Go.config(state='normal')
    S_DropList.current(0)

def Zone_Selected(event):
    global Zone_info,G_Zone

    temp=S_DropList.current()
    temp_str=S_DropList.get()
    #G_Zone=temp    The only thing that can change Zone is Go or Retreat
               
    if temp==0:  #
        S_Btn_Boss.config(state='disabled',text='No Boss')
        S_Btn_Go.config(state='disabled')
        #S_Btn_Retreat.config(state='disabled')
    else:
        if '???' in temp_str:
            S_Btn_Boss.config(state='disabled',text='Boss??')
            S_Btn_Go.config(state='disabled')
            S_Btn_Retreat.config(state='normal')
        else:
            
            if Zone_info.Completed[temp] or Zone_info.EnoughKill(temp):
                S_Btn_Boss.config(state='normal',text='Boss Ready')
                S_Btn_Go.config(state='normal')
                S_Btn_Retreat.config(state='normal')
            else:
                S_Btn_Boss.config(state='disabled',text='Boss '+Zone_info.Str_progress(temp))
                S_Btn_Go.config(state='normal')
                S_Btn_Retreat.config(state='normal')

def ZoneBoss_Click():
    global G_Zone,InBattle,MyTurn
    
    temp=S_DropList.current()

    #if temp==0:
    #    Retreat_Click()
    #    return

    if Zone_info.Completed[temp]:
        Show_Story('\nYou entered Boss Room in '+S_DropList.get()+'\nYou have done this before...\n----------------------------\n','T_blue')
    else:
        Show_Story('\nYou entered Boss Room in '+S_DropList.get()+'\n----------------------------\n','T_blue')
    #Zone_info.EmptyProgress(G_Zone)  Only Retreat empty progress, changing zone does not matter

    
    
    G_Zone=temp  #update G_Zone
    MyTurn='Player'

    S_DropList.config(state='disabled')
    S_Btn_Boss.config(state='disabled')
    S_Btn_Retreat.config(state='disabled')
    S_Btn_Go.config(state='disabled')  #Nothing can be done until Monster wave is off
    
    root.update()
    time.sleep(1)
    Show_Story('\nHere they come!!\n','T_red')   
    #root.after(1000,Load_Monsters)
    Load_Boss()

def Quit_Click():
    sure=messagebox.askyesno("Enough Fun?","You want to quite?\nAre you sure?")
    if sure:
        exit()

def About_Click():    
    messagebox.showinfo('About Random ADV II','This is a game for my kids I programmed during COVID19.\nThe key here is for them to be able to design their own levels.\nJust for fun! -- SP')

def SaveGame():
    # get save going
    global SD

    for ii in range(3):
        SD.PlayerData[ii]=G_Player[ii].ExtractData()
        SD.MonsterData[ii]=G_Monster[ii].ExtractData()
    
    
    SD.Zones=Zone_info
    #SD.Dict_Magic=Dict_Magic
    #SD.Dict_Monster=Dict_Monster
    #SD.Dict_E=Dict_Equipment
    #SD.Dict_I=Dict_Item

    for ii in range(G_Box_ItemN):
        SD.Box_Item[ii,0]=G_Box_Item[ii].ID
        SD.Box_Item[ii,1]=G_Box_Item[ii].LV

    for ii in range(G_Box_EquipN):
        SD.Box_Equip[ii,0]=G_Box_Equip[ii].ID
        SD.Box_Equip[ii,1]=G_Box_Equip[ii].LV

    for ii in range(Drop_ItemN):
        SD.Drop_Item[ii,0]=Drop_Item[ii].ID
        SD.Drop_Item[ii,1]=Drop_Item[ii].LV

    for ii in range(Drop_EquipN):
        SD.Drop_Equip[ii,0]=Drop_Equip[ii].ID
        SD.Drop_Equip[ii,1]=Drop_Equip[ii].LV

    SD.Current_Zone=G_Zone  #G_Zone=0 #safe zone
    SD.InBattle=InBattle  #InBattle=False
    SD.Turn=MyTurn  #MyTurn='Player' #or 'Monster'      
    SD.G_Money=G_Money   
    SD.G_PTequip=G_PTequip
    SD.G_PTmag=G_PTmag
    SD.G_Box_ItemN=G_Box_ItemN  
    SD.G_Box_Item_In=G_Box_Item_In
    SD.G_Box_EquipN=G_Box_EquipN
    SD.G_Box_Equip_In=G_Box_Equip_In 
    SD.Drop_ItemN=Drop_ItemN
    SD.Drop_Item_In=Drop_Item_In 
    SD.Drop_EquipN=Drop_EquipN
    SD.Drop_Equip_In=Drop_Equip_In

    SD.Btn_Boss=S_Btn_Boss['state']
    SD.Btn_Go=S_Btn_Go['state']
    SD.Btn_Roll=S_Btn_Roll['state']
    SD.Btn_Start=S_Btn_Start['state']
    SD.Btn_Retreat=S_Btn_Retreat['state']
    SD.Btn_PlayerAll=NbPA_Btn_Attack['state']

    SD.SpecialEvents=G_Events

    
    # ask for file name
    temp_f=filedialog.asksaveasfilename()
    if temp_f=='':
        return
    temp_fp=open(temp_f,'wb')
    CP.dump(SD,temp_fp)
    temp_fp.close()

def LoadGame():

    global SD,Dict_Item,Dict_Equipment,Dict_Magic,CWD
    global G_Box_ItemN,Zone_info,G_Box_EquipN,Drop_ItemN,Drop_EquipN
    global G_Box_Item,G_Box_Equip,Drop_Equip,Drop_Item,G_Events

    global G_Zone, InBattle, MyTurn, G_Money, G_PTequip, G_PTmag

    # load all into SD
    temp_f=filedialog.askopenfilename()
    if temp_f=='':
        return
    temp_fp=open(temp_f,'rb')
    SD=CP.load(temp_fp)
    temp_fp.close()

  

    # pass it to variables
    for ii in range(3):
        G_Player[ii]=Player()
        G_Player[ii].Import_from_Data(SD.PlayerData[ii],Dict_Item,Dict_Magic,Dict_Equipment,CWD)
        G_Monster[ii]=Player()
        G_Monster[ii].Import_from_Data(SD.MonsterData[ii],Dict_Item,Dict_Magic,Dict_Equipment,CWD)

  

    Zone_info=SD.Zones
    #Dict_Magic=SD.Dict_Magic
    #Dict_Monster=SD.Dict_Monster
    #Dict_Equipment=SD.Dict_E
    #Dict_Item=SD.Dict_I
    G_Zone=SD.Current_Zone
    InBattle=SD.InBattle
    MyTurn=SD.Turn    
    G_Money=SD.G_Money
    G_PTequip=SD.G_PTequip
    G_PTmag=SD.G_PTmag
    G_Box_ItemN=SD.G_Box_ItemN
    G_Box_Item_In=SD.G_Box_Item_In
    G_Box_EquipN=SD.G_Box_EquipN
    G_Box_Equip_In=SD.G_Box_Equip_In
    Drop_ItemN=SD.Drop_ItemN
    Drop_Item_In=SD.Drop_Item_In
    Drop_EquipN=SD.Drop_EquipN
    Drop_Equip_In=SD.Drop_Equip_In

    G_Events=SD.SpecialEvents
   

    for ii in range(G_Box_ItemN):
               
        G_Box_Item[ii]=copy.copy(Dict_Item[SD.Box_Item[ii,0]])
        G_Box_Item[ii].LV=SD.Box_Item[ii,1]
        

    for ii in range(G_Box_EquipN):
        G_Box_Equip[ii]=copy.copy(Dict_Equipment[SD.Box_Equip[ii,0]])
        G_Box_Equip[ii].LV=SD.Box_Equip[ii,1]

    for ii in range(Drop_ItemN):
        Drop_Item[ii]=copy.copy(Dict_Item[SD.Drop_Item[ii,0]])
        Drop_Item[ii].LV=SD.Drop_Item[ii,1]

    for ii in range(Drop_EquipN):
        Drop_Equip[ii]=copy.copy(Dict_Equipment[SD.Drop_Equip[ii,0]])
        Drop_Equip[ii].LV=SD.Drop_Equip[ii,1]

    #G_Box_Item=SD.Box_Item
    #G_Box_Equip=SD.Box_Equip
    #Drop_Item=SD.Drop_Item
    #Drop_Equip=SD.Drop_Equip


    S_Btn_Boss.config(state=SD.Btn_Boss)
    S_Btn_Go.config(state=SD.Btn_Go)
    S_Btn_Roll.config(state=SD.Btn_Roll)
    S_Btn_Start.config(state=SD.Btn_Start)
    S_Btn_Retreat.config(state=SD.Btn_Retreat)
    NbPA_Btn_Attack.config(state=SD.Btn_PlayerAll)
    NbPA_Btn_Defend.config(state=SD.Btn_PlayerAll)
    NbPA_Btn_Recruit.config(state=SD.Btn_PlayerAll)
    NbPA_Btn_Run.config(state=SD.Btn_PlayerAll)
    NbPA_Btn_item_Use.config(state=SD.Btn_PlayerAll)
    NbPA_Btn_mag_Use.config(state=SD.Btn_PlayerAll)
    NbPA_Btn_Talk.config(state=SD.Btn_PlayerAll)

    S_DropList.config(value=Zone_info.DisplayName())

    S_DropList.current(G_Zone)

    S_DropList.config(state='normal')

    Update_Players()
    Update_Monsters()
    Box_updateGUI()

#endregion

#endregion End of binding functions----------------

#region GUIs

#region Global GUI -----main window set up-----
root=tk.Tk()
root.title('Random Adventure II v1.0') 
root_H=680
root_W=1240
root.geometry(str(root_W)+'x'+str(root_H))
root.resizable(False,False)

default_font=font.nametofont("TkDefaultFont")
default_font.configure(size=12)


FrmP=tk.Frame(root,height=root_H,bg='cyan')  #width of frame will adjust based on contents
FrmS=tk.Frame(root,height=root_H,bg='light yellow')
FrmM=tk.Frame(root,height=root_H,bg='salmon')
FrmP.grid(row=0,column=0)
FrmS.grid(row=0,column=1)
FrmM.grid(row=0,column=2)

#endregion
#region GUI_FramP set up
#region -------FramP outside set up-------------
P_canv=np.array([tk.Canvas()]*3)
P_NameLV=np.array([tk.Label()]*3)
P_NickName=np.array([tk.Label()]*3)
P_HP=np.array([tk.Label()]*3)
P_HPbar=np.array([ttk.Progressbar()]*3)
P_MP=np.array([tk.Label()]*3)
P_MPbar=np.array([ttk.Progressbar()]*3)
P_AP=np.array([tk.Label()]*3)


for ii in range(3):
    P_NickName[ii]=tk.Label(FrmP,bg='green',text='Player-'+str(ii+1))
    #P_NickName[ii].grid(row=0,column=ii*3,columnspan=3)
    P_canv[ii]=tk.Canvas(FrmP,height=120,width=120,bg='blue')
    P_canv[ii].grid(row=1,column=ii,columnspan=1)
    P_NameLV[ii]=tk.Label(FrmP,bg='green',text='')
    P_NameLV[ii].grid(row=0,column=ii,columnspan=1)
    P_HP[ii]=tk.Label(FrmP,text='HP')
    P_HP[ii].grid(row=2,column=ii)
    P_HPbar[ii]=ttk.Progressbar(FrmP,orient=tk.HORIZONTAL, maximum=100, mode='determinate',length=120)
    P_HPbar[ii].grid(row=3,column=ii,columnspan=1)
    P_MP[ii]=tk.Label(FrmP,text='MP')
    P_MP[ii].grid(row=4,column=ii)
    P_MPbar[ii]=ttk.Progressbar(FrmP,orient=tk.HORIZONTAL, maximum=100, mode='determinate',length=120)
    P_MPbar[ii].grid(row=5,column=ii,columnspan=1)
    P_AP[ii]=tk.Label(FrmP,text='AP',bg='springgreen')
    P_AP[ii].grid(row=6,column=ii)

#region binding functions
P_canv[0].bind("<Button-1>",P1_Canv_Click)
P_canv[1].bind("<Button-1>",P2_Canv_Click)
P_canv[2].bind("<Button-1>",P3_Canv_Click)

#endregion

NbP=ttk.Notebook(FrmP)
NbP_Stats=tk.Frame(NbP)
NbP_Equip=tk.Frame(NbP)
NbP_Item=tk.Frame(NbP)
NbP_Magic=tk.Frame(NbP)
NbP_Box=tk.Frame(NbP)
NbP_Action=tk.Frame(NbP)
NbP.add(NbP_Stats,text='Stats')
NbP.add(NbP_Action,text='Action')
#NbP.add(NbP_Magic,text='Magic')
#NbP.add(NbP_Item,text='Item')
NbP.add(NbP_Equip,text='Equipment')
NbP.add(NbP_Box,text='Box')
NbP.grid(row=7,column=0,columnspan=3)
#endregion
#region --Page Action set up---
NbPA_Btn_Attack=tk.Button(NbP_Action,text='Attack',height=1,width=10)
NbPA_Btn_Talk=tk.Button(NbP_Action,text='Talk',height=1,width=8)
NbPA_Btn_Recruit=tk.Button(NbP_Action,text='Recruit',height=1,width=8)
NbPA_Btn_Run=tk.Button(NbP_Action,text='Run',height=1,width=8,command=RunAway)
NbPA_Btn_Defend=tk.Button(NbP_Action,text='Defend',height=1,width=8)
NbPA_Lab_act=tk.Label(NbP_Action,text='Action',height=1,width=14)
NbPA_Lab_item=tk.Label(NbP_Action,text='Item')
NbPA_Lab_mag=tk.Label(NbP_Action,text='Magic')
NbPA_Lab_tar=tk.Label(NbP_Action,text='Target')
NbPA_Lab_Mpt=tk.Label(NbP_Action,text='Magic PT=?')


Target_Action=tk.IntVar()
tk.Radiobutton(NbP_Action,text="P1",variable=Target_Action,value=0,bg='cyan').grid(row=8,column=0)
tk.Radiobutton(NbP_Action,text="P2",variable=Target_Action,value=1,bg='cyan').grid(row=8,column=1)
tk.Radiobutton(NbP_Action,text="P3",variable=Target_Action,value=2,bg='cyan').grid(row=8,column=2)
tk.Radiobutton(NbP_Action,text="M1",variable=Target_Action,value=3,bg='salmon').grid(row=8,column=3)
tk.Radiobutton(NbP_Action,text="M2",variable=Target_Action,value=4,bg='salmon').grid(row=8,column=4)
tk.Radiobutton(NbP_Action,text="M3",variable=Target_Action,value=5,bg='salmon').grid(row=8,column=5)
Target_Action.set(3)

NbPA_Btn_Attack.grid(row=6,column=4,columnspan=2)
NbPA_Btn_Talk.grid(row=2,column=4,columnspan=2)
NbPA_Btn_Recruit.grid(row=3,column=4,columnspan=2)
NbPA_Btn_Run.grid(row=5,column=4,columnspan=2)
NbPA_Btn_Defend.grid(row=4,column=4,columnspan=2)
NbPA_Lab_act.grid(row=1,column=4,columnspan=2)
NbPA_Lab_item.grid(row=0,column=0,columnspan=2)
NbPA_Lab_mag.grid(row=0,column=2,columnspan=2)
NbPA_Lab_tar.grid(row=7,column=0,columnspan=6)
NbPA_Lab_Mpt.grid(row=0,column=4,columnspan=2)

# items and mag
NbPA_Inv_item=tk.Listbox(NbP_Action,height=8,width=15)
NbPA_Inv_mag=tk.Listbox(NbP_Action,height=8,width=15)
NbPA_Inv_item.grid(row=1,column=0,columnspan=2,rowspan=4)
NbPA_Inv_mag.grid(row=1,column=2,columnspan=2,rowspan=4)

NbPA_Btn_item_Store=tk.Button(NbP_Action,text='Store',height=1,width=5,command=P_Item_Throw_Click)
NbPA_Btn_item_Sell=tk.Button(NbP_Action,text='Sell',height=1,width=5,command=P_Item_Sell_Click)
NbPA_Btn_item_Use=tk.Button(NbP_Action,text='Use on',height=1,width=10,command=P_Item_Use_Click)
NbPA_Btn_mag_Upgrade=tk.Button(NbP_Action,text='Upgrad',height=1,width=5,command=P_Magic_Upgrade_Click)
NbPA_Btn_mag_Forget=tk.Button(NbP_Action,text='Forget',height=1,width=5,command=P_Magic_Forget_Click)
NbPA_Btn_mag_Use=tk.Button(NbP_Action,text='Cast to',height=1,width=10,command=P_Magic_Use_Click)

NbPA_Btn_item_Store.grid(row=5,column=0,columnspan=1)
NbPA_Btn_item_Sell.grid(row=5,column=1,columnspan=1)
NbPA_Btn_item_Use.grid(row=6,column=0,columnspan=2)
NbPA_Btn_mag_Upgrade.grid(row=5,column=2,columnspan=1)
NbPA_Btn_mag_Forget.grid(row=5,column=3,columnspan=1)
NbPA_Btn_mag_Use.grid(row=6,column=2,columnspan=2)


#region binding function
#NbPA_Btn_Attack.bind("<ButtonRelease-1>",P_Attack_Click)
#
#NbPA_Btn_Recruit.bind("<ButtonRelease-1>",P_Recruit_Click)
#
#NbPA_Btn_Defend.bind("<ButtonRelease-1>",P_Defend_Click)
#
#NbPA_Btn_Talk.bind("<ButtonRelease-1>",P_Talk_Click)
NbPA_Btn_Attack.config(command=P_Attack_Click)

NbPA_Btn_Recruit.config(command=P_Recruit_Click)

NbPA_Btn_Defend.config(command=P_Defend_Click)

NbPA_Btn_Talk.config(command=P_Talk_Click)

#binding
NbPA_Inv_item.bind('<<ListboxSelect>>',P_Inv_Item_Click)
NbPA_Inv_mag.bind('<<ListboxSelect>>',P_Inv_Magic_Click)
#endregion

#endregion
#region --Page Stats set up---
NbPS_Labels=np.array([[tk.Label()]*5]*8)
NbPS_Btns=[tk.Button()]*7
for ii in range(8):
    for jj in range(5):
        NbPS_Labels[ii][jj]=tk.Label(NbP_Stats,text='')
        
        NbPS_Labels[ii][jj].grid(row=ii+2,column=jj+1)
temp=['S','P','E','C','I','A','L']
for ii in range(7):
    NbPS_Btns[ii]=tk.Button(NbP_Stats,text=temp[ii]+'+',width=2)
    NbPS_Btns[ii].grid(row=ii+1+2,column=0)
    NbPS_Btns[ii].bind("<Button-1>",lambda event, Indx=ii: P_Btn_StatPlus(event,Indx))

NbPS_Btn_Cminus=tk.Button(NbP_Stats,text='C-',width=2,bg='red',command=P_Btn_StatMinus)
NbPS_Btn_Cminus.grid(row=2,column=0)

NbPS_Labels[0][0].config(text='Stats',bg='cyan',width=6)
NbPS_Labels[0][1].config(text='Align',bg='cyan',width=6)
NbPS_Labels[0][2].config(text='Att',bg='cyan',width=6)
NbPS_Labels[0][3].config(text='Def',bg='cyan',width=6)
NbPS_Labels[0][4].config(text='Prof',bg='cyan',width=6)
NbPS_Labels[1][1].config(text='Physic',bg='cyan',width=6)
NbPS_Labels[2][1].config(text='Cold',bg='cyan',width=6)
NbPS_Labels[3][1].config(text='Fire',bg='cyan',width=6)
NbPS_Labels[4][1].config(text='Lightn',bg='cyan',width=6)
NbPS_Labels[5][1].config(text='Poison',bg='cyan',width=6)
NbPS_Labels[6][1].config(text='Holy',bg='cyan',width=6)
NbPS_Labels[7][1].config(text='Dark',bg='cyan',width=6)

NbPS_LVexp=tk.Label(NbP_Stats,text='LV1(0/500)')
NbPS_StatPT=tk.Label(NbP_Stats,text='SP:0')
NbPS_Money=tk.Label(NbP_Stats,text='$0')
NbPS_HPreg=tk.Label(NbP_Stats,text='HP-Reg:')
NbPS_MPreg=tk.Label(NbP_Stats,text='MP-Reg:')
NbPS_Drop=tk.Label(NbP_Stats,text='Dp:100%')

NbPS_LVexp.grid(row=0,column=1,columnspan=2,sticky='W')
NbPS_StatPT.grid(row=0,column=3,sticky='W')
NbPS_Money.grid(row=0,column=4,columnspan=2)
NbPS_HPreg.grid(row=1,column=1,sticky='W',columnspan=2)
NbPS_MPreg.grid(row=1,column=3,sticky='W',columnspan=2)
NbPS_Drop.grid(row=1,column=5)

#endregion
#region --Page Equip set up---
NbPE_Canvs=[tk.Canvas()]*15
NbPE_Info0=tk.Label(NbP_Equip,text='Equipment')
#NbPE_Info=tk.Text(NbP_Equip,height=8,width=10,wrap='word')
NbPE_Inv0=tk.Label(NbP_Equip,text='Inventory(0/10)')
NbPE_Inv=tk.Listbox(NbP_Equip,height=6,width=15)
NbPE_Btn_Equip=tk.Button(NbP_Equip,text='Equip',width=7,height=1)
NbPE_Btn_Takeoff=tk.Button(NbP_Equip,text='Takeoff',width=7,height=1)
NbPE_Btn_Sell=tk.Button(NbP_Equip,text='Sell',width=7,height=1)
NbPE_Btn_Throw=tk.Button(NbP_Equip,text='Store',width=7,height=1)
NbPE_Btn_Upgrade=tk.Button(NbP_Equip,text='Upgrade',width=7,height=1)
NbPE_PTequip=tk.Label(NbP_Equip,text='PT=0')
#NbPE_Selected=tk.Canvas(NbP_Equip,height=40,width=40,bg='blue',highlightthickness=1,highlightbackground='red')
NbPE_Info0.grid(row=0,column=0,columnspan=2)
#NbPE_Info.grid(row=1,column=3,rowspan=6,columnspan=2)
NbPE_Btn_Upgrade.grid(row=1,column=4)
NbPE_PTequip.grid(row=0,column=4,columnspan=1)
NbPE_Inv0.grid(row=0,column=5,columnspan=1)
#NbPE_Selected.grid(row=1,column=5,rowspan=2,columnspan=2)
NbPE_Inv.grid(row=1,column=5,rowspan=3,columnspan=1)
NbPE_Btn_Equip.grid(row=4,column=5)
NbPE_Btn_Takeoff.grid(row=4,column=4)
NbPE_Btn_Sell.grid(row=3,column=4)
NbPE_Btn_Throw.grid(row=2,column=4)
temp=[[0,2,1,1,1],
    [1,2,1,1,1],
    [2,1,1,1,1],
    [2,2,1,1,1],
    [3,2,1,1,1],
    [0,3,2,1,1],
    [2,3,1,1,1],
    [0,1,1,1,1],
    [1,1,1,1,1],
    [0,0,1,1,1],
    [1,0,1,1,1],
    [2,0,1,1,1],
    [3,0,1,1,1],
    [3,3,1,1,1],
    [3,1,1,1,1]]

for ii in range(15):
    NbPE_Canvs[ii]=tk.Canvas(NbP_Equip,height=40*temp[ii][2],width=40*temp[ii][4],bg='blue',highlightthickness=1,highlightbackground='red')
    NbPE_Canvs[ii].grid(row=temp[ii][0]+1,column=temp[ii][1],rowspan=temp[ii][2],columnspan=temp[ii][3])
    NbPE_Canvs[ii].bind("<Button-1>",lambda event, Indx=ii: P_Cav_Equip_Click(event,Indx))
#region binding
NbPE_Inv.bind('<<ListboxSelect>>',P_Inv_Equip_Click)
NbPE_Btn_Upgrade.bind("<ButtonRelease-1>",P_Btn_EqUpgrade_Click)
NbPE_Btn_Takeoff.bind("<ButtonRelease-1>",P_Btn_EqTakeoff_Click)
NbPE_Btn_Equip.bind("<ButtonRelease-1>",P_Btn_EqPuton_Click)
NbPE_Btn_Sell.bind("<ButtonRelease-1>",P_Btn_EqSell_Click)
NbPE_Btn_Throw.bind("<ButtonRelease-1>",P_Btn_EqThrow_Click)
#endregion

#endregion
#region --Page Item set up---
    #NbPI_Inv0=tk.Label(NbP_Item,text='Inventory')
    #NbPI_Inv=tk.Listbox(NbP_Item,height=8,width=14)
    #NbPI_Info0=tk.Label(NbP_Item,text='Information')
    #NbPI_Info=tk.Text(NbP_Item,height=6,width=25,wrap='word')
    #NbPI_Btn_Use=tk.Button(NbP_Item,text='Use Item On:')
    #NbPI_Btn_Sell=tk.Button(NbP_Item,text='Sell')
    ##NbPI_Btn_Buy=tk.Button(NbP_Item,text='Buy')
    #NbPI_Btn_Throw=tk.Button(NbP_Item,text='Throw')
    #NbPI_Money=tk.Label(NbP_Item,text='$200')
    #NbPI_Selected=tk.Canvas(NbP_Item,width=40,height=40,bg='blue',highlightthickness=1,highlightbackground='red')
    #Target_Item=tk.IntVar()
    #tk.Radiobutton(NbP_Item,text="P1",variable=Target_Item,value=0).grid(row=1,column=2)
    #tk.Radiobutton(NbP_Item,text="P2",variable=Target_Item,value=1).grid(row=1,column=3)
    #tk.Radiobutton(NbP_Item,text="P3",variable=Target_Item,value=2).grid(row=1,column=4)
    #tk.Radiobutton(NbP_Item,text="M1",variable=Target_Item,value=3).grid(row=2,column=2)
    #tk.Radiobutton(NbP_Item,text="M2",variable=Target_Item,value=4).grid(row=2,column=3)
    #tk.Radiobutton(NbP_Item,text="M3",variable=Target_Item,value=5).grid(row=2,column=4)
    #Target_Item.set(3)
    #NbPI_Selected.grid(row=1,column=1,rowspan=2)
    #NbPI_Inv0.grid(row=0,column=0)
    #NbPI_Inv.grid(row=1,column=0,rowspan=3)
    ##NbPI_Info0.grid(row=0,column=1,columnspan=2)
    #NbPI_Money.grid(row=0,column=1,columnspan=1)
    #NbPI_Info.grid(row=3,column=1,columnspan=4,rowspan=3)
    #NbPI_Btn_Use.grid(row=0,column=2,columnspan=3)
    ##NbPI_Btn_Buy.grid(row=2,column=2)
    #NbPI_Btn_Sell.grid(row=4,column=0)
    #NbPI_Btn_Throw.grid(row=5,column=0)
    #
    ##region binding
    #NbPI_Inv.bind('<<ListboxSelect>>',P_Inv_Item_Click)
    #NbPI_Btn_Throw.bind("<ButtonRelease-1>",P_Item_Throw_Click)
    #NbPI_Btn_Sell.bind("<ButtonRelease-1>",P_Item_Sell_Click)
    #NbPI_Btn_Use.bind("<ButtonRelease-1>",P_Item_Use_Click)



#endregion
#region --Page Magic set up---
    #NbPM_Inv0=tk.Label(NbP_Magic,text='Magic List')
    #NbPM_Inv=tk.Listbox(NbP_Magic,height=8,width=14)
    ##NbPM_Info0=tk.Label(NbP_Magic,text='Information')
    #NbPM_Info=tk.Text(NbP_Magic,height=6,width=25,wrap='word')
    #NbPM_Btn_Use=tk.Button(NbP_Magic,text='Use')
    #NbPM_Btn_Upgrade=tk.Button(NbP_Magic,text='Upgrade')
    ##NbPM_Btn_Learn=tk.Button(NbP_Magic,text='Learn')
    #NbPM_Btn_Forget=tk.Button(NbP_Magic,text='Forget')
    #NbPM_Point=tk.Label(NbP_Magic,text='PM=3')
    #NbPM_Selected=tk.Canvas(NbP_Magic,width=40,height=40,bg='blue',highlightthickness=1,highlightbackground='red')
    #
    #Target_Magic=tk.IntVar()
    #tk.Radiobutton(NbP_Magic,text="P1",variable=Target_Magic,value=0).grid(row=1,column=2)
    #tk.Radiobutton(NbP_Magic,text="P2",variable=Target_Magic,value=1).grid(row=1,column=3)
    #tk.Radiobutton(NbP_Magic,text="P3",variable=Target_Magic,value=2).grid(row=1,column=4)
    #tk.Radiobutton(NbP_Magic,text="M1",variable=Target_Magic,value=3).grid(row=2,column=2)
    #tk.Radiobutton(NbP_Magic,text="M2",variable=Target_Magic,value=4).grid(row=2,column=3)
    #tk.Radiobutton(NbP_Magic,text="M3",variable=Target_Magic,value=5).grid(row=2,column=4)
    #Target_Magic.set(3)
    #NbPM_Selected.grid(row=1,column=1,rowspan=2)
    #NbPM_Inv0.grid(row=0,column=0)
    #NbPM_Inv.grid(row=1,column=0,rowspan=3)
    ##NbPM_Info0.grid(row=0,column=1,columnspan=2)
    #NbPM_Point.grid(row=0,column=1,columnspan=1)
    #NbPM_Info.grid(row=3,column=1,columnspan=4,rowspan=3)
    #NbPM_Btn_Use.grid(row=0,column=2,columnspan=3)
    #NbPM_Btn_Upgrade.grid(row=4,column=0)
    ##NbPM_Btn_Learn.grid(row=2,column=3)
    #NbPM_Btn_Forget.grid(row=5,column=0)
    #
    ##region binding
    #NbPM_Inv.bind('<<ListboxSelect>>',P_Inv_Magic_Click)
    #NbPM_Btn_Forget.bind("<ButtonRelease-1>",P_Magic_Forget_Click)
    #NbPM_Btn_Upgrade.bind("<ButtonRelease-1>",P_Magic_Upgrade_Click)
    #NbPM_Btn_Use.bind("<ButtonRelease-1>",P_Magic_Use_Click)
#endregion
#region --Page Box set up---

Target_Box=tk.IntVar()
tk.Radiobutton(NbP_Box,text="Money",variable=Target_Box,value=0,width=8).grid(row=1,column=4)
tk.Radiobutton(NbP_Box,text="Magic PT",variable=Target_Box,value=1,width=8).grid(row=3,column=4)
tk.Radiobutton(NbP_Box,text="Equip PT",variable=Target_Box,value=2,width=8).grid(row=5,column=4)
Target_Box.set(0)

NbPB_Lab_Money=tk.Label(NbP_Box,text='$0')
NbPB_Lab_PTmag=tk.Label(NbP_Box,text='0 PT')
NbPB_Lab_PTequip=tk.Label(NbP_Box,text='0 PT')

NbPB_Lab_Money.grid(row=2,column=4)
NbPB_Lab_PTmag.grid(row=4,column=4)
NbPB_Lab_PTequip.grid(row=6,column=4)

NbPB_Btn_Gather=tk.Button(NbP_Box,text='Gather All',command=B_Gather,width=8)
NbPB_Btn_Gather.grid(row=7,column=4)
NbPB_Lab_bank=tk.Label(NbP_Box,text='Bank')
NbPB_Lab_bank.grid(row=0,column=4)

NbPB_Ent_amount=tk.Entry(NbP_Box,width=12)
NbPB_Ent_amount.grid(row=8,column=4)
NbPB_Btn_Take=tk.Button(NbP_Box,text='Withdraw',command=B_Take,width=8)
NbPB_Btn_Take.grid(row=9,column=4)


NbPB_Item0=tk.Label(NbP_Box,text='Item 0/50')
NbPB_Item=tk.Listbox(NbP_Box,width=15,height=11)
NbPB_Btn_ItemSell=tk.Button(NbP_Box,text='Sell',command=B_Item_Sell_Click,width=5)
NbPB_Btn_ItemTake=tk.Button(NbP_Box,text='Take',command=B_Item_Take_Click,width=5)

NbPB_Item0.grid(row=0,column=0,columnspan=2)
NbPB_Item.grid(row=1,column=0,rowspan=8,columnspan=2)
NbPB_Btn_ItemSell.grid(row=9,column=0)
NbPB_Btn_ItemTake.grid(row=9,column=1)

NbPB_Equip0=tk.Label(NbP_Box,text='Equip 0/50')
NbPB_Equip=tk.Listbox(NbP_Box,width=15,height=11)
NbPB_Btn_EquipSell=tk.Button(NbP_Box,text='Sell',command=B_Equip_Sell_Click,width=5)
NbPB_Btn_EquipTake=tk.Button(NbP_Box,text='Take',command=B_Equip_Take_Click,width=5)
NbPB_Equip0.grid(row=0,column=2,columnspan=2)
NbPB_Equip.grid(row=1,column=2,rowspan=8,columnspan=2)
NbPB_Btn_EquipSell.grid(row=9,column=2)
NbPB_Btn_EquipTake.grid(row=9,column=3)
#NbPB_Info0=tk.Label(NbP_Box,text='Information')
#NbPB_Info=tk.Text(NbP_Box,height=10,width=15,wrap='word')
#NbPB_Selected=tk.Canvas(NbP_Box,width=45,height=45,bg='blue',highlightthickness=1,highlightbackground='red')
##NbPB_Info0.grid(row=0,column=3)
#NbPB_Info.grid(row=2,column=2,rowspan=3,columnspan=2)
#NbPB_Selected.grid(row=0,column=2,rowspan=2)

NbPB_Item.bind('<<ListboxSelect>>',B_Inv_Item_Click)
NbPB_Equip.bind('<<ListboxSelect>>',B_Inv_Equip_Click)

#NbPB_Btn_ItemSell.bind("<ButtonRelease-1>",B_Item_Sell_Click)
#NbPB_Btn_EquipSell.bind("<ButtonRelease-1>",B_Equip_Sell_Click)
#
#NbPB_Btn_ItemTake.bind("<ButtonRelease-1>",B_Item_Take_Click)
#NbPB_Btn_EquipTake.bind("<ButtonRelease-1>",B_Equip_Take_Click)
#endregion

#endregion End of Frame_Player

#region GUI_Frame Story set up
S_Btn_Roll=tk.Button(FrmS,text='ReRoll(7)',height=1,width=10,command=PlayerRoll_Click)
S_Btn_Start=tk.Button(FrmS,text='Start',height=1,width=10,command=Start_Click)
S_Btn_Save=tk.Button(FrmS,text='Save',height=1,width=10,command=SaveGame)
S_Btn_Load=tk.Button(FrmS,text='Load',height=1,width=10,command=LoadGame)
S_Btn_Quit=tk.Button(FrmS,text='Quit',command=Quit_Click,height=1,width=10)
S_Btn_About=tk.Button(FrmS,text='About',height=1,width=10,command=About_Click)
S_Canvs=tk.Canvas(FrmS,height=110,width=130,bg='blue',highlightthickness=1,highlightbackground='red')

S_Canvs.grid(row=0,column=3,rowspan=4,columnspan=1)
S_Btn_Roll.grid(row=0,column=0)
S_Btn_Start.grid(row=0,column=1)
S_Btn_Quit.grid(row=0,column=2)
S_Btn_Load.grid(row=1,column=1)
S_Btn_Save.grid(row=1,column=0)
S_Btn_About.grid(row=1,column=2)



S_DropList=ttk.Combobox(FrmS,value=Zone_info.DisplayName())
S_DropList.current(0)
S_DropList.config(state='disabled',height=1,width=25)
S_Btn_Go=tk.Button(FrmS,text='Go=>',state='disabled',height=1,width=10,command=Go_Click)
S_Btn_Retreat=tk.Button(FrmS,text='Retreat',state='disabled',height=1,width=10,command=Retreat_Click)
S_Btn_Boss=tk.Button(FrmS,text='BOSS',state='disabled',height=1,width=10,command=ZoneBoss_Click)
S_Drop_lab=tk.Label(FrmS,text='Zone:')

S_Drop_lab.grid(row=2,column=0,columnspan=1)
S_DropList.grid(row=3,column=0,columnspan=2)
S_Btn_Go.grid(row=3,column=2)
S_Btn_Boss.grid(row=2,column=2)
S_Btn_Retreat.grid(row=2,column=1)

#S_DropList=ttk.Combobox(FrmS,value=['Safe Zone','Zone 1: Sewer','Zone 2: ???(Beat Boss to Unlock)'])


S_Story=tk.Text(FrmS,width=50,height=20,wrap='word')
S_Story.grid(row=4,column=0,columnspan=4)
#tags
S_Story.tag_configure('T_red',foreground='red')
S_Story.tag_configure('T_blue',foreground='blue')
S_Story.tag_configure('T_black',foreground='black')
S_Story.tag_configure('T_green',foreground='green')

# information section

S_Info_title=tk.Label(FrmS,text='Detailed Information')
S_Info_Canvs=tk.Canvas(FrmS,height=120,width=120,bg='blue',highlightthickness=1,highlightbackground='red')
S_Info_text=tk.Text(FrmS,width=36,height=7,wrap='word')
S_Footnote=tk.Label(FrmS,text='All rights reserved 2020')

#S_Milestone0=tk.Label(FrmS,text='Milestones')
#S_Milestone=tk.Text(FrmS,width=20,height=6,wrap='word')

S_Info_title.grid(row=5,column=0,columnspan=4)
S_Info_Canvs.grid(row=6,column=3,columnspan=1)
S_Info_text.grid(row=6,column=0,columnspan=3)
S_Footnote.grid(row=7,column=0,columnspan=4)


#binding zone

S_DropList.bind("<<ComboboxSelected>>",Zone_Selected)
#S_Btn_Roll.bind("<ButtonRelease-1>",PlayerRoll_Click)

#S_Btn_Start.bind("<ButtonRelease-1>",Start_Click)


#S_Btn_Go.bind("<ButtonRelease-1>",Go_Click)
#endregion End of Frame story set up

#region GUI_FramM set up
#region FramM outside set up
M_canv=[tk.Canvas()]*3
M_NameLV=[tk.Label()]*3
M_NickName=[tk.Label()]*3
M_HP=[tk.Label()]*3
M_HPbar=[ttk.Progressbar()]*3
M_MP=[tk.Label()]*3
M_MPbar=[ttk.Progressbar()]*3
M_AP=[tk.Label()]*3


for ii in range(3):
    M_NickName[ii]=tk.Label(FrmM,bg='green',text='Nickname')
    #M_NickName[ii].grid(row=0,column=ii*3,columnspan=3)
    M_canv[ii]=tk.Canvas(FrmM,height=120,width=120,bg='blue')
    M_canv[ii].grid(row=1,column=ii,columnspan=1)
    M_NameLV[ii]=tk.Label(FrmM,bg='green',text='')
    M_NameLV[ii].grid(row=0,column=ii,columnspan=1)
    M_HP[ii]=tk.Label(FrmM,text='HP')
    M_HP[ii].grid(row=2,column=ii)
    M_HPbar[ii]=ttk.Progressbar(FrmM,orient=tk.HORIZONTAL, maximum=100, mode='determinate',length=120)
    M_HPbar[ii].grid(row=3,column=ii,columnspan=1)
    M_MP[ii]=tk.Label(FrmM,text='MP')
    M_MP[ii].grid(row=4,column=ii)
    M_MPbar[ii]=ttk.Progressbar(FrmM,orient=tk.HORIZONTAL, maximum=100, mode='determinate',length=120)
    M_MPbar[ii].grid(row=5,column=ii,columnspan=1)
    M_AP[ii]=tk.Label(FrmM,text='AP',bg='springgreen')
    M_AP[ii].grid(row=6,column=ii)
    

#region binding
M_canv[0].bind("<Button-1>",M1_Canv_Click)
M_canv[1].bind("<Button-1>",M2_Canv_Click)
M_canv[2].bind("<Button-1>",M3_Canv_Click)
#endregion

NbM=ttk.Notebook(FrmM)
NbM_Stats=tk.Frame(NbM)
NbM_Equip=tk.Frame(NbM)
NbM_Item=tk.Frame(NbM)
NbM_Magic=tk.Frame(NbM)
NbM_Drop=tk.Frame(NbM)
NbM.add(NbM_Stats,text='Stats')
NbM.add(NbM_Equip,text='Equipment')
NbM.add(NbM_Item,text='Item/Magic')
#NbM.add(NbM_Magic,text='Magic')
NbM.add(NbM_Drop,text='Drop')
NbM.grid(row=7,column=0,columnspan=3)
#endregion
#region --Page Stats set up---
NbMS_Labels=np.array([[tk.Label()]*5]*9)
NbMS_Btns=[tk.Button()]*7
for ii in range(8):
    for jj in range(5):
        NbMS_Labels[ii][jj]=tk.Label(NbM_Stats,text='0')
        NbMS_Labels[ii][jj].grid(row=ii+2,column=jj+1)
temp=['S','P','E','C','I','A','L']
for ii in range(7):
    NbMS_Btns[ii]=tk.Button(NbM_Stats,text=temp[ii]+':',state='disabled',width=2)
    NbMS_Btns[ii].grid(row=ii+1+2,column=0)

NbMS_Labels[0][0].config(text='Stats',bg='cyan',width=6)
NbMS_Labels[0][1].config(text='Align',bg='cyan',width=6)
NbMS_Labels[0][2].config(text='Att',bg='cyan',width=6)
NbMS_Labels[0][3].config(text='Def',bg='cyan',width=6)
NbMS_Labels[0][4].config(text='Prof',bg='cyan',width=6)
NbMS_Labels[1][1].config(text='Physic',bg='cyan',width=6)
NbMS_Labels[2][1].config(text='Cold',bg='cyan',width=6)
NbMS_Labels[3][1].config(text='Fire',bg='cyan',width=6)
NbMS_Labels[4][1].config(text='Lightn',bg='cyan',width=6)
NbMS_Labels[5][1].config(text='Poison',bg='cyan',width=6)
NbMS_Labels[6][1].config(text='Holy',bg='cyan',width=6)
NbMS_Labels[7][1].config(text='Dark',bg='cyan',width=6)

NbMS_LVexp=tk.Label(NbM_Stats,text='LV1(254)')
NbMS_StatPT=tk.Label(NbM_Stats,text='SP:0')
NbMS_Money=tk.Label(NbM_Stats,text='$0')
NbMS_HPreg=tk.Label(NbM_Stats,text='HP-Reg:')
NbMS_MPreg=tk.Label(NbM_Stats,text='MP-Reg:')
NbMS_Drop=tk.Label(NbM_Stats,text='Dp:25%')

NbMS_LVexp.grid(row=0,column=1,columnspan=2,sticky='W')
NbMS_StatPT.grid(row=0,column=3,sticky='W')
NbMS_Money.grid(row=0,column=4,columnspan=2)
NbMS_HPreg.grid(row=1,column=1,sticky='W',columnspan=2)
NbMS_MPreg.grid(row=1,column=3,sticky='W',columnspan=2)
NbMS_Drop.grid(row=1,column=5)
#endregion
#region --Page Equip set up---
NbME_Canvs=[tk.Canvas()]*15
NbME_Info0=tk.Label(NbM_Equip,text='Equipment')
NbME_Info0.grid(row=0,column=0,columnspan=2)

#NbME_Info=tk.Text(NbM_Equip,height=12,width=12,wrap='word')
NbME_Inv0=tk.Label(NbM_Equip,text='Inventory')
NbME_Inv0.grid(row=0,column=4,columnspan=1)


NbME_Inv=tk.Listbox(NbM_Equip,height=6,width=18)
NbME_Inv.grid(row=1,column=4,rowspan=3,columnspan=1)

#NbME_Selected=tk.Canvas(NbM_Equip,height=60,width=60,bg='blue',highlightthickness=1,highlightbackground='red')
NbME_Btn_StealI=tk.Button(NbM_Equip,text='Steal from Inv',width=10)
NbME_Btn_BuyI=tk.Button(NbM_Equip,text='Buy from Inv',width=10)
NbME_Btn_StealB=tk.Button(NbM_Equip,text='Steal from body',width=12)

NbME_Point=tk.Label(NbM_Equip,text='PE=5')  # hide by not pack, need by GUI update, but no need to show in game
NbME_Point.grid(row=0,column=2,columnspan=2)

NbME_Btn_BuyI.grid(row=4,column=4)
NbME_Btn_StealB.grid(row=5,column=0,columnspan=4)
NbME_Btn_StealI.grid(row=5,column=4)

temp=[[0,2,1,1,1],
    [1,2,1,1,1],
    [2,1,1,1,1],
    [2,2,1,1,1],
    [3,2,1,1,1],
    [0,3,2,1,1],
    [2,3,1,1,1],
    [0,1,1,1,1],
    [1,1,1,1,1],
    [0,0,1,1,1],
    [1,0,1,1,1],
    [2,0,1,1,1],
    [3,0,1,1,1],
    [3,3,1,1,1],
    [3,1,1,1,1]]

for ii in range(15):
    NbME_Canvs[ii]=tk.Canvas(NbM_Equip,height=40*temp[ii][2],width=40*temp[ii][4],bg='blue',highlightthickness=1,highlightbackground='red')
    NbME_Canvs[ii].grid(row=temp[ii][0]+1,column=temp[ii][1],rowspan=temp[ii][2],columnspan=temp[ii][3])
    NbME_Canvs[ii].bind("<Button-1>",lambda event, Indx=ii: M_Cav_Equip_Click(event,Indx))

#region binding
NbME_Inv.bind('<<ListboxSelect>>',M_Inv_Equip_Click)
NbME_Btn_BuyI.bind("<ButtonRelease-1>",Buy_M_Equip)
NbME_Btn_StealI.bind("<ButtonRelease-1>",Steal_M_EquipInv)
NbME_Btn_StealB.bind("<ButtonRelease-1>",Steal_M_Equiped)
#endregion

#endregion
#region --Page Item/mag set up---
NbMI_Inv0=tk.Label(NbM_Item,text='Inventory')
NbMI_Inv=tk.Listbox(NbM_Item,height=10,width=20)

NbMI_Btn_Steal=tk.Button(NbM_Item,text='Steal Item',width=8)
NbMI_Btn_Buy=tk.Button(NbM_Item,text='Buy Item',width=8)

NbMI_Inv0.grid(row=0,column=0,columnspan=2)
NbMI_Inv.grid(row=1,column=0,columnspan=2)

NbMI_Btn_Steal.grid(row=2,column=0)
NbMI_Btn_Buy.grid(row=2,column=1)


NbMI_Inv.bind('<<ListboxSelect>>',M_Inv_Item_Click)
NbMI_Btn_Buy.bind("<ButtonRelease-1>",Buy_M_Item)
NbMI_Btn_Steal.bind("<ButtonRelease-1>",Steal_M_Item)
# magic part
NbMM_Inv0=tk.Label(NbM_Item,text='Magic List')
NbMM_Inv=tk.Listbox(NbM_Item,height=10,width=20)

NbMM_Point=tk.Label(NbM_Item,text='PM=3')
NbMM_Btn_Learn=tk.Button(NbM_Item,text='Learn',width=8)

NbMM_Inv0.grid(row=0,column=2,columnspan=2)
NbMM_Inv.grid(row=1,column=2,columnspan=2)

NbMM_Point.grid(row=2,column=2,columnspan=1)

NbMM_Btn_Learn.grid(row=2,column=3)

NbMM_Inv.bind('<<ListboxSelect>>',M_Inv_Magic_Click)
NbMM_Btn_Learn.bind("<ButtonRelease-1>",Learn_M_Magic)



#endregion
#region --Page Magic set up---

    #NbMM_Info0=tk.Label(NbM_Magic,text='Information')
    #NbMM_Info=tk.Text(NbM_Magic,height=8,width=15,wrap='word')
    ##NbMM_Btn_Use=tk.Button(NbM_Magic,text='Use')
    ##NbMM_Btn_Upgrade=tk.Button(NbM_Magic,text='Upgrade')
    #NbMM_Btn_Learn=tk.Button(NbM_Magic,text='Learn')
    ##NbMM_Btn_Forget=tk.Button(NbM_Magic,text='Forget')
    #NbMM_Point=tk.Label(NbM_Magic,text='PM=3')
    #NbMM_Selected=tk.Canvas(NbM_Magic,width=60,height=60,bg='blue',highlightthickness=1,highlightbackground='red')
    #NbMM_Selected.grid(row=1,column=5)
    #
    #
    #
    ##NbMM_Btn_Use.grid(row=2,column=1)
    ##NbMM_Btn_Upgrade.grid(row=2,column=2)
    #
    ##NbMM_Btn_Forget.grid(row=2,column=4)
    #
    ##region binding
    #
    #
    ##endregion

#endregion
#region --Page Drop set up---
NbMD_Item0=tk.Label(NbM_Drop,text='Item 0/50')
NbMD_Item=tk.Listbox(NbM_Drop,width=20,height=10)
NbMD_Btn_ItemTake=tk.Button(NbM_Drop,text='Take',width=7)
NbMD_Btn_ItemSell=tk.Button(NbM_Drop,text='Sell',width=7)
NbMD_Btn_ItemClear=tk.Button(NbM_Drop,text='Sell All',width=7)
NbMD_Btn_ItemAll=tk.Button(NbM_Drop,text='Take All',width=7,command=Drop_TakeAll_Item)

NbMD_Item0.grid(row=0,column=0,columnspan=2)
NbMD_Item.grid(row=2,column=0,columnspan=2)
NbMD_Btn_ItemTake.grid(row=3,column=0,columnspan=1)
NbMD_Btn_ItemSell.grid(row=3,column=1,columnspan=1)
NbMD_Btn_ItemClear.grid(row=1,column=0,columnspan=1)
NbMD_Btn_ItemAll.grid(row=1,column=1,columnspan=1)

NbMD_Equip0=tk.Label(NbM_Drop,text='Equip 0/50')
NbMD_Equip=tk.Listbox(NbM_Drop,width=20,height=10)
NbMD_Btn_EquipTake=tk.Button(NbM_Drop,text='Take',width=7)
NbMD_Btn_EquipSell=tk.Button(NbM_Drop,text='Sell',width=7)
NbMD_Btn_EquipClear=tk.Button(NbM_Drop,text='Sell All',width=7)
NbMD_Btn_EquipAll=tk.Button(NbM_Drop,text='Take All',width=7,command=Drop_TakeAll_Equip)

NbMD_Equip0.grid(row=0,column=2,columnspan=2)
NbMD_Equip.grid(row=2,column=2,columnspan=2)
NbMD_Btn_EquipTake.grid(row=3,column=2,columnspan=1)
NbMD_Btn_EquipSell.grid(row=3,column=3,columnspan=1)
NbMD_Btn_EquipClear.grid(row=1,column=2,columnspan=1)
NbMD_Btn_EquipAll.grid(row=1,column=3,columnspan=1)

    #NbMD_Info0=tk.Label(NbM_Drop,text='Information')
    #NbMD_Info=tk.Text(NbM_Drop,height=8,width=15,wrap='word')
    #NbMD_Selected=tk.Canvas(NbM_Drop,width=60,height=60,bg='blue',highlightthickness=1,highlightbackground='red')
    #
    #NbMD_Info0.grid(row=0,column=3)
    #NbMD_Selected.grid(row=1,column=3,rowspan=2)
    #NbMD_Info.grid(row=3,column=3,rowspan=3)

NbMD_Item.bind('<<ListboxSelect>>',Drop_Inv_Item_Click)
NbMD_Equip.bind('<<ListboxSelect>>',Drop_Inv_Equip_Click)

NbMD_Btn_ItemTake.bind("<ButtonRelease-1>",Drop_Take_Item)
NbMD_Btn_ItemSell.bind("<ButtonRelease-1>",Drop_Sell_Item)
NbMD_Btn_ItemClear.bind("<ButtonRelease-1>",Drop_Clear_Item)

NbMD_Btn_EquipTake.bind("<ButtonRelease-1>",Drop_Take_Equip)
NbMD_Btn_EquipSell.bind("<ButtonRelease-1>",Drop_Sell_Equip)
NbMD_Btn_EquipClear.bind("<ButtonRelease-1>",Drop_Clear_Equip)
#endregion
#endregion End of Frame Monster set up

#region Define GUI group
GUIs_player=[0,0,0]

for ii in range(3):
    GUIs_player[ii]=GUIgroup()
    GUIs_player[ii].Canv_Pic=P_canv[ii]
    GUIs_player[ii].Canv_Equiped=NbPE_Canvs
    for jj in range(7):
        GUIs_player[ii].Lab_Att[jj]=NbPS_Labels[jj+1][2]
        GUIs_player[ii].Lab_Def[jj]=NbPS_Labels[jj+1][3]
        GUIs_player[ii].Lab_Prof[jj]=NbPS_Labels[jj+1][4]
        GUIs_player[ii].Lab_Stat[jj]=NbPS_Labels[jj+1][0]
    GUIs_player[ii].List_Equip=NbPE_Inv
    GUIs_player[ii].List_Item=NbPA_Inv_item
    GUIs_player[ii].List_Magic=NbPA_Inv_mag
    GUIs_player[ii].Lab_Name=P_NameLV[ii]
    GUIs_player[ii].Lab_Nickname=P_NickName[ii]
    GUIs_player[ii].Lab_HP=P_HP[ii]
    GUIs_player[ii].Lab_MP=P_MP[ii]
    GUIs_player[ii].Pbar_HP=P_HPbar[ii]
    GUIs_player[ii].Pbar_MP=P_MPbar[ii]

    GUIs_player[ii].Lab_Money=NbPS_Money
    GUIs_player[ii].Lab_PTstat=NbPS_StatPT
    GUIs_player[ii].Lab_PTmag=NbPA_Lab_Mpt
    GUIs_player[ii].Lab_PTequip=NbPE_PTequip

    GUIs_player[ii].Lab_ItemInv=NbPA_Lab_item
    GUIs_player[ii].Lab_MagicInv=NbPA_Lab_mag
    GUIs_player[ii].Lab_EquipInv=NbPE_Inv0

    GUIs_player[ii].Lab_LVexp=NbPS_LVexp
    GUIs_player[ii].Lab_HPreg=NbPS_HPreg
    GUIs_player[ii].Lab_MPreg=NbPS_MPreg
    GUIs_player[ii].Lab_DropR=NbPS_Drop

    GUIs_player[ii].Lab_AP=P_AP[ii]

GUIs_monster=[0,0,0]

for ii in range(3):
    GUIs_monster[ii]=GUIgroup()
    GUIs_monster[ii].Canv_Pic=M_canv[ii]
    GUIs_monster[ii].Canv_Equiped=NbME_Canvs
    for jj in range(7):
        GUIs_monster[ii].Lab_Att[jj]=NbMS_Labels[jj+1][2]
        GUIs_monster[ii].Lab_Def[jj]=NbMS_Labels[jj+1][3]
        GUIs_monster[ii].Lab_Prof[jj]=NbMS_Labels[jj+1][4]
        GUIs_monster[ii].Lab_Stat[jj]=NbMS_Labels[jj+1][0]
    GUIs_monster[ii].List_Equip=NbME_Inv
    GUIs_monster[ii].List_Item=NbMI_Inv
    GUIs_monster[ii].List_Magic=NbMM_Inv
    GUIs_monster[ii].Lab_Name=M_NameLV[ii]
    GUIs_monster[ii].Lab_Nickname=M_NickName[ii]
    GUIs_monster[ii].Lab_HP=M_HP[ii]
    GUIs_monster[ii].Lab_MP=M_MP[ii]
    GUIs_monster[ii].Pbar_HP=M_HPbar[ii]
    GUIs_monster[ii].Pbar_MP=M_MPbar[ii]

    GUIs_monster[ii].Lab_Money=NbMS_Money
    GUIs_monster[ii].Lab_PTstat=NbMS_StatPT
    GUIs_monster[ii].Lab_PTmag=NbMM_Point
    GUIs_monster[ii].Lab_PTequip=NbME_Point

    GUIs_monster[ii].Lab_ItemInv=NbMI_Inv0
    GUIs_monster[ii].Lab_MagicInv=NbMM_Inv0
    GUIs_monster[ii].Lab_EquipInv=NbME_Inv0

    GUIs_monster[ii].Lab_LVexp=NbMS_LVexp
    GUIs_monster[ii].Lab_HPreg=NbMS_HPreg
    GUIs_monster[ii].Lab_MPreg=NbMS_MPreg
    GUIs_monster[ii].Lab_DropR=NbMS_Drop

    GUIs_monster[ii].Lab_AP=M_AP[ii]

#endregion GUIs Define

#endregion End of GUIs

#region main routine debug
# Welcome msg

# Start by creating Player
G_Player[0]=Player()
G_Player[0].ID=-1
G_Player[0].Name='The Dude'
G_Player[0].Nickname='The ONE'
G_Player[0].Pic='Player.png'
G_Player[0].PlayerRoll(Dict_Equipment,Dict_Item,Dict_Magic)
G_Player[0].LoadImg(CWD)
G_Player[0].Rest_Full()
G_Player[0].UpdateGUI(GUIs_player[0])


#following should be in button function
G_Player[0].UpdateGUI_Basic(GUIs_player[0])

ActiveP_index=0
P_canv[ActiveP_index].config(highlightthickness=3,highlightbackground='yellow')

ActiveM_index=-1


#
### initialize by assign Nobody to all players, if anyone dies, replace the slot with Nobody (empty player())
#for ii in range(3):
#    #G_Player[ii]=Player()
#    G_Player[ii]=copy.copy(Dict_Monster[ii+1])
#    G_Player[ii].Randomize(Dict_Equipment,Dict_Item,Dict_Magic)
#    G_Player[ii].Data_Base[10,0]=100
#    G_Player[ii].LoadImg(CWD)
#    G_Player[ii].UpdateGUI_Basic(GUIs_player[ii])
#
#    #G_Monster[ii]=Player()
#    G_Monster[ii]=copy.deepcopy(Dict_Monster[ii+4])
#    G_Monster[ii].Randomize(Dict_Equipment,Dict_Item,Dict_Magic)
#    G_Monster[ii].LoadImg(CWD)
#    G_Monster[ii].UpdateGUI_Basic(GUIs_monster[ii])
#
#ActiveP_index=0
#ActiveM_index=0
#P_canv[ActiveP_index].config(highlightthickness=3,highlightbackground='yellow')
#G_Player[ActiveP_index].UpdateGUI(GUIs_player[ActiveP_index])
#M_canv[ActiveM_index].config(highlightthickness=3,highlightbackground='yellow')
#G_Monster[ActiveM_index].UpdateGUI(GUIs_monster[ActiveM_index])
##

#endregion  main routine

#region Idle running loop================
def constRun():
    for ii in range(3):
        if G_Player[ii].ID!=0:
            if ii==ActiveP_index:
                G_Player[ii].UpdateGUI(GUIs_player[ii])
            else:
                G_Player[ii].UpdateGUI_Basic(GUIs_player[ii])
        
        if G_Monster[ii].ID!=0:
            if ii==ActiveM_index:
                G_Monster[ii].UpdateGUI(GUIs_monster[ii])
            else:
                G_Monster[ii].UpdateGUI_Basic(GUIs_monster[ii])

    
    root.after(200,constRun)

#constRun()
#endregion End of Idle running loop================
root.mainloop()