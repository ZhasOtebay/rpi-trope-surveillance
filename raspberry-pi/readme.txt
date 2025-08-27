 Пошаговое руководство: Установка библиотек из requirements.txt

 Шаг 1: Создание виртуального окружения

 
 Переходим в папку проекта
cd ~/my_project

 Создаем виртуальное окружение
python3 -m venv venv
 

 Шаг 2: Активация виртуального окружения

 
source venv/bin/activate
 

 Признак успешной активации: в командной строке появится `(venv)`
 
(venv) user@server:~/my_project$
 

 Шаг 3: Проверка активации

 
 Проверяем путь к Python
which python
 Должно вернуть: /home/user/my_project/venv/bin/python

 Проверяем путь к pip
which pip
 Должно вернуть: /home/user/my_project/venv/bin/pip
 

 Шаг 4: Установка библиотек из requirements.txt

 
 Базовая установка
pip install -r requirements.txt

 С подробным выводом (verbose)
pip install -r requirements.txt -v

 Игнорируя кеш (если есть проблемы с кешированием)
pip install --no-cache-dir -r requirements.txt

 Только для текущего пользователя (без прав sudo)
pip install --user -r requirements.txt
 

 Шаг 5: Проверка установленных пакетов

 
 Список установленных пакетов
pip list

 Показать информацию о конкретном пакете
pip show имя_пакета

 Проверить зависимости
pip check
 

 Шаг 6: Деактивация окружения (когда закончили работу)

 
deactivate
 

 Дополнительные полезные команды

 
 Обновить pip перед установкой
pip install --upgrade pip

 Установить в режиме разработки (если есть setup.py)
pip install -e .

 Сгенерировать requirements.txt из установленных пакетов
pip freeze > requirements.txt

 Установить конкретную версию пакета (если нужно переопределить)
pip install "package-name==1.2.3"
 

 Пример файла requirements.txt
 
Django==4.2.7
requests>=2.25.0
numpy<1.24.0
pandas
 

Важно: Все команды выполняются только после активации виртуального окружения!
