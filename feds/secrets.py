def secret_db_name():
    return 'feds'


def secret_db_user():
    return 'feds'


def secret_db_password():
    return 'hunter2'


def secret_db_port():
    return 3306


def secret_db_host():
    return 'db'


def secret_key():
    return '_(g#-==3_y-0fp(!dc_6=ukct@xeuz%$k^1pdp8wc8ql3#4pjq'


def secret_allowed_hosts():
    # ['*']
    return ['127.0.0.1', 'localhost']


def secret_static_root():
    return '/opt/project/feds/feds/static'


def secret_superuser_deets():
    superuser = {
            'username': 'greer',
            'first_name': 'Greer',
            'last_name': 'Ryan',
            'password': 'PercyAte86BurgersLastMonth',
            'email': 'greer@example.com',
        }
    return superuser


def secret_users():
    users = {
        'dan': {
            'first_name': 'Dan',
            'last_name': 'Ryan',
            'password': 'GetMeHigh',
            'email': 'dan@example.com',
            'is_staff': False,
            'is_active': False,
        },
        'maddy': {
            'first_name': 'Maddy',
            'last_name': 'Ryan',
            'password': 'HundoP',
            'email': 'maddy@example.com',
            'is_staff': False,
            'is_active': False,
        },
    }
    return users


def secret_pages():
    page_specs = [
        {
            'title': 'Welcome',
            'slug': 'home',
            'content': 'Welcome to FEDS',
        },
        {
            'title': 'About us',
            'slug': 'about-us',
            'content': 'We think we exist.',
        },
        {
            'title': 'Frequently asked questions',
            'slug': 'faqs',
            'content': 'Nobody asks about *this* project.',
        },
    ]
    return page_specs


def secret_recapture_keys():
    keys = {
        'public': '6LcQji4UAAAAAHA-LKie_7yMAAzqB4lvguuyW1za',
        'private': '6LcQji4UAAAAAG6ia0CkTMc-Wf3e9NO_csI8vv8S',
    }
    return keys
