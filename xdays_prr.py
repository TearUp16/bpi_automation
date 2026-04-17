import re
import os
import pandas as pd # type: ignore
from playwright.sync_api import Playwright, sync_playwright # type: ignore
from datetime import datetime, timedelta


def get_target_date():
    today = datetime.now()
    if today.weekday() == 0:
        return today - timedelta(days=3)
    else:
        return today - timedelta(days=2)


def format_date(date_obj):
    return date_obj.strftime("%Y-%m-%d")


def fix_account_numbers(file_path):
    df = pd.read_csv(file_path, dtype=str)
    df.columns = df.columns.str.strip()

    # -------------------------------
    # FIX ACCOUNT NUMBER
    # -------------------------------
    if "Account No." in df.columns:
        def convert_value(x):
            try:
                if "E+" in str(x):
                    return '{:.0f}'.format(float(x))
                return x
            except:
                return x

        df["Account No."] = df["Account No."].apply(convert_value)

    # -------------------------------
    # LOAD REFERENCE
    # -------------------------------
    reference_path = os.path.join(os.path.dirname(__file__), "Reference.xlsx")

    if os.path.exists(reference_path):
        ref_df = pd.read_excel(reference_path, dtype=str)
        ref_df.columns = ref_df.columns.str.strip()

        # STATUS mapping
        status_map = dict(zip(
            ref_df["Status"].str.strip().str.upper(),
            ref_df["Final Status"]
        ))

        df["STATUS"] = df["Status"].str.strip().str.upper().map(status_map)
        df["STATUS"] = df["STATUS"].replace("UNKNOWN", "").fillna("0")

        # -------------------------------
        # 🔥 FIXED LOOKUP KEY (MATCH REFERENCE)
        # -------------------------------
        ref_df["lookup_key"] = (
            ref_df["Cycle"].str.strip().str.upper() +
            pd.to_datetime(ref_df["Date"], errors="coerce", dayfirst=True).dt.strftime("%d/%m/%Y")
        )

        cutoff_map = dict(zip(ref_df["lookup_key"], ref_df["Cut off"]))

    else:
        print("⚠️ Reference file not found:", reference_path)
        df["STATUS"] = ""
        cutoff_map = {}

    # -------------------------------
    # 🔥 FIXED CYCLE FORMAT
    # -------------------------------
    df["CYCLE"] = "CYCLE " + df["Card No."].str[:2].fillna("")

    # -------------------------------
    # MONTH EXTRACTED
    # -------------------------------
    df["Month Extracted"] = pd.to_datetime(
        df["Date"], errors="coerce", dayfirst=True
    ).dt.strftime("%b")

    # -------------------------------
    # 🔥 FIXED LOOKUP KEY (MATCH FORMAT EXACTLY)
    # -------------------------------
    df["lookup_key"] = (
        df["CYCLE"].str.strip().str.upper() +
        pd.to_datetime(df["Date"], errors="coerce", dayfirst=True).dt.strftime("%d/%m/%Y")
    )

    df["Month Cut Off"] = df["lookup_key"].map(cutoff_map).fillna("")
    df.drop(columns=["lookup_key"], inplace=True)

    # -------------------------------
    # FINAL COLUMN SELECTION
    # -------------------------------
    desired_columns = [
        "STATUS",
        "CYCLE",
        "Month Cut Off",
        "Month Extracted",
        "S.No",
        "Date",
        "Time",
        "Debtor",
        "Account No.",
        "Card No.",
        "Status",
        "Remark",
        "Remark By",
        "Client",
        "Product Type",
        "PTP Amount",
        "Next Call",
        "PTP Date",
        "Claim Paid Amount",
        "Claim Paid Date",
        "Dialed Number",
        "Balance",
        "Call Duration"
    ]

    existing_columns = [col for col in desired_columns if col in df.columns]
    df = df[existing_columns]

    # -------------------------------
    # SAVE FILE
    # -------------------------------
    date_part = os.path.basename(file_path)\
        .replace("drr_csv_", "")\
        .replace(".csv", "")

    new_file = os.path.join(
        os.path.dirname(file_path),
        f"CMS EXTRACTION_BPI CARDS as of {date_part}.xlsx"
    )

    df.to_excel(new_file, index=False)
    print(f"[SUCCESS] Fixed file saved as: {new_file}")


def run(playwright: Playwright) -> None:
    save_path = r"C:\Users\SPM\Documents\Save Files Here\abpineda\BPI PROJECT"
    os.makedirs(save_path, exist_ok=True)

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://texxen-voliappe2.spmadridph.com/")
    page.get_by_role("link").first.click()
    page.get_by_role("textbox", name="Username").fill("MMMEJIA")
    page.get_by_role("textbox", name="Password").fill("$PMadr!d3124")
    page.get_by_role("button", name="Login").click()

    page.wait_for_load_state("networkidle")
    page.locator("a").filter(has_text="Report").click()
    page.get_by_role("button", name="Address Report").click()
    page.locator("a").filter(has_text="Daily Remark Export Direct").click()
    page.get_by_text("Both", exact=True).click()

    # -------------------------------
    # DATE PICKER
    # -------------------------------
    target_date = get_target_date()
    date_str_ui = target_date.strftime("%d/%m/%Y")
    print("Target date:", date_str_ui)

    full_range = f"{date_str_ui} - {date_str_ui}"

    page.evaluate("""
        ({ selector, value, start, end }) => {
            const input = document.querySelector(selector);

            input.value = value;

            if (input._daterangepicker || input.dataset) {
                const picker = $(input).data('daterangepicker');
                if (picker) {
                    picker.setStartDate(start);
                    picker.setEndDate(end);
                }
            }

            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            input.blur();
        }
    """, {
        "selector": "#daily_remark_report_daterange",
        "value": full_range,
        "start": date_str_ui,
        "end": date_str_ui
    })

    page.wait_for_timeout(1000)

    # -------------------------------
    # FILTERS
    # -------------------------------
    page.locator("#blockMultiClient").get_by_role("button", name="Nothing selected").click()
    page.get_by_role("option", name="BPI CARDS XDAYS SL").nth(1).click()
    page.wait_for_timeout(3000)
    page.keyboard.press("Escape")

    page.locator("#blockBatch").get_by_role("button", name="Nothing selected").click()
    page.get_by_role("button", name="Select All", exact=True).click()
    page.get_by_role("textbox", name="Search", exact=True).press("Escape")

    page.get_by_role("button", name="Follow Up Remark").click()
    page.locator("a").filter(has_text=re.compile(r"^ALL$")).click()

    # -------------------------------
    # DOWNLOAD
    # -------------------------------
    date_str = format_date(target_date)
    csv_filename = f"drr_csv_{date_str}.csv"
    final_file_path = os.path.join(save_path, csv_filename)

    with page.expect_download() as download_info:
        page.get_by_role("button", name="Generate").click()

    download = download_info.value
    download.save_as(final_file_path)

    print(f"[DOWNLOAD] File saved to: {final_file_path}")

    fix_account_numbers(final_file_path)

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)