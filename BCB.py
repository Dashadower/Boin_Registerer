# -*- coding:utf-8 -*-
from tkinter import Label,Button,Frame,StringVar,Entry,Menu
from tkinter.constants import *
from tkinter.messagebox import showinfo,showerror,showwarning
from tkinter.messagebox import askyesno
import tkinter.tix as tix
import requests
import bs4
import ast
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

        #showinfo("","로그인하기 전\n1.브라우저에도 기기등록이 되어있는지 확인해주세요(동시에 기기등록이 되면 안됩니다)\n2.로그인을 하면 1분후에 기기등록 해제가 되고, 그때가 되서야 브라우저에서 접속이 가능해집니다.\n\n위 내용을 숙지하시기 바랍니다.")
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

    def SelectLecture(self,lecture_info):
        self.requesthandler.RegisterPC(lecture_info[1][1])
        SeasonInfoScreen(self.master,self.requesthandler,lecture_info)


class SeasonInfoScreen(Frame):
    def __init__(self, master,requesthandler,SeasonInfo):
        clearscreen()
        Frame.__init__(self,master)
        self.pack(expand=YES,fill=BOTH)
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW",on_close)
        self.requesthandler = requesthandler
        self.SeasonInfo = SeasonInfo
        self.Session_ID = self.SeasonInfo[1]
        OptionFrame = Frame(self)
        OptionFrame.pack(side=TOP,fill=X)
        Button(OptionFrame,text="뒤로",command=lambda:SeasonScreen(self.master,self.requesthandler)).pack(side=RIGHT)
        Label(OptionFrame,text=self.SeasonInfo[0]+" "+str(SeasonInfo[1])).pack(anchor=W,fill=X)

        self.PopulateClass()
    def PopulateClass(self):



        TopFrame_ = tix.ScrolledWindow(self,scrollbar=Y)
        TopFrame_.pack(expand=YES,fill=BOTH)
        TopFrame = TopFrame_.window



        response = self.requesthandler.GetClassList(self.SeasonInfo[1][1])
        if not "수강신청용" in response:
            showerror("","기기등록이 되지 않았거나 다른 학년을 선택했습니다.다른 기기에서 등록한지 1분이 지났나요?(request error)")
            on_close()
        else:
            myMenu = Menu(self.master)
            myMenu.add_command(label="본인정보 등록",command=self.AddPersonalInfo)
            self.Student_Name = StringVar()
            self.Student_ID = StringVar()
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

            Label(TopFrame,text="순번").grid(row=0,column=0)
            Label(TopFrame,text="학년").grid(row=0,column=1)
            Label(TopFrame,text="[선택군] 강좌 이름").grid(row=0,column=2)
            Label(TopFrame,text="담당교사").grid(row=0,column=3)
            Label(TopFrame,text="신청/정원").grid(row=0,column=4)
            Label(TopFrame,text="수강료").grid(row=0,column=5)
            Label(TopFrame,text="상태").grid(row=0,column=6)
            jsvalue = []

            for class_info in classes:

                if class_increment == 2: print(class_info)

                if int(class_info[5].split("/")[0]) >= int(class_info[5].split("/")[1]):
                    open_state = False
                else: open_state = True
                Label(TopFrame,text=class_info[1]).grid(row=class_increment,column=0)
                Label(TopFrame,text=class_info[2]).grid(row=class_increment,column=1)
                Label(TopFrame,text=class_info[3]+" ("+str(ast.literal_eval(class_info[0].split("bL")[1])[1] if class_info[0] != None else "None")+")").grid(row=class_increment,column=2)
                Label(TopFrame,text=class_info[4]).grid(row=class_increment,column=3)
                Label(TopFrame,text=class_info[5],fg="blue" if open_state else "red").grid(row=class_increment,column=4)
                Label(TopFrame,text=class_info[6]).grid(row=class_increment,column=5)
                jsvalue.append((ast.literal_eval(class_info[0].split("bL")[1]) if class_info[0] else None,class_increment-1))
                Button(TopFrame,text="가능" if open_state else "마감",fg="blue" if open_state else "red",state=NORMAL if open_state else DISABLED,command=lambda class_increment=class_increment:self.RegisterClass(jsvalue[class_increment-1])).grid(row=class_increment,column=6)
                class_increment += 1

            showwarning("","주의! 이미 신청 성공한 강좌를 한번더 신청을 시도하면 돌이킬수 없는 오류가 일어날수가 있습니다. 자신이 강좌 명단에 포함되어 있는지 확인한 다음에 신청 다시 해주세요.")
    def nothing(self):
        pass

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
    def RegisterClass(self,Class_Tuple):
        if Class_Tuple[0] == None:
            showerror("","해당 학년이 아닙니다")
        else:
            if not self.Student_Name.get():
                self.AddPersonalInfo()
                showinfo("","학생정보 및 메모를 입력해주세요.")
            #Button(Register_window,text="등록",command=lambda:self.RegisterClass_handler(Class_Tuple,self.Student_Name.get(),self.Student_ID.get(),self.Memo.get())).grid(row=4,column=0,columnspan=2)
            else:
                self.RegisterClass_handler(Class_Tuple, self.Student_Name.get(), self.Student_ID.get(), self.Memo.get())
    def RegisterClass_handler(self,Class_Tuple,Name,ID,Memo):
        if Name and ID:
            if askyesno("","%이름:%s\n학번:%s\n메모:%s\n이대로 강좌를 신청할까요?"%(Name,ID,Memo)):

                res = self.requesthandler.RegisterClass(self.Session_ID[1],Class_Tuple[1],Class_Tuple[0],ID,Name,Memo)
                if res == 1:
                    showinfo("","등록이 완료되었습니다.혹시 모르니 보인아이 홈페이지에서 등록이 되어있는지 한번 더 확인해주세요.")

                else:
                    showinfo("","등록을 실패했습니다. 혹시 모르니 보인아이 홈페이지에서 등록이 되어있는지 확인해주세요.")
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
            return 1
        else: return 0


################################################################################
#GUI Utilities
def clearscreen():
    for child in root.winfo_children():
        child.destroy()
def on_close():
    if askyesno("","종료전에 기기 등록해제작업 및 로그아웃을 하시겠습니까?"):
        res = MyRequestHandler.UnRegisterPC()
        if res != 0:
            showerror("",res)
        else:
            showinfo("","기기등록이 해제되었습니다.")

            MyRequestHandler.Logout()
            showinfo("","로그아웃되었습니다.")

            root.destroy()
if __name__ == "__main__":
    root = tix.Tk()
    root.resizable(0,0)
    root.maxsize(root.winfo_screenwidth(),root.winfo_screenheight()-150)
    MyRequestHandler = BoinWebHandler()

    LoginScreen(root,MyRequestHandler)

    root.mainloop()