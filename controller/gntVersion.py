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
from flask import request

SBLGNT = 'sblgnt'
TG = Fabric( modules=SBLGNT, silent=False )

gnt = TG.load('''
    book chapter verse
    g_word trailer
    otext otype psp
    Case Gender Mood Number
    Person Tense Type Voice
    UnicodeLemma
''')
# 보류: ClType, function

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
    # verse = '''
    #     <div ref='verse'>
    #     <div style="text-align:left">
    #     <b-button size='sm' id='syntax_enact' ref='syntax' variant='outline-secondary' @click='gntsyntax'>구문단위표시</b-button>
    #     </div>
    #     <ol>
    # '''
    verse = '<ol>'

    #한글 번역본 로드(신약)
    korVrs = json_to_verse('kor', book, chapter, 'new')
    i = 0

    for v in verseNode:
        verse += '<li>'
        wordsNode = gnt.L.d(v, otype='word')
        for w in wordsNode:
            # clauseNode = gnt.L.u(w, otype='clause')
            # phraseNode = gnt.L.u(w, otype='phrase')
            # firstClauseWordNode = gnt.L.d(clauseNode[0], otype='word')[0]
            # lastClauseWordNode = gnt.L.d(clauseNode[0], otype='word')[-1]

            # firstPhraseWordNode = gnt.L.d(phraseNode[0], otype='word')[0]
            # lastPhraseWordNode = gnt.L.d(phraseNode[0], otype='word')[-1]

            # if w == firstClauseWordNode:
            #     verse += '<span class=clauseNode id=clauseNode clause_node='+str(clauseNode[0])+'>'
            #     if gnt.F.ClType.v(clauseNode[0]):
            #         cltype = gnt.F.ClType.v(clauseNode[0])
            #     else:
            #         cltype = 'verbal'
            #     verse += "<span class='syntax clause1 hidden' id=syntax>C:"+ cltype +"</span>"

            # if w == firstPhraseWordNode:
            #     verse += '<span class=phraseNode id=phraseNode phrase_node='+str(phraseNode[0])+'>'
            #     verse += "<span class='syntax phrase1 hidden' id=syntax>P:"+ gnt.F.function.v(phraseNode[0]) + "</span>"

            verse += '<span class=gntwordNode><a tabindex=0 class=sblgnt_word_elm data-poload=/sblgnt/word/'+str(w)+' data-toggle=popover data-trigger=focus>'
            verse += gnt.F.g_word.v(w)
            verse += '</a></span>'

            if gnt.F.trailer.v(w):
                verse += '<span class=trailerNode>'
                verse += gnt.F.trailer.v(w)
                verse += '</span>'
            
            # if w == lastClauseWordNode: verse += '</span>'
            # if w == lastPhraseWordNode: verse += '</span>'

        #한글 구절 추가
        i = int(i) + 1
        if korVrs[str(i)] == '[없음]':
            i = int(i) + 1
        #print(str(i) + ' ' + korVrs[str(i)])
        verse += '<p>' + str(chapter) + ':' + str(i) + ' ' + korVrs[str(i)] + '</p>'

        ## span end태그 오류가 생길 경우(신택스 뷰어 설정시) 아래와 같이 조정하면 고쳐짐. 
        # verse += '</span></span></span></span></li>'
        verse += '</li>'

    verse += '</ol></div>'
    return verse

# 단어 정보 불러오기
def word_function(node):
    w_f = []
    w_f.append("원형: " + gnt.F.UnicodeLemma.v(node))
    w_f.append("품사: " + gnt.F.psp.v(node))
    if gnt.F.Tense.v(node):
        w_f.append("시제: " + gnt.F.Tense.v(node))
    if gnt.F.Mood.v(node):
        w_f.append("화법: " + gnt.F.Mood.v(node))
    if gnt.F.Voice.v(node):
        w_f.append("태: " + gnt.F.Voice.v(node))
    if gnt.F.Person.v(node):
        w_f.append("인칭: " + gnt.F.Person.v(node))
    if gnt.F.Gender.v(node):
        w_f.append("성: " + gnt.F.Gender.v(node))
    if gnt.F.Number.v(node):
        w_f.append("수: " + gnt.F.Number.v(node))
    if gnt.F.Case.v(node):
        w_f.append("격: " + gnt.F.Case.v(node))
    if gnt.F.Type.v(node):
        w_f.append("유형: " + gnt.F.Type.v(node))
    #w_f.append("사전: <a href=https://dict.naver.com/grckodict/#/search?query=" + gnt.F.UnicodeLemma.v(node)  + " target=_blank>보기</a>")

    return w_f


