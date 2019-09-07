'''
gntVersion.py
Text-Fabric api를 이용한 그리스어 텍스트 가공
로컬 환경에서 데이터 위치
C:/Users/kungs/text-fabric-data/sblgnt
C:/Users/kungs/github/text-fabric-data/sblgnt
C:/Users/kungs/Dropbox/text-fabric-data/sblgnt
참조: https://github.com/biblicalhumanities/greek-new-testament/tree/master/syntax-trees/sblgnt
현재 syntax viewer에 문제가 있음. 추후 수정
'''

from tf.fabric import Fabric
import os
import json
import codecs
import csv
# from flask import request

from sblgnt_back.controller import translate as tr
from sblgnt_back.lib import vcodeparser as vp

SBLGNT = 'sblgnt'
TG = Fabric( modules=SBLGNT, silent=False )

gnt = TG.load('''
    book chapter verse
    g_word trailer
    otext otype psp
    Case Gender Mood Number
    Person Tense Voice
    UnicodeLemma gloss strong
    transliteration ClType function
''')

# 번역본 텍스트 불러오기
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
            verse_str = d[book_code[book]]['chapters'][json_chp][str(chp)]
            return verse_str
        except KeyError:
            return 'DB 오류로 번역지원되지 않음.'


# 그리스어 텍스트 불러오기
def getGnt(book='Matthew', chapter=1):
    chpNode = gnt.T.nodeFromSection((book, chapter))
    verseNode = gnt.L.d(chpNode, otype='verse')
    verse = '<ol>'

    #한글 번역본 로드(신약)
    korVrs = json_to_verse('kor', book, chapter, 'new')
    n = 1

    for v in verseNode: 
        sectionFromVerse = gnt.T.sectionFromNode(v)
        vcode = vp.nodetocode(sectionFromVerse, vp.bookList)
        while sectionFromVerse[2] != n:
            verse += '<li style="font-size:20px; padding-bottom:15px;">[없음]</li>'
            n = n + 1

        verse += '<li style="font-size:20px;">'
        wordsNode = gnt.L.d(v, otype='word')
        for w in wordsNode:
            clauseNode = gnt.L.u(w, otype='clause')
            clauseAtomNode = gnt.L.u(w, otype='clause_atom')

            firstClauseWordNode = gnt.L.d(clauseNode[0], otype='word')[0]
            lastClauseWordNode = gnt.L.d(clauseNode[0], otype='word')[-1]

            try:
                if gnt.L.d(clauseAtomNode[0], otype='word')[0]:
                    firstClauseAtomWordNode = gnt.L.d(clauseAtomNode[0], otype='word')[0]
            except IndexError:
                firstClauseAtomWordNode = 0
                pass

            try:
                if gnt.L.d(clauseAtomNode[0], otype='word')[-1]:
                    lastClauseAtomWordNode = gnt.L.d(clauseAtomNode[0], otype='word')[-1]
            except IndexError:
                lastClauseAtomWordNode = 0
                pass

            if w == firstClauseWordNode:
                verse += '<span class=clauseNode clause_node='+str(clauseNode[0])+'>'
                if gnt.F.ClType.v(clauseNode[0]):
                    cltype = gnt.F.ClType.v(clauseNode[0])
                else:
                    cltype = 'Verbal'
                verse += "<span class='clause1'>C:"+ tr.eng_to_kor(cltype, "full") +"</span>"

            if w == firstClauseAtomWordNode:
                verse += '<span class=phraseNode phrase_node='+str(clauseAtomNode[0])+'>'
                verse += "<span class='clauseatom'>P:"+ tr.eng_to_kor(gnt.F.function.v(clauseAtomNode[0]), "full") + "</span>"

            verse += '<span class=gntwordNode><a tabindex=0 class=sblgnt_word_elm data-poload=/sblgnt/word/'+str(w)+' data-toggle=popover data-trigger=focus>'
            verse += gnt.F.g_word.v(w)
            verse += '</a></span>'

            if gnt.F.trailer.v(w):
                verse += '<span class=trailerNode>'
                verse += gnt.F.trailer.v(w)
                verse += '</span>'

            if w == lastClauseWordNode: verse += '</span>'
            if w == lastClauseAtomWordNode: verse += '</span>'

        ## span end태그 오류가 생길 경우(신텍스 뷰어 설정시) 아래와 같이 조정하면 고쳐짐.
        verse += '</span></span></span></span>'
        verse += '<button type="button" class="btn btn-default btn-xs sblgnt_verse_analysis" verse_node='+str(v)+'>절분석</button> '    

        #절노트 버튼
        versenote_url = "'../../commentary/vcode/" + vcode + "'" 
        verse += '<button type="button" class="btn btn-default btn-xs verse_note" onclick="location.href=' + versenote_url + '">주석</button>'

        verse +='</li>'
        #한글 구절 추가
        verse += '<p class=sblgnt_korean>' + str(chapter) + ':' + str(n) + ' ' + korVrs[str(n)] + '</p>'
        verse += '</li>'

        n = n + 1

    verse += '</ol></div>'
    return verse

# 단어 정보 불러오기
def word_function(node):
    w_f = []
    w_f.append("원형:  <span class=sblgnt_word_api>" + gnt.F.UnicodeLemma.v(node) + "</span>" )
    w_f.append("음역: " + gnt.F.transliteration.v(node))
    w_f.append("품사: " + tr.eng_to_kor(gnt.F.psp.v(node), "full"))
    if gnt.F.Tense.v(node):
        w_f.append("시제: " + tr.eng_to_kor(gnt.F.Tense.v(node), "full"))
    if gnt.F.Mood.v(node):
        w_f.append("화법: " + tr.eng_to_kor(gnt.F.Mood.v(node), "full"))
    if gnt.F.Voice.v(node):
        w_f.append("태: " + tr.eng_to_kor(gnt.F.Voice.v(node), "full"))
    if gnt.F.Person.v(node):
        w_f.append("인칭: " + tr.eng_to_kor(gnt.F.Person.v(node), "full"))
    if gnt.F.Gender.v(node):
        w_f.append("성: " + tr.eng_to_kor(gnt.F.Gender.v(node), "full"))
    if gnt.F.Number.v(node):
        w_f.append("수: " + tr.eng_to_kor(gnt.F.Number.v(node), "full"))
    if gnt.F.Case.v(node):
        w_f.append("격: " + tr.eng_to_kor(gnt.F.Case.v(node), "full"))
#    if gnt.F.Type.v(node):
#        w_f.append("유형: " + tr.eng_to_kor(gnt.F.Type.v(node), "full"))
    # if gnt.F.gloss.v(node):
        # w_f.append("의미: " + gnt.F.gloss.v(node))
    w_f.append("의미: " + get_kor_hgloss(gnt.F.strong.v(node), node))
    if gnt.F.strong.v(node):
        w_f.append("<a href=https://dict.naver.com/ancientgreek/#/search?query=" + gnt.F.strong.v(node)  + " target=_blank>네이버사전</a>")
        w_f.append("<a href=https://biblehub.com/str/greek/" + gnt.F.strong.v(node)  + ".htm target=_blank>바이블허브</a>")

    return w_f

def get_kor_hgloss(strongnum, w):
    f = open('sblgnt_back/static/csv/gstrong.csv', 'r', encoding='utf-8')
    gstrong = list(csv.reader(f))
    try:
        gloss = gstrong[int(strongnum)]
        f.close()
        result = gloss[1].split(';')
        return result[0]
    except:
        f.close()
        return gnt.F.gloss.v(node)

# 절 정보 불러오기
def verse_function(node):
    wordsNode = gnt.L.d(node, otype='word')
    verse_api = {'words': [], 'gloss': [], 'pdp': [], 'parse': [], 'parse2': []}

    for w in wordsNode:
        verse_api['words'].append(gnt.F.g_word.v(w))
        # verse_api['gloss'].append(gnt.F.gloss.v(w))
        verse_api['gloss'].append(get_kor_hgloss(gnt.F.strong.v(w), w))
        pdp = tr.eng_to_kor(gnt.F.psp.v(w), 'abbr')
        verse_api['pdp'].append(pdp)
        if pdp == '동':

            if gnt.F.Gender.v(w):
                gender = tr.eng_to_kor(gnt.F.Gender.v(w), 'abbr')
            else:
                gender = ''

            if gnt.F.Person.v(w):
                person = tr.eng_to_kor(gnt.F.Person.v(w), 'abbr')
            else:
                person = ''

            if gnt.F.Number.v(w):
                number = tr.eng_to_kor(gnt.F.Number.v(w), 'abbr')
            else:
                number = ''

            if gnt.F.Mood.v(w):
                mood = tr.eng_to_kor(gnt.F.Mood.v(w), 'abbr')
            else:
                mood = ''

            if gnt.F.Voice.v(w):
                voice = tr.eng_to_kor(gnt.F.Voice.v(w), 'abbr')
            else:
                voice = ''

            parse_str = tr.eng_to_kor(gnt.F.Tense.v(w), 'abbr') + "." + person + gender + number
            parse_str2 = mood + '.' + voice

            verse_api['parse'].append(parse_str)
            verse_api['parse2'].append(parse_str2)
        elif pdp == '명' or pdp == '형' or pdp == '관':
            parse_str = tr.eng_to_kor(gnt.F.Gender.v(w), 'abbr') + tr.eng_to_kor(gnt.F.Number.v(w), 'abbr')
            verse_api['parse'].append(parse_str)

            if gnt.F.Case.v(w):
                case = tr.eng_to_kor(gnt.F.Case.v(w), 'abbr')
            else:
                case = ''
            verse_api['parse2'].append(case)
        else:
            verse_api['parse'].append('')
            verse_api['parse2'].append('')

    section = gnt.T.sectionFromNode(wordsNode[0])
    verse_str = {"kjv": [], "kor": []}

    verse_num = section[2]
    while json_to_verse('kor', section[0], section[1], 'new')[str(verse_num)] == '[없음]':
        verse_num = verse_num + 1

    korVrs = str(section[1]) + ":" + str(verse_num) + " " + json_to_verse('kor', section[0], section[1], 'new')[str(verse_num)]
    kjvVrs = str(section[1]) + ":" + str(verse_num) + " " + json_to_verse('kjv', section[0], section[1], 'new')[str(verse_num)]

    verse_str['kor'].append(korVrs)
    verse_str['kjv'].append(kjvVrs)
 
    result = {
        "scripture": section[0] + " " + str(section[1]) + ":" + str(section[2]),
        "parsing": verse_api,
        "translation": verse_str
    }

    return result
