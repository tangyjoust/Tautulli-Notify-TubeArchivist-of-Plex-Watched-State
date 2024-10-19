# Tautulli watched sync
Automatically synchronize watched Youtube Videos to TubeArchivist. 

A script for [TubeArchivist](https://github.com/tubearchivist/tubearchivist). Do not post issues regarding this to the main repository

This assumes that the filename for the videos will be `{youtube_id}.ext` where the extension is removed before passing on to TubeArchivist as the key to mark watched.

## Setup
Download `tubearchivist_sync.py` and `sync_settings.ini.example` to your Tautulli host.
Rename `sync_settings.ini.example` to `sync_settings.ini` and add the `user_ids`, `api_token` and `url`. See below for more info on these settings.

**Important!** Make sure `sync-settings.ini` is writable

### Settings
`./sync-settings.ini`

```
  [Plex]
  user_ids: a comma separated list of user ids, only entries for these users will be synced
    The user id for a user can be found in your url in Tautulli when you click on a user.

  [TubeArchivist]
  Update `url` with your TubeArchivist url and `api_token` with your TubeArchivist API Key.
  Look [here](https://docs.tubearchivist.com/api/introduction/#authentication) as for how to receive these credentials.

```

### Tautulli
```
Adding the script to Tautulli:
Tautulli > Settings > Notification Agents > Add a new notification agent > Script

Configuration:
Tautulli > Settings > Notification Agents > New Script > Configuration:

  Script Folder: /path/to/your/scripts
  Script File: ./tubearchivist_sync.py (Should be selectable in a dropdown list)
  Script Timeout: {timeout}
  Description: TubeArchivist sync
  Save

Triggers:
Tautulli > Settings > Notification Agents > New Script > Triggers:
  
  Check: Watched
  Save
  
Conditions:
Tautulli > Settings > Notification Agents > New Script > Conditions:
  
  Set Conditions: [{condition} | {operator} | {value} ]
  Save
  
Script Arguments:
Tautulli > Settings > Notification Agents > New Script > Script Arguments:
  
  Select: Watched
  Arguments:  --userId {user_id} --contentType {media_type}
              <episode>--youtube_id {filename}</episode>

  Save
  Close
```

# Thanks

Heavily based on https://github.com/JvSomeren/tautulli-watched-sync/
