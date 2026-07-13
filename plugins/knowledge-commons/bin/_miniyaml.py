#!/usr/bin/env python3
"""A vendored YAML subset parser.

The plugin must run on a fresh machine with no dependencies to install. Verified on the
development machine: python3 is 3.9.6 and PyYAML is not installed. So the validator parses
YAML itself, covering exactly what `.commons.yml` and note frontmatter actually use.

The governing discipline is LOUDNESS. Every construct this parser does not support raises
MiniYAMLError with a line number. Nothing is skipped, nothing is guessed, and no partial
document is ever returned. A YAML parser that silently mis-parses is worse than no parser:
it would make the validator confidently wrong, which is the failure class the reference's
own checker demonstrates.

Supported:
    block mappings, nested by indentation
    block sequences, including sequences of block maps and of flow maps
    inline flow maps {a: b} and flow sequences [a, b], nestable
    plain, 'single-quoted', and "double-quoted" scalars (with \\ escapes)
    typed plain scalars: true/false, null/~/empty, int, float; everything else is a string
    comments, quote-aware

Not supported, each raising at its line:
    block scalars (| and >), anchors/aliases (& and *), merge keys (<<:), tags (!!),
    multiple documents, complex keys (?), tab indentation, duplicate keys

Duplicate keys deserve a note. PyYAML silently last-wins on them. A duplicated `required:`
under one type would therefore vanish without a word -- which is exactly the dead-config-key
bug catalogued in the spec's list of the reference's latent defects. Here it is an error.

Note on PyYAML: it is deliberately NOT used at runtime, even when importable. It resolves
`date: 2026-07-08` to a datetime.date and `version: 1.0` to a float, last-wins on duplicate
keys, and carries no line numbers -- so preferring it when present would ship two different
validator behaviors gated on whether a machine happens to have a library, which is the
environment-dependent divergence that "stdlib only" exists to prevent. PyYAML is used in the
test suite as a differential oracle, and nowhere else.
"""

import re

__all__ = ["MiniYAMLError", "Mapping", "load", "load_file", "split_frontmatter"]


class MiniYAMLError(Exception):
    """Malformed or unsupported YAML. Carries the line number and the offending source."""

    def __init__(self, line, reason, source_line=""):
        self.line = line
        self.reason = reason
        self.source_line = source_line
        message = "line %d: %s" % (line, reason)
        if source_line.strip():
            # Every raise site passes this and nothing ever showed it. The offending text is
            # the single most useful thing in the message.
            message += "\n    %s" % source_line.strip()
        super().__init__(message)


class Mapping(dict):
    """A dict that remembers the source line each key was defined on.

    The line numbers are what let a finding say `insights/Foo.md:4: [E] E_GENITOR_UNRESOLVED`
    instead of naming the file and leaving the human to search it. PyYAML cannot produce them.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lines = {}

    def line_of(self, key):
        """Return the 1-based source line where `key` was defined, or None."""
        return self.lines.get(key)


# Constructs that are valid YAML and that this parser refuses rather than mis-parses.
_UNSUPPORTED = [
    (re.compile(r"^\s*[^#\s].*:\s*[|>][-+0-9]*\s*$"),
     "block scalars (| and >) are not supported -- use a quoted scalar"),
    (re.compile(r"^\s*-?\s*&\S"), "anchors (&) are not supported"),
    (re.compile(r"^\s*-?\s*\*\S"), "aliases (*) are not supported"),
    (re.compile(r"^\s*<<\s*:"), "merge keys (<<:) are not supported"),
    (re.compile(r"^\s*!!"), "tags (!!) are not supported"),
    (re.compile(r"^\s*\?\s"), "complex keys (?) are not supported"),
]

_INT_RE = re.compile(r"^[+-]?\d+$")
_FLOAT_RE = re.compile(r"^[+-]?(\d+\.\d*|\.\d+|\d+[eE][+-]?\d+|\d+\.\d*[eE][+-]?\d+)$")


def load_file(path):
    """Parse a YAML file. Raises MiniYAMLError."""
    with open(path, "r", encoding="utf-8") as fh:
        return load(fh.read())


def load(text):
    """Parse a YAML document. Returns a Mapping, list, scalar, or None."""
    tokens = _tokenize(text)
    if not tokens:
        return None
    value, index = _parse_block(tokens, 0, tokens[0][0])
    if index < len(tokens):
        indent, content, lineno = tokens[index]
        raise MiniYAMLError(lineno, "unexpected content at indent %d" % indent, content)
    return value


def split_frontmatter(text):
    """Split `---`-fenced frontmatter from a note body.

    Returns (frontmatter_text_or_None, body_text, body_first_line_number). A note with no
    fence is not an error here -- the validator reports it, because "no frontmatter" is a
    finding about the note, not a parse failure.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text, 1
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:]), i + 2
    raise MiniYAMLError(1, "frontmatter opened with --- but never closed")


def _tokenize(text):
    """Return [(indent, content, lineno)], dropping blanks and comments, keeping line numbers.

    A flow collection may span several source lines -- the spec's own config writes

        evidence:  { name: observation, dir: observations/, map: observations,
                     attractor-field: patterns, min-attractors: 1 }

    so any line that leaves a `{` or `[` open is joined with the lines that follow until the
    collection closes. The token keeps the line number of the line the collection OPENED on,
    which is the one a human would go looking at.
    """
    tokens = []
    pending = None          # (indent, [fragments], lineno) while a flow collection is open
    depth = 0

    for offset, raw in enumerate(text.split("\n")):
        lineno = offset + 1
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise MiniYAMLError(lineno, "tab indentation is not supported -- use spaces", raw)
        stripped = _strip_comment(raw, lineno)
        if not stripped.strip():
            continue

        if pending is None:
            if stripped.strip() in ("---", "..."):
                raise MiniYAMLError(lineno, "multiple documents are not supported", raw)
            for pattern, reason in _UNSUPPORTED:
                if pattern.match(stripped):
                    raise MiniYAMLError(lineno, reason, raw)
            indent = len(stripped) - len(stripped.lstrip())
            depth = _flow_depth(stripped, 0, lineno)
            if depth > 0:
                pending = (indent, [stripped.strip()], lineno)
                continue
            tokens.append((indent, stripped.strip(), lineno))
        else:
            depth = _flow_depth(stripped, depth, lineno)
            pending[1].append(stripped.strip())
            if depth == 0:
                tokens.append((pending[0], " ".join(pending[1]), pending[2]))
                pending = None

    if pending:
        raise MiniYAMLError(
            pending[2], "unterminated flow collection", " ".join(pending[1]))
    return tokens


def _flow_depth(line, depth, lineno):
    """Return the flow-collection nesting depth after `line`, starting from `depth`.

    Brackets inside quoted scalars do not count -- a title like `[[Note]]` in a quoted
    frontmatter value must not be read as opening a flow sequence.
    """
    quote = None
    escaped = False
    for i, ch in enumerate(line):
        if escaped:
            escaped = False
            continue
        if quote == '"' and ch == "\\":
            escaped = True
            continue
        if quote:
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"') and _opens_quote(line, i):
            quote = ch
            continue
        if ch in ("{", "["):
            depth += 1
        elif ch in ("}", "]"):
            depth -= 1
            if depth < 0:
                raise MiniYAMLError(lineno, "unbalanced `%s`" % ch, line)
    return depth


#: A quote character only OPENS a quoted scalar when it sits where a scalar may begin: at the
#: start of the line, or just after `:`, `,`, `-`, `[` or `{`. Anywhere else it is an ordinary
#: character.
#:
#: This matters far more than it looks. Treating every `'` as a quote makes
#:
#:     summary: the orchard's south rows wake first
#:
#: -- ordinary, valid YAML, the kind of sentence that appears in real notes constantly -- a
#: hard parse error. The note is then dropped from every other check, and its attractor emits
#: a spurious drift error for the evidence that "vanished". An apostrophe is not a quote.
_SCALAR_MAY_START_AFTER = (":", ",", "-", "[", "{")


def _opens_quote(text, i):
    """True if the quote character at `text[i]` begins a quoted scalar."""
    for j in range(i - 1, -1, -1):
        if text[j] in (" ", "\t"):
            continue
        return text[j] in _SCALAR_MAY_START_AFTER
    return True   # nothing but whitespace before it: start of the line


def _strip_comment(line, lineno):
    """Remove a trailing `#` comment, respecting quotes. A `#` inside a quoted scalar stays."""
    out = []
    quote = None
    escaped = False
    for i, ch in enumerate(line):
        if escaped:
            out.append(ch)
            escaped = False
            continue
        if quote == '"' and ch == "\\":
            out.append(ch)
            escaped = True
            continue
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"') and _opens_quote(line, i):
            quote = ch
            out.append(ch)
            continue
        if ch == "#" and (i == 0 or line[i - 1] in (" ", "\t")):
            break
        out.append(ch)
    if quote:
        raise MiniYAMLError(lineno, "unterminated %s-quoted scalar" % quote, line)
    return "".join(out).rstrip()


def _parse_block(tokens, index, indent):
    """Parse a block (map or sequence) at `indent`. Returns (value, next_index)."""
    if index >= len(tokens):
        return None, index
    if tokens[index][1].startswith("- "):
        return _parse_sequence(tokens, index, indent)
    if tokens[index][1] == "-":
        return _parse_sequence(tokens, index, indent)
    return _parse_mapping(tokens, index, indent)


def _parse_sequence(tokens, index, indent):
    """Parse a block sequence at `indent`."""
    items = []
    while index < len(tokens):
        item_indent, content, lineno = tokens[index]
        if item_indent < indent:
            break
        if item_indent > indent:
            raise MiniYAMLError(lineno, "unexpected indent in sequence", content)
        if not (content == "-" or content.startswith("- ")):
            break
        rest = content[1:].strip()
        index += 1
        if not rest:
            # `-` alone: the item is the nested block beneath it.
            if index < len(tokens) and tokens[index][0] > indent:
                value, index = _parse_block(tokens, index, tokens[index][0])
                items.append(value)
            else:
                items.append(None)
            continue
        if rest.startswith("{") or rest.startswith("["):
            items.append(_parse_flow(rest, lineno))
            continue
        if _looks_like_key(rest):
            # A sequence of block maps: `- name: firm`, with the rest of the mapping indented
            # beneath it.
            #
            # The first key sits at the column the `-` marker pushed it to, so compute that
            # column rather than assuming "- " is always exactly two characters. Every
            # following token keeps its OWN indent, which is what lets a nested block under
            # one of these keys still parse as a nested block:
            #
            #     - type: chronicle        <- inner_indent
            #       defaults:              <- inner_indent (a sibling key)
            #         project: devbox      <- deeper: a CHILD of `defaults`
            #
            # Forcing every continuation token to inner_indent (which this did) collapses the
            # last two lines to the same level, so `defaults` silently becomes None and its
            # children leak upward as siblings -- a wrong value returned without a word, which
            # is the one thing this parser exists to make impossible.
            after_dash = content[1:]
            inner_indent = indent + 1 + (len(after_dash) - len(after_dash.lstrip()))
            synthetic = [(inner_indent, rest, lineno)]
            while index < len(tokens) and tokens[index][0] > indent:
                if tokens[index][1].startswith("- ") or tokens[index][1] == "-":
                    break
                if tokens[index][0] < inner_indent:
                    raise MiniYAMLError(
                        tokens[index][2],
                        "indent %d is less than the sequence item's first key at column %d"
                        % (tokens[index][0], inner_indent), tokens[index][1])
                synthetic.append(tokens[index])
                index += 1
            value, consumed = _parse_mapping(synthetic, 0, inner_indent)
            if consumed != len(synthetic):
                raise MiniYAMLError(lineno, "could not parse sequence item", rest)
            items.append(value)
            continue
        items.append(_parse_scalar(rest, lineno))
    return items, index


def _parse_mapping(tokens, index, indent):
    """Parse a block mapping at `indent`."""
    mapping = Mapping()
    while index < len(tokens):
        key_indent, content, lineno = tokens[index]
        if key_indent < indent:
            break
        if key_indent > indent:
            raise MiniYAMLError(lineno, "unexpected indent in mapping", content)
        if content.startswith("- ") or content == "-":
            break
        key, raw_value = _split_key(content, lineno)
        if key in mapping:
            raise MiniYAMLError(
                lineno,
                "duplicate key %r -- a silently discarded key is a dead config entry" % key,
                content)
        index += 1
        if raw_value:
            mapping[key] = _parse_value(raw_value, lineno)
        elif index < len(tokens) and tokens[index][0] > key_indent:
            mapping[key], index = _parse_block(tokens, index, tokens[index][0])
        elif (index < len(tokens) and tokens[index][0] == key_indent
              and (tokens[index][1].startswith("- ") or tokens[index][1] == "-")):
            # A sequence written flush with its key, which YAML permits.
            mapping[key], index = _parse_sequence(tokens, index, key_indent)
        else:
            mapping[key] = None
        mapping.lines[key] = lineno
    return mapping, index


def _looks_like_key(text):
    """True if `text` opens a mapping (`key: ...`) rather than being a bare scalar."""
    try:
        _split_key(text, 0)
        return True
    except MiniYAMLError:
        return False


def _split_key(content, lineno):
    """Split `key: value` at the first colon outside quotes. Returns (key, raw_value)."""
    quote = None
    escaped = False
    for i, ch in enumerate(content):
        if escaped:
            escaped = False
            continue
        if quote == '"' and ch == "\\":
            escaped = True
            continue
        if quote:
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"') and _opens_quote(content, i):
            quote = ch
            continue
        if ch == ":" and (i + 1 == len(content) or content[i + 1] in (" ", "\t")):
            key = content[:i].strip()
            if not key:
                raise MiniYAMLError(lineno, "empty key", content)
            return _unquote(key, lineno), content[i + 1:].strip()
    raise MiniYAMLError(lineno, "expected `key: value`", content)


def _parse_value(raw, lineno):
    """Parse the right-hand side of a mapping entry."""
    if raw.startswith("{") or raw.startswith("["):
        return _parse_flow(raw, lineno)
    return _parse_scalar(raw, lineno)


def _parse_flow(text, lineno):
    """Parse an inline flow map or sequence. Nestable."""
    value, consumed = _scan_flow(text, 0, lineno)
    if text[consumed:].strip():
        raise MiniYAMLError(lineno, "trailing content after flow collection", text)
    return value


def _scan_flow(text, i, lineno):
    """Scan one flow collection or scalar starting at `i`. Returns (value, next_index)."""
    i = _skip_space(text, i)
    if i >= len(text):
        raise MiniYAMLError(lineno, "unexpected end of flow collection", text)
    if text[i] == "{":
        return _scan_flow_map(text, i, lineno)
    if text[i] == "[":
        return _scan_flow_seq(text, i, lineno)
    return _scan_flow_scalar(text, i, lineno)


def _scan_flow_map(text, i, lineno):
    """Scan `{a: b, c: [d]}` starting at the brace."""
    mapping = Mapping()
    i += 1
    while True:
        i = _skip_space(text, i)
        if i >= len(text):
            raise MiniYAMLError(lineno, "unterminated flow map", text)
        if text[i] == "}":
            return mapping, i + 1
        key, i = _scan_flow_scalar(text, i, lineno, stop=":")
        i = _skip_space(text, i)
        if i >= len(text) or text[i] != ":":
            raise MiniYAMLError(lineno, "expected `:` in flow map", text)
        value, i = _scan_flow(text, i + 1, lineno)
        if key in mapping:
            raise MiniYAMLError(lineno, "duplicate key %r in flow map" % key, text)
        mapping[key] = value
        mapping.lines[key] = lineno
        i = _skip_space(text, i)
        if i < len(text) and text[i] == ",":
            i += 1
            continue
        if i < len(text) and text[i] == "}":
            return mapping, i + 1
        raise MiniYAMLError(lineno, "expected `,` or `}` in flow map", text)


def _scan_flow_seq(text, i, lineno):
    """Scan `[a, b, c]` starting at the bracket."""
    items = []
    i += 1
    while True:
        i = _skip_space(text, i)
        if i >= len(text):
            raise MiniYAMLError(lineno, "unterminated flow sequence", text)
        if text[i] == "]":
            return items, i + 1
        value, i = _scan_flow(text, i, lineno)
        items.append(value)
        i = _skip_space(text, i)
        if i < len(text) and text[i] == ",":
            i += 1
            continue
        if i < len(text) and text[i] == "]":
            return items, i + 1
        raise MiniYAMLError(lineno, "expected `,` or `]` in flow sequence", text)


def _scan_flow_scalar(text, i, lineno, stop=""):
    """Scan a scalar inside a flow collection, stopping at a structural character."""
    if text[i] in ("'", '"'):
        raw, i = _scan_quoted(text, i, lineno)
        return _unquote(raw, lineno), i
    start = i
    while i < len(text) and text[i] not in (",", "}", "]") and text[i] not in stop:
        i += 1
    literal = text[start:i].strip()
    if not literal:
        raise MiniYAMLError(lineno, "empty scalar in flow collection", text)
    return _parse_scalar(literal, lineno), i


def _scan_quoted(text, i, lineno):
    """Scan a quoted scalar starting at its opening quote. Returns (raw_with_quotes, next)."""
    quote = text[i]
    start = i
    i += 1
    while i < len(text):
        if quote == '"' and text[i] == "\\":
            i += 2
            continue
        if text[i] == quote:
            if quote == "'" and i + 1 < len(text) and text[i + 1] == "'":
                i += 2
                continue
            return text[start:i + 1], i + 1
        i += 1
    raise MiniYAMLError(lineno, "unterminated %s-quoted scalar" % quote, text)


def _skip_space(text, i):
    """Advance past whitespace."""
    while i < len(text) and text[i] in (" ", "\t"):
        i += 1
    return i


def _parse_scalar(literal, lineno):
    """Type a scalar. Quoted scalars are always strings; plain ones are resolved.

    An anchor or alias in VALUE position (`a: &x 1`, `b: *x`) is caught here rather than by
    the line-start patterns, which only see it in key position. Left alone it would parse as
    the plain string "&x 1" -- a silent wrong value, which is the one outcome this parser
    exists to make impossible.
    """
    if not literal:
        return None
    if literal[0] == "&":
        raise MiniYAMLError(lineno, "anchors (&) are not supported", literal)
    if literal[0] == "*":
        raise MiniYAMLError(lineno, "aliases (*) are not supported", literal)
    if literal[0] == "!":
        raise MiniYAMLError(lineno, "tags (!) are not supported", literal)
    if literal[0] in ("'", '"'):
        raw, consumed = _scan_quoted(literal, 0, lineno)
        if literal[consumed:].strip():
            raise MiniYAMLError(lineno, "trailing content after quoted scalar", literal)
        return _unquote(raw, lineno)
    lowered = literal.lower()
    if lowered in ("null", "~"):
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if _INT_RE.match(literal):
        return int(literal)
    if _FLOAT_RE.match(literal):
        return float(literal)
    return literal


def _unquote(literal, lineno):
    """Strip quotes and apply escapes. A plain scalar is returned as-is."""
    if len(literal) >= 2 and literal[0] == literal[-1] == "'":
        return literal[1:-1].replace("''", "'")
    if len(literal) >= 2 and literal[0] == literal[-1] == '"':
        return _unescape(literal[1:-1], lineno)
    return literal


def _unescape(body, lineno):
    """Apply double-quote escapes.

    Load-bearing for `event-delimiter: "^## \\d{2}:\\d{2}"`. Getting this wrong yields a
    regex that silently matches nothing, so /process queues no events, forever, in silence.
    """
    out = []
    i = 0
    simple = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "/": "/", "0": "\0"}
    while i < len(body):
        ch = body[i]
        if ch != "\\":
            out.append(ch)
            i += 1
            continue
        if i + 1 >= len(body):
            raise MiniYAMLError(lineno, "trailing backslash in double-quoted scalar", body)
        nxt = body[i + 1]
        if nxt in simple:
            out.append(simple[nxt])
            i += 2
            continue
        raise MiniYAMLError(lineno, "unsupported escape \\%s" % nxt, body)
    return "".join(out)
