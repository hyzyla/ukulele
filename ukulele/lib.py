from __future__ import annotations

import ast
import codecs
import encodings
import io
import logging
from dataclasses import dataclass
from typing import Dict, Optional

import toml

utf_8 = encodings.search_function('utf8')


@dataclass
class Config:
    python: Optional[str]
    dependencies: Dict[str, str]

    @staticmethod
    def parse(comment: str) -> Config:
        config = toml.loads(comment)

        return Config(
            python=config.get('python'),
            dependencies=config.get('dependencies', {})
        )


def do_magic(source: str) -> None:

    module = ast.parse(source)
    body = module.body
    if not body:
        print("No body")
        return

    exp = body[0]
    if not isinstance(exp, ast.Expr):
        print("not expiression")
        return

    constant = exp.value
    if not isinstance(constant, ast.Constant):
        print("not constant")
        return

    comment = constant.value
    print(comment)
    if not isinstance(comment, str):
        print("NOT A STRING")
        return

    import toml
    config = toml.loads(comment)
    print(config)


def decode(raw_source, errors: str = 'strict'):

    source, length = utf_8.decode(raw_source, errors=errors)

    try:
        do_magic(source)
    except Exception as exc:
        logging.exception('Exc', exc_info=exc)

    return source, length


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    def _buffer_decode(self, input, errors, final):  # pragma: no cover
        if final:
            return decode(input, errors)
        else:
            return '', 0


class StreamReader(utf_8.streamreader, object):
    """decode is deferred to support better error messages"""
    _stream = None
    _decoded = False

    @property
    def stream(self):
        if not self._decoded:
            text, _ = decode(self._stream.read())
            self._stream = io.BytesIO(text.encode('UTF-8'))
            self._decoded = True
        return self._stream

    @stream.setter
    def stream(self, stream):
        self._stream = stream
        self._decoded = False


fstring_decode = decode

codec_map = {
    'ukulele': codecs.CodecInfo(
        name='ukulele',
        encode=utf_8.encode,
        decode=decode,
        incrementalencoder=utf_8.incrementalencoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=utf_8.streamwriter,
    )
}


def register():
    codecs.register(codec_map.get)
