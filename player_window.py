import tkinter,os,requests#,vk_audio
from tkinter import messagebox
from PIL import Image,ImageDraw
from PIL import ImageTk
from tkinter import ttk
try:
    from .music_play import Player
    from .frames import AudiosFrame
    from .download_manager import DownloadManager
except ImportError:
    from music_play import Player
    from frames import AudiosFrame
    from download_manager import DownloadManager
from io import BytesIO
#from .music_play import Player
class PlayerWindow(tkinter.Tk):
    window = None
    TOP_FRAME_OFFSET=2
    VOLUME_SPEED_SCALE_OFFSET=15#%
    BUTTONS_BUTTON_OFFSET=3#%
    MAIN_SCALE_WIDTH=90#%
    def __init__(self):
        super().__init__()
        if(PlayerWindow.window):self.destroy();return;
        self.index=0
        self.scale_blocked=False;

        self.player=Player();
        self.title("Плеер")
        self.minsize(400,400)
        
        if(ttk is not tkinter):
            notebook = ttk.Notebook(self);
            self.f=tkinter.Frame(notebook);

            self.queue = tkinter.Frame(notebook);
            self.audios_count = tkinter.StringVar(self.queue,"");
            tkinter.Label(self.queue,font=('times',20),textvariable=self.audios_count).pack();
            self.f_q = AudiosFrame(self.queue);
            self.f_q.pack(side=tkinter.BOTTOM,expand=True,fill=tkinter.BOTH);
            notebook.add(self.f,text="Плеер");
            notebook.add(self.queue, text='Очередь')
            notebook.place(x=0,y=0,relheight=1,relwidth=1)
            
        else:
            self.f = tkinter.Frame(self,height=400);
            self.f.place(x=0,y=0,relheight=1,relwidth=1)
        first_frame = tkinter.Frame(self.f)
        first_frame.place(height=300,relwidth=1,x=0,rely=self.TOP_FRAME_OFFSET/100,anchor="nw")
        self.image = tkinter.Canvas(first_frame, width = 160, height = 160)
        self.image.place(y=10,relx=0.5,anchor="n")


        self.title_var,self.artist_var,self.scale_var,self.scale_text_var,self.speed_var=(tkinter.StringVar(self.f,"Title..."), 
            tkinter.StringVar(self.f,"Artist..."),
            tkinter.IntVar(self.f,0),
            tkinter.StringVar(self.f,"0.0/0.0"),
            tkinter.DoubleVar(self.f,1.));

        self.title = tkinter.Label(first_frame,
                                   anchor="center",
                                   text="Title...",font=("Helvetica", 16),
                                   textvariable=self.title_var);
        self.title.place(y=180,x=0,relwidth=1)#.grid(row=2, column=0,sticky="wens")

        self.artist= tkinter.Label(first_frame, text="Artist...",font=("Helvetica", 12),foreground="#717171",textvariable=self.artist_var);
        self.artist.place(y=210,x=0,relwidth=1)
        #region scale_controls
        volume_frame=tkinter.Frame(first_frame)
        volume_frame.place(y=10,relx=self.VOLUME_SPEED_SCALE_OFFSET/100,anchor="n",width=75,height=150)
        volume_scale = tkinter.Scale(volume_frame,from_=100,to=0,command=self.setVolume,orient=tkinter.VERTICAL)
        volume_scale.set(100);
        volume_scale.pack()#.place(relx=0.5,anchor="n")
        tkinter.Label(volume_frame,text="Громкость").pack()#.place(y=120)


        speedFrame = tkinter.Frame(first_frame)
        speedFrame.place(y=10,relx=1-self.VOLUME_SPEED_SCALE_OFFSET/100,anchor="n",width=75,height=150)
        speed_scale = tkinter.Scale(speedFrame,from_=3,to=0.05,variable=self.speed_var ,resolution = 0.01,orient=tkinter.VERTICAL)
        speed_scale.bind("<ButtonRelease-1>",self.setSpeed)
        speed_scale.pack()
        tkinter.Label(speedFrame,text="Скорость").pack()
        #endregion
        self.time_text = tkinter.Label(first_frame,anchor="center",textvariable=self.scale_text_var,font=("Helvetica",  22))
        self.time_text.place(y=240,relwidth=1)

        self.scale = ttk.Scale(first_frame,from_=0,variable=self.scale_var, to=100,orient=tkinter.HORIZONTAL,takefocus =0)
        self.scale.place(y=280,relwidth=self.MAIN_SCALE_WIDTH/100,anchor="nw",relx=0.05)
        self.scale.bind('<Button-1>',lambda *args:self.posSetting(True))
        self.scale.bind("<ButtonRelease-1>",self.onScale)
        
        self.__set_image_buttons();
        self._update_time(True)
        self.lift()
        PlayerWindow.window=self
    @staticmethod
    def init(playlist,index):
        if(PlayerWindow.window is not None):
            return PlayerWindow.window.set_info(playlist,index);
        else:
            return PlayerWindow().set_info(playlist,index);
    def set_info(self,playlist=None,index=None):
        if(playlist is not None):self.playlist=playlist;   
        if(index is not None):self.index=index;
        if(self.index==-1):self.index=len(self.playlist)-1
        elif(self.index==len(self.playlist)):self.index=0;

        self.audios_count.set(str(self.index+1)+" Аудио");
        
        self.f_q._update(self.playlist,self.index);

        self.item = self.playlist[self.index];
        self.action_button.image = self.image_plus if not self.item.can_delete else self.image
        self._set_image_from_item(self.item)
        
        img=self.image_delete if self.item.can_delete else self.image_plus
        self.action_button.image=img
        self.action_button.config(image=img)

        self.artist_var.set(self.playlist[self.index].artist)
        self.title_var.set(self.playlist[self.index].title)
        self.player.play(self.playlist[self.index].url)
        self.scale_blocked=False;

        return self
    def __set_image_buttons(self):
        try:
            from .__init__ import __main__
        except ImportError:
            from __init__ import __main__
        buttons_frame = tkinter.Frame(master=self.f,height=50);
        buttons_frame.place(x=0,rely=1-self.BUTTONS_BUTTON_OFFSET/100,height=50,relwidth=1,anchor="sw")

        self.image_play = tkinter.PhotoImage(master=buttons_frame,file=__main__.i_f("play.png"))
        self.image_pause = tkinter.PhotoImage(master=buttons_frame,file=__main__.i_f("pause.png"))
        
        self.image_plus = tkinter.PhotoImage(master=buttons_frame,file=__main__.i_f("plus.png"))
        self.image_download = tkinter.PhotoImage(master=buttons_frame,file=__main__.i_f("download.png"))
        self.image_delete =ImageTk.PhotoImage(Image.open(__main__.i_f("plus.png")).rotate(45),master=self.f);
        image_next = tkinter.PhotoImage(master=buttons_frame,file=__main__.i_f("next.png"))
        image_back = tkinter.PhotoImage(master=buttons_frame,file=__main__.i_f("back.png"))

        self.action_button = ttk.Button(buttons_frame,image=self.image_plus,command=self.actionClick)
        self.action_button.place(width=50,height=50,relx=0.2,anchor="n")
        
        self.back_button=ttk.Button(buttons_frame,image=image_back,command=self.backButtonClick)
        self.back_button.image=image_back
        self.back_button.place(width=50,height=50,relx=0.35,anchor="n")
        
        self.play_button = ttk.Button(buttons_frame,image=self.image_pause,command=self.pauseButtonClick);
        self.play_button.image=self.image_pause;
        self.play_button.place(width=50,height=50,relx=0.5,anchor="n")

        self.next_button = ttk.Button(buttons_frame,image=image_next,command=self.nextButtonClick)
        self.next_button.image=image_next
        self.next_button.place(width=50,height=50,relx=0.65,anchor="n")
       
        self.button_download = ttk.Button(buttons_frame,image=self.image_download,command=lambda:DownloadManager.get().download(self.item))
        self.button_download.place(width=50,height=50,relx=0.8,anchor="n")

        self.iconbitmap(__main__.icon())
    def _update_time(self,repeat=False):
        is_playing=self.player.is_playing
        if(not self.scale_blocked):
            if(self.scale['to']!=self.player.max_time):
                self.scale.configure(to=self.player.max_time)
            self.scale_var.set(self.player.pos)
        self.scale_text_var.set(self.player.pos_formated);
        if(is_playing==Player.STOPED):
            self.index+=1;
            self.set_info();
        if(repeat):
            self.title.after(200,lambda:self._update_time(True))
    #region onclicks
    def onScale(self,i):
        self.player.pause()
        self.player.pos=float(self.scale_var.get())
        self.player.play()
        self.posSetting(False)
        self._update_time()
        return;
    def setVolume(self,i):
        self.player.volume=int(i);
        return
    def setSpeed(self,i):
        self.player.speed=self.speed_var.get()
        return
    def nextButtonClick(self):
        self.player.pause();
        self.index+=1;
        self.set_info();
        pass
    def backButtonClick(self):
        self.player.pause();
        self.index-=1;
        self.set_info();
        pass
    def pauseButtonClick(self):
        if(not self.player.is_playing):
            self.play_button.configure(image=self.image_pause)
            self.play_button.image = self.image_pause
            self.player.play()
        else:
            self.play_button.configure(image=self.image_play)
            self.play_button.image = self.image_play
            self.player.pause();
        pass
    def posSetting(self,mousedown:bool):
        self.scale_blocked=mousedown;
        pass
    def actionClick(self):
        if (self.item.can_delete):
            if(messagebox.askokcancel("Подтвердите действие","Вы уверены, что хотите удалить это аудио из ВАШИХ аудиозаписей?")):
                self.item.delete();
                self.action_button.image=self.image_plus
                self.action_button.config(image=self.image_plus)
            return
        if(self.item.can_restore):
            self.item.restore()
        else:
            self.item.add()
        self.action_button.image=self.image_delete
        self.action_button.config(image=self.image_delete)

        pass
    #endregion
    def _set_image_from_item(self,image):
        try:
            from .__init__ import __main__
        except ImportError:
            from __init__ import __main__
        def add_corners(im, rad): 
            circle = Image.new('L', (rad * 2, rad * 2), 0) 
            draw = ImageDraw.Draw(circle) 
            draw.ellipse((0, 0, rad * 2, rad * 2), fill=255) 
            alpha = Image.new('L', im.size, 255) 
            w, h = im.size 
            alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0)) 
            alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad)) 
            alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0)) 
            alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad)) 
            im.putalpha(alpha) 
            return im 
        if(hasattr(image,"bitmap")):
            img = Image.open(image.bitmap);
        elif(image.image):
            image.bitmap = BytesIO(requests.get(image.image,stream=True).content);
            img = Image.open(image.bitmap);
        else:
            image.bitmap = img = Image.open(__main__.i_f("no_image.png"));
        if(img.size!=(150,150)):
            img=img.resize((150,150))
        img = add_corners(img,20)
        self.image.image=ImageTk.PhotoImage(img,master=self.f);
        self.image.create_image(5, 5, anchor=tkinter.NW, image=self.image.image) 
    def destroy(self):
        PlayerWindow.window=None;
        self.player.close()
        return super().destroy()

#tk = PlayerWindow(None,None)
#tk.mainloop()