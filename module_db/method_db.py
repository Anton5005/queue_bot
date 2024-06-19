import mysql.connector
import json
# import datetime
from datetime import datetime, timedelta

from config import CONFIG_DB


class MethodDB:
    # Підключення до бази даних
    @property
    def get_connection(self):
        return mysql.connector.connect(**CONFIG_DB)

    @staticmethod
    def method_db(query):
        try:
            # Встановлюємо з'єднання з базою даних
            link = mysql.connector.connect(**CONFIG_DB)
            # Створюємо курсор
            cursor = link.cursor()
            # Виконуємо запит
            cursor.execute(query)
            # Якщо запит є SELECT-запитом, отримуємо всі результати запиту
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                for row in results:
                    print(row)
                return results
            else:
                # Для інших запитів комітимо зміни
                link.commit()
                print("Query executed and changes committed successfully")
            # Отримуємо всі результати запиту
            results = cursor.fetchall()
            # Виводимо результати
            for row in results:
                print(row)
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            # Закриваємо курсор і з'єднання, якщо вони були успішно створені
            if 'cursor' in locals():
                cursor.close()
            if 'link' in locals() and link.is_connected():
                link.close()

    # Додавання нового користувача якщо його немає+++
    def check_and_add_user(self, user_id, username):
        # Перевірка, чи існує користувач з вказаним messenger_id
        query = f"SELECT * FROM users WHERE user_id = {int(user_id)}"
        # Парсимо JSON результат
        result = self.method_db(query)
        # Якщо користувача не знайдено, додаємо нового
        if not result:
            insert_query = f"INSERT INTO users (user_id, username) VALUES ({user_id}, '{username}')"
            self.method_db(insert_query)
            print(json.dumps({"message": "User added successfully"}))
        else:
            print(json.dumps({"message": "User already exists"}))

    # Створення нового слота +++
    def create_slot(self, slot_time, slot_date):
        #("14:50:30", "2024-05-24")
        # створюємо слот
        query = f"INSERT INTO slots (slot_time, slot_date) VALUES ('{slot_time}', '{slot_date}')"
        self.method_db(query)
        # отримуємо слот
        query = f"SELECT slot_id FROM slots WHERE slot_time='{slot_time}' AND slot_date='{slot_date}'"
        return self.method_db(query)[0][0]

    # # Запис користувача на слот +++
    def book_slot(self, user_id, slot_id, service_id):
        query = f"SELECT is_available FROM slots WHERE slot_id = {slot_id}"
        if self.method_db(query) != 1:
            print("слот доступний")
            # Якщо слот доступний, робимо запис
            insert_query = f"INSERT INTO appointments (user_id, slot_id, service_id) VALUES ({user_id}, {slot_id}, {service_id});"
            self.method_db(insert_query)
            # Оновлюємо статус слота як зайнятий
            update_query = f"UPDATE slots SET is_available = FALSE WHERE slot_id = {slot_id}"
            self.method_db(update_query)
            print("Slot booked successfully")
        else:
            print("Slot is not available")

    # Перегляд всіх записів користувача +++
    def get_user_appointments(self, user_id):
        query = f"""
        SELECT s.slot_time, s.slot_date, se.service_name
        FROM appointments a
        JOIN services se ON a.service_id = se.service_id
        JOIN slots s ON a.slot_id = s.slot_id 
        WHERE a.user_id = {user_id}
        ORDER BY s.slot_date ASC, s.slot_time ASC;
        """
        dates = self.method_db(query)
        print(dates)
        date_str = ""
        if not dates:
            return "Ви ще не зайняли чергу"
        for date in dates:
            # Припустимо, що ми маємо значення timedelta та date:
            time_delta = date[0]
            day = date[1]
            # Перетворюємо timedelta у об'єкт datetime для коректного використання strftime
            time_object = datetime(1, 1, 1) + time_delta
            # Форматуємо час у зручний формат HH:MM
            formatted_time = time_object.strftime('%H:%M')
            # Форматуємо дату у зрозумілий формат
            formatted_date = day.strftime("%d.%m")
            date_str += f"Дата: {formatted_date}, Час: {formatted_time}, Послуга: {date[2]}\n"
        return date_str

    # отримати вільні слоти
    def get_free_slots(self, slot_date):
        query = f"SELECT slot_time FROM slots WHERE slot_date = '{slot_date}';"
        time_deltas = self.method_db(query)
        formatted_times = []
        for (time,) in time_deltas:
            # Convert timedelta to datetime object for correct strftime usage
            time_object = datetime(1, 1, 1) + time
            # Format time to HH:MM
            formatted_time = time_object.strftime('%H:%M')
            formatted_times.append(formatted_time)

        print("formatted_times " + str(formatted_times))
        free_time = []
        # Start and end of the working day
        start_time = datetime.strptime('08:00', '%H:%M')
        end_time = datetime.strptime('18:00', '%H:%M')
        # Interval of 60 minutes
        time_interval = timedelta(minutes=60)
        # Generate and store free times
        current_time = start_time
        while current_time <= end_time:
            if current_time.strftime('%H:%M') not in formatted_times:
                free_time.append(current_time.strftime('%H:%M'))
            current_time += time_interval

        print("free_time" + str(free_time))
        return free_time

    # Перегляд всіх записів (для працівників) +++
    def get_all_appointments(self, slot_date):
        query = f"""
                SELECT s.slot_time, u.username, ser.service_name
                FROM appointments a 
                JOIN users u ON a.user_id = u.user_id 
                JOIN slots s ON a.slot_id = s.slot_id
                JOIN services ser ON a.service_id = ser.service_id
                WHERE s.slot_date = '{slot_date}'
                ORDER BY s.slot_time ASC;
                """
        # Перетворення slot_date з рядка в об'єкт datetime
        date_obj = datetime.strptime(slot_date, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d.%m')
        response = f"Ваш розклад на {formatted_date}:\n"
        if data := self.method_db(query):
            for time_delta, name, service in data:
                # Перетворення timedelta в час у форматі 'HH:MM'
                hours, remainder = divmod(time_delta.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                time_str = f"{hours:02}:{minutes:02}"
                response += f"{time_str}, @{name}, {service}\n"
            return response
        else:
            return f"На {formatted_date}, ще ніхто не записався"

    # Перегляд всіх послуг
    def get_services(self):
        query = "SELECT * FROM `services`"
        response = {}
        if data := self.method_db(query):
            for service_id, service_name in data:
                response[service_id] = service_name
        return response

    # отримати назву послуги по її айді
    def get_service_name(self, service_id):
        query = f'SELECT service_name FROM `services` WHERE service_id = {service_id};'
        return self.method_db(query)[0][0]

    # повертає інформацію про створений запис
    def get_the_text_of_the_record(self, time, date_str, service_id):
        # Перетворення рядка дати на об'єкт datetime
        date = datetime.strptime(date_str, '%Y-%m-%d')
        day = date.strftime('%d.%m')  # Використовуємо strftime безпосередньо на об'єкті date
        service_name = self.get_service_name(int(service_id))
        return f"Ви записані)))\nЧас: {time}, число: {day}, стрижка: {service_name}"
