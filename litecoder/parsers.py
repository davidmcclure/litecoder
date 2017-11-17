

import attr
import re

from boltons.iterutils import windowed

from .utils import isplit


@attr.s(repr=False)
class Token:

    token = attr.ib()
    index = attr.ib()

    def __repr__(self):
        return f'{self.token}_{self.index}'


class TokenList:

    @classmethod
    def from_text(cls, text):
        """Remove periods, tokenize.
        """
        tokens = []
        text = text.replace('.', '')

        i = 0
        for token in re.findall('[a-z-]+|,', text, re.I):
            tokens.append(Token(token, i))
            if token != ',': i += 1

        return cls(tokens)

    def __init__(self, tokens):
        self.tokens = tokens

    def __repr__(self):
        return f'{self.__class__.__name__}({self.tokens})'

    def text(self):
        """Get combined text string.
        """
        token_strs = [t.token for t in self.tokens]
        return ' '.join(token_strs)

    def key(self):
        """Make index key from tokens.
        """
        return self.text().lower()


class LocationField(TokenList):

    def candidate_toponyms(self, maxn=4):
        """Generate candidate toponym ngrams.
        """
        # Split on commas.
        for comma_part in isplit(self.tokens, lambda t: t.token == ','):

            # Slide window across tokens.
            for n in range(1, maxn+1):
                for w in windowed(comma_part, n):
                    yield TokenList(w)
