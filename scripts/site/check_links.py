"""Offline crawler for the actual built HTML, including clean URLs and anchors."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.ids = set()
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'): self.ids.add(attrs['id'])
        if tag == 'a' and attrs.get('name'): self.ids.add(attrs['name'])
        if tag in ('a', 'link') and attrs.get('href'): self.links.append(attrs['href'])
        if tag in ('script', 'img', 'source', 'iframe') and attrs.get('src'): self.links.append(attrs['src'])

def check(root, base):
    pages = {p: Page(p.read_text()) for p in root.rglob('*.html')}
    errors = set()
    checked = 0
    for file, page in pages.items():
        current = 'https://local.invalid' + base + file.relative_to(root).as_posix()
        for link in page.links:
            url = urlsplit(urljoin(current, link))
            if url.netloc != 'local.invalid' or url.scheme not in ('http', 'https'): continue
            path = unquote(url.path)
            if not path.startswith(base):
                errors.add(f'{file.relative_to(root)}: path escapes base: {link}'); continue
            rel = path[len(base):]
            path = root / rel
            candidates = [path, Path(str(path) + '.html'), path / 'index.html']
            target = next((p for p in candidates if p.is_file()), None)
            if target is None:
                errors.add(f'{file.relative_to(root)}: missing {link}'); continue
            checked += 1
            fragment = unquote(url.fragment)
            if fragment and target in pages and not fragment.startswith('paper=') and fragment not in pages[target].ids:
                # Redirect stubs preserve anchors for the destination page.
                if 'location.replace(' not in target.read_text(): errors.add(f'{file.relative_to(root)}: missing anchor {link}')
    return checked, sorted(errors)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    parser.add_argument('--base', default='/')
    args = parser.parse_args()
    count, errors = check(Path(args.directory).resolve(), args.base)
    print(f'Checked {count} internal links; {len(errors)} errors')
    for error in errors: print(error)
    raise SystemExit(bool(errors))
