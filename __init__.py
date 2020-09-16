from tkinter import messagebox,Tk,Button,ttk,font,StringVar,Entry,messagebox,ttk,Label,Canvas,BooleanVar,Checkbutton
import sqlite3,os,threading,vk_api,platform
from wget import download
from threading import Thread
try:
    from .init import MainApp
except ImportError:
    from init import MainApp
class __main__(object):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"images")
    @staticmethod
    def icon():
        if platform.system()=="Windows":
            return __main__.i_f("icon.ico")
        else:
            return "@"+__main__.i_f("icon.xbm")    
    @staticmethod
    def i_f(f):
        return os.path.join(__main__.path,f)  
    @property
    def login_text(self):
        if(self.__login is None):
            if(not os.path.exists("login.txt")):self.login_text="";
            with open("login.txt",'r',encoding="utf-8") as f:
                self.__login= f.read()
        return self.__login
        
    @login_text.setter
    def login_text(self,v):
        with open("login.txt","w",encoding="utf-8") as f:
            f.write(v)
        self.__login=v;
    def __init__(self,root):
        self.__login=None
        self.root,self.mask = root, BooleanVar()
        self.font_log,self.font_vihod,self.font_normal =font.Font(size=13,root = self.root), font.Font(size=15,root = self.root),font.Font(size=25,root = self.root)

        self.buttons(),self.inputs(),self.text(),self.mask.set(False),self.check_buttons()
        #self.lines()
    def inputs(self,n=None):
        self.login,pas = StringVar(self.root,"Логин"),StringVar(self.root,)
        
        if not n:
            Entry(self.root, textvariable=self.login,font=self.font_log).place(height = 30,width=150,relx=.6, rely=.1, anchor="c")
            if self.login_text:
                self.login.set(self.login_text)
         
        self.entry = Entry(self.root,show=["*" if not self.mask.get() else None][0], textvariable=pas,font=self.font_log)
        self.entry.place(height = 30,width=150,relx=.6, rely=.3, anchor="c")
        pas.set("пароль" if not n else self.password.get())
        self.password = pas
    """
    def lines(self):
        canvas = Canvas(self.root)
        s = canvas.create_line(100, 100, 100, 100)

        canvas.pack(expand=0)
    """
        
    def text(self):
        s = Label(self.root,text="Логин:",font=self.font_normal)
        s.place(height = 30,width=150,relx=.2, rely=.1, anchor="c")
        
        s = Label(self.root,text="Пароль:",font=self.font_normal)
        s.place(height = 40,width=150,relx=.2, rely=.3, anchor="c")
    def buttons(self):
        s = Button(text="Авторизоваться",command=self.auth_button,font=self.font_normal,fg="brown")
        s.config(cursor='question_arrow'),s.place(relx=.5, rely=.6, anchor="c")
        #кнопка выхода
        s1 = Button(text="выход",command=self.root.destroy,fg="red",height = 1,width = 6,font=self.font_vihod,relief="ridge")#sunken, raised,groove , and ")
        s1.bind("<Button-1>")
        s1.config(cursor='X_cursor')
        s1.place(x=300,y=230)

    def auth_button(self):
        #s = tkinter_gif.h
        #def n():
        #    s(os.path.join(dir_path, 'load.gif'))
        #sk = Thread(None,target=n)
        #sk.start()
        log,passw = self.login.get(),self.password.get()
        
        if not log or not passw:
            messagebox.showerror("Ошибка","Какое-то поле пустое!")
        vk = vk_api.VkApi(login=log,password=passw,app_id=2685278)                   
        try:
            print(log,passw)
            vk.auth()
            self.login_text=log;
            self.root.destroy()
            MainApp(vk)
        except vk_api.exceptions.BadPassword:
            messagebox.showerror("Ошибка","Неправильный логин или пароль!!!")       
        except vk_api.exceptions.Captcha:
            messagebox.showerror("Ошибка","Нужна капча")

            
    def check_buttons(self):
        cb = Checkbutton(self.root, text="Показать", command=self.onClickCkeckButton)
        cb.place(height = 40,relx=.9, rely=.3, anchor="c")
    def onClickCkeckButton(self):
        q = self.mask.get();self.mask.set(not q )
        self.inputs(n="ok")
def start():
    root = Tk()
    __main__(root)
    root.bindtags,root.title("музыка вк авторизация"),root.geometry("400x300"),root.config(cursor='top_left_arrow'),root.resizable(False,False),root.iconbitmap(__main__.icon())
    root.mainloop()


if(__name__=="__main__"):
    start();
