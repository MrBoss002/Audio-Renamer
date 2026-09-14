<div align="center">

<img src="https://i.ibb.co/HDtx1FcD/file-22.jpg" alt="Bot Preview" width="25%">

# ⚡ DeadPool Audio Renamer

**A high-performance, lightweight Telegram bot built with `python-telegram-bot` and MongoDB, designed for advanced audio/video renaming, custom metadata injection, permanent thumbnail management, and automated caption styling.**

<br>

  <a href="https://t.me/BossAudioRenamerBot">
    <img src="https://img.shields.io/badge/_𝗧𝗥𝗬_𝗟𝗜𝗩𝗘_𝗕𝗢𝗧-24A1EF?style=for-the-badge&logo=telegram&logoColor=white" alt="Try Live Bot">
</a>

</div>
  
---

## ✨ Features

* **⚙️ Interactive Settings Hub**: Manage custom captions, audio titles, artist names, and permanent thumbnails on the fly.
* **🖼️ Instant Dashboard Refresh**: Automatically displays an updated settings dashboard card right after a change is saved so you can configure next options immediately.
* **🔒 Force Subscription (F-Sub)**: Restricts bot access to members of your mandatory update/support channels.
* **⚡ Blazing Fast Architecture**: Modular 3-file structure (`config.py`, `database.py`, `main.py`) optimized for zero bloat and rapid response times.

---

## 🛠️ Environment Variables

Configure the following keys in your hosting provider's environment settings:

| Variable Name | Description | Required |
| :--- | :--- | :--- |
| `BOT_TOKEN` | Your Telegram Bot Token from [@BotFather](https://t.me/BotFather) | **Yes** |
| `MONGO_URI` | Your MongoDB Connection String (from MongoDB Atlas) | **Yes** |
| `OWNER_USERNAME` | Your Telegram Username (e.g., `@YourUsername`) | **Yes** |
| `UPDATE_CHANNEL` | Public link or URL to your update channel | **Yes** |
| `SUPPORT_GROUP` | Public link or URL to your support group/chat | **Yes** |
| `CHANNEL_1_ID` | Telegram Channel ID 1 for Force Subscription | No |
| `CHANNEL_1_LINK` | Invite link for Channel 1 | No |
| `CHANNEL_2_ID` | Telegram Channel ID 2 for Force Subscription | No |
| `CHANNEL_2_LINK` | Invite link for Channel 2 | No |

---

## 🚀 Deployment Guide

1. **Star this repository** to support the project! ⭐ &nbsp;&nbsp; <a href="https://github.com/MrBoss002/Audio-Renamer">
    <img src="https://img.shields.io/badge/Star%20Repo-1f2328?style=for-the-badge&logo=github&logoColor=white" alt="Star Repo">
  </a>

2. **Fork this repository** to your own GitHub account. 🍴 &nbsp;&nbsp; <a href="https://github.com/MrBoss002/Audio-Renamer/fork">
    <img src="https://img.shields.io/badge/Fork%20Repo-1f2328?style=for-the-badge&logo=git&logoColor=white" alt="Fork Repo">
  </a>

3. Choose your preferred cloud hosting provider below and deploy using your forked repo:

<br>

<p align="center">
  <a href="https://render.com/deploy?repo=https://github.com/MrBoss002/Audio-Renamer">
    <img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render">
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://app.koyeb.com/deploy?type=git&repository=https://github.com/MrBoss002/Audio-Renamer&branch=main&name=audio-renamer">
    <img src="https://www.koyeb.com/static/images/deploy/button.svg" alt="Deploy to Koyeb">
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://railway.app/new/template?template=https://github.com/MrBoss002/Audio-Renamer">
    <img src="https://railway.app/button.svg" alt="Deploy on Railway">
  </a>
</p>

<br>

### Universal Configuration Settings
If your platform requires manual command inputs during setup, use these standard parameters:
* **Build Command:** `pip install -r requirements.txt`
* **Start / Run Command:** `python main.py`
* Remember to add all required **Environment Variables** listed above in your dashboard settings before starting the service.

> **⚠️ Note on Vercel:** Vercel is optimized for serverless functions and short-lived web applications, whereas Telegram long-polling bots require persistent background processes. We recommend using Render, Koyeb, or Railway for optimal bot performance.

---

## 📄 License
> This project is open-source software licensed under the **GNU General Public License v3.0 (GNU GPLv3)**. You are free to use, modify, and distribute this software under the terms of the license.

---

<div align="center">

## ☕ Support & Community

If this Audio Renamer bot saved you time or enhanced your workflow, consider supporting the ongoing development of this project!

| ☕ Support Developer | 🌐 Official Channel | ⛑ Need Assistance |
| :---: | :---: | :---: |
| [![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/MrBoss002) | [![Powered By](https://img.shields.io/badge/Powered%20By-%40MrBossTG-FF0055?style=for-the-badge&logo=telegram&logoColor=blue)](https://t.me/MrBossTG) | [![Dev Help](https://img.shields.io/badge/Contact-Developer-229ED9?style=for-the-badge&logo=telegram&logoColor=blue)](https://t.me/ZeroTwoCare) |

<br />

[![Developed By](https://img.shields.io/badge/Developed%20By-%40MrBoss002-00C853?style=flat-square&logo=github)](https://github.com/MrBoss002)

**DeadPool Audio Renamer** • Built with ❤️ for the open-source community.

</div>

