import sys, os, json, random, re, shutil, math
from PySide6.QtCore import (Qt, QUrl, QThread, Signal, QSettings, QSize, QRect, QRectF, QPointF, QTimer,
                            QObject, QEvent, QPropertyAnimation, QEasingCurve, QAbstractAnimation,
                            QVariantAnimation)
from PySide6.QtGui import (QPixmap, QImage, QIcon, QPainter, QPainterPath, QColor, QPen, QPolygonF,
                           QFont, QShortcut, QKeySequence, QCursor, QLinearGradient, QBrush)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QPushButton, QSlider, QLineEdit, QFileDialog, QAbstractItemView, QFrame, QMenu,
    QInputDialog, QScrollArea, QStyledItemDelegate, QStyle, QGraphicsOpacityEffect,
    QPlainTextEdit, QComboBox, QCheckBox, QProgressBar)
from mutagen import File as MFile

APP = 'MigsMusic'
EXTS = ('.mp3', '.m4a', '.flac', '.ogg', '.opus', '.wav', '.wma', '.aac')
BLUE = '#0a84ff'
GRAY = '#9a9a9a'
WHITE = '#f2f2f2'

QSS = f"""
* {{ font-family: 'Segoe UI', sans-serif; color: {WHITE}; }}
QMainWindow, QWidget#root {{ background: #1c1c1c; }}
QFrame#top, QWidget#sidebar {{ background: #1c1c1c; }}
QFrame#top {{ border-bottom: 1px solid #2b2b2b; }}
QFrame#head {{ border-bottom: 1px solid #2b2b2b; background: #202020; }}
QStackedWidget {{ background: #202020; }}
QLineEdit {{ background: #2b2b2b; border: 1px solid #333; border-radius: 6px; padding: 7px 10px; }}
QListWidget#side {{ background: #1c1c1c; border: 0; outline: 0; }}
QListWidget#alist {{ background: #202020; border: 0; font-size: 14px; outline: 0; }}
QListWidget#alist::item {{ padding: 6px 8px; border-left: 3px solid transparent; border-radius: 6px; margin: 1px 4px; }}
QListWidget#alist::item:hover {{ background: #2a2a2a; }}
QListWidget#alist::item:selected {{ background: #2b2b2b; border-left: 3px solid {BLUE}; }}
QListWidget#grid {{ background: #202020; border: 0; outline: 0; }}
QTableWidget {{ background: #202020; border: 0; font-size: 13px; outline: 0; alternate-background-color: #242424; }}
QTableWidget::item {{ padding: 6px; }}
QTableWidget::item:selected {{ background: #3a3a3c; }}
QHeaderView::section {{ background: #202020; color: {GRAY}; border: 0; border-bottom: 1px solid #333; padding: 6px; }}
QScrollArea {{ border: 0; background: #202020; }}
QScrollArea > QWidget {{ background: #202020; }}
QWidget#page {{ background: #202020; }}
QScrollArea > QWidget > QWidget {{ background: #202020; }}
QPushButton {{ background: transparent; border: 0; padding: 6px 8px; border-radius: 6px; }}
QPushButton:hover {{ background: #333; }}
QPushButton#circ {{ background: #2e2e2e; border-radius: 18px; min-width: 36px; max-width: 36px; min-height: 36px; max-height: 36px; padding: 0; }}
QPushButton#circ:hover, QPushButton#pill:hover {{ background: #3a3a3a; }}
QPushButton#pill {{ background: #2e2e2e; border-radius: 18px; min-height: 36px; padding: 0 18px; font-weight: 700; font-size: 14px; }}
QPushButton#alink {{ color: {BLUE}; font-size: 24px; font-weight: 600; text-align: left; padding: 0; }}
QPushButton#alink:hover {{ background: transparent; color: #4da3ff; }}
QFrame#now {{ background: #2a2a2a; border: 1px solid #333; border-radius: 4px; }}
QSlider::groove:horizontal {{ height: 3px; background: #4a4a4a; }}
QSlider::sub-page:horizontal {{ background: #cfcfcf; }}
QSlider::handle:horizontal {{ width: 0px; }}
QSlider#vol::handle:horizontal {{ width: 8px; height: 8px; margin: -3px 0; border-radius: 4px; background: #fff; }}
QScrollBar:vertical {{ background: transparent; width: 10px; }}
QScrollBar::handle:vertical {{ background: #484848; border-radius: 5px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QPlainTextEdit {{ background: #2b2b2b; border: 1px solid #333; border-radius: 8px; padding: 8px; font-size: 13px; }}
QComboBox {{ background: #2b2b2b; border: 1px solid #333; border-radius: 6px; padding: 6px 10px; min-width: 80px; }}
QComboBox QAbstractItemView {{ background: #2b2b2b; selection-background-color: {BLUE}; border: 1px solid #3a3a3a; }}
QProgressBar {{ background: #2b2b2b; border: 0; border-radius: 3px; max-height: 6px; min-height: 6px; }}
QProgressBar::chunk {{ background: {BLUE}; border-radius: 3px; }}
QMenu {{ background: #2b2b2b; border: 1px solid #3a3a3a; padding: 4px; }}
QMenu::item {{ padding: 6px 20px; border-radius: 4px; }}
QMenu::item:selected {{ background: {BLUE}; }}
"""

# ====================== ÍCONES DESENHADOS (vetoriais) ======================


def svgpath(d):
    t = d.split()
    i = 0
    p = QPainterPath()
    cx = cy = 0.0
    nargs = {'M': 2, 'L': 2, 'Q': 4, 'C': 6, 'H': 1, 'V': 1, 'Z': 0}
    while i < len(t):
        c = t[i]
        i += 1
        a = [float(x) for x in t[i:i + nargs[c]]]
        i += nargs[c]
        if c == 'M':
            p.moveTo(*a); cx, cy = a
        elif c == 'L':
            p.lineTo(*a); cx, cy = a
        elif c == 'H':
            p.lineTo(a[0], cy); cx = a[0]
        elif c == 'V':
            p.lineTo(cx, a[0]); cy = a[0]
        elif c == 'Q':
            p.quadTo(*a); cx, cy = a[2], a[3]
        elif c == 'C':
            p.cubicTo(*a); cx, cy = a[4], a[5]
        else:
            p.closeSubpath()
    return p


def _pen(p, c, w=8):
    pn = QPen(QColor(c), w)
    pn.setCapStyle(Qt.RoundCap)
    pn.setJoinStyle(Qt.RoundJoin)
    p.setPen(pn)
    p.setBrush(Qt.NoBrush)


def _fill(p, c, w=0):
    pn = QPen(QColor(c), w) if w else QPen(Qt.NoPen)
    pn.setJoinStyle(Qt.RoundJoin)
    p.setPen(pn)
    p.setBrush(QColor(c))


def _star_d():
    pts = []
    for i in range(10):
        r = 44 if i % 2 == 0 else 19
        a = -math.pi / 2 + i * math.pi / 5
        pts.append(f"{50 + r * math.cos(a):.1f} {56 + r * math.sin(a):.1f}")
    return 'M ' + ' L '.join(pts) + ' Z'


COLS = ['title', None, 'dur', 'artist', 'album', 'genre', 'fav', 'plays']


def _draw(p, name, c):
    def st(d, w=8):
        _pen(p, c, w)
        p.drawPath(svgpath(d))

    def fl(d):
        _fill(p, c, 6)
        p.drawPath(svgpath(d))
    if name == 'play':
        fl('M 30 18 L 30 82 L 84 50 Z')
    elif name == 'pause':
        _fill(p, c)
        p.drawRoundedRect(QRectF(24, 16, 18, 68), 5, 5)
        p.drawRoundedRect(QRectF(58, 16, 18, 68), 5, 5)
    elif name == 'next':
        fl('M 14 24 L 14 76 L 48 50 Z')
        fl('M 52 24 L 52 76 L 86 50 Z')
    elif name == 'prev':
        fl('M 86 24 L 86 76 L 52 50 Z')
        fl('M 48 24 L 48 76 L 14 50 Z')
    elif name == 'shuffle':
        st('M 10 30 H 26 C 50 30 50 70 74 70 H 84')
        st('M 10 70 H 26 C 36 70 42 64 46 56')
        st('M 54 44 C 58 36 64 30 74 30 H 84')
        st('M 74 18 L 86 30 L 74 42')
        st('M 74 58 L 86 70 L 74 82')
    elif name in ('repeat', 'repeat1'):
        st('M 18 46 V 40 Q 18 28 30 28 H 82')
        st('M 70 16 L 82 28 L 70 40')
        st('M 82 54 V 60 Q 82 72 70 72 H 18')
        st('M 30 60 L 18 72 L 30 84')
        if name == 'repeat1':
            f = QFont('Segoe UI')
            f.setPixelSize(30)
            f.setBold(True)
            p.setFont(f)
            p.setPen(QColor(c))
            p.drawText(QRectF(30, 34, 40, 32), Qt.AlignCenter, '1')
    elif name == 'volume':
        fl('M 10 38 L 28 38 L 48 20 L 48 80 L 28 62 L 10 62 Z')
        _pen(p, c, 7)
        for r in (16, 32):
            path = QPainterPath()
            rect = QRectF(48 - r, 50 - r, 2 * r, 2 * r)
            path.arcMoveTo(rect, -42)
            path.arcTo(rect, -42, 84)
            p.drawPath(path)
    elif name == 'dl':
        st('M 50 14 V 62')
        st('M 30 44 L 50 64 L 70 44')
        st('M 16 84 H 84')
    elif name == 'search':
        _pen(p, c, 8)
        p.drawEllipse(QPointF(42, 42), 26, 26)
        st('M 62 62 L 86 86')
    elif name == 'sort':
        st('M 14 26 H 86')
        st('M 28 50 H 72')
        st('M 42 74 H 58')
    elif name == 'chev_up':
        st('M 20 64 L 50 34 L 80 64', 10)
    elif name == 'chev_down':
        st('M 20 36 L 50 66 L 80 36', 10)
    elif name == 'star':
        st(_star_d(), 7)
    elif name == 'star_f':
        fl(_star_d())
    elif name == 'yt':
        _fill(p, c)
        p.drawRoundedRect(QRectF(4, 20, 92, 60), 18, 18)
        p.setCompositionMode(QPainter.CompositionMode_Clear)
        fl('M 40 36 L 40 64 L 66 50 Z')
    elif name == 'sc':
        _fill(p, c)
        p.drawPath(svgpath('M 38 78 L 38 44 Q 46 28 64 30 Q 80 32 82 48 Q 96 50 96 64 Q 96 78 82 78 Z'))
        st('M 14 60 V 74', 6)
        st('M 23 52 V 76', 6)
        st('M 31 46 V 76', 6)
    elif name == 'mute':
        fl('M 10 38 L 28 38 L 48 20 L 48 80 L 28 62 L 10 62 Z')
        st('M 62 38 L 88 62', 7)
        st('M 88 38 L 62 62', 7)
    elif name == 'home':
        st('M 12 48 L 50 16 L 88 48')
        st('M 24 42 V 84 H 42 V 62 H 58 V 84 H 76 V 42', 7)
    elif name == 'clock':
        _pen(p, c, 7)
        p.drawEllipse(QPointF(50, 50), 36, 36)
        st('M 50 28 V 50 L 66 60', 7)
    elif name == 'mic':
        _pen(p, c, 7)
        p.drawRoundedRect(QRectF(36, 10, 28, 46), 14, 14)
        st('M 24 44 Q 24 72 50 72 Q 76 72 76 44', 7)
        st('M 50 72 V 88', 7)
        st('M 36 88 H 64', 7)
    elif name == 'album':
        _pen(p, c, 7)
        p.drawRoundedRect(QRectF(22, 36, 56, 52), 8, 8)
        st('M 30 23 H 70', 7)
        st('M 38 10 H 62', 7)
    elif name == 'note':
        _fill(p, c)
        p.drawEllipse(QPointF(34, 74), 15, 12)
        st('M 46 70 V 18')
        st('M 46 18 Q 74 20 76 50')
    elif name == 'playlist':
        st('M 10 24 H 64', 7)
        st('M 10 46 H 64', 7)
        st('M 10 68 H 36', 7)
        _fill(p, c)
        p.drawEllipse(QPointF(68, 74), 10, 8)
        st('M 77 72 V 40', 6)
        st('M 77 40 Q 90 42 90 56', 6)
    elif name == 'grid':
        _pen(p, c, 7)
        for x, y in ((12, 12), (56, 12), (12, 56), (56, 56)):
            p.drawRoundedRect(QRectF(x, y, 32, 32), 7, 7)
    elif name == 'plus':
        st('M 50 18 V 82')
        st('M 18 50 H 82')
    elif name == 'folder':
        st('M 10 30 V 74 Q 10 82 18 82 H 82 Q 90 82 90 74 V 40 Q 90 32 82 32 H 46 L 38 20 H 18 Q 10 20 10 28 Z', 7)
    elif name == 'back':
        st('M 86 50 H 16')
        st('M 44 22 L 16 50 L 44 78')
    elif name == 'check':
        st('M 22 52 L 42 72 L 80 30', 10)
    elif name == 'chev':
        st('M 36 18 L 68 50 L 36 82', 10)
    elif name == 'more':
        _fill(p, c)
        for x in (18, 50, 82):
            p.drawEllipse(QPointF(x, 50), 8, 8)
    elif name == 'download':
        _fill(p, c)
        p.drawEllipse(QPointF(50, 50), 40, 40)
        p.setCompositionMode(QPainter.CompositionMode_Clear)
        st('M 50 28 V 66', 9)
        st('M 34 52 L 50 68 L 66 52', 9)
    elif name == 'eq':
        _fill(p, c)
        for x, y, h in ((12, 35, 50), (32, 15, 70), (52, 40, 45), (72, 25, 60)):
            p.drawRoundedRect(QRectF(x, y, 14, h), 5, 5)
    elif name == 'library':
        _pen(p, c, 7)
        p.drawRoundedRect(QRectF(14, 14, 72, 72), 14, 14)
        _fill(p, c)
        p.drawEllipse(QPointF(40, 64), 9, 7)
        st('M 48 62 V 34', 6)
        st('M 48 34 Q 62 36 64 48', 6)
    elif name == 'logo':
        _fill(p, c)
        p.drawRoundedRect(QRectF(4, 4, 92, 92), 24, 24)
        p.setCompositionMode(QPainter.CompositionMode_Clear)
        _fill(p, c)
        p.drawEllipse(QPointF(38, 68), 14, 11)
        st('M 50 64 V 28', 9)
        st('M 50 28 Q 74 30 76 52', 9)


_pc = {}


def pix(name, c=WHITE, n=24):
    k = (name, c, n)
    if k not in _pc:
        pm = QPixmap(n * 2, n * 2)
        pm.fill(Qt.transparent)
        pm.setDevicePixelRatio(2)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        p.scale(n / 100, n / 100)
        _draw(p, name, c)
        p.end()
        _pc[k] = pm
    return _pc[k]


def ico(name, c=WHITE, n=24):
    i = QIcon()
    i.addPixmap(pix(name, c, n), QIcon.Normal)
    i.addPixmap(pix(name, '#1c1c1c' if name == 'back' else '#4a4a4a', n), QIcon.Disabled)
    return i


_ph = {}


def placeholder(n):
    if n not in _ph:
        pm = QPixmap(n, n)
        pm.fill(QColor('#333333'))
        p = QPainter(pm)
        p.drawPixmap((n - n // 2) // 2, (n - n // 2) // 2, pix('note', '#8a8a8a', n // 2))
        p.end()
        _ph[n] = pm
    return _ph[n]


def avatar(n):
    pm = QPixmap(n, n)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor('#3a3a3c'))
    p.drawEllipse(0, 0, n, n)
    p.drawPixmap(n // 4, n // 4, pix('mic', '#8a8a8a', n // 2))
    p.end()
    return pm


_rc = {}


def rounded(pm, n, r=8, circle=False):
    key = (pm.cacheKey(), n, r, circle)
    if key in _rc:
        return _rc[key]
    pm = pm.scaled(n, n, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    out = QPixmap(n, n)
    out.fill(Qt.transparent)
    p = QPainter(out)
    p.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    if circle:
        path.addEllipse(0, 0, n, n)
    else:
        path.addRoundedRect(0, 0, n, n, r, r)
    p.setClipPath(path)
    p.drawPixmap(0, 0, pm)
    p.end()
    _rc[key] = out
    return out


def square(img, n):
    s = min(img.width(), img.height())
    img = img.copy((img.width() - s) // 2, (img.height() - s) // 2, s, s)
    return img.scaled(n, n, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)


def fmt(sec):
    sec = int(sec or 0)
    return f"{sec // 60}:{sec % 60:02d}"


def total_txt(l):
    m = round(sum(s['dur'] for s in l) / 60)
    h, mi = divmod(m, 60)
    t = f"{len(l)} música{'s' if len(l) != 1 else ''}"
    if h:
        t += f", {h} hora{'s' if h > 1 else ''}"
    return t + f", {mi} minuto{'s' if mi != 1 else ''}"


def track_nums(l):
    ok = all(s['n'] for s in l) and len({(s['disc'], s['n']) for s in l}) == len(l)
    return [s['n'] if ok else i + 1 for i, s in enumerate(l)]


def meta(l):
    return ' · '.join(x for x in (l[0]['genre'], l[0]['year']) if x)


def label(text, css=''):
    l = QLabel(text)
    if css:
        l.setStyleSheet(css)
    return l


def icon_label(name, c, n):
    l = QLabel()
    l.setPixmap(pix(name, c, n))
    l.setFixedSize(n, n)
    return l


# ====================== LEITURA DAS MÚSICAS ======================

def read_tags(path):
    s = {'path': path, 'title': os.path.splitext(os.path.basename(path))[0],
         'artist': 'Artista desconhecido', 'album': 'Álbum desconhecido', 'aartist': None,
         'n': 0, 'disc': 1, 'genre': '', 'year': '', 'dur': 0, 'mtime': 0}
    try:
        s['mtime'] = os.path.getmtime(path)
        m = MFile(path, easy=True)
        if m is not None:
            if m.info:
                s['dur'] = m.info.length
            t = m.tags

            def g(k):
                v = t.get(k) if t else None
                return str(v[0]) if v else None
            s['title'] = g('title') or s['title']
            s['artist'] = g('artist') or s['artist']
            s['album'] = g('album') or s['album']
            s['aartist'] = g('albumartist')
            s['genre'] = g('genre') or ''
            s['year'] = (g('date') or '')[:4]
            n = (g('tracknumber') or '0').split('/')[0]
            s['n'] = int(n) if n.isdigit() else 0
            d = (g('discnumber') or '1').split('/')[0]
            s['disc'] = int(d) if d.isdigit() else 1
    except Exception:
        pass
    s['aartist'] = s['aartist'] or s['artist']
    base = os.path.splitext(os.path.basename(path))[0]
    if s['title'] == base:
        m = re.match(r'^(\d{1,3})[\s._-]+(.+)$', base)
        if m:
            s['title'] = m.group(2).strip()
            s['n'] = s['n'] or int(m.group(1))
    return s


def read_cover(path):
    try:
        m = MFile(path)
        if m is None:
            return None
        if getattr(m, 'pictures', None):
            return m.pictures[0].data
        if m.tags:
            for k in m.tags.keys():
                if str(k).startswith('APIC'):
                    return m.tags[k].data
            if 'covr' in m.tags:
                return bytes(m.tags['covr'][0])
    except Exception:
        pass
    return None


class Scanner(QThread):
    found = Signal(list)

    def __init__(self, folders):
        super().__init__()
        self.folders = folders

    def run(self):
        batch, seen = [], set()
        for folder in self.folders:
            for root, _, files in os.walk(folder):
                for f in files:
                    if not f.lower().endswith(EXTS):
                        continue
                    p = os.path.join(root, f)
                    s = read_tags(p)
                    k = (s['album'], s['aartist'])
                    if k not in seen:
                        seen.add(k)
                        d = read_cover(p)
                        if d:
                            img = QImage.fromData(d)
                            if not img.isNull():
                                s['img'] = square(img, 300)
                    batch.append(s)
                    if len(batch) >= 40:
                        self.found.emit(batch)
                        batch = []
        self.found.emit(batch)


# ====================== WIDGETS ======================

def find_ffmpeg():
    base = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
    for d in (base, os.path.join(base, 'ffmpeg'), os.path.join(base, 'ffmpeg', 'bin')):
        if os.path.isfile(os.path.join(d, 'ffmpeg.exe')) or os.path.isfile(os.path.join(d, 'ffmpeg')):
            return d
    p = shutil.which('ffmpeg')
    if p:
        return os.path.dirname(p)
    try:  # ffmpeg embutido (pacote imageio-ffmpeg), funciona sem instalar nada
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.isfile(exe):
            return exe
    except Exception:
        pass
    return None


def _scrub(path, ptitle):
    """Se a etiqueta de álbum do arquivo for o nome da playlist, apaga essa etiqueta."""
    if not path or not ptitle or not os.path.isfile(path):
        return
    try:
        m = MFile(path, easy=True)
        if m is None or not m.tags:
            return
        al = m.tags.get('album')
        if al and str(al[0]).strip().lower() == ptitle.strip().lower():
            del m.tags['album']
            m.save()
    except Exception:
        pass


def _entries(info):
    if not info:
        return []
    if info.get('entries'):
        out = []
        for e in info['entries']:
            out += _entries(e)
        return out
    return [info]


def _clean(m):
    return re.sub(r'(?i)yt-?dlp|ffmpeg|ffprobe', 'o downloader', str(m)).strip()


_BAD = ('lyric', 'live', 'ao vivo', 'remix', 'cover', 'karaoke', 'instrumental', 'reaction',
        'slowed', 'sped up', 'nightcore', '8d')


def _score(c, ref):
    """Pontua um resultado: quanto maior, mais parece a versão só de áudio da mesma música."""
    title = (c.get('title') or '').lower()
    ch = (c.get('channel') or c.get('uploader') or '').lower()
    rt = (ref.get('title') or '').lower()
    for bad in _BAD:
        if bad in title and bad not in rt:
            return -1
    d, rd = c.get('duration'), ref.get('duration')
    if d and rd and abs(d - rd) > max(20, 0.15 * rd):
        return -1
    s = 0
    if ch.endswith('- topic'):
        s += 3
    if re.search(r'\baudio\b|\báudio\b', title) and not re.search(r'video|vídeo|clip', title):
        s += 2
    return s


class _YLog:
    def __init__(self, sig):
        self.sig = sig

    def debug(self, m):
        if not m.startswith('['):
            self.sig.emit(_clean(m))

    info = debug

    def warning(self, m):
        self.sig.emit('Aviso: ' + _clean(m))

    def error(self, m):
        self.sig.emit('Erro: ' + _clean(m))


class Downloader(QThread):
    progress = Signal(int, str)
    log = Signal(str)
    done = Signal(int, int)

    def __init__(self, items, dest, fmt, playlist, ffdir, source='youtube'):
        super().__init__()
        self.items, self.dest, self.fmt, self.playlist, self.ffdir = items, dest, fmt, playlist, ffdir
        self.source = source
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def _scrub_all(self, info, ptitle):
        for e in _entries(info):
            pt = e.get('playlist_title') or e.get('playlist') or ptitle
            for rd in e.get('requested_downloads') or []:
                _scrub(rd.get('filepath'), pt)

    def _flat(self, yt_dlp, query, noplaylist=True):
        o = {'quiet': True, 'extract_flat': 'in_playlist', 'noplaylist': noplaylist,
             'skip_download': True, 'logger': _YLog(self.log)}
        with yt_dlp.YoutubeDL(o) as y:
            return y.extract_info(query, download=False) or {}

    @staticmethod
    def _vurl(e):
        if e.get('id') and len(str(e['id'])) == 11:
            return 'https://www.youtube.com/watch?v=' + e['id']
        return e.get('webpage_url') or e.get('url')

    def best_audio(self, yt_dlp, ref, cands=None):
        """Procura a versão só de áudio; se não achar, usa o próprio vídeo."""
        if cands is None:
            title = ref.get('track') or ref.get('title') or ''
            artist = (ref.get('artist') or ref.get('channel') or ref.get('uploader') or '')
            artist = re.sub(r'(?i)\s*-\s*topic$', '', artist)
            clean = re.sub(r'(?i)[(\[][^)\]]*(official|video|vídeo|clip|lyric|audio|áudio|hd|4k)[^)\]]*[)\]]',
                           '', title).strip()
            q = clean if artist.lower() in clean.lower() else f'{artist} {clean}'
            cands = self._flat(yt_dlp, 'ytsearch10:' + q.strip()).get('entries') or []
        best, bs = None, 1
        for c in cands:
            if c and c.get('id'):
                sc = _score(c, ref)
                if sc > bs:
                    best, bs = c, sc
        if best:
            self.log.emit('Versão em áudio encontrada.')
            return self._vurl(best)
        self.log.emit('Versão em áudio não encontrada, usando o áudio do vídeo.')
        return self._vurl(ref)

    def targets(self, yt_dlp, item, is_url):
        if is_url:
            info = self._flat(yt_dlp, item, noplaylist=not self.playlist)
            refs = [r for r in (info.get('entries') or [info]) if r]
            ptitle = (info.get('title') or None) if (info.get('entries') and len(refs) > 1) else None
            return [self.best_audio(yt_dlp, r) for r in refs], ptitle
        res = [r for r in (self._flat(yt_dlp, 'ytsearch10:' + item).get('entries') or []) if r]
        if not res:
            return [], None
        return [self.best_audio(yt_dlp, res[0], res)], None

    def run(self):
        try:
            import yt_dlp
        except ImportError:
            self.log.emit('Componente de download não encontrado. Gere o app de novo pelo gerar_exe.bat.')
            self.done.emit(0, len(self.items))
            return

        def hook(d):
            if self._cancel:
                raise yt_dlp.utils.DownloadCancelled()
            if d['status'] == 'downloading':
                tot = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                pct = int(d.get('downloaded_bytes', 0) * 100 / tot) if tot else 0
                self.progress.emit(pct, f"Baixando… {pct}%  {str(d.get('_speed_str', '')).strip()}")
            elif d['status'] == 'finished':
                self.progress.emit(100, 'Convertendo…' if self.ffdir else 'Download concluído')

        def make_opts(tmpl, noplaylist):
            o = {'format': 'bestaudio/best' if self.ffdir else 'bestaudio[ext=m4a]/bestaudio',
                 'outtmpl': os.path.join(self.dest, tmpl), 'noplaylist': noplaylist,
                 'quiet': True, 'logger': _YLog(self.log), 'progress_hooks': [hook],
                 'windowsfilenames': True}
            if self.ffdir:
                o['ffmpeg_location'] = self.ffdir
                o['writethumbnail'] = True
                pp = [{'key': 'FFmpegExtractAudio', 'preferredcodec': self.fmt,
                       'preferredquality': '0' if self.fmt == 'flac' else '192'},
                      {'key': 'FFmpegMetadata', 'add_metadata': True}]
                if self.fmt in ('mp3', 'm4a', 'flac'):
                    pp = ([{'key': 'FFmpegThumbnailsConvertor', 'format': 'jpg', 'when': 'before_dl'}]
                          + pp + [{'key': 'EmbedThumbnail'}])
                o['postprocessors'] = pp
            return o

        ok = fail = 0
        for i, it in enumerate(self.items, 1):
            if self._cancel:
                break
            is_url = bool(re.match(r'https?://', it))
            self.log.emit(f'[{i}/{len(self.items)}] {it}')
            ptitle = None
            if self.source == 'youtube':
                try:
                    urls, ptitle = self.targets(yt_dlp, it, is_url)
                except Exception:
                    self.log.emit('Não foi possível procurar a versão em áudio; usando o link original.')
                    urls = [it] if is_url else ['ytsearch1:' + it]
                if not urls:
                    fail += 1
                    self.log.emit('Nada encontrado.')
                    continue
            else:
                urls = [it if is_url else 'scsearch1:' + it]
            for j, u in enumerate(urls, 1):
                if self._cancel:
                    break
                if len(urls) > 1:
                    self.log.emit(f'  ({j}/{len(urls)})')
                o = make_opts('%(title)s.%(ext)s', self.source == 'youtube' or not self.playlist)
                try:
                    with yt_dlp.YoutubeDL(o) as y:
                        info = y.extract_info(u, download=True)
                    self._scrub_all(info, ptitle)
                    ok += 1
                except Exception as e:
                    if self._cancel:
                        break
                    fail += 1
                    self.log.emit('Falhou: ' + _clean(e))
        self.done.emit(ok, fail)


def make_app_icon():
    """Logo do app (janela e barra de tarefas): quadrado arredondado vermelho com nota branca."""
    ic = QIcon()
    for n in (16, 24, 32, 48, 64, 128, 256):
        pm = QPixmap(n, n)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        g = QLinearGradient(0, 0, n, n)
        g.setColorAt(0, QColor('#ff6b81'))
        g.setColorAt(1, QColor('#fa243c'))
        p.setBrush(QBrush(g))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(QRectF(0, 0, n, n), n * 0.225, n * 0.225)
        s = n / 100 * 0.703
        p.translate(n / 2 - 50 * s, n / 2 - 50 * s)
        p.scale(s, s)
        _draw(p, 'note', '#ffffff')
        p.end()
        ic.addPixmap(pm)
    return ic


def dark_titlebar(win):
    try:
        import ctypes
        hwnd = int(win.winId())
        for attr, val in ((20, 1), (19, 1), (35, 0x001c1c1c)):
            v = ctypes.c_int(val)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(v), 4)
    except Exception:
        pass


class GridDelegate(QStyledItemDelegate):
    def sizeHint(self, opt, idx):
        return QSize(224, 276)

    def paint(self, p, opt, idx):
        r = opt.rect
        if opt.state & QStyle.State_MouseOver:
            p.fillRect(r, QColor('#272727'))
        p.drawPixmap(r.x() + 12, r.y() + 8, idx.data(Qt.UserRole + 1))
        f = p.font()
        f.setPixelSize(14)
        p.setFont(f)
        p.setPen(QColor(WHITE))
        t = p.fontMetrics().elidedText(idx.data(Qt.UserRole + 2), Qt.ElideRight, 200)
        p.drawText(QRect(r.x() + 12, r.y() + 212, 200, 20), Qt.AlignLeft | Qt.AlignVCenter, t)
        p.setPen(QColor(GRAY))
        t = p.fontMetrics().elidedText(idx.data(Qt.UserRole + 3), Qt.ElideRight, 200)
        p.drawText(QRect(r.x() + 12, r.y() + 232, 200, 20), Qt.AlignLeft | Qt.AlignVCenter, t)


class SideDelegate(QStyledItemDelegate):
    def sizeHint(self, opt, idx):
        return QSize(250, 40)

    def paint(self, p, opt, idx):
        p.save()
        p.setRenderHint(QPainter.Antialiasing)
        r = opt.rect.adjusted(4, 1, -4, -1)
        clickable = idx.data(Qt.UserRole) is not None
        sel = bool(opt.state & QStyle.State_Selected) and clickable
        hov = bool(opt.state & QStyle.State_MouseOver) and clickable
        if sel or hov:
            p.setPen(Qt.NoPen)
            p.setBrush(QColor('#2d2d2d' if sel else '#252525'))
            p.drawRoundedRect(r, 6, 6)
        if sel:
            p.setBrush(QColor(BLUE))
            p.drawRoundedRect(QRectF(r.x(), r.center().y() - 9, 3, 18), 1.5, 1.5)
        cy = r.center().y()
        x = r.x() + 14 + (idx.data(Qt.UserRole + 1) or 0) * 30
        pm = idx.data(Qt.UserRole + 5)
        if pm is not None:
            p.drawPixmap(x, cy - 10, pm)
        else:
            p.drawPixmap(x, cy - 9, pix(idx.data(Qt.UserRole + 2), WHITE, 20))
        f = p.font()
        f.setPixelSize(14)
        p.setFont(f)
        p.setPen(QColor(WHITE))
        right = r.right() - (76 if not clickable else 12)
        txt = p.fontMetrics().elidedText(idx.data(Qt.DisplayRole), Qt.ElideRight, right - x - 32)
        p.drawText(QRect(x + 32, r.y(), right - x - 32, r.height()), Qt.AlignLeft | Qt.AlignVCenter, txt)
        if not clickable:
            grp = idx.data(Qt.UserRole + 3)
            p.drawPixmap(r.right() - 66, cy - 8, pix('more' if grp == 'lib' else 'plus', '#bbbbbb', 16))
            up = idx.data(Qt.UserRole + 4)
            p.drawPixmap(r.right() - 32, cy - 7, pix('chev_up' if up else 'chev_down', '#bbbbbb', 14))
        p.restore()


class SourceCard(QFrame):
    clicked = Signal()

    def __init__(self, title, sub, icon, c1, c2, enabled, h):
        super().__init__()
        self.title, self.sub, self.icon, self.c1, self.c2, self.on = title, sub, icon, c1, c2, enabled
        self.hover = False
        self.setFixedHeight(h)
        self.setCursor(Qt.PointingHandCursor if enabled else Qt.ArrowCursor)

    def enterEvent(self, e):
        self.hover = True
        self.update()

    def leaveEvent(self, e):
        self.hover = False
        self.update()

    def mousePressEvent(self, e):
        if self.on and e.button() == Qt.LeftButton:
            self.clicked.emit()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        if self.on:
            g = QLinearGradient(r.topLeft(), r.bottomRight())
            g.setColorAt(0, QColor(self.c1))
            g.setColorAt(1, QColor(self.c2))
            p.setBrush(QBrush(g))
            p.setPen(Qt.NoPen)
        else:
            p.setBrush(QColor('#232323'))
            p.setPen(QPen(QColor('#3a3a3a'), 1.5, Qt.DashLine))
        p.drawRoundedRect(r, 16, 16)
        if self.on and self.hover:
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 255, 255, 28))
            p.drawRoundedRect(r, 16, 16)
        h = self.height()
        f = p.font()
        if self.icon:
            p.drawPixmap(32, (h - 72) // 2, pix(self.icon, '#ffffff', 72))
            f.setPixelSize(26)
            f.setBold(True)
            p.setFont(f)
            p.setPen(QColor('#ffffff'))
            p.drawText(QRect(124, h // 2 - 40, self.width() - 140, 40), Qt.AlignLeft | Qt.AlignBottom, self.title)
            f.setPixelSize(13)
            f.setBold(False)
            p.setFont(f)
            p.setPen(QColor(255, 255, 255, 215))
            p.drawText(QRect(124, h // 2 + 6, self.width() - 140, 44), Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap,
                       self.sub)
        else:
            f.setPixelSize(24)
            f.setBold(True)
            p.setFont(f)
            p.setPen(QColor('#8a8a8a'))
            p.drawText(QRect(0, h // 2 - 36, self.width(), 36), Qt.AlignCenter, self.title)
            f.setPixelSize(13)
            f.setBold(False)
            p.setFont(f)
            p.setPen(QColor('#6a6a6a'))
            p.drawText(QRect(0, h // 2 + 4, self.width(), 24), Qt.AlignCenter, self.sub)


class SongHeader(QHeaderView):
    col = -1
    asc = True

    def __init__(self, table):
        super().__init__(Qt.Horizontal, table)

    def paintSection(self, painter, rect, idx):
        painter.save()
        painter.fillRect(rect, QColor('#202020'))
        painter.setPen(QColor('#2b2b2b'))
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())
        if idx == 6:
            painter.drawPixmap(rect.x() + 12, rect.center().y() - 6, pix('star', '#9a9a9a', 12))
        else:
            text = self.model().headerData(idx, Qt.Horizontal, Qt.DisplayRole) or ''
            f = painter.font()
            f.setPixelSize(12)
            f.setBold(idx == self.col)
            painter.setFont(f)
            painter.setPen(QColor('#ffffff' if idx == self.col else '#9a9a9a'))
            painter.drawText(rect.adjusted(8, 0, -22, 0), Qt.AlignLeft | Qt.AlignVCenter, text)
        if idx == self.col:
            painter.setRenderHint(QPainter.Antialiasing)
            painter.drawPixmap(rect.right() - 20, rect.center().y() - 5,
                               pix('chev_up' if self.asc else 'chev_down', '#cfcfcf', 10))
        painter.restore()


class SongTable(QTableWidget):
    def __init__(self, win):
        super().__init__(0, 8)
        self.win = win

    def leaveEvent(self, e):
        self.win.set_hrow(-1)
        super().leaveEvent(e)


class SongDelegate(QStyledItemDelegate):
    def __init__(self, win):
        super().__init__(win.table)
        self.win = win

    def paint(self, p, opt, idx):
        w = self.win
        row, col, r = idx.row(), idx.column(), opt.rect
        if row >= len(w.view):
            return
        s = w.view[row]
        hov = row == w.hrow
        if opt.state & QStyle.State_Selected:
            p.fillRect(r, QColor('#34343a'))
        elif hov:
            p.fillRect(r, QColor('#2a2a2a'))
        p.save()
        p.setRenderHint(QPainter.Antialiasing)
        cy = r.center().y()
        if col == 1:
            p.drawPixmap(r.x() + (r.width() - 18) // 2, cy - 9, pix('more', '#cfcfcf', 18))
        elif col == 6:
            if s['path'] in w.fav_songs:
                p.drawPixmap(r.x() + 12, cy - 7, pix('star_f', '#f5c400', 14))
            elif hov:
                p.drawPixmap(r.x() + 12, cy - 7, pix('star', '#9a9a9a', 14))
        else:
            if col == 7:
                n = w.plays.get(s['path'], 0)
                text = str(n) if n else ''
            else:
                text = idx.data(Qt.DisplayRole) or ''
            cur = w.queue[w.idx]['path'] if 0 <= w.idx < len(w.queue) else None
            f = p.font()
            f.setPixelSize(13)
            p.setFont(f)
            blue = col == 0 and s['path'] == cur
            p.setPen(QColor(BLUE if blue else '#e6e6e6'))
            txt = p.fontMetrics().elidedText(text, Qt.ElideRight, r.width() - 16)
            p.drawText(QRect(r.x() + 8, r.y(), r.width() - 16, r.height()),
                       Qt.AlignLeft | Qt.AlignVCenter, txt)
        p.restore()


class TrackRow(QFrame):
    def __init__(self, win, lst, idx, num, two):
        super().__init__()
        self.win, self.lst, self.idx, self.s = win, lst, idx, lst[idx]
        self.num_txt = str(num)
        self.hover = self.playing = False
        self._h = 0.0
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(140)
        self._anim.valueChanged.connect(self._set_h)
        self.setObjectName('trow')
        self.setFixedHeight(47 if two else 43)
        h = QHBoxLayout(self)
        h.setContentsMargins(4, 0, 8, 0)
        h.setSpacing(10)
        self.num = label(self.num_txt, f'color: {GRAY};')
        self.num.setFixedWidth(36)
        self.num.setAlignment(Qt.AlignCenter)
        h.addWidget(self.num)
        v = QVBoxLayout()
        v.setSpacing(0)
        v.setContentsMargins(0, 0, 0, 0)
        v.addStretch()
        v.addWidget(QLabel(self.s['title']))
        if two:
            v.addWidget(label(self.s['artist'], f'color: {GRAY}; font-size: 12px;'))
        v.addStretch()
        h.addLayout(v, 1)
        d = label(fmt(self.s['dur']), 'color: #aaa;')
        d.setFixedWidth(48)
        d.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        h.addWidget(d)
        self.more = QLabel()
        self.more.setFixedSize(18, 18)
        h.addWidget(self.more)

    def refresh(self):
        self.more.setPixmap(pix('more', '#aaa', 18) if self.hover else QPixmap())
        if self.hover:
            self.num.setPixmap(pix('play', WHITE, 16))
        elif self.playing:
            self.num.setPixmap(pix('eq', BLUE, 16))
        else:
            self.num.setText(self.num_txt)

    def set_playing(self, on):
        self.playing = on
        self.refresh()

    def _set_h(self, v):
        self._h = float(v)
        self.update()

    def _fade(self, to):
        self._anim.stop()
        self._anim.setStartValue(self._h)
        self._anim.setEndValue(to)
        self._anim.start()

    def paintEvent(self, e):
        p = QPainter(self)
        if self._h > 0:
            p.fillRect(self.rect(), QColor(255, 255, 255, int(16 * self._h)))
        p.setPen(QColor('#262626'))
        p.drawLine(0, self.height() - 1, self.width(), self.height() - 1)

    def enterEvent(self, e):
        self.hover = True
        self.refresh()
        self._fade(1.0)

    def leaveEvent(self, e):
        self.hover = False
        self.refresh()
        self._fade(0.0)

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return
        if e.position().x() < 50:
            self.win.play_at(self.idx, self.lst)
        elif e.position().x() > self.width() - 40:
            self.win.song_menu(self.s, e.globalPosition().toPoint())

    def mouseDoubleClickEvent(self, e):
        self.win.play_at(self.idx, self.lst)

    def contextMenuEvent(self, e):
        self.win.song_menu(self.s, e.globalPos())


class SmoothScroll(QObject):
    """Rolagem animada com a rodinha do mouse."""

    def __init__(self, area):
        super().__init__(area)
        self.bar = area.verticalScrollBar()
        self.target = 0
        self.anim = QPropertyAnimation(self.bar, b'value', self)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.setDuration(280)
        area.viewport().installEventFilter(self)

    def eventFilter(self, o, e):
        if e.type() == QEvent.Wheel:
            dy = e.angleDelta().y()
            if dy == 0:
                return False
            running = self.anim.state() == QAbstractAnimation.Running
            base = self.target if running else self.bar.value()
            self.target = int(max(self.bar.minimum(), min(self.bar.maximum(), base - dy)))
            self.anim.stop()
            self.anim.setStartValue(self.bar.value())
            self.anim.setEndValue(self.target)
            self.anim.start()
            return True
        return False


class Seek(QSlider):
    seeked = Signal(int)
    dragging = False

    def __init__(self):
        super().__init__(Qt.Horizontal)

    def _pos(self, e):
        f = max(0.0, min(1.0, e.position().x() / max(1, self.width())))
        v = int(self.minimum() + (self.maximum() - self.minimum()) * f)
        self.setValue(v)
        return v

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.dragging = True
            self._pos(e)

    def mouseMoveEvent(self, e):
        if self.dragging:
            self._pos(e)

    def mouseReleaseEvent(self, e):
        if self.dragging:
            self.dragging = False
            self.seeked.emit(self._pos(e))


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP)
        self.resize(1280, 780)
        self.cfg = QSettings(APP, 'player')
        self.songs, self.by_path, self.covers, self.rows = [], {}, {}, []
        self.queue, self.view, self.idx = [], [], -1
        self.shuffle, self.repeat = False, 0
        self.hist, self.cur = [], None
        self.sort = 'title'
        self.collapsed = set()
        self.hrow = -1
        self.tsort = ('artist', True)
        self.counted = True
        self.fav_songs = set(self.cfg.value('fav_songs', [], type=list))
        try:
            self.plays = json.loads(self.cfg.value('plays', '{}'))
        except Exception:
            self.plays = {}
        self.side_sel = ('home',)
        try:
            self.playlists = json.loads(self.cfg.value('playlists', '{}'))
        except Exception:
            self.playlists = {}

        self.audio = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio)
        self.audio.setVolume(0.7)
        self.vol_val = 0.7
        self.player.positionChanged.connect(self.on_pos)
        self.player.durationChanged.connect(lambda d: self.seek.setRange(0, d))
        self.player.mediaStatusChanged.connect(
            lambda st: self.next(True) if st == QMediaPlayer.EndOfMedia else None)
        self.player.playbackStateChanged.connect(
            lambda st: self.set_ic(self.b_play, 'pause' if st == QMediaPlayer.PlayingState else 'play'))

        root = QWidget(objectName='root')
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        body = QHBoxLayout()
        body.setSpacing(0)
        outer.addLayout(body, 1)

        # ---------- barra lateral (altura total) ----------
        side = QWidget(objectName='sidebar')
        side.setFixedWidth(290)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(8, 0, 8, 8)
        sl.setSpacing(0)
        hw = QWidget()
        sh = QHBoxLayout(hw)
        sh.setContentsMargins(0, 0, 0, 0)
        sh.setSpacing(4)
        self.back = self.btn('back', self.go_back, size=18)
        sh.addWidget(self.back)
        sh.addWidget(icon_label('logo', WHITE, 20))
        sh.addSpacing(2)
        sh.addWidget(label(APP, 'font-size: 14px; font-weight: 600;'))
        sh.addStretch()
        self.b_menu = self.btn('more', self.app_menu, size=18)
        sh.addWidget(self.b_menu)
        hw.setFixedHeight(62)
        sl.addWidget(hw)
        self.search = QLineEdit(placeholderText='Pesquisar')
        self.search.addAction(ico('search', GRAY, 16), QLineEdit.TrailingPosition)
        self.search.textChanged.connect(self.render)
        sl.addWidget(self.search)
        sl.addSpacing(8)
        self.side = QListWidget(objectName='side')
        self.side.setItemDelegate(SideDelegate(self.side))
        self.side.setMouseTracking(True)
        self.side.itemClicked.connect(self.on_side)
        self.side.setContextMenuPolicy(Qt.CustomContextMenu)
        self.side.customContextMenuRequested.connect(self.side_ctx)
        sl.addWidget(self.side, 1)
        body.addWidget(side)

        right = QVBoxLayout()
        right.setSpacing(0)

        # ---------- barra superior (player) ----------
        top = QFrame(objectName='top')
        top.setFixedHeight(62)
        tl = QHBoxLayout(top)
        tl.setContentsMargins(16, 4, 16, 4)
        tl.addStretch(1)
        self.b_shuf = self.btn('shuffle', self.toggle_shuffle)
        self.b_prev = self.btn('prev', self.prev)
        self.b_play = self.btn('play', self.toggle, size=30)
        self.b_next = self.btn('next', lambda: self.next(False))
        self.b_rep = self.btn('repeat', self.toggle_repeat)
        for b in (self.b_shuf, self.b_prev, self.b_play, self.b_next, self.b_rep):
            tl.addWidget(b)
        tl.addSpacing(30)

        now = QFrame(objectName='now')
        now.setFixedSize(560, 54)
        nl = QHBoxLayout(now)
        nl.setContentsMargins(0, 0, 0, 0)
        nl.setSpacing(0)
        self.cover = QLabel()
        self.cover.setFixedSize(52, 52)
        self.cover.setPixmap(placeholder(52))
        nl.addWidget(self.cover)
        nv = QVBoxLayout()
        nv.setSpacing(0)
        nv.setContentsMargins(0, 6, 0, 0)
        self.lt = label('', 'font-size: 12px; font-weight: 700;')
        self.la = label('', f'font-size: 11px; color: {GRAY};')
        self.lt.setAlignment(Qt.AlignCenter)
        self.la.setAlignment(Qt.AlignCenter)
        self.seek = Seek()
        self.seek.setFixedHeight(10)
        self.seek.seeked.connect(self.player.setPosition)
        nv.addWidget(self.lt)
        nv.addWidget(self.la)
        nv.addStretch()
        nv.addWidget(self.seek)
        self.np_info = QWidget()
        self.np_info.setLayout(nv)
        self.np_info.hide()
        self.np_idle = QWidget()
        il = QHBoxLayout(self.np_idle)
        il.addWidget(icon_label('logo', '#7a7a7a', 26), 0, Qt.AlignCenter)
        nl.addWidget(self.np_info, 1)
        nl.addWidget(self.np_idle, 1)
        tl.addWidget(now)
        tl.addStretch(1)
        self.b_vol = self.btn('volume', self.toggle_mute, size=20)
        tl.addWidget(self.b_vol)
        vol = Seek()
        vol.setObjectName('vol')
        vol.setFixedHeight(16)
        vol.setRange(0, 100)
        vol.setValue(70)
        vol.setFixedWidth(100)
        vol.valueChanged.connect(self.set_vol)
        tl.addWidget(vol)
        tl.addSpacing(6)
        self.b_queue = self.btn('playlist', self.show_queue, size=20)
        tl.addWidget(self.b_queue)
        right.addWidget(top)

        # ---------- título da página ----------
        head = QFrame(objectName='head')
        head.setFixedHeight(48)
        hl = QHBoxLayout(head)
        hl.setContentsMargins(12, 0, 12, 0)
        hl.setSpacing(0)
        hl.addSpacing(72)
        self.title = label('', 'font-size: 15px; font-weight: 700;')
        self.title.setAlignment(Qt.AlignCenter)
        hl.addWidget(self.title, 1)
        for ic, fn in (('search', lambda: self.search.setFocus()), ('sort', self.sort_menu)):
            b = self.btn(ic, fn, size=18)
            b.setFixedWidth(36)
            hl.addWidget(b)
        right.addWidget(head)

        self.stack = QStackedWidget()
        self.grid = QListWidget(objectName='grid')
        self.grid.setViewMode(QListWidget.IconMode)
        self.grid.setItemDelegate(GridDelegate(self.grid))
        self.grid.setGridSize(QSize(224, 276))
        self.grid.setSpacing(8)
        self.grid.setMovement(QListWidget.Static)
        self.grid.setResizeMode(QListWidget.Adjust)
        self.grid.setMouseTracking(True)
        self.grid.setContentsMargins(24, 24, 24, 24)
        self.grid.itemClicked.connect(self.grid_click)
        self.table = SongTable(self)
        self.table.setHorizontalHeader(SongHeader(self.table))
        self.table.setHorizontalHeaderLabels(['Título', '', 'Duração', 'Artista', 'Álbum', 'Gênero', '',
                                              'Reproduções'])
        h = self.table.horizontalHeader()
        h.setSectionsClickable(True)
        h.setStretchLastSection(True)
        h.setFixedHeight(38)
        for i, wd in enumerate((300, 44, 80, 160, 200, 130, 44, 120)):
            h.setSectionResizeMode(i, QHeaderView.Interactive)
            self.table.setColumnWidth(i, wd)
        h.sectionClicked.connect(self.on_header)
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setShowGrid(False)
        self.table.setMouseTracking(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setItemDelegate(SongDelegate(self))
        self.table.cellDoubleClicked.connect(lambda r, c: self.play_at(r, self.view))
        self.table.cellClicked.connect(self.cell_clicked)
        self.table.cellEntered.connect(lambda r, c: self.set_hrow(r))
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.table_ctx)
        self.scroll_album = QScrollArea()
        self.scroll_album.setWidgetResizable(True)
        ap = QWidget(objectName='page')
        ap.setAttribute(Qt.WA_StyledBackground, True)
        al = QHBoxLayout(ap)
        al.setContentsMargins(0, 0, 0, 0)
        al.setSpacing(0)
        self.alist = QListWidget(objectName='alist')
        self.alist.setFixedWidth(236)
        self.alist.setIconSize(QSize(40, 40))
        self.alist.itemClicked.connect(self.artist_click)
        self.scroll_art = QScrollArea()
        self.scroll_art.setWidgetResizable(True)
        al.addWidget(self.alist)
        al.addWidget(self.scroll_art, 1)
        for w in (self.grid, self.table, self.scroll_album, ap, self.build_hub(), self.build_download()):
            self.stack.addWidget(w)
        scrolls = (self.grid, self.table, self.scroll_album, self.scroll_art, self.side, self.alist)
        for a in scrolls:
            a.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            if isinstance(a, QAbstractItemView):
                a.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.alist.setTextElideMode(Qt.ElideRight)
        self.side.setTextElideMode(Qt.ElideRight)
        self._smooth = [SmoothScroll(a) for a in scrolls]
        right.addWidget(self.stack, 1)
        body.addLayout(right, 1)

        QShortcut(QKeySequence(Qt.Key_Space), self, activated=self.toggle)

        self.folders = self.cfg.value('folders', [], type=list)
        self.build_side()
        self.side.setCurrentRow(0)
        self.show_view(('home',), False)
        QTimer.singleShot(300, self.ask_folder)

    def btn(self, ic, fn, name=None, size=22, text=''):
        b = QPushButton(text)
        if name:
            b.setObjectName(name)
        b.sz = size
        b.setIconSize(QSize(size, size))
        b.setCursor(Qt.PointingHandCursor)
        b.clicked.connect(lambda _=False: fn())
        self.set_ic(b, ic)
        return b

    def set_ic(self, b, name, color=WHITE):
        b.ic = name
        b.setIcon(ico(name, color, b.sz))

    # ---------- pasta ----------
    def ask_folder(self):
        start = self.folders[0] if self.folders else os.path.expanduser('~')
        d = QFileDialog.getExistingDirectory(self, 'Escolha a pasta de músicas', start)
        if d:
            self.folders = [d]
            self.cfg.setValue('folders', self.folders)
        if not self.folders:
            m = os.path.join(os.path.expanduser('~'), 'Music')
            if os.path.isdir(m):
                self.folders = [m]
        self.scan()

    def scan(self):
        self.songs, self.by_path, self.covers = [], {}, {}
        folders = list(self.folders)
        dl = self.cfg.value('dl_dir', '')
        if dl and os.path.isdir(dl):
            nd = os.path.normcase(os.path.abspath(dl))
            inside = any(nd == os.path.normcase(os.path.abspath(x)) or
                         nd.startswith(os.path.normcase(os.path.abspath(x)) + os.sep) for x in folders)
            if not inside:
                folders.append(dl)
        self.scanner = Scanner(folders)
        self.scanner.found.connect(self.on_found)
        self.scanner.finished.connect(self.render)
        self.scanner.finished.connect(self.refresh_side)
        self.scanner.start()

    def on_found(self, batch):
        for s in batch:
            img = s.pop('img', None)
            if img is not None:
                self.covers[(s['album'], s['aartist'])] = QPixmap.fromImage(img)
            self.songs.append(s)
            self.by_path[s['path']] = s
        if len(self.songs) <= 80:
            self.render()

    def cover_of(self, s):
        return self.covers.get((s['album'], s['aartist'])) or placeholder(200)

    # ---------- barra lateral ----------
    def build_side(self):
        L = self.side
        L.clear()

        def add(text, icon, desc=None, lvl=0, group=None, pm=None):
            it = QListWidgetItem(text)
            it.setData(Qt.UserRole + 1, lvl)
            it.setData(Qt.UserRole + 2, icon)
            it.setData(Qt.UserRole + 3, group)
            it.setData(Qt.UserRole + 5, pm)
            if desc is None:
                it.setFlags(Qt.ItemIsEnabled)
                it.setData(Qt.UserRole + 4, group not in self.collapsed)
            else:
                it.setData(Qt.UserRole, desc)
            L.addItem(it)
            if lvl and group in self.collapsed:
                it.setHidden(True)
        add('Início', 'home', ('home',))
        add('Baixar músicas', 'dl', ('download',))
        add('Biblioteca', 'library', None, 0, 'lib')
        add('Adições Recentes', 'clock', ('recent',), 1, 'lib')
        add('Artistas', 'mic', ('artists',), 1, 'lib')
        add('Álbuns', 'album', ('albums',), 1, 'lib')
        add('Músicas', 'note', ('songs',), 1, 'lib')
        add('Playlists', 'playlist', None, 0, 'pl')
        add('Todas as Playlists', 'grid', ('playlists',), 1, 'pl')
        for n, paths in self.playlists.items():
            first = next((self.by_path[p] for p in paths if p in self.by_path), None)
            pm = rounded(self.cover_of(first), 20, 4) if first else None
            add(n, 'note', ('playlist', n), 1, 'pl', pm)
        add('Nova playlist', 'plus', ('new',), 1, 'pl')

    def refresh_side(self):
        self.build_side()
        self.select_side(self.side_sel)

    def toggle_group(self, g):
        self.collapsed ^= {g}
        self.refresh_side()

    def grid_click(self, it):
        d = it.data(Qt.UserRole)
        QTimer.singleShot(0, lambda: self.show_view(d, True))

    def artist_click(self, it):
        d = ('artist', it.data(Qt.UserRole))
        QTimer.singleShot(0, lambda: self.show_view(d, False, False))

    def on_side(self, item):
        d = item.data(Qt.UserRole)
        if d:
            self.side_sel = d
            QTimer.singleShot(0, lambda: self.side_go(d))
            return
        g = item.data(Qt.UserRole + 3)
        gp = QCursor.pos()
        vp = self.side.viewport()
        x, w = vp.mapFromGlobal(gp).x(), vp.width()
        if g == 'pl' and w - 76 <= x <= w - 44:
            QTimer.singleShot(0, lambda: self.side_go(('new',)))
        elif g == 'lib' and w - 76 <= x <= w - 44:
            QTimer.singleShot(0, lambda: self.app_menu(gp))
        else:
            QTimer.singleShot(0, lambda: self.toggle_group(g))

    def side_go(self, d):
        # limpa a busca, senão ela continua escondendo a página escolhida
        self.search.blockSignals(True)
        self.search.clear()
        self.search.blockSignals(False)
        if d[0] == 'new':
            name, ok = QInputDialog.getText(self, 'Nova playlist', 'Nome da playlist:')
            name = name.strip()
            if ok and name and name not in self.playlists:
                self.playlists[name] = []
                self.save_pl()
                self.build_side()
                self.select_side(('playlist', name))
                self.hist = []
                self.show_view(('playlist', name), False)
            return
        self.hist = []
        self.show_view(d, False)

    def select_side(self, desc):
        self.side_sel = desc
        for i in range(self.side.count()):
            if self.side.item(i).data(Qt.UserRole) == desc:
                self.side.setCurrentRow(i)
                return

    def side_ctx(self, pos):
        it = self.side.itemAt(pos)
        d = it.data(Qt.UserRole) if it else None
        if d and d[0] == 'playlist':
            m = QMenu(self)
            a = m.addAction('Excluir playlist')
            if m.exec(self.side.viewport().mapToGlobal(pos)) == a:
                self.playlists.pop(d[1], None)
                self.save_pl()
                self.build_side()
                self.select_side(('playlists',))
                self.hist = []
                self.show_view(('playlists',), False)

    def save_pl(self):
        self.cfg.setValue('playlists', json.dumps(self.playlists))

    # ---------- navegação ----------
    def fade(self):
        pass

    def show_view(self, desc, push, fade=True):
        if push and self.cur is not None:
            self.hist.append(self.cur)
        self.cur = desc
        self.render()
        if fade:
            self.fade()

    def go_back(self):
        if self.hist:
            self.cur = self.hist.pop()
            self.render()
            self.fade()

    def render(self):
        if self.cur is None:
            return
        self.back.setEnabled(bool(self.hist))
        self.rows = []
        k = self.cur[0]
        term = self.search.text().strip().lower()
        if term:
            res = [s for s in self.songs if term in (s['title'] + s['artist'] + s['album']).lower()]
            self.fill_table(sorted(res, key=lambda s: s['title'].lower()), 'Resultados')
        elif k == 'download':
            if len(self.cur) > 1:
                yt = self.cur[1] == 'youtube'
                self.dl_source = self.cur[1]
                self.title.setText('YouTube' if yt else 'SoundCloud')
                self.dl_urls.setPlaceholderText('https://www.youtube.com/watch?v=...' if yt
                                                else 'https://soundcloud.com/...')
                self.stack.setCurrentIndex(5)
            else:
                self.title.setText('Baixar músicas')
                self.stack.setCurrentIndex(4)
        elif k in ('home', 'albums', 'recent'):
            groups = {}
            for s in self.songs:
                groups.setdefault((s['album'], s['aartist']), []).append(s)
            if k in ('home', 'recent') or self.sort == 'recent':
                keys = sorted(groups, key=lambda x: -max(s['mtime'] for s in groups[x]))
            elif self.sort == 'artist':
                keys = sorted(groups, key=lambda x: (x[1].lower(), x[0].lower()))
            else:
                keys = sorted(groups, key=lambda x: x[0].lower())
            self.fill_grid([(self.cover_of(groups[x][0]), x[0], x[1], ('album', x)) for x in keys],
                           {'home': 'Início', 'recent': 'Adições Recentes'}.get(k, 'Álbuns'))
        elif k in ('artists', 'artist'):
            self.page_artists(self.cur[1] if k == 'artist' else None)
        elif k == 'album':
            self.page_album(self.cur[1])
        elif k == 'playlists':
            items = []
            for n, paths in self.playlists.items():
                first = next((self.by_path[p] for p in paths if p in self.by_path), None)
                items.append((self.cover_of(first) if first else placeholder(200), n,
                              f"{len(paths)} música(s)", ('playlist', n)))
            self.fill_grid(items, 'Playlists')
        elif k == 'songs':
            self.fill_table(self.song_sorted(self.songs), 'Músicas', True)
        elif k == 'playlist':
            lst = [self.by_path[p] for p in self.playlists.get(self.cur[1], []) if p in self.by_path]
            self.fill_table(lst, self.cur[1])
        self.mark_playing()

    def fill_grid(self, items, title):
        self.title.setText(title)
        self.grid.clear()
        for pm, t, sub, desc in items:
            it = QListWidgetItem()
            it.setData(Qt.UserRole, desc)
            it.setData(Qt.UserRole + 1, rounded(pm, 200, 8))
            it.setData(Qt.UserRole + 2, t)
            it.setData(Qt.UserRole + 3, sub)
            it.setSizeHint(QSize(224, 276))
            self.grid.addItem(it)
        self.stack.setCurrentIndex(0)

    def fill_table(self, lst, title, sortable=False):
        self.title.setText(title)
        self.view = lst
        self.hrow = -1
        self.table.clearSelection()
        self.table.setRowCount(len(lst))
        for r, s in enumerate(lst):
            for c, v in ((0, s['title']), (2, fmt(s['dur'])), (3, s['artist']),
                         (4, s['album']), (5, s['genre'])):
                self.table.setItem(r, c, QTableWidgetItem(v))
        hdr = self.table.horizontalHeader()
        hdr.col = COLS.index(self.tsort[0]) if sortable else -1
        hdr.asc = self.tsort[1]
        hdr.viewport().update()
        self.stack.setCurrentIndex(1)

    # ---------- página do álbum ----------
    def ordered(self, l):
        return sorted(l, key=lambda s: (s['disc'], s['n'], s['title'].lower()))

    def page_album(self, key):
        lst = self.ordered([s for s in self.songs if (s['album'], s['aartist']) == key])
        self.title.setText('')
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(40, 40, 40, 30)
        if not lst:
            self.scroll_album.setWidget(w)
            self.stack.setCurrentIndex(2)
            return
        top = QHBoxLayout()
        top.setSpacing(32)
        cov = QLabel()
        cov.setPixmap(rounded(self.covers.get(key) or placeholder(270), 270, 10))
        cov.setFixedSize(270, 270)
        top.addWidget(cov, 0, Qt.AlignTop)
        info = QVBoxLayout()
        info.setSpacing(2)
        info.addStretch()
        info.addWidget(label(key[0], 'font-size: 26px; font-weight: 700;'))
        a = QPushButton(key[1].replace('&', '&&'), objectName='alink')
        a.setCursor(Qt.PointingHandCursor)
        a.clicked.connect(lambda: self.show_view(('artist', key[1]), True))
        info.addWidget(a, 0, Qt.AlignLeft)
        info.addWidget(label(meta(lst), f'color: {GRAY}; font-size: 12px; font-weight: 700;'))
        info.addSpacing(28)
        br = QHBoxLayout()
        br.addWidget(self.btn('shuffle', lambda: self.play_shuffled(lst), 'circ', 16))
        br.addWidget(self.btn('play', lambda: self.play_at(0, lst), 'pill', 16, '  Reproduzir'))
        fk = '||'.join(key)
        fb = self.btn('check', lambda: self.fav_toggle(fk, fb), 'circ', 16)
        self.set_ic(fb, 'check', BLUE if fk in self.favs() else WHITE)
        br.addWidget(fb)
        br.addStretch()
        mb = self.btn('more', lambda: self.more_menu(lst, mb), 'circ', 18)
        br.addWidget(mb)
        info.addLayout(br)
        top.addLayout(info, 1)
        v.addLayout(top)
        v.addSpacing(28)
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet('background: #2c2c2c;')
        v.addWidget(sep)
        v.addSpacing(18)
        nums = track_nums(lst)
        multi = len({s['disc'] for s in lst}) > 1
        disc = None
        pos = 0
        for i, s in enumerate(lst):
            if s['disc'] != disc:
                disc, pos = s['disc'], 0
                if multi:
                    v.addWidget(label(f'Disco {disc}', 'font-size: 16px; font-weight: 700;'))
                    v.addSpacing(6)
            pos += 1
            r = TrackRow(self, lst, i, nums[i], True)
            self.rows.append(r)
            v.addWidget(r)
        v.addStretch()
        self.scroll_album.setWidget(w)
        self.stack.setCurrentIndex(2)

    # ---------- página de artistas ----------
    def page_artists(self, sel):
        self.title.setText('Artistas')
        groups = {}
        for s in self.songs:
            groups.setdefault(s['aartist'], []).append(s)
        names = sorted(groups, key=str.lower)
        self.alist.clear()
        for n in names:
            pm = next((self.covers[(s['album'], s['aartist'])] for s in groups[n]
                       if (s['album'], s['aartist']) in self.covers), None)
            it = QListWidgetItem(QIcon(rounded(pm, 40, circle=True) if pm else avatar(40)), n)
            it.setData(Qt.UserRole, n)
            self.alist.addItem(it)
        if sel not in groups:
            sel = names[0] if names else None
        if sel is not None:
            self.alist.setCurrentRow(names.index(sel))
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(40, 28, 40, 30)
        if sel is not None:
            lst = groups[sel]
            albums = {}
            for s in lst:
                albums.setdefault(s['album'], []).append(s)
            order = sorted(albums, key=lambda a: (albums[a][0]['year'], a.lower()))
            flat = []
            for a in order:
                albums[a] = self.ordered(albums[a])
                flat += albums[a]
            head = QHBoxLayout()
            head.addWidget(label(sel, 'font-size: 26px; font-weight: 700;'))
            head.addWidget(icon_label('chev', WHITE, 18))
            head.addStretch(1)
            head.addWidget(self.btn('play', lambda: self.play_at(0, flat), 'circ', 16))
            head.addWidget(self.btn('shuffle', lambda: self.play_shuffled(flat), 'circ', 16))
            mb = self.btn('more', lambda: self.more_menu(flat, mb), 'circ', 18)
            head.addWidget(mb)
            v.addLayout(head)
            v.addWidget(label(f"{len(order)} {'álbum' if len(order) == 1 else 'álbuns'}, {len(lst)} {'música' if len(lst) == 1 else 'músicas'}",
                              f'color: {GRAY}; font-size: 12px; font-weight: 700;'))
            v.addSpacing(24)
            off = 0
            for a in order:
                l = albums[a]
                nums = track_nums(l)
                row = QHBoxLayout()
                row.setSpacing(28)
                left = QVBoxLayout()
                cov = QLabel()
                cov.setPixmap(rounded(self.cover_of(l[0]), 200, 8))
                cov.setFixedSize(200, 200)
                left.addWidget(cov)
                t = label(total_txt(l), f'color: {GRAY}; font-size: 12px; font-weight: 700;')
                t.setFixedWidth(200)
                t.setWordWrap(True)
                left.addWidget(t)
                left.addStretch()
                rt = QVBoxLayout()
                rt.setSpacing(0)
                rt.addWidget(label(a, 'font-size: 16px; font-weight: 700;'))
                rt.addWidget(label(meta(l), f'color: {GRAY}; font-size: 12px; font-weight: 700;'))
                rt.addSpacing(8)
                for i, s in enumerate(l):
                    r = TrackRow(self, flat, off + i, nums[i], False)
                    self.rows.append(r)
                    rt.addWidget(r)
                rt.addStretch()
                row.addLayout(left)
                row.addLayout(rt, 1)
                v.addLayout(row)
                v.addSpacing(34)
                off += len(l)
        v.addStretch()
        self.scroll_art.setWidget(w)
        self.stack.setCurrentIndex(3)

    # ---------- menus / playlists ----------
    def table_ctx(self, pos):
        r = self.table.rowAt(pos.y())
        if 0 <= r < len(self.view):
            self.song_menu(self.view[r], self.table.viewport().mapToGlobal(pos))

    def song_menu(self, s, gpos):
        m = QMenu(self)
        sub = m.addMenu('Adicionar à playlist')
        if not self.playlists:
            sub.addAction('(crie uma playlist antes)').setEnabled(False)
        for n in self.playlists:
            a = sub.addAction(n)
            a.triggered.connect(lambda _=False, n=n: self.pl_add(n, s))
        if self.cur and self.cur[0] == 'playlist':
            a = m.addAction('Remover da playlist')
            a.triggered.connect(lambda _=False: self.pl_rm(self.cur[1], s))
        m.exec(gpos)

    def pl_add(self, name, s):
        if s['path'] not in self.playlists[name]:
            self.playlists[name].append(s['path'])
            self.save_pl()

    def pl_rm(self, name, s):
        if s['path'] in self.playlists[name]:
            self.playlists[name].remove(s['path'])
            self.save_pl()
            self.render()

    def song_sorted(self, lst):
        k, asc = self.tsort
        keyf = {'title': lambda s: s['title'].lower(),
                'dur': lambda s: s['dur'],
                'artist': lambda s: (s['artist'].lower(), s['album'].lower(), s['disc'], s['n']),
                'album': lambda s: (s['album'].lower(), s['disc'], s['n']),
                'genre': lambda s: s['genre'].lower(),
                'plays': lambda s: self.plays.get(s['path'], 0),
                'recent': lambda s: s['mtime'],
                'fav': lambda s: s['path'] in self.fav_songs}[k]
        return sorted(lst, key=keyf, reverse=not asc)

    def on_header(self, i):
        key = COLS[i]
        if key is None:
            return
        asc = (not self.tsort[1]) if self.tsort[0] == key else key not in ('plays', 'fav')
        self.tsort = (key, asc)
        if self.cur and self.cur[0] == 'songs':
            self.render()

    def set_hrow(self, r):
        if r != self.hrow:
            self.hrow = r
            self.table.viewport().update()

    def cell_clicked(self, r, c):
        if not 0 <= r < len(self.view):
            return
        s = self.view[r]
        if c == 1:
            self.song_menu(s, QCursor.pos())
        elif c == 6:
            self.fav_songs ^= {s['path']}
            self.cfg.setValue('fav_songs', list(self.fav_songs))
            self.table.viewport().update()

    def song_key(self):
        if self.sort == 'artist':
            return lambda s: (s['artist'].lower(), s['title'].lower())
        if self.sort == 'recent':
            return lambda s: -s['mtime']
        return lambda s: s['title'].lower()

    def set_sort(self, k):
        self.sort = k
        self.tsort = {'title': ('title', True), 'artist': ('artist', True), 'recent': ('recent', False)}[k]
        self.render()

    def sort_menu(self):
        m = QMenu(self)
        for key, text in (('title', 'Título'), ('artist', 'Artista'), ('recent', 'Adicionados recentemente')):
            a = m.addAction(text)
            a.setCheckable(True)
            a.setChecked(self.sort == key)
            a.triggered.connect(lambda _=False, k=key: self.set_sort(k))
        m.exec(QCursor.pos())

    def app_menu(self, pos=None):
        m = QMenu(self)
        m.addAction('Trocar pasta de músicas').triggered.connect(lambda: self.ask_folder())
        m.addAction('Baixar músicas').triggered.connect(lambda: self.nav_to(('download',)))
        m.exec(pos or self.b_menu.mapToGlobal(self.b_menu.rect().bottomLeft()))

    def nav_to(self, desc):
        self.select_side(desc)
        self.hist = []
        self.show_view(desc, False)

    def show_queue(self):
        m = QMenu(self)
        up = range(self.idx + 1, min(len(self.queue), self.idx + 13)) if self.idx >= 0 else []
        if not up:
            m.addAction('Fila vazia').setEnabled(False)
        for i in up:
            s = self.queue[i]
            a = m.addAction(f"{s['title']} — {s['artist']}")
            a.triggered.connect(lambda _=False, i=i: self.play_at(i))
        m.exec(self.b_queue.mapToGlobal(self.b_queue.rect().bottomLeft()))

    def favs(self):
        return set(self.cfg.value('favs', [], type=list))

    def fav_toggle(self, k, b):
        s = self.favs()
        s ^= {k}
        self.cfg.setValue('favs', list(s))
        self.set_ic(b, 'check', BLUE if k in s else WHITE)

    def more_menu(self, lst, btn):
        m = QMenu(self)
        m.addAction('Reproduzir').triggered.connect(lambda: self.play_at(0, lst))
        m.addAction('Reproduzir em ordem aleatória').triggered.connect(lambda: self.play_shuffled(lst))
        sub = m.addMenu('Adicionar tudo à playlist')
        if not self.playlists:
            sub.addAction('(crie uma playlist antes)').setEnabled(False)
        for n in self.playlists:
            a = sub.addAction(n)
            a.triggered.connect(lambda _=False, n=n: self.pl_add_many(n, lst))
        m.exec(btn.mapToGlobal(btn.rect().bottomLeft()))

    def pl_add_many(self, name, lst):
        for s in lst:
            if s['path'] not in self.playlists[name]:
                self.playlists[name].append(s['path'])
        self.save_pl()

    # ---------- downloader (yt-dlp) ----------
    def build_hub(self):
        w = QWidget(objectName='page')
        w.setAttribute(Qt.WA_StyledBackground, True)
        v = QVBoxLayout(w)
        v.setContentsMargins(40, 36, 40, 30)
        v.setSpacing(20)
        row = QHBoxLayout()
        row.setSpacing(20)
        yt = SourceCard('YouTube', 'Baixa a versão em áudio da música; se não existir, o áudio do vídeo', 'yt', '#ff3b30', '#a8001c', True, 170)
        sc = SourceCard('SoundCloud', 'Baixar faixas e sets', 'sc', '#ff8a00', '#ff3d00', True, 170)
        yt.clicked.connect(lambda: self.show_view(('download', 'youtube'), True))
        sc.clicked.connect(lambda: self.show_view(('download', 'soundcloud'), True))
        row.addWidget(yt, 1)
        row.addWidget(sc, 1)
        v.addLayout(row)
        v.addWidget(SourceCard('Em breve', 'Mais fontes chegando', None, '#232323', '#232323', False, 220))
        v.addStretch(1)
        return w

    def build_download(self):
        self.dl_thread = None
        self.dl_source = 'youtube'
        w = QWidget(objectName='page')
        w.setAttribute(Qt.WA_StyledBackground, True)
        v = QVBoxLayout(w)
        v.setContentsMargins(40, 30, 40, 30)
        v.setSpacing(12)
        intro = label('Cole links ou digite o nome da música, um por linha. '
                      'Baixe apenas o que você tem direito de baixar.',
                      f'color: {GRAY}; font-size: 13px;')
        intro.setWordWrap(True)
        v.addWidget(intro)
        self.dl_urls = QPlainTextEdit()
        self.dl_urls.setPlaceholderText('https://www.youtube.com/watch?v=...')
        self.dl_urls.setFixedHeight(110)
        v.addWidget(self.dl_urls)
        row = QHBoxLayout()
        self.dl_fmt = QComboBox()
        self.dl_fmt.addItems(['MP3', 'M4A', 'FLAC', 'OPUS'])
        self.dl_pl = QCheckBox('Baixar playlists inteiras')
        row.addWidget(QLabel('Formato'))
        row.addWidget(self.dl_fmt)
        row.addSpacing(16)
        row.addWidget(self.dl_pl)
        row.addStretch()
        v.addLayout(row)
        br = QHBoxLayout()
        self.dl_go = self.btn('dl', self.dl_start, 'pill', 16, '  Baixar')
        self.dl_stop = QPushButton('Cancelar', objectName='pill')
        self.dl_stop.setEnabled(False)
        self.dl_stop.clicked.connect(self.dl_cancel)
        opn = QPushButton('Abrir pasta', objectName='pill')
        opn.clicked.connect(self.dl_open)
        for b in (self.dl_go, self.dl_stop, opn):
            br.addWidget(b)
        br.addStretch()
        v.addLayout(br)
        self.dl_bar = QProgressBar()
        self.dl_bar.setTextVisible(False)
        v.addWidget(self.dl_bar)
        self.dl_status = label('', f'color: {GRAY}; font-size: 12px;')
        v.addWidget(self.dl_status)
        if not find_ffmpeg():
            note = label('A conversão de formato não está disponível neste computador: o áudio será salvo em m4a.',
                         f'color: {GRAY}; font-size: 12px;')
            note.setWordWrap(True)
            v.addWidget(note)
        self.dl_logbox = QPlainTextEdit()
        self.dl_logbox.setReadOnly(True)
        self.dl_logbox.hide()
        v.addWidget(self.dl_logbox, 1)
        self.dl_fill = QWidget()
        v.addWidget(self.dl_fill, 1)
        return w

    def dl_dest(self):
        d = self.cfg.value('dl_dir', '')
        if d and os.path.isdir(d):
            return d
        base = self.folders[0] if self.folders else os.path.join(os.path.expanduser('~'), 'Music')
        return os.path.join(base, 'MigsMusic Downloads')

    def dl_start(self):
        items = [l.strip() for l in self.dl_urls.toPlainText().splitlines() if l.strip()]
        if not items:
            self.dl_status.setText('Cole um link ou digite o nome de uma música.')
            return
        if self.dl_thread is not None and self.dl_thread.isRunning():
            return
        start = self.dl_dest()
        if not os.path.isdir(start):
            start = os.path.dirname(start)
        dest = QFileDialog.getExistingDirectory(self, 'Escolha a pasta para salvar os downloads', start)
        if not dest:
            self.dl_status.setText('Download cancelado: nenhuma pasta escolhida.')
            return
        self.cfg.setValue('dl_dir', dest)
        self.dl_thread = Downloader(items, dest, self.dl_fmt.currentText().lower(),
                                    self.dl_pl.isChecked(), find_ffmpeg(), self.dl_source)
        self.dl_thread.progress.connect(lambda p, t: (self.dl_bar.setValue(p), self.dl_status.setText(t)))
        self.dl_thread.log.connect(lambda m: self.dl_logbox.appendPlainText(m.strip()))
        self.dl_thread.done.connect(self.dl_done)
        self.dl_go.setEnabled(False)
        self.dl_stop.setEnabled(True)
        self.dl_bar.setValue(0)
        self.dl_status.setText('Iniciando…')
        self.dl_fill.hide()
        self.dl_logbox.show()
        self.dl_logbox.appendPlainText('Salvando em: ' + dest)
        self.dl_thread.start()

    def dl_cancel(self):
        if self.dl_thread is not None:
            self.dl_thread.cancel()
            self.dl_status.setText('Cancelando…')

    def dl_done(self, ok, fail):
        self.dl_go.setEnabled(True)
        self.dl_stop.setEnabled(False)
        self.dl_status.setText(f'Concluído: {ok} baixada(s), {fail} com erro.')
        if ok:
            self.dl_bar.setValue(100)
            self.scan()

    def dl_open(self):
        d = self.dl_dest()
        os.makedirs(d, exist_ok=True)
        if hasattr(os, 'startfile'):
            os.startfile(d)

    # ---------- reprodução ----------
    def play_shuffled(self, lst):
        if not lst:
            return
        self.shuffle = True
        self.mark(self.b_shuf, True)
        self.play_at(random.randrange(len(lst)), lst)

    def play_at(self, i, lst=None):
        if lst is not None:
            self.queue = lst
        if not self.queue:
            return
        self.idx = i % len(self.queue)
        s = self.queue[self.idx]
        self.player.setSource(QUrl.fromLocalFile(s['path']))
        self.player.play()
        self.counted = False
        self.fade_in()
        self.np_idle.hide()
        self.np_info.show()
        self.lt.setText(s['title'])
        self.la.setText(f"{s['artist']} — {s['album']}")
        pm = self.covers.get((s['album'], s['aartist']))
        self.cover.setPixmap((pm or placeholder(52)).scaled(52, 52, Qt.KeepAspectRatio,
                                                            Qt.SmoothTransformation))
        self.mark_playing()

    def mark_playing(self):
        self.table.viewport().update()
        p = self.queue[self.idx]['path'] if 0 <= self.idx < len(self.queue) else None
        for r in self.rows:
            try:
                r.set_playing(r.s['path'] == p)
            except RuntimeError:
                pass

    def next(self, auto):
        if not self.queue:
            return
        if auto and self.repeat == 2:
            return self.play_at(self.idx)
        if self.shuffle:
            return self.play_at(random.randrange(len(self.queue)))
        if auto and self.repeat == 0 and self.idx == len(self.queue) - 1:
            return
        self.play_at(self.idx + 1)

    def toggle(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        elif self.idx >= 0:
            self.player.play()
        elif self.view:
            self.play_at(max(0, self.table.currentRow()), self.view)

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        self.mark(self.b_shuf, self.shuffle)

    def toggle_repeat(self):
        self.repeat = (self.repeat + 1) % 3
        self.set_ic(self.b_rep, 'repeat1' if self.repeat == 2 else 'repeat',
                    BLUE if self.repeat else WHITE)

    def mark(self, b, on):
        self.set_ic(b, b.ic, BLUE if on else WHITE)

    def on_pos(self, p):
        if not self.seek.dragging:
            self.seek.setValue(p)
        if not self.counted and p > 30000 and 0 <= self.idx < len(self.queue):
            self.counted = True
            path = self.queue[self.idx]['path']
            self.plays[path] = self.plays.get(path, 0) + 1
            self.cfg.setValue('plays', json.dumps(self.plays))
            self.table.viewport().update()

    def prev(self):
        if self.player.position() > 3000:
            self.player.setPosition(0)
        else:
            self.play_at(self.idx - 1)

    def set_vol(self, v):
        self.vol_val = v / 100
        self.audio.setVolume(self.vol_val)

    def fade_in(self):
        a = QVariantAnimation(self)
        a.setDuration(450)
        a.setStartValue(0.0)
        a.setEndValue(1.0)
        a.valueChanged.connect(lambda v: self.audio.setVolume(float(v) * self.vol_val))
        a.start()
        self._fin = a

    def toggle_mute(self):
        m = not self.audio.isMuted()
        self.audio.setMuted(m)
        self.set_ic(self.b_vol, 'mute' if m else 'volume')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    try:  # faz a barra de tarefas usar o ícone do app
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('MigsMusic.App')
    except Exception:
        pass
    app.setStyle('Fusion')
    app.setWindowIcon(make_app_icon())
    app.setStyleSheet(QSS)
    w = Main()
    w.show()
    dark_titlebar(w)
    sys.exit(app.exec())
