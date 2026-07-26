"""Design token hygiene.

The stylesheet is the whole design system, so these check the things a reviewer
would otherwise have to hold in their head: that every token referenced actually
exists, that none linger unused, and that font sizes come from the scale rather
than being written inline.
"""

import re
from pathlib import Path

CSS = Path("blog/static/styles/main.css")
TEMPLATES = sorted(Path("blog/templates").rglob("*.html"))


def stylesheet() -> str:
    return CSS.read_text()


def markup() -> str:
    return "".join(p.read_text() for p in TEMPLATES)


def declared(prefix: str, css: str) -> set[str]:
    return set(re.findall(rf"^\s*({re.escape(prefix)}[a-z0-9-]+):", css, re.M))


def used(prefix: str, text: str) -> set[str]:
    return set(re.findall(rf"var\(({re.escape(prefix)}[a-z0-9-]+)\)", text))


def test_every_token_used_is_declared():
    """A typo in a var() name fails silently — the property is just dropped."""
    css = stylesheet()
    everything = css + markup()

    missing = sorted(used("--", everything) - declared("--", css))
    assert not missing, f"referenced but never declared: {missing}"


def test_no_token_is_declared_and_never_used():
    css = stylesheet()
    everything = css + markup()

    # Palette halves are referenced only through the theme assignments, which the
    # regex above does catch, so nothing needs excluding here.
    unused = sorted(declared("--", css) - used("--", everything))
    assert not unused, f"declared but never used: {unused}"


def test_no_component_names_a_literal_colour():
    """Colours belong to the palette, not to the rules that use them.

    A component that hardcodes a hex value cannot follow the theme, so every
    literal must sit on a line declaring a `--color-light-*`, `--color-dark-*` or
    `--shadow-panel-*` palette value. That
    is what lets light and dark work with no per-component branching.
    """
    offenders = []
    for number, line in enumerate(stylesheet().splitlines(), 1):
        if not re.search(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(", line):
            continue
        if not re.match(r"\s*--(color-(light|dark)|shadow-panel)-", line):
            offenders.append(f"{number}: {line.strip()}")

    assert not offenders, "colour literals outside the palette:\n" + "\n".join(offenders)


def test_templates_do_not_hardcode_colours():
    for path in TEMPLATES:
        for style in re.findall(r'style="([^"]*)"', path.read_text()):
            assert not re.search(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(", style), f"{path}: {style}"


def test_type_scale_is_named_by_role():
    """Positional names (--step-2) mean renumbering every use to insert a size."""
    css = stylesheet()
    assert not re.search(r"--step-{1,2}\d", css.replace("`--step--2`", "")), (
        "the type scale should use role names, not numbered steps"
    )

    scale = declared("--text-", css)
    assert scale == {
        "--text-label",
        "--text-caption",
        "--text-body",
        "--text-body-lg",
        "--text-heading-sm",
        "--text-heading",
        "--text-heading-lg",
    }


def test_token_names_follow_one_pattern():
    """The point of the rename: no ad-hoc modifiers left.

    Type is `--text-<role>` with an optional -sm/-lg tier. Colour modifiers come
    from one vocabulary. A bare numeric suffix (`--color-surface-2`) carries no
    meaning, so it is not allowed.
    """
    css = stylesheet()

    roles = {
        n.removeprefix("--text-").removesuffix("-sm").removesuffix("-lg")
        for n in declared("--text-", css)
    }
    assert roles == {"label", "caption", "body", "heading"}, roles

    allowed = {"", "muted", "subtle", "strong", "sunken"}
    for token in declared("--color-", css):
        name = re.sub(r"^--color-(light-|dark-)?", "", token)
        base, _, modifier = name.rpartition("-")
        if not base:  # single-word name, no modifier
            continue
        assert modifier in allowed, f"{token}: unknown modifier {modifier!r}"
        assert not modifier.isdigit(), f"{token}: bare numeric suffix"


def test_type_scale_ascends_in_declaration_order():
    """Reading the block top to bottom should also read smallest to largest."""
    css = stylesheet()
    sizes = [
        (name, float(value))
        for name, value in re.findall(r"^\s*(--text-[a-z-]+):\s*([\d.]+)rem;", css, re.M)
    ]
    assert len(sizes) == 7
    values = [value for _, value in sizes]
    assert values == sorted(values), f"out of order: {sizes}"


def test_font_sizes_come_from_the_scale():
    """Ad-hoc sizes are how a scale quietly stops being one."""
    css = stylesheet()

    # Filtering in Python rather than with a negative lookahead: `\s*(?!var\()`
    # backtracks to match zero whitespace and then tests the space, so every
    # value slips through.
    values = [value.strip() for value in re.findall(r"font-size:\s*([^;]+);", css)]
    assert values, "no font-size declarations found"

    # `em` values are relative to their context by design (icons, code, prose
    # descendants); only absolute units would be bypassing the scale.
    offenders = [
        value
        for value in values
        if not value.startswith("var(--text-") and not value.endswith("em")
    ]
    assert not offenders, f"font sizes outside the scale: {offenders}"


def test_templates_do_not_hardcode_font_sizes():
    for path in TEMPLATES:
        for match in re.findall(r'style="([^"]*)"', path.read_text()):
            if "font-size" in match:
                assert "var(--text-" in match, f"{path}: {match}"
