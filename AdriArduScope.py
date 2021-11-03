# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 19:32:52 2019

@author: akeating
"""

import serial
import findSerialPorts
from os import path as ospath
import numpy as np
from sys import argv, exit
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.widgets import Button,TextBox,Slider,RadioButtons
from matplotlib.text import Text
import matplotlib.patches as patches
import time
from datetime import datetime
import sys

VERBOSE_FLAG=False
ChannelOptions={'Ch1':1, r"$\bf{" + 'Ch2' + "}$":2,'Alt Ch1 & 2':3}
Functions={'OscilloScope':1, r"$\bf{" + 'Spectrum' + "}$":2,'Cross-Correlation (Ch1-MEM)':3,'Cross-Correlation (Ch1-Ch2)':4}
__author__="Adrian Keating(UWA)"
__version__ = "0.1.0"

def nextfilename(filename):
    prefix,ext=ospath.splitext(filename)
    counter = 0
    filename = prefix+"{}"+ext
    while ospath.isfile(filename.format(counter)):
        counter += 1
    filename = filename.format(counter)
    return filename

class scope_button:
    def __init__(self):
        self.buttonlist = []
        self.dblbuttonlist = []
        self.buttonliststate=[]
        self.buttonlistsvales=[]
        self.pressbuttonlist=[]
        self.X0=.7
        self.Y0=.7
        self.w=.04
        self.Scale=50
        self.layout='vertical' # or 'horizontal'
        self.lableside='top' # or 'left'
        self.colors=['red', 'lime' ]
        self.Yconstants={'top':1,'bottom':-1}
        self.Xconstants={'left':-1,'right':1}
        self.font={'fontname':'Arial', 'size':str(np.sqrt(self.w)*self.Scale), 'color':'black', 'weight':'normal','verticalalignment':'bottom'}

 
        self.ind = 3
        #self.ch=1
        self.N=1024
        self.text=str(self.N)
        self.ac=False
        self.savenext=False
        self.absflag=False
        self.logflag=False
        self.memory=[]
        self.xcorrflag=False
        self.mem_storeflag=False
        self.lpf_flag=False
        self.Channel=1
        self.CurrentChannel=1
        self.Function=1
        self.Button_dict={}
        
        #self.font={'fontname':'Arial', 'size':str(np.sqrt(self.w)*self.Scale), 'color':'black', 'weight':'normal','verticalalignment':'bottom'}


    def add_dblbutton(self, cmd,label='Select',values=[1.12,2.123,3.1234,4.12345,5,6,7,8,9,10],direction='horizontal',initalindex=0):

        #bttn_ax.set_frame_on(False)
        #Button_dict={}

        #bttn.append(Button(bttn_ax[0],label=u'$\u25B6$',hovercolor='.1')) #'Enter', , image=ICON_PLAY)
        #bttn.append(TextBox(bttn_ax[1],label=u'$\u25C0$',hovercolor='.5')) #'Enter', , image=ICON_PLAY)
        #bttn_ax.add_patch(rect3)
 # Bottom vertical alignment for more space
        #bttn_ax.set_fontsize(20, **title_font)
        #fontname='Arial', size=str(np.sqrt(w)*Scale))
         #fontname='Arial', size=str(np.sqrt(w)*Scale))
        if (direction=='horizontal'):
            left_ax=plt.axes([self.X0-np.sqrt(self.w)/7, self.Y0, self.w,self.w])
            right_ax=plt.axes([self.X0+np.sqrt(self.w)/7, self.Y0, self.w,self.w])
            self.Button_dict.update({'Right_Button':Button(right_ax,label=u'$\u25B6$',color='r',hovercolor='.5')})
            self.Button_dict.update({'Left_Button':Button(left_ax,label=u'$\u25C0$',color='g',hovercolor='.5')})
        else:
            left_ax=plt.axes([self.X0, self.Y0-np.sqrt(self.w)/3.5, self.w,self.w]) # actually BOTTOM
            right_ax=plt.axes([self.X0, self.Y0+np.sqrt(self.w)/3.5, self.w,self.w]) # actually TOP
            self.Button_dict.update({'Right_Button':Button(right_ax,label=u'$\u25B2$',color='r',hovercolor='.5')})
            self.Button_dict.update({'Left_Button':Button(left_ax,label=u'$\u25BC$',color='g',hovercolor='.5')})

        self.Button_dict['Right_Button'].label.set_fontsize((eval(self.font['size'])*2))
        self.Button_dict['Left_Button'].label.set_fontsize((eval(self.font['size'])*2))
        right_ax.set_frame_on(False)
        left_ax.set_frame_on(False)
        index=len(self.dblbuttonlist)
        #self.Button_dict.update({'state':True})
        self.Button_dict.update({'values':values})
        self.Button_dict.update({'value':values[initalindex]})
        self.Button_dict.update({'index':initalindex})
        X=0
        Y=0
        if(self.lableside.lower() in self.Yconstants):
            Y=self.Yconstants[self.lableside.lower()]+0.5*self.w
        if(self.lableside.lower() in self.Xconstants):
            X=self.Xconstants[self.lableside.lower()]*.05*len(label)/np.sqrt(self.w) #eval(self.font['size'])/(1*self.Scale)
        if (direction=='horizontal'):
            self.Button_dict.update({'label':label})
            self.Button_dict.update({'label_pos':left_ax.text(X, Y+0.5*self.w,self.Button_dict['label'], **self.font)})
            self.Button_dict.update({'value_pos':left_ax.text(.75+self.w/2, eval(self.font['size'])/150,np.around(self.Button_dict['value'],2), **self.font)})
        else:
            self.Button_dict.update({'label':label})
            self.Button_dict.update({'label_pos':left_ax.text(X-.1, Y-1.5,self.Button_dict['label'], **self.font,rotation=90)})
            self.Button_dict.update({'value_pos':left_ax.text(X+.2, Y+.4,np.around(self.Button_dict['value'],2), **self.font)})
        #.label.set_fontsize(w*Scale)

        #print(self.buttonliststate[1])
        # this lambda function first calls the set state and then the cmd 
        valuesign=int(np.sign(values[-1]-values[0]))
        callingfunction_plus=lambda localevent_x: (self.update_dblbutton(valuesign),cmd(self.Button_dict['value']))
        callingfunction_minus=lambda localevent_x: (self.update_dblbutton(-valuesign),cmd(self.Button_dict['value']))
        #self.Button_dict.update({'command':cmd})
        self.Button_dict['Left_Button'].on_clicked(callingfunction_minus)
        self.Button_dict['Right_Button'].on_clicked(callingfunction_plus)
        self.dblbuttonlist.append(self.Button_dict)

        if (self.layout=='vertical'):
            if (direction=='horizontal'):
                self.Y0-=self.w*2+np.sqrt(self.w)/8
            else:
                self.Y0-=self.w*5+np.sqrt(self.w)/8
        else:
            self.X0+=self.w*2.5
        return index  # return index to button ID
    
    def update_pressbutton(self, Btn_index,Val_index):
        
        Btn=self.Button_dict
        tempindex=Btn['index']+Val_index
        if(tempindex<len(Btn['values']) and tempindex>-1):
            Btn['index']=tempindex
            Btn['value']=Btn['values'][tempindex]
        #Btn['value_pos'].set_text(np.around(Btn['value'],2))  
        #print(Btn_index,Val_index,Btn['value'])
        return tempindex  # return index to button ID
    
    def update_dblbutton(self, Val_index):
        
        Btn=self.Button_dict
        tempindex=Btn['index']+Val_index
        if(len(Btn['values'])>2):
            # deal with a preset list
            if(tempindex<len(Btn['values']) and tempindex>-1):
                Btn['index']=tempindex
                Btn['value']=Btn['values'][tempindex]
        else:
            if(tempindex<=max(Btn['values']) and tempindex>=min(Btn['values']) ):
                Btn['index']=tempindex
                Btn['value']=tempindex
        Btn['value_pos'].set_text(np.around(Btn['value'],2))  
        #print(Btn_index,Val_index,Btn['value'])
        return tempindex  # return index to button ID

    def addpressbutton(self, cmd,label='button'):
        bttn_ax=plt.axes([self.X0, self.Y0, self.w,self.w])
        #Button_dict={}
        #Button_dict.update({'Button':Button(bttn_ax,label=u'$\u1F4BE$')})
        self.Button_dict.update({'Button':Button(bttn_ax,label=u'$\u25B6$')})
        
        bttn_ax.set_frame_on(False)
        #self.Button_dict.update({'Button':Button(bttn_ax,label='',color='r',hovercolor='.5')})
        index=len(self.pressbuttonlist)
        self.Button_dict.update({'state':True})
        #self.Button_dict.update({'values':values})
        self.Button_dict.update({'value':0})
        X=0
        Y=0
        if(self.lableside.lower() in self.Yconstants):
            Y=self.Yconstants[self.lableside.lower()]++0.5*self.w
        if(self.lableside.lower() in self.Xconstants):
            X=self.Xconstants[self.lableside.lower()]*.05*len(label)/np.sqrt(self.w) #eval(self.font['size'])/(1*self.Scale)
        self.Button_dict.update({'value_pos':bttn_ax.text(1+0.1*self.w, 1.5*self.w,self.Button_dict['value'], **self.font)})
        #.label.set_fontsize(w*Scale)
        self.Button_dict.update({'label':label})
        self.Button_dict.update({'label_pos':bttn_ax.text(X, Y+0.5*self.w,self.Button_dict['label'], **self.font)})
        #print(self.buttonliststate[1])
        # this lambda function first calls the set state and then the cmd 
        #callingfunction=lambda localevent_x: (self.setstate(index),cmd(localevent_x))
        callingfunction=lambda localevent_x: (cmd(localevent_x))
        #self.Button_dict.update({'command':callingfunction})
        self.Button_dict['Button'].on_clicked(callingfunction)
        self.pressbuttonlist.append(self.Button_dict)

        if (self.layout=='vertical'):
            self.Y0-=self.w*1.5+np.sqrt(self.w)/8
        else:
            self.X0+=self.w*2.5
        self.setstate(index)
        return   # return index to button ID
    
    def addbutton(self, cmd,label='button',values=['off','on']):
        bttn_ax=plt.axes([self.X0, self.Y0, self.w,self.w])
        #print('cmd',cmd)
        #cmd()
        #bttn_ax.set_frame_on(False)
        self.Button_dict={}
        rect1 = patches.Rectangle((.1,.1), .4 ,.8, linewidth=0, edgecolor='k', facecolor='k')
        rect2 = patches.Rectangle((.5,.1), .4,.8, linewidth=0, edgecolor='k', facecolor='k')
        #rect3=patches.Rectangle((0, .5), 0.5, 0.5,alpha=.1,label='Label', facecolor='w')
        bttn_ax.add_patch(rect1)
        bttn_ax.add_patch(rect2)
        #bttn_ax.add_patch(rect3)
 # Bottom vertical alignment for more space
        #bttn_ax.set_fontsize(20, **title_font)
        #fontname='Arial', size=str(np.sqrt(w)*Scale))
         #fontname='Arial', size=str(np.sqrt(w)*Scale))
        self.Button_dict.update({'Button':Button(bttn_ax,label='',color='r',hovercolor='.5')})
        index=len(self.buttonlist)-1
        self.Button_dict.update({'state':True})
        self.Button_dict.update({'values':values})
        self.Button_dict.update({'value':values[0]})
        X=0
        Y=0
        if(self.lableside.lower() in self.Yconstants):
            Y=self.Yconstants[self.lableside.lower()]++0.5*self.w
        if(self.lableside.lower() in self.Xconstants):
            X=self.Xconstants[self.lableside.lower()]*.05*len(label)/np.sqrt(self.w) #eval(self.font['size'])/(1*self.Scale)
        self.Button_dict.update({'value_pos':bttn_ax.text(1+0.1*self.w, 1.5*self.w,self.Button_dict['value'], **self.font)})
        #.label.set_fontsize(w*Scale)
        self.Button_dict.update({'label':label})
        self.Button_dict.update({'label_pos':bttn_ax.text(X, Y+0.5*self.w,self.Button_dict['label'], **self.font)})
        #print(self.buttonliststate[1])
        # this lambda function first calls the set state and then the cmd 
        callingfunction=lambda localevent_x: (self.setstate())
        self.Button_dict.update({'command':callingfunction})
        self.Button_dict['Button'].on_clicked(callingfunction)
        self.buttonlist.append(self.Button_dict)

        if (self.layout=='vertical'):
            self.Y0-=self.w*1.5+np.sqrt(self.w)/8
        else:
            self.X0+=self.w*2.5
        self.setstate()
        return index  # return index to button ID

    def setstate(self,index=0):
        #print('index',index,len(self.buttonlist),self.X0, self.Y0)
        Btn=self.Button_dict
        toggle=Btn['state']
        #print(Btn['value_pos'].__dict__)
        if(toggle==True):
            Btn['Button'].color = self.colors[0]
            Btn.update({'value':Btn['values'][0]})
        else:
            Btn['Button'].color= self.colors[1]
            Btn.update({'value':Btn['values'][1]})
        Btn['value_pos'].set_text(Btn['value'])
        # If you want the button's color to change as soon as it's clicked, you'll
        # need to set the hovercolor, as well, as the mouse is still over it
        Btn['Button'].hovercolor=Btn['Button'].color  # forces an immediate change to the button color
        #Btn['Button'].ax.figure.set_axis_bgcolor(Btn['Button'].color)
        #print('self.buttonlist',self.buttonlist[index].__dict__)
        Btn['Button'].ax.patches[0].set_visible(toggle)
        Btn['Button'].ax.patches[1].set_visible(not(toggle))
        #rect2.set_visible(not(toggle))
        
        Btn['state']=not(toggle)
        #fig.update()
        Btn['Button'].canvas.draw()
        Btn['Button'].canvas.draw_idle()
        Btn['Button'].ax.figure.canvas.draw()
        #Btn['Button'].update()
        #Btn['Button'].ax.canvas.draw()
        fig.canvas.draw_idle() #update_ update_
        fig.canvas.draw()
        return
    
class panel:
    def __init__(self):
        self.buttonlist = []
        self.dblbuttonlist = []
        self.buttonliststate=[]
        self.buttonlistsvales=[]
        self.pressbuttonlist=[]
        self.X0=.7
        self.Y0=.7
        self.w=.04
        self.Scale=50
        self.layout='vertical' # or 'horizontal'
        self.lableside='top' # or 'left'
        self.colors=['red', 'lime' ]
        self.Yconstants={'top':1,'bottom':-1}
        self.Xconstants={'left':-1,'right':1}
        self.font={'fontname':'Arial', 'size':str(np.sqrt(self.w)*self.Scale), 'color':'black', 'weight':'normal','verticalalignment':'bottom'}
        self.about_string=(
        r"$\bf{Adri/Adru-Scope}$ (Version: "+str(__version__)+") is a project developed by Dr. Adrian Keating within the School of Engineering "
        "at The University of Western Australia. The idea is to create the basic functionality of an Oscilloscope (plus spectrum "
        "analyser and cross-correlation scope) from a very low cost Arduino. The project was developed on an Arduino Uno and "
        "Nano, with less that 2k of free space. This can allow students the ability to explore signals, collect data and "
        "complete laboratories even when they are completing portions of their studies remotely.")

        self.ABOUT_IMG = mpimg.imread(ospath.join('images','About.png'))
        
        self.ind = 3
        #self.ch=1
        self.f_index=3
        self.N=1024
        self.text=str(self.N)
        self.ac=False
        self.savenext=False
        self.absflag=False
        self.logflag=False
        self.memory=[]
        self.xcorrflag=False
        self.mem_storeflag=False
        self.lpf_flag=False
        self.Channel=1
        self.CurrentChannel=1
        self.Function=1
        self.Offset=2.5
        self.Amp=6
        self.OffsetSpectrum=2.5
        self.AmpSpectrum=6
        self.TimebaseMultiples=6.6 # ms
        self.DelayMultiples=0.01 # ms
        self.TimebaseValue=self.TimebaseMultiples
        self.DelayValue=0
        self.Timebaseindex0=3
        self.ValidTimebaseValue=[(2**i)*self.TimebaseMultiples for i in range(-1*self.Timebaseindex0,15)]
        #print(self.ValidTimebaseValue)
        self.shwoabout=False
        #self.Setup_about()
        self.fig2=None
        # Send to console
        print(self.about_string)
        
        
        
        #self.font={'fontname':'Arial', 'size':str(np.sqrt(self.w)*self.Scale), 'color':'black', 'weight':'normal','verticalalignment':'bottom'}

    
    def about(self,ErrorScreen=''):
        self.shwoabout=True
        self.fig2, self.ax2 = plt.subplots(figsize=(6,5))
        if(ErrorScreen!=''):

            axErrortext=self.invisible_axis([0.1, .92, 1,1])
            axErrortext.text(0, 0, ErrorScreen , color='r',fontname='Arial', size=11,wrap = True)
            axErrortext.set_frame_on(False)
            self.fig2.canvas.set_window_title("ERROR in Adri/Ardu-Scope")
        else:
            self.fig2.canvas.set_window_title("ABOUT Adri/Ardu-Scope")
        axbtn=plt.axes([0, -.2, 1,1])
        Button(axbtn,label='', image=self.ABOUT_IMG)
        axbtn.set_frame_on(False)
        self.ax2.set_frame_on(False)
        self.ax2.axes.xaxis.set_visible(False)
        self.ax2.axes.yaxis.set_visible(False)
        self.ax2.axes.xaxis.set_ticks([])
        self.ax2.axes.yaxis.set_ticks([])
        self.ax2.axes.xaxis.set_ticklabels([])
        self.ax2.axes.yaxis.set_ticklabels([])
        self.ax2.axes.xaxis.set_label([])
        self.ax2.axes.yaxis.set_label([])
        #fig2.set_visible(False) # show no plot area #not plt.gcf().get_visible())
        axtext=plt.axes([0, .45, .5,.5])
        
        
        axtext.text(0.05, .4,self.about_string, fontname='Arial', size=11,wrap = True)
        axtext.set_frame_on(False)
        axtext.axes.xaxis.set_visible(False)
        axtext.axes.yaxis.set_visible(False)
        axtext.axes.xaxis.set_ticks([])
        axtext.axes.yaxis.set_ticks([])
        axtext.axes.xaxis.set_ticklabels([])
        axtext.axes.yaxis.set_ticklabels([])
        axtext.axes.xaxis.set_label([])
        axtext.axes.yaxis.set_label([])
        plt.draw()
        self.fig2.canvas.draw_idle() #update_ update_
        #self.fig2.canvas.flush_events()
        plt.pause(0.1)
        #self.canvas.draw_idle()
        self.fig2.canvas.draw()
        self.fig2.canvas.mpl_connect('close_event', self.beforeclose)
        #while(self.shwoabout==True):
        if(ErrorScreen==''):
            self.fig2.canvas.draw_idle()
            time.sleep(5)
            plt.close(self.fig2) 
            self.shwoabout=False
        return

    def beforeclose(self,event):
        if (VERBOSE_FLAG): print('Trying to close')
        self.shwoabout=False
        #plt.close(self.fig2) #=None
        #return
    
    def Setup_about(self,ErrorScreen=''):
        self.fig2, self.ax2 = plt.subplots(figsize=(6,5))
        if(ErrorScreen!=''):

            axErrortext=self.invisible_axis([0.1, .92, 1,1])
            axErrortext.text(0, 0, ErrorScreen , color='r',fontname='Arial', size=11,wrap = True)
            axErrortext.set_frame_on(False)
            self.fig2.canvas.set_window_title("ERROR in Adri/Ardu-Scope")
        else:
            self.fig2.canvas.set_window_title("ABOUT Adri/Ardu-Scope")
        axbtn=plt.axes([0, -.2, 1,1])
        Button(axbtn,label='', image=self.ABOUT_IMG)
        axbtn.set_frame_on(False)
        self.ax2.set_frame_on(False)
        self.ax2.axes.xaxis.set_visible(False)
        self.ax2.axes.yaxis.set_visible(False)
        self.ax2.axes.xaxis.set_ticks([])
        self.ax2.axes.yaxis.set_ticks([])
        self.ax2.axes.xaxis.set_ticklabels([])
        self.ax2.axes.yaxis.set_ticklabels([])
        self.ax2.axes.xaxis.set_label([])
        self.ax2.axes.yaxis.set_label([])
        #fig2.set_visible(False) # show no plot area #not plt.gcf().get_visible())
        axtext=plt.axes([0, .45, .5,.5])
        
        
        axtext.text(0.05, .4,self.about_string, fontname='Arial', size=11,wrap = True)
        axtext.set_frame_on(False)
        axtext.axes.xaxis.set_visible(False)
        axtext.axes.yaxis.set_visible(False)
        axtext.axes.xaxis.set_ticks([])
        axtext.axes.yaxis.set_ticks([])
        axtext.axes.xaxis.set_ticklabels([])
        axtext.axes.yaxis.set_ticklabels([])
        axtext.axes.xaxis.set_label([])
        axtext.axes.yaxis.set_label([])
        #plt.draw()
        #self.fig2.canvas.draw_idle() #update_ update_
        self.fig2.canvas.flush_events()
        plt.pause(.00001)
        #self.canvas.draw_idle()
        #fig2.canvas.draw()
        return
    def invisible_axis(self,position_list):
        ax2=plt.axes(position_list)
        ax2.set_frame_on(False)
        ax2.axes.xaxis.set_visible(False)
        ax2.axes.yaxis.set_visible(False)
        ax2.axes.xaxis.set_ticks([])
        ax2.axes.yaxis.set_ticks([])
        ax2.axes.xaxis.set_ticklabels([])
        ax2.axes.yaxis.set_ticklabels([])
        ax2.axes.xaxis.set_label([])
        ax2.axes.yaxis.set_label([])
        return ax2

    
    def SetChannel(self,label):
        self.Channel = int(ChannelOptions[label])
        if (VERBOSE_FLAG): print(self.Channel)
        return

    def SetAmp(self,value):
        self.Amp=value
        return

    def SetOffset(self,value):
        self.Offset=value
        return

    def Timebase(self,value):       
        if(value>self.ValidTimebaseValue[self.f_index]):
            self.nextf()
            self.TimebaseValue=self.ValidTimebaseValue[self.f_index]
        elif(value<self.ValidTimebaseValue[self.f_index] and value>=self.ValidTimebaseValue[self.Timebaseindex0]):
            self.prevf()
            self.TimebaseValue=self.ValidTimebaseValue[self.f_index]
        else:
            self.TimebaseValue=value
        return

    def Delay(self,value):
        self.DelayValue=value
        string='d'+str(int(self.DelayValue*1000))+';'
        if (VERBOSE_FLAG): print(string,self.f_index)
        heartbeatserial(string)  # send as bytes
        heartbeatio.flush()
        time.sleep(.1) # wait 
        return

    def nextf(self ):
        self.f_index += 1
        self.f_index = max(min(self.f_index,15),3)
        string='f'+str(self.f_index)+';'
        if (VERBOSE_FLAG): print(string,self.f_index)
        heartbeatserial(string)  # send as bytes
        heartbeatio.flush()
        time.sleep(.1) # wait 
        return

    def prevf(self ):
        self.f_index -= 1
        self.f_index = max(min(self.f_index,15),3)
        string='f'+str(self.f_index)+';'
        if (VERBOSE_FLAG): print(string,self.f_index)
        heartbeatserial(string)  # send as bytes
        heartbeatio.flush()
        time.sleep(.1) # wait 
        return    
        
    def SetFunction(self,label):
        self.Function = int(Functions[label])
        if (VERBOSE_FLAG): print(self.Function)
        return
    def save_on(self,event):
        self.savenext=True
        return
    def abs_on(self,event):
        self.absflag = not(self.absflag)
        #print(ac_onBtn.val,self.ac)
        return
    def log_on(self,event):
        self.logflag = not(self.logflag)
        if(self.logflag):
            log_onBtn.label.set_text("LOG(|x|)")
            log_onBtn.label.set_fontsize(10)
            log_onBtn.color="red"
        else:
            log_onBtn.label.set_text("x(t)")
            log_onBtn.label.set_fontsize(10)
            log_onBtn.color="green"
        return
    def ac_on(self, event):
        self.ac = not(self.ac)
        if(self.ac):
            if (VERBOSE_FLAG): print('AC',event)
        else:
            if (VERBOSE_FLAG): print('DC',event)
        return
    def mem_store(self,event):
        self.memory=[]
        self.mem_storeflag = True
        return
        
    def xcorr_on(self,event):
        self.xcorrflag = not(self.xcorrflag) # xcorrflag
        if(self.xcorrflag):
            xcorr_on_Btn.label.set_text("Rxx")
            xcorr_on_Btn.label.set_fontsize(10)
            xcorr_on_Btn.color="red"
        else:
            xcorr_on_Btn.label.set_text("?Rxx?")
            xcorr_on_Btn.label.set_fontsize(10)
            xcorr_on_Btn.color="green"
        return
    
    
def flushheartbeatserial():
    if COMValid:
        if verbosegbl: print ("Attempting to FLUSH heartbeat IO")
        heartbeatio.flush()  # send as bytes
        time.sleep(.5) # wait
    return     
def heartbeatserial(arg):
    mystrout=arg  #+'\n'
    if COMValid:
        heartbeatio.write(mystrout.encode())  # send as bytes
    time.sleep(.01) # wait 
    return mystrout
def heartbeatstart():
    heartbeatserial('r') 
    #time.sleep(.02) # wait 
    return 
def heartbeatstop():
    #heartbeatserial('x') 
    return 
def getheartbeat():
    heartbeatserial('g') # gets a single line 
    msg=heartbeatio.readline()
    return msg
def heartbeatserialReadx():
    lenofdata=heartbeatio.inWaiting()
    if verbosegbl: print (str(lenofdata))
    msg=''
    if (lenofdata > 0):
        msg = heartbeatio.read(lenofdata) # read 
        if verbosegbl: print (str(msg))
    time.sleep(.0020) # wait 5    
    return msg

def heartbeatserialRead():

    msg=heartbeatio.readline()  
    return msg

def gracefulexit( ):
    if (VERBOSE_FLAG): print(u"COM ports issue: TRYING to EXIT NICELY")


def getsync(heartbeatio):
    validdata=False
    while(validdata==False):
        header = heartbeatio.read(10)
        #print('header',header)
        if(len(header)>1):
            #print('header',header[0],header[1])
            if(header[0]==65 and header[1]==90):  #65='A', 90='Z'
                validdata=True
    Samples=header[2]*256+header[3]
    duration_micro=header[4]*256+header[5]
    Nbits=header[6]
    Beyond8=Nbits-8
    return ({'N':Samples,'T':duration_micro,'Beyond8':Beyond8})


def butter_lowpass_filter(data, cutoff, fs, order):
    nyq = 0.5 * fs  # Nyquist Frequency
    normal_cutoff = cutoff / nyq
    # Get the filter coefficients 
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y

def updateplot(i):
    global line1,line2
    global tlast, ylast
    global plt,ax
    callback=frontpanel  # redefine to reduce code rewrite
    if(1):
        proceedflag=True
        retry=0
        validdata=False
        while(validdata==False and proceedflag==True):
            #print('GOT A',header)      
            astart = heartbeatio.read(1) # look for start byte
            if(len(astart)>0):
                if(astart[0]==65):
                    #print('GOT A',header)
                    zstart = heartbeatio.read(1)
                    if(len(zstart)>0):
                        if(zstart[0]==90):
                            header = heartbeatio.read(10)
                    #print('header',header)
                            if(len(header)!=10):
                                print('Incomplete header read failure only ',len(header),' in length = ',header)
                                proceedflag=False
                                heartbeatio.flush()  # MUST flush after a CRC failues in the header
                                time.sleep(.1) 
                                #heartbeatserial("X")  # send as bytes  
                                #time.sleep(.1) 
                                #heartbeatserial("R1;")  # send as bytes 
                            else:
                                SamplesTaken=header[0]*256+header[1]
                                Samples=header[2]*256+header[3]
                                duration_micro=header[4]*256*256+header[5]*256+header[6]
                                Nbits=header[7]
                                crc=SamplesTaken +duration_micro+Nbits
                        #headercrc=(crc).to_bytes(2, byteorder='big')
                                test=header[8]*256+header[9]
                            #print(test,crc)
                            #print(headercrc,duration_micro,Samples,Nbits)
                            #print(crc,header[8],test,crc%(256*256))
                                if(test==crc%(256*256)):
                                    validdata=True
                                else:
                                    print('HEADER CRC failure',astart+zstart,SamplesTaken,Samples,duration_micro,Nbits,crc,test)
                                    heartbeatio.flush()  # MUST flush after a CRC failues in the header
                                    time.sleep(.1) 
            else:
                retry=+1
                if(retry%10==0):
                    print('No start bit detected after ', retry,' retry(ies)')
                    heartbeatio.flush()  # MUST flush after a CRC failues in the header
                    time.sleep(.1)
                if(retry>100):
                    print('Aborting Looking for start bit')
                    proceedflag=False

    if(proceedflag==True):
        Beyond8=Nbits-8
        shift=2
        dataset=[]
        #current verions MUST have samples divisible by 8
        if(Samples>0):
                data=heartbeatio.read(int(Samples)) #heartbeatio.read(int(Samples*10/8))
                #print("data=",data)
                if(len(data)!=int(Samples)):
                    proceedflag=False
                    print('Incomplete data failure only ',len(data),' bytes but expected ',int(Samples))
                else:
                    if(Nbits==10):
                        core=data[0]<<shift & (2**Nbits -1)
                        for ind,each in enumerate(data[1:]):
                            
                            carry=each>>(8-shift)  # use current value of shift to calculate carry  
                            if(shift!=0):
                                #print(ind+1,shift,each,each<<shift,core,carry,carry+core)
                                dataset.append(carry+core)
                                #print(ind+1,shift,each,dataset[-1])
                            shift=(shift+Beyond8)%Nbits
                            core=each<<shift & (2**Nbits -1)
    
                    elif(Nbits==8):
                            for ind,each in enumerate(data):
                                dataset.append(each*4) # lower 2 bits have been stripped away
                    # only CONTINUE if proceedflag=True
                    crc = heartbeatio.read(1) 
                    intcrc=int.from_bytes(crc,"little")
                    y=np.array(dataset)
                    oldlocalcrc=int(sum(y)& 255)
                    localcrc=int(sum(data)& 255)
                    #print(duration_micro,SamplesTaken,Samples,Nbits,Scaled_duration_micro,intcrc)
                    #print('CRC',crc,intcrc,localcrc,intcrc==localcrc)
                    #
                    if(intcrc==localcrc):
                        t0=callback.DelayValue+np.linspace(0,duration_micro,len(dataset))/1000
                        fs=1000000/np.mean(np.diff(t0))
                        y0=5*np.array(dataset)/1024 #*Vmax/(2**Nbits)
                        fixed_duration=callback.TimebaseValue #TimebaseMultiples*len(dataset)*(2**(callback.ind-3))/Nmax # in microsec
                        t=t0
                        y=y0
                        if (callback.Function==1):  # \;    
                            ax.set_title("Adri/Ardu-"+r"$\bf{" + 'Scope' + "}$"+': <ESC> to exit')
                            ax.set_xlabel('Time (ms)')
                            ax.set_ylabel('Voltage (V)')
                            saveheader='time(ms),Voltage (V)'
                            savename='ArduScope_V'
                            
                        if (callback.Function==2):   
                            ax.set_title('RealTime Adri/Ardu-'+r"$\bf{" + 'Spectrum' + "}$"+': <ESC> to exit')
                            ax.set_xlabel('Frequency (kHz)')
                            ax.set_ylabel('log10(Voltage)')
                            saveheader='Frequency(kHz),log10(Voltage)'
                            savename='ArduSpectrum_V'
                            ffty=fourier(y) 
                            #print(ffty.size)
                            #print(t[1]-t[0],fixed_duration/len(dataset),fixed_duration/(len(dataset)-1))
                            f = np.linspace(0, 0.5/(t0[1]-t0[0]), ffty.size//2)
                            t=f
                            #t0=f
                            baseline=(0.5*5/len(dataset))
                            y=np.log10(np.abs(ffty[0:ffty.size//2])+baseline/100)  # add baseline/100 to avoid any ZEROS being logged
                            y= (y-np.log10(baseline)) # SUBTRACT the noise FLOOR /np.max(np.abs(y))
                            y=1*(y) #np.max(y)-y)
                            y0=y
                            fixed_duration=0.5*1/(callback.TimebaseValue/ffty.size) #(Scaled_duration_micro/Samples)
                            #print('fixed duration',fixed_duration,duration_micro,(t0[1]-t0[0]),ffty.size)
                        #y=interpolate.splev(t, tck)  
                        if (callback.Function==3):   
                            ax.set_title('RealTime Adri/Ardu-'+r"$\bf{" + 'Correlate(Ch1,MEM)' + "}$"+': <ESC> to exit')
                            ax.set_xlabel('Lag (ms)')
                            ax.set_ylabel('Power ($V^{2}$)')
                            saveheader='Lag (ms),Power ($V^{2}$)'
                            savename='ArduCrossCorrelateR_1mem_V'
                            if (callback.memory!=[]):
                                mean=np.mean(y)
                                y=(y-mean)
                                meanstored=np.mean(callback.memory)
                                yref=(callback.memory-meanstored)
                                y=np.correlate(y,yref,'full')
                                yy=np.correlate(yref,yref,'same')
                                y=y[len(y)//2:len(y)//2+len(y)]/np.max(yy)
                                #print('auto y', len(y))

                        if (callback.Function==4):   
                            ax.set_title('RealTime Adri/Ardu-'+r"$\bf{" + 'Correlate(Ch1,Ch2)' + "}$"+': <ESC> to exit')
                            ax.set_xlabel('Lag (ms)')
                            ax.set_ylabel('Power ($V^{2}$)')
                            saveheader='Lag (ms),Power ($V^{2}$)'
                            savename='ArduCrossCorrelateR_12_V'
                            #callback.CurrentChannel=3
                            if ((callback.CurrentChannel & 2) ==2):
                                # both channels must be active, only update when 2nd grab is obtained
                                mean=np.mean(y)
                                y1=(y-mean)
                                y2=ylast-np.mean(ylast)
                                #meanstored=np.mean(callback.memory)
                                #yref=(callback.memory-meanstored)
                                Rxy=np.correlate(y1,y2,'full')
                                yy1=np.max(np.correlate(y1,y1,'same'))
                                yy2=np.max(np.correlate(y2,y2,'same'))
                                Rxy=np.abs(Rxy[len(Rxy)//2-len(y1)//2:len(Rxy)//2+len(y1)//2]) #/np.max([yy1,yy2])

                        
                        if(ac_btn.Button_dict['state']==True):
                            mean=np.mean(y)
                            y=(y-mean)
                            #ax.set_ylim(-3,3)
                            ax.set_ylim(-frontpanel.Amp/2,frontpanel.Amp/2)
                        else:
                            #print(frontpanel.Amp,frontpanel.Offset,frontpanel.Offset-frontpanel.Amp/2,frontpanel.Amp/2+frontpanel.Offset)
                            ax.set_ylim(frontpanel.Offset-frontpanel.Amp/2,frontpanel.Amp/2+frontpanel.Offset)
                        if(1):
                            if(callback.xcorrflag==True):
                                if (callback.memory!=[]):
                                    y=np.correlate(y,callback.memory,'same')
                                    yy=np.correlate(callback.memory,callback.memory,'same')
                                    y=y/np.max(yy)
                                    
                            if(abs_btn.Button_dict['state']==True):
                                ylimits=ax.set_ylim()
                                #ax.set_ylim(0,ylimits[1])
                                y=abs(y)
                                #y = butter_lowpass_filter(y, 1000, fs, 2)
                            if(callback.logflag):
                                callback.absflag=False
                                callback.abs_on(1) # ensure ABS is on
                                ylimits=ax.set_ylim()
                                ax.set_ylim(0,ylimits[1])
                                for indexy in range(len(y)):
                                    if y[indexy]==0:
                                        y[indexy]=0.5/1024
                                y=np.abs(np.log(np.abs(y)))                            
                            if(callback.savenext):
                                #wb = Workbook(write_only=True)
                                #ws = wb.create_sheet()
                                i=1
                                data=[]
                                for index in range(len(t)):
                                    data.append([t[index],y[index]])
                                filenametouse=nextfilename(savename+'.csv')
                                np.savetxt(filenametouse,data,fmt='%f', delimiter=',',header=saveheader)
                                callback.savenext=False
                            if(callback.mem_storeflag==True):
                                callback.memory=y
                                callback.mem_storeflag=False



                        if (callback.Function==1): 
                            ax.set_xlim(callback.DelayValue,callback.DelayValue+fixed_duration)
                        elif (callback.Function==2):
                            ax.set_xlim(0,fixed_duration)
                        elif (callback.Function==3):
                            ax.set_xlim(callback.DelayValue,callback.DelayValue+fixed_duration)        
                        elif (callback.Function==4):
                            ax.set_xlim(callback.DelayValue,callback.DelayValue+fixed_duration)

                        if ((callback.CurrentChannel &1)==1):                           
                            tlast=t;
                            ylast=y;
                        if (callback.Function==4):
                            if ((callback.CurrentChannel & 2) ==2):
                                line1.set_ydata(Rxy)
                                line1.set_xdata(t)
                                line2.set_ydata([-99])
                                line2.set_xdata([0])
                                line1.set_color("white")
                                fig.canvas.draw()
                        else:
                            if ((callback.CurrentChannel &1)==1):                           
                                line1.set_ydata(y)
                                line1.set_xdata(t)
                                line1.set_color("white")
                                tlast=t;
                                ylast=y;
                                if ((callback.Channel) !=3):
                                    # only redraw if no 2nd line to redraw
                                    fig.canvas.draw()
                                
                            if ((callback.CurrentChannel & 2) ==2):                           
                                line2.set_ydata(y)   
                                line2.set_xdata(t)
                                line2.set_color("blue")
                                line1.set_ydata([-99])
                                if ((callback.Channel) ==3):
                                    line1.set_ydata(ylast)
                                    line1.set_xdata(tlast)
                                    line1.set_color("white")
                                fig.canvas.draw()
                           
                        
                        fig.canvas.flush_events()
                        plt.pause(.00001)

                    else:
                        fig.canvas.draw_idle()
                        fig.canvas.flush_events()
                        #print(duration_micro,SamplesTaken,Samples,Nbits,Scaled_duration_micro)
                        #print('CRC',crc,intcrc,localcrc,oldlocalcrc,intcrc==localcrc)   
                        heartbeatio.flush()
                        time.sleep(.1) 
                        #print("flushed") 
        if(callback.CurrentChannel!=callback.Channel):
           #pas:
           if(callback.Channel==1):
               pass
               line2.set_ydata(-99) # remove other line
                                  #pass
           if(callback.Channel==2):
               pass
               line1.set_ydata(-99) # remove other line
           callback.CurrentChannel=(callback.CurrentChannel)%2 +1  # toggles the channel
           setchannel(callback.CurrentChannel)
    return

def onclick(event):
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))

def beforeclose(event):
    global exitflag
    exitflag=True
    fig.canvas.draw_idle()
    
def handle(event):
    global exitflag
    #if event.key == 'r':
    #    update(heartbeatio)
    if event.key == 'escape':
        #print('EXIT FLAG SET')
        exitflag=True
    fig.canvas.draw_idle()

def setchannel(channel_num):
    ind = max(min(channel_num,2),1)
    string='c'+str(ind)+';'#).encode()
    heartbeatserial(string)  # send as bytes
    if (VERBOSE_FLAG): print(string)
    heartbeatio.flush()
    time.sleep(.1) # wait 
    return

def fourier(y3):
    NN=1024
    ffty = np.fft.fft(y3)/(NN)  # 1 / NN is a normalization factor
    MM=ffty.size
    parea=np.sum(np.abs(ffty)**2)
    ypower=np.std(y3)**2+np.mean(y3)**2
    return ffty
        


def selectFromDict(options, name):

    index = 0
    indexValidList = []
    print('Select a ' + name + ':')
    for optionName in options:
        index = index + 1
        indexValidList.extend([options[optionName]])
        print(str(index) + ') ' + optionName)
    inputValid = False
    while not inputValid:
        inputRaw = input(name + ': ')
        inputNo = int(inputRaw) - 1
        if inputNo > -1 and inputNo < len(indexValidList):
            selected = indexValidList[inputNo]
            print('Selected ' +  name + ': ' + selected)
            inputValid = True
            break
        else:
            print('Please select a valid ' + name + ' number')
    
    return selected

  
if __name__ == "__main__":
    ValidSerial=True
    verbosegbl=False
    COMValid=True
    BaudRate=115200
    Nmax=1024
    Vmax=5 # Vref of Arduino
    plt.ion() # turn on interactive mode
    plt.rcParams['toolbar'] = 'None'
    UWA_LOGO = mpimg.imread(ospath.join('images','UWA-Full-Ver-CMYK3.png'))

        
    frontpanel=panel()

    
    Portslist= findSerialPorts.serial_ports()
    #print('USBs=',Portslist)
    USBdev=[s for s in Portslist if 'COM' in s] 
    #print('USBs=',USBdev,len(USBdev))
    options = {}
    if(len(USBdev)==0):
        frontpanel.about('Error: Could not find a valid SERIAL port for Adri/Ardu-Scope')
        axclosebtn=plt.axes([0.5, .96, 0.08,.04],facecolor='r')
        #axclosebtn.set_frame_on(True)
        closebtn=Button(axclosebtn,label='CLOSE',color='r',hovercolor='.5')
        callingfunction=lambda localevent_x: (gracefulexit())
        closebtn.on_clicked(quit)
        input()

 
    else:
        if(len(USBdev)==1):
            option=USBdev[0]
        else:
            option = selectFromDict(USBdev, 'USB Port')
        # if here then a valid port was found
        heartbeat_Connect=option
        heartbeatio = serial.Serial(heartbeat_Connect,BaudRate,timeout=1) #115200 19200
        flushheartbeatserial()
        time.sleep(1) # wait 

        tlast=[];
        ylast=[];
        fig, ax = plt.subplots(figsize=(10,4))
        fig.canvas.set_window_title("Adri/ArduScope (Version: "+str(__version__)+") - by Dr. Adrian Keating at The University of Western Australia")
        ax.grid(True)
        ax.grid(color='k', ls = ':', lw = 1)
        ax.set_facecolor('xkcd:green') #
        scrnY=0.95
        scrnX=0.65
        Y0=0.15
        X0=0.05
        plt.subplots_adjust(bottom=Y0,top=scrnY,left=X0,right=scrnX)
        plt.title('RealTime Adri/Ardu-Scope: <ESC> to exit')
        plt.xlabel('Time (ms)')
        plt.ylabel('Voltage (V)')
        plt.ylim( ymin = 0)
        btnax=plt.axes([.79, 0, .3,.5])
        bttn=Button(btnax,label='',image=UWA_LOGO )
        bttn.on_clicked(lambda event:frontpanel.about())
        btnax2=plt.axes([.89, .5, .1,.1])
        bttn2=Button(btnax2,label='About')
        bttn2.on_clicked(lambda event:frontpanel.about())
        btnax.set_frame_on(False)
    
        line1, = ax.plot([0],[0])#,'w-')                       
        line2, = ax.plot([0],[0])#, 'b-') # Returns a tuple of line objects, thus the comma 
        exitflag=False
        fig.canvas.mpl_connect('key_press_event', handle)
        fig.canvas.mpl_connect('close_event', beforeclose)
        heartbeatio.write('d0;c1;f3;R1;'.encode())  # send as bytes
        time.sleep(.1)

        i=0              
        fn=lambda xx: (print("Click ING .....!"),print('state=',xx))
        frontpanel.X0=.6
        frontpanel.Y0=.9
        Amp_btn=scope_button()
        Amp_btn.X0=.67
        Amp_btn.Y0=.8
        kk=30
        Avalues=[frontpanel.Amp*(1-(i/kk)) for i in range(kk)]
        Amp_btn.add_dblbutton(frontpanel.SetAmp,'Amplitude (V)',direction='vertical',values=Avalues)
        Offset_btn=scope_button()
        Offset_btn.X0=Amp_btn.X0
        Offset_btn.Y0=Amp_btn.Y0
        Ovalues=[frontpanel.Offset+frontpanel.Amp*(i-kk//2)/kk for i in range(kk)]
        Offset_btn.add_dblbutton(frontpanel.SetOffset,'Offset (V)',direction='vertical',values=Ovalues,initalindex=kk//2)      

        
        panel_Btns=scope_button()
        ac_btn=scope_button()
        #print(frontpanel.__dict__)
        ac_btn.X0=Offset_btn.X0
        ac_btn.Y0=Offset_btn.Y0
        ac_btn.addbutton(cmd=frontpanel.ac_on,label='AC')
        abs_btn=scope_button()
        abs_btn.X0=ac_btn.X0
        abs_btn.Y0=ac_btn.Y0
        abs_btn.addbutton(cmd=frontpanel.abs_on,label='ABS()')
        axcolor = 'y'
        mem_store = plt.axes([abs_btn.X0-0.005, abs_btn.Y0-0.005, .085, 0.05], facecolor=axcolor)
        mem_store_Btn = Button(mem_store,label='STORE CH1', color='white', hovercolor='grey')
        mem_store_Btn.on_clicked(frontpanel.mem_store)

        save_on = plt.axes([abs_btn.X0-0.005, abs_btn.Y0-0.075, .085, 0.05], facecolor=axcolor)
        save_onBtn = Button(save_on,label='SAVE', color='white', hovercolor='grey')
        save_onBtn.on_clicked(frontpanel.save_on)

        
        H=len(Functions)*scrnY/12
        W=.15
        Xc=scrnX+0+.07
        Yc=scrnY-H*1
        Fnax = plt.axes([Xc, Yc, W, H], facecolor=axcolor,frame_on=False)
        Fnradio = RadioButtons(Fnax, Functions.keys())
        Fnradio.on_clicked(frontpanel.SetFunction) 
        #H=H*3/4
        ax_separator= plt.axes([Xc, Yc, W, H/20], facecolor=axcolor,frame_on=False)
        ax_separator.set_frame_on(False)
        Button(ax_separator,label='-----------------------')
        W=.1
        H=len(ChannelOptions)*scrnY/12
        Yc=scrnY-H*2-H/5
        Xc=Xc+W/10
        Chax = plt.axes([Xc, Yc, W, H], facecolor=axcolor,frame_on=False)
        Chradio = RadioButtons(Chax, ChannelOptions.keys())
        Chradio.on_clicked(frontpanel.SetChannel)
        #Chax.set_frame_on(False)
        ax_separator= plt.axes([Xc, Yc, W, H/20], facecolor=axcolor,frame_on=False)
        ax_separator.set_frame_on(False)
        Button(ax_separator,label='----------------')
        
        Time_btn=scope_button()
        Time_btn.X0=Xc+.05
        Time_btn.Y0=Yc-H/2
        Tvalues=frontpanel.ValidTimebaseValue #[frontpanel.TimebaseMultiples*(i+1) for i in range(10)]
        Time_btn.add_dblbutton(frontpanel.Timebase,'Timebase (ms)',values=Tvalues,initalindex=3)
        Delay_btn=scope_button()
        Delay_btn.X0=Time_btn.X0
        Delay_btn.Y0=Time_btn.Y0
        #Delay_btn.add_dblbutton(fn,'Delay (ms)')
        Dvalues=[frontpanel.DelayMultiples*(i)*100 for i in range(50)]
        Delay_btn.add_dblbutton(frontpanel.Delay,label='Delay (micros)',values=Dvalues)
  
        btnax=plt.axes([.79, 0, .3,.5])
        bttn=Button(btnax,label='',image=UWA_LOGO )
        bttn.on_clicked(lambda event:frontpanel.about())
        btnax2=plt.axes([.89, .5, .1,.1])
        bttn2=Button(btnax2,label='About')
        bttn2.on_clicked(lambda event:frontpanel.about())
        btnax.set_frame_on(False)
        while(exitflag==False):
            if(frontpanel.shwoabout==False):
                updateplot(i)
                heartbeatio.write('R1;'.encode())  # send as bytes
                fig.canvas.draw_idle()
            time.sleep(.01)
            i+=1
        gracefulexit()     
        flushheartbeatserial()  # remove any unread data
        heartbeatstop()
        heartbeatio.close()
 
        

   
