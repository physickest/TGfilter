
# TGfilter

An automated, serverless Telegram channel synchronization and filtering bot designed to extract high-value information while automatically blocking low-value noise, advertisements, and spoilers. 

**Note on Vision Models:** The experimental vision-model pipeline (using DINOv2/OpenCLIP) for Zero-day visual spoiler detection is currently marked as "deprecated for now". The system currently operates on a highly robust text, metadata, and regex-based filtering engine.

---

## 🌟 Key Features

* **Serverless Headless Deployment:** Runs autonomously on GitHub Actions using Ubuntu environments and Python 3.9. No dedicated server is required.
* **Matrix Concurrency Architecture:** The workflow (`TG_Purifier_Matrix_Service`) uses a GitHub Actions matrix strategy to process multiple target channels (e.g., `Seele_Leaks`, `homokeqing`) in parallel without interference.
* **Deep Content Penetration:** The extraction engine does not just read message text. It scans media captions, webpage preview descriptions, and file names to ensure no spoiler or ad slips through.
* **Intelligent Media Group Handling:** If a single image within a multi-image post (grouped ID) triggers the blocklist, the entire album is safely discarded.
* **Stateful Watermark Tracking:** Automatically queries the destination channel for the last forwarded message ID to establish a "watermark," ensuring efficient incremental fetching without needing an external database.

---

## 🛠️ Configuration & Setup

### 1. Generate a Telegram Session
Because this bot runs headlessly, you must authenticate it with your Telegram account first.
1. Obtain your `API_ID` and `API_HASH` from Telegram. (The default uses ID `2040` and Hash `b18441a1ff607e10a989891a5462e627`).
2. Install dependencies: `pip install telethon pysocks`.
3. Run the session generator locally:
   ```bash
   python get_session.py

4. Follow the prompt to log in. Copy the outputted `STRING_SESSION`.

### 2. Configure GitHub Secrets
In your GitHub repository, navigate to **Settings > Secrets and variables > Actions** and add the following repository secrets:
* `TG_API_ID`: Your Telegram API ID.
* `TG_API_HASH`: Your Telegram API Hash.
* `TG_STRING_SESSION`: The session string generated in step 1.
* `PRIVATE_CHANNEL_ID`: The destination channel ID where purified messages will be forwarded.

### 3. Customize Filter Rules
Edit the `CHANNEL_RULES` dictionary in `sync_purifier.py` to target your specific channels and establish keyword/sender blocklists. For example, the current setup blocks keywords like `ZZZ`, `HI3`, `AKEndfield`, and `Endfield`, as well as senders flagged as `广告源` (Ads).

```python
CHANNEL_RULES = {
    'Seele_Leaks': {
        'blocked_keywords': ['ZZZ', 'HI3', 'AKEndfield', 'Endfield'],
        'blocked_senders': ['广告源']
    }
}
```

---

## 📜 Future Roadmap: Addressing the OOD Challenge
While the text-filtering pipeline is highly effective, visual "Zero-day" spoilers (unseen image leaks) remain a challenge for static models due to Knowledge Cutoff. 

Future updates aim to implement a "One-shot visual interception pipeline" using semantic perception (DINOv2/OpenCLIP) and Cosine Similarity to intercept images based on dynamic feature reference caches rather than pre-trained classification labels.

## 📄 License
This project is licensed under the Apache License, Version 2.0.
```
