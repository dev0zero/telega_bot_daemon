
# получаем коментарии и проверяем и производим какие то действия

class Commentator:
    def __init__(self, commands):
        """
        commands: словарь вида
            {
                'key': {'command': '/cmd', 'privileges': lvl},
                ...
            }
        """
        self.commands = commands

    def listCommands(self, user_privilege_level):
        """
        Вернуть список команд, доступных для указанного уровня привилегий.
        """
        coms = []
        for key, data in self.commands.items():
            cmd = data['command']
            cmd_priv = data['privileges']
            if user_privilege_level >= cmd_priv:
                coms.append(f"→ {cmd}")
        return "\n".join(coms) if coms else "Нет доступных команд"

    def find_first_command(self, text, user_privilege_level):
        """
        Найти первую команду в тексте, которая доступна для данного уровня привилегий.
        Возвращает кортеж (ключ команды, оставшийся текст) или (None, None), если не найдено.
        """
        positions = []
        for key, data in self.commands.items():
            cmd = data['command']
            cmd_priv = data['privileges']
            if user_privilege_level < cmd_priv:
                continue  # недостаточно прав для этой команды
            idx = text.find(cmd)
            if idx != -1:
                positions.append((idx, key, cmd))
        if not positions:
            return None, None  # ни одна доступная команда не найдена
        first_pos, first_key, first_cmd = min(positions, key=lambda x: x[0])
        rest = text[first_pos + len(first_cmd):].strip()
        return first_key, rest