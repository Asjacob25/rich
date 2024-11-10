import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from unittest.mock import patch

from rich.color import Color, ColorParseError, ColorSystem, ColorType, ColorTriplet, blend_rgb, parse_rgb_hex
from rich.terminal_theme import TerminalTheme


@pytest.fixture
def default_terminal_theme():
    """Provides a default terminal theme fixture."""
    return TerminalTheme(
        foreground_color=ColorTriplet(255, 255, 255),
        background_color=ColorTriplet(0, 0, 0),
        ansi_colors=[ColorTriplet(i, i, i) for i in range(16)]
    )


class TestColor:
    def test_parse_valid_standard_color(self):
        """Test parsing a valid standard color name."""
        color = Color.parse("red")
        assert color.name == "red"
        assert color.type == ColorType.STANDARD
        assert color.number == 1

    def test_parse_valid_hex_color(self):
        """Test parsing a valid hex color."""
        color = Color.parse("#ff0000")
        assert color.name == "#ff0000"
        assert color.type == ColorType.TRUECOLOR
        assert color.triplet == ColorTriplet(255, 0, 0)

    def test_parse_invalid_color_raises_error(self):
        """Test parsing an invalid color raises ColorParseError."""
        with pytest.raises(ColorParseError):
            Color.parse("not_a_color")

    def test_from_ansi(self):
        """Test creating a color from an ANSI code."""
        color = Color.from_ansi(90)
        assert color.type in (ColorType.STANDARD, ColorType.EIGHT_BIT)
        assert color.number == 90

    def test_from_triplet(self):
        """Test creating a color from a color triplet."""
        triplet = ColorTriplet(100, 150, 200)
        color = Color.from_triplet(triplet)
        assert color.type == ColorType.TRUECOLOR
        assert color.triplet == triplet

    def test_from_rgb(self):
        """Test creating a color from RGB values."""
        color = Color.from_rgb(100, 150, 200)
        assert color.type == ColorType.TRUECOLOR
        assert color.triplet == ColorTriplet(100, 150, 200)

    def test_default_color(self):
        """Test getting the default color."""
        color = Color.default()
        assert color.name == "default"
        assert color.type == ColorType.DEFAULT

    @patch('rich.color.DEFAULT_TERMINAL_THEME', new_callable=lambda: default_terminal_theme())
    def test_get_truecolor_with_default_theme(self, mock_theme):
        """Test getting the truecolor of a color with the default terminal theme."""
        color = Color.parse("red").get_truecolor()
        assert isinstance(color, ColorTriplet)

    def test_color_system_conversion(self):
        """Test conversion of color to a specified color system."""
        color = Color.parse("#ff0000")
        downgraded = color.downgrade(ColorSystem.EIGHT_BIT)
        assert downgraded.type == ColorType.EIGHT_BIT
        assert downgraded.number is not None

    def test_get_ansi_codes_for_truecolor(self):
        """Test getting ANSI codes for a truecolor."""
        color = Color.from_rgb(255, 0, 0)
        codes = color.get_ansi_codes()
        assert "38" in codes
        assert "255" in codes
        assert "0" in codes


class TestColorFunctions:
    def test_parse_rgb_hex_valid(self):
        """Test parsing a valid RGB hex string."""
        triplet = parse_rgb_hex("abcdef")
        assert triplet == ColorTriplet(171, 205, 239)

    def test_parse_rgb_hex_invalid_length_raises_error(self):
        """Test parsing an RGB hex string of invalid length raises AssertionError."""
        with pytest.raises(AssertionError):
            parse_rgb_hex("abc")

    def test_blend_rgb_midpoint(self):
        """Test blending two RGB colors at the midpoint."""
        color1 = ColorTriplet(10, 20, 30)
        color2 = ColorTriplet(20, 40, 60)
        blended = blend_rgb(color1, color2, 0.5)
        assert blended == ColorTriplet(15, 30, 45)

    def test_blend_rgb_full_crossfade(self):
        """Test blending two RGB colors with full crossfade to the second color."""
        color1 = ColorTriplet(0, 0, 0)
        color2 = ColorTriplet(255, 255, 255)
        blended = blend_rgb(color1, color2, 1.0)
        assert blended == color2