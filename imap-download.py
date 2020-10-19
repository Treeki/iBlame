import os
import json
from imaplib import IMAP4_SSL

with open('config.json', 'r') as fp:
    config = json.load(fp)
emails_dir = config['emails_dir']

if not os.path.isdir(emails_dir):
    os.mkdir(emails_dir)

max_id = 0
for name in os.listdir(emails_dir):
    if name.endswith('.eml'):
        this_id = int(name[:name.index('.')])
        if this_id > max_id:
            max_id = this_id

with IMAP4_SSL(config['imap_ssl_hostname']) as imap:
    imap.login(config['imap_username'], config['imap_password'])
    imap.select(config['imap_folder'])
    print('max ID: %d' % max_id)
    result, mails = imap.fetch('%d:*' % (max_id + 1), '(RFC822)')
    for bit in mails:
        if len(bit) == 2:
            status, payload = bit
            print(repr(status))
            this_id = status[:status.index(b' ')]
            this_id = int(this_id.decode('ascii'))
            with open(f'{emails_dir}/{this_id}.eml', 'wb') as f:
                f.write(payload)

