from data_base.database import DATABASE

class Querys:
    def user_exist(self, message):
        return "SELECT EXISTS (SELECT 1 FROM users WHERE telegram_id = {0});".format(message.chat.id)

    def users_telegram_id(self):
        return "SELECT telegram_id FROM users;"

    def sum_money_users(self):
        return "SELECT SUM(money) FROM users;"

    def categories_name(self):
        return "SELECT name FROM categories;"

    def categories_all(self):
        return "SELECT id, name FROM categories"

    def difference_income_expense(self):
        return """
                SELECT
                    (COALESCE((SELECT SUM(money) FROM expenses WHERE income = true), 0) -
                    COALESCE((SELECT SUM(money) FROM expenses WHERE income = false), 0)) AS dif
                FROM expenses
                GROUP BY dif;"""

    def all_expenses_on_month(self):
        return """
                SELECT COALESCE(SUM(money),0) AS total_expenses
                FROM expenses
                WHERE income = false AND EXTRACT(MONTH FROM date) = EXTRACT(MONTH FROM CURRENT_DATE);"""

    def all_user_expenses_for_the_month(self, chat_id):
        return """
                SELECT COALESCE(SUM(expenses.money),0) AS total_expenses
                FROM expenses
                LEFT JOIN users ON users.id = expenses.uid
                WHERE income = false
                    AND EXTRACT(MONTH FROM date) = EXTRACT(MONTH FROM CURRENT_DATE)
                    AND category_id = 4
                    AND telegram_id = {0};
                """.format(chat_id)

    def all_income_on_month(self):
        return """
                SELECT SUM(money) 
                FROM expenses 
                WHERE income = true and (SELECT EXTRACT(MONTH FROM date)) = (SELECT EXTRACT(MONTH FROM CURRENT_DATE))"""

    def all_user_income_for_the_month(self, chat_id):
        return """
                SELECT  SUM(expenses.money) 
                FROM expenses 
                JOIN users ON users.id = expenses.uid 
                WHERE income = true 
                    AND (SELECT EXTRACT(MONTH FROM date)) = (SELECT EXTRACT(MONTH FROM CURRENT_DATE)) 
                    AND telegram_id = {0};""".format(chat_id)

    def table_expense_on_month(self, category):
        return """
                SELECT
                   users.name AS name,
                   CASE
                       WHEN expenses.income = FALSE THEN expenses.money * -1
                       ELSE expenses.money
                   END AS money,
                   expenses.comment
                FROM expenses
                JOIN users ON users.id = expenses.uid
                LEFT JOIN categories ON categories.id = expenses.category_id
                WHERE EXTRACT(MONTH FROM expenses.date) = EXTRACT(MONTH FROM CURRENT_DATE) and categories.name = '{0}';
                """.format(category)

    def table_expense_all_time(self,):
        return """
                SELECT 
                    users.name, 
                    CASE 
                        WHEN expenses.income = false THEN expenses.money * -1 
                        ELSE expenses.money 
                    END AS money,
                    expenses.comment 
                FROM 
                    expenses
                LEFT JOIN 
                    users ON users.id = expenses.uid
                LEFT JOIN 
                    categories ON categories.id = expenses.category_id;
                """

    def transaction_income(self,message):
        text = message.text
        words = text.split()
        money = float(words[0])
        comment = ""
        for word in words[1:]:
            comment += word + " "
        return """
                        DO $$
                        DECLARE
                            user_id INT;
                        BEGIN
                            SELECT id INTO user_id
                            FROM users
                            WHERE telegram_id = {0};

                            IF user_id IS NULL THEN
                                RAISE EXCEPTION 'Пользователь с telegram_id {0} не найден';
                            END IF;

                            -- Вычесть деньги из баланса пользователя
                            UPDATE users
                            SET money = money + {1}
                            WHERE id = user_id;

                            -- Добавить запись в таблицу expenses
                            INSERT INTO expenses (uid, money, comment, income, date)
                            VALUES (user_id, {1}, '{2}', TRUE, CURRENT_TIMESTAMP);
                        END $$;
                        """.format(message.chat.id, money, comment)
    def transaction_expenses(self,message,category):
        text = message.text
        words = text.split()
        money = float(words[0])
        comment = ""
        for word in words[1:]:
            comment += word + " "
        return """
            DO $$
            DECLARE
                user_id INT;
                category_id INT;
            BEGIN
                -- Найти ID пользователя по telegram_id
                SELECT id INTO user_id
                FROM users
                WHERE telegram_id = {0};

                IF user_id IS NULL THEN
                    RAISE EXCEPTION 'Пользователь с telegram_id {0} не найден';
                END IF;

                SELECT id INTO category_id
                FROM categories
                WHERE name = '{1}';

                IF category_id IS NULL THEN
                    RAISE EXCEPTION 'Категория с именем {1} не найдена';
                END IF;

                -- Вычесть деньги из баланса пользователя
                UPDATE users
                SET money = money - {2}
                WHERE id = user_id;

                -- Добавить запись в таблицу expenses
                INSERT INTO expenses (uid, category_id, money, comment, income, date)
                VALUES (user_id, category_id, {2}, '{3}', FALSE, CURRENT_TIMESTAMP);
            END $$;
            """.format(message.chat.id, category, money, comment)
