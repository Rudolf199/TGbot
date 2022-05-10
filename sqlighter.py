import psycopg2


class DataBase:

    def __init__(self, database, host, password, port, user):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        self.cursor = self.connection.cursor()
    # subscribers

    def get_subscriptions(self, status=True):
        """Получаем всех активных подписчиков бота"""
        with self.connection:
            self.cursor.execute(f"SELECT * FROM subscribers WHERE status = {status}")
            return self.cursor.fetchall()

    def subscriber_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            self.cursor.execute(f"SELECT * FROM subscribers WHERE user_id = {user_id}")
            result = self.cursor.fetchall()
            return bool(len(result))

    def add_subscriber(self, user_id, status=True):
        """Добавляем нового подписчика"""
        with self.connection:
            return self.cursor.execute("INSERT INTO subscribers(user_id, status) VALUES(%s, %s)", (user_id, status))

    def update_subscription(self, user_id, status):
        """Обновляем статус подписки пользователя"""
        with self.connection:
            return self.cursor.execute(f"UPDATE subscribers SET status = {status} WHERE user_id = {user_id}")

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()