import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.append(str(Path(__file__).parent.parent))

from main import Mail, MailClassifier


class TestIncidentsCategory: # сделан
    """Тесты для категории Incidents - критические инциденты и сбои"""
    
    @pytest.fixture
    def classifier(self):
        with patch("builtins.open"):
            return MailClassifier(["script.py", "fake.zip"])
    
    @pytest.mark.parametrize("subject,body", [
        ("СРОЧНО!", "Произошла критическая ошибка"),
        ("Система не отвечает", "Работа остановлена"),
        ("Critical error", "System crashed unexpectedly"),
        ("Восстановление данных", "Требуется срочное восстановление"),
        ("Ошибка в дата-центре", "Отключилось охлаждение"),
        ("Критичный инцидент", "Система не работает"),
        ("Работа остановлена", "Производство встало"),
        ("Alert!","Корпус затопило, срочно покиньте здание"),
        ("Error: не работает", "Need urgent recovery"),
        ("URGENT: alert, Server down", "Production server is not responding")
    ])
    def test_incidents_detection(self, classifier, subject, body):
        """Проверка, что письма с инцидентами определяются как Incidents, From = """
        data = {
            "From": "coder228@HSE.com",
            "Subject": subject,
            "Body": body
        }
        result = classifier.classification(data, use_ai=False)
        assert result == "Incidents", f"Ошибка: {subject} | {body} → получено {result}"



class TestAccessCategory: # сделан
    """Тесты для категории Access - управление доступом и правами"""
    
    @pytest.fixture
    def classifier(self):
        with patch("builtins.open"):
            return MailClassifier(["script.py", "fake.zip"])
    
    @pytest.mark.parametrize("subject,body", [
        ("Запрос на доступ", "Нужно предоставить доступ к папке 'Отчеты'"),
        ("Создать учетную запись", "У нас новый сотрудник."),
        ("Восстановить доступ", "Сотрудник вышел из отпуска"),
        ("Подготовить рабочее место", "Сотрудник вышел с больничного"),
        ("Восстановить доступ", "Пользователь потерял доступ к почте"),
        ("Права на чтение", "Выдайте права на чтение новой папки"),
        ("Повысить уровень доступа", "Для руководителя отдела"),
        ("Больничный", "Уровень доступа изменился"),
    ])
    def test_access_detection(self, classifier, subject, body):
        """Проверка, что запросы доступа определяются как Access"""
        data = {
            "From": "hr@HSE.com",
            "Subject": subject,
            "Body": body
        }
        result = classifier.classification(data, use_ai=False)
        assert result == "Access", f"Ошибка в тесте: {subject} | {body}"



class TestSpamCategory: # сделан
    """Тесты для категории Spam - спам, фишинг, реклама"""
    
    @pytest.fixture
    def classifier(self):
        with patch("builtins.open"):
            return MailClassifier(["script.py", "fake.zip"])
    
    @pytest.mark.parametrize("subject,body", [
        # Выигрыши и призы
        ("ВЫ ВЫИГРАЛИ IPhone!", "Перейдите по ссылке для получения приза"),
        ("Поздравляем с победой!", "Вы стали нашим 1000-м посетителем"),
        ("Выигрыш миллиона", "Заполните форму для получения денег"),
        
        # Фишинг и прочий скам 
        ("Подтвердите личность", "Ваш аккаунт будет заблокирован через 24 часа"),
        ("Верификация аккаунта", "Немедленно войдите по ссылке для подтверждения"),
        ("Обновите пароль", "Срок действия пароля истекает"),
        ("Ваш аккаунт будет заблокирован", "Срочно перейдите по ссылке"),
        ("Скидка 90% только сегодня", "Эксклюзивное предложение, действуйте немедленно"),
        ("Эксклюзивное предложение", "Войдите по ссылке"),
        ("Черная пятница", "Товары со скидкой до 70%, http://fake-link.com/confirm"),
        ("Важное сообщение", "войдите по ссылке https://scam-site.ru"),
    ])
    def test_spam_detection(self, classifier, subject, body):
        """Проверка, что спам-письма определяются как Spam"""
        data = {
            "From": "noreply@HSE.com",
            "Subject": subject,
            "Body": body
        }
        result = classifier.classification(data, use_ai=False)
        assert result == "Spam", f"Ошибка в тесте: {subject} | {body}"

class TestSupportCategory: # сделан
    """Тесты для категории Support - технические проблемы"""
    
    @pytest.fixture
    def classifier(self): 
        with patch("builtins.open"):
            return MailClassifier(["script.py", "fake.zip"])
    
    @pytest.mark.parametrize("subject,body", [
        ("Браузер зависает", "Chrome не открывает файлы после обновления"),
        ("Excel вылетает", "При открытии большой таблицы"),
        ("Нет доступа", "Доступ к Adobe Reader потерян"),
        ("Антивирус блокирует", "Программу распознает как вирус"),
        ("Принтер не печатает", "Выдает ошибку 'нет бумаги', хотя бумага есть"),
        ("Сканер не работает", "Устройство не определяется"),
        ("Ноутбук не включается", "После обновления завис на черном экране"),
        ("Сломалась мышь", "Не нажимаются кнопки"),
        ("Гарнитура не работает", "В Zoom нет звука"),
        ("Помогите!", "Что делать, если не загружается сайт?"),
        ("VPN не работает", "Не могу подключиться к VPN, ошибка 800"),
    ])
    def test_support_detection(self, classifier, subject, body):
        """Проверка, что технические проблемы определяются как Support"""
        data = {
            "From": "user@HSE.com",
            "Subject": subject,
            "Body": body
        }
        result = classifier.classification(data, use_ai=False)
        assert result == "Support", f"Ошибка в тесте: {subject} | {body}"


class TestInfoCategory:
    """Тесты для категории Info - информационные рассылки"""
    
    @pytest.fixture
    def classifier(self):
        with patch("builtins.open"):
            return MailClassifier(["script.py", "fake.zip"])
    
    @pytest.mark.parametrize("subject,body", [
        ("Еженедельный дайджест", "Главные новости компании за неделю"),
        ("Новый выпуск", "Вышел апрельский номер корпоративной газеты"),
        ("Приглашение на встречу", "Приглашаем вас на созвон в 15:00"),
        ("Созвон по проекту", "Ссылка для подключения в письме"),
        ("Отчет за май", "Результаты работы отдела"),
        ("Квартальный отчет", "Финансовые показатели"),
        ("Напоминание о дедлайне", "Завтра последний день сдачи отчетов"),
        ("Плановые работы", "Система будет недоступна в выходные с 2:00 до 6:00"),
        ("Технические работы", "Вышел выпуск новостей: обновление серверов 5 июня"),
        ("Uptime за неделю", "Отчет: доступность системы составила 99.9%"),
        ("Ошибки 5xx", "Дайджест: количество ошибок сократилось на 15%"),
    ])
    def test_info_detection(self, classifier, subject, body):
        """Проверка, что информационные письма определяются как Info"""
        data = {
            "From": "noreply@HSE.com",
            "Subject": subject,
            "Body": body
        }
        result = classifier.classification(data, use_ai=False)
        assert result == "Info", f"Ошибка в тесте: {subject} | {body}"


class TestDocumentsCategory: # сделан
    """Тесты для категории Documents - документы, счета, договоры"""
    
    @pytest.fixture
    def classifier(self):
        with patch("builtins.open"):
            return MailClassifier(["script.py", "fake.zip"])
    
    @pytest.mark.parametrize("subject,body", [
        ("Счет на оплату №123", "Оплатите счет до 30 июня"),
        ("Инвойс от поставщика", "Invoice №INV-2024-001"),
        ("Счет №45 от 01.06", "На сумму 50 000 рублей"),
        ("Договор на подпись", "Просим подписать договор оказания услуг"),
        ("Контракт с заказчиком", "Согласование финальной версии"),
        ("Техническое задание", "ТЗ на разработку системы"),
        ("Акт выполненных работ", "Просим подписать акт"),
        ("Спецификация", "Описание требований к оборудованию, документ во вложении"),
        ("Документы во вложении", "Прикрепляем скан договора"),
        ("Проверьте файл", "Во вложении pdf-файл с подробностями"),
        ("Реквизиты для оплаты", "Банковские реквизиты организации"),
        ("Бухгалтерская справка", "Для закрытия периода"),
    ])
    def test_documents_detection(self, classifier, subject, body):
        """Проверка, что письма с документами определяются как Documents"""
        data = {
            "From": "doc@HSE.com",
            "Subject": subject,
            "Body": body
        }
        result = classifier.classification(data, use_ai=False)
        assert result == "Documents", f"Ошибка в этом тесте: {subject} | {body}"


class TestOtherCategory: # сделано
    """Тесты для категории Other - всё остальное"""
    
    @pytest.fixture
    def classifier(self):
        with patch("builtins.open"):
            return MailClassifier(["script.py", "fake.zip"])
    
    @pytest.mark.parametrize("subject,body", [
        ("Бог", "шо?"),
        ("Спас бог", "!"),
        ("Спасибо хорошо!", ":)"),

        ("пам пам пам пам па па па па па па па пам пам", "мел?"),
        ("", ""),
        ("Тест", "Тестовое сообщение для проверки"),
        ("Без темы", "Неважное содержание"),
        ("Ок", "Да"),
        ("Доброе утро", "Доброе утро всем"),
        ("Вопрос", "У меня есть вопрос, но я его напишу потом"),
        ("Интересно", "Мне интересно ваше мнение"),
    ])
    def test_other_detection(self, classifier, subject, body):
        """Проверка, что неподходящие письма определяются как Other"""
        data = {
            "From": "unknown@HSE.com",
            "Subject": subject,
            "Body": body
        }
        result = classifier.classification(data, use_ai=False)
        assert result == "Other", f"Ошибка в этом тесте: {subject} | {body}. Получено: {result}"


class TestCategoryCompetition:
    """Тесты, когда письмо подходит под несколько категорий"""
    
    @pytest.fixture
    def classifier(self):
        with patch("builtins.open"):
            return MailClassifier(["script.py", "fake.zip"])
    
    @pytest.mark.parametrize("subject,body,expected", [
        ("Не открывается счет", "Прикрепляю счет на оплату, но файл не открывается, программа зависает", "Documents"),
        ("Нет доступа к принтеру", "Не могу печатать, выдает ошибку доступа", "Access"),
        ("Выиграйте принтер!", "Перейдите по ссылке и получите принтер в подарок", "Support"),
        ("Критическая ошибка принтера", "Принтер сломался, срочно чините, система недоступна", "Incidents"),
        ("Отчет с вложением", "Еженедельный отчет во вложении, прикрепляю файл", "Documents"),
    ])
    def test_multiple_categories(self, classifier, subject, body, expected):
        """Проверка определения при конкуренции категорий"""
        data = {
            "From": "user@HSE.com",
            "Subject": subject,
            "Body": body
        }
        result = classifier.classification(data, use_ai=False)
        assert result == expected, f"Ошибка в тесте {subject} | {body}. Ожидалось: {expected}, получено: {result}"
    


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
