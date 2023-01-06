import os
from django.core.mail import send_mail

os.environ['DJANGO_SETTINGS_MODULE'] = 'Forum.settings'

if __name__ == '__main__':

    send_mail(
        '来自xd的测试邮件',
        '热爱学习Python、Django技术！',
        'xd1455817493@sina.com',
        ['1455817493@qq.com'],
    )
