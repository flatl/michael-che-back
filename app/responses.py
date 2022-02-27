import json

'''
  errors:
  0 - successful request (opt.)
  1 - token has expired
  2 - lack of token or wrong token
  3 - lack of requested data or incorrect data
'''

SUCCESS_MESSAGE = json.dumps({
  'success': True,
  'error': 0
})

EMPTY_DATA_MESSAGE = json.dumps({
  'success': False,
  'message': 'Недостаточно данных',
  'error': 3
})

INCORRECT_DATA_MESSAGE = json.dumps({
  'success': False,
  'message': 'Некорректные данные',
  'error': 3
})

NO_TOKEN_MESSAGE = json.dumps({
  'success': False,
  'message': 'Отсутствует токен',
  'error': 2
})

WRONG_TOKEN_MESSAGE = json.dumps({
  'success': False,
  'message': 'Неверный токен',
  'error': 2
})

TOKEN_EXPIRED_MESSAGE = json.dumps({
  'success': False,
  'message': 'Время действия токена истекло',
  'error': 1
})
