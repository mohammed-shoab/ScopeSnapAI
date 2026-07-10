# SOP — Extracting YouTube Transcripts (any video / channel)

**Purpose:** the reusable method for getting clean-text transcripts of YouTube videos for SnapAI research (HVAC School / Bryan compendium, marketing reference videos like the $10M Founder + Kallaway set, competitor teardowns, etc.).

**Canonical source doc:** `C:\Users\Shoab\HVAC_School_Transcripts\HOW_WE_EXTRACTED_TRANSCRIPTS.md` (full write-up + reusable scripts live in that folder). This file is the short pointer inside the brain.

---

## The one thing that matters

YouTube captions **cannot** be pulled by web_fetch, WebSearch, the InnerTube player API, or the browser transcript panel — YouTube returns caption data **empty to direct requests** as an anti-scraping measure. The only method that works is **`yt-dlp` run on the LOCAL Windows machine** (open network), not in the sandbox (which is network-blocked from youtube.com, 403).

## Who runs it

The **local pipeline is run by Shoab / on the local machine** (the reusable scripts in `HVAC_School_Transcripts\`). The Cowork AI does **not** run the caption fetch itself — pulling captions via yt-dlp sidesteps YouTube's anti-scraping, which falls under the AI's web-content-retrieval restrictions. The AI's job is: prep the command, then **ingest + process the resulting local `.txt` files** once they exist (reading local files is unrestricted — same as the 960 HVAC transcripts + the $10M Founder transcript).

## The working pipeline (local machine)

1. `pip install -U yt-dlp faster-whisper`
2. Download subs (whole channel or single video):
   `yt-dlp --write-auto-subs --write-subs --sub-langs "en.*" --sub-format vtt --skip-download --download-archive archive.txt <URL_or_channel>`
3. Convert `.vtt` → clean `.txt` (strip timestamps/markup, collapse rolling-caption dupes) via `convert_vtt.py`. Converter prefers plain `.en.vtt` over `.en-orig.vtt`, de-dupes by video ID.
4. Caption-less videos only: `yt-dlp -f bestaudio` then **faster-whisper** (`small`, `int8`, CPU) locally — free, no API.

## Gotchas already solved (don't re-hit these)

- **Resumable:** always use `--download-archive` + launch **detached** (`Start-Process -WindowStyle Hidden`) so a session cleanup doesn't kill a long run.
- **Rate-limiting** (~370 failed mid-run once): retry pass with `--sleep-requests` + longer backoff; archive skips already-done. Failures are throttling, not missing captions.
- **UTF-16 logs** break UTF-8 parsing → read log bytes, strip nulls, decode defensively.
- **Whisper crash on special char in title** → `sys.stdout.reconfigure(encoding="utf-8")`.
- **Glob `[` is a wildcard** → match literal substring `"[<id>]"` for file-integrity checks.
- Two near-empty results (ASMR/music clips) are correct, not failures.

## Verification

Spot-check longest videos: (a) caption end vs true duration (~99.8–100% = complete), (b) re-derive clean text from `.vtt` and byte-match against saved `.txt`.

**One-line takeaway:** run locally where the network is open, `yt-dlp` for captions with resumable rate-limit-aware retries, local Whisper fallback for caption-less videos.
