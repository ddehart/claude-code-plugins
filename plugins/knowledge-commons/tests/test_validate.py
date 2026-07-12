#!/usr/bin/env python3
"""Prove every check fires.

The spec's method note is blunt: every defect found in the superseded design across six
rounds was found by EXECUTING the thing or by checking two documents against each other.
Author review found none of them. So this suite does not read the validator -- it runs it,
against a graph deliberately broken one way at a time.

The load-bearing test is `test_every_check_is_proven_to_fire` at the bottom. A check with no
firing test is, empirically, indistinguishable from a check that always passes -- which is
exactly how the reference's own dead checks survived for a year.
"""

import os
import unittest

from support import GraphCase, codes, materialize, run_check, fixture


def drop_line(needle):
    """Remove the first line containing `needle`."""
    def mutate(text):
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if needle in line:
                del lines[i]
                break
        return "\n".join(lines)
    return mutate


def replace(old, new):
    """Replace the first occurrence of `old`."""
    return lambda text: text.replace(old, new, 1)


def append(extra):
    """Append text."""
    return lambda text: text + extra


OBS_ROW = "observations/Row four leafs out ten days before row nine.md"
OBS_BLOSSOM = "observations/Blossom damage clusters at the bottom of the slope.md"
PATTERN = "patterns/Cold air pools at the low end of the slope.md"
PRACTICE = "practices/Mulch after the first hard freeze, not before.md"
PLOT = "plots/North Plot.md"
MAP_OBS = "maps/observations.md"
ATLAS = "grove.md"
LOGBOOK = "logbook/2026-03-14 Spring walkthrough.md"


class ValidFixtures(GraphCase):
    """The pristine fixtures must be clean, or every warning below is background noise."""

    def test_feeder_is_clean(self):
        findings = run_check(fixture("orchard"))
        self.assertEqual([], findings,
                         "the feeder fixture must have zero findings, got: %s"
                         % [(f.check, f.locus()) for f in findings])

    def test_commons_has_no_errors(self):
        self.assertClean(run_check(fixture("commons")))

    def test_commons_demonstrates_the_graduation_bar(self):
        """The federation's whole premise: an attractor spanning two domains has earned a stance."""
        findings = run_check(fixture("commons"))
        self.assertFires("KC021", findings, severity="warning")

    def test_feeder_runs_no_graduation_check(self):
        """D5b: the >=2-domain bar is incoherent in a single-domain graph and must not run."""
        findings = run_check(fixture("orchard"))
        self.assertNotIn("KC021", codes(findings))
        self.assertNotIn("KC022", codes(findings))


class Frontmatter(GraphCase):

    def test_KC001_unparseable_frontmatter(self):
        root = materialize(edits={OBS_ROW: replace("type: observation", "type: [oops")})
        self.assertFires("KC001", run_check(root))

    def test_KC001_missing_frontmatter(self):
        root = materialize(edits={OBS_ROW: lambda t: t.split("---\n", 2)[-1]})
        self.assertFires("KC001", run_check(root))

    def test_KC002_undeclared_type(self):
        root = materialize(edits={OBS_ROW: replace("type: observation", "type: musing")})
        self.assertFires("KC002", run_check(root))

    def test_KC032_directory_mismatch_is_only_a_warning(self):
        """`type:` is authoritative; the directory is a default. A folderless graph validates."""
        root = materialize(base="orchard")
        src = os.path.join(root, OBS_ROW)
        dst = os.path.join(root, "Row four leafs out ten days before row nine.md")
        os.rename(src, dst)
        self.assertFires("KC032", run_check(root), severity="warning")


class Navigation(GraphCase):

    def test_KC003_no_genitor(self):
        root = materialize(edits={OBS_ROW: drop_line("genitor:")})
        self.assertFires("KC003", run_check(root))

    def test_KC004_genitor_unresolved(self):
        root = materialize(edits={OBS_ROW: replace('genitor: "[[observations]]"',
                                                   'genitor: "[[nowhere]]"')})
        self.assertFires("KC004", run_check(root))

    def test_KC005_genitor_names_the_wrong_map(self):
        """`genitor` answers 'where do I file this', never 'what is this about'."""
        root = materialize(edits={OBS_ROW: replace('genitor: "[[observations]]"',
                                                   'genitor: "[[patterns]]"')})
        self.assertFires("KC005", run_check(root))

    def test_KC006_atlas_with_a_genitor(self):
        root = materialize(edits={ATLAS: replace("type: atlas",
                                                 'type: atlas\ngenitor: "[[observations]]"')})
        self.assertFires("KC006", run_check(root))

    def test_KC007_down_link_missing(self):
        """The half people forget. A resolving genitor alone does not make a note reachable."""
        root = materialize(edits={
            MAP_OBS: drop_line("Row four leafs out ten days before row nine")})
        findings = run_check(root)
        self.assertFires("KC007", findings)
        hit = [f for f in findings if f.check == "KC007"][0]
        # The fix set names BOTH the note and the map -- either could be the file that is
        # wrong, and a transaction touching only one of them must still see this.
        self.assertEqual([MAP_OBS, OBS_ROW], hit.paths)

    def test_KC007_map_missing_from_atlas(self):
        root = materialize(edits={ATLAS: drop_line("[[patterns]]")})
        self.assertFires("KC007", run_check(root))

    def test_KC008_entries_out_of_order(self):
        root = materialize(edits={MAP_OBS: replace(
            "- [[Blossom damage clusters at the bottom of the slope]]\n"
            "- [[Mulching before the first hard freeze cut winter loss]]",
            "- [[Mulching before the first hard freeze cut winter loss]]\n"
            "- [[Blossom damage clusters at the bottom of the slope]]")})
        self.assertFires("KC008", run_check(root), severity="warning")

    def test_KC009_duplicate_entry_is_an_error(self):
        root = materialize(edits={MAP_OBS: append(
            "- [[Row four leafs out ten days before row nine]]\n")})
        self.assertFires("KC009", run_check(root))

    def test_KC030_a_map_is_needed(self):
        """Flags, never creates. Maps are proposed in the plan, not conjured at check time."""
        adds = {}
        for i in range(5):
            adds["observations/Placeholder note %d.md" % i] = (
                '---\ntype: observation\ngenitor: "[[seasons]]"\ndate: 2026-05-0%d\n'
                'source: "x#y"\nsupports:\n'
                '  - "[[Cold air pools at the low end of the slope]]"\n---\nBody.\n' % (i + 1))
        root = materialize(adds=adds)
        self.assertFires("KC030", run_check(root), severity="warning")

    def test_KC031_headings_out_of_order(self):
        root = materialize(edits={MAP_OBS: replace(
            "## entries", "## zebra\n- [[Row four leafs out ten days before row nine]]\n\n## alpha")})
        self.assertFires("KC031", run_check(root), severity="warning")

    def test_an_annotated_entry_does_not_corrupt_completeness(self):
        """A map entry is the FIRST wikilink on a bullet line; the rest are annotations."""
        root = materialize(edits={MAP_OBS: replace(
            "- [[Row four leafs out ten days before row nine]]",
            "- [[Row four leafs out ten days before row nine]] (see also "
            "[[Cold air pools at the low end of the slope]])")})
        self.assertClean(run_check(root))


class Reasoning(GraphCase):

    def test_KC010_evidence_names_no_attractor(self):
        root = materialize(edits={OBS_ROW: replace(
            'supports:\n  - "[[Cold air pools at the low end of the slope]]"\n', "")})
        self.assertFires("KC010", run_check(root))

    def test_KC011_attractor_does_not_resolve(self):
        root = materialize(edits={OBS_ROW: replace(
            "[[Cold air pools at the low end of the slope]]", "[[No such attractor]]")})
        self.assertFires("KC011", run_check(root))

    def test_KC011_points_at_a_non_attractor(self):
        root = materialize(edits={OBS_ROW: replace(
            "[[Cold air pools at the low end of the slope]]", "[[Bramley cooking apple]]")})
        self.assertFires("KC011", run_check(root))

    def test_KC025_attractor_with_no_evidence(self):
        root = materialize(adds={"patterns/Nothing points at this.md":
                                 '---\ntype: pattern\ngenitor: "[[patterns]]"\n---\n'
                                 '# Nothing points at this\n\n## so what\nA topic.\n\n'
                                 '## evidence\n'})
        self.assertFires("KC025", run_check(root), severity="warning")

    def test_KC034_attractor_with_no_so_what_is_a_topic(self):
        root = materialize(edits={PATTERN: replace("## so what", "## commentary")})
        self.assertFires("KC034", run_check(root), severity="warning")

    def test_KC035_evidence_section_omits_a_supporter(self):
        """The propagation choreography, made mechanically checkable."""
        root = materialize(edits={
            PATTERN: drop_line("- [[Row four leafs out ten days before row nine]]")})
        self.assertFires("KC035", run_check(root))

    def test_KC035_evidence_section_lists_a_non_supporter(self):
        """The section is a cache; the evidence note's frontmatter is the record."""
        root = materialize(edits={
            PATTERN: append("- [[Mulching before the first hard freeze cut winter loss]]\n")})
        self.assertFires("KC035", run_check(root))


class Hubs(GraphCase):

    def test_KC012_hub_lists_an_attractor_that_does_not_name_it_back(self):
        """Half a bidirectional pair is not a smaller violation than none. It is a worse one."""
        root = materialize(edits={PATTERN: drop_line('- "[[North Plot]]"')})
        findings = run_check(root)
        self.assertFires("KC012", findings)
        hit = [f for f in findings if f.check == "KC012"][0]
        self.assertEqual([PATTERN, PLOT], hit.paths)

    def test_KC013_attractor_names_a_hub_that_does_not_link_back(self):
        root = materialize(edits={
            PLOT: drop_line("- [[Cold air pools at the low end of the slope]]")})
        self.assertFires("KC013", run_check(root))

    def test_KC033_renaming_the_section_fails_loudly(self):
        """It must FAIL, never silently disable the check that depends on it."""
        root = materialize(edits={PLOT: replace("## patterns", "## Related patterns")})
        self.assertFires("KC033", run_check(root))

    def test_the_hub_section_is_matched_case_insensitively(self):
        root = materialize(edits={PLOT: replace("## patterns", "## Patterns")})
        self.assertClean(run_check(root))


class Schema(GraphCase):

    def test_KC014_required_field_missing(self):
        root = materialize(edits={OBS_ROW: drop_line("date:")})
        self.assertFires("KC014", run_check(root))

    def test_KC015_forbidden_field_present(self):
        """`domain:` exists only in the commons. A feeder that sprouts one is wrong."""
        root = materialize(edits={OBS_ROW: replace("type: observation",
                                                   "type: observation\ndomain: orchard")})
        self.assertFires("KC015", run_check(root))

    def test_KC016_controlled_value_violation(self):
        root = materialize(edits={OBS_ROW: replace("season: spring", "season: monsoon")})
        self.assertFires("KC016", run_check(root))

    def test_KC016_is_checked_on_every_note_carrying_the_field(self):
        """Not just on types that happen to appear in some lookup table."""
        root = materialize(edits={OBS_BLOSSOM: replace("season: spring", "season: harvest")})
        findings = run_check(root)
        self.assertFires("KC016", findings)
        self.assertIn(OBS_BLOSSOM, [f.locus() for f in findings if f.check == "KC016"])

    def test_KC024_status_on_a_type_with_no_lifecycle(self):
        """D5b: a feeder graph is single-domain and nothing graduates in it."""
        root = materialize(edits={PATTERN: replace("type: pattern",
                                                   "type: pattern\nstatus: held")})
        self.assertFires("KC024", run_check(root))

    def test_KC024_status_outside_the_lifecycle(self):
        root = materialize(base="commons", edits={
            "principles/Execution beats review for validating a guard.md":
                replace("status: provisional", "status: canonised")})
        self.assertFires("KC024", run_check(root))


class Links(GraphCase):

    def test_KC017_body_wikilink_unresolved(self):
        root = materialize(edits={PATTERN: append("\nSee also [[A note that does not exist]].\n")})
        self.assertFires("KC017", run_check(root))

    def test_KC019_alias_collides_with_another_title(self):
        root = materialize(edits={PLOT: replace("  - Lower Orchard",
                                                "  - Bramley cooking apple")})
        self.assertFires("KC019", run_check(root))

    def test_links_resolve_through_aliases(self):
        """The reference's most likely latent bug, fixed: resolution must follow `aliases:`.

        The link goes in the prose of `## so what`, not at the end of the note -- appending
        would land it inside `## evidence`, where KC035 would rightly object that the section
        now lists a note which is not evidence. (It did, the first time this test was written.)
        """
        root = materialize(edits={PATTERN: replace(
            "Site frost-tender varietals uphill",
            "Site frost-tender varietals uphill in the [[Lower Orchard]]")})
        self.assertClean(run_check(root))

    def test_KC020_lateral_orphan(self):
        """Not 'no inbound link of any kind' -- that could never fire. LATERAL inbound."""
        root = materialize(adds={
            "practices/An unlinked practice.md":
                '---\ntype: practice\ngenitor: "[[practices]]"\n---\n'
                '# An unlinked practice\n\n## so what\nNothing associates with it.\n\n'
                '## evidence\n- [[Mulching before the first hard freeze cut winter loss]]\n',
            })
        # also list it in its map, so the ONLY thing wrong is the missing lateral edge
        root2 = materialize(
            adds={"practices/An unlinked practice.md":
                  '---\ntype: practice\ngenitor: "[[practices]]"\n---\n'
                  '# An unlinked practice\n\n## so what\nNothing associates with it.\n\n'
                  '## evidence\n'},
            edits={"maps/practices.md": append("- [[An unlinked practice]]\n")})
        self.assertFires("KC020", run_check(root2), severity="warning")


class Ledger(GraphCase):

    def test_KC027_stamp_is_not_a_list(self):
        root = materialize(edits={LOGBOOK: replace(
            "processed:\n  - date: 2026-03-15\n    ran: [extract-logbook]\n"
            "    skipped: []\n    errored: []",
            "processed:\n  date: 2026-03-15")})
        self.assertFires("KC027", run_check(root))

    def test_KC027_stamp_date_is_not_iso(self):
        root = materialize(edits={LOGBOOK: replace("date: 2026-03-15", "date: last Tuesday")})
        self.assertFires("KC027", run_check(root))

    def test_KC028_duplicate_event_headings_collide(self):
        """Two identical headings in one artifact resolve to ONE canonical identity."""
        root = materialize(adds={
            "logbook-source/2026-05-01.md":
                "# 2026-05-01\n\n## 09:20 Walkthrough\nFirst.\n\n## 09:20 Walkthrough\nSecond.\n"})
        self.assertFires("KC028", run_check(root, source_scan=True))


class Config(GraphCase):

    def test_KC102_min_attractors_below_the_invariant(self):
        """A config value below the invariant is a config error, not an override."""
        root = materialize(edits={".commons.yml": replace("min-attractors: 1",
                                                          "min-attractors: 0")})
        self.assertFires("KC102", run_check(root))

    def test_KC103_type_declares_no_map(self):
        root = materialize(edits={".commons.yml": replace(
            "{ name: varietal, dir: varietals/, map: varietals }",
            "{ name: varietal, dir: varietals/ }")})
        self.assertFires("KC103", run_check(root))

    def test_KC105_hub_declares_bidir_but_no_field(self):
        """The field must be declared, never guessed by pluralizing the hub's name."""
        root = materialize(edits={".commons.yml": replace(
            'section: "## patterns", field: plots', 'section: "## patterns"')})
        self.assertFires("KC105", run_check(root))

    def test_KC106_source_tier_with_path_and_no_glob(self):
        root = materialize(edits={".commons.yml": drop_line('glob: "20*.md"')})
        self.assertFires("KC106", run_check(root))

    def test_KC107_promotes_to_is_a_bare_path(self):
        root = materialize(edits={".commons.yml": replace(
            "promotes-to: { kind: graph, path: ../commons }", "promotes-to: ../commons")})
        self.assertFires("KC107", run_check(root))

    def test_KC108_source_tier_declares_no_ledger(self):
        """It must be declared, not discovered."""
        root = materialize(edits={".commons.yml": drop_line("ledger: source-note")})
        self.assertFires("KC108", run_check(root))

    def test_KC109_unknown_key_is_a_typo_detector(self):
        root = materialize(edits={".commons.yml": replace("  maps-dir: maps/",
                                                          "  maps-dirr: maps/")})
        self.assertFires("KC109", run_check(root), severity="warning")

    def test_KC110_dead_schema_key_never_fires(self):
        """A dead config key is indistinguishable from a passing check. That is the bug."""
        root = materialize(edits={".commons.yml": replace(
            "  varietal: { required: [type, genitor, verified] }",
            "  varietal: { required: [type, genitor, verified] }\n"
            "  cultivar: { required: [type] }")})
        self.assertFires("KC110", run_check(root))

    def test_KC104_feeder_declaring_a_lifecycle(self):
        root = materialize(edits={".commons.yml": replace(
            "{ name: practice, dir: practices/, map: practices,",
            "{ name: practice, dir: practices/, map: practices, lifecycle: [a, b],")})
        self.assertFires("KC104", run_check(root), severity="warning")


class ScopeAndBaseline(GraphCase):
    """Scoping narrows REPORTING. The baseline diff is what narrows blame."""

    def test_scope_hides_findings_whose_fix_set_it_does_not_touch(self):
        root = materialize(edits={OBS_ROW: drop_line("date:")})
        self.assertFires("KC014", run_check(root))
        self.assertEqual([], run_check(root, scope=[PLOT]))

    def test_scope_keeps_a_cross_file_finding_from_either_side(self):
        """A half-written pair is visible from BOTH files, which is why paths is the fix set."""
        root = materialize(edits={PATTERN: drop_line('- "[[North Plot]]"')})
        self.assertFires("KC012", run_check(root, scope=[PATTERN]))
        self.assertFires("KC012", run_check(root, scope=[PLOT]))

    def test_fingerprints_survive_a_line_shift(self):
        """A line-sensitive identity would make every pre-existing finding look brand new,
        and the transaction would then refuse every write into an imperfect graph."""
        broken = materialize(edits={OBS_ROW: drop_line("date:")})
        before = {f.fingerprint() for f in run_check(broken)}

        shifted = materialize(edits={OBS_ROW: drop_line("date:")})
        path = os.path.join(shifted, PATTERN)
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text.replace("## so what", "\n\n## so what"))
        after = {f.fingerprint() for f in run_check(shifted)}

        self.assertTrue(before, "expected a pre-existing finding to compare")
        self.assertTrue(before <= after,
                        "a pre-existing finding changed fingerprint after an unrelated edit")


class EveryCheckFires(GraphCase):
    """The load-bearing test.

    A check with no firing test is indistinguishable from a check that always passes. This is
    what makes 'every check is proven to fire' mechanical instead of aspirational, and it is
    the direct answer to the reference's dead checks -- three note types that got zero
    validation for a year because they were missing from a lookup table nobody re-read.
    """

    def test_every_check_is_proven_to_fire(self):
        import validate as v
        import inspect
        import re

        declared = set()
        for name, fn in vars(v).items():
            if name.startswith("check_") and callable(fn):
                declared |= set(re.findall(r'"(KC\d{3})"', inspect.getsource(fn)))

        untested = declared - GraphCase.asserted
        self.assertEqual(
            set(), untested,
            "these checks are declared but no test proves they fire: %s"
            % sorted(untested))


def load_tests(loader, tests, pattern):
    """Force EveryCheckFires to run last, after every other test has registered its code."""
    suite = unittest.TestSuite()
    classes = [ValidFixtures, Frontmatter, Navigation, Reasoning, Hubs, Schema, Links,
               Ledger, Config, ScopeAndBaseline, EveryCheckFires]
    for cls in classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    return suite


if __name__ == "__main__":
    unittest.main()
