import sys
import shutil
from pathlib import Path
import re

import json
from collections import defaultdict
from openai import OpenAI

class Mail():
    def __init__(self, text):
        self.From = ""
        self.To = ""
        self.Subject = ""
        self.Date = ""
        self.Body = ""
        self.clas = None
        self._parse(text)

    def to_json(self):
        return {"From": self.From, "To": self.To, "Subject": self.Subject, "Date": self.Date, "Body": self.Body}

    def _parse(self, text):
        fro = re.search(r'^From:\s*(.+)', text, re.MULTILINE)
        if fro:
            self.From = fro.group(1).strip()
        fro = re.search(r'^От кого:\s*(.+)', text, re.MULTILINE)
        if fro:
            self.From = fro.group(1).strip()
        fro = re.search(r'^Ot kogo:\s*(.+)', text, re.MULTILINE)
        if fro:
            self.From = fro.group(1).strip()

        to = re.search(r'^To:\s*(.+)', text, re.MULTILINE)
        if to:
            self.To = to.group(1).strip()
        to = re.search(r'^Кому:\s*(.+)', text, re.MULTILINE)
        if to:
            self.To = to.group(1).strip()
        to = re.search(r'^Komu:\s*(.+)', text, re.MULTILINE)
        if to:
            self.To = to.group(1).strip()

        sub = re.search(r'^Subject:\s*(.+)', text, re.MULTILINE)
        if sub:
            self.Subject = sub.group(1).strip()
        sub = re.search(r'^Тема:\s*(.+)', text, re.MULTILINE)
        if sub:
            self.Subject = sub.group(1).strip()
        sub = re.search(r'^Tema:\s*(.+)', text, re.MULTILINE)
        if sub:
            self.Subject = sub.group(1).strip()

        date = re.search(r'^Date:\s*(.+)', text, re.MULTILINE)
        if date:
            self.Date = date.group(1).strip()
        date = re.search(r'^Дата:\s*(.+)', text, re.MULTILINE)
        if date:
            self.Date = date.group(1).strip()
        date = re.search(r'^Data:\s*(.+)', text, re.MULTILINE)
        if date:
            self.Date = date.group(1).strip()

        body2 = text.replace('\r\n', '\n').replace('\r', '\n')

        body = body2.split('\n\n', 1)

        if len(body) == 2:
            self.Body = body[1].strip()



class MailClassifier:
    def __init__(self, pyt):
        self.pyt = pyt
        self.folders = ['Incidents', 'Access', 'Spam', 'Support', 'Info', 'Documents', 'Other']
        self.__SYSTEM_PROMPT = """
Роль: Ты – система классификации корпоративной почты IT-поддержки. Твоя задача – определить категорию входящего письма на основе его содержимого.
Входной формат: JSON-объект с полями From, Subject, Body. Некоторые поля могут быть пустыми строками.

Выходной формат: Только JSON вида {"category": "название_категории"}. Никаких пояснений, дополнительного текста или разметки.
Список возможных категорий (строго одна из восьми):

1. Incidents – критический инциденты, сбои.
2. Access – все запросы, не требующие технического вмешательства, а связанные с управлением сотрудниками и их правами.
3. Spam - фишинг, реклама, выигрыши, подозрительные ссылки, акции, скидки и подобное.
4. Support – технические проблемы.
5. Info – информационные рассылки.
6. Documents – любые документы, счета, акты и тому подобное.
7. Other – если письмо не подходит ни под одну из перечисленных категорий.

Примеры:

Вход:{"From": "s.volkov@partner.ru", "Subject": "браузер Chrome зависает при открытии", "Body": "После обновления системы браузер Chrome не открывает файлы нужного формата. Раньше всё работало."}
Выход:{"category": "Support"}
"""

    def classification_ai(self, data: json):
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        
        try:
            user_message = json.dumps(data)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.__SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.1,
            )

            raw_content = response.choices[0].message.content
            result = json.loads(raw_content)['category']

            # Базовая валидация
            pass 

            return result

        except Exception as e:
            return "Other"

    def classification(self, data, use_ai=False):
        """
        data: dict с ключами 'From', 'Subject', 'Body' (все могут быть пустыми)
        возвращает одну из категорий self.folders
        """

        if use_ai:
            return self.classification_ai(data)

        from_addr = (data.get('From', '') or '').lower()
        subject = (data.get('Subject', '') or '').lower()
        body = (data.get('Body', '') or '').lower()
        full_text = f"{subject} {body}"


        weights = defaultdict(float)


        incident_patterns = [
            (r'ошибка|error|сбой|происшествие|восстанов|срочн', 6),
            (r'не отвечает|недоступен|не работает|не открывается|не запускается', 3),
            (r'работа остановлена|массовый сбой|критичный инцидент', 5),
            (r'alert*|немедленно', 4),
            (r'urgent|critical|crash|down', 3)
        ]
        for pattern, score in incident_patterns:
            if re.search(pattern, full_text):
                weights['Incidents'] += score


        spam_patterns = [
            (r'выиграл|розыгрыш|приз|победител|поздрав|подтвердите личность|подозрительн', 5),
            (r'подтвердит[ье]\s+личност|верификация аккаунта|войдите по ссылке|будет\s+заблокирован', 4),
            (r'http://', 2),
            (r'скидк|акция|эксклюзив|немедленно', 3),
            (r'пароль истекает.*обновите|ваш аккаунт будет заблокирован', 5),
        ]
        for pattern, score in spam_patterns:
            if re.search(pattern, full_text):
                weights['Spam'] += score


        access_patterns = [
            (r'доступ|права|времен\w+ сотруд', 7),
            (r'новый сотрудник|подготовить рабочее место|выход на работу', 4),
            (r'отпуск|больничный|нетрудоспособност|больничн', 3),
            (r'восстановить доступ|пропал доступ|нет доступа', 4),
            (r'уровень доступа|права на чтение|доступ к системе', 3),
            (r'выход\s+на\s+работу|подготовить\s+рабочее\s+место|(создать|завести|сделать) учетн\w+ запись|', 5),
        ]
        for pattern, score in access_patterns:
            if re.search(pattern, full_text):
                weights['Access'] += score


        support_patterns = [
            (r'после обновления|после переустановки|жалоб|перезайти', 5),
            (r'не открывает файлы|не читает|зависает|тормозит|вылетает|сломал|нужная помощь|что*делать|антивирус', 3),
            (r'браузер|антивирус|excel|adobe reader|outlook|zoom|confluence|gitlab|jira', 2),
            (r'принтер|сканер|гарнитур|ноутбук|мышь|ремонт|не включается|сломался|устройство:', 5),
            (r'зависает|код ошибки', 2),
            (r'помогите|нужна помощь|что делать', 1),
        ]
        for pattern, score in support_patterns:
            if re.search(pattern, full_text):
                weights['Support'] += score


        info_patterns = [
            (r'дайджест|выпуск|приглаш|созвон|отчет|отчёт|напомина|созвон', 6),
            (r'плановы', 3),
            (r'uptime|среднее время ответа|ошибок 5xx', 2),
            (r'(технические|плановые) работы', 2),
        ]
        for pattern, score in info_patterns:
            if re.search(pattern, full_text):
                weights['Info'] += score


        doc_patterns = [
            (r'инструкци|задание|согласов|договор|контракт|документ|технич* задани|тз|оплата|реквизиты|счёт|акт|договор', 4),
            (r'вложени|прикреп|файл|документ|скан', 2),
            (r'направляем|просим проверить|подпись|правки', 2),
            (r'\.docx|\.pdf|screenshot|_log\.txt', 2),
            (r'счёт на|счёт №\d+|инвойс|invoice|бухгалтер', 5),
        ]
        for pattern, score in doc_patterns:
            if re.search(pattern, full_text):
                weights['Documents'] += score


        if not weights:
            return 'Other'

        best_category = max(weights.items(), key=lambda x: x[1])[0]

        # Если вес слишком маленький 
        if weights[best_category] < 5:
            return 'Other'

        return best_category

    def sort_files(self, use_ai=False):
        log = []

        try:
            if str(self.pyt[1])[-3:] == "zip":
                shutil.unpack_archive(self.pyt[1], extract_dir="new_data")
            else:
                shutil.copytree(self.pyt[1], Path(__file__).resolve().parent / "new_data", dirs_exist_ok=True)
        except IndexError:
            log.append("Не передан путь к архиву, запустить код через Bash крипт с указание Path на архив")
            print("Не передан путь к архиву, запустить код через Bash крипт с указание Path на архив")
            exit(0)

        ds_path = Path("new_data/inbox/.DS_Store")
        ds_path.unlink(missing_ok=True)

        sc_dir = Path(__file__).resolve().parent

        folder_map = {}
        for folder_name in self.folders:
            path = sc_dir / folder_name
            shutil.rmtree(path, ignore_errors=True)
            path.mkdir(exist_ok=True)

            folder_map[folder_name] = path

        folder = Path("new_data")
        files = [f for f in folder.rglob("*") if f.is_file()]
        for file_path in files:
            if file_path.is_file():
                log.append(f"Файл {file_path} принят в обработку")
                print(f"Файл {file_path} принят в обработку")
                if str(file_path)[-3:] == "txt" or str(file_path)[-3:] == "eml":
                    
                    # print('file_path:', file_path)
                    try:
                        text = file_path.read_text(encoding="utf-8")

                        data = Mail(text)
                        res = self.classification(data.to_json(), use_ai=use_ai)

                        target_folder = folder_map.get(res)
                        if target_folder:
                            shutil.move(str(file_path), str(target_folder), )
                            log.append(f"Файл {file_path} успешно перемещен в {target_folder}")
                            print(f"Файл {file_path} успешно перемещен в {target_folder}")
                    except UnicodeDecodeError:
                        log.append(f"Файл {file_path} имеет некорректную кодировку, пропущен")
                        print(f"Файл {file_path} имеет некорректную кодировку, пропущен")
                        continue


                elif str(file_path)[-3:] == "bin":
                    log.append(f"Файл {file_path} не удалось расшифровать")
                    print(f"Файл {file_path} не удалось расшифровать")

                elif str(file_path)[-4:] == "json":
                    log.append(f"Файл {file_path} не удалось расшифровать")
                    print(f"Файл {file_path} не удалось расшифровать")

                elif str(file_path)[-4:] == "jpeg":
                    log.append(f"Файл {file_path} не является письмом")
                    print(f"Файл {file_path} не является письмом")

                else:
                    log.append(f"Файл {file_path} является неизвестным форматом")
                    print(f"Файл {file_path} является неизвестным форматом")

        # for i in log:
        #     print(i)


def main():
    pyt = sys.argv
    cl = MailClassifier(pyt)

    cl.sort_files()

if __name__ == "__main__":
    main()
