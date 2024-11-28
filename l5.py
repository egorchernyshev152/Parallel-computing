import time
import threading
import pickle
import os

# Глобальные данные
data_file = "car_rental_data.pkl"
cars = []
rented_cars = []
customer_balance = 0  # Баланс задаётся пользователем при аренде


# Функция загрузки данных
def load_data():
    global cars, rented_cars
    if os.path.exists(data_file):
        with open(data_file, "rb") as file:
            data = pickle.load(file)
            cars = data.get("cars", [])
            rented_cars = data.get("rented_cars", [])
    else:
        print("Файл данных отсутствует. Начало с чистого листа.")


# Функция сохранения данных
def save_data():
    with open(data_file, "wb") as file:
        data = {"cars": cars, "rented_cars": rented_cars}
        pickle.dump(data, file)


# Функция обратного отсчёта для аренды
def countdown_timer(car, duration=86400):
    time.sleep(duration)
    rented_cars.remove(car)
    cars.append(car)
    print(f"\nВремя аренды автомобиля {car['brand']} {car['model']} истекло. Автомобиль возвращён в список доступных.\n")


# Меню администратора
def admin_menu():
    password = input("Введите пароль администратора: ")
    if password != "123":
        print("Неверный пароль!")
        return

    while True:
        print("\n-— Администратор —-")
        print("1. Добавить машину")
        print("2. Удалить машину")
        print("3. Редактировать машину")
        print("4. Посмотреть список машин")
        print("5. Выйти")
        choice = input("Выберите действие: ")

        if choice == "1":
            brand = input("Введите марку машины: ")
            model = input("Введите модель машины: ")

            while True:
                try:
                    year = int(input("Введите год выпуска (число): "))
                    break
                except ValueError:
                    print("Ошибка: Год должен быть числом!")

            while True:
                try:
                    price = int(input("Введите цену аренды (в день, число): "))
                    break
                except ValueError:
                    print("Ошибка: Цена должна быть числом!")

            cars.append({"brand": brand, "model": model, "year": year, "price": price})
            print("Машина добавлена!")
            save_data()

        elif choice == "2":
            view_cars()
            idx = int(input("Введите номер машины для удаления: ")) - 1
            if 0 <= idx < len(cars):
                removed_car = cars.pop(idx)
                print(f"Машина {removed_car['brand']} {removed_car['model']} удалена")
                save_data()
            else:
                print("Неверный номер!")

        elif choice == "3":
            view_cars()
            idx = int(input("Введите номер машины для редактирования: ")) - 1
            if 0 <= idx < len(cars):
                car = cars[idx]
                print("Оставьте поле пустым, если не хотите изменять параметр.")
                brand = input(f"Марка ({car['brand']}): ") or car['brand']
                model = input(f"Модель ({car['model']}): ") or car['model']

                while True:
                    year = input(f"Год ({car['year']}): ")
                    if not year:
                        year = car['year']
                        break
                    try:
                        year = int(year)
                        break
                    except ValueError:
                        print("Ошибка: Год должен быть числом!")

                while True:
                    price = input(f"Цена ({car['price']}): ")
                    if not price:
                        price = car['price']
                        break
                    try:
                        price = int(price)
                        break
                    except ValueError:
                        print("Ошибка: Цена должна быть числом!")

                cars[idx] = {"brand": brand, "model": model, "year": year, "price": price}
                print("Машина обновлена!")
                save_data()
            else:
                print("Неверный номер!")

        elif choice == "4":
            view_cars()

        elif choice == "5":
            break

        else:
            print("Неверный выбор!")


# Р¤СѓРЅРєС†РёСЏ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ СЃРїРёСЃРєР° РјР°С€РёРЅ
def view_cars():
    if not cars:
        print("Список машин пуст.")
        return
    print("\n-— Список машин —-")
    for i, car in enumerate(cars, start=1):
        print(f"{i}. {car['brand']} {car['model']}, {car['year']} - {car['price']} руб./день")


# Меню клиента
def customer_menu():
    global customer_balance

    while True:
        print("\n-— Клиент —-")
        print("1. Просмотреть доступные машины")
        print("2. Ваши машины")
        print("3. Оформить аренду")
        print("4. Выйти")
        choice = input("Выберите действие: ")

        if choice == "1":
            view_cars()

        elif choice == "2":
            if not rented_cars:
                print("У вас нет арендованных машин.")
            else:
                print("\n-— Ваши машины —-")
                for car in rented_cars:
                    print(f"{car['brand']} {car['model']}")

        elif choice == "3":
            if customer_balance == 0:
                while True:
                    try:
                        customer_balance = int(input("Введите ваш начальный баланс: "))
                        break
                    except ValueError:
                        print("Ошибка: Баланс должен быть числом!")

            budget = int(input("Введите ваш бюджет: "))
            affordable_cars = [car for car in cars if car['price'] <= budget]
            if not affordable_cars:
                print("Нет машин, подходящих под ваш бюджет.")
            else:
                print("\n-— Доступные машины —-")
                for i, car in enumerate(affordable_cars, start=1):
                    print(f"{i}. {car['brand']} {car['model']}, {car['year']} - {car['price']} руб./день")

                idx = int(input("Выберите номер машины для аренды: ")) - 1
                if 0 <= idx < len(affordable_cars):
                    selected_car = affordable_cars[idx]
                    if customer_balance >= selected_car['price']:
                        customer_balance -= selected_car['price']
                        rented_cars.append(selected_car)
                        cars.remove(selected_car)
                        print(f"Вы арендовали {selected_car['brand']} {selected_car['model']}!")
                        print(f"Оставшийся баланс: {customer_balance} руб.")
                        save_data()
                        threading.Thread(target=countdown_timer, args=(selected_car,)).start()
                    else:
                        print("Недостаточно средств!")
                else:
                    print("Неверный номер!")

        elif choice == "4":
            break

        else:
            print("Неверный выбор!")


# Главное меню
def main_menu():
    load_data()
    while True:
        print("\n-— Система проката автомобилей —-")
        print("1. Администратор")
        print("2. Клиент")
        print("3. Выйти")
        choice = input("Выберите роль: ")

        if choice == "1":
            admin_menu()
        elif choice == "2":
            customer_menu()
        elif choice == "3":
            print("До свидания!")
            break
        else:
            print("Неверный выбор!")
    save_data()


# Запуск программы
if __name__ == "__main__":
    main_menu()