from typing import Optional, Type, Union

__all__ = ("Colors",)

class Colors:
    r"""Represents the class used for normal strings to Discord ANSI Codeblocks that support colors.

    Usage
    ----------------
    from discord.colorize import Colors
    colors = Colors()
    message = colors.colorize('Hello World!', fg='green', 'bg'='indigo', 'bold'=True)

    All Colors
    ----------------
    Foreground -
    ・gray - 30
    ・red - 31
    ・green - 32
    ・yellow - 33
    ・blue - 34
    ・pink - 35
    ・cyan - 36
    ・white - 37
    Background -
    ・darkBlue - 40
    ・orange - 41
    ・gray - 46
    ・lightGray - 43
    ・lighterGray - 44
    ・indigo - 45
    ・white - 47
    Formatting -
    ・bold - 1
    ・underline - 4
    ・default - 0

    Both the names of colors and styles (bold, gray, darkBlue, etc), and their integer equivalents (1, 30, 40) are accepted as valid inputs for colorization. Color names are not case-sensitive.
    """

    class unknownColor(Exception):
        """The unknown color class, this exception is raised when a color is not found."""

        def __init__(self, unknownColor: Union[int, str]):
            """Initializes the unknown color exception."""
            self.color = unknownColor

        def __str__(self):
            """Returns the string representation of the exception."""

            return f"Unknown color: {self.color}"

    def __init__(self):
        """Initializes the Colors class."""
        self.foregroundColors = {
            "gray": "30",
            "red": "31",
            "green": "32",
            "yellow": "33",
            "blue": "34",
            "pink": "35",
            "cyan": "36",
            "white": "37",
            "default": "0",
        }
        self.backgroundColors = {
            "darkblue": "40",
            "orange": "41",
            "gray": "46",
            "lightgray": "43",
            "lightergray": "44",
            "indigo": "45",
            "white": "47",
            "default": "0",
        }
        self.formatCodes = {"bold": "1", "underline": "4", "default": "0"}
        self.allFormatCodes = [1, 4]

    def returnColor(self, color: str, kind: str) -> int:
        """Returns the color code for the given color.

        Args:
            color (str): The color to return the code for.
            kind (str): The kind of color to return.

        Raises:
            self.unknownColor: Raised when the color is not found.

        Returns:
            int: The color code.
        """
        if type(color) is not str:
            return None
        if kind == "fg":
            try:
                return self.foregroundColors[color.lower()]
            except KeyError:
                raise self.unknownColor(color)
        elif kind == "bg":
            try:
                return self.backgroundColors[color.lower()]
            except KeyError:
                raise self.unknownColor(color)

    def colorize(
        self,
        text: str,
        bg: Union[str, int] = 0,
        fg: Union[str, int] = 0,
        bold: bool = 0,
        underline: bool = 0,
    ) -> str:
        """Returns a string with the ANSI color codes for the given parameters.

        Args:
            text (str): The text to colorize.
            bg (Union[str, int], optional): The background color to use. Defaults to no background.
            fg (Union[str, int], optional): The foreground color to use. Defaults to no foreground.
            bold (bool, optional): Whether or not to use bold. Defaults to no bold.
            underline (bool, optional): Whether or not to use underline. Defaults to no underline.

        Returns:
            str: The colorized string.
        """
        if bg is not None:
            if type(bg) is str:
                bg = self.returnColor(bg, "bg")
            elif type(bg) is int:
                if str(bg) not in self.backgroundColors.values():
                    raise self.unknownColor(bg)
            else:
                return TypeError("Argument 'bg' must be of type 'str' or 'int'.")
        if fg is not None:
            if type(fg) is str:
                fg = self.returnColor(fg, "fg")
            elif type(fg) is int:
                if str(fg) not in self.foregroundColors.values():
                    raise self.unknownColor(fg)
            else:
                raise TypeError("Argument 'fg' must be of type 'str' or 'int'.")
        if bold:
            bold = self.formatCodes["bold"]
        if underline:
            underline = self.formatCodes["underline"]
        return (
            f"[{bold};{underline};{fg};{bg};m{text}".replace("0;", "")
            .replace("0m", "m")
            .replace(";m", "m")
            .replace(";0;", ";")
            .replace("[0;", "[")
            + "[0m"
        )
