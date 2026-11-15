# MigsMusic

A modern, dark desktop music player for Windows that plays the music already stored on your computer, with a built-in audio downloader for YouTube and SoundCloud.

The interface is inspired by the Apple Music desktop app: sidebar navigation, album grids, artist pages and a sortable song table. MigsMusic is an independent project and is not affiliated with or endorsed by Apple.

## Features

### Player
- Plays local files: `mp3`, `m4a`, `flac`, `ogg`, `opus`, `wav`, `wma`, `aac`
- Play / pause, previous, next, shuffle, repeat (off, all, one)
- Seek bar and volume slider that jump to wherever you click, plus mute
- Up-next queue menu
- Smooth volume fade-in when a track starts
- `Space` toggles play / pause

### Library
- Scans a folder (and all its subfolders) and reads tags and embedded cover art
- **Home** and **Recently Added**: album grids, newest first
- **Albums** and **Artists**: grid of covers, album pages with track lists, artist pages with all their albums
- **Songs**: a sortable table with Title, Time, Artist, Album, Genre, Favorite star and Play count
- Hover over a track to reveal the play button
- Favorites and play counts are remembered between sessions
- **Playlists**: create playlists, add songs from the context menu, delete with a right-click
- Search across titles, artists and albums

### Downloader
- **YouTube**: looks for the audio version of a song first (for example the auto-generated "Topic" upload or an "Official Audio" upload). If none exists, it downloads the audio of the video.
- **SoundCloud**: downloads tracks and sets
- Paste links or just type a song name (one per line)
- Output formats: MP3, M4A, FLAC, OPUS, with cover art and tags embedded
- Optional download of entire playlists; file names contain only the song title
- You choose the destination folder every time you download
- Downloaded songs appear in your library automatically

### Other
- Available in **English** and **Portuguese** (it follows your system language and can be switched from the `···` menu)
- Smooth animated scrolling and hover effects
- Custom vector icons drawn in code, no image assets required

## Requirements

- Windows 10 or 11 (the code is cross-platform Qt, but the build script and some touches such as the dark title bar target Windows)
- Python 3.12 recommended (newer versions may not have PySide6 wheels yet)

Python packages (see `requirements.txt`):

| Package | Used for |
| --- | --- |
| [PySide6](https://pypi.org/project/PySide6/) | Qt user interface and audio playback |
| [mutagen](https://pypi.org/project/mutagen/) | Reading and editing audio tags and cover art |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Downloading audio from YouTube and SoundCloud |
| [imageio-ffmpeg](https://pypi.org/project/imageio-ffmpeg/) | Bundled FFmpeg for format conversion |
| [PyInstaller](https://pyinstaller.org/) | Building the `.exe` (build time only) |

## Getting started

### Run from source

1. Download this repository (green **Code** button, then **Download ZIP**) and extract it, or clone it with Git.
2. Open a terminal in the project folder and run:

```bash
pip install -r requirements.txt
python MigsMusic.py
```

On launch the app asks for your music folder. It starts the dialog in the folder you used last time; cancel it to keep the previous folder.

### Build the `.exe`

Double-click `gerar_exe.bat`, or run:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --clean ^
  --collect-submodules yt_dlp --collect-all imageio_ffmpeg ^
  --icon MigsMusic.ico --name MigsMusic MigsMusic.py
```

The executable is created at `dist/MigsMusic.exe`. FFmpeg is bundled inside it, so no extra installation is needed.

## Usage

| Action | How |
| --- | --- |
| Choose or change the music folder | Dialog at startup, or `···` menu, then *Change music folder* |
| Play a track | Click the play button that appears on hover, or double-click the track |
| Add a song to a playlist | Right-click the song, or use the `···` button on its row |
| Sort songs | Click a column header on the *Songs* page |
| Favorite a song | Click the star on its row |
| Change language | `···` menu, then *Idioma / Language* (the app restarts) |
| Download music | *Download music* in the sidebar, pick a source, paste links or song names |

## Project structure

```
MigsMusic/
├── MigsMusic.py      # the whole application
├── MigsMusic.ico     # application icon
├── gerar_exe.bat     # one-click Windows build script
├── requirements.txt
├── LICENSE
├── .gitignore
└── README.md
```

Settings (music folder, playlists, favorites, play counts, language) are stored with Qt's `QSettings`, which uses the Windows registry.

## Troubleshooting

- **Downloads stopped working for some links**: sites change often. Update the downloader with `pip install -U yt-dlp` and rebuild the `.exe`.
- **Songs show as "Unknown artist / Unknown album"**: the files have no tags. Tag them with any tag editor, or download them with the built-in downloader, which embeds tags.
- **The `.exe` build fails**: use Python 3.12 and make sure `MigsMusic.ico` is in the same folder as the script.

## Legal notice

Only download content that you own or have the right to download. You are responsible for complying with the terms of service of each platform and with the copyright laws of your country. The authors do not encourage or condone piracy.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the downloading engine
- [FFmpeg](https://ffmpeg.org/) for audio conversion
- [Qt for Python (PySide6)](https://doc.qt.io/qtforpython-6/) and [mutagen](https://github.com/quodlibet/mutagen)

## License

MigsMusic is released under the [MIT License](LICENSE). The third-party libraries listed above keep their own licenses, which also apply when you distribute a built `.exe` that bundles them.
