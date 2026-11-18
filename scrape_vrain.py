import csv
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright

URL = "https://vrain.vn/20/overview?public_map=windy"
OUTPUT = Path("data/vrain_hourly.csv")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(locale="vi-VN")

        page.goto(URL, wait_until="domcontentloaded", timeout=90_000)
        page.wait_for_selector(".station .station-row-1", timeout=60_000)

        collected = {}

        for _ in range(40):
            rows = page.locator(".station").evaluate_all("""
                cards => cards.map(card => {
                    const row = card.querySelector('.station-row-1');
                    const parts = row
                        ? Array.from(row.children).map(x => x.innerText.trim())
                        : [];

                    return {
                        station: parts[0] || '',
                        rainfall_text: parts[1] || '',
                        location: card.querySelector('.station-row-2')
                            ?.innerText.trim() || ''
                    };
                })
            """)

            for row in rows:
                if row["station"]:
                    collected[(row["station"], row["location"])] = row

            pane = page.locator(".landing-content-container")
            if pane.count():
                pane.evaluate("(el) => el.scrollTop = el.scrollHeight")

            page.wait_for_timeout(400)

        browser.close()

    if not collected:
        raise RuntimeError("Không tìm thấy trạm trên trang Vrain.")

    timestamp = datetime.now(
        ZoneInfo("Asia/Ho_Chi_Minh")
    ).isoformat(timespec="seconds")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    file_exists = OUTPUT.exists()

    with OUTPUT.open("a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "collected_at_vn",
                "station",
                "rainfall_text",
                "rainfall_mm",
                "location",
            ],
        )

        if not file_exists:
            writer.writeheader()

        for row in collected.values():
            match = re.search(r"[\d]+(?:[.,]\d+)?", row["rainfall_text"])
            rainfall_mm = (
                float(match.group().replace(",", ".")) if match else ""
            )

            writer.writerow({
                "collected_at_vn": timestamp,
                "station": row["station"],
                "rainfall_text": row["rainfall_text"],
                "rainfall_mm": rainfall_mm,
                "location": row["location"],
            })

    print(f"Đã ghi {len(collected)} trạm lúc {timestamp} vào {OUTPUT}")


if __name__ == "__main__":
    main()
