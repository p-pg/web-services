from uuid import uuid4
from pathlib import Path


def generate_name(prefix, filename: str):
    return f'{prefix}{uuid4()}{Path(filename).suffix}'


def code_submission_file_name(instance, filename: str):
    return generate_name('upload-required-documents/', filename)


__all__ = ('generate_name', 'code_submission_file_name')
