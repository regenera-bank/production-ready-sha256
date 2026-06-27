from html.parser import HTMLParser

class _AuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.images_without_alt = 0
        self.inputs_without_name = 0
        self.buttons = 0
        self.unnamed_buttons = 0
        self._button_text: list[str] = []
        self._in_button = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "img" and not values.get("alt"):
            self.images_without_alt += 1
        if tag == "input" and not (values.get("aria-label") or values.get("id") or values.get("name")):
            self.inputs_without_name += 1
        if tag == "button":
            self.buttons += 1
            self._in_button = True
            self._button_text = []
            if values.get("aria-label"):
                self._button_text.append(values["aria-label"] or "")

    def handle_data(self, data: str) -> None:
        if self._in_button:
            self._button_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "button" and self._in_button:
            if not "".join(self._button_text).strip():
                self.unnamed_buttons += 1
            self._in_button = False


def audit_html(html: str) -> dict[str, int]:
    parser = _AuditParser()
    parser.feed(html)
    return {
        "images_without_alt": parser.images_without_alt,
        "inputs_without_name": parser.inputs_without_name,
        "unnamed_buttons": parser.unnamed_buttons,
    }
