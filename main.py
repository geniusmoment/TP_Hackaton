import sys
import shutil
from pathlib import Path
import re
import shutil
import json

def classification(data):
    """
    :param data: {"From": str, "To": str, "Subject": str, "Date": str, "Body": str}
    :return: "Важное" | "Спам" | "Черновик" | "Исходящее"
    """
    import random
    return random.choice(["Важное", "Спам", "Черновик", "Исходящие"])

def parse(text):
    data = {}

    fro = re.search(r'From:\s*(.+)', text, re.MULTILINE)
    if fro:
        data["From"] = fro.group(1).strip()
    fro = re.search(r'От кого:\s*(.+)', text, re.MULTILINE)
    if fro:
        data["From"] = fro.group(1).strip()
    fro = re.search(r'От кого:\s*(.+)', text, re.MULTILINE)
    if fro:
        data["From"] = fro.group(1).strip()

    to = re.search(r'To:\s*(.+)', text, re.MULTILINE)
    if to:
        data["To"] = to.group(1).strip()
    to = re.search(r'Кому:\s*(.+)', text, re.MULTILINE)
    if to:
        data["To"] = to.group(1).strip()
    to = re.search(r'Komu:\s*(.+)', text, re.MULTILINE)
    if to:
        data["To"] = to.group(1).strip()

    sub = re.search(r'Subject:\s*(.+)', text, re.MULTILINE)
    if sub:
        data["Subject"] = sub.group(1).strip()
    sub = re.search(r'Тема:\s*(.+)', text, re.MULTILINE)
    if sub:
        data["Subject"] = sub.group(1).strip()
    sub = re.search(r'Tema:\s*(.+)', text, re.MULTILINE)
    if sub:
        data["Subject"] = sub.group(1).strip()

    date = re.search(r'Date:\s*(.+)', text, re.MULTILINE)
    if date:
        data["Date"] = date.group(1).strip()
    date = re.search(r'Дата:\s*(.+)', text, re.MULTILINE)
    if date:
        data["Date"] = date.group(1).strip()
    date = re.search(r'Data:\s*(.+)', text, re.MULTILINE)
    if date:
        data["Date"] = date.group(1).strip()

    body2 = text.replace('\r\n', '\n').replace('\r', '\n')

    body = body2.split('\n\n', 1)

    if len(body) == 2:
        data["Body"] = body[1].strip()

    return data



def main():

    log = []

    pyt = sys.argv

    shutil.unpack_archive(pyt[1], extract_dir="new_data")

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
    for file_path in folder.rglob("*"):
        if file_path.is_file():
            if str(file_path)[-3:] == "txt":
                text = file_path.read_text(encoding="utf-8")

                data = parse(text)

                res = classification(data)
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
                with open(file_path, "rb") as f:
                    data = f.read()
                try:
                    data.decode(encoding="utf-8")
                    data = parse(data)

                    res = classification(data)
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

                except UnicodeDecodeError:
                    log.append(f"Файл {file_path} не удалось расшифровать")

            elif str(file_path)[-4:] == "json":
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    data = parse(data)

                    res = classification(data)
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

                except json.decoder.JSONDecodeError:
                    log.append(f"Файл {file_path} не удалось расшифровать")
            elif str(file_path)[-4:] == "jpeg":
                log.append(f"Файл {file_path} не является письмом")
            else:
                text = file_path.read_text(encoding="utf-8")
                data = parse(text)

                res = classification(data)
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
    for i in log:
        print(i)



if __name__ == "__main__":
    main()