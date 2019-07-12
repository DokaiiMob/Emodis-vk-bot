# /usr/bin/env python3.7
# -*- coding: utf-8 -*-
import re


class Message():
    date = 0
    from_id = 0
    id = 0
    out = 0
    peer_id = 0
    conversation_message_id = 0
    fwd_messages = 0
    important = 0
    random_id = 0
    attachments = []
    is_hidden = 0
    is_sticker = 0
    text = ''

    def __init__(self, arr_msg):
        super().__init__()
        for key in arr_msg:
            setattr(self, key, arr_msg[key])
            setattr(self, key, arr_msg[key])

    def parseAttachments(self):
        if len(self.attachments) > 0:
            str = ''
            for attach in self.attachments:
                str += attach['type'] + " "
            return str
        return ''

    # мб переписать при помощь регулярки

    def parse_bot(self):
        self.text = self.text.strip().lower()
        if re.match('работяга', self.text):
            self.text = self.text.replace(self.text[:9], '')
            return True
        if re.match("\[club183796256\|\@emodis\],", self.text):
            self.text = self.text.replace(self.text[:24], '')
            self.text = self.text.strip()
            return True
        if re.match("\[club183796256\|\@emodis\]", self.text):
            self.text = self.text.replace(self.text[:23], '')
            self.text = self.text.strip()
            return True
        return False

    def parse_users(self):
        users = re.findall(r'\w+\|@?\w+', self.text)
        if not users:
            return False
        return users
