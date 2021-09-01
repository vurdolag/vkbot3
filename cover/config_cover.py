
POINT_FOR_LIKE = 1  # очки за лайки поста

POINT_FOR_TIME_LIKE_1 = 4  # лайк поста не позже... n1 времени
TIME_LIKE_1 = 60*10

POINT_FOR_TIME_LIKE_2 = 2  # лайк поста не позже... n2 времени
TIME_LIKE_2 = 60*30

POINT_FOR_COMMENT = 5

LIKE_ON_COMMENT = True  # начислять очки за лайки комментариев других юзеров
POINT_FOR_LIKE_ON_COMMENT = 1

LIKE_MY_COMMENT = True  # начислять очки за количество лайков на комментарии юзера
POINT_FOR_LIKE_ON_MY_COMMENT = 0.34

MY_LIKE_ON_MY_COMMENT = True  # фильр самолайков комментариев
IS_MEMBER = True  # проверка является участником группы


COUNT_USER_VIEW = 9
PATH_BACK = 'cover/back/'
PATH_FONT = 'cover/GothaProBol.otf'
PATH_DEFAULT_USER_PHOTO = 'cover/back/-.jpg'
DATE_POST = 60*60*24*7
TIME_ITER = 60
TIME_GLOBAL = 60*60*3

BAN_USER = [
    '38487286',
    '7678173',
    '510175612',
    '526138906',
    '7695700',
    '526138528',
    '526139810',
    '2488557',
    '2770679',
    '449046',
    '566489438',
    '566489538',
    '566490466',
    '566490414',
    '566491806',
    '8006872',
    '510097267',
    '507368207',
    '4772132',
    '495552769',
]

TEMPLATE = {
    '-168691465': {
        'size': 136,
        'pad': 4,
        'pad_img': 8,
        'rad': 45,
        'xy': [(80, 50), (240, 50), (80, 215), (240, 215),
               (1590 - 80 - 150, 50), (1590 - 240 - 150, 50),
               (1590 - 80 - 150, 215), (1590 - 240 - 150, 215)],
        'text_xy': (65, 140),
        'digit_xy': (110, 110),
        'font_size': 20},

    '-30688695': {
        'size': 136,
        'pad': 4,
        'pad_img': 8,
        'rad': 45,
        'xy': [(x + 120, 225) for x in range(0, 1590 - 150*2, 150)],
        'text_xy': (65, 140),
        'digit_xy': (110, 110),
        'font_size': 20},

    '-174587092': {
        'size': 136,
        'pad': 4,
        'pad_img': 8,
        'rad': 45,
        'xy': [(x + 120, 225) for x in range(0, 1590 - 150*2, 150)],
        'text_xy': (65, 140),
        'digit_xy': (110, 110),
        'font_size': 20},

    '-193674464': {
        'size': 136,
        'pad': 4,
        'pad_img': 8,
        'rad': 45,
        'xy': [(x + 120, 225) for x in range(0, 1590 - 150*2, 150)],
        'text_xy': (65, 140),
        'digit_xy': (110, 110),
        'font_size': 20},

}
