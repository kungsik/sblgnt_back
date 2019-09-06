# from tf.fabric import Fabric
import json
import locale
import unicodedata
# from flask import request

from sblgnt_back.controller import translate as tr
from sblgnt_back.lib import vcodeparser as vp
from sblgnt_back.controller.gntVersion import gnt, get_kor_hgloss

def gntReadingTool(rangeCode, check1, check2):

    sections = rangeCode.split(";")

    result = '<div class="reading">'
    result += '<h3>알파알렙 성경 원문읽기 도우미 (신약)</h3><br>'

    if not check1:
        parsing = '<h4>단어 문법 분석</h4>'
        parsing += '<font size=3>불변화사나 전치사 등과 같이 빈번하게 등장하는 단어들은 단어 리스트 참조</font>'
        parsing += '<br><br><div class="parsing">'

    vocalist = {}

    for section in sections:
        nodeList = vp.codetorange(section, gnt)
        sectionTitle = vp.codetostr(section, vp.bookListKor)
    
        if nodeList == False:
            error = "오류가 발생했습니다." 
            return error
        
        if len(nodeList) > 100:
            error = "범위가 너무 많습니다. 100절 이하의 범위를 입력해 주세요."
            return error
        
        result += '<h4>' + sectionTitle + '</h4>'
        result += '<br>'
        result += '<div class="section_gnt">'
        
        for node in nodeList:
            section = gnt.T.sectionFromNode(node)
            wordsNode = gnt.L.d(node, otype='word')
            result += '<span class=chpvrs>' + str(section[2]) + '</span> <span class="verse">' + gnt.T.text(wordsNode) + '</span>'

            if not check1:
                parsing += vp.booknameconv(section[0], vp.bookList, vp.bookListKorAbbr) + str(section[1]) + ":" + str(section[2]) + "<br>"

            for w in wordsNode:
                strong = gnt.F.strong.v(w)
                gloss = get_kor_hgloss(strong, w)

                if not check2:
                    root = gnt.F.UnicodeLemma.v(w)

                    if not root in vocalist:
                        vocalist[root] = gloss

                if not check1:                  
                    pdp = tr.eng_to_kor(gnt.F.psp.v(w), 'full')
                    if pdp == '전치사' or pdp == '관사' or pdp == '정관사' or pdp == '접속사' or pdp == '관계사' or pdp == '부사':
                        continue

                    parsing += '<span class="parsing_gnt">'
                    parsing += "[" + gnt.F.g_word.v(w) + "] "
                    parsing += "</span>"

                    parsing += pdp + " "

                    if pdp == '동사':
                        if gnt.F.Person.v(w):
                            Person = tr.eng_to_kor(gnt.F.Person.v(w), 'full')
                        else: 
                            Person = ''

                        if tr.eng_to_kor(gnt.F.Number.v(w), 'full'):
                            Number = tr.eng_to_kor(gnt.F.Number.v(w), 'full')
                        else:
                            Number = ''

                        if tr.eng_to_kor(gnt.F.Mood.v(w), 'full'):
                            Mood = tr.eng_to_kor(gnt.F.Mood.v(w), 'full')
                        else: 
                            Mood = ''

                        if tr.eng_to_kor(gnt.F.Voice.v(w), 'full'):
                            Voice = tr.eng_to_kor(gnt.F.Voice.v(w), 'full')
                        else:
                            Voice = ''

                        parsing += "(" + gnt.F.UnicodeLemma.v(w) + ") "
                        parsing += tr.eng_to_kor(gnt.F.Tense.v(w), 'full') + "." + Person + "." + Number + " " + Mood + " " + Voice + " "
                                
                    if pdp == '명사' or pdp == '형용사' or pdp == '인칭대명사':
                        if tr.eng_to_kor(gnt.F.Gender.v(w), 'full'):
                            Gender = tr.eng_to_kor(gnt.F.Gender.v(w), 'full')
                        else:
                            Gender = ''

                        if tr.eng_to_kor(gnt.F.Number.v(w), 'full'):
                            Number = tr.eng_to_kor(gnt.F.Number.v(w), 'full')
                        else:
                            Number = ''
                            
                        if  tr.eng_to_kor(gnt.F.Case.v(w), 'full'):
                            Case = tr.eng_to_kor(gnt.F.Case.v(w), 'full')
                        else:
                            Case = ''

                        parsing += "(" + gnt.F.UnicodeLemma.v(w) + ") "
                        parsing += Gender + "." + Number + "." + Case + " "

                    parsing += "(" + gloss + ")<br>"
            
            if not check1:
                parsing += "<br>" 
        
        result += '</div><br><br>'
    
    if not check1:
        parsing += '</div><br><br>'
        result += parsing

    if not check2:
        result += '<h4>단어 리스트</h4>'
        result += '<br>'
        result += '<div class="wordlist">'

        greek_list = []
        for k,v in vocalist.items():
            greek_list.append(k)

        locale.setlocale(locale.LC_ALL, "el_GR.UTF-8")
        sorted_greeklist = sorted(greek_list, key=locale.strxfrm)
        # sorted_greeklist = sorted(greek_list)

        # print(sorted_greeklist)

        for voca in sorted_greeklist:
            result += '<span class="parsing_gnt">' + voca + '</span> <span class="parsing">' + vocalist[voca] + '</span><br>'
        
        result += '</div>'
    
    result += '</div>'

    result += '<div class="notice">일러두기<br>'
    result += '저작권: 저작자표시-비영리 2.0 대한민국 (CC BY-NC 2.0 KR)<br>'
    result += '본 내용은 알파알렙성경(app.alphalef.com)을 통해서 출력되었습니다. 이 문서를 변형하거나 누구에게나 자유롭게 배포할 수 있습니다. 다만, 상업적인 이용은 불가하며 공유시 본 일러두기 부분을 반드시 첨부하여 주시면 감사하겠습니다.'
    result += '</div>'

    return result