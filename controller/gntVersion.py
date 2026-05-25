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
import xml.etree.ElementTree as ET
from collections import defaultdict
# from flask import request

from sblgnt_back.controller import translate as tr
from sblgnt_back.lib import vcodeparser as vp

SBLGNT = 'sblgnt'
TG = Fabric( modules=SBLGNT, silent=False )

# ── 평행구 데이터 ──────────────────────────────────────────────────────────────
_TF_TO_XML_GRK = {
    'Matthew':'MAT','Mark':'MRK','Luke':'LUK','John':'JHN','Acts':'ACT',
    'Romans':'ROM','1_Corinthians':'1CO','2_Corinthians':'2CO','Galatians':'GAL',
    'Ephesians':'EPH','Philippians':'PHP','Colossians':'COL',
    '1_Thessalonians':'1TH','2_Thessalonians':'2TH','1_Timothy':'1TI','2_Timothy':'2TI',
    'Titus':'TIT','Philemon':'PHM','Hebrews':'HEB','James':'JAS',
    '1_Peter':'1PE','2_Peter':'2PE','1_John':'1JN','2_John':'2JN','3_John':'3JN',
    'Jude':'JUD','Revelation':'REV',
}

_GNT_PARALLEL = defaultdict(list)
_this_dir     = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_this_dir))
_parallel_xml = os.path.join(_project_root, 'kimsbible', 'static', 'json', 'ParallelPassages.xml')
if os.path.exists(_parallel_xml):
    _pt = ET.parse(_parallel_xml)
    for _passage in _pt.getroot().findall('Passage'):
        _verses = _passage.findall('Verse')
        _refs = [(v.text.strip(), 'HEB' if v.get('HEB') else 'GRK') for v in _verses]
        for i, (_ref, _type) in enumerate(_refs):
            _others = [{'ref': r, 'type': t} for j, (r, t) in enumerate(_refs) if j != i]
            _GNT_PARALLEL[_ref].extend(_others)


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

# 그리스어 텍스트 마지막 장 불러오기
def getlastchp(book):
    whole_chpNode = gnt.T.nodeFromSection((book,))
    chapter_nodes = gnt.L.d(whole_chpNode, otype='chapter')
    return gnt.T.sectionFromNode(chapter_nodes[-1])[1]

# 그리스어 텍스트 불러오기
def getGnt(book='Matthew', chapter=1):
    chpNode = gnt.T.nodeFromSection((book, chapter))
    verseNode = gnt.L.d(chpNode, otype='verse')
    verse = '<ol>'

    #개역한글 번역본 로드(신약)
    korVrs = json_to_verse('kor', book, chapter, 'new')

    #kjv 번역본 로드(신약)
    kjvVrs = json_to_verse('kjv', book, chapter, 'new')
    n = 1

    for v in verseNode: 
        sectionFromVerse = gnt.T.sectionFromNode(v)
        vcode = vp.nodetocode(sectionFromVerse, vp.bookList)
        while sectionFromVerse[2] != n:
            verse += '<li style="font-size:18px; padding-bottom:15px;">[없음]</li>'
            n = n + 1

        verse += '<li style="font-size:18px;">'
        verse += '<div class=verseContainer>'
        verse += '<div class=verseNode>'
        wordsNode = gnt.L.d(v, otype='word')
        for w in wordsNode:
            clauseNode = gnt.L.u(w, otype='clause')
            clauseAtomNode = gnt.L.u(w, otype='clause_atom')

            try:
                if gnt.L.d(clauseNode[0], otype='word')[0]:
                    firstClauseWordNode = gnt.L.d(clauseNode[0], otype='word')[0]
            except IndexError:
                pass

            try:
                if gnt.L.d(clauseNode[0], otype='word')[-1]:
                    lastClauseWordNode = gnt.L.d(clauseNode[0], otype='word')[-1]
            except IndexError:
                pass
            
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
        verse += '<br><button type="button" class="btn btn-outline-secondary btn-sm sblgnt_verse_analysis" verse_node='+str(v)+'>절분석</button> '    

        #절노트 버튼
        versenote_url = "../../commentary/vcode/" + vcode + "/"
        verse += '<a href="' + versenote_url + '" target="_blank"><button class="btn btn-outline-secondary btn-sm verse_note">주석</button></a>'

        # 평행구 버튼 (평행구가 존재하는 절에만 표시)
        _xml_abbr = _TF_TO_XML_GRK.get(sectionFromVerse[0])
        if _xml_abbr:
            _xml_ref = _xml_abbr + ' ' + str(sectionFromVerse[1]) + ':' + str(sectionFromVerse[2])
            if _xml_ref in _GNT_PARALLEL:
                verse += ' <button type="button" class="btn btn-outline-success btn-sm parallel_btn" data-ref="' + _xml_ref + '">평행구</button>'

        verse += '</div>' #versenode

        verse += '<div class="transversions">'
        #개역한글 구절 추가
        verse += '<p class=kor>' + str(chapter) + ':' + str(n) + ' ' + korVrs[str(n)] + '</p>'

        #kjv 구절 추가
        verse += '<p class=kjv>' + str(chapter) + ':' + str(n) + ' ' + kjvVrs[str(n)] + '</p>'

        verse += "</div>" #transversions

        verse += '</div>' #versecontainer

        verse += '</li>'

        n = n + 1

    verse += '</ol>'
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
        w_f.append("<a href='#' onclick=\"openDictPopup('https://dict.naver.com/ancientgreek/#/search?query=" + gnt.F.strong.v(node) + "'); return false;\">네이버사전</a>")
        w_f.append("<a href='#' onclick=\"openDictPopup('https://biblehub.com/str/greek/" + gnt.F.strong.v(node) + ".htm'); return false;\">바이블허브</a>")
        w_f.append("<a href='#' onclick=\"openDictPopup('/sblgnt/sdbh/" + gnt.F.strong.v(node) + "/'); return false;\">SDBH</a>")

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
