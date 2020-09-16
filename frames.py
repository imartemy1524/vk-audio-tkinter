from tkinter import Frame,Canvas,Scrollbar,font,NW,NSEW,YES,Button,BOTH,Y,BOTTOM,RIGHT,LEFT,NONE,HORIZONTAL,Label,Menu as MenuTk
import tkinter.ttk as ttk
import vk_audio,requests
from io import BytesIO
from PIL import Image,ImageDraw
from PIL import ImageTk
try:
    from .download_manager import DownloadManager
except ImportError:
    from download_manager import DownloadManager
class AudiosFrame(Frame):
    dataCols = ('ID', 'артист', 'Название')

    def __init__(self,master,audios=None,need_to_reorder=False,select_index=0,**args):
        super().__init__(master,**args)
        self.need_to_reorder=need_to_reorder;
        self.audios=audios;

        self._set_buttons();
        
        self.tree = ttk.Treeview(self, columns=self.dataCols);
        self.scrollbar = Scrollbar(self, command=self.tree.yview)
        self.scrollbar.pack(side=RIGHT,pady=5,fill=Y)
        self.tree.pack(fill=BOTH,expand=True,side=RIGHT)#.place(relwidth=0.95,anchor="n",relheight=0.9,relx=0.5)

        self.tree.heading('#0', text='count', anchor='center')
        self.tree.heading('#1', text='ID', anchor='center')
        self.tree.heading('#2', text='артист', anchor='center')
        self.tree.heading('#3', text='Название', anchor='w')

        self.tree.column('#0', stretch=YES,minwidth=40, width=40)
        self.tree.column('#1', stretch=YES, width=170,minwidth=150)
        self.tree.column('#2', stretch=YES, minwidth=50, width=250)
        self.tree.column('#3', stretch=YES, minwidth=50, width=253)

        #self.tree.bind("<<TreeviewSelect>>", self.OnDoubleClick)
        menu = Menu(self,self.tree,self)
        #.place(relx=1,rely=0.003,relheight=0.9,anchor="ne")

        self.scrollbar.config();
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        style = ttk.Style(self)
        style.configure('Treeview', rowheight=38)
        if(self.audios is not None):
            self._update(index=select_index);
    def _update(self,audios=None,index=0):
        if(audios!=self.audios):
            if(audios is not None):
                self.audios=audios
            map(self.tree.delete, self.tree.get_children())
            for i in range(len(self.audios)-1,-1,-1):
                self.add_column(self.audios[i],i)
        column = self.tree.selection_set(self.tree.get_children()[index])
    def _set_buttons(self):
        padx=10
        buttons_frame = Frame(self)
        buttons_frame.pack(side=BOTTOM,pady=5,fill=NONE)
        self.dowload_button= Button(buttons_frame,text="скачать",command=self.download,fg="red",font=font.Font(size=15,root = self))
        self.dowload_button.pack(side=LEFT,padx=padx)#.place(rely=0.9088,relx=0.01,anchor="n")
        self.listen_button= Button(buttons_frame,text="прослушать",command=self.listen,fg="brown",font=font.Font(size=15,root = self))
        self.listen_button.pack(side=LEFT,padx=padx)#.pack(side=BOTTOM,padx=20,fill=NONE)#.place(rely=0.9088,relx=0.14,anchor="n")
        self.dowload_all_button= Button(buttons_frame,text="скачать всё аудио",command=self.download_all,fg="orange",font=font.Font(size=15,root = self))
        self.dowload_all_button.pack(side=LEFT,padx=padx)#.pack(side=BOTTOM,padx=20,fill=NONE)#.place(rely=0.9088,relx=0.39,anchor="n")
    def add_column(self,item,i):
        self.tree.insert('', 0,text=str(i), value=("audio{}_{}".format(item.owner_id,item.id),item.artist,item.title))                                                
    def download_all(self):
        for i in self.audios:
            self.download(i);
    def download(self,item=None):
        item = self.audios[self.count] if type(item)!=vk_audio.AudioObj else item;
        DownloadManager.get().download(item); 
    def listen(self):
        try:
            from .player_window import PlayerWindow
        except ImportError:
            from player_window import PlayerWindow
        p = PlayerWindow.init(self.audios,self.count)
    @property
    def count(self):
        item = self.tree.selection()
        if(not item):return 0;
        return self.tree.get_children().index(item[0])
        #self.count = int(self.tree.item(item,"text"))
class Menu(Frame):
    def __init__(self, parent,tree,selfa:AudiosFrame):
        Frame.__init__(self, parent)   
        self.parent = parent;
        self.on = selfa
        self.tree = tree;
        self.tree.bind("<Button-3>", self.showMenu)

    def initUI(self):
        menu = MenuTk(self.tree,tearoff=0);fileMenu = MenuTk(menu,tearoff=0)       
        menu.add_command(label="Воспроизвести", underline=0,command=self.start_play)
        menu.add_command(label="Скачать", underline=0,command=self.download )
        
        if(self.on.audios[int(self.on.count)]):
            menu.add_command(label="Перейти к артисту", underline=0,command=self.go_to_artist )
        
        menu.add_cascade(label="Скопировать", underline=0, menu=fileMenu)
        
        fileMenu.add_command(label='Ссылку на аудио', underline=0, command=self.onUrl)
        fileMenu.add_command(label='ID', underline=0)

        fileMenu.add_command(label="Артист", underline=0, command=self.onArtist)

        fileMenu.add_command(label="Название", underline=0, command=self.onName)
                
        return menu;
    def start_play(self):self.on.listen()
    def download(self):self.on.download()
    def go_to_artist(self):
        aud = self.on.audios[int(self.on.count)]
        mus = aud.artist_music(0)
        try:
            from .viget_download import App
        except ImportError:
            from viget_download import App
        App.get(mus,vk_audio=mus.vk_audio,info={"first_name":mus.nick,"last_name":"","id":mus.owner_id})
    def onName(self):
        self.clipboard_clear()
        self.clipboard_append(self.on.audios[int(self.on.count)].title)
    def onUrl(self):
        self.clipboard_clear()
        self.clipboard_append(self.on.audios[int(self.on.count)].url)
    def onArtist(self):
        self.clipboard_clear();
        self.clipboard_append(self.on.audios[int(self.on.count)].artist)
    def showMenu(self, e):
        self.initUI().post(e.x_root, e.y_root)
    def onExit(self):self.quit()
class AlbumsFrame(ttk.Frame):
    ONE_ITEM_WIDTH=200
    DEFAULT_FONT=('times',12)
    HOVER_FONT=('times',13,'bold')
    DEF_FG="#717171"
    HOVER_FG="blue"
    def __init__(self,master,albums:list,album_onclick,author_onclick):
        super().__init__(master);
        self.onclick = album_onclick;
        self.a_onclick=author_onclick
        #region scrollbar
        canvas = Canvas(self);
        scrollbar = ttk.Scrollbar(self,orient=HORIZONTAL);

        self.f=ttk.Frame(canvas)
        #self.f.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.f, anchor="nw")
        
        canvas.configure(xscrollcommand=scrollbar.set)
        scrollbar.pack(side=BOTTOM, fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        #endregion
        for i in albums:
            self.create_album(i);
        scrollbar.config(command=canvas.xview);
        self._config = lambda:canvas.configure(scrollregion=canvas.bbox("all"))
        self._config()
        return
    def create_album(self,playlist:vk_audio.Playlist):
        click = lambda _:self.onclick(playlist)
        f = ttk.Frame(self.f,width=self.ONE_ITEM_WIDTH,cursor="hand2");
        f.bind("<Button-1>", click)

        img = Canvas(f,width=160,height=160);
        img.pack(pady=5)        
        img.bind("<Button-1>", click)

        self.set_image_from_album(img,playlist)
        title = Label(f,text=playlist.title,font=('times',14));
        title.pack(padx=10)
        title.bind("<Button-1>", click)

        author = Label(f,text=",".join(i['name'] for i in playlist.author_info),font=self.DEFAULT_FONT,fg=self.DEF_FG);
        author.pack(padx=10)
        author.bind("<Button-1>",lambda _:self.a_onclick(playlist))
        author.bind("<Enter>", lambda _:(author.config(font=self.HOVER_FONT,fg=self.HOVER_FG),self._config()))
        author.bind("<Leave>", lambda _:(author.config(font=self.DEFAULT_FONT,fg=self.DEF_FG),self._config()))

        f.pack(side=LEFT)
    def set_image_from_album(self,canvas,playlist):
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
        def resize(img,height=150,width=150):
            if(img.size!=(width,height)):return img.resize((height,height))
            return img
        if(hasattr(playlist, 'bitmap')):
            img = playlist.bitmap
        else:
            l = len(playlist.images);
            if(l==1):
                content = BytesIO(requests.get(playlist.images[0],stream=True).content);
                img = Image.open(content);
            elif(l==2):
                img = Image.new("RGB",(150,150))
                bytes =(BytesIO(requests.get(playlist.images[i],stream=True).content) for i in range(2))
                img1,img2 = (resize(Image.open(i)) for i in bytes)
                for i in bytes:i.close()
                img.paste(img1.crop((150/4,0,150-150/4,150)),(0,0))
                img.paste(img2.crop((150/4,0,150-150/4,150)),(75,0))
                img1.close();img2.close()
            elif(l==3):
                img = Image.new("RGB",(150,150))
                bytes =(BytesIO(requests.get(playlist.images[i],stream=True).content) for i in range(3))
                img1,img2,img3 = (resize(Image.open(i)) for i in bytes)
                for i in bytes:i.close()
                img.paste(img1.crop((150/4,0,150-150/4,150)),(0,0))
                img.paste(resize(img2,75,75),(75,0))
                img.paste(resize(img3,75,75),(75,75))
                img1.close();img2.close();img3.close()
            elif(l==4):
                img = Image.new("RGB",(150,150))
                bytes =(BytesIO(requests.get(playlist.images[i],stream=True).content) for i in range(4))
                images = (resize(Image.open(i),75,75) for i in bytes)
                for i in bytes:i.close()
                img.paste(images[0],(0,0))
                img.paste(images[1],(75,0))
                img.paste(images[2],(0,75))
                img.paste(images[3],(75,75))
                for i in images:i.close()
            else:
                img = Image.open(__main__.i_f("no_image.png"));
            playlist.bitmap=img
        
        img = add_corners(resize(img),20)
        canvas.image=ImageTk.PhotoImage(img,master=canvas);
        canvas.create_image(5, 5, anchor=NW, image=canvas.image) 
        



 