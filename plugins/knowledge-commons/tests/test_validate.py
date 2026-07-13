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

from support import GraphCase, codes, materialize, run_check, run_cli, fixture


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

    def test_KC006_two_notes_could_claim_the_atlas(self):
        """The atlas is the root of the whole reachability invariant, so which note holds the
        role must not depend on the order os.walk happened to yield."""
        root = materialize(adds={"logbook/grove.md":
                                 "---\ntype: atlas\n---\n# Impostor\n"})
        self.assertFires("KC006", run_check(root))

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

    def test_KC022_promoted_below_the_bar(self):
        """The question is `open` on one domain. Flip it to `graduated` and it has been
        promoted on evidence that did not earn it -- which is the whole reason for the bar."""
        root = materialize(base="commons", edits={
            "questions/When is a checklist better than automation.md":
                replace("status: open", "status: graduated")})
        self.assertFires("KC022", run_check(root), severity="warning")

    def test_KC023_staleness(self):
        """`today` is injected, because a check whose result depends on the wall clock is a
        check nobody can prove fires -- and an unprovable check is the whole failure mode
        this suite exists to prevent."""
        findings = run_check(fixture("commons"), today="2027-06-01")
        self.assertFires("KC023", findings, severity="warning")

    def test_KC023_does_not_fire_on_fresh_evidence(self):
        findings = run_check(fixture("commons"), today="2026-08-01")
        self.assertNotIn("KC023", codes(findings))

    def test_the_staleness_cutoff_is_always_a_real_date(self):
        """Naive month arithmetic returned 2027-02-31 for one month before 2027-03-31, and
        the cutoff is compared lexicographically -- so notes dated the 28th or 29th were
        judged stale days early whenever `today` landed on the 29th to the 31st."""
        import datetime
        import validate as v
        for iso, months in [("2027-03-31", 1), ("2027-03-30", 1), ("2026-05-31", 3),
                            ("2028-03-29", 1), ("2027-01-31", 2), ("2027-12-31", 12)]:
            with self.subTest(iso=iso, months=months):
                cutoff = v._months_before(iso, months)
                datetime.date.fromisoformat(cutoff)   # raises if it is not a real date
                self.assertLess(cutoff, iso)


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

    def test_KC018_a_wikilink_may_not_escape_the_graph(self):
        """D9's first layer, and the only one that does not depend on an LLM reading prose.

        Promotion DERIVES a new, self-contained note. It never links across a boundary -- if
        a derived note needs its source to make sense, it has not generalized.
        """
        root = materialize(edits={PATTERN: replace(
            "Site frost-tender varietals uphill",
            "Site frost-tender varietals uphill, see [[../commons/Some principle]]")})
        self.assertFires("KC018", run_check(root))

    def test_KC018_catches_an_absolute_path(self):
        root = materialize(edits={PATTERN: replace(
            "Site frost-tender varietals uphill",
            "Site frost-tender varietals uphill, see [[/etc/passwd]]")})
        self.assertFires("KC018", run_check(root))

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

    def test_a_config_error_is_never_scoped_away(self):
        """Regression, and the worst bug in the first cut of this file.

        A config finding's only path is `.commons.yml`, which no scoped note ever matches, so
        the scope filter removed it -- and a --scope'd run on a graph with a broken config
        printed "0 errors" and exited 0. That is exactly the call `knowledge-graph` makes
        before every write, so the transaction gate would have waved every write through on a
        graph it could not even validate.
        """
        root = materialize(edits={".commons.yml": replace("min-attractors: 1",
                                                          "min-attractors: 0")})
        scoped = run_check(root, scope=[PATTERN])
        self.assertFires("KC102", scoped)
        self.assertTrue(any(f.severity == "error" for f in scoped),
                        "a scoped run on a broken config must still report an error")

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


class ExitCodes(GraphCase):
    """The exit code is the contract. knowledge-graph reads nothing else."""

    def test_valid_graph_exits_zero(self):
        code, _ = run_cli("check", "--graph", fixture("orchard"))
        self.assertEqual(0, code)

    def test_broken_graph_exits_two(self):
        root = materialize(edits={OBS_ROW: drop_line("genitor:")})
        code, _ = run_cli("check", "--graph", root)
        self.assertEqual(2, code)

    def test_a_scoped_run_on_a_broken_config_does_not_exit_zero(self):
        """The regression that mattered: this printed "0 errors" and exited 0."""
        root = materialize(edits={".commons.yml": replace("min-attractors: 1",
                                                          "min-attractors: 0")})
        code, out = run_cli("check", "--graph", root, "--scope", PATTERN)
        self.assertEqual(2, code,
                         "a broken config must never report clean, scoped or not. Got:\n%s" % out)

    def test_a_missing_config_is_fatal_and_not_clean(self):
        root = materialize(deletes=[".commons.yml"])
        code, _ = run_cli("check", "--graph", root)
        self.assertEqual(1, code)

    def test_baseline_pins_today_so_a_later_check_agrees_with_it(self):
        """A time-dependent check not pinned on both sides manufactures phantom NEW findings.

        Asserted on the JSON, not the prose: an earlier version of this test grepped stdout
        for "NEW" and matched the summary line "0 NEW errors vs baseline", so it failed
        against a working fix.
        """
        import json
        import tempfile
        out = os.path.join(tempfile.mkdtemp(), "base.json")
        code, _ = run_cli("baseline", "--graph", fixture("commons"),
                          "--out", out, "--today", "2028-01-01")
        self.assertEqual(0, code)

        with open(out) as fh:
            self.assertEqual("2028-01-01", json.load(fh)["today"],
                             "the baseline must record the date it was taken against")

        # No --today here: it must be inherited from the baseline, not re-read from the clock.
        code, text = run_cli("check", "--graph", fixture("commons"), "--baseline", out,
                             "--format", "json")
        self.assertEqual(0, code)
        payload = json.loads(text)
        phantom = [f["check"] for f in payload["findings"] if f["new"]]
        self.assertEqual([], phantom,
                         "nothing was edited, so nothing may be NEW. These findings appeared "
                         "only because the baseline and the check disagreed about `today`: %s"
                         % phantom)


class ColdReviewRegressions(GraphCase):
    """Bugs an independent reviewer found that this suite was blind to.

    Every one of them lived outside what the fixtures exercise. That is the whole lesson: a
    green suite proves the paths it walks, and nothing else.
    """

    def test_a_config_error_is_never_excused_by_a_baseline(self):
        """The --scope hole, through a different door, and worse.

        A pre-existing config error is IN the baseline, so it is "not new", so exit 0 -- while
        cmd_check ran NO graph check at all. Deleting an attractor two notes depend on (five
        real errors) was waved straight through.
        """
        import tempfile
        root = materialize(edits={".commons.yml": replace("min-attractors: 1",
                                                          "min-attractors: 0")})
        out = os.path.join(tempfile.mkdtemp(), "base.json")
        run_cli("baseline", "--graph", root, "--out", out)

        os.remove(os.path.join(root, PATTERN))       # wreck the graph
        code, text = run_cli("check", "--graph", root, "--baseline", out)
        self.assertEqual(2, code,
                         "a graph whose config cannot be validated is NEVER safe to write to, "
                         "baseline or no baseline. Got:\n%s" % text)

    def test_an_unquoted_genitor_wikilink_does_not_disable_genitor_checking(self):
        """`genitor: [[X]]` is valid YAML for a NESTED LIST, not a string.

        _fm_links skipped non-strings, so it returned nothing; check_genitor saw a truthy raw
        value (so KC003 stayed quiet) and then `continue`d past KC004 and KC005. A note could
        name a genitor that does not exist and the graph validated completely clean.
        """
        root = materialize(edits={OBS_ROW: replace('genitor: "[[observations]]"',
                                                   "genitor: [[Totally Nonexistent Map]]")})
        findings = run_check(root)
        self.assertTrue(any(f.severity == "error" for f in findings),
                        "an unresolvable genitor must never validate clean, quoted or not")
        self.assertFires("KC004", findings)

    def test_an_unquoted_genitor_still_resolves_when_it_is_valid(self):
        root = materialize(edits={OBS_ROW: replace('genitor: "[[observations]]"',
                                                   "genitor: [[observations]]")})
        self.assertClean(run_check(root))

    def test_KC018_honours_a_custom_parent_field(self):
        """It hardcoded "genitor", so the identical boundary breach went unreported under a
        configured parent-field -- the hardcoded-lookup-table failure this file is written
        against."""
        root = materialize(edits={
            ".commons.yml": lambda t: t.replace("parent-field: genitor",
                                                "parent-field: parent"),
            OBS_ROW: replace('genitor: "[[observations]]"',
                             'parent: "[[../commons/observations]]"')})
        self.assertFires("KC018", run_check(root))

    def test_KC017_resolves_wikilinks_in_arbitrary_frontmatter_fields(self):
        """_lateral_links counts them as graph edges; nothing resolved them unless the field
        happened to have a dedicated check."""
        root = materialize(edits={OBS_ROW: replace(
            "type: observation",
            'type: observation\nrelated: "[[No Such Note At All]]"')})
        self.assertFires("KC017", run_check(root))

    def test_a_non_utf8_note_is_a_finding_not_a_traceback(self):
        """_read_note promises "never an exception"; the open() sat outside the try."""
        root = materialize()
        with open(os.path.join(root, "observations", "Latin1.md"), "wb") as fh:
            fh.write(b"---\ntype: observation\n---\ncaf\xe9\n")
        code, text = run_cli("check", "--graph", root)
        self.assertEqual(2, code)
        self.assertNotIn("Traceback", text)
        self.assertIn("KC001", text)

    def test_an_unreadable_baseline_is_fatal_not_empty(self):
        """Treating it as empty would mark every finding NEW -- or look clean."""
        code, text = run_cli("check", "--graph", fixture("orchard"),
                             "--baseline", "/nonexistent/nope.json")
        self.assertEqual(1, code)
        self.assertNotIn("Traceback", text)

    def test_severity_labels_are_not_truncated(self):
        code, text = run_cli("check", "--graph", fixture("commons"))
        self.assertNotIn("WARNI ", text)
        self.assertIn("WARNING", text)


class IndexRendering(GraphCase):
    """The index had NO test at all.

    That gap let a NameError ship in `render_index` while all 97 other tests stayed green --
    the exact failure this whole branch is about, committed by the person writing the branch
    about it. A green suite proves the paths it walks and says nothing about the rest.
    """

    def test_index_renders(self):
        code, text = run_cli("index", "--graph", fixture("commons"))
        self.assertEqual(0, code, "index crashed:\n%s" % text)
        self.assertIn("# Index", text)

    def test_index_lists_attractors_and_not_evidence(self):
        _code, text = run_cli("index", "--graph", fixture("commons"))
        self.assertIn("Execution beats review for validating a guard", text)
        self.assertIn("When is a checklist better than automation", text)
        # claims are evidence; they never appear in the index
        self.assertNotIn("Executing a config caught an error", text)

    def test_index_renders_the_so_what_and_the_domains(self):
        _code, text = run_cli("index", "--graph", fixture("commons"))
        self.assertIn("Run the artifact against a deliberately-broken input", text)
        self.assertIn("[orchard, workshop]", text)

    def test_index_flags_come_from_the_checks(self):
        """The flags and the checks must not be able to disagree."""
        _code, text = run_cli("index", "--graph", fixture("commons"))
        self.assertIn("graduation-pending", text)

    def test_every_index_flag_names_a_real_check(self):
        """An index flag keyed on a code no check emits would print a flag nothing can produce."""
        import validate as v
        import inspect
        import re
        emitted = set(re.findall(r'Finding\(\s*"(KC\d{3})"', inspect.getsource(v)))
        unknown = set(v.INDEX_FLAGS) - emitted
        self.assertEqual(set(), unknown,
                         "INDEX_FLAGS names codes no check emits: %s" % sorted(unknown))

    def test_the_index_and_KC034_agree_about_whether_a_section_exists(self):
        """They did not. `_first_prose` ignored heading depth, so KC034 reported "no
        '## so what' section" while the index happily rendered a so-what from a `###`."""
        root = materialize(edits={PATTERN: replace("## so what", "### so what")})
        findings = run_check(root)
        self.assertFires("KC034", findings, severity="warning")
        _code, text = run_cli("index", "--graph", root)
        self.assertNotIn("Site frost-tender varietals uphill", text,
                         "the index rendered a so-what from a section KC034 says is absent")


class Round3Regressions(GraphCase):
    """A third independent review, after the simplification pass. All five were real."""

    def test_a_source_artifact_is_not_a_note(self):
        """The worst one, and no test could have caught it: the fixtures ship an EMPTY source
        tier.

        `sources[].path` names RAW material -- a chronicle, a transcript, no frontmatter. The
        walker ingested it as a note, so every source artifact became a KC001 "no frontmatter"
        ERROR. A feeder graph whose source tier actually had anything in it could never
        validate, and since the write gate refuses on any error, could never be written to
        again. The whole point of the queue entry mode is that those files EXIST.
        """
        root = materialize(adds={
            "logbook-source/2026-03-14.md":
                "# 2026-03-14\n\n## 09:15\nWalked the north plot.\n\n## 14:30\nBlossom damage.\n"})
        findings = run_check(root)
        self.assertEqual([], [f for f in findings if f.severity == "error"],
                         "a raw source artifact must not be validated as a note: %s"
                         % [(f.check, f.locus()) for f in findings])

    def test_the_source_artifact_is_still_scanned_for_event_collisions(self):
        """Excluded from the NOTE walk, but --source-scan must still read it."""
        root = materialize(adds={
            "logbook-source/2026-05-01.md":
                "# 2026-05-01\n\n## 09:20 Walk\nFirst.\n\n## 09:20 Walk\nSecond.\n"})
        self.assertFires("KC028", run_check(root, source_scan=True))

    def test_KC023_is_emitted_once_per_attractor(self):
        """A regression the refactor introduced: _check_staleness was hoisted out of
        _check_graduation and called from check_lifecycle, but the ORIGINAL call was never
        deleted. KC023 fired twice for every attractor, the summary double-counted, and the
        baseline stored duplicate fingerprints -- and 103 tests stayed green, because nothing
        asserted a finding COUNT."""
        findings = run_check(fixture("commons"), today="2030-01-01")
        stale = [f for f in findings if f.check == "KC023"]
        self.assertEqual(2, len(stale),
                         "expected one KC023 per attractor, got %d: %s"
                         % (len(stale), [f.locus() for f in stale]))

    def test_no_finding_is_emitted_twice(self):
        """The general form of the above. A duplicate finding inflates the summary and puts
        duplicate fingerprints in the baseline."""
        for name, today in (("orchard", None), ("commons", "2030-01-01")):
            with self.subTest(graph=name):
                findings = run_check(fixture(name), today=today)
                prints = [f.fingerprint() for f in findings]
                dupes = {p for p in prints if prints.count(p) > 1}
                self.assertEqual(set(), dupes,
                                 "%d duplicate findings" % len(dupes))

    def test_an_owned_field_on_the_wrong_type_is_still_resolved(self):
        """Field ownership is TYPE-SCOPED, because the owning checks are.

        `check_evidence` resolves `supports:` only on the evidence type; the hub reverse-loop
        resolves a hub field only on the attractor it is bound to. Global ownership meant a
        `practice` carrying `supports:` had that link excluded from KC017 as somebody else's
        job, while nobody scanned it -- dangling, silently, forever.
        """
        root = materialize(edits={PRACTICE: replace(
            'genitor: "[[practices]]"',
            'genitor: "[[practices]]"\n'
            'supports: "[[No Such Attractor At All]]"\n'
            'plots: "[[No Such Plot Whatsoever]]"')})
        findings = run_check(root)
        unresolved = {f.key for f in findings if f.check == "KC017"}
        self.assertIn("No Such Attractor At All", unresolved)
        self.assertIn("No Such Plot Whatsoever", unresolved)

    def test_KC101_a_non_mapping_config_block(self):
        """check_config exists to turn config mistakes into findings; it may not crash on one."""
        for bad in ("graph: hello\ntypes: {}\n", "graph:\n  - a\n  - b\ntypes: {}\n"):
            with self.subTest(config=bad.split("\n")[0]):
                root = materialize(edits={".commons.yml": lambda _t, b=bad: b})
                self.assertFires("KC101", run_check(root))
                code, text = run_cli("check", "--graph", root)
                self.assertNotIn("Traceback", text)
                self.assertEqual(2, code)

    def test_the_index_renders_prose_not_a_sub_heading(self):
        """_section_lines rightly includes deeper headings (a link under a sub-heading is
        still under the section), but a heading is not prose, and index.md is generated."""
        root = materialize(edits={PATTERN: replace("## so what\n", "## so what\n### summary\n")})
        _code, text = run_cli("index", "--graph", root)
        self.assertNotIn("### summary", text)
        self.assertIn("Site frost-tender varietals uphill", text)


class Round4Regressions(GraphCase):
    """A GitHub review, done STATICALLY (its sandbox had no Bash). Every claim held up when
    executed -- including the one it flagged as unverified."""

    def test_a_malformed_today_is_a_clean_fatal_not_a_traceback(self):
        """--today is an unchecked argparse string that flowed straight into int() arithmetic.
        This is the call the write gate makes; a traceback on stdout is what the {fatal:...}
        contract exists to prevent."""
        for bad in ("notadate", "2026-02-31", "26-1-1", ""):
            with self.subTest(today=bad):
                code, text = run_cli("check", "--graph", fixture("commons"), "--today", bad)
                self.assertNotIn("Traceback", text)
                self.assertEqual(1, code)

    def test_a_malformed_today_is_fatal_in_json_too(self):
        import json
        code, text = run_cli("check", "--graph", fixture("commons"),
                             "--today", "notadate", "--format", "json")
        self.assertEqual(1, code)
        self.assertIn("fatal", json.loads(text))

    def test_a_corrupted_baseline_date_is_a_clean_fatal(self):
        """The baseline's `today` comes off disk and could be anything."""
        import json
        import tempfile
        out = os.path.join(tempfile.mkdtemp(), "b.json")
        run_cli("baseline", "--graph", fixture("commons"), "--out", out)
        with open(out) as fh:
            payload = json.load(fh)
        payload["today"] = "garbage"
        with open(out, "w") as fh:
            json.dump(payload, fh)
        code, text = run_cli("check", "--graph", fixture("commons"), "--baseline", out)
        self.assertNotIn("Traceback", text)
        self.assertEqual(1, code)

    def test_a_valid_today_still_works(self):
        code, _text = run_cli("check", "--graph", fixture("commons"), "--today", "2030-01-01")
        self.assertEqual(0, code)


class EveryCheckFires(GraphCase):
    """The load-bearing test.

    A check with no firing test is indistinguishable from a check that always passes. This is
    what makes 'every check is proven to fire' mechanical instead of aspirational, and it is
    the direct answer to the reference's dead checks -- three note types that got zero
    validation for a year because they were missing from a lookup table nobody re-read.
    """

    def test_every_check_is_proven_to_fire(self):
        """Every code MENTIONED anywhere in the validator must have a test that fires it.

        This deliberately greps the whole module, docstrings included -- not just quoted
        strings. The first version of this test only looked for `"KC0xx"` in quotes, i.e.
        codes actually emitted, and so it could not see a check that was *named and never
        implemented*. Two were: KC018 (a wikilink escaping the graph -- the boundary's only
        mechanical layer) and KC023 (staleness, which was even rendered in the index's flag
        vocabulary). Both were caught by reading the docs against the code, not by this test.

        A check that is documented but unimplemented is worse than a missing one: the clean
        run tells you it passed.
        """
        import validate as v
        import inspect
        import re

        source = inspect.getsource(v)
        mentioned = set(re.findall(r"\bKC\d{3}\b", source))
        untested = mentioned - GraphCase.asserted
        self.assertEqual(
            set(), untested,
            "mentioned in validate.py but no test proves they fire: %s. Either write a test, "
            "or delete the mention -- a check named and never fired is indistinguishable "
            "from a check that always passes." % sorted(untested))


def load_tests(loader, tests, pattern):
    """Force EveryCheckFires to run last, after every other test has registered its code."""
    suite = unittest.TestSuite()
    classes = [ValidFixtures, Frontmatter, Navigation, Reasoning, Hubs, Schema, Links,
               Ledger, Config, ScopeAndBaseline, ExitCodes, ColdReviewRegressions,
               IndexRendering, Round3Regressions, Round4Regressions,
               EveryCheckFires]
    for cls in classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    return suite


if __name__ == "__main__":
    unittest.main()
