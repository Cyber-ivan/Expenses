from my_secrets import secrets

BOT_TOKEN = secrets.get('BOT_API_TOKEN')

DB_SETTINGS = {
    "host": "localhost",
    "dbname": secrets.get('db_name'),
    "user": secrets.get('db_user'),
    "password": secrets.get('db_password'),
}
