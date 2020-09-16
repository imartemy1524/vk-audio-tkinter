from tkinter import Tk,Button,Entry,Listbox,font,StringVar,END,Scrollbar,messagebox,Toplevel,Label,TOP,Frame
from tkinter.ttk import Combobox
import time,vk_api
from io import BytesIO
try:
    from .viget_download import App

except ImportError:
    from viget_download import App

import threading
import vk_audio
class MainApp(object):
    def __init__(self,vk):
        self.VkAudio=vk_audio.VkAudio(vk)
        self.vk = vk;
        self.init()
        self.info = vk.method("users.get")[0]
        self.login=vk.login;self.password=vk.password;self.comboxes();self.inputs()
        self.is_destroyd = True;self.buttons();self.ssilka_musick()
        #threading.Thread(target=self.get_inputs).start()
        self.root.after(300,self.get_inputs);
        self.root.mainloop()
    def init(self):
        try:
            from .__init__ import __main__
        except ImportError:
            from __init__ import __main__
        info = self.vk.method("users.get",{"name_case":"gen"});name = info[0]["first_name"];last_name=info[0]["last_name"]
        self.root = Tk();self.root.title("музыка {} {}".format(name,last_name)),self.root.geometry("800x500"),self.root.config(cursor='top_left_arrow'),self.root.resizable(False,False),self.root.iconbitmap(__main__.icon())
    def friends_get(self):
        friendse = self.vk.method("friends.get",{"count":100,"fields":"nickname"})
        return friendse["items"]
    def friends_search(self,q):
        friendse = self.vk.method("friends.search",{"q":q,"fields":"nickname,photo_200"})
        return friendse["items"]

    def comboxes(self):
        list_friend = self.friends_get()
        self.s = ["Мои"];(self.s.append("{} {}".format(i["first_name"],i["last_name"])) for i in list_friend)
        self.listbox = Listbox(self.root, width=40, height=5, font=('times', 13))
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        self.listbox.place(relx=.01, rely=.1,height=300)
        for i in self.s:
            self.listbox.insert(END,i)
        self.scrollbar = Scrollbar(self.root, command=self.listbox.yview)
        self.scrollbar.place(relx=0.46,rely=0.1,height=300);self.scrollbar.config();self.listbox.configure(yscrollcommand=self.scrollbar.set)

    def append_listbox(self,event,lists=None):
        if not lists:
            lists = self.friends_get();lists.insert(0,{"first_name":"Мои","last_name":""})
        self.listbox.delete(0,'end')
        for i in lists:
            self.listbox.insert(END, "{} {}".format(i["first_name"],i["last_name"]))
        
    def on_select(self,value):
        if self.listbox.curselection():
            self.person =  self.listbox.get(self.listbox.curselection())
            if self.person:
                self.box.set(self.person)
    def inputs(self):
        self.box = StringVar();self.box.set("Мои")
        Entry(self.root, textvariable=self.box,font=font.Font(size=25,root = self.root),fg="red").place(relx=.01, rely=.01,width = 360,height = 30)
    def buttons(self):
        self.button = Button(self.root,text="Получить музыку",command=self.get_music_onclick,font=font.Font(size=15,root = self.root),fg="brown")
        self.button.config(cursor='question_arrow'),self.button.place(relx=.22, rely=.75, anchor="c")
    def child(self,text):
        """
        self.kkk = "ok"
        self.childs = Toplevel(self.root)
        self.childs.resizable=(False,False);self.childs.title('Эта та страница?');self.childs.geometry('350x400');self.childs["bg"] = "orange";self.childs.iconbitmap(self.icon)

        def x(d):
            self.kkk = d
            self.childs.destroy()
        Label(self.childs,text=text,font=font.Font(size=15,root = self.childs),bg="orange").pack(side =TOP)
        Button(self.childs,text = 'Да', command = lambda: x(True),font=font.Font(size=25,root = self.childs)).place(relx=0.7,rely=0.8,width=80,height=40)
        Button(self.childs,text = 'Нет', command = lambda: x(False),font=font.Font(size=25,root = self.childs)).place(relx=0.1,rely=0.8,width=80,height=40)
        if self.url:
            Label(self.childs, image=self.url).place(relx = 0.2,rely = 0.2)
        #self.childs.mainloop()
        return self.kkk
        """
        return True if messagebox.askquestion("Это та страница?",text) =="yes" else False

    def get_music_onclick(self):
        #from tkinter import Image
        if self.box.get().lower()!="мои":
            friend = self.friends_search(q=self.box.get())[0]
        else:
            friend = self.info
        q = self.child(text="id : {},\nИмя : {},\nФамилия: {}".format(friend["id"],friend["first_name"],friend["last_name"]))

        if q:
            App.get(vk_audio =self.VkAudio,owner_id=friend["id"],info=friend)
        
    def get_music_by_link(self):
        url = self.ssilka.get().replace("https://","").replace("http://","").replace("vk.com","").replace("id","").replace("/","")
        user = self.vk.method("users.get",{"user_ids":url})
        if len(user)>0:
            q = self.child(text="id : {},\nИмя : {},\nФамилия: {}".format(user[0]["id"],user[0]["first_name"],user[0]["last_name"]))
            if q:
                App.get(vk_audio = self.VkAudio,owner_id=user[0]["id"],info=user[0])
        else:
            messagebox.showerror("извини, но ссылка не правильная(((")
    def ssilka_musick(self):
        self.ssilka = StringVar();self.ssilka.set("vk.com/id"+str(self.info["id"]))
        Entry(self.root, textvariable=self.ssilka,font=font.Font(size=25,root = self.root),fg="blue").place(relx=.5, rely=.01,width = 350,height = 30)
        self.button = Button(self.root,text="Получить музыку по ссылке",command=self.get_music_by_link,font=font.Font(size=15,root = self.root),fg="brown")
        self.button.config(cursor='question_arrow'),self.button.place(relx=.75, rely=.75, anchor="c")

    def get_inputs(self):
        self.q= None
        try:
            if self.box.get()!=self.q:
                self.q = self.box.get()
                if self.q.lower().strip(" ")!="мои" and self.q!="" :
                    self.append_listbox(event=None,lists=self.friends_search(q=self.box.get()))
                else:
                    self.append_listbox(event=None)
            else:
                self.root.after(300,self.get_inputs)
        except:
            self.root.after(300,self.get_inputs)


