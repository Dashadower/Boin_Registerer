# -*- coding:utf-8 -*-
from tkinter import Label,Button,Frame,StringVar,Entry,Menu,IntVar,DoubleVar, Text,Scrollbar, Scale
from tkinter.constants import *
from tkinter.messagebox import showinfo,showerror,showwarning
from tkinter.messagebox import askyesno
import tkinter.tix as tix, datetime, time
import requests,bs4,ast,urllib
from webbrowser import open as webopen
# Some common data structures
# Session(방과후학교, 동아리 등 구별): (session_type,session_id,session_opt)
#                                       (1,128,8182)
# Class ("사진반, 국어 탐구): (class_type,class_id,class_opt)
#                             (1,8254,3)
# You need to know the session_id to get the info link
# Link :"?club=index&action=view&db=1701&page=1&cate=%s&cls=&sort=rate&uid=%s"%(session_id,class_id)




# The actual register handler:
# Once you get to the lecture page, it sends a POST request with action="?"
# POST Parameters
# (name | value)
# club | index
# action | ment
# form_chk | ment
# uid | (class_id)
# num |
# inum | 0
# type | 강좌
# act |
# re | 3
# db | 1701
# mode |
# cate | (session_id)
# cls |
# page | 1
# sort | rate
# key |
# key2 |
# s1 |
# s2 |
# s3 |
# s_num | (학번)
# name | (이름)
# memo | (메모글)
################################################################################
#Gui Functions

class LoginScreen(Frame):
    def __init__(self, master,requesthandler):
        clearscreen()
        Frame.__init__(self,master)
        self.pack(expand=YES,fill=BOTH)
        self.master = master
        self.requesthandler = requesthandler
        self.ID = StringVar()
        self.PW = StringVar()
        self.DrawWidgets()
    def DrawWidgets(self):
        Label(self,text="아이디").grid(row=0,column=0)
        Entry(self,textvariable=self.ID).grid(row=0,column=1)
        Label(self,text="비밀번호").grid(row=1,column=0)
        Entry(self,textvariable=self.PW,show="*").grid(row=1,column=1)
        Button(self,text="로그인",command=self.Login_Handler).grid(row=2,column=1)
        Button(self,text="보인아이",command=lambda:webopen("https://boini.net")).grid(row=2,column=0)
        #Label(self, text="제작자: 보인고 전우회").grid(row=3, column=0, columnspan=2)
        #self.master.after_idle(lambda: showinfo("","로그인하기 전\n1.브라우저에도 기기등록이 되어있는지 확인해주세요(동시에 기기등록이 안됩니다)\n2.로그인을 하면 최소 1분이 지나 기기등록 해제가 되고, 그때가 되서야 브라우저에서 접속이 가능해집니다.\n\n위 내용을 숙지하시기 바랍니다."))
    def Login_Handler(self):
        if self.ID.get() and self.PW.get():
            if self.requesthandler.Login(self.ID.get(),self.PW.get()):
                SeasonScreen(self.master,self.requesthandler)
        else:
            showerror("","아이디와 비밀번호를 입력해 주세요.")

class SeasonScreen(Frame):
    def __init__(self, master,requesthandler):
        clearscreen()
        Frame.__init__(self,master)
        self.master = master
        self.pack(expand=YES,fill=BOTH)
        self.requesthandler = requesthandler

        self.seasons = self.requesthandler.GetSeasons()
        list_increment = 0
        for items in self.seasons:

            Button(self,text=items[0],command=lambda items=items:self.SelectLecture(items)).grid(row=list_increment,column=0)

            list_increment += 1

        Button(self, text="사용법", fg="yellow", bg="black" ,command=lambda: ShowTutorial()).grid(row=list_increment, column=0)
        Button(self,text="Debug",command=lambda: DebugWindow(self.master,self.requesthandler)).grid(row=list_increment+1,column=0)

    def SelectLecture(self,lecture_info):
        self.requesthandler.RegisterPC(lecture_info[1][1])
        SeasonInfoScreen(self.master,self.requesthandler,lecture_info)

def ShowTutorial():
    showinfo("사용법", """
이 프로그램은 여러분들의 용이한 방과후,동아리, 등의 신청을 위해 개발했습니다.
현재 수동신청과 자동신청 두가지가 있습니다.
수동신청은 본인이 직접 클릭해서 신청하는 것이고, 자동신청은 일정한 시간에 컴퓨터가 자동으로 신청합니다(현재 한가지 강좌만 지원가능)
방과후학교 목록에 들어간 후, 상단에 있는 "본인정보 등록"을 눌러 이름과 학번을 입력하신 후, 자동신청을 사용하실 분들은 옆에 있는
"자동등록 설정"을 눌러 신청을 원하는 시간을 입력한 후, 강좌의 목록중 희망하시는 강좌의 "바로신청" 또는 자동신청을 누르시면 됩니다.
    """)
class DebugWindow(Frame):
    def __init__(self, master,requesthandler):
        clearscreen()
        Frame.__init__(self,master)
        self.pack(expand=YES,fill=BOTH)
        self.master = master
        self.requesthandler = requesthandler
        self.PyCommand = StringVar()
        self.PyCommand.set("Custom PyCommand")
        Button(self, text="back", command=lambda: SeasonScreen(self.master, self.requesthandler)).grid(row=0,column=1)
        Entry(self,textvariable=self.PyCommand).grid(row=1,column=0)
        Button(self,text="Run",command=lambda: exec(self.PyCommand.get())).grid(row=1,column=1)
class SeasonInfoScreen(Frame):
    def __init__(self, master,requesthandler,SeasonInfo):
        clearscreen()
        Frame.__init__(self,master)
        self.pack(expand=YES,fill=BOTH)
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW",on_close)
        self.requesthandler = requesthandler
        self.SeasonInfo = SeasonInfo  # (seasonname, season info tuple)
        self.Session_ID = self.SeasonInfo[1]  # season info tuple
        self.checkincrement = IntVar()
        self.checkincrement.set(120)
        self.devicecheckcount = IntVar()
        self.devicecheckcount.set(0)
        self.AutoRegisterEnabled = False
        self.ServerTimeOffset = datetime.timedelta(0,0,0)
        self.RequestLatency = DoubleVar()
        OptionFrame = Frame(self)
        OptionFrame.pack(side=TOP,fill=X)
        Button(OptionFrame,text="뒤로",command=lambda:SeasonScreen(self.master,self.requesthandler)).pack(side=RIGHT)
        Label(OptionFrame,text=self.SeasonInfo[0]+" "+str(SeasonInfo[1])).pack(anchor=W,fill=X)

        self.PopulateClass()
    def PopulateClass(self):



        TopFrame_ = tix.ScrolledWindow(self,scrollbar=Y)
        TopFrame_.pack(expand=YES,fill=BOTH)
        self.TopFrame = TopFrame_.window



        response = self.requesthandler.GetClassList(self.SeasonInfo[1][1])
        if not "수강신청용" in response:
            showerror("","기기등록에 실패했습니다. 이는 주로 기기등록을 한지 1분도 안지나고 다시 기기등록을 시도하면 발생합니다. 1분 경과후 재시도해주세요.(request error)")
        else:
            myMenu = Menu(self.master)
            myMenu.add_command(label="본인정보 등록",command=self.AddPersonalInfo)
            myMenu.add_command(label="자동등록 설정",command=self.OnAutomate)
            myMenu.add_command(labe="큰 시계보기",command=self.ShowClock)
            self.Student_Name = StringVar()
            self.Student_ID = StringVar()
            self.AutoRegisterTime = IntVar()
            self.AutoRegisterInfo = StringVar()
            self.AutoRegisterInput = StringVar()
            #self.AutoRegisterList = {}
            self.Memo = StringVar()
            self.master.config(menu=myMenu)
            soup = bs4.BeautifulSoup(response,"html.parser")
            classes = []
            table = soup.find("table",{"class":"table_box"})

            rows = table.findAll("tr")
            for row in rows:
                vars = []
                cols = row.findAll("td")
                if row.find("a"):
                    vars.append(row.find("a").get("href"))
                else: vars.append(None)
                for items in cols:
                    vars.append(items.text.strip())
                classes.append(vars)

            classes.pop(0)
            class_increment = 1

            Label(self.TopFrame,text="순번").grid(row=0,column=0)
            Label(self.TopFrame,text="학년").grid(row=0,column=1)
            Label(self.TopFrame,text="[선택군] 강좌 이름(내부 강좌 코드)").grid(row=0,column=2)
            Label(self.TopFrame,text="담당교사").grid(row=0,column=3)
            Label(self.TopFrame,text="신청/정원").grid(row=0,column=4)
            Label(self.TopFrame,text="수강료").grid(row=0,column=5)
            Label(self.TopFrame,text="바로신청").grid(row=0,column=6)
            Label(self.TopFrame,text="자동신청").grid(row=0,column=7)
            jsvalue = []

            for class_info in classes:

                if class_increment == 2:print(class_info)

                if int(class_info[5].split("/")[0]) >= int(class_info[5].split("/")[1]):
                    open_state = False
                else: open_state = True
                Label(self.TopFrame,text=class_info[1]).grid(row=class_increment,column=0)
                Label(self.TopFrame,text=class_info[2]).grid(row=class_increment,column=1)
                Label(self.TopFrame,text=class_info[3]+" ("+str(ast.literal_eval(class_info[0].split("bL")[1])[1] if class_info[0] != None else "None")+")").grid(row=class_increment,column=2)
                Label(self.TopFrame,text=class_info[4]).grid(row=class_increment,column=3)
                Label(self.TopFrame,text=class_info[5],fg="blue" if open_state else "red").grid(row=class_increment,column=4)
                Label(self.TopFrame,text=class_info[6]).grid(row=class_increment,column=5)
                jsvalue.append((ast.literal_eval(class_info[0].split("bL")[1]) if class_info[0] else None,class_increment-1))
                Button(self.TopFrame,text="바로신청" if open_state else "마감",fg="blue" if open_state else "red",state=NORMAL if open_state else DISABLED,command=lambda class_increment=class_increment:self.RegisterClass(jsvalue[class_increment-1])).grid(row=class_increment,column=6)
                Button(self.TopFrame, text="자동신청" if open_state else "마감", fg="blue" if open_state else "red", state=NORMAL if open_state else DISABLED,
                       command=lambda class_increment=class_increment: self.AutoRegisterClass(jsvalue[class_increment - 1],classes[class_increment-1])).grid(row=class_increment, column=7)
                class_increment += 1

            showwarning("","신청에 성공했다고 하여도 프로그램 종료 후, 브라우저에서 보인아이에 접속하여 정상적으로 신청되었는지 꼭 확인해주세요.")
    def nothing(self):
        pass

    def ShowClock(self):
        self.SetServerTimeOffset()
        clockwindow = tix.Toplevel()

        clockwindow.resizable(0,0)
        tix.Label(clockwindow, text="현재 보인아이 시간").pack()
        clocklabel = Label(clockwindow, text="00:00:00", font=("TkDefaultFont", 50, "bold"))
        clocklabel.pack(expand=YES, fill=BOTH)
        clockwindow.update_idletasks()
        fontscale = Scale(clockwindow,label="글자크기",from_=10, to=200, orient=HORIZONTAL, resolution=10)
        fontscale.pack(fill=Y,anchor=S)
        fontscale.set(50)
        fontscale.bind("<ButtonRelease-1>",lambda x: self.UpdateStandaloneClock(clocklabel, fontscale))
        clocklabel.after(100, self.UpdateBoiniClock(clocklabel))

    def UpdateStandaloneClock(self, clocklabel, fontscale):
        clocklabel.config(font=("TkDefaultFont", fontscale.get(), "bold"))

    def AddPersonalInfo(self):

        Register_window = tix.Toplevel(self.master)
        Register_window.grab_set()
        Register_window.resizable(0,0)

        Label(Register_window,text="이름").grid(row=0,column=0)
        Label(Register_window,text="학번").grid(row=1,column=0)
        Label(Register_window,text="메모").grid(row=2,column=0)
        Entry(Register_window,textvariable=self.Student_Name).grid(row=0,column=1)
        Entry(Register_window,textvariable=self.Student_ID).grid(row=1,column=1)
        Entry(Register_window,textvariable=self.Memo).grid(row=2,column=1)
        Register_window.columnconfigure(0,weight=1)
        Register_window.columnconfigure(0,weight=1)
        Label(Register_window,text="이름과 학번은 어떻게 치든 본인걸로 등록됩니다.",foreground="red").grid(row=3,column=0,columnspan=2)
        Button(Register_window,text="닫기",command=lambda:Register_window.destroy()).grid(row=4,column=0,columnspan=2)

    def OnAutomate(self):
        Register_window = tix.Toplevel(self.master)
        Register_window.grab_set()
        Register_window.resizable(0, 0)
        clocklabel =  Label(Register_window,text="현재 이 컴퓨터의 시간: %s:%s:%s"%(str(datetime.datetime.now().hour).rjust(2,"0"), str(datetime.datetime.now().minute).rjust(2,"0"),str(datetime.datetime.now().second).rjust(2,"0")))
        boini_clock_label = Label(Register_window,text="현재 보인아이 홈페이지의 시간: (동기화 중...잠시만 기다려주세요)")
        clocklabel.grid(row=0,column=0,columnspan=2)
        boini_clock_label.grid(row=1, column=0, columnspan=2)
        clocklabel.after(500, lambda: self.UpdateOnAutomateClock(clocklabel, True))
        boini_clock_label.after(1000, lambda: self.GetServerTime(boini_clock_label))
        Label(Register_window,text="등록시작을 원하는 시간을 현재 보인아이의 시간을 기준으로 24시간:분:초 형식으로 입력해주세요\n(예:8시부터 신청을 원하면 20:00:00). 이 사간부터 프로그램은 될때까지 등록을 계속 합니다.").grid(row=2,column=0,columnspan=2)
        Label(Register_window, text="시간(24시간 형식):분:초").grid(row=3, column=0)
        timeentry = Entry(Register_window,textvariable=self.AutoRegisterInput)
        timeentry.grid(row=3, column=1)
        timeentry.bind("<KeyRelease>",self.OnAutomateCallBack)
        #Button(Register_window, text="설정하기", command= lambda: self.OnAutomateCallBack("event")).grid(row=3, column=0, columnspan=2)
        Label(Register_window, textvariable=self.AutoRegisterInfo).grid(row=4,column=0,columnspan=2)
        Button(Register_window, text="닫기", command=lambda: Register_window.destroy()).grid(row=5, column=0, columnspan=2)

    def UpdateBoiniClock(self, labelwidget, user_friendly=False):
        if labelwidget.winfo_exists():
            ct = datetime.datetime.now() - self.ServerTimeOffset
            if user_friendly:
                labelwidget.config(text="현재 보인아이 홈페이지의 시간: %s:%s:%s" % (
                str(ct.hour).rjust(2, "0"), str(ct.minute).rjust(2, "0"), str(ct.second).rjust(2, "0")))
            else:
                labelwidget.config(text="%s:%s:%s" % (
                    str(ct.hour).rjust(2, "0"), str(ct.minute).rjust(2, "0"), str(ct.second).rjust(2, "0")))
            #self.master.update()
            labelwidget.after(100, lambda: self.UpdateBoiniClock(labelwidget, user_friendly))

    def SetServerTimeOffset(self):
        starttime = time.time()
        testreq = requests.get("http://boini.net")
        endtime = time.time()
        latency = round(endtime - starttime, 2)
        self.RequestLatency.set(latency)
        dateparam = testreq.headers["Date"]
        dtval = datetime.datetime.strptime(dateparam, '%a, %d %b %Y %H:%M:%S GMT') + datetime.timedelta(0, 3600 * 9, 0)
        server_time_with_latency = dtval + datetime.timedelta(0, latency, 0)
        timediff = datetime.datetime.now() - server_time_with_latency
        self.ServerTimeOffset = timediff

    def GetServerTime(self, labelwidget):
        if labelwidget.winfo_exists():
            starttime = time.time()
            testreq = requests.get("http://boini.net")
            endtime = time.time()
            latency = round(endtime-starttime, 2)
            self.RequestLatency.set(latency)
            dateparam = testreq.headers["Date"]
            dtval = datetime.datetime.strptime(dateparam, '%a, %d %b %Y %H:%M:%S GMT') + datetime.timedelta(0,3600*9,0)
            server_time_with_latency = dtval + datetime.timedelta(0, latency,0)
            timediff = datetime.datetime.now() - server_time_with_latency
            self.ServerTimeOffset = timediff
            ct = datetime.datetime.now() - timediff
            print("latency:",latency)
            print("Date Header:", dateparam)
            print("dtval:", dtval)
            print("timediff:", timediff)
            print("ct:", ct)
            labelwidget.config(text="현재 보인아이 홈페이지의 시간: %s:%s:%s"%(str(ct.hour).rjust(2,"0"), str(ct.minute).rjust(2,"0"),str(ct.second).rjust(2,"0")))
            #self.master.update()
            labelwidget.after(100,lambda: self.UpdateBoiniClock(labelwidget, True))

    def UpdateOnAutomateClock(self,labelwidget, user_friendly=False):
        if labelwidget.winfo_exists():
            if user_friendly:
                labelwidget.config(text="현재 이 컴퓨터의 시간: %s:%s:%s"%(str(datetime.datetime.now().hour).rjust(2,"0"), str(datetime.datetime.now().minute).rjust(2,"0"),str(datetime.datetime.now().second).rjust(2,"0")))
            else:
                labelwidget.config(text="%s:%s:%s" % (
                str(datetime.datetime.now().hour).rjust(2, "0"), str(datetime.datetime.now().minute).rjust(2, "0"),
                str(datetime.datetime.now().second).rjust(2, "0")))
            #self.master.update()
            labelwidget.after(100, lambda: self.UpdateOnAutomateClock(labelwidget, user_friendly))
    def OnAutomateCallBack(self,event):
        self.master.update_idletasks()
        hourvar, minutevar, secondvar = IntVar(), IntVar(), IntVar()
        data = self.AutoRegisterInput.get()
        try:
            hour, minute, second = data.split(":")
        except ValueError:
            self.AutoRegisterInfo.set("올바르지 않은 시간 형식입니다.")
        else:
            if hour.isdigit() and minute.isdigit() and second.isdigit():
                newtime = datetime.datetime.now() - self.ServerTimeOffset
                newtime = newtime.replace(hour=int(hour),minute=int(minute),second=int(second))

                offset = newtime - (datetime.datetime.now() - self.ServerTimeOffset)
                offhours,r1 = divmod(offset.seconds,3600)
                offminutes, offseconds = divmod(r1,60)
                self.AutoRegisterInfo.set("시작시간: %s시 %s분 %s초 (%d시간 %d분 %d초 후) 으로 설정되었습니다."%(hour,minute,second,offhours,offminutes,offseconds))
                self.AutoRegisterTime.set(time.mktime(newtime.timetuple()))
            else:
                self.AutoRegisterInfo.set("올바르지 않은 시간 형식입니다.")
    def AutoRegisterClass(self,Class_Tuple,class_info):
        if Class_Tuple[0] == None:
            showerror("","해당 학년이 아닙니다")
        else:
            if not self.Student_Name.get():
                self.AddPersonalInfo()
                showinfo("","학생정보 및 메모를 입력해주세요.")
            #Button(Register_window,text="등록",command=lambda:self.RegisterClass_handler(Class_Tuple,self.Student_Name.get(),self.Student_ID.get(),self.Memo.get())).grid(row=4,column=0,columnspan=2)
            else:
                if not self.AutoRegisterTime.get():
                    self.OnAutomate()
                    showinfo("","신청시간을 설정해주세요.")
                else:
                    if self.AutoRegisterEnabled:
                        showinfo("","자동등록은 현재 한가지 강좌만 지원됩니다.")
                    else:
                        self.AutoRegisterClass_handler(Class_Tuple,class_info)

    def CheckAutoRegister(self,mainwindow, statuslabel, infotext, ctuple):
        ctime = time.mktime((datetime.datetime.now()-self.ServerTimeOffset).timetuple())
        if mainwindow.winfo_exists():
            if ctime >= self.AutoRegisterTime.get():
                statuslabel.config(text="신청중")
                infotext.config(state=NORMAL)
                infotext.insert(END, "신청 시도중...\n")
                infotext.see(END)
                infotext.config(state=DISABLED)
                res = self.requesthandler.RegisterClass(self.Session_ID[1], ctuple[1], ctuple[0], self.Student_ID.get(),self.Student_Name.get(),self.Memo.get())
                if not res:
                    mainwindow.focus_force()
                    statuslabel.config(text="신청완료",fg="green")
                    infotext.config(state=NORMAL)
                    infotext.insert(END, "신청이 완료되었습니다. 브라우저에서 보인아이를 확인해주세요\n")
                    infotext.see(END)
                    infotext.config(state=DISABLED)
                else:
                    mainwindow.focus_force()
                    statuslabel.config(text="신청실패",fg="red")
                    infotext.config(state=NORMAL)
                    infotext.insert(END, "신청에 실패했습니다. 바로신청을 통해 다시 신청을 시도해보거나, 브라우저를 통해 접속해주세요. (오류 내용 첨부)\n")
                    infotext.insert(END,res+"\n")
                    infotext.see(END)
                    infotext.config(state=DISABLED)
            else:
                if self.checkincrement.get() == 0:
                    infotext.config(state=NORMAL)
                    infotext.insert(END, "기기 등록상태 확인중(%d)..."%(self.devicecheckcount.get()))
                    self.devicecheckcount.set(self.devicecheckcount.get()+1)
                    infotext.see(END)
                    infotext.config(state=DISABLED)
                    info = self.requesthandler.GetClassList(self.Session_ID[1])
                    if "기기등록이 필요합니다" in info:
                        infotext.config(state=NORMAL)
                        infotext.insert(END, "만료됨\n")
                        infotext.insert(END, "기기 재등록중...")
                        infotext.see(END)
                        infotext.config(state=DISABLED)
                        self.requesthandler.RegisterPC(self.SeasonInfo[0])
                        infotext.config(state=NORMAL)
                        infotext.insert(END, "완료\n")
                        infotext.see(END)
                        infotext.config(state=DISABLED)
                    else:
                        infotext.config(state=NORMAL)
                        infotext.insert(END, "정상\n")
                        infotext.see(END)
                        infotext.config(state=DISABLED)
                    self.checkincrement.set(120)
                else:
                    self.checkincrement.set(self.checkincrement.get()-1)
                statuslabel.after(500, lambda: self.CheckAutoRegister(mainwindow,statuslabel,infotext,ctuple))

    def OnAutoWindowClose(self,window):
        self.AutoRegisterEnabled = False
        self.devicecheckcount.set(0)
        self.checkincrement.set(120)
        window.destroy()
    def AutoRegisterClass_handler(self,Class_Tuple,Class_Info):
        Waitwindow = tix.Toplevel()
        Waitwindow.title("자동 신청 - %s"%(Class_Info[3]))
        Waitwindow.resizable(0,0)
        self.AutoRegisterEnabled = True
        Waitwindow.protocol("WM_DELETE_WINDOW",lambda:self.OnAutoWindowClose(Waitwindow))
        Label(Waitwindow,text="강좌이름").grid(row=0,column=0)
        Label(Waitwindow,text=Class_Info[3]).grid(row=0,column=1)
        Label(Waitwindow,text="현재 보인아이 시간").grid(row=1,column=0)
        literal = "%d:%d:%d"%(datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second)
        clocklabel = Label(Waitwindow, text=literal)
        clocklabel.grid(row=1, column=1)
        clocklabel.after(500, lambda: self.UpdateBoiniClock(clocklabel))
        Label(Waitwindow, text="자동신청 시간").grid(row=2,column=0)
        Label(Waitwindow, text="%s"%(time.strftime("%H:%M:%S",time.localtime(self.AutoRegisterTime.get())))).grid(row=2, column=1)
        Label(Waitwindow, text="상태").grid(row=3, column=0)
        statuslabel = Label(Waitwindow,text="대기중",fg="green")
        statuslabel.grid(row=3,column=1)
        Label(Waitwindow, text="기기등록 확인").grid(row=4,column=0)
        Label(Waitwindow, textvariable=self.checkincrement).grid(row=4,column=1)
        textframe = Frame(Waitwindow)
        textframe.grid(row=5,rowspan=3,column=0,columnspan=2)

        infotext = Text(textframe, borderwidth=1, relief=SUNKEN)
        infotext.pack(side=LEFT,expand=YES,fill=BOTH)
        infotext.insert(END, "자동신청이 이 강좌에 한해 활성화되었습니다. 취소하려면 이 창을 끄면 됩니다.\n")
        infotext.insert(END, str(Class_Tuple)+"\n")
        infotext.config(state=DISABLED)

        textscroll = Scrollbar(textframe,command=infotext.yview)
        textscroll.pack(side=RIGHT,fill=Y)
        infotext.config(yscrollcommand=textscroll.set)
        self.devicecheckcount.set(0)
        root.after(500,lambda: self.CheckAutoRegister(Waitwindow,statuslabel,infotext, Class_Tuple))
    def RegisterClass(self,Class_Tuple):
        if Class_Tuple[0] == None:
            showerror("","해당 학년이 아닙니다")
        else:
            if not self.Student_Name.get():
                self.AddPersonalInfo()
                showinfo("","학생정보 및 메모를 입력해주세요.")
            #Button(Register_window,text="등록",command=lambda:self.RegisterClass_handler(Class_Tuple,self.Student_Name.get(),self.Student_ID.get(),self.Memo.get())).grid(row=4,column=0,columnspan=2)
            else:
                self.RegisterClass_handler(Class_Tuple,self.Student_Name.get(),self.Student_ID.get(),self.Memo.get())
    def RegisterClass_handler(self,Class_Tuple,Name,ID,Memo):
        if Name and ID:
            if askyesno("","이대로 강좌를 신청할까요?"):

                res = self.requesthandler.RegisterClass(self.Session_ID[1],Class_Tuple[1],Class_Tuple[0],ID,Name,Memo)
                if not res:
                    showinfo("","등록이 완료되었습니다.혹시 모르니 보인아이 홈페이지에서 등록이 되어있는지 한번 더 확인해주세요.")

                else:
                    showinfo("","등록을 실패했습니다. 혹시 모르니 보인아이 홈페이지에서 등록이 되어있는지 확인해주세요.\n오류내용:\n"+str(res))
        else:
            showwarning("","이름,학번를 입력해주세요")


################################################################################
#Web Request Handlers
class BoinWebHandler():
    def __init__(self):
        self.HomeURL = "https://boini.net/home.php"
        self.LoginURL = "https://boini.net/user.php"
        self.afterschoolmainURL = "https://boini.net/lecture.php?club=index&db=1701&action=idx&cate=undefined"
        self.RegisterURL = "https://boini.net/lecture.php?action=device&db=1701&confirm=%s&cate=" #(session_id)
        self.UnRegisterURL = "https://boini.net/lecture.php?action=device&act=delete"
        self.LogoutURL = "https://boini.net/user.php?action=user_logout"
        self.ClassList = "https://boini.net/lecture.php?club=index&action=list&db=1701&cate=" #(session_id)
        self.ClassInfoURL = "https://boini.net/lecture.php?club=index&action=view&db=1701&page=1&cate=%s&cls=&sort=rate&uid=%s&inum=%s" #(session_id,class_id,opt)
        self.Session = requests.session()
        self.Session.verify = "cacert.pem"
        self.Session.get(self.HomeURL)
    def Login(self,id,pw):
        self.ID = id
        LoginPayload = {
        "mid": id,
        "mpass": pw,
        "action": "user_login",
        "club":"index",
        "URI": "L2hvbWUucGhw"
        }
        returndata = self.Session.post(self.LoginURL,data=LoginPayload).content.decode()
        if str("아이디가") in str(returndata):
            showerror("","아이디 또는 비밀번호가 틀렸습니다.")
            return False
        else:
            return True
    def GetSeasons(self):
        result = self.Session.get(self.afterschoolmainURL).content.decode()
        soup = bs4.BeautifulSoup(result,"html.parser")
        links = []
        for a in soup.findAll("a",href=True):
            if "https" in str(a):
                st1,tx1 = str(a).split(';')
                st2 = st1.split("bL")[1]
                tx2 = tx1.split("<")[0].split(">")[1].rstrip()

                links.append((tx2,ast.literal_eval(st2)))
        return links
    def RegisterPC(self,season_type):
        self.Session.get(self.RegisterURL%(self.ID)+season_type)
    def UnRegisterPC(self):
        response = self.Session.get(self.UnRegisterURL).content.decode()
        if "1분" in response:
            return "기기가 등록된지 1분 내에는 해제할수 없습니다."
        else: return 0
    def Logout(self):
        self.Session.get(self.LogoutURL)
        return 0
    def GetClassList(self,Session_ID):
        response = self.Session.get(self.ClassList+Session_ID).content.decode()
        return response
    def RegisterClass(self,Session_ID,Class_Order,ClassTuple,Student_ID,Student_Name,memo):
        InfoLink = self.ClassInfoURL%(Session_ID,ClassTuple[1],ClassTuple[2])
        payload = {"club":"index",
        "action":"ment",
        "form_chk":"ment",
        "uid":ClassTuple[1],
        "num":"",
        "inum":Class_Order,
        "type":"강좌",
        "act":"",
        "re":"3",
        "db":"1701",
        "cate":Session_ID,
        "cls":"",
        "page":"1",
        "sort":"rate",
        "key":"",
        "key2":"",
        "s1":"",
        "s2":"",
        "s3":"",
        "s_num":Student_ID,
        "name":Student_Name,
        "memo":memo}
        response = self.Session.post("https://boini.net/lecture.php",data=payload).content.decode()
        if"window.location='?club=index" in response:
            return 0
        else:
            return response


################################################################################
#GUI Utilities
def clearscreen():
    for child in root.winfo_children():
        child.destroy()
def on_close():
    if askyesno("","종료전에 기기 등록해제작업 및 로그아웃을 하시겠습니까?"):
        res = MyRequestHandler.UnRegisterPC()
        if res != 0:
            if askyesno("",str(res)+"\n강제종료 하시겠습니까?"):
                root.destroy()
        else:
            showinfo("","기기등록이 해제되었습니다.")

            MyRequestHandler.Logout()
            showinfo("","로그아웃되었습니다.")

            root.destroy()
def change_title1():
    root.title("누구보다 빠르게")
    root.after(2000, change_title2)
def change_title2():
    root.title("난 남들과는 다르게")
    root.after(2000, change_title1)
if __name__ == "__main__":
    root = tix.Tk()
    root.resizable(0,0)
    root.title("방과후등록을 편리하게~")
    #root.after(1000, change_title1)
    root.maxsize(root.winfo_screenwidth(),root.winfo_screenheight()-150)
    MyRequestHandler = BoinWebHandler()

    LoginScreen(root,MyRequestHandler)

    root.mainloop()
