"""Morse lookup and timing-to-text decoding."""
MORSE_TO_TEXT = {
    ".-":"A", "-...":"B", "-.-.":"C", "-..":"D", ".":"E", "..-.":"F",
    "--.":"G", "....":"H", "..":"I", ".---":"J", "-.-":"K", ".-..":"L",
    "--":"M", "-.":"N", "---":"O", ".--.":"P", "--.-":"Q", ".-.":"R",
    "...":"S", "-":"T", "..-":"U", "...-":"V", ".--":"W", "-..-":"X",
    "-.--":"Y", "--..":"Z",
    "-----":"0", ".----":"1", "..---":"2", "...--":"3", "....-":"4",
    ".....":"5", "-....":"6", "--...":"7", "---..":"8", "----.":"9",
    ".-.-.-":".", "--..--":",", "..--..":"?", "-.-.--":"!", "-..-.":"/"
}

class MorseDecoder:
    def __init__(self, letter_gap=1.15, word_gap=2.5):
        self.letter_gap = letter_gap
        self.word_gap = word_gap
        self.pattern = ""
        self.text = ""
        self.last_symbol_at = None

    def add_symbol(self, symbol, timestamp):
        self.pattern += symbol
        self.last_symbol_at = timestamp

    def update(self, timestamp):
        """Flush a pending pattern when its inter-blink pause is long enough."""
        if not self.pattern or self.last_symbol_at is None:
            return None
        elapsed = timestamp - self.last_symbol_at
        if elapsed >= self.word_gap:
            letter = self._flush_pattern()
            if self.text and not self.text.endswith(" "):
                self.text += " "
            return letter
        if elapsed >= self.letter_gap:
            return self._flush_pattern()
        return None

    def _flush_pattern(self):
        if not self.pattern:
            return None
        decoded = MORSE_TO_TEXT.get(self.pattern, "?")
        self.text += decoded
        self.pattern = ""
        self.last_symbol_at = None
        return decoded

    def flush(self):
        return self._flush_pattern()

    def reset(self):
        self.pattern = ""
        self.text = ""
        self.last_symbol_at = None
