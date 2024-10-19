#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description: Sync viewing history with TubeArchivist
Author: Phill Price

Important!
Make sure `./sync-settings.ini` is writable

Settings:
./sync-settings.ini

  [Plex]
  user_ids: a comma separated list of user ids, only entries for these users will be synced
    The user id for a user can be found in your url in Tautulli when you click on a user.

  [TubeArchivist]
  Update `url` with your TubeArchivist url and `api_token` with your TubeArchivist API Key.
  Look [here](https://docs.tubearchivist.com/api/introduction/#authentication) as for how to receive these credentials.

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
"""

import os
import sys
import requests
import json
import argparse
import datetime
import time
import uuid
import hmac
from getpass import getpass
from hashlib import sha256

from configparser import ConfigParser, NoOptionError, NoSectionError

TAUTULLI_ENCODING = os.getenv('TAUTULLI_ENCODING', 'UTF-8')

credential_path = os.path.dirname(os.path.realpath(__file__))
credential_file = 'sync_settings.ini'

config = ConfigParser()
try:
  with open('%s/%s' % (credential_path,credential_file)) as f:
    config.read_file(f)
except IOError:
  print('ERROR: %s/%s not found' % (credential_path,credential_file))
  sys.exit(1)

def arg_decoding(arg):
  """Decode args, encode UTF-8"""
  return arg.decode(TAUTULLI_ENCODING).encode('UTF-8')

def write_settings():
  """Write config back to settings file"""
  try:
    with open('%s/%s' % (credential_path,credential_file), 'w') as f:
      config.write(f)
  except IOError:
    print('ERROR: unable to write to %s/%s' % (credential_path,credential_file))
    sys.exit(1)

def sync_for_user(user_id):
  """Returns whether or not to sync for the passed user_id"""
  try:
    user_ids = config.get('Plex', 'user_ids')
  except (NoSectionError, NoOptionError):
    print('ERROR: %s not setup - missing user_ids' % credential_file)
    sys.exit(1)

  return str(user_id) in user_ids.split(',')

class TubeArchivist:
  def __init__(self, youtube_id):
    self.youtube_id = youtube_id[:-4]

    self.session = requests.Session()
    self.session.params = {}

    try:
      self.api_token = config.get('TubeArchivist', 'api_token')
    except (NoSectionError, NoOptionError):
      print('ERROR: %s not setup - missing api_token' % credential_file)
      sys.exit(1)
    try:
      self.url = config.get('TubeArchivist', 'url')
    except (NoSectionError, NoOptionError):
      print('ERROR: %s not setup - missing url' % credential_file)
      sys.exit(1)

  def prepare_request(self, method, url, data, headers):
    request = requests.Request(method.upper(), url, data=data, headers=headers)

    return self.session.prepare_request(request)

  def mark_watched(self):
    method = 'post'
    url = self.url + '/api/watched/'

    headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
    payload = {
        'id': self.youtube_id,
        "is_watched": True
    }
    payload = json.dumps(payload)

    request = self.prepare_request(method, url, payload, headers)
    request.headers['Authorization'] = 'Token ' + self.api_token

    r = self.session.send(request)

    response = r.json()
    print('Successfully logged as watched.')

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description="Syncing viewing activity to Trakt.tv and TubeArchivist.")

  parser.add_argument('--userId', required=True, type=int,
                      help='The user_id of the current user.')

  parser.add_argument('--contentType', required=True, type=str,
                      help='The type of content: episode.')

  parser.add_argument('--youtube_id', type=str,
                      help='Youtube ID.')

  opts = parser.parse_args()

  if not sync_for_user(opts.userId) and not opts.userId == -1:
    print('We will not sync for this user')
    sys.exit(0)

  if opts.contentType == 'episode':
    tubearchivist = TubeArchivist(opts.youtube_id)
    tubearchivist.mark_watched()
  else:
    print('ERROR: %s not found - invalid contentType' % opts.contentType)
