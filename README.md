# python-ncsync
Sync local folders with your nextcloud

## usage

### sync from nextcloud to local folder
```
from ncsync import vDir

source = vDir(
    server = 'https://your.server.com',
    user = 'username',
    password = 'secret'
    folder = 'remote.php/dav/files/.....'
)
target = vDir( folder = '/home/localname/localfolder' )

r = vDir.sync(source,target)
if r:
    # trigger something if changes occurred
```

### sync from local folder to nextcloud
```
from ncsync import vDir

source = vDir( folder = '/home/localname/localfolder' )
target = vDir(
    server = 'https://your.server.com',
    user = 'username',
    password = 'secret'
    folder = 'remote.php/dav/files/.....'
)

r = vDir.sync(source,target)
if r:
    # trigger something if changes occurred
```

### hints
You might want to use a nextcloud [application password](https://docs.nextcloud.com/server/stable/user_manual/en/files/access_webdav.html) instead of your user's real password.
