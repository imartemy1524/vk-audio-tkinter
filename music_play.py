import time,vk_api,wget,vk_audio,platform,eyed3,requests,threading
class Player:
    IS_PLAYING=1
    NOT_PLAYING=0
    STOPED=-1
    def __init__(self):
        self.system =platform.system();
        self.url=None
        self.__speed=1.0
        if(self.system=="Windows"):
            from win32com.client import Dispatch
            self.mp = Dispatch("WMPlayer.OCX")
        elif(platform.system()=="Linux"):
            try:
                import gi
                gi.require_version('Gst', '1.0')
                from gi.repository import Gst
                self.Gst = Gst
                Gst.init(None)
                self.mp = Gst.ElementFactory.make('playbin', 'playbin')
                self.mp.set_state(Gst.State.READY)
            except Exception as e:
                import tkinter
                tkinter.messagebox.showerror("Пожалуйста, установить модуль gi для воспроизведения.\nУстановить можно командой sudo apt-get install python3-gi")    
    def _end_event(self):
        self.mp.get_bus().poll(self.Gst.MessageType.EOS, self.Gst.CLOCK_TIME_NONE)
        self.mp.set_state(self.Gst.State.NULL)
    def play(self,url=None,position=None):
        if(platform.system()=="Windows"):
            if(url is not None and self.url!=url):
                tune = self.mp.newMedia(url)
                self.mp.currentPlaylist.appendItem(tune)
                self.mp.controls.play()
                self.mp.controls.playItem(tune);
                self.url=url;
            else:
                self.mp.controls.play();
            self.speed=self.__speed;
        elif(self.system=="Linux"):
            if(url is not None and self.url != url):
                self.mp.set_state(self.Gst.State.NULL)
                self.mp.props.uri=url;
                self.url=url;
                threading.Thread(target=self._end_event).start();
            self.mp.set_state(self.Gst.State.PLAYING)
            self.mp.get_state(self.Gst.CLOCK_TIME_NONE)
            position = position if position is not None else self.mp.query_position(self.Gst.Format.TIME)[1]
            self.mp.seek(self.__speed, self.Gst.Format.TIME, self.Gst.SeekFlags.FLUSH,self.Gst.SeekType.SET,position, self.Gst.SeekType.NONE, -1)
    def pause(self):
        if(self.is_playing==self.IS_PLAYING):
            if(platform.system()=="Windows"):        
                self.mp.controls.pause()
            elif(self.system=="Linux"):
                self.mp.set_state(self.Gst.State.PAUSED)
    @property
    def is_playing(self):
        if(platform.system()=="Windows"):
            state = self.mp.playState
            answers={
                1:self.STOPED,
                3:self.IS_PLAYING,
                4:self.IS_PLAYING,
                #5:self.IS_PLAYING,
                #6:self.IS_PLAYING,
                10:self.STOPED,
                11:self.IS_PLAYING
                }
            return answers[state] if state in answers else self.NOT_PLAYING
        elif(platform.system()=="Linux"):
            state = self.mp.get_state(self.Gst.State.PLAYING)[1]
            return self.IS_PLAYING if state==self.Gst.State.PLAYING else self.STOPED if state==self.Gst.State.NULL else self.NOT_PLAYING
        return self.NOT_PLAYING
    def close(self):
        if(platform.system()=="Windows"): self.mp.Close()
        elif(platform.system()=="Linux"):self.mp.set_state(Gst.State.NULL)
    #region pos
    @property
    def pos_formated(self):
        def time_format(i):
            i = int(i)
            seconds = str(i%60)
            minutes = str(i//60)
            if(len(seconds)==1):seconds = "0"+seconds
            return minutes+"."+seconds
        return time_format(self.pos)+"/"+time_format(self.max_time)
    @property
    def pos(self):
        if(platform.system()=="Windows"):
            return self.mp.controls.currentPosition
        elif(platform.system()=="Linux"): return float(self.mp.query_position(self.Gst.Format.TIME)[1])/self.Gst.SECOND
    @pos.setter
    def pos(self,i:float):
        if(platform.system()=="Windows"):
            need_to_pause = not self.is_playing
            self.mp.controls.currentPosition=i
            self.speed=self.__speed;
            if(need_to_pause):
                self.pause();
        elif(platform.system()=="Linux"):
            pos = i * self.Gst.SECOND
            if(self.is_playing):
                self.play(None,pos);
    @property
    def max_time(self):
        if(platform.system()=="Windows"):
            if(self.mp.currentMedia is not None):
                return self.mp.currentMedia.duration;
        elif(platform.system()=="Linux"):
            return self.mp.query_duration(self.Gst.Format.TIME)[1]/self.Gst.SECOND
        return 0;
    #endregion
    #region speed 
    @property
    def speed(self):
        if(platform.system()=="Windows"):
            return self.__speed;
        elif(platform.system()=="Linux"):
            return self.__speed;

        return 1;
    @speed.setter
    def speed(self,i:float):
        if(platform.system()=="Windows"):
            self.__speed=i;
            if(self.mp.settings.rate!=i):
                self.mp.settings.rate=i
        elif(platform.system()=="Linux"):
            self.__speed=i;
            self.mp.get_state(self.Gst.CLOCK_TIME_NONE)
            if(self.is_playing):self.play();        
    #endregion
    #region volume
    @property
    def volume(self):
        if(platform.system()=="Windows"):
            return self.mp.settings.volume
        elif(platform.system()=="Linux"):
            return self.mp.props.volume*100;
        return 1;
    @volume.setter
    def volume(self,i:int):
        if(platform.system()=="Windows"):
            self.mp.settings.volume=i
        elif(platform.system()=="Linux"):
            self.mp.props.volume=i/100;
    #endregion
        