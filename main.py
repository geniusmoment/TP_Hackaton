import sys
import shutil
from pathlib import Path
import re


class Mail:
    def __init__(self, text):
        self.From = ""
        self.To = ""
        self.Subject = ""
        self.Date = ""
        self.Body = ""
        self.clas = None
        self._parse(text)

    def to_json(self):
        return {
            "From": self.From,
            "To": self.To,
            "Subject": self.Subject,
            "Date": self.Date,
            "Body": self.Body,
        }

    def _parse(self, text):
        fro = re.search(r"^From:\s*(.+)", text, re.MULTILINE)
        if fro:
            self.From = fro.group(1).strip()
        fro = re.search(r"^От кого:\s*(.+)", text, re.MULTILINE)
        if fro:
            self.From = fro.group(1).strip()
        fro = re.search(r"^Ot kogo:\s*(.+)", text, re.MULTILINE)
        if fro:
            self.From = fro.group(1).strip()

        to = re.search(r"^To:\s*(.+)", text, re.MULTILINE)
        if to:
            self.To = to.group(1).strip()
        to = re.search(r"^Кому:\s*(.+)", text, re.MULTILINE)
        if to:
            self.To = to.group(1).strip()
        to = re.search(r"^Komu:\s*(.+)", text, re.MULTILINE)
        if to:
            self.To = to.group(1).strip()

        sub = re.search(r"^Subject:\s*(.+)", text, re.MULTILINE)
        if sub:
            self.Subject = sub.group(1).strip()
        sub = re.search(r"^Тема:\s*(.+)", text, re.MULTILINE)
        if sub:
            self.Subject = sub.group(1).strip()
        sub = re.search(r"^Tema:\s*(.+)", text, re.MULTILINE)
        if sub:
            self.Subject = sub.group(1).strip()

        date = re.search(r"^Date:\s*(.+)", text, re.MULTILINE)
        if date:
            self.Date = date.group(1).strip()
        date = re.search(r"^Дата:\s*(.+)", text, re.MULTILINE)
        if date:
            self.Date = date.group(1).strip()
        date = re.search(r"^Data:\s*(.+)", text, re.MULTILINE)
        if date:
            self.Date = date.group(1).strip()

        body2 = text.replace("\r\n", "\n").replace("\r", "\n")

        body = body2.split("\n\n", 1)

        if len(body) == 2:
            self.Body = body[1].strip()


class MailClassifier:
    def __init__(self, pyt):
        self.pyt = pyt
        self.folders = [
            "Incidents",
            "Access",
            "Spam",
            "Support",
            "Info",
            "Documents",
            "Other",
        ]

    def classification(self, data):
        """
        :param data: {"From": str, "To": str, "Subject": str, "Date": str, "Body": str}
        :return: 1 категорию из self.folders
        """
        import random

        return random.choice(self.folders)

    def sort_files(self):
        log = []

        try:
            shutil.unpack_archive(self.pyt[1], extract_dir="new_data")
        except IndexError:
            log.append("Не передан путь к архиву")

        ds_path = Path("new_data/inbox/.DS_Store")
        ds_path.unlink(missing_ok=True)

        sc_dir = Path(__file__).resolve().parent
        folder_map = {}
        for folder_name in self.folders:
            path = sc_dir / folder_name
            path.mkdir(exist_ok=True)

            folder_map[folder_name] = path

        folder = Path("new_data")
        files = [f for f in folder.rglob("*") if f.is_file()]
        for file_path in files:
            if file_path.is_file():
                log.append(f"Файл {file_path} принят в обработку")
                if str(file_path)[-3:] == "txt" or str(file_path)[-3:] == "eml":
                    text = file_path.read_text(encoding="utf-8")

                    data = Mail(text)

                    res = self.classification(data.to_json())
                    target_folder = folder_map.get(res)
                    if target_folder:
                        shutil.move(str(file_path), str(target_folder))
                        log.append(
                            f"Файл {file_path} успешно перемещен в {target_folder}"
                        )

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


def main():
    pyt = sys.argv
    cl = MailClassifier(pyt)

    cl.sort_files()


if __name__ == "__main__":
    main()
