import re
import random
from typing import List, Dict
from glob import glob

from validators import ReactionSchema


class Reactions:
    def __init__(self):
        self._reactions = self.load_reactions()

    @staticmethod
    def load_reactions() -> List[Dict]:
        """
        Загружает реакции из файлов по пути reactions/ с именем *.json

        Бэкслэши в файлах должны быть экранированы (напр., \b -> \\b)

        Структура файла описана в классе ReactionsSchema в validators.py
        """
        reactions_files = glob(r'reactions/*.json')
        schema = ReactionSchema(many=True)
        # reactions: List[Dict] = []
        reactions = []
        for file in reactions_files:
            with open(file, encoding='utf-8') as f:
                validated_data = schema.loads(f.read())
                if validated_data.errors:
                    print("{0} error file".format(f.name))
                          validated_data.errors)
                reactions += validated_data.data
        return reactions

    def message_handler(self, message) -> None:
        # Каждый раз перемешиваем список реакций, затем
        # отправляем первое попавшееся совпадение
        random.shuffle(self._reactions)
        for reaction in self._reactions:
            chance: int = reaction['chance']
            if random.uniform(0, 100) > chance:
                continue

            if reaction['triggers']:
                for trigger in reaction['triggers']:
                    if re.search(trigger, message, re.IGNORECASE):
                        return random.choice(reaction['reactions'])
            else:
                return random.choice(reaction['reactions'])
