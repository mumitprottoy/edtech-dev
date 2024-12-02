
from secrets import choice as c
from datetime import datetime as dt
from .constants import DATETIME_FORMAT_FOR_KEYS


class KeyGen:
    
    def random_az(self) -> str:
        return chr(c([x for x in range(65,123) if x not in range(91,97)]))
        
    def random_digit(self) -> int: 
        return c(range(10))
        
    def num_key(self, length:int=6) -> str:
        return ''.join(str(self.random_digit()) for i in range(length))

    def datetime_key(self) -> str:
        return dt.today().strftime(DATETIME_FORMAT_FOR_KEYS)

    def key(self) -> str:
        key = self.alpha_key(2).upper()
        key += self.alphanumeric_key(5).upper()
        key += self.datetime_key()
        return key

    def transaction_id(self) -> str:
        key = 'E4E' + self.datetime_key()
        key += self.alphanumeric_key(4).upper()        
        return key
    
    def alpha_key(self, length:int=69) -> str:
        return ''.join([self.random_az() for i in range(length)])

    def alphanumeric_key(self, length:int=69) -> str:
        return ''.join([
        str(c([self.random_az, self.random_digit])()) 
        for i in range(length)
        ])

    def unique_name(self):
        return self.alphanumeric_key(5) + self.datetime_key()