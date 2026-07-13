#!/usr/bin/env python3
"""Validate a knowledge commons graph.

THE validator. One implementation, several entrypoints -- so the write-time gate and the
health check can never disagree about what the rules are.

    validate.py check    --graph ROOT [--scope REL ...] [--baseline FILE] [--format json]
    validate.py baseline --graph ROOT --out FILE
    validate.py schema   --graph ROOT
    validate.py index    --graph ROOT [--write]

Two facts govern the whole design.

FIRST: scoping narrows REPORTING, never ANALYSIS. Every run parses every note under the
graph root and builds the complete file, alias, link and map indexes. This is not a
concession to convenience -- it is the only sound option, because every invariant that
matters is cross-file (does the parent map list this note? is the bidirectional pair
consistent in BOTH directions? does this wikilink resolve, following aliases?). A subgraph
cannot answer any of them. It is also cheap: a 676-note graph is one walk and 676 small
reads. What `--scope` filters is the finding list, via each finding's FIX SET -- the files
whose content would have to change to fix it, which is not the same as the file the problem
was discovered in. A note absent from its map is a finding about BOTH the note and the map.

SECOND: "new" is defined against a baseline, by fingerprint. A real graph has pre-existing
findings, and a write must not be refused for a violation it did not cause. The fingerprint
deliberately excludes line numbers and message prose: a line-sensitive identity would make
every pre-existing finding in an edited file look brand new, and the transaction would
refuse every write into an already-imperfect graph -- which is the normal case.

Severity policy (spec): a dangling reference is an ERROR; an incomplete or untidy index is a
WARNING; a schema violation is an ERROR -- a health check that merely warns about what the
writer refuses would be incoherent. Exit non-zero iff an error.

Stdlib only. Python 3.9 floor.
"""

import argparse
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _miniyaml as miniyaml  # noqa: E402

CONFIG_NAME = ".commons.yml"

EXIT_OK = 0
EXIT_USAGE = 1        # the validator could not run. Never mistake this for "clean".
EXIT_ERRORS = 2
EXIT_NEW_ERRORS = 3   # only reachable with --baseline

WIKILINK_RE = re.compile(r"\[\[([^\]\|#\^]+)(?:[#\^][^\]\|]*)?(?:\|([^\]]*))?\]\]")
BULLET_RE = re.compile(r"^\s*[-*+]\s+(.*)$")
HEADING_RE = re.compile(r"^(#+)\s+(.*?)\s*$")

# Config keys we know about. Anything else earns KC109, the typo detector -- which is how a
# dead config key (a real bug in the reference: a required-fields entry keyed on a tag the
# notes never carry, so the branch never fired) surfaces instead of silently never firing.
KNOWN_GRAPH_KEYS = {
    "root", "name", "atlas", "maps-dir", "parent-field", "growth", "promotes-to",
    "ordering-exempt", "expected-orphans",
}
KNOWN_TOP_KEYS = {"graph", "types", "schema", "sources", "outputs", "boundary",
                  "graduation", "feeders"}


class Finding:
    """One validation finding.

    `paths` is the FIX SET -- every graph-relative file whose content would have to change to
    resolve this. It is not the discovery site. A half-written bidirectional pair names both
    the hub and the attractor, because either one could be the file that is wrong, and
    because a transaction that touched only one of them must still see it.
    """

    def __init__(self, check, severity, paths, message, line=None, key="", hint=""):
        self.check = check
        self.severity = severity
        self.paths = sorted(set(paths))
        self.message = message
        self.line = line
        self.key = key
        self.hint = hint
        self.new = None

    def fingerprint(self):
        """Stable identity across unrelated edits. Excludes line numbers and prose."""
        raw = "|".join([self.check, ",".join(self.paths), self.key])
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]

    def locus(self):
        """The file to name first when reporting."""
        return self.paths[0] if self.paths else CONFIG_NAME

    def to_dict(self):
        """Serialize for --format json."""
        return {
            "check": self.check,
            "severity": self.severity,
            "fingerprint": self.fingerprint(),
            "paths": self.paths,
            "line": self.line,
            "key": self.key,
            "message": self.message,
            "hint": self.hint,
            "new": self.new,
        }


class Note:
    """A parsed note."""

    def __init__(self, rel, fm, body, body_line, fm_error=None):
        self.rel = rel
        self.fm = fm if fm is not None else miniyaml.Mapping()
        self.body = body
        self.body_line = body_line
        self.fm_error = fm_error
        self.type = self.fm.get("type")
        self.title = os.path.splitext(os.path.basename(rel))[0]
        self.aliases = _as_list(self.fm.get("aliases"))

    def line_of(self, key):
        """Source line of a frontmatter key, if known."""
        return self.fm.line_of(key) if hasattr(self.fm, "line_of") else None


class Graph:
    """The whole graph, indexed. Always built whole, never partially."""

    def __init__(self, root, config, today=None):
        self.root = root
        self.config = config
        self.today = today
        self.notes = {}
        self.file_index = {}     # casefolded title/alias -> [rel, ...]
        self.map_entries = {}    # map rel -> [(entry_title, line, heading)]
        self.lateral_inbound = {}  # rel -> set(rel) of body links, excluding map entries


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(description="Validate a knowledge commons graph.")
    sub = parser.add_subparsers(dest="command")

    p_check = sub.add_parser("check", help="validate the graph")
    p_check.add_argument("--graph", required=True)
    p_check.add_argument("--scope", action="append", default=[],
                         help="report only findings whose fix set touches these files")
    p_check.add_argument("--baseline", help="baseline.json; mark findings absent from it as new")
    p_check.add_argument("--format", choices=["text", "json"], default="text")
    p_check.add_argument("--source-scan", action="store_true",
                         help="also scan source artifacts for event-identity collisions")
    p_check.add_argument("--today", help="ISO date to measure staleness against (default: today)")
    p_check.set_defaults(func=cmd_check)

    p_base = sub.add_parser("baseline", help="write the whole-graph fingerprint set")
    p_base.add_argument("--graph", required=True)
    p_base.add_argument("--out", required=True)
    p_base.add_argument("--today", help="ISO date to measure staleness against; RECORDED in "
                                        "the baseline so a later check reuses it")
    p_base.set_defaults(func=cmd_baseline)

    p_schema = sub.add_parser("schema", help="validate .commons.yml only")
    p_schema.add_argument("--graph", required=True)
    p_schema.add_argument("--format", choices=["text", "json"], default="text")
    p_schema.set_defaults(func=cmd_schema)

    p_index = sub.add_parser("index", help="render index.md")
    p_index.add_argument("--graph", required=True)
    p_index.add_argument("--write", action="store_true")
    p_index.set_defaults(func=cmd_index)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return EXIT_USAGE
    return args.func(args)


def cmd_check(args):
    """Run the full validation."""
    try:
        config = load_config(args.graph)
    except (miniyaml.MiniYAMLError, IOError, OSError) as exc:
        return _fail("cannot read %s: %s" % (CONFIG_NAME, exc), args.format)

    findings = check_config(config)
    if _has_error(findings):
        # A wrong config makes every graph finding meaningless, so no graph check runs -- and
        # that is exactly why this must return non-zero UNCONDITIONALLY, ignoring both --scope
        # and --baseline. A pre-existing config error is present in the baseline, hence "not
        # new", hence exit 0 -- while nothing whatsoever was validated. The graph could be in
        # any state at all. A graph that cannot be validated is never safe to write to.
        _report(findings, args, note="config errors -- NO graph check ran")
        return EXIT_ERRORS

    graph = build_graph(args.graph, config, today=_resolve_today(args))
    findings.extend(run_graph_checks(graph, source_scan=args.source_scan))
    return _report(findings, args)


def _resolve_today(args):
    """The date to measure staleness against.

    An explicit --today wins; otherwise inherit the date RECORDED IN THE BASELINE. Without
    that inheritance, a baseline taken on one date and a check run with a different --today
    disagree about which attractors are stale, and the difference surfaces as findings marked
    NEW that the edit did not cause. Any time-dependent check that is not pinned to the same
    instant on both sides of the diff will manufacture phantom refusals.
    """
    explicit = getattr(args, "today", None)
    if explicit:
        return explicit
    baseline = getattr(args, "baseline", None)
    if baseline:
        try:
            with open(baseline, "r", encoding="utf-8") as fh:
                return json.load(fh).get("today")
        except (IOError, OSError, ValueError):
            return None
    return None


def cmd_baseline(args):
    """Write the whole-graph fingerprint set, unscoped."""
    try:
        config = load_config(args.graph)
    except (miniyaml.MiniYAMLError, IOError, OSError) as exc:
        return _fail("cannot read %s: %s" % (CONFIG_NAME, exc), "text")
    today = getattr(args, "today", None) or _today()
    findings = check_config(config)
    if not _has_error(findings):
        graph = build_graph(args.graph, config, today=today)
        findings.extend(run_graph_checks(graph))
    payload = {
        "version": 1,
        "graph": os.path.abspath(args.graph),
        "today": today,
        "fingerprints": sorted(f.fingerprint() for f in findings),
        "counts": _counts(findings),
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    print("baseline: %d findings (%d errors, %d warnings) -> %s"
          % (len(findings), payload["counts"]["errors"], payload["counts"]["warnings"],
             args.out))
    return EXIT_OK


def cmd_schema(args):
    """Validate only the config."""
    try:
        config = load_config(args.graph)
    except (miniyaml.MiniYAMLError, IOError, OSError) as exc:
        return _fail("cannot read %s: %s" % (CONFIG_NAME, exc), args.format)
    args.scope = []
    args.baseline = None
    return _report(check_config(config), args)


def cmd_index(args):
    """Render index.md: attractors only, one line each."""
    try:
        config = load_config(args.graph)
    except (miniyaml.MiniYAMLError, IOError, OSError) as exc:
        return _fail("cannot read %s: %s" % (CONFIG_NAME, exc), "text")
    graph = build_graph(args.graph, config)
    # Validate once and hand the findings over, rather than letting render_index run all 42
    # checks again purely to recover four lifecycle flags.
    text = render_index(graph, findings=run_graph_checks(graph))
    if args.write:
        with open(os.path.join(args.graph, "index.md"), "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote index.md")
    else:
        sys.stdout.write(text)
    return EXIT_OK


# --------------------------------------------------------------------------- config


def load_config(root):
    """Load .commons.yml from the graph root."""
    path = os.path.join(root, CONFIG_NAME)
    if not os.path.exists(path):
        raise IOError("no %s at %s" % (CONFIG_NAME, root))
    data = miniyaml.load_file(path)
    if not isinstance(data, dict):
        raise miniyaml.MiniYAMLError(1, "%s must be a mapping" % CONFIG_NAME)
    return data


def type_table(config):
    """Return {role: [typedef, ...]} for every declared type. No lookup tables, ever.

    The reference's checker early-returns unless a note's directory appears in one hardcoded
    table, and three of its types are absent from it -- so those three get zero validation,
    silently, forever. Here every check loops over THIS table, which is built from the config,
    so a declared type cannot be skipped.
    """
    types = config.get("types") or {}
    table = {}
    for role in ("atlas", "map", "source", "evidence", "reference"):
        td = types.get(role)
        if isinstance(td, dict):
            table[role] = [td]
    for role in ("attractors", "hubs"):
        items = types.get(role) or []
        if isinstance(items, list):
            table[role] = [t for t in items if isinstance(t, dict)]
    return table


def all_typedefs(config):
    """Return {type-name: (role, typedef)} across every role."""
    out = {}
    for role, defs in type_table(config).items():
        for td in defs:
            name = td.get("name")
            if name:
                out[name] = (role, td)
    return out


def is_commons(config):
    """True if this graph is the commons.

    The switch is the presence of a `graduation:` block. Getting this wrong is the single
    most consequential error in this spec's history: the lifecycle, graduation and `domain:`
    are commons-tier mechanisms, and running the >=2-domain bar against a single-domain
    feeder makes it incoherent -- it can never fire, or it gets quietly reinterpreted against
    whatever field happens to be handy. A feeder declares no graduation block, and none of
    those checks run against it.
    """
    return isinstance(config.get("graduation"), dict)


def check_config(config):
    """Config self-checks. These run first; an error here stops the graph checks."""
    out = []
    graph = config.get("graph") or {}
    types = config.get("types") or {}
    typedefs = all_typedefs(config)

    for key in config:
        if key not in KNOWN_TOP_KEYS:
            out.append(Finding("KC109", "warning", [CONFIG_NAME],
                               "unknown top-level config key %r" % key, key=key,
                               hint="a typo here means the block silently never fires"))
    for key in graph:
        if key not in KNOWN_GRAPH_KEYS:
            out.append(Finding("KC109", "warning", [CONFIG_NAME],
                               "unknown key %r under `graph:`" % key, key="graph." + key))

    if not graph.get("atlas"):
        out.append(Finding("KC103", "error", [CONFIG_NAME],
                           "`graph.atlas` is required -- it names the one note with no genitor",
                           key="atlas"))

    evidence = types.get("evidence")
    if isinstance(evidence, dict):
        minimum = evidence.get("min-attractors", 1)
        if not isinstance(minimum, int) or minimum < 1:
            out.append(Finding(
                "KC102", "error", [CONFIG_NAME],
                "`min-attractors: %r` is below the invariant -- a config value below the "
                "invariant is a config error, not an override" % minimum,
                key="min-attractors"))
        if not evidence.get("attractor-field"):
            out.append(Finding("KC102", "error", [CONFIG_NAME],
                               "evidence declares no `attractor-field`",
                               key="attractor-field"))

    # Every content type must declare the map it is entered in -- without it the down-link
    # check has no target, which is how a reachability invariant quietly becomes a no-op.
    for name, (role, td) in sorted(typedefs.items()):
        if role in ("atlas", "map"):
            continue
        if not td.get("map"):
            out.append(Finding("KC103", "error", [CONFIG_NAME],
                               "type %r declares no `map:` -- the down-link check has no target"
                               % name, key=name))

    for td in type_table(config).get("attractors", []):
        name = td.get("name")
        if td.get("lifecycle") and not is_commons(config):
            out.append(Finding(
                "KC104", "warning", [CONFIG_NAME],
                "attractor %r declares a lifecycle but this graph has no `graduation:` block; "
                "a feeder graph is single-domain and nothing graduates in it" % name,
                key=name))
        if is_commons(config) and not td.get("lifecycle"):
            out.append(Finding("KC104", "error", [CONFIG_NAME],
                               "the commons declares `graduation:` but attractor %r has no "
                               "`lifecycle:` to move through" % name, key=name))

    for td in type_table(config).get("hubs", []):
        name = td.get("name")
        if td.get("bidir-with"):
            missing = [k for k in ("section", "field") if not td.get(k)]
            if missing:
                out.append(Finding(
                    "KC105", "error", [CONFIG_NAME],
                    "hub %r declares `bidir-with` but is missing %s -- the field must be "
                    "declared, never guessed by pluralizing the hub's name"
                    % (name, " and ".join("`%s:`" % m for m in missing)), key=name))

    for tier in config.get("sources") or []:
        if not isinstance(tier, dict):
            continue
        label = tier.get("type", "?")
        if tier.get("path") and not tier.get("glob"):
            out.append(Finding("KC106", "error", [CONFIG_NAME],
                               "source tier %r declares `path:` with no `glob:` -- a permissive "
                               "default queues non-sources" % label, key=label))
        if not tier.get("ledger"):
            out.append(Finding("KC108", "error", [CONFIG_NAME],
                               "source tier %r declares no `ledger:` -- it must be declared, "
                               "not discovered" % label, key=label))

    promotes = graph.get("promotes-to")
    if promotes is not None:
        if not isinstance(promotes, dict) or "kind" not in promotes or "path" not in promotes:
            out.append(Finding("KC107", "error", [CONFIG_NAME],
                               "`promotes-to` must be {kind: graph|instruction-tier, path: ...}",
                               key="promotes-to"))
        elif promotes.get("kind") not in ("graph", "instruction-tier"):
            out.append(Finding("KC107", "error", [CONFIG_NAME],
                               "`promotes-to.kind` must be `graph` or `instruction-tier`, not %r"
                               % promotes.get("kind"), key="promotes-to"))

    schema = config.get("schema") or {}
    for key in schema:
        if key == "controlled-values":
            continue
        if key not in typedefs:
            out.append(Finding("KC110", "error", [CONFIG_NAME],
                               "`schema.%s` names no declared type -- this block never fires"
                               % key, key=key,
                               hint="a dead config key is indistinguishable from a passing check"))
    for name in sorted(typedefs):
        if name not in schema:
            out.append(Finding("KC110", "warning", [CONFIG_NAME],
                               "type %r has no `schema:` entry -- nothing is required of it"
                               % name, key=name))
    return out


# --------------------------------------------------------------------------- graph


def build_graph(root, config, today=None):
    """Walk the graph and build every index. Always whole, never scoped."""
    graph = Graph(os.path.abspath(root), config, today=today)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            if not name.endswith(".md"):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            if rel in ("index.md", "changelog.md") or rel.startswith("changelog/"):
                continue
            graph.notes[rel] = _read_note(path, rel)
    _build_indexes(graph)
    return graph


def _read_note(path, rel):
    """Parse one note. A parse failure becomes a Note carrying the error, never an exception."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except (UnicodeDecodeError, IOError, OSError) as exc:
        # The open() used to sit outside the try, so a single latin-1 byte anywhere in the
        # graph killed the whole run with a traceback instead of reporting one bad note.
        return Note(rel, None, "", 1, fm_error="cannot read file: %s" % exc)
    try:
        fm_text, body, body_line = miniyaml.split_frontmatter(text)
    except miniyaml.MiniYAMLError as exc:
        return Note(rel, None, text, 1, fm_error=str(exc))
    if fm_text is None:
        return Note(rel, None, text, 1, fm_error="no frontmatter")
    try:
        fm = miniyaml.load(fm_text)
    except miniyaml.MiniYAMLError as exc:
        return Note(rel, None, body, body_line, fm_error=str(exc))
    if fm is None:
        fm = miniyaml.Mapping()
    if not isinstance(fm, dict):
        return Note(rel, None, body, body_line, fm_error="frontmatter is not a mapping")
    return Note(rel, fm, body, body_line)


def _build_indexes(graph):
    """Build the file index (alias-aware), the map-entry index, and lateral inbound links."""
    for rel, note in graph.notes.items():
        graph.file_index.setdefault(note.title.casefold(), []).append(rel)
        for alias in note.aliases:
            if isinstance(alias, str):
                graph.file_index.setdefault(alias.casefold(), []).append(rel)

    map_type = (graph.config.get("types") or {}).get("map") or {}
    heading_level = map_type.get("heading-level", 1)
    map_rels = {r for r, n in graph.notes.items() if n.type == map_type.get("name")}
    atlas_rel = _atlas_rel(graph)
    if atlas_rel:
        map_rels.add(atlas_rel)

    for rel in map_rels:
        graph.map_entries[rel] = _parse_map(graph.notes[rel], heading_level)

    # A LATERAL edge is any link that is not a navigation link. Concretely: exclude maps and
    # the atlas as sources entirely (their body links ARE the down-link entries), and exclude
    # the `genitor` field (that is the up-link). Everything else counts -- body prose links
    # AND frontmatter association fields like `supports:` or `plots:`, because those are the
    # reasoning tier's edges and they are exactly what the dead vault lacked. Its wikilinks
    # were parent-pointers and nothing else.
    parent_field = (graph.config.get("graph") or {}).get("parent-field", "genitor")
    for rel, note in graph.notes.items():
        if rel in map_rels:
            continue
        for link in _lateral_links(note, parent_field):
            resolved = resolve_link(graph, link.target)
            if resolved and resolved != rel:
                graph.lateral_inbound.setdefault(resolved, set()).add(rel)


def _lateral_links(note, parent_field):
    """Every non-navigation link a note makes: body prose, plus frontmatter minus `genitor`.

    Only genuine `[[wikilinks]]` count here. `_fm_links` deliberately falls back to the raw
    value (so an unbracketed `genitor: observations` still resolves), but that fallback would
    turn `date: 2026-07-08` into a link to a note called "2026-07-08".
    """
    links = list(_body_links(note))
    for key in note.fm:
        if key == parent_field:
            continue
        for value in _as_list(note.fm.get(key)):
            if not isinstance(value, str):
                continue
            for match in WIKILINK_RE.finditer(value):
                links.append(Link(match.group(1).strip(), note.line_of(key), field=key))
    return [l for l in links if l.target]


def _atlas_rel(graph):
    """The atlas's rel path. An exact path wins; a basename match is a deterministic fallback.

    The atlas is the root of the entire reachability invariant -- every down-link check and
    the root count hang off it -- so which note holds the role must not depend on the order
    os.walk happened to yield. Matching a bare basename anywhere in the tree let a second
    `grove.md` in some subdirectory silently claim the role. Exact match first, then a
    basename match chosen deterministically; the ambiguity itself is reported by check_atlas.
    """
    atlas = (graph.config.get("graph") or {}).get("atlas")
    if not atlas:
        return None
    if atlas in graph.notes:
        return atlas
    candidates = _atlas_candidates(graph, atlas)
    return candidates[0] if candidates else None


def _atlas_candidates(graph, atlas):
    """Every note whose basename matches the configured atlas filename, sorted."""
    return sorted(rel for rel in graph.notes if os.path.basename(rel) == atlas)


class Link:
    """A wikilink occurrence."""

    def __init__(self, target, line, field=None):
        self.target = target
        self.line = line
        self.field = field


def _parse_map(note, heading_level):
    """Return [(entry_title, line, heading)] for a map.

    A map entry is the FIRST wikilink on a bullet line. Any further wikilinks on that line
    are annotations, not entries -- without this rule an annotated entry like
    `- [[Note]] (context, see [[Other]])` corrupts both completeness and duplicate checking.
    """
    entries = []
    heading = None
    marker = "#" * heading_level
    for offset, raw in enumerate(note.body.split("\n")):
        line = note.body_line + offset
        head = HEADING_RE.match(raw)
        if head and len(head.group(1)) == len(marker):
            heading = head.group(2)
            continue
        bullet = BULLET_RE.match(raw)
        if not bullet:
            continue
        match = WIKILINK_RE.search(bullet.group(1))
        if match:
            entries.append((match.group(1).strip(), line, heading))
    return entries


def _body_links(note):
    """Every wikilink in a note's body."""
    out = []
    for offset, raw in enumerate(note.body.split("\n")):
        for match in WIKILINK_RE.finditer(raw):
            out.append(Link(match.group(1).strip(), note.body_line + offset))
    return out


def _fm_links(note, field):
    """Every wikilink in a frontmatter field.

    Values are FLATTENED first, and this is load-bearing. An unquoted wikilink --
    `genitor: [[observations]]`, which people write constantly -- is valid YAML for a nested
    flow sequence, so it parses to `[["observations"]]`, not to a string. Skipping non-strings
    (as this used to) meant `_fm_links` returned nothing, `check_genitor` found `raw` truthy so
    KC003 stayed quiet, and then hit `if not links: continue` -- silently skipping KC004 and
    KC005 entirely. A note could name a genitor that does not exist and the graph validated
    clean. Flattening recovers the target and the checks run.
    """
    out = []
    for value in _flatten(note.fm.get(field)):
        if not isinstance(value, str):
            continue
        match = WIKILINK_RE.search(value)
        target = match.group(1).strip() if match else value.strip()
        if target:
            out.append(Link(target, note.line_of(field), field=field))
    return out


def _flatten(value):
    """Flatten arbitrarily nested lists to a flat list of scalars."""
    if value is None:
        return []
    if not isinstance(value, list):
        return [value]
    out = []
    for item in value:
        out.extend(_flatten(item))
    return out


def resolve_link(graph, target):
    """Resolve a wikilink target to a rel path. Alias-aware; case-insensitive.

    Alias-awareness is the fix for the reference's most likely latent bug: its checker
    resolves links against bare filenames while its own conventions actively encourage
    `aliases:`, so any link written via an alias would be reported unresolved. It only works
    today because a desktop-app CLI does the resolving -- the very dependency this plugin
    must drop.
    """
    if not target:
        return None
    key = target.strip()
    stem = os.path.splitext(os.path.basename(key))[0]
    for candidate in (key.casefold(), stem.casefold()):
        hits = graph.file_index.get(candidate)
        if hits:
            # An ambiguous target resolves deterministically to the first candidate; KC019
            # reports the collision itself, as an error. No resolution policy lives here.
            return sorted(hits)[0]
    return None


def resolve_candidates(graph, target):
    """Every rel path a target could resolve to. >1 means ambiguity, which is an error."""
    if not target:
        return []
    key = target.strip()
    stem = os.path.splitext(os.path.basename(key))[0]
    for candidate in (key.casefold(), stem.casefold()):
        hits = graph.file_index.get(candidate)
        if hits:
            return sorted(set(hits))
    return []


# --------------------------------------------------------------------------- checks


def run_graph_checks(graph, source_scan=False):
    """Run every graph check. Registered, never early-returning."""
    out = []
    for check in (
        check_frontmatter, check_types, check_genitor, check_atlas, check_downlinks,
        check_map_order, check_map_duplicates, check_maps_needed, check_evidence,
        check_hubs, check_schema_fields, check_controlled_values, check_wikilinks,
        check_alias_collisions, check_orphans, check_attractor_shape, check_lifecycle,
        check_processed_stamp,
    ):
        out.extend(check(graph))
    if source_scan:
        out.extend(check_event_identity(graph))
    return out


def check_frontmatter(graph):
    """KC001 -- frontmatter present and parses."""
    out = []
    for rel, note in sorted(graph.notes.items()):
        if note.fm_error:
            out.append(Finding("KC001", "error", [rel],
                               "frontmatter: %s" % note.fm_error, key="fm"))
    return out


def check_types(graph):
    """KC002 -- `type:` declared. KC032 -- directory is a default, never authoritative."""
    out = []
    typedefs = all_typedefs(graph.config)
    for rel, note in sorted(graph.notes.items()):
        if note.fm_error:
            continue
        if not note.type:
            out.append(Finding("KC002", "error", [rel], "no `type:` in frontmatter", key="type"))
            continue
        if note.type not in typedefs:
            out.append(Finding("KC002", "error", [rel],
                               "type %r is not declared in %s" % (note.type, CONFIG_NAME),
                               line=note.line_of("type"), key=note.type))
            continue
        _role, td = typedefs[note.type]
        want = td.get("dir")
        if want:
            actual = os.path.dirname(rel) + "/" if os.path.dirname(rel) else ""
            if actual != want:
                out.append(Finding(
                    "KC032", "warning", [rel],
                    "note is type %r but sits in %r, not the declared %r -- `type:` is "
                    "authoritative and the directory is only a default, so this is reported, "
                    "never acted on" % (note.type, actual or "./", want), key="dir"))
    return out


def check_genitor(graph):
    """KC003/KC004/KC005 -- the up-link."""
    out = []
    config = graph.config
    field = (config.get("graph") or {}).get("parent-field", "genitor")
    typedefs = all_typedefs(config)
    atlas_type = ((config.get("types") or {}).get("atlas") or {}).get("name")

    for rel, note in sorted(graph.notes.items()):
        if note.fm_error or not note.type or note.type not in typedefs:
            continue
        if note.type == atlas_type:
            if note.fm.get(field):
                out.append(Finding("KC006", "error", [rel],
                                   "the atlas must have no `%s` -- it is the root" % field,
                                   key="atlas-genitor"))
            continue
        raw = note.fm.get(field)
        if not raw:
            out.append(Finding("KC003", "error", [rel],
                               "no `%s:` -- every note has a navigation parent" % field,
                               key=field))
            continue
        links = _fm_links(note, field)
        if not links:
            # `raw` is truthy but yielded no target -- an empty list, a mapping, something
            # structurally odd. This used to `continue`, which silently skipped every genitor
            # check below it. There is no shape of a present-but-unusable genitor that should
            # validate clean.
            out.append(Finding("KC003", "error", [rel],
                               "`%s:` is present but names no note (got %r)"
                               % (field, raw), line=note.line_of(field), key=field))
            continue
        target = links[0].target
        resolved = resolve_link(graph, target)
        if not resolved:
            out.append(Finding("KC004", "error", [rel],
                               "`%s: [[%s]]` does not resolve" % (field, target),
                               line=note.line_of(field), key=target))
            continue
        role, td = typedefs[note.type]
        want_map = td.get("map")
        if want_map and role not in ("atlas", "map"):
            got = graph.notes[resolved]
            if got.title.casefold() != str(want_map).casefold():
                out.append(Finding(
                    "KC005", "error", [rel],
                    "type %r must be filed under map %r, but `%s` names %r -- `genitor` "
                    "answers 'where do I file this', never 'what is this about'"
                    % (note.type, want_map, field, got.title),
                    line=note.line_of(field), key=want_map))
    return out


def check_atlas(graph):
    """KC006 -- exactly one root, and it is the atlas."""
    out = []
    config = graph.config
    field = (config.get("graph") or {}).get("parent-field", "genitor")
    atlas_type = ((config.get("types") or {}).get("atlas") or {}).get("name")
    name = (config.get("graph") or {}).get("atlas")
    atlas_rel = _atlas_rel(graph)
    if not atlas_rel:
        return [Finding("KC006", "error", [CONFIG_NAME],
                        "the atlas %r does not exist -- a graph with no root is unreachable"
                        % name, key="atlas-missing")]
    if atlas_rel not in graph.notes or name not in graph.notes:
        candidates = _atlas_candidates(graph, name)
        if len(candidates) > 1:
            out.append(Finding(
                "KC006", "error", candidates,
                "%d notes are named %r, so which one is the atlas depends on filesystem "
                "order -- and the atlas is the root of the whole reachability invariant. "
                "Name the atlas by its path in `graph.atlas`." % (len(candidates), name),
                key="ambiguous-atlas"))
    roots = [r for r, n in sorted(graph.notes.items())
             if not n.fm_error and not n.fm.get(field) and n.type == atlas_type]
    if len(roots) > 1:
        out.append(Finding("KC006", "error", roots,
                           "%d notes have no `%s` -- a graph has exactly one root"
                           % (len(roots), field), key="multiple-roots"))
    return out


def check_downlinks(graph):
    """KC007 -- the down-link. ERROR.

    The redundancy with `genitor` is the point, and this is the half people forget: a valid
    `genitor` alone does not make a note reachable, because a human navigates by READING the
    map's bullet list, not by querying inbound frontmatter fields. The up-link is the
    machine-checkable metadata; the down-link is the human-browsable index.

    This is an ERROR, not a warning, on the authority of the refusal list -- "a note with no
    genitor, or absent from its map -> refused". The severity policy's "an incomplete index
    is a warning" governs `index.md`, the generated editorial artifact, and map TIDINESS
    (ordering, KC008/KC031) -- not reachability, which is half the invariant.
    """
    out = []
    config = graph.config
    typedefs = all_typedefs(config)
    map_type = ((config.get("types") or {}).get("map") or {}).get("name")
    atlas_rel = _atlas_rel(graph)

    listed = {}
    for map_rel, entries in graph.map_entries.items():
        for title, _line, _heading in entries:
            resolved = resolve_link(graph, title)
            if resolved:
                listed.setdefault(resolved, set()).add(map_rel)

    for rel, note in sorted(graph.notes.items()):
        if note.fm_error or not note.type or note.type not in typedefs:
            continue
        role, td = typedefs[note.type]
        if role == "atlas":
            continue

        if note.type == map_type:
            if atlas_rel and atlas_rel not in listed.get(rel, set()):
                out.append(Finding(
                    "KC007", "error", [rel, atlas_rel],
                    "map %r is not listed in the atlas -- it is unreachable by browsing"
                    % note.title, key="atlas-entry",
                    hint="add `- [[%s]]` to %s" % (note.title, atlas_rel)))
            continue

        want_map = td.get("map")
        if not want_map:
            continue
        map_rel = resolve_link(graph, str(want_map))
        if not map_rel:
            continue
        if map_rel not in listed.get(rel, set()):
            out.append(Finding(
                "KC007", "error", [rel, map_rel],
                "%r is not an entry in its parent map %r -- a resolving `genitor` alone does "
                "not make a note reachable" % (note.title, want_map),
                key="down-link",
                hint="add `- [[%s]]` to %s, alphabetically in position" % (note.title, map_rel)))
    return out


def check_map_order(graph):
    """KC008/KC031 -- alphabetical ordering. WARNING (tidiness, not reachability)."""
    out = []
    exempt = {str(x).casefold()
              for x in _as_list((graph.config.get("graph") or {}).get("ordering-exempt"))}
    for map_rel, entries in sorted(graph.map_entries.items()):
        note = graph.notes[map_rel]
        if note.title.casefold() in exempt:
            continue
        by_heading = {}
        for title, line, heading in entries:
            by_heading.setdefault(heading, []).append((title, line))
        for heading, items in by_heading.items():
            titles = [t for t, _ in items]
            if titles != sorted(titles, key=lambda s: s.casefold()):
                out.append(Finding(
                    "KC008", "warning", [map_rel],
                    "entries under %r are not alphabetical -- entries are inserted in "
                    "position, never appended" % (heading or "(no heading)"),
                    line=items[0][1], key=str(heading)))
        headings = [h for h in by_heading if h]
        if headings != sorted(headings, key=lambda s: s.casefold()):
            out.append(Finding("KC031", "warning", [map_rel],
                               "headings are not in alphabetical order", key="headings"))
    return out


def check_map_duplicates(graph):
    """KC009 -- a duplicated entry is ambiguity, not untidiness. ERROR."""
    out = []
    for map_rel, entries in sorted(graph.map_entries.items()):
        seen = {}
        for title, line, _heading in entries:
            folded = title.casefold()
            if folded in seen:
                out.append(Finding("KC009", "error", [map_rel],
                                   "duplicate entry [[%s]] (first at line %d)"
                                   % (title, seen[folded]), line=line, key=folded))
            else:
                seen[folded] = line
    return out


def check_maps_needed(graph):
    """KC030 -- a map is needed. Flags, never creates."""
    out = []
    growth = (graph.config.get("graph") or {}).get("growth") or {}
    threshold = growth.get("new-map-at")
    if not isinstance(threshold, int):
        return out
    field = (graph.config.get("graph") or {}).get("parent-field", "genitor")
    missing = {}
    for rel, note in sorted(graph.notes.items()):
        if note.fm_error:
            continue
        for link in _fm_links(note, field):
            if not resolve_link(graph, link.target):
                missing.setdefault(link.target, []).append(rel)
    for target, rels in sorted(missing.items()):
        if len(rels) >= threshold:
            out.append(Finding(
                "KC030", "warning", sorted(rels),
                "%d notes name a map %r that does not exist (threshold %d) -- a map is "
                "needed here; maps are never created silently"
                % (len(rels), target, threshold), key=target))
    return out


def check_evidence(graph):
    """KC010/KC011 -- the evidence -> attractor edge. The reasoning tier's whole point."""
    out = []
    config = graph.config
    evidence_def = (config.get("types") or {}).get("evidence")
    if not isinstance(evidence_def, dict):
        return out
    ev_name = evidence_def.get("name")
    field = evidence_def.get("attractor-field")
    minimum = evidence_def.get("min-attractors", 1)
    if not isinstance(minimum, int) or minimum < 1:
        minimum = 1   # the config check already errored; keep checking with the invariant
    attractor_names = {td.get("name") for td in type_table(config).get("attractors", [])}
    if not ev_name or not field:
        return out

    for rel, note in sorted(graph.notes.items()):
        if note.fm_error or note.type != ev_name:
            continue
        links = _fm_links(note, field)
        if len(links) < minimum:
            out.append(Finding(
                "KC010", "error", [rel],
                "evidence names %d attractor(s) in `%s:` but needs at least %d -- evidence "
                "that points at nothing is a note nobody will ever find again"
                % (len(links), field, minimum),
                line=note.line_of(field), key=field))
            continue
        for link in links:
            resolved = resolve_link(graph, link.target)
            if not resolved:
                out.append(Finding("KC011", "error", [rel],
                                   "`%s: [[%s]]` does not resolve" % (field, link.target),
                                   line=link.line, key=link.target))
                continue
            target_type = graph.notes[resolved].type
            if target_type not in attractor_names:
                what = repr(target_type) if target_type else "a note with no `type:`"
                out.append(Finding(
                    "KC011", "error", [rel, resolved],
                    "`%s: [[%s]]` points at %s, which is not an attractor"
                    % (field, link.target, what), line=link.line, key=link.target))
    return out


def check_hubs(graph):
    """KC012/KC013/KC033 -- the bidirectional obligation, checked in BOTH directions.

    The reference validates only the first entity type it finds on a note, so a note tagged
    with two validates one. Here the loop is over the config's hub list, so there is no
    first-match to win, and no type can be omitted from a table that does not exist.
    """
    out = []
    config = graph.config
    typedefs = all_typedefs(config)
    for hub_def in type_table(config).get("hubs", []):
        hub_name = hub_def.get("name")
        bound_to = hub_def.get("bidir-with")
        if not hub_name or not bound_to:
            continue
        section = hub_def.get("section")
        field = hub_def.get("field")
        if not section or not field:
            continue   # KC105 already errored on the config

        hub_rels = [r for r, n in graph.notes.items()
                    if not n.fm_error and n.type == hub_name]
        attractor_rels = [r for r, n in graph.notes.items()
                          if not n.fm_error and n.type == bound_to]

        # forward: hub's section lists an attractor -> that attractor must name the hub
        for hub_rel in sorted(hub_rels):
            hub = graph.notes[hub_rel]
            listed = _section_links(hub, section)
            if listed is None:
                out.append(Finding(
                    "KC033", "error", [hub_rel],
                    "hub has no %r section -- renaming or dropping the section must FAIL, "
                    "never silently disable the bidirectional check" % section,
                    key="section", hint="add a `%s` heading" % section))
                continue
            for link in listed:
                resolved = resolve_link(graph, link.target)
                if not resolved:
                    out.append(Finding("KC012", "error", [hub_rel],
                                       "%s lists [[%s]], which does not resolve"
                                       % (section, link.target), line=link.line,
                                       key=link.target))
                    continue
                attractor = graph.notes[resolved]
                named = {resolve_link(graph, l.target) for l in _fm_links(attractor, field)}
                if hub_rel not in named:
                    out.append(Finding(
                        "KC012", "error", [hub_rel, resolved],
                        "hub %r lists [[%s]] in %s, but that attractor does not name the hub "
                        "back in `%s:` -- half a bidirectional pair is not a smaller "
                        "violation than none, it is a worse one"
                        % (hub.title, link.target, section, field),
                        line=link.line, key="pair"))

        # reverse: attractor names a hub -> that hub's section must link back
        for att_rel in sorted(attractor_rels):
            attractor = graph.notes[att_rel]
            for link in _fm_links(attractor, field):
                resolved = resolve_link(graph, link.target)
                if not resolved:
                    out.append(Finding("KC013", "error", [att_rel],
                                       "`%s: [[%s]]` does not resolve" % (field, link.target),
                                       line=link.line, key=link.target))
                    continue
                hub = graph.notes[resolved]
                if hub.type != hub_name:
                    if hub.type not in typedefs or typedefs[hub.type][0] != "hubs":
                        out.append(Finding(
                            "KC013", "error", [att_rel, resolved],
                            "`%s: [[%s]]` points at a %r, which is not a hub"
                            % (field, link.target, hub.type), line=link.line,
                            key=link.target))
                    continue
                listed = _section_links(hub, section)
                if listed is None:
                    continue   # KC033 already fired on the hub
                back = {resolve_link(graph, l.target) for l in listed}
                if att_rel not in back:
                    out.append(Finding(
                        "KC013", "error", [att_rel, resolved],
                        "attractor %r names hub [[%s]] in `%s:`, but the hub's %s does not "
                        "link back" % (attractor.title, link.target, field, section),
                        line=link.line, key="pair"))
    return out


def _section_links(note, section):
    """Wikilinks under a named section. None if the section is absent.

    The heading is matched on normalized text, case-insensitively -- never by a hardcoded
    case-sensitive regex, which in the reference means renaming a section silently disables
    the check that depends on it. Here a missing section is loud (KC033).
    """
    want = section.lstrip("#").strip().casefold()
    depth = len(section) - len(section.lstrip("#"))
    links = []
    inside = False
    for offset, raw in enumerate(note.body.split("\n")):
        head = HEADING_RE.match(raw)
        if head:
            level = len(head.group(1))
            if head.group(2).strip().casefold() == want and (not depth or level == depth):
                inside = True
                continue
            if inside and level <= (depth or level):
                break
        if inside:
            for match in WIKILINK_RE.finditer(raw):
                links.append(Link(match.group(1).strip(), note.body_line + offset))
    return links if inside else None


def check_schema_fields(graph):
    """KC014/KC015 -- required present, forbidden absent. ERRORS, deliberately.

    The reference warns. That is a divergence and a deliberate one: knowledge-graph REFUSES a
    missing required field at write time, and a health check that merely warns about what the
    writer refuses is incoherent.
    """
    out = []
    schema = graph.config.get("schema") or {}
    for rel, note in sorted(graph.notes.items()):
        if note.fm_error or not note.type:
            continue
        rules = schema.get(note.type)
        if not isinstance(rules, dict):
            continue
        for want in _as_list(rules.get("required")):
            if note.fm.get(want) in (None, "", [], {}):
                out.append(Finding("KC014", "error", [rel],
                                   "required field `%s:` is missing" % want, key=str(want)))
        for banned in _as_list(rules.get("forbidden")):
            if banned in note.fm:
                out.append(Finding(
                    "KC015", "error", [rel],
                    "forbidden field `%s:` is present" % banned,
                    line=note.line_of(banned), key=str(banned),
                    hint="`domain:` exists only in the commons; a feeder graph is "
                         "single-domain and its provenance is `source:`"))
    return out


def check_controlled_values(graph):
    """KC016 -- controlled vocabularies. Checked on EVERY note carrying the field.

    Four of the reference's six controlled vocabularies are documented but unenforced,
    because the check is keyed on a lookup table that most types are missing from. Here the
    loop is over the vocabularies themselves, so a type cannot escape by being absent from a
    table.
    """
    out = []
    vocab = (graph.config.get("schema") or {}).get("controlled-values") or {}
    if not isinstance(vocab, dict):
        return out
    for field, allowed in sorted(vocab.items()):
        allowed_list = _as_list(allowed)
        if not allowed_list:
            continue
        for rel, note in sorted(graph.notes.items()):
            if note.fm_error or field not in note.fm:
                continue
            for value in _as_list(note.fm.get(field)):
                if value not in allowed_list:
                    out.append(Finding(
                        "KC016", "error", [rel],
                        "`%s: %r` is not in the controlled set %r"
                        % (field, value, allowed_list),
                        line=note.line_of(field), key="%s=%s" % (field, value)))
    return out


def check_wikilinks(graph):
    """KC017 -- links resolve. KC018 -- nothing escapes the graph.

    KC018 is D9's first layer: mechanical containment. A promoted note must be self-contained,
    so a link that reaches out of the graph root -- `[[../commons/Something]]`, or an absolute
    path -- is a boundary breach and not merely a broken link. It is the one boundary layer
    that does not depend on an LLM reading prose, which is why it must actually exist.
    """
    out = []
    parent_field = (graph.config.get("graph") or {}).get("parent-field", "genitor")
    for rel, note in sorted(graph.notes.items()):
        if note.fm_error:
            continue
        for link in _lateral_links(note, "\0") + _fm_links(note, parent_field):
            if _escapes(link.target):
                out.append(Finding(
                    "KC018", "error", [rel],
                    "[[%s]] reaches outside the graph -- a wikilink may not cross a graph "
                    "boundary. Promotion DERIVES a new note; it never links across."
                    % link.target, line=link.line, key=link.target))
        # Body links AND frontmatter wikilinks. `_lateral_links` already counts a frontmatter
        # wikilink as a graph edge -- "exactly what the dead vault lacked" -- but nothing
        # resolved it unless the field happened to have a dedicated check (`genitor`, the
        # attractor field, a hub field). Any other association field (`related:`, `see-also:`,
        # anything a domain invents) could point at nothing at all, forever, in silence.
        for link in _body_links(note) + _other_fm_links(graph, note):
            candidates = resolve_candidates(graph, link.target)
            if not candidates:
                out.append(Finding(
                    "KC017", "error", [rel],
                    "[[%s]] does not resolve%s" % (
                        link.target, " (in `%s:`)" % link.field if link.field else ""),
                    line=link.line, key=link.target,
                    hint="stub before linking -- a one-line stub is fine, and stubs "
                         "accumulate content over time"))
            elif len(candidates) > 1:
                out.append(Finding(
                    "KC019", "error", [rel] + candidates,
                    "[[%s]] is ambiguous: %s" % (link.target, ", ".join(candidates)),
                    line=link.line, key=link.target,
                    hint="an ambiguous target makes resolution nondeterministic, which is "
                         "silently-wrong rather than loudly-broken"))
    return out


def _other_fm_links(graph, note):
    """Frontmatter wikilinks in fields that have no dedicated resolution check of their own.

    `genitor`, the evidence type's attractor field, and hub fields are each resolved by the
    check that owns them, and reporting them twice would double-count. Everything else lands
    here, so no frontmatter field can carry a dangling link unnoticed just because nobody
    wrote a check for it.
    """
    config = graph.config
    owned = {(config.get("graph") or {}).get("parent-field", "genitor")}
    evidence = (config.get("types") or {}).get("evidence")
    if isinstance(evidence, dict) and evidence.get("attractor-field"):
        owned.add(evidence["attractor-field"])
    for hub in type_table(config).get("hubs", []):
        if hub.get("field"):
            owned.add(hub["field"])

    out = []
    for key in note.fm:
        if key in owned:
            continue
        for value in _flatten(note.fm.get(key)):
            if not isinstance(value, str):
                continue
            for match in WIKILINK_RE.finditer(value):
                out.append(Link(match.group(1).strip(), note.line_of(key), field=key))
    return out


def _escapes(target):
    """True if a wikilink target reaches outside the graph root."""
    if not target:
        return False
    clean = target.strip()
    return (clean.startswith("/") or clean.startswith("~")
            or clean.startswith("../") or "/../" in clean)


def check_alias_collisions(graph):
    """KC019 -- no alias may collide with another note's title or alias."""
    out = []
    for key, rels in sorted(graph.file_index.items()):
        unique = sorted(set(rels))
        if len(unique) > 1:
            out.append(Finding("KC019", "error", unique,
                               "%r resolves to %d notes: %s"
                               % (key, len(unique), ", ".join(unique)), key=key))
    return out


def check_orphans(graph):
    """KC020 -- lateral orphans. WARNING.

    "No inbound link of ANY kind" is not a usable definition: a note's parent map always
    links it (that is the down-link, and it is mandatory), so under that reading the check
    could never fire on a valid graph. Under the opposite reading -- excluding maps -- every
    leaf note is an orphan, and it fires on everything. Neither is a check.

    So inbound means LATERAL: a wikilink from another note's body, excluding maps and the
    atlas. That makes this the dead-vault detector the design actually wants -- the dead
    vault's diagnosis was precisely "effectively zero lateral links" -- rather than a
    restatement of the down-link check.
    """
    out = []
    config = graph.config
    typedefs = all_typedefs(config)
    exempt = {str(x).casefold()
              for x in _as_list((config.get("graph") or {}).get("expected-orphans"))}
    atlas_rel = _atlas_rel(graph)

    for rel, note in sorted(graph.notes.items()):
        if note.fm_error or not note.type or note.type not in typedefs:
            continue
        role, _td = typedefs[note.type]
        # Exempt by design: maps and the atlas are the navigation tier itself; reference is
        # lookup-only and never indexed; a source note is the ledger, and nothing is supposed
        # to link to it -- provenance flows the other way, through `source:`.
        if role in ("atlas", "map", "reference", "source") or rel == atlas_rel:
            continue
        if note.title.casefold() in exempt:
            continue
        if not graph.lateral_inbound.get(rel):
            out.append(Finding(
                "KC020", "warning", [rel],
                "no lateral inbound link -- reachable by browsing, but nothing associates "
                "with it", key="orphan"))
    return out


def check_attractor_shape(graph):
    """KC025/KC034/KC035 -- attractors accumulate evidence, and say so what."""
    out = []
    config = graph.config
    evidence_def = (config.get("types") or {}).get("evidence") or {}
    ev_name = evidence_def.get("name")
    ev_field = evidence_def.get("attractor-field")

    inbound = {}
    if ev_name and ev_field:
        for rel, note in graph.notes.items():
            if note.fm_error or note.type != ev_name:
                continue
            for link in _fm_links(note, ev_field):
                resolved = resolve_link(graph, link.target)
                if resolved:
                    inbound.setdefault(resolved, set()).add(rel)

    for td in type_table(config).get("attractors", []):
        name = td.get("name")
        stake = td.get("stake-section")
        evidence_section = td.get("evidence-section")
        for rel, note in sorted(graph.notes.items()):
            if note.fm_error or note.type != name:
                continue
            supporters = inbound.get(rel, set())

            if not supporters:
                out.append(Finding(
                    "KC025", "warning", [rel],
                    "attractor has no evidence -- an attractor nothing points at is a topic",
                    key="no-evidence"))

            if stake and _section_links(note, stake) is None:
                out.append(Finding(
                    "KC034", "warning", [rel],
                    "no %r section -- an attractor without a 'so what' is a topic, not an "
                    "attractor" % stake, key="stake"))

            if evidence_section:
                listed = _section_links(note, evidence_section)
                if listed is None:
                    out.append(Finding("KC035", "error", [rel],
                                       "no %r section to accumulate evidence in"
                                       % evidence_section, key="evidence-section"))
                    continue
                shown = {resolve_link(graph, l.target) for l in listed}
                shown.discard(None)
                for missing in sorted(supporters - shown):
                    out.append(Finding(
                        "KC035", "error", [rel, missing],
                        "%r names this attractor, but it is absent from %s -- the "
                        "propagation is half-done" % (graph.notes[missing].title,
                                                      evidence_section),
                        key="drift:" + missing))
                for extra in sorted(shown - supporters):
                    out.append(Finding(
                        "KC035", "error", [rel, extra],
                        "%s lists %r, but that note does not name this attractor in `%s:` -- "
                        "the evidence note's frontmatter is authoritative, the section is a "
                        "cache" % (evidence_section, graph.notes[extra].title, ev_field),
                        key="drift:" + extra))
    return out


def check_lifecycle(graph):
    """KC021-KC024 -- commons-tier only. A feeder declares no lifecycle and none of this runs.

    Resolved BY POSITION, never by literal name -- a rule that says "flag it `held`" is wrong
    for a type whose lifecycle has no `held`.
    """
    out = []
    config = graph.config
    commons = is_commons(config)
    for td in type_table(config).get("attractors", []):
        name = td.get("name")
        lifecycle = _as_list(td.get("lifecycle"))
        for rel, note in sorted(graph.notes.items()):
            if note.fm_error or note.type != name:
                continue
            status = note.fm.get("status")
            if not lifecycle:
                if status is not None:
                    out.append(Finding(
                        "KC024", "error", [rel],
                        "`status: %r` but type %r declares no lifecycle -- the lifecycle is a "
                        "commons-tier mechanism; a feeder graph is single-domain and nothing "
                        "graduates in it" % (status, name),
                        line=note.line_of("status"), key="no-lifecycle"))
                continue
            if status is None:
                out.append(Finding("KC024", "error", [rel],
                                   "no `status:` but type %r declares a lifecycle %r"
                                   % (name, lifecycle), key="status"))
                continue
            if status not in lifecycle:
                out.append(Finding("KC024", "error", [rel],
                                   "`status: %r` is not in the lifecycle %r"
                                   % (status, lifecycle),
                                   line=note.line_of("status"), key=str(status)))

    if commons:
        out.extend(_check_graduation(graph))
    return out


def _check_graduation(graph):
    """KC021/KC022 -- the >=2-domain bar. Counted off the EVIDENCE notes, never the bullets."""
    out = []
    config = graph.config
    graduation = config.get("graduation") or {}
    bar = graduation.get("bar", 2)
    evidence_def = (config.get("types") or {}).get("evidence") or {}
    ev_name = evidence_def.get("name")
    ev_field = evidence_def.get("attractor-field")
    if not ev_name or not ev_field or not isinstance(bar, int):
        return out

    domains = {}
    for rel, note in graph.notes.items():
        if note.fm_error or note.type != ev_name:
            continue
        domain = note.fm.get("domain")
        for link in _fm_links(note, ev_field):
            resolved = resolve_link(graph, link.target)
            if resolved and domain:
                domains.setdefault(resolved, set()).add(domain)

    for td in type_table(config).get("attractors", []):
        lifecycle = _as_list(td.get("lifecycle"))
        if len(lifecycle) < 2:
            continue
        for rel, note in sorted(graph.notes.items()):
            if note.fm_error or note.type != td.get("name"):
                continue
            status = note.fm.get("status")
            if status not in lifecycle:
                continue
            position = lifecycle.index(status)
            count = len(domains.get(rel, set()))
            if position == 0 and count >= bar:
                out.append(Finding(
                    "KC021", "warning", [rel],
                    "evidence spans %d domains (bar is %d) -- has earned %r, not yet applied"
                    % (count, bar, lifecycle[1]), key="graduation-pending"))
            elif position == 1 and count < bar:
                out.append(Finding(
                    "KC022", "warning", [rel],
                    "at %r on evidence from %d domain(s), below the bar of %d -- promoted "
                    "early" % (status, count, bar), key="single-domain"))

    out.extend(_check_staleness(graph))
    return out


def _check_staleness(graph):
    """KC023 -- no new evidence in N months.

    `today` is injectable, because a check whose result changes with the wall clock cannot be
    tested, and an untestable check is one nobody can prove fires. The staleness threshold
    itself is an open item in the spec -- to be picked empirically once there are real
    attractors to measure -- so this reports rather than prescribes.
    """
    out = []
    config = graph.config
    graduation = config.get("graduation") or {}
    months = graduation.get("staleness-months")
    if not isinstance(months, int):
        return out

    evidence_def = (config.get("types") or {}).get("evidence") or {}
    ev_name = evidence_def.get("name")
    ev_field = evidence_def.get("attractor-field")
    if not ev_name or not ev_field:
        return out

    newest = {}
    for rel, note in graph.notes.items():
        if note.fm_error or note.type != ev_name:
            continue
        date = str(note.fm.get("date") or "")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            continue
        for link in _fm_links(note, ev_field):
            resolved = resolve_link(graph, link.target)
            if resolved:
                if date > newest.get(resolved, ""):
                    newest[resolved] = date

    today = graph.today or _today()
    cutoff = _months_before(today, months)
    for td in type_table(config).get("attractors", []):
        lifecycle = _as_list(td.get("lifecycle"))
        for rel, note in sorted(graph.notes.items()):
            if note.fm_error or note.type != td.get("name"):
                continue
            # A retired attractor (the last lifecycle position) is not "stale"; it is done.
            if lifecycle and note.fm.get("status") == lifecycle[-1]:
                continue
            last = newest.get(rel)
            if last and last < cutoff:
                out.append(Finding(
                    "KC023", "warning", [rel],
                    "no new evidence since %s (threshold: %d months before %s)"
                    % (last, months, today), key="stale"))
    return out


def _today():
    """Today, as an ISO date string."""
    import datetime
    return datetime.date.today().isoformat()


def _months_before(iso, months):
    """The ISO date `months` before `iso`, with the day clamped to the target month.

    Naive arithmetic that keeps the day-of-month yields 2027-02-31 for one month before
    2027-03-31. The cutoff is compared lexicographically against evidence dates, so an
    impossible date silently flags attractors stale several days early whenever `today`
    lands on the 29th to the 31st.
    """
    import calendar
    year, month, day = (int(x) for x in iso.split("-"))
    total = year * 12 + (month - 1) - months
    target_year, target_month = total // 12, total % 12 + 1
    day = min(day, calendar.monthrange(target_year, target_month)[1])
    return "%04d-%02d-%02d" % (target_year, target_month, day)


def check_processed_stamp(graph):
    """KC027 -- the ledger stamp has a schema and is checked.

    The reference references this stamp and never defines or validates it.
    """
    out = []
    for rel, note in sorted(graph.notes.items()):
        if note.fm_error or "processed" not in note.fm:
            continue
        stamp = note.fm.get("processed")
        line = note.line_of("processed")
        if not isinstance(stamp, list):
            out.append(Finding("KC027", "error", [rel],
                               "`processed:` must be a list, so it keeps a history",
                               line=line, key="shape"))
            continue
        for entry in stamp:
            if not isinstance(entry, dict):
                out.append(Finding("KC027", "error", [rel],
                                   "each `processed:` entry must be a mapping", line=line,
                                   key="entry"))
                continue
            date = entry.get("date")
            if not isinstance(date, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", str(date)):
                out.append(Finding("KC027", "error", [rel],
                                   "`processed[].date: %r` is not an ISO date" % date,
                                   line=line, key="date"))
            for key in ("ran", "skipped", "errored"):
                if key in entry and not isinstance(entry.get(key), list):
                    out.append(Finding("KC027", "error", [rel],
                                       "`processed[].%s` must be a list" % key, line=line,
                                       key=key))
    return out


def check_event_identity(graph):
    """KC028 -- two identical headings in one source artifact collide on the same identity.

    An event's canonical identity is `<artifact-path>#<verbatim-heading>`. Two identical
    headings in one artifact therefore produce one identity, and the second event is treated
    as already processed -- silently. That silence is why this is an error and not a warning.
    """
    out = []
    import glob as globmod
    for tier in graph.config.get("sources") or []:
        if not isinstance(tier, dict):
            continue
        path = tier.get("path")
        pattern = tier.get("glob")
        delimiter = tier.get("event-delimiter")
        if not path or not pattern or not delimiter:
            continue
        try:
            regex = re.compile(delimiter)
        except re.error as exc:
            out.append(Finding("KC028", "error", [CONFIG_NAME],
                               "source tier %r has an uncompilable `event-delimiter`: %s"
                               % (tier.get("type"), exc), key="delimiter"))
            continue
        base = path if os.path.isabs(path) else os.path.join(graph.root, path)
        for artifact in sorted(globmod.glob(os.path.join(base, pattern))):
            try:
                with open(artifact, "r", encoding="utf-8") as fh:
                    lines = fh.read().split("\n")
            except (IOError, OSError):
                continue
            seen = {}
            for offset, raw in enumerate(lines):
                if not regex.match(raw):
                    continue
                heading = raw.strip()
                if heading in seen:
                    out.append(Finding(
                        "KC028", "error", [CONFIG_NAME],
                        "%s has two identical event headings %r (lines %d and %d) -- they "
                        "collide on one canonical identity and the second would be silently "
                        "treated as already processed"
                        % (artifact, heading, seen[heading], offset + 1),
                        key="%s#%s" % (artifact, heading)))
                else:
                    seen[heading] = offset + 1
    return out


# --------------------------------------------------------------------------- index


def render_index(graph, findings=None):
    """Render index.md -- attractors only, one line each. The stimulus for association.

    The flag vocabulary is closed and maps 1:1 onto the checks, which is exactly why the
    index lives inside the validator: the flags and the checks must not be able to disagree.

    `findings` is passed in when the caller has already validated, so regenerating the index
    does not walk and re-validate the whole graph a second time. It is computed only when the
    caller has nothing to hand over.
    """
    config = graph.config
    if findings is None:
        findings = run_graph_checks(graph)
    flags = {}
    for finding in findings:
        flag = {
            "KC021": "graduation-pending",
            "KC022": "single-domain",
            "KC023": "stale",
            "KC025": "orphan",
        }.get(finding.check)
        if flag:
            for rel in finding.paths:
                flags.setdefault(rel, set()).add(flag)

    evidence_def = (config.get("types") or {}).get("evidence") or {}
    ev_name = evidence_def.get("name")
    ev_field = evidence_def.get("attractor-field")
    domains = {}
    if ev_name and ev_field:
        for rel, note in graph.notes.items():
            if note.fm_error or note.type != ev_name:
                continue
            domain = note.fm.get("domain")
            for link in _fm_links(note, ev_field):
                resolved = resolve_link(graph, link.target)
                if resolved and domain:
                    domains.setdefault(resolved, set()).add(str(domain))

    lines = ["# Index", "",
             "_Generated by `commons-check --index`. Do not hand-edit._", ""]
    for td in type_table(config).get("attractors", []):
        name = td.get("name")
        stake = td.get("stake-section")
        rels = sorted(r for r, n in graph.notes.items()
                      if not n.fm_error and n.type == name)
        if not rels:
            continue
        lines.append("## %ss" % name)
        for rel in rels:
            note = graph.notes[rel]
            so_what = _first_prose(note, stake) if stake else ""
            bits = ["- **%s**" % note.title]
            if so_what:
                bits.append(" — %s" % so_what)
            found = sorted(domains.get(rel, set()))
            if found:
                bits.append(" `[%s]`" % ", ".join(found))
            for flag in sorted(flags.get(rel, set())):
                bits.append(" ⚠️ %s" % flag)
            lines.append("".join(bits))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _first_prose(note, section):
    """The first non-empty prose line under a section."""
    want = section.lstrip("#").strip().casefold()
    inside = False
    for raw in note.body.split("\n"):
        head = HEADING_RE.match(raw)
        if head:
            if head.group(2).strip().casefold() == want:
                inside = True
                continue
            if inside:
                break
        if inside and raw.strip():
            return raw.strip()
    return ""


# --------------------------------------------------------------------------- reporting


def _as_list(value):
    """Coerce a scalar-or-list config value to a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _has_error(findings):
    """True if any finding is an error."""
    return any(f.severity == "error" for f in findings)


def _counts(findings):
    """Error and warning counts."""
    return {
        "errors": sum(1 for f in findings if f.severity == "error"),
        "warnings": sum(1 for f in findings if f.severity == "warning"),
    }


def _fail(message, fmt):
    """The validator could not run. Loud, and never mistaken for clean."""
    if fmt == "json":
        json.dump({"version": 1, "fatal": message}, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stderr.write("fatal: %s\n" % message)
    return EXIT_USAGE


def _report(findings, args, note=""):
    """Filter by scope, mark against baseline, render, and pick an exit code."""
    scope = {s.replace(os.sep, "/") for s in getattr(args, "scope", []) or []}
    if scope:
        # A config finding is NEVER scoped away. Its only path is `.commons.yml`, which no
        # scoped note ever matches, so filtering it out made a broken config report "0 errors,
        # exit 0" on precisely the call `knowledge-graph` makes before every write -- the gate
        # would have waved every write through on a graph it could not even validate.
        findings = [f for f in findings
                    if CONFIG_NAME in f.paths or scope & set(f.paths)]

    baseline = None
    if getattr(args, "baseline", None):
        try:
            with open(args.baseline, "r", encoding="utf-8") as fh:
                baseline = set(json.load(fh).get("fingerprints") or [])
        except (IOError, OSError, ValueError) as exc:
            # Never treat an unreadable baseline as an empty one: every finding would look
            # NEW, or -- worse, if the caller ignores the code -- the run would look clean.
            return _fail("cannot read baseline %s: %s" % (args.baseline, exc),
                         getattr(args, "format", "text"))
        for finding in findings:
            finding.new = finding.fingerprint() not in baseline

    findings.sort(key=lambda f: (f.locus(), f.check, f.line or 0))
    counts = _counts(findings)
    new_errors = [f for f in findings if f.new and f.severity == "error"]

    if getattr(args, "format", "text") == "json":
        payload = {
            "version": 1,
            "scope": sorted(scope),
            "summary": {
                "errors": counts["errors"],
                "warnings": counts["warnings"],
                "new_errors": len(new_errors),
            },
            "findings": [f.to_dict() for f in findings],
        }
        if note:
            payload["note"] = note
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        for finding in findings:
            where = finding.locus()
            if finding.line:
                where += ":%d" % finding.line
            marker = "NEW " if finding.new else ""
            print("%-7s %s %s  %s" % (finding.severity.upper(), finding.check,
                                       where, marker + finding.message))
            if finding.hint:
                print("      %s" % finding.hint)
        summary = "%d error%s, %d warning%s" % (
            counts["errors"], "" if counts["errors"] == 1 else "s",
            counts["warnings"], "" if counts["warnings"] == 1 else "s")
        if baseline is not None:
            summary += " — %d NEW error%s vs baseline" % (
                len(new_errors), "" if len(new_errors) == 1 else "s")
        if note:
            summary += " (%s)" % note
        print(summary)

    if baseline is not None:
        return EXIT_NEW_ERRORS if new_errors else EXIT_OK
    return EXIT_ERRORS if counts["errors"] else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
