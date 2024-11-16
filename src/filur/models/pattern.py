class Pattern:
    def __init__(self, pattern: str, type: str = 'string', weight: int = 1, operator: str = 'OR'):
        self.pattern = pattern
        self.type = type
        self.weight = weight
        self.operator = operator

    def to_dict(self):
        return {
            'pattern': self.pattern,
            'type': self.type,
            'weight': self.weight,
            'operator': self.operator
        }

    def __repr__(self):
        return f"Pattern(pattern={self.pattern}, type={self.type}, weight={self.weight}, operator={self.operator})"
