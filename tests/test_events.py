import codecs

import pytest

from ircproto.events import decode_event, IRCEvent
from ircproto.exceptions import ProtocolError, UnknownCommand


def test_decode_event_oversized():
    buffer = bytearray(b':foo!bar@blah PRIVMSG hey' + b'y' * 600 + b'\r\n')
    exc = pytest.raises(ProtocolError, decode_event, buffer)
    assert str(exc.value) == 'IRC protocol violation: received oversized message (627 bytes)'


def test_decode_event_unknown_command():
    buffer = bytearray(b':foo!bar@blah FROBNICATE\r\n')
    exc = pytest.raises(UnknownCommand, decode_event, buffer)
    assert str(exc.value) == 'IRC protocol violation: unknown command: FROBNICATE'


def test_decode_fallback_conversion():
    decoder = codecs.getdecoder('utf-8')
    fallback_decoder = codecs.getdecoder('iso-8859-1')
    buffer = bytearray(b':foo!bar@blah PRIVMSG hey du\xe2\xa9k\r\n')
    assert decode_event(buffer, decoder=decoder, fallback_decoder=fallback_decoder)


def test_encode_event():
    ev = IRCEvent(sender=None)

    encoded_word = ev.encode('PRIVMSG', 'hey', 'you')
    assert encoded_word == 'PRIVMSG hey you\r\n'

    encoded_colonword = ev.encode('PRIVMSG', 'hey', ':-)')
    assert encoded_colonword == 'PRIVMSG hey ::-)\r\n'

    encoded_sentence = ev.encode('PRIVMSG', 'hey', 'some text')
    assert encoded_sentence == 'PRIVMSG hey :some text\r\n'

    encoded_colonsentence = ev.encode('PRIVMSG', 'hey', ':+1: lgtm')
    assert encoded_colonsentence == 'PRIVMSG hey ::+1: lgtm\r\n'

    exc = pytest.raises(ProtocolError, ev.encode, 'PRIVMSG', 'hey you', 'sup')
    assert str(exc.value) == 'IRC protocol violation: only the last parameter can contain spaces'

    encoded_empty = ev.encode('PRIVMSG', 'hey', '')
    assert encoded_empty == 'PRIVMSG hey\r\n'
