from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class DateUtils:
    def __init__(self, fmt: str = "%Y-%m-%d %H:%M:%S"):
        self.format = fmt

    def set_format(self, fmt: str):
        self.format = fmt

    def _start_of_day(self, dt: datetime) -> datetime:
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    # ==== БАЗОВЫЕ ====
    def today(self):
        now = datetime.now()  # ✅ обязательно со скобками
        start = self._start_of_day(now)
        return start.strftime(self.format), now.strftime(self.format)

    def yesterday(self):
        now = datetime.now()
        yest = now - timedelta(days=1)
        start = self._start_of_day(yest)
        end = start + timedelta(days=1) - timedelta(seconds=1)
        return start.strftime(self.format), end.strftime(self.format)

    def this_week(self):
        now = datetime.now()
        start = self._start_of_day(now - timedelta(days=now.weekday()))
        return start.strftime(self.format), now.strftime(self.format)

    def this_month(self):
        now = datetime.now()
        start = self._start_of_day(now.replace(day=1))
        return start.strftime(self.format), now.strftime(self.format)

    def this_year(self):
        now = datetime.now()
        start = self._start_of_day(now.replace(month=1, day=1))
        return start.strftime(self.format), now.strftime(self.format)

    # ==== СО СМЕЩЕНИЕМ ====
    def days_ago(self, n: int):
        now = datetime.now()
        start = self._start_of_day(now - timedelta(days=n))
        return start.strftime(self.format), now.strftime(self.format)

    def weeks_ago(self, n: int):
        now = datetime.now()
        start = self._start_of_day(now - timedelta(weeks=n))
        return start.strftime(self.format), now.strftime(self.format)

    def months_ago(self, n: int):
        now = datetime.now()
        start = self._start_of_day(now - relativedelta(months=n))
        return start.strftime(self.format), now.strftime(self.format)

    def years_ago(self, n: int):
        now = datetime.now()
        start = self._start_of_day(now - relativedelta(years=n))
        return start.strftime(self.format), now.strftime(self.format)

    # ==== УНИВЕРСАЛЬНЫЙ ====
    def range(self, period: str):
        """
        Поддерживаемые варианты:
        du.range("today")
        du.range("yesterday")
        du.range("this_week")
        du.range("this_month")
        du.range("this_year")
        du.range("days:7"), du.range("d7")
        du.range("weeks:2"), du.range("w2")
        du.range("months:3"), du.range("m3")
        du.range("years:1"), du.range("y1")
        """
        # стандартные ключевые слова
        if period == "today":
            return self.today()
        elif period == "yesterday":
            return self.yesterday()
        elif period == "this_week":
            return self.this_week()
        elif period == "this_month":
            return self.this_month()
        elif period == "this_year":
            return self.this_year()

        # формат "тип:число"
        if ":" in period:
            kind, value = period.split(":")
            n = int(value)
            if kind == "days":
                return self.days_ago(n)
            elif kind == "weeks":
                return self.weeks_ago(n)
            elif kind == "months":
                return self.months_ago(n)
            elif kind == "years":
                return self.years_ago(n)

        # короткие алиасы: d7, w2, m3, y1
        if period[0] in "dwmy" and period[1:].isdigit():
            kind = period[0]
            n = int(period[1:])
            if kind == "d":
                return self.days_ago(n)
            elif kind == "w":
                return self.weeks_ago(n)
            elif kind == "m":
                return self.months_ago(n)
            elif kind == "y":
                return self.years_ago(n)

        raise ValueError(f"Неизвестный период: {period}")

    # ==== ВСПОМОГАТЕЛЬНОЕ ====
    def convert_date(self, date_str: str) -> datetime:
        return datetime.strptime(date_str, self.format)