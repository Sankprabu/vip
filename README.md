# ViP Browser

<p align="center">
  <img src="assets/browser_icon.ico" alt="ViP Browser Logo" width="200"/>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

ViP Browser adalah web browser ringan dan aman yang dibuat dengan PyQt6. Browser ini menawarkan fitur modern sambil tetap menjaga privasi dan keamanan pengguna.

## ✨ Fitur

- 🔒 **Prioritas Privasi**
  - Mode Penyamaran
  - Do Not Track (DNT)
  - Kontrol Privasi Global (GPC)
  - Manajemen Client Hints

- 🎨 **UI Modern**
  - Mode Gelap/Terang
  - Tampilan Desktop/Mobile
  - Manajemen Tab
  - Antarmuka Bersih

- 📚 **Fitur Pengguna**
  - Manajemen Bookmark
  - Riwayat Browsing
  - Pengelola Unduhan
  - Pencarian dalam Halaman
  - Manajemen Cache

## 🚀 Instalasi

### Prasyarat
- Python 3.8+
- pip (Python package manager)

### Langkah-langkah

1. Clone repositori
```bash
git clone https://github.com/yourusername/vip-browser.git
cd vip-browser
```

2. Install the required packages:

```bash
pip install PyQt6 user_agents
```
3. Make sure you have the necessary assets (like icons) in the assets directory.

## Usage

To run the browser, execute the following command in your terminal:

```bash
python main.py
```
This will launch the ViP Browser, allowing you to start browsing the web.

## Configuration

The browser settings are stored in a JSON file named settings.json. You can customize the following options:

- desktop_mode: Set to true to enable desktop mode by default.
- dark_mode: Set to true to enable dark mode by default.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to the PyQt community for providing a powerful framework for building desktop applications.
- Special thanks to all contributors and users who support the development of ViP Browser.
