# from tf.fabric import Fabric
import json
import csv
# from flask import request

from sblgnt_back.controller import translate as tr
from sblgnt_back.lib import vcodeparser as vp
from sblgnt_back.controller.gntVersion import gnt, get_kor_hgloss

gnt.makeAvailableIn(globals())

def gntReadingTool(rangeCode, check1, check2):

    sections = rangeCode.split(";")

    result = '<div class="reading">'
    result += '<h3>알파알렙 성경 원문읽기 도우미</h3><br>'

    if not check1:
        parsing = '<h4>단어 문법 분석</h4>'
        parsing += '<font size=3>불변화사나 전치사 등과 같이 빈번하게 등장하는 단어들은 단어 리스트 참조</font>'
        parsing += '<br><br><div class="parsing">'

    vocalist = {}

    for section in sections:
        nodeList = vp.codetorange(section)
        sectionTitle = vp.codetostr(section, vp.bookListKor)
    
        if nodeList == False:
            error = "오류가 발생했습니다." 
            return error
        
        if len(nodeList) > 100:
            error = "범위가 너무 많습니다. 100절 이하의 범위를 입력해 주세요."
            return error
        
        result += '<h4>' + sectionTitle + '</h4>'
        result += '<br>'
        result += '<div class="section">'
        
        for node in nodeList:
            section = T.sectionFromNode(node)
            wordsNode = L.d(node, otype='word')
            result += '<span class=chpvrs>' + str(section[2]) + '</span> <span class="verse">' + T.text(wordsNode) + '</span>'

            if not check1:
                parsing += vp.booknameconv(section[0], vp.bookList, vp.bookListKorAbbr) + str(section[1]) + ":" + str(section[2]) + "<br>"

            for w in wordsNode:
                strong = gnt.F.strong.v(node)
                gloss = get_kor_hgloss(strong, w)

                if not check2:
                    root = F.voc_utf8.v(L.u(w, otype='lex')[0])

                    if not root in vocalist:
                        vocalist[root] = gloss

                if not check1:                  
                    pdp = kb.eng_to_kor(F.pdp.v(w), 'full')
                    if pdp == '전치사' or pdp == '관사' or pdp == '접속사' or pdp == '관계사' or pdp == '부사':
                        continue

                    parsing += '<span class="parsing_heb">'
                    parsing += "[" + gnt.F.g_word.v(w) + "] "
                    parsing += "</span>"

                    parsing += pdp + " "

                    # 여기서부터
                    if pdp == '동사':
                        parsing += "(" + gnt.F.UnicodeLemma.v(w) + ") "
                        parsing += tr.eng_to_kor(F.vt.v(w), 'full') + "." + tr.eng_to_kor(F.ps.v(w), 'full') + "." + tr.eng_to_kor(F.gn.v(w), 'full') + "." + tr.eng_to_kor(F.nu.v(w), 'full') + " "
                        if F.prs_ps.v(w) != 'unknown':
                            parsing += "접미."
                            parsing += kb.eng_to_kor(F.prs_ps.v(w), 'full') + "." + kb.eng_to_kor(F.prs_gn.v(w), 'full') + "." + kb.eng_to_kor(F.prs_nu.v(w), 'full') + " "
                    
                    if pdp == '명사':
                        parsing += "(" + F.voc_utf8.v(L.u(w, otype='lex')[0]) + ") "
                        parsing += kb.eng_to_kor(F.gn.v(w), 'full') + "." + kb.eng_to_kor(F.nu.v(w), 'full') + " "
                    
                    if F.g_prs_utf8.v(w) != "":
                        parsing += "접미." + kb.eng_to_kor(F.prs_ps.v(w), 'full') + "." + kb.eng_to_kor(F.prs_gn.v(w), 'full') + "." + kb.eng_to_kor(F.prs_nu.v(w), 'full') + " "

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

        sorted_vocalist = sorted(vocalist.items())
        for voca in sorted_vocalist:
            result += '<span class="parsing_heb">' + voca[0] + '</span> <span class="parsing">' + voca[1] + '</span><br>'
        
        result += '</div>'
    
    result += '</div>'

    result += '<div class="notice">일러두기<br>'
    result += '저작권: 저작자표시-비영리 2.0 대한민국 (CC BY-NC 2.0 KR)<br>'
    result += '본 내용은 알파알렙성경(app.alphalef.com)을 통해서 출력되었습니다. 이 문서를 변형하거나 누구에게나 자유롭게 배포할 수 있습니다. 다만, 상업적인 이용은 불가하며 공유시 본 일러두기 부분을 반드시 첨부하여 주시면 감사하겠습니다.'
    result += '</div>'

    return result