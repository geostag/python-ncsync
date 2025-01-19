from webdav4.client import Client
import os, stat, datetime, logging

logger = logging.getLogger('ncsync')

class vFile:
    def __init__(self, **kwargs):
        self.vDir = kwargs.get('vdir',None)
        self.name = kwargs.get('name',None)
        self.size = kwargs.get('size',None)
        self.mtime = kwargs.get('mtime',None)
        self.file = kwargs.get('file',False)

    @property
    def fullpath(self):
        return os.path.join(self.vDir.folder,self.name)

    def __str__(self):
        return ("%s,%s,%s" % (self.name,self.size,self.mtime))
    
    def __gt__(self,other):
        if self.name != other.name or self.size != other.size or self.file != other.file or self.mtime > other.mtime:
            return True
        
        else:
            return False
        
    def rm(self):
        vdir = self.vDir
        logger.debug(f'remove {self.fullpath}')
        if vdir.server:
            vdir.client.remove(self.fullpath)

        else:
            os.remove(self.fullpath)
        
    @classmethod
    def copy(cls,src,tgt):
        svdir = src.vDir
        s = src.fullpath
        if type(tgt) == vDir:
            tvdir = tgt
            t = os.path.join(tvdir.folder,src.name)
        else:
            tvdir = tgt.vDir
            t = os.path.join(tvdir.folder,tgt.name)

        if svdir.server and not tvdir.server:
            # remote -> local
            logger.debug(f'download {s} -> {t}')
            svdir.client.download_file(s,t)

        elif not svdir.server and tvdir.server:
            # local -> remote
            logger.debug(f'upload {s} -> {t}')
            tvdir.client.upload_file(s,t,overwrite=True)

        else:
            raise NotImplementedError

class vDir:
    def __init__(self, **kwargs):
        self.server = kwargs.get('server',None)
        self.user = kwargs.get('user',None)
        self.password = kwargs.get('password',None)
        self.folder = kwargs.get('folder',None)
        self.read = False
        self.list = []
        self._exists = {}
        if self.server:
            self.client = Client(self.server, auth=(self.user,self.password))

    def _read(self):
        if not self.read:
            if self.server:
                self.readWebdav()

            else:
                self.readLocal()

            self.read = True

    def ls(self):
        self._read()
        return self.list
    
    def exists(self,name):
        self._read()
        return self._exists.get(name,False)

    def readLocal(self):
        for f in os.listdir(self.folder):
            s = os.lstat(os.path.join(self.folder,f))
            vf = vFile(
                vdir = self,
                name = f,
                size = s.st_size,
                mtime = datetime.datetime.fromtimestamp(s.st_mtime,datetime.timezone.utc),
                file = stat.S_ISREG(s.st_mode)
            )
            self.list.append(vf)
            self._exists[f] = vf

    def readWebdav(self):
        for f in self.client.ls(self.folder):
            vf = vFile(
                vdir = self,
                name = os.path.split(f["name"])[-1],
                size = f["content_length"],
                mtime = f["modified"],
                file = (f["type"] == "file")
            )
            self.list.append(vf)
            self._exists[vf.name] = vf

    @classmethod
    def sync(cls, src, tgt):
        change = False

        # copy new ones from src
        for sf in src.ls():
            tf = tgt.exists(sf.name)
            if not tf or sf > tf:
                vFile.copy(sf,tgt)
                change = True

        # remove tgt stale ones
        for tf in tgt.ls():
            sf = src.exists(tf.name)
            if not sf:
                tf.rm()
                change = True

        return(change)
