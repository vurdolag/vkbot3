from re import compile

quot = compile(r'&quot;')
space = compile(r' {2,}')
double_comma = compile('"')
n_symbol = compile(r'\\n')


joke_re1 = compile(r'#21201e">.{1,2000}<\' \+ \'/div><\' \+ \'footer style')
joke_re2 = compile(r'(#21201e">|<\' \+ \'/div><\' \+ \'footer style)')
joke_re3 = compile(r'<\' \+ \'br>')
joke_re4 = compile(r'<.{,4}>')
joke_re5 = compile(r'[^А-ЯЁA-Z0-9!]')

img1 = compile(r'(/|-)')
img2 = compile(r'(⏩ ещё арт|арт|картинк|фото|случайный арт|🌄)')

wiki = compile('<.{0,200}?>')

vkloop1 = compile(r'\\xa0')

s_format = compile(r'(\.jpg|\.png|\.bmp|\.gif|\.mp3|\.wav|\.ogg|\.mp4)')

update_re1 = compile(r'(^\!(b|bot|бот|)|\[.{1,}\|.{1,}\](,|))')
update_re3 = compile(r'^\!(b|bot|бот|)')

quest1 = compile(r'[^А-ЯЁа-яё,.!?0-9)(\-*/%: ]')
clear = compile(r'[^A-Za-zА-ЯЁа-яё,.!?0-9)(\-*/%: ]')

chgk1 = compile(r'(\n|\.|\")')
chgk2 = compile(r'(\n|\[.+\])')
chgk3 = compile(r'\(pic:.*\)')
chgk4 = compile(r'\[.*?\]')
chgk5 = compile(r'(\[|\])')

voice1 = compile(r'[^А-ЯЁа-яё,.!?0-9)(\-*/%: ]')
voice2 = compile(r'<.{,4}>')

d = compile(r'[^0-9]')
n_ruw = compile('[^А-ЯЁа-яё ]')

photo_search = compile(r'(http|цена|размер|наличие|цвет|количество|материал)')

log1 = compile(r'/\w+\.py.+line \d+')
log2 = compile(r'[^\w\d._ ]')
