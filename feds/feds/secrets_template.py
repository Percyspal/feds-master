def secret_db_name():
    return 'Name of the DB'


def secret_db_user():
    return 'Name of the DB user'


def secret_db_password():
    return 'The DB password'


def secret_key():
    return 'The secret key'


def secret_allowed_hosts():
    # Allowed hosts, like the list below.
    # return ['127.0.0.1', 'localhost']
    return ['*']


def secret_superuser_deets():
    superuser = {
            'username': 'superuser user name',
            'first_name': 'superuser first name',
            'last_name': 'superuser last name',
            'password': 'superuser password',
            'email': 'superuser email',
        }
    return superuser


def secret_users():
    # Repeat for as many users are you want.
    # The key of each element, like username1, is the username, e.g., norwegianblue.
    users = {
        'username1': {
            'first_name': 'User 1 first name',
            'last_name': 'User 1 last name',
            'password': 'User 1 password',
            'email': 'User 1 email',
            'is_staff': False,
            'is_active': False,
        },
        'username2': {
            'first_name': 'User 2 first name',
            'last_name': 'User 2 last name',
            'password': 'User 2 password',
            'email': 'User 2 email',
            'is_staff': False,
            'is_active': False,
        },
    }
    return users


def secret_pages():
    # Add a list element for each page you want.
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
    ]
    return page_specs
