import os
import json
import codecs
from flask import request

#자체 json 파일로 번역본 인용
def json_to_verse(ver, book, chp, bib):
    path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

    if bib == "old" :
        book_code = {
            "Genesis": 0, "Exodus": 1, "Leviticus": 2, "Numbers": 3, "Deuteronomy": 4, "Joshua": 5, "Judges": 6, "Ruth": 7,
            "1_Samuel": 8, "2_Samuel": 9, "1_Kings": 10, "2_Kings": 11, "1_Chronicles": 12, "2_Chronicles": 13, "Ezra": 14, "Nehemiah": 15,
            "Esther": 16, "Job": 17, "Psalms": 18, "Proverbs": 19, "Ecclesiastes": 20, "Song_of_songs": 21, "Isaiah": 22, "Jeremiah": 23, "Lamentations": 24,
            "Ezekiel": 25, "Daniel": 26, "Hosea": 27, "Joel": 28, "Amos": 29, "Obadiah": 30, "Jonah": 31, "Micah": 32, "Nahum": 33, "Habakkuk": 34,
            "Zephaniah": 35, "Haggai": 36, "Zechariah": 37, "Malachi": 38
        }
        location = path + "/static/version/" + ver + "_old.json"
    else :
        book_code = {
            "Matthew": 0, "Mark": 1, "Luke": 2, "John": 3, "Acts": 4, "Romans": 5, "1_Corinthians": 6, "2_Corinthians": 7,
            "Galatians": 8, "Ephesians": 9, "Philippians": 10, "Colossians": 11, "1_Thessalonians": 12, "2_Thessalonians": 13,
            "1_Timothy": 14, "2_Timothy": 15, "Titus": 16, "Philemon": 17, "Hebrews": 18, "James": 19, "1_Peter": 20,
            "2_Peter": 21, "1_John": 22, "2_John": 23, "3_John":24, "Jude": 25, "Revelation": 26
        }
        location = path + "/static/version/" + ver + "_new.json"

    with codecs.open(location, 'r', 'utf-8-sig') as json_data:
        d = json.load(json_data)
        json_chp = int(chp) - 1
        try:
            verse_str = d[book_code[book]]['chapters'][json_chp][chp]
            return verse_str
        except KeyError:
            return 'DB 오류로 번역지원되지 않음.'

def heb_vrs_to_eng(book, chp, verse):
    vrs_str = chp + ":" + verse
    path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    location = path + "/static/json/heb_eng_vrs.json"
    with open(location) as json_data:
        d = json.load(json_data)
        if book in d.keys():
            if vrs_str in d[book].keys():
                if isinstance(d[book][vrs_str], list):
                    eng_chp_vrs = d[book][vrs_str]
                    return eng_chp_vrs
                else:
                    eng_chp_vrs = [d[book][vrs_str]]
                    return eng_chp_vrs
            else:
                eng_chp_vrs = [chp+":"+verse]
                return eng_chp_vrs
        else:
            eng_chp_vrs = [chp + ":" + verse]
            return eng_chp_vrs
