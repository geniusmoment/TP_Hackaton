import sys
import shutil
from pathlib import Path
import re

import json
import logging
from collections import defaultdict
from openai import OpenAI

import time
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
logger = logging.getLogger(__name__)

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

class MailAnalytics:
    def __init__(self):
        self.total_files_seen = 0
        self.processed_mails = 0
        self.skipped_encodings = 0
        self.skipped_formats = defaultdict(int)
        self.category_counts = defaultdict(int)
        self.start_time = 0.0
        self.end_time = 0.0

    def start_timer(self): self.start_time = time.time()
    def stop_timer(self): self.end_time = time.time()

    @property
    def total_duration(self): return self.end_time - self.start_time

    @property
    def avg_time(self): return self.total_duration / self.processed_mails if self.processed_mails else 0.0

    def log_file_seen(self): self.total_files_seen += 1
    def log_encoding_error(self): self.skipped_encodings += 1
    def log_skipped_format(self, extension): self.skipped_formats[extension] += 1
    
    def log_processed(self, category):
        self.processed_mails += 1
        self.category_counts[category] += 1

    def generate_reports(self, output_dir: Path):
        print(f"\nTotal Duration:  {self.total_duration:.2f} sec")
        print(f"Avg Time per Mail:  {self.avg_time:.4f} sec")
        print(f"Total Files Detected :  {self.total_files_seen} files\n")

        if self.total_files_seen == 0: 
            return

        output_dir.mkdir(parents=True, exist_ok=True)
        sns.set_theme(style="whitegrid")
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('Отчет по обработке писем', fontsize=16, fontweight='bold')

        if self.category_counts:
            axes[0].pie(self.category_counts.values(), labels=self.category_counts.keys(), autopct='%1.1f%%', 
                        startangle=140, colors=sns.color_palette("pastel", len(self.category_counts)), 
                        wedgeprops={'edgecolor': 'gray', 'linewidth': 1.0})
        else:
            axes[0].text(0.5, 0.5, 'Нет обработанных писем', ha='center', va='center')
        axes[0].set_title('Распределение по категориям', fontsize=12, fontweight='bold')

        stats_val = [self.total_files_seen, self.processed_mails, self.skipped_encodings, sum(self.skipped_formats.values())]
        
        sns.barplot(x=stats_val, y=['Всего файлов', 'Обработано', 'Ошибка декодирования', 'Неверный формат'], ax=axes[1], palette="viridis")
        axes[1].set_title('Успешность обработки', fontsize=12, fontweight='bold')
        axes[1].set_xlabel('файлов')
        
        for i, v in enumerate(stats_val):
            axes[1].text(v + 0.2, i, str(v), va='center', fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_dir / "analytics.png", dpi=300)
        plt.close()

class MailClassifier:
    def __init__(self, pyt):
        self.pyt = pyt
        self.folders = ['Incidents', 'Access', 'Spam', 'Support', 'Info', 'Documents', 'Other']
        self.analytics = MailAnalytics()
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
        self.analytics.start_timer()
        try:
            if str(self.pyt[1])[-3:] == "zip":
                shutil.unpack_archive(self.pyt[1], extract_dir="new_data")
            else:
                shutil.copytree(self.pyt[1], Path(__file__).resolve().parent / "new_data", dirs_exist_ok=True)
        except IndexError:
            logger.info("Не передан путь к архиву, запустить код через Bash крипт с указание Path на архив")
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
            self.analytics.log_file_seen()
            if file_path.is_file():
                ext = file_path.suffix.lower().replace('.', '')
                logger.info(f"Файл {file_path} принят в обработку")
                if str(file_path)[-3:] == "txt" or str(file_path)[-3:] == "eml":
                    
                    # print('file_path:', file_path)
                    try:
                        text = file_path.read_text(encoding="utf-8")

                        data = Mail(text)
                        res = self.classification(data.to_json(), use_ai=use_ai)

                        target_folder = folder_map.get(res)
                        if target_folder:
                            shutil.move(str(file_path), str(target_folder), )
                            logger.info(f"Файл {file_path} успешно перемещен в {target_folder}")
                        self.analytics.log_processed(res)
                    except UnicodeDecodeError:
                        logger.info(f"Файл {file_path} имеет некорректную кодировку, пропущен")
                        continue


                elif str(file_path)[-3:] == "bin":
                    logger.info(f"Файл {file_path} не удалось расшифровать")
                    self.analytics.log_skipped_format(ext or "no_ext")

                elif str(file_path)[-4:] == "json":
                    logger.info(f"Файл {file_path} не удалось расшифровать")
                    self.analytics.log_skipped_format(ext or "no_ext")

                elif str(file_path)[-4:] == "jpeg":
                    logger.info(f"Файл {file_path} не является письмом")
                    self.analytics.log_skipped_format(ext or "no_ext")

                else:
                    logger.info(f"Файл {file_path} является неизвестным форматом")
                    self.analytics.log_skipped_format(ext or "no_ext")

        self.analytics.stop_timer()

        self.analytics.generate_reports(sc_dir)


def main():
    pyt = sys.argv
    cl = MailClassifier(pyt)

    cl.sort_files()

if __name__ == "__main__":
    main()
