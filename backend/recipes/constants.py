from django.conf import settings

MAX_LEN_TAG = 32
MAX_LEN_TEXT = 256
LOOK_TEXT = 50
MAX_LEN_NAME_INGREDIENT = 128
MAX_LEN_MEASUREMENT_UNIT = 64
MIN_VALUE = 1
MESSAGE = f'Убедитесь, что это значение больше либо равно {MIN_VALUE}.'
HTTP_DOMEN = f'http://{settings.ALLOWED_HOSTS[0]}/'
NAME_FILE = 'output.txt'
