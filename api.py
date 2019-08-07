'''
api.py
api의 블루프린트를 정의
api response정의
'''

from flask import Blueprint, jsonify, request
from bibleapi.controller import translateVersion as tv
from bibleapi.controller import gntVersion as gv


api = Blueprint('api', __name__)

# 한글, 영어 번역본 텍스트 불러오기
@api.route('/text/<string:ver>/<string:bib>/<string:book>/<string:chp>/')
def translateVersion(ver, book, chp, bib):
    result = tv.json_to_verse(ver, book, chp, bib)
    verse = {'verse': result}
    return jsonify(verse)  

# gnt 텍스트 불러오기
@api.route('/text/gnt/<string:book>/<int:chp>/')
def gntVersion(book, chp):
    result = gv.getGnt(book, chp)
    verse = {'verse': result}
    return jsonify(verse)

# gnt 단어 분석
@api.route('/word/gnt/<int:node>/')
def gntwordinfo(node):
    result = gv.word_function(node)
    gntwordinfo = {'gntwordinfo': result}
    return jsonify(gntwordinfo)