#!/usr/bin/env python3
"""Prove the vendored YAML parser handles what the config uses, and REFUSES what it does not.

The refusal half matters more than the support half. A parser that silently mis-parses makes
the validator confidently wrong, and a confidently-wrong validator is worse than no validator
at all -- it reports a clean graph while the invariant it was built to enforce quietly rots.
"""

import glob
import os
import unittest

from support import _miniyaml as m, FIXTURES

try:
    import yaml
    HAVE_PYYAML = True
except ImportError:
    HAVE_PYYAML = False


class Subset(unittest.TestCase):
    """Everything `.commons.yml` and note frontmatter actually use."""

    def test_block_map_nested(self):
        d = m.load("graph:\n  name: orchard\n  growth:\n    new-map-at: 5\n")
        self.assertEqual(5, d["graph"]["growth"]["new-map-at"])

    def test_flow_map_and_list(self):
        d = m.load("growth: { new-map-at: 5, tags: [a, b] }\n")
        self.assertEqual({"new-map-at": 5, "tags": ["a", "b"]}, d["growth"])

    def test_flow_map_spanning_lines(self):
        """The spec's own config writes flow maps across two lines. It must parse."""
        d = m.load("evidence:  { name: observation, dir: observations/,\n"
                   "             attractor-field: supports, min-attractors: 1 }\n")
        self.assertEqual("observation", d["evidence"]["name"])
        self.assertEqual(1, d["evidence"]["min-attractors"])

    def test_sequence_of_flow_maps(self):
        d = m.load("attractors:\n  - { name: pattern, dir: patterns/ }\n"
                   "  - { name: practice, dir: practices/ }\n")
        self.assertEqual(["pattern", "practice"], [a["name"] for a in d["attractors"]])

    def test_sequence_of_block_maps(self):
        d = m.load("sources:\n  - type: chronicle\n    ledger: source-note\n"
                   "  - type: email\n    ledger: none\n")
        self.assertEqual(["chronicle", "email"], [s["type"] for s in d["sources"]])

    def test_nested_block_map_inside_a_sequence_item(self):
        """Regression. This used to be flattened, SILENTLY.

        Every continuation token was rewritten to one synthetic indent, which collapsed a
        nested block to its parent's level: `defaults` came back as None and `project` and
        `labels` leaked upward as siblings of `type`. No error -- a wrong value returned
        without a word, which is the single thing this parser exists to make impossible.
        """
        d = m.load("sources:\n"
                   "  - type: chronicle\n"
                   "    ledger: source-note\n"
                   "    defaults:\n"
                   "      project: devbox\n"
                   "      labels: [next]\n"
                   "  - type: email\n"
                   "    ledger: none\n")
        self.assertEqual(
            {"type": "chronicle", "ledger": "source-note",
             "defaults": {"project": "devbox", "labels": ["next"]}},
            d["sources"][0])
        self.assertEqual({"type": "email", "ledger": "none"}, d["sources"][1])

    def test_deeply_nested_block_map_inside_a_sequence_item(self):
        d = m.load("outputs:\n  - name: a\n    deep:\n      one:\n        two: 3\n")
        self.assertEqual({"name": "a", "deep": {"one": {"two": 3}}}, d["outputs"][0])

    def test_sequence_of_scalars(self):
        d = m.load('supports:\n  - "[[A]]"\n  - "[[B]]"\n')
        self.assertEqual(["[[A]]", "[[B]]"], d["supports"])

    def test_null_and_bool_and_int(self):
        d = m.load("a: null\nb: ~\nc: true\nd: false\ne: 42\nf:\n")
        self.assertEqual([None, None, True, False, 42, None],
                         [d["a"], d["b"], d["c"], d["d"], d["e"], d["f"]])

    def test_a_date_stays_a_string(self):
        """PyYAML would hand back a datetime.date here. The validator wants the literal."""
        d = m.load("date: 2026-07-08\n")
        self.assertEqual("2026-07-08", d["date"])
        self.assertIsInstance(d["date"], str)

    def test_quote_aware_comment_stripping(self):
        d = m.load("a: 1  # trailing\nb: 'has # inside'\n")
        self.assertEqual({"a": 1, "b": "has # inside"}, dict(d))

    def test_escaped_regex_round_trips(self):
        r"""`event-delimiter: "^## \d{2}:\d{2}"` -- get this wrong and /process silently
        queues nothing, forever, with no message."""
        import re
        d = m.load('event-delimiter: "^## \\\\d{2}:\\\\d{2}"\n')
        self.assertEqual(r"^## \d{2}:\d{2}", d["event-delimiter"])
        self.assertTrue(re.compile(d["event-delimiter"]).match("## 14:01 Converged"))

    def test_a_colon_inside_a_quoted_value_survives(self):
        d = m.load('source: "docs/chronicle/2026-07-12.md### 14:01 Converged"\n')
        self.assertEqual("docs/chronicle/2026-07-12.md### 14:01 Converged", d["source"])

    def test_brackets_inside_quotes_do_not_open_a_flow_sequence(self):
        d = m.load('genitor: "[[maps/observations]]"\n')
        self.assertEqual("[[maps/observations]]", d["genitor"])

    def test_line_numbers_are_recorded(self):
        d = m.load("a: 1\nb: 2\nc: 3\n")
        self.assertEqual([1, 2, 3], [d.line_of("a"), d.line_of("b"), d.line_of("c")])

    def test_split_frontmatter(self):
        fm, body, first = m.split_frontmatter("---\ntype: x\n---\nBody here.\n")
        self.assertEqual("type: x", fm)
        self.assertEqual("Body here.\n", body)
        self.assertEqual(4, first)


class Refusals(unittest.TestCase):
    """Every unsupported construct raises with a line number. Nothing is skipped or guessed."""

    CASES = [
        ("block scalar", "desc: |\n  hello\n"),
        ("folded scalar", "desc: >\n  hello\n"),
        ("anchor in key position", "- &x\n  a: 1\n"),
        ("anchor in value position", "a: &x 1\n"),
        ("alias in value position", "b: *x\n"),
        ("alias inside a flow list", "a: [*x]\n"),
        ("merge key", "<<: *base\n"),
        ("tag", "a: !!python/object\n"),
        ("tab indentation", "a:\n\tb: 1\n"),
        ("duplicate key", "required: [a]\nrequired: [b]\n"),
        ("multiple documents", "a: 1\n---\nb: 2\n"),
        ("unterminated flow map", "a: { b: 1\n"),
        ("unterminated quote", 'a: "oops\n'),
        ("unsupported escape", 'a: "\\q"\n'),
        ("no colon", "just a bare line\n"),
        ("unbalanced bracket", "a: 1]\n"),
    ]

    def test_each_unsupported_construct_raises(self):
        for label, text in self.CASES:
            with self.subTest(construct=label):
                with self.assertRaises(m.MiniYAMLError, msg="%s did not raise" % label) as ctx:
                    m.load(text)
                self.assertGreaterEqual(ctx.exception.line, 1,
                                        "%s raised without a line number" % label)

    def test_a_duplicate_key_is_not_silently_last_wins(self):
        """PyYAML last-wins here. A silently discarded key is a dead config entry -- which is
        a real bug in the reference: a required-fields block keyed on a tag the notes never
        carry, so the branch never fires and nothing ever says so."""
        with self.assertRaises(m.MiniYAMLError):
            m.load("schema:\n  required: [a]\n  required: [b]\n")

    def test_values_containing_special_characters_still_parse(self):
        d = m.load("a: \"a & b\"\nb: 3 * 4\nc: not!bang\n")
        self.assertEqual({"a": "a & b", "b": "3 * 4", "c": "not!bang"}, dict(d))


class DifferentialOracle(unittest.TestCase):
    """PyYAML is a TEST oracle and never a runtime dependency.

    The spec says "prefer PyYAML when importable". Followed literally that ships two different
    production behaviors -- PyYAML resolves `date:` to a datetime and last-wins on duplicate
    keys -- gated on whether a machine happens to have a library installed. That is exactly the
    environment-dependent divergence "stdlib only" exists to prevent, and it would appear in
    one population of users and never in CI. So the vendored parser is the only production
    path, and PyYAML's job is to keep it honest here.
    """

    @unittest.skipUnless(HAVE_PYYAML, "PyYAML not installed (which is the normal case here)")
    def test_agrees_with_pyyaml_on_every_fixture_config(self):
        configs = glob.glob(os.path.join(FIXTURES, "*", ".commons.yml"))
        self.assertTrue(configs, "no fixture configs found")
        for path in configs:
            with self.subTest(config=os.path.basename(os.path.dirname(path))):
                with open(path, "r", encoding="utf-8") as fh:
                    text = fh.read()
                self.assertEqual(_normalize(yaml.safe_load(text)),
                                 _normalize(m.load(text)))


def _normalize(value):
    """Erase the differences that are PyYAML's implicit resolver, not real disagreements."""
    import datetime
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    return value


if __name__ == "__main__":
    unittest.main()
