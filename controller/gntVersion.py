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

            verse += "<span class=gntwordNode @click='gntwordinfo(" + str(w) + ")'>"
            verse += gnt.F.g_word.v(w)
            verse += '</span>'

            if gnt.F.trailer.v(w):
                verse += '<span class=trailerNode>'
                verse += gnt.F.trailer.v(w)
                verse += '</span>'

            # if w == lastClauseWordNode: verse += '</span>'
            # if w == lastPhraseWordNode: verse += '</span>'

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

    return w_f


