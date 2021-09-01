# vk id and token group or user
token = {
    # example
    30688695: '7463a7fc41c88cebfb00511fgjfgjfgjfja15d08ecbebbdf6929ba2cc593d8f8ca644d9ec',
}


token_telegram = {
    # example
    99991056475566: '1056475566:AAG4gfjfgCf-R45ythdhddfhENfdhNcdY',
    # 9999{your id}
}


# admin id
admin = [123456]

# admin info for work in comment
cover = True
work_in_comment = True

user_app_id = 2685278
user_login = '7999123456'
user_pass = 'qwerty'

# need for work in comments
user_group_id = '168691465'
user_album_id = '270643164'

group_for_post = []
bd_path = 'db/vkbot.db'

bd_tabs = {
            "mail": '"id" INTEGER, "id_group" INTEGER',
            "chat": '"id" VARCHAR(30), "id_block" VARCHAR(30)',
            "bilion": '"id" INTEGER,"step" INTEGER, "point" INTEGER, "lvl"	INTEGER',
            "cache_gif": '"gif_id"	TEXT UNIQUE, "source" TEXT UNIQUE',
            "facts": '"id" INTEGER, "fact" TEXT UNIQUE, "from_id" INTEGER',
            "message": 'id INTEGER, time INTEGER, msg VARCHAR(550)',
            "qest": 'id INTEGER, point INTEGER',
            "reviews": '"id" INTEGER, "group" INTEGER, "time" INTEGER, "txt" TEXT',
            "time_send": ('"type_key" TEXT, "group_id" INTEGER, "user_id" INTEGER, "time" '
                          'INTEGER, "send_command"	TEXT, "send_keyboard"	TEXT, "global_time" INTEGER'),
            "userdata": ('"id" INTEGER, "fname" VARCHAR(30), "lname" VARCHAR(30),'
                         ' "gender" CHAR(1), "joining" DATE, "bday" DATE, "group_id" INTEGER, PRIMARY KEY("id")'),

            "yam": ('"pattern" VARCHAR(550), "id" VARCHAR(30) UNIQUE,'
                    ' "title" VARCHAR(550), "url" VARCHAR(150), "time" INTEGER'),

            "yam_user": '"user_id" INTEGER, "time" INTEGER, "msg" VARCHAR(550)',

            "cover": ('"group_id" INTEGER, "post_id" INTEGER, "user_id" INTEGER,'
                      ' "time_action" INTEGER, "type_action" INTEGER, "count" INTEGER'),
            "condition": '"id" INTEGER UNIQUE, "json" TEXT'
        }

# key
# example enter your keys Yandex api
ya_translate = 'trnsl.1.1.20191026T085210Z.d618fdfhdhcba4c.64c40d3e7e87d85fgjfe0b057e2ffd122'
ya_dict = 'dict.1.1.20200127T093811Z.5bbdfjfb91a.4d8dc144ea9755ddghd338dc736844811a3'
ya_speech = '22fedfhdha2f-4a58-a934-54fsdgsdg8'
ya_moderation = 'AgAAAAADRT4KAATsdgdsfgh8sXD7mZxzJEc'

# https://deepai.org/
deepai = '434f4bb2-a1e6-4474-92b9-76c5c9061743'

# https://www.deviantart.com
deviantart_id = 123456
deviantart_secret = 'd8d82bddhfgdg0ebfaf40'

# proxy
proxy = [
     # 'login:password@ip:port'
]

# subscribes
subscribe = True

# captcha_key https://rucaptcha.com/
captcha = '9a826fa8bf248a5d3'

import ssl

#ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
#ssl_context.load_cert_chain('domain_srv.crt', 'domain_srv.key')

ssl_context = None

port = 7070
key_api = ''

