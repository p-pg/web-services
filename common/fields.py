from django.db import models


class IMixin:
    def to_python(self, value: str | None):
        if result := super().to_python(value):
            return result.lower()


class ICharField(IMixin, models.CharField):
    pass


class IEmailField(IMixin, models.EmailField):
    pass


__all__ = ('ICharField', 'IEmailField')
