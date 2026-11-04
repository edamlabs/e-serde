"""NativeYamlCodec coverage — saphyr (YAML 1.2 core schema) + native emitter."""

from __future__ import annotations

import pytest

from eserde.backends.native.yaml import NativeYamlCodec
from eserde.infra.errors import LoadError
from eserde.infra.formats import Format


@pytest.fixture
def codec() -> NativeYamlCodec:
    return NativeYamlCodec()


async def test_codec_format_is_yaml() -> None:
    assert NativeYamlCodec.format is Format.YAML


async def test_roundtrip_nested(codec: NativeYamlCodec, nested_payload: dict[str, object]) -> None:
    assert codec.loads(codec.dumps(nested_payload)) == nested_payload


async def test_loads_core_schema_types(codec: NativeYamlCodec) -> None:
    data = b"a: 1\nb: 2.5\nc: true\nd: null\ne: yes\nf: 2026-01-01\n"
    assert codec.loads(data) == {"a": 1, "b": 2.5, "c": True, "d": None, "e": "yes", "f": "2026-01-01"}


async def test_loads_explicit_tag(codec: NativeYamlCodec) -> None:
    assert codec.loads(b"a: !!str 42\n") == {"a": "42"}


async def test_loads_tagged_collection_expands_inner(codec: NativeYamlCodec) -> None:
    assert codec.loads(b"a: !custom [1, 2]\n") == {"a": [1, 2]}


async def test_loads_unicode(codec: NativeYamlCodec) -> None:
    assert codec.loads("city: Málaga\n".encode()) == {"city": "Málaga"}


async def test_dumps_quotes_ambiguity(codec: NativeYamlCodec) -> None:
    assert codec.dumps({"a": "true", "b": "123", "c": "# hash"}) == b'a: "true"\nb: "123"\nc: "# hash"\n'


async def test_dumps_quotes_yaml11_retyped_strings(codec: NativeYamlCodec) -> None:
    payload = {"date": "2024-01-15", "yn": "yes", "switch": "off", "hex": "0x1F", "inf": ".inf"}
    assert codec.dumps(payload) == b'date: "2024-01-15"\nyn: "yes"\nswitch: "off"\nhex: "0x1F"\n"inf": ".inf"\n'


async def test_dumps_empty_collections(codec: NativeYamlCodec) -> None:
    assert codec.loads(codec.dumps({"a": {}, "b": []})) == {"a": {}, "b": []}


async def test_dumps_sequence_of_mappings(codec: NativeYamlCodec) -> None:
    payload = {"rows": [{"i": 1, "name": "a"}, {"i": 2, "name": "b"}]}
    assert codec.loads(codec.dumps(payload)) == payload


async def test_dumps_sequence_of_mappings_alignment(codec: NativeYamlCodec) -> None:
    payload = {"rows": [{"i": 1, "name": "a"}, {"i": 2, "name": "b"}]}
    assert codec.dumps(payload) == b"rows:\n- i: 1\n  name: a\n- i: 2\n  name: b\n"


@pytest.mark.parametrize(
    "payload",
    [
        {"n": [["a", "b"], ["c", "d"]]},
        [[1, 2], [3]],
        {"deep": [[[1, 2], [3]], [4]]},
        {"rows": [[{"i": 1, "name": "a"}, {"i": 2}], []]},
    ],
    ids=["pairs", "top-level", "deep", "mappings-inside"],
)
async def test_roundtrip_nested_sequences(codec: NativeYamlCodec, payload: object) -> None:
    assert codec.loads(codec.dumps(payload)) == payload


async def test_dumps_nested_sequence_alignment(codec: NativeYamlCodec) -> None:
    """Every dash of one sequence in one column: the first item follows its parent's dash on the same line."""
    assert codec.dumps({"rows": [["a", "b"], ["c"]]}) == b"rows:\n- - a\n  - b\n- - c\n"


async def test_dumps_escapes_ansi_log(codec: NativeYamlCodec) -> None:
    line = "\x1b[31mERROR\x1b[0m: boom"
    assert codec.dumps({"log": line}) == b'log: "\\e[31mERROR\\e[0m: boom"\n'


@pytest.mark.parametrize(
    "text",
    [
        "".join(map(chr, range(0x100))),
        "\u2028\u2029\ufeff\ufffe\uffff",
        "e\u0301: \U0001f600",
        "a\x00b",
    ],
)
async def test_roundtrip_non_printable(codec: NativeYamlCodec, text: str) -> None:
    payload = {text: text}
    assert codec.loads(codec.dumps(payload)) == payload


async def test_loads_multi_document_raises(codec: NativeYamlCodec) -> None:
    with pytest.raises(LoadError, match="exactly one"):
        codec.loads(b"a: 1\n---\nb: 2\n")


async def test_loads_invalid_raises(codec: NativeYamlCodec) -> None:
    with pytest.raises(LoadError):
        codec.loads(b"{ invalid: yaml: :: ")


async def test_loads_non_utf8_raises(codec: NativeYamlCodec) -> None:
    with pytest.raises(LoadError):
        codec.loads(b"\xff\xfe broken")
