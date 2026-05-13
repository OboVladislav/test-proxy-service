from app.core.celery_app import celery


@celery.task
def send_activation_email(email: str, key: str):
    message = f"""
========================================
  Proxy Service — письмо активации
========================================
Здравствуйте!

Ваш ключ активации для подключения к прокси-серверу:

  {key}

Введите его в десктопном приложении Proxy Client, нажмите «Подключиться».
Ключ одноразовый — после использования он будет аннулирован.

С уважением,
Команда Proxy Service
========================================
"""
    print(f"[EMAIL] To: {email}")
    print(message)
