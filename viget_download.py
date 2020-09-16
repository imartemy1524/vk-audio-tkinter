import tkinter as tk;import base64;from io import BytesIO
from tkinter import font,messagebox;import vk_api;import tkinter.ttk as ttk;
try:
    from .music_play import Player;
    from .download_manager import DownloadManager
    from .player_window import PlayerWindow
    from .frames import AudiosFrame,AlbumsFrame
except ImportError:
    from music_play import Player;
    from download_manager import DownloadManager
    from player_window import PlayerWindow
    from frames import AudiosFrame,AlbumsFrame
import vk_audio,os,threading
from tkinter.ttk import Notebook
class App(tk.Tk):
    window = None
    def get_title(self,info):
        return "Музыка {} {} (id{})".format(info["first_name"],info["last_name"],info["id"])
    def __init__(self, audio_obj,vk_audio,info):
        #initialize self
        if(App.window is not None):return
        super().__init__();
        self.vk_audio = vk_audio
        self.geometry('733x450');
        self.columnconfigure(0, weight=1)

        self.count,self.SortDir,self.player_window=False,True,None;

        #initialize notebook
        self.tabs = Notebook(self);
        self.tabs.place(x=0,y=0,relwidth=1,relheight=1)
        self.tabs.bind('<<NotebookTabChanged>>',self.tab_changed);

        self.list = [];
        self.add_tab(audio_obj,info)
        App.window=self;
    def add_tab(self,audio:vk_audio.Audio,info):
        if(audio in self.list):self.tabs.select(self.list.index(audio));return
        title = self.get_title(info);
        f = tk.Frame(self.tabs);
        tk.Button(f,text="Закрыть",command = self.on_close_tab_clicked).pack()
        #add_albums_frame
        if(audio.Playlists):
            AlbumsFrame(f,audio.Playlists,self.add_tab_playlist,self.author_clicked).pack(side=tk.TOP,fill=tk.BOTH,expand=False)
        #add_audios_frame
        AudiosFrame(f,audio.Audios,True).pack(fill=tk.BOTH,expand =True,side=tk.BOTTOM)
        self.tabs.add(f,text=title)
        self.list.append(audio)
        self.focus_force()
        self.tabs.select(len(self.list)-1)
        return self
    def on_close_tab_clicked(self):
        t = self.tabs.select()
        index = self.tabs.tabs().index(t)
        self.list.pop(index)
        if(not self.list):self.destroy();
        self.tabs.forget(t);
    def tab_changed(self,event):
        tab = self.tabs.tab(event.widget.index("current") if not isinstance(event,int) else event)
        self.title(tab['text'])
    def add_tab_playlist(self,playlist:vk_audio.Playlist):
        if(playlist in self.list):self.tabs.select(self.list.index(playlist));return
        self.list.append(playlist)
        title = "Плейлист {} (id{})".format(playlist.title,playlist.owner_id);
        f = tk.Frame(self.tabs);
        tk.Button(f,text="Закрыть",command = self.on_close_tab_clicked).pack()

        #region add playlist info
        tk.Label(f,text=playlist.title,font=('times',16)).pack()
        
        author = tk.Label(f,text=",".join(i['name'] for i in playlist.author_info),font=AlbumsFrame.DEFAULT_FONT,fg=AlbumsFrame.DEF_FG,cursor="hand2");
        author.pack()
        author.bind("<Button-1>",lambda _:self.author_clicked(playlist))
        author.bind("<Enter>", lambda _:author.config(font=AlbumsFrame.HOVER_FONT,fg=AlbumsFrame.HOVER_FG))
        author.bind("<Leave>", lambda _:author.config(font=AlbumsFrame.DEFAULT_FONT,fg=AlbumsFrame.DEF_FG))
        
        img = tk.Canvas(f,width=160,height=160);img.pack(pady=5)

        AlbumsFrame.set_image_from_album(None,img,playlist)
        #endregion
        AudiosFrame(f,playlist.Audios,True).pack(fill=tk.BOTH,expand =True,side=tk.BOTTOM)
        self.tabs.add(f,text=title)
        self.focus_force()
        self.tabs.select(len(self.list)-1);

    def author_clicked(self,playlist):
        if(playlist.author_hrefs):
            for i,item in enumerate(self.list):
                if(isinstance(item,vk_audio.Audio) and item.owner_id == playlist.owner_id):
                    self.tabs.select(i);
                    break
            else:
                artist_music = playlist.artist_music(0);

                self.add_tab(artist_music,{"first_name":artist_music.nick,"last_name":"","id":artist_music.owner_id})
        elif(playlist.owner_id>0):
            for i,item in enumerate(self.list):
                if(isinstance(item,vk_audio.Audio) and item.owner_id == playlist.owner_id):
                    self.tabs.select(i);
                    break
            else:
                self.add_tab(self.vk_audio.load(playlist.owner_id))

        else:
            messagebox.showerror("Ошибка","Пока брать музыку у артиста(")

    def destroy(self):
        if(App.window is self):
            App.window = None;
        return super().destroy()
    @staticmethod
    def get(item=None,owner_id=None,vk_audio=None,info=None):
        if(item is None and vk_audio is not None):
            item=vk_audio.load(owner_id=owner_id)
        return App(audio_obj=item,info=info,vk_audio=vk_audio) if App.window is None else App.window.add_tab(item,info)
    

        
