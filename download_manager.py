import tkinter,threading,queue,wget,eyed3,requests,gc
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showerror
class DownloadManager(tkinter.Tk):
    window=None
    def STRING(self,i):
        if(i==0):return "Скачивание завершено"
        c = "Осталось скачать {} файл".format(i)
        p=i%10
        if(p in (0,5,6,7,8,9) or i%100 in (i for i in range(11,20))):c+="ов";
        elif(p in (2,3,4)):c+="a"
        return c;
    def __init__(self):
        super().__init__("Загрузка","загркзка")
        self.geometry('300x150')
        self.resizable(width=False, height=False)
        self.items = queue.Queue();
        self.working=False
        try:
            import tkinter.ttk
            self.progressbar = tkinter.ttk.Progressbar(self,mode="determinate")
        except Exception as e:
            self.progressbar = tkinter.Label(self,text="Виджет недоступен")
        self.c=self.i=self.max=0;
        self.textvar = tkinter.StringVar(self,self.STRING(0));
        tkinter.Label(self,textvariable=self.textvar,font=('times',17)).pack();
        self.progressbar.pack(fill="x");
        DownloadManager.window=self;
    @staticmethod
    def get():return DownloadManager.window or DownloadManager();
    def download(self,item):
        file = asksaveasfilename(master=self,
            filetypes = [('Media files', '.mp3'),('All files', '*')],
            defaultextension="mp3",
            title="Choice location",
            initialfile=''.join(
                        i for i in "{0} - {1}.mp3".format(item.title,item.artist) 
                                if i not in ("*","/","\\",":","?","|",'"',">","<")))
        if(file==''):
            if(not self.working):self.destroy()
            return;
        self.c+=1;
        self.items.put((item,file))
        if(not self.working):
            self.working=True
            self.on_download_progress();
            self.thread = threading.Thread(target=self.__download_item_worker).start();
    def __download_item(self,item,file):
        try:
            wget.download(item.url,file,self.progress_thread);
        except Exception as e:
            showerror("Неизвестная ошибка:",str(e))
        song = eyed3.load(file);
        if(song.tag is None):
            song.initTag();    
        if(item.image):
            song.tag.images.set(3, requests.get(item.image).content , "image/jpeg" ,u"Description")
        song.tag.artist=item.artist;
        song.tag.title=item.title;

        if(item.text):song.tag.lyrics.set(item.text.encode())
        try:

            song.tag.save()
        except:pass
    def progress_thread(self,i,max,_):
            self.i=i/100000;
            self.max=max/100000;
            pass
    def __download_item_worker(self):
        while(not self.items.empty()):
            self.__download_item(*self.items.get())
            self.c-=1
        self.working=False
    def on_download_progress(self):
        if(type(self.progressbar) is not tkinter.Label): 
            self.progressbar.config(maximum=self.max)
            self.progressbar['value']=self.i;
        self.textvar.set(self.STRING(self.c));
        if(self.working):
            self.after(100,self.on_download_progress)
    def destroy(self):
        DownloadManager.window=None
        gc.collect()
        return super().destroy()