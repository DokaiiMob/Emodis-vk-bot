# /usr/bin/env python3.7
# -*- coding: utf-8 -*-

from random import randint
import re
import vk
from config import GROUP_ID
from models import *
import locale
import datetime


class CommandHandler:
    chat_id = 0
    peer_id = 0
    user_id = 0
    max_pred = 3
    expr = r'a[\W_]*s[\W_]*s(?:[\W_]*e[\W_]*s)?|f[\W_]*u[\W_]*c[\W_]*k(?:[\W_]*i[\W_]*n[\W_]*g)?|ж[\W_]*(?:[ыиiu][\W_]*[дd](?:[\W_]*[уыаyiau]|[\W_]*[оo0][\W_]*[вbv])?|[оo0][\W_]*[пnp][\W_]*(?:[аa](?:[\W_]*[хxh])?|[уеыeyiu]|[оo0][\W_]*[йj]))|[дd][\W_]*[еe][\W_]*[рpr][\W_]*(?:[ьb][\W_]*)?[мm][\W_]*[оуеаeoya0u](?:[\W_]*[мm])?|[чc][\W_]*[мm][\W_]*(?:[оo0]|[ыi][\W_]*[рpr][\W_]*[еиьяeibu])|[сsc][\W_]*[уuy][\W_]*(?:(?:[чc][\W_]*)?[кk][\W_]*[ауиiyau](?:[\W_]*[нhn](?:[\W_]*[оo0][\W_]*[йj]|[\W_]*[уаыyiau])?)?|[чc][\W_]*(?:(?:[ьb][\W_]*)?(?:[еёяиeiu]|[еиeiu][\W_]*[йj])|[аa][\W_]*[рpr][\W_]*[ыауеeyiau]))|[гrg][\W_]*(?:[аоoa0][\W_]*(?:[нhn][\W_]*[дd][\W_]*[аоoa0][\W_]*[нhn](?:[\W_]*[ыуyiu])?|[вbv][\W_]*[нhn][\W_]*[оаoa0](?:[\W_]*(?:[мm]|[еe][\W_]*[дd](?:[\W_]*[ыуаеeyiau]|[\W_]*[оаoa0][\W_]*[мm](?:[\W_]*[иiu])?)?))?)|[нhn][\W_]*(?:[иiu][\W_]*[дd][\W_]*(?:[ыуеаeyiau]|[оo0][\W_]*[йj])|[уyu][сsc](?:[\W_]*[аыуyiau]|[\W_]*[оаoa0][\W_]*[мm](?:[\W_]*[иiu])?)?))|(?:[нhn][\W_]*[еe][\W_]*)?(?:(?:[з3z][\W_]*[аa]|[оo0][тt]|[пnp][\W_]*[оo0]|[пnp][\W_]*(?:[еe][\W_]*[рpr][\W_]*[еe]|[рpr][\W_]*[оеиeiou0]|[иiu][\W_]*[з3z][\W_]*[дd][\W_]*[оo0])|[нhn][\W_]*[аa]|[иiu][\W_]*[з3z]|[дd][\W_]*[оo0]|[вbv][\W_]*[ыi]|[уyu]|[рpr][\W_]*[аa][\W_]*[з3z]|[з3z][\W_]*[лl][\W_]*[оo0]|[тt][\W_]*[рpr][\W_]*[оo0]|[уyu])[\W_]*)?(?:[вbv][\W_]*[ыi][\W_]*)?(?:[ъьb][\W_]*)?(?:[еёe][\W_]*[бb6](?:(?:[\W_]*[оеёаиуeioyau0])?(?:[\W_]*[нhn](?:[\W_]*[нhn])?[\W_]*[яуаиьiybau]?)?(?:[\W_]*[вbv][\W_]*[аa])?(?:(?:[\W_]*(?:[иеeiu]ш[\W_]*[ьb][\W_]*[сsc][\W_]*я|[тt][\W_]*(?:(?:[ьb][\W_]*)?[сsc][\W_]*я|[ьb]|[еe][\W_]*[сsc][\W_]*[ьb]|[еe]|[оo0]|[иiu][\W_]*[нhn][\W_]*[уыеаeyiau])|(?:щ[\W_]*(?:[иiu][\W_]*[йj]|[аa][\W_]*я|[иеeiu][\W_]*[еe]|[еe][\W_]*[гrg][\W_]*[оo0])|ю[\W_]*[тt])(?:[\W_]*[сsc][\W_]*я)?|[еe][\W_]*[мтmt]|[кk](?:[\W_]*[иаiau])?|[аa][\W_]*[лl](?:[\W_]*[сsc][\W_]*я)?|[лl][\W_]*(?:[аa][\W_]*[нhn]|[оаoa0](?:[\W_]*[мm])?|(?:[иiu][\W_]*)?[сsc][\W_]*[ьяb]|[иiu]|[аa][\W_]*[сsc][\W_]*[ьb])|[рpr][\W_]*[ьb]|[сsc][\W_]*[яьb]|[нhn][\W_]*[оo0]|[чc][\W_]*(?:[иiu][\W_]*[хxh]|[еe][\W_]*[сsc][\W_]*[тt][\W_]*[ьиibu](?:[\W_]*ю)?)|(?:[тt][\W_]*[еe][\W_]*[лl][\W_]*[ьb][\W_]*[сsc][\W_]*[кk][\W_]*|[сsc][\W_]*[тt][\W_]*|[лl][\W_]*[иiu][\W_]*[вbv][\W_]*|[чтtc][\W_]*)?(?:[аa][\W_]*я|[оo0][\W_]*[йемejm]|[ыi][\W_]*[хйеejxh]|[ыi][\W_]*[мm](?:[\W_]*[иiu])?|[уyu][\W_]*ю|[иiu][\W_]*[еe]|[оo0][\W_]*[мm][\W_]*[уyu]|[иiu][\W_]*[йj]|[еe][\W_]*[вbv]|[иiu][\W_]*[мm](?:[\W_]*[иiu])?)|[чтыйилijltcu]))?)|[\W_]*[ыi](?:(?:[\W_]*[вbv][\W_]*[аa]|[\W_]*[нhn](?:[\W_]*[нhn])?)(?:(?:[\W_]*(?:[иеeiu]ш[\W_]*[ьb][\W_]*[сsc][\W_]*я|[тt][\W_]*(?:[ьb][\W_]*[сsc][\W_]*я|[ьb]|[еe][\W_]*[сsc][\W_]*[ьb]|[еe]|[иiu][\W_]*[нhn][\W_]*[уыеаeyiau])|(?:щ[\W_]*(?:[иiu][\W_]*[йj]|[аa][\W_]*я|[иеeiu][\W_]*[еe]|[еe][\W_]*[гrg][\W_]*[оo0])|ю[\W_]*[тt])(?:[\W_]*[сsc][\W_]*я)?|[еe][\W_]*[мтmt]|[лl][\W_]*(?:(?:[иiu][\W_]*)?[сsc][\W_]*[ьяb]|[иiu]|[аa][\W_]*[сsc][\W_]*[ьb])|(?:[сsc][\W_]*[тt][\W_]*|[лl][\W_]*[иiu][\W_]*[вbv][\W_]*|[чтtc][\W_]*)?(?:[аa][\W_]*я|[оo0][\W_]*[йемejm]|[ыi][\W_]*[хйеejxh]|[ыi][\W_]*[мm](?:[\W_]*[иiu])?|[уyu][\W_]*ю|[иiu][\W_]*[еe]|[оo0][\W_]*[мm][\W_]*[уyu]|[иiu][\W_]*[йj]|[еe][\W_]*[вbv]|[иiu][\W_]*[мm](?:[\W_]*[иiu])?))))|[рpr][\W_]*[ьb]))|я[\W_]*[бb6](?:[\W_]*[оеёаиуeioyau0])?(?:(?:[\W_]*[нhn](?:[\W_]*[нhn])?[\W_]*[яуаиьiybau]?)?(?:(?:[\W_]*(?:[иеeiu]ш[\W_]*[ьb][\W_]*[сsc][\W_]*я|[тt][\W_]*(?:[ьb][\W_]*[сsc][\W_]*я|[ьb]|[еe][\W_]*[сsc][\W_]*[ьb]|[еe]|[иiu][\W_]*[нhn][\W_]*[уыеаeyiau])|(?:щ[\W_]*(?:[иiu][\W_]*[йj]|[аa][\W_]*я|[иеeiu][\W_]*[еe]|[еe][\W_]*[гrg][\W_]*[оo0])|ю[\W_]*[тt])(?:[\W_]*[сsc][\W_]*я)?|[еe][\W_]*[мтmt]|[кk](?:[\W_]*[иаiau])?|[аa][\W_]*[лl](?:[\W_]*[сsc][\W_]*я)?|[лl][\W_]*(?:[аa][\W_]*[нhn]|[оаoa0](?:[\W_]*[мm])?|(?:[иiu][\W_]*)?[сsc][\W_]*[ьяb]|[иiu])|[рpr][\W_]*[ьb]|[сsc][\W_]*[яьb]|[нhn][\W_]*[оo0]|[чc][\W_]*(?:[иiu][\W_]*[хxh]|[еe][\W_]*[сsc][\W_]*[тt][\W_]*[ьиibu](?:[\W_]*ю)?)|(?:[тt][\W_]*[еe][\W_]*[лl][\W_]*[ьb][\W_]*[сsc][\W_]*[кk][\W_]*|[сsc][\W_]*[тt][\W_]*|[лl][\W_]*[иiu][\W_]*[вbv][\W_]*|[чтtc][\W_]*)?(?:[аa][\W_]*я|[оo0][\W_]*[йемejm]|[ыi][\W_]*[хйеejxh]|[ыi][\W_]*[мm](?:[\W_]*[иiu])?|[уyu][\W_]*ю|[иiu][\W_]*[еe]|[оo0][\W_]*[мm][\W_]*[уyu]|[иiu][\W_]*[йj]|[еe][\W_]*[вbv]|[иiu][\W_]*[мm](?:[\W_]*[иiu])?)|[чмйилijlmcu]))|(?:[\W_]*[нhn](?:[\W_]*[нhn])?[\W_]*[яуаиьiybau]?)))|я[\W_]*[бb6][\W_]*(?:[еёаиуeiyau][\W_]*)?(?:[нhn][\W_]*(?:[нhn][\W_]*)?(?:[яуаиьiybau][\W_]*)?)?[тt])|[сsc][\W_]*[ьъb][\W_]*[еяёe][\W_]*[бb6][\W_]*(?:[уyu]|(?:[еиёауeiyau](?:[\W_]*[лl](?:[\W_]*[иоаioau0])?|[\W_]*ш[\W_]*[ьb]|[\W_]*[тt][\W_]*[еe])?(?:[\W_]*[сsc][\W_]*[ьяb])?))|[еe][\W_]*(?:[бb6][\W_]*(?:[уyu][\W_]*[кk][\W_]*[еe][\W_]*[нhn][\W_]*[тt][\W_]*[иiu][\W_]*[йj]|[еe][\W_]*[нhn][\W_]*(?:[ьb]|я(?:[\W_]*[мm])?)|[иiu][\W_]*(?:[цc][\W_]*[кk][\W_]*[аa][\W_]*я|[чc][\W_]*[еe][\W_]*[сsc][\W_]*[кk][\W_]*[аa][\W_]*я)|[лl][\W_]*[иiu][\W_]*щ[\W_]*[еe]|[аa][\W_]*(?:[лl][\W_]*[ьb][\W_]*[нhn][\W_]*[иiu][\W_]*[кk](?:[\W_]*[иаiau])?|[тt][\W_]*[оo0][\W_]*[рpr][\W_]*[иiu][\W_]*[йj]|[нhn][\W_]*(?:[тt][\W_]*[рpr][\W_]*[оo0][\W_]*[пnp]|[аa][\W_]*[тt][\W_]*[иiu][\W_]*(?:[кk]|[чc][\W_]*[еe][\W_]*[сsc][\W_]*[кk][\W_]*[иiu][\W_]*[йj]))))|[дd][\W_]*[рpr][\W_]*[иiu][\W_]*[тt])|[нhn][\W_]*[еe][\W_]*[вbv][\W_]*[рpr][\W_]*[оo0][\W_]*[тt][\W_]*ъ[\W_]*[еe][\W_]*[бb6][\W_]*[аa][\W_]*[тt][\W_]*[еe][\W_]*[лl][\W_]*[ьb][\W_]*[сsc][\W_]*[кk][\W_]*[иiu][\W_]*(?:[ыиiu][\W_]*[йj]|[аa][\W_]*я|[оo0][\W_]*[ейej]|[ыi][\W_]*[хxh]|[ыi][\W_]*[еe]|[ыi][\W_]*[мm](?:[\W_]*[иiu])?|[уyu][\W_]*ю|[оo0][\W_]*[мm][\W_]*[уyu])|[уyu][\W_]*(?:[ёеe][\W_]*[бb6][\W_]*(?:[иiu][\W_]*щ[\W_]*[еаea]|[аa][\W_]*[нhn](?:[\W_]*[тt][\W_]*[уyu][\W_]*[сsc])?(?:[\W_]*[аоoa0][\W_]*[вмbmv]|[\W_]*[ыуеаeyiau])?)|[рpr][\W_]*[оo0][\W_]*[дd](?:[\W_]*[аоoa0][\W_]*[вмbmv]|[\W_]*[ыуеаeyiau])?|[бb6][\W_]*[лl][\W_]*ю[\W_]*[дd][\W_]*(?:[оo0][\W_]*[кk]|[кk][\W_]*(?:[аоoa0][\W_]*[вмbmv](?:[\W_]*[иiu])?|[иуеаeiyau])?))|[мm][\W_]*(?:[уyu][\W_]*[дd][\W_]*(?:[оo0][\W_]*[хxh][\W_]*[аa][\W_]*(?:[тt][\W_]*[ьb][\W_]*[сsc][\W_]*я|ю[\W_]*[сsc][\W_]*[ьb]|[еe][\W_]*ш[\W_]*[ьb][\W_]*[сsc][\W_]*я)|[аa][\W_]*(?:[кk](?:[\W_]*[иаiau]|[оo0][мвbmv])?|[чc][\W_]*(?:[ьb][\W_]*[еёe]|[иiu][\W_]*[нhn][\W_]*[уыаyiau]|[кk][\W_]*(?:[аиеуeiyau]|[оo0][\W_]*[йj])))|[еe][\W_]*[нhn][\W_]*[ьb]|[иiu][\W_]*[лl](?:[\W_]*[аеоыeoia0]?))|[аa][\W_]*[нhn][\W_]*[дd][\W_]*[уаyau]|[лl][\W_]*(?:[иiu][\W_]*[нhn]|я))|(?:[мm][\W_]*(?:[оo0][\W_]*[з3z][\W_]*[гrg]|[уyu][\W_]*[дd])|[дd][\W_]*(?:[оo0][\W_]*[лl][\W_]*[бb6]|[уyu][\W_]*[рpr])|[сsc][\W_]*[кk][\W_]*[оo0][\W_]*[тt]|ж[\W_]*[иiu][\W_]*[дd])[\W_]*[аоoa0][\W_]*(?:[хxh][\W_]*[уyu][\W_]*[ийяiju]|[ёеe][\W_]*[бb6](?:[\W_]*[еоeo0][\W_]*[вbv]|[\W_]*[ыаia]|[\W_]*[сsc][\W_]*[тt][\W_]*[вbv][\W_]*[оуoy0u](?:[\W_]*[мm])?|[иiu][\W_]*[з3z][\W_]*[мm])?)|(?:[нhn][\W_]*[еe][\W_]*|[з3z][\W_]*[аa][\W_]*|[оo0][\W_]*[тt][\W_]*|[пnp][\W_]*[оo0][\W_]*|[нhn][\W_]*[аa][\W_]*|[рpr][\W_]*[аa][\W_]*[сз3szc][\W_]*)?(?:[пnp][\W_]*[иiu][\W_]*[з3z][\W_]*[дd][\W_]*[ияеeiu]|(?:ъ)?[еёe][\W_]*[бb6][\W_]*[аa])[\W_]*(?:(?:[тt][\W_]*[ьb][\W_]*[сsc][\W_]*я|[тt][\W_]*[ьb]|[лl][\W_]*[иiu]|[аa][\W_]*[лl]|[лl]|c[\W_]*[ьb]|[иiu][\W_]*[тt]|[иiu]|[тt][\W_]*[еe]|[чc][\W_]*[уyu]|ш[\W_]*[ьb])|(?:[йяиiju]|[иеeiu][\W_]*[мm](?:[\W_]*[иiu])?|[йj][\W_]*[сsc][\W_]*(?:[кk][\W_]*(?:[ыиiu][\W_]*[йеej]|[аa][\W_]*я|[оo0][\W_]*[еe]|[ыi][\W_]*[хxh]|[ыi][\W_]*[мm](?:[\W_]*[иiu])?|[уyu][\W_]*ю|[оo0][\W_]*[мm][\W_]*[уyu])|[тt][\W_]*[вbv][\W_]*[оуаoya0u](?:[\W_]*[мm])?)))|[пnp][\W_]*[еиыeiu][\W_]*[дd][\W_]*[аеэоeoa0][\W_]*[рpr](?:(?:[\W_]*[аa][\W_]*[сз3szc](?:(?:[\W_]*[тt])?(?:[\W_]*[ыi]|[\W_]*[оаoa0][\W_]*[мm](?:[\W_]*[иiu])?|[\W_]*[кk][\W_]*[аиiau])?|(?:[\W_]*[ыуаеeyiau]|[\W_]*[оаoa0][\W_]*[мm](?:[\W_]*[иiu])?|[\W_]*[оo0][\W_]*[вbv])))|[\W_]*(?:[ыуаеeyiau]|[оаoa0][\W_]*[мm](?:[\W_]*[иiu])?|[оo0][\W_]*[вbv]|[нhn][\W_]*я))?|[пnp][\W_]*[иiu][\W_]*[з3z][\W_]*(?:[ьb][\W_]*)?[дd][\W_]*(?:[ёеe][\W_]*(?:[нhn][\W_]*[ыi][\W_]*ш(?:[\W_]*[ьb])?|[шнжhn](?:[\W_]*[ьb])?)|[уyu][\W_]*(?:[йj](?:[\W_]*[тt][\W_]*[еe])?|[нhn](?:[\W_]*[ыi])?)|ю[\W_]*(?:[кk](?:[\W_]*(?:[аеуиeiyau]|[оo0][\W_]*[вbv]|[аa][\W_]*[мm](?:[\W_]*[иiu])?))?|[лl](?:[ьиibu]|[еe][\W_]*[йj]|я[\W_]*[хмmxh]))|[еe][\W_]*[цc]|[аоoa0][\W_]*(?:[нhn][\W_]*[уyu][\W_]*)?[тt][\W_]*(?:[иiu][\W_]*[йj]|[аa][\W_]*я|[оo0](?:[\W_]*[ейej])?|[ыi][\W_]*[ейхejxh]|[ыi][\W_]*[мm](?:[\W_]*[иiu])?|[уyu][\W_]*ю|[оo0][\W_]*[мm][\W_]*[уyu]|[еe][\W_]*[еe]|[ауьеыeyibau])|[аa][\W_]*[нhn][\W_]*[уyu][\W_]*[лl](?:[\W_]*[аиiau])?|[ыеуиаeiyau]|[оаoa0][\W_]*(?:[йj]|[хxh][\W_]*[уyu][\W_]*[йj]|[еёe][\W_]*[бb6]|(?:[рpr][\W_]*[оo0][\W_]*[тt]|[гrg][\W_]*[оo0][\W_]*[лl][\W_]*[оo0][\W_]*[вbv])[\W_]*(?:[ыиiu][\W_]*[йj]|[аa][\W_]*я|[оo0][\W_]*[ейej]|[ыi][\W_]*[хxh]|[ыi][\W_]*[еe]|[ыi][\W_]*[мm](?:[\W_]*[иiu])?|[уyu][\W_]*ю|[оo0][\W_]*[мm][\W_]*[уyu])|[бb6][\W_]*(?:[рpr][\W_]*[аa][\W_]*[тt][\W_]*[иiu][\W_]*я|[оo0][\W_]*[лl](?:[\W_]*[аыуyiau])?)))|[пnp][\W_]*(?:[аa][\W_]*[дd][\W_]*[лl][\W_]*[аоыoia0]|[оаoa0][\W_]*[сsc][\W_]*[кk][\W_]*[уyu][\W_]*[дd][\W_]*(?:[ыуаеeyiau]|[оаoa0][\W_]*[мm](?:[\W_]*[иiu])?)|[иеeiu][\W_]*[дd][\W_]*(?:[иiu][\W_]*[кk]|[рpr][\W_]*[иiu][\W_]*[лl](?:[\W_]*[лl])?)(?:[\W_]*[оаoa0][\W_]*[мвbmv]|[\W_]*[иуеоыаeioyau0])?|[рpr][\W_]*[оo0][\W_]*[бb6][\W_]*[лl][\W_]*я[\W_]*[дd][\W_]*[оo0][\W_]*[мm])|(?:[з3z][\W_]*[аa][\W_]*|[оo0][\W_]*[тt][\W_]*|[нhn][\W_]*[аa][\W_]*)?[сsc][\W_]*[рpr][\W_]*(?:[аa][\W_]*[тt][\W_]*[ьb]|[аa][\W_]*[лl](?:[\W_]*[иiu])?|[eуиiyu])|[сsc][\W_]*[рpr][\W_]*[аa][\W_]*(?:[кk][\W_]*(?:[аеиуeiyau]|[оo0][\W_]*[йj])|[нhn](?:[\W_]*[нhn])?(?:[ьb]|(?:[\W_]*[ыi][\W_]*[йеej]|[\W_]*[аa][\W_]*я|[\W_]*[оo0][\W_]*[еe]))|[лl][\W_]*[ьb][\W_]*[нhn][\W_]*[иiu][\W_]*[кk](?:[\W_]*[иiu]|[\W_]*[оаoa0][\W_]*[мm])?)|(?:[з3z][\W_]*[аa][\W_]*)?[тt][\W_]*[рpr][\W_]*[аa][\W_]*[хxh][\W_]*(?:[нhn][\W_]*(?:[уyu](?:[\W_]*[тt][\W_]*[ьb](?:[\W_]*[сsc][\W_]*я)?|[\W_]*[сsc][\W_]*[ьb]|[\W_]*[лl](?:[\W_]*[аиiau])?)?|[еиeiu][\W_]*ш[\W_]*[ьb][\W_]*[сsc][\W_]*я)|[аa][\W_]*(?:[лl](?:[\W_]*[аоиioau0])?|[тt][\W_]*[ьb](?:[\W_]*[сsc][\W_]*я)?|[нhn][\W_]*(?:[нhn][\W_]*)?(?:[ыиiu][\W_]*[йj]|[аa][\W_]*я|[оo0][\W_]*[йеej]|[ыi][\W_]*[хxh]|[ыi][\W_]*[еe]|[ыi][\W_]*[мm](?:[\W_]*[иiu])?|[уyu][\W_]*ю|[оo0][\W_]*[мm][\W_]*[уyu])))|(?:[нhn][\W_]*[иеeiu][\W_]*|[пnp][\W_]*[оo0][\W_]*|[нhn][\W_]*[аa][\W_]*|[оаoa0][\W_]*(?:[тt][\W_]*)?|[дd][\W_]*[аоoa0][\W_]*|[з3z][\W_]*[аa][\W_]*)?(?:(?:[фf][\W_]*[иiu][\W_]*[гrg]|[хxh][\W_]*(?:[еиeiu][\W_]*(?:[йj][\W_]*)?[рpr]|[рpr][\W_]*[еe][\W_]*[нhn]|[уyu](?:[\W_]*[йj])?))(?:[\W_]*[еоёeo0][\W_]*[вbv](?:[\W_]*[аa][\W_]*ю[\W_]*щ|[\W_]*ш)?)?(?:[\W_]*[аиеeiau][\W_]*[лнlhn])?(?:[нhn])?(?:[\W_]*(?:[иаоёяыеeioau0][юяиевмйbeijmvu]|я[\W_]*(?:[мm](?:[\W_]*[иiu])?|[рpr][\W_]*(?:ю|[иiu][\W_]*(?:[тt](?:[\W_]*[ьеeb][\W_]*[сsc][\W_]*[яьb])?|[лl](?:[\W_]*[иоаioau0])?))|[чc][\W_]*(?:[аиiau][\W_]*[тt](?:[\W_]*[сsc][\W_]*я)|[иiu][\W_]*[лl](?:[\W_]*[иоаioau0])?)|[чc](?:[\W_]*[ьb])?)|[еe][\W_]*(?:[тt][\W_]*(?:[оo0][\W_]*[йj]|[аьуybau])|[еe][\W_]*(?:[тt][\W_]*[еe]|ш[\W_]*[ьb]))|[аыоуяюйиijoyau0]|[лl][\W_]*[иоiou0]|[чc][\W_]*[уyu])))|(?:[фf][\W_]*[иiu][\W_]*[гrg]|[хxh][\W_]*(?:[еиeiu][\W_]*(?:[йj][\W_]*)?[рpr]|[рpr][\W_]*[еe][\W_]*[нhn]|[уyu][\W_]*[йj]))|[хxh][\W_]*[уyu][\W_]*(?:[еёиeiu][\W_]*(?:[сsc][\W_]*[оo0][\W_]*[сsc]|[пnp][\W_]*[лl][\W_]*[еe][\W_]*[тt]|[нhn][\W_]*[ыi][\W_]*ш)(?:[\W_]*[аыуyiau]|[\W_]*[оаoa0][\W_]*[мm](?:[\W_]*[иiu])?|[нhn][\W_]*(?:[ыиiu][\W_]*[йj]|[аa][\W_]*я|[оo0][\W_]*[йеej]|[ыi][\W_]*[хxh]|[ыi][\W_]*[еe]|[ыi][\W_]*[мm](?:[\W_]*[иiu])?|[уyu][\W_]*ю|[оo0][\W_]*[мm][\W_]*[уyu]))?|[дd][\W_]*[оo0][\W_]*ё[\W_]*[бb6][\W_]*[иiu][\W_]*[нhn][\W_]*(?:[оo0][\W_]*[йj]|[аеыуeyiau]))|[бb6][\W_]*[лl][\W_]*я(?:[\W_]*[дтdt][\W_]*(?:[ьb]|[иiu]|[кk][\W_]*[иiu]|[сsc][\W_]*[тt][\W_]*[вbv][\W_]*[оo0]|[сsc][\W_]*[кk][\W_]*(?:[оo0][\W_]*[ейej]|[иiu][\W_]*[еe]|[аa][\W_]*я|[иiu][\W_]*[йj]|[оo0][\W_]*[гrg][\W_]*[оo0])))?|[вbv][\W_]*[ыi][\W_]*[бb6][\W_]*[лl][\W_]*я[\W_]*[дd][\W_]*(?:[оo0][\W_]*[кk]|[кk][\W_]*(?:[иуаеeiyau]|[аa][\W_]*[мm](?:[\W_]*[иiu])?))|(?:[з3z][\W_]*[аоoa0][\W_]*)(?:[пnp][\W_]*[аоoa0][\W_]*[дd][\W_]*[лl][\W_]*[оыаoia0]|[лl][\W_]*[уyu][\W_]*[пnp][\W_]*(?:[оo0][\W_]*[йj]|[аеыуeyiau]))|ш[\W_]*[лl][\W_]*ю[\W_]*[хxh][\W_]*(?:[ауеиeiyau]|[оo0][\W_]*[йj])|[аa][\W_]*[нhn][\W_]*[уyu][\W_]*[сsc](?:[\W_]*[еаыуeyiau]|[\W_]*[оo0][\W_]*[мm])?|(?:\w*(?:[хxh](?:[рpr][еe][нhn]|[уyu][иiu])|[пnp][еиeiu](?:[з3z][дd]|[дd](?:[еаоeoa0][рpr]|[рpr]))|[бb6][лl]я[дd]|[оo0][хxh][уyu][еe]|[мm][уyu][дd][еоиаeioau0]|[дd][еe][рpr][ьb]|[гrg][аоoa0][вbv][нhn]|[уyu][еёe][бb6])|[хxh][\W_]*(?:[рpr][\W_]*[еe][\W_]*[нhn]|[уyu][\W_]*[йиеяeiju])|[пnp][\W_]*[еиeiu][\W_]*(?:[з3z][\W_]*[дd]|[дd][\W_]*(?:[еаоeoa0][\W_]*[рpr]|[рpr]))|[бb6][\W_]*[лl][\W_]*я[\W_]*[дd]|[оo0][\W_]*[хxh][\W_]*[уyu][\W_]*[еe]|[мm][\W_]*[уyu][\W_]*[дd][\W_]*[еоиаeioau0]|[дd][\W_]*[еe][\W_]*[рpr][\W_]*[ьb]|[гrg][\W_]*[аоoa0][\W_]*[вbv][\W_]*[нhn]|[уyu][\W_]*[еёe][\W_]*[бb6]|[ёеe][бb6])\w+'

    def __init__(self, api):
        self.api = api

    def set_peer_id(self, peer_id):
        self.peer_id = peer_id

    def find_update_user(self, member_id):
        user = find_user(member_id)
        if len(user.full_name) == 0:
            user.full_name = self.api_full_name(user.id)
            user.save()

    def check_slang(self, string):
        self.expr = r'(?:\b|(?<=_))(?:' + self.expr + r')(?:\b|(?=_))'
        p = re.compile(self.expr, re.IGNORECASE)
        match = p.search(string)
        if match:
            return True
        return False

    def is_chat_invite_user(self, member_id):
        if member_id > 0:
            self.find_update_user(member_id)
            stats = find_stats_addit_user_and_chat(member_id, self.chat_id)
            if stats.is_banned == 1:
                self.remove_chat_user(member_id)

        if member_id < 0:
            print("Here adding to chat another bot")
        if member_id == -GROUP_ID:
            try:
                for chat_user in self.getConversationMembers():
                    self.find_update_user(chat_user['from_id'])
            except vk.exceptions.VkAPIError:
                self.send_msg(msg=get_hello(self.peer_id))

    def api_full_name(self, user_id):
        name = self.api.users.get(user_ids=user_id)[0]
        return "{0} {1}".format(name['first_name'], name['last_name'])

    def send_msg(self, msg):
        self.api.messages.send(peer_id=self.peer_id, random_id=randint(
            -2147483647, 2147483647), message=msg)

    def getConversationsById(self):
        try:
            chat_data = self.api.messages.getConversationsById(
                peer_ids=self.peer_id, group_id=GROUP_ID)
            if chat_data['items']:
                if chat_data['items'][0]:
                    return chat_data['items'][0]['chat_settings']
        except vk.exceptions.VkAPIError:
            return False

    def getConversationMembers(self):
        return self.api.messages.getConversationMembers(peer_id=self.peer_id, group_id=GROUP_ID)['profiles']

    def parse_attachments(self, attachments):
        if len(attachments) > 0:
            str = ''
            for attach in attachments:
                str += attach['type'] + " "
            return str
        return ''

    def parse_bot(self, text):
        text = text.strip()
        if re.match('работяга', text.lower()):
            text = text.replace(text[:9], '')
            return True, text.strip()
        if re.match("\[club183796256\|\@emodis\],", text.lower()):
            text = text.replace(text[:24], '')
            return True, text.strip()
        if re.match("\[club183796256\|\@emodis\]", text.lower()):
            text = text.replace(text[:23], '')
            return True, text.strip()
        return False, text

    def parse_users(self, text):
        users = re.findall(r'\w+\|@?\w+', text)
        if not users:
            return False
        return users

    def get_top(self):
        self.send_msg(find_all_users_by_msg(self.chat_id))

    def get_help(self):
        self.send_msg(msg=get_help())

    def get_choise(self, text):
        msg = text.replace(text[:6], '')
        array = msg.split('или')
        self.send_msg(msg="Я выбираю {0}".format(
            array[randint(0, len(array) - 1)]))

    def get_inform(self):
        self.send_msg(msg=get_random())

    def get_preds(self):
        exist = False
        msg = 'Все предупреждения:\n'
        index = 1
        for p in get_preds_db(self.chat_id, self.user_id):
            exist = True
            name = self.api.users.get(user_ids=p.id_user)[0]
            msg += "#{0} {1} {2} {3}\n".format(index,
                                               name['first_name'], name['last_name'], p.is_pred)
            index = index + 1
        if exist:
            self.send_msg(msg=msg)
        else:
            self.send_msg(msg="Предупреждений в чате нет")

    def get_bans(self):
        msg = 'Все блокировки:\n'
        index = 1
        exist = False
        for p in get_bans_db(self.chat_id, self.user_id):
            exist = True
            name = self.api.users.get(user_ids=p.id_user)[0]
            msg += "#{0} {1} {2}\n".format(index,
                                           name['first_name'], name['last_name'])
            index = index + 1
        if exist:
            self.send_msg(msg=msg)
        else:
            self.send_msg(msg="Блокировок в чате нет")

    def remove_chat_user(self, id):
        try:
            self.api.messages.removeChatUser(
                chat_id=self.chat_id, member_id=id)
            return True
        except vk.exceptions.VkAPIError:
            self.send_msg(msg=not_access())
            return False

    def give_pred_by_id(self, user_id, msg):
        stats = find_stats_addit_user_and_chat(user_id, self.chat_id)
        stats.is_pred = stats.is_pred + 1
        stats.save()
        if int(stats.is_pred) >= int(self.max_pred):
            # По сути надо выбирать что делать роботу
            # stats.is_banned = 1
            # stats.is_pred = 0
            # self.send_msg(msg="Лимит предупреждений! Кик :-)")
            # И парсить максимальное кол-во
            self.remove_chat_user(user_id)
        self.send_msg(msg=msg + ' ' + get_pred(stats.is_pred, self.max_pred))

    def pred(self, users):
        for user in users:
            if re.match('id', user.split('|')[0]):
                id = user.split('|')[0].split('id')[1]
                stats = find_stats_addit_user_and_chat(id, self.chat_id)
                stats.is_pred = stats.is_pred + 1
                stats.save()

                if int(stats.is_pred) >= int(self.max_pred):
                    # По сути надо выбирать что делать роботу
                    # stats.is_banned = 1
                    # stats.is_pred = 0
                    # self.send_msg(msg="Лимит предупреждений! Кик :-)")
                    # И парсить максимальное кол-во
                    self.remove_chat_user(id)
                self.send_msg(msg=get_pred(stats.is_pred, self.max_pred))

    def kick(self, users):
        for user in users:
            if re.match('id', user.split('|')[0]):
                self.remove_chat_user(user.split('|')[0].split('id')[1])

    def ban(self, users):
        for user in users:
            if re.match('id', user.split('|')[0]):
                id = user.split('|')[0].split('id')[1]
                stats = find_stats_addit_user_and_chat(id, self.chat_id)
                stats.is_banned = 1 if self.remove_chat_user(id) else 0
                stats.save()

    def ban_off(self, users):
        for user in users:
            if re.match('id', user.split('|')[0]):
                id = user.split('|')[0].split('id')[1]
                stats = find_stats_addit_user_and_chat(id, self.chat_id)
                stats.is_banned = 0
                stats.is_pred = 0
                stats.save()

    def pred_off(self, users):
        for user in users:
            if re.match('id', user.split('|')[0]):
                id = user.split('|')[0].split('id')[1]
                stats = find_stats_addit_user_and_chat(id, self.chat_id)
                stats.is_pred = 0
                stats.save()

    def dog_kick(self):
        for chat_user in self.api.messages.getConversationMembers(peer_id=self.peer_id, group_id=GROUP_ID)['profiles']:
            dog_exist = False
            if chat_user.get('deactivated'):
                if self.remove_chat_user(chat_user['id']):
                    dog_exist = True
        if not dog_exist:
            self.send_msg(msg=get_delete_dogs_not())
        else:
            self.send_msg(msg=get_delete_dogs())

    def get_need_lvl(self, old):
        all_count_msgs = find_all_stats_sum(
            self.user_id, self.chat_id).count_msgs
        if round(int(all_count_msgs) ** 0.2) > old:
            return round(int(all_count_msgs) ** 0.2)
        else:
            return old

    def get_married(self, user):
        if re.match('id', user.split('|')[0]):
            id = user.split('|')[0].split('id')[1]
            marryed = add_marrieds(self.user_id, id, self.chat_id)
            if marryed == 1:
                self.send_msg(
                    msg="Нужно подтвердить другому участнику, написав Работяга брак да/нет")
            if marryed == 0:
                self.send_msg(msg="Брак невозможен")

    def get_all_marry(self):
        m = get_marryieds(self.chat_id)
        if m:
            msg = 'Все браки: \n'
            index = 1
            time = datetime.datetime.now()
            for mr in m:
                msg += "#{0} {1} и {2} {3} дн.\n".format(
                    index, mr.id_user_one.full_name, mr.id_user_two.full_name, abs(time - mr.date_time).days)
                index = index + 1
            self.send_msg(msg=msg)
        else:
            self.send_msg(msg="Браков ещё нет")

    def delete_married(self):
        if del_marry(self.chat_id, self.user_id):
            self.send_msg(msg="В браке отказано:)")

    def remove_married(self):
        if del_marry_all(self.chat_id, self.user_id):
            self.send_msg(msg="Брак аннулирован:)")

    def save_married(self):
        if done_marry(self.chat_id, self.user_id):
            self.send_msg(msg="Поздравляю:)")

    def settings(self, text):
        text_array = text.split(' ')
        if len(text_array) >= 2:
            type_set = int(text_array[0])
            val = text_array[1]
            if type_set == 1:
                if int(val) == 0 or int(val) == 1:
                    settings_set(self.chat_id, type_set, val)
                    return True
            if type_set == 2:
                if int(val) == 0 or int(val) == 1:
                    settings_set(self.chat_id, type_set, val)
                    return True
            if type_set == 3:
                settings_set(self.chat_id, type_set, val)
                return True
            if type_set == 4:
                if int(val) == 0 or int(val) == 1:
                    settings_set(self.chat_id, type_set, val)
                    return True
        return False

    def is_admin(self):
        try:
            chat_users = self.api.messages.getConversationMembers(
                peer_id=self.peer_id, group_id=GROUP_ID)['items']
            for chat_user in chat_users:
                if self.user_id == chat_user['member_id'] and chat_user.get('is_admin'):
                    return True
        except vk.exceptions.VkAPIError:
            return False
        return False

    def parse_command(self, text, user_id):

        self.user_id = user_id

        if re.match('топ', text):
            self.get_top()
            return True

        if re.match('выбери', text):
            self.get_choise(text)
            return True

        if re.match('инфа', text):
            self.get_inform()
            return True

        if re.match('все', text):
            text = text.replace(text[:4], '')

            if re.match('преды', text):
                self.get_preds()
                return True

            if re.match('баны', text):
                self.get_bans()
                return True

            if re.match('браки', text):
                self.get_all_marry()
                return True

        if re.match('развод', text):
            self.remove_married()
            return True

        if re.match('брак', text):
            text = text.replace(text[:5], '')
            if re.match('нет', text):
                self.delete_married()
                return True
            if re.match('да', text):
                self.save_married()
                return True
            users = self.parse_users(text)
            if users:
                self.get_married(users[0])
            return True

        if self.is_admin():
            if re.match('настройка', text):
                kek = self.settings(text.replace(text[:10], ''))
                if kek:
                    self.send_msg(msg="Сохранено!")
                return True

            if re.match('исключить собачек', text):
                self.dog_kick()
                return True

            if re.match('снять', text):
                text = text.replace(text[:6], '')
                if re.match('пред', text):
                    users = self.parse_users(text)
                    if users:
                        self.pred_off(users)
                        self.send_msg(msg="Готово!")
                    return True

                if re.match('бан', text):
                    users = self.parse_users(text)
                    if users:
                        self.ban_off(users)
                        self.send_msg(msg="Готово!")
                    return True

            if re.match('бан', text):
                users = self.parse_users(text)
                if users:
                    self.ban(users)
                return True

            if re.match('пред', text):
                users = self.parse_users(text)
                if users:
                    self.pred(users)
                return True

            if re.match('кик', text):
                users = self.parse_users(text)
                if users:
                    self.kick(users)
                return True
