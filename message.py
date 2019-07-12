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
        if self.text.find('работяга') == 0:
            return True
        else:
            return False

    def parse_command(self):
        # переписать
        # re.match("помощь", self.text)
        if self.text.find('помощь') == 9:
            return 'help', 'msg'
        if self.text.find('рандом') == 9:
            return 'random', 'msg'
        if self.text.find('выбери') == 9:
            return 'random_array', 'msg'
        if self.text.find('кик') == 9:
            return 'kick', 'do'
        return '','msg'            
    
    def parse_users(self):
        users = re.findall(r'\w+\|\w+', self.text)
        if not users:
            return False
        +