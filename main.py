import sys
import shutil
from pathlib import Path
import re

class Mail():
    def __init__(self, text):
        self.From = ""
        self.To = ""
        self.Subject = ""
        self.Date = ""
        self.Body = ""
        self.clas = None
        self._parse(text)

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



def classification(data):
    """
    :param data: {"From": str, "To": str, "Subject": str, "Date": str, "Body": str}
    :return: "Важное" | "Спам" | "Черновик" | "Исходящие"
    """
    import random
    return random.choice(["Важное", "Спам", "Черновик", "Исходящие"])





def main():

    log = []

    pyt = sys.argv

    try:
        shutil.unpack_archive(pyt[1], extract_dir="new_data")
    except IndexError:
        log.append("Не передан путь к архиву")

    ds_path = Path("new_data/inbox/.DS_Store")
    ds_path.unlink(missing_ok=True)

    sc_dir = Path(__file__).resolve().parent
    p_1 = sc_dir / "Важное"
    p_1.mkdir(exist_ok=True)
    p_2 = sc_dir / "Спам"
    p_2.mkdir(exist_ok=True)
    p_3 = sc_dir / "Черновик"
    p_3.mkdir(exist_ok=True)
    p_4 = sc_dir / "Исходящие"
    p_4.mkdir(exist_ok=True)

    folder = Path("new_data")
    files = [f for f in folder.rglob("*") if f.is_file()]
    for file_path in files:
        if file_path.is_file():
            log.append(f"Файл {file_path} принят в обработку")
            if str(file_path)[-3:] == "txt" or str(file_path)[-3:] == "eml":
                text = file_path.read_text(encoding="utf-8")

                data = Mail(text)
                data2 = {"From": data.From, "To": data.To, "Subject": data.Subject, "Date": data.Date, "Body": data.Body}

                res = classification(data2)
                if res == "Важное":
                    shutil.move(str(file_path), str(p_1))
                    log.append(f"Файл {file_path} успешно перемещен в {p_1}")
                if res == "Спам":
                    shutil.move(str(file_path), str(p_2))
                    log.append(f"Файл {file_path} успешно перемещен в {p_2}")
                if res == "Черновик":
                    shutil.move(str(file_path), str(p_3))
                    log.append(f"Файл {file_path} успешно перемещен в {p_3}")
                if res == "Исходящие":
                    shutil.move(str(file_path), str(p_4))
                    log.append(f"Файл {file_path} успешно перемещен в {p_4}")

            elif str(file_path)[-3:] == "bin":
                log.append(f"Файл {file_path} не удалось расшифровать")

            elif str(file_path)[-4:] == "json":
                log.append(f"Файл {file_path} не удалось расшифровать")

            elif str(file_path)[-4:] == "jpeg":
                log.append(f"Файл {file_path} не является письмом")

            else:
                log.append(f"Файл {file_path} является неизвестным форматом")

    for i in log:
        print(i)



if __name__ == "__main__":
    main()