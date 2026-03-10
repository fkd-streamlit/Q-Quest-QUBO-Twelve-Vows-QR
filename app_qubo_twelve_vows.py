# -*- coding: utf-8 -*-
"""
Q-Quest-QUBO : Quantum Shintaku (2026-03-05 spec)
-------------------------------------------------
仕様変更（要約版 2026-03-05）に対応：
- 4門は撤廃
- 入力は「3軸（顕↔密 / 智↔悲 / 和↔荒）」スライダー
- 十二因縁 ↔ 12誓願（介入点） ↔ 12神（語り手）を一貫した説明線で接続
- 12神の選択は one-hot QUBO（Simulated Annealing でサンプリング）

Excel（統合）シート想定：
1) 十二因縁と12誓願の統合
2) 12神の本質・性格・3軸ベクトルとその説明
3) 神と誓願の因果律マトリクス（距離ベース）
4) 神と誓願の因果律マトリクス（意味ベース）
"""

import math
import random
import re
import io
import json
import base64
import hashlib
import zlib
from pathlib import Path
from html import escape
from typing import List, Dict, Optional
from urllib.parse import quote

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
import plotly.graph_objects as go

try:
    import qrcode
except Exception:
    qrcode = None

# ============================================================
# Streamlit config（必ず最初）
# ============================================================
st.set_page_config(
    page_title="Q-Quest-QUBO｜量子神託（3軸→誓願→QUBO）",
    layout="wide",
)

# ============================================================
# SAFE THEME / CSS
# ============================================================
SPACE_CSS = """
<style>
:root{
  --bg0: #060812;
  --bg1: #0a0c1a;
  --panel: rgba(12,16,30,0.92);
  --panel2: rgba(18,24,42,0.92);
  --text: rgba(245,245,255,0.96);
  --muted: rgba(210,220,240,0.78);
  --line: rgba(255,255,255,0.14);
  --accent: #7fb2ff;
  --accent2: #ff7b7f;
  --good: rgba(60,140,95,0.35);
}

/* app background */
html, body, [data-testid="stAppViewContainer"], .stApp {
  background:
    radial-gradient(circle at 18% 24%, rgba(110,150,255,0.10), transparent 36%),
    radial-gradient(circle at 78% 68%, rgba(255,160,220,0.08), transparent 42%),
    linear-gradient(180deg, var(--bg0), var(--bg1)) !important;
  color: var(--text) !important;
}

/* main containers */
.main .block-container {
  padding-top: 1.2rem;
  color: var(--text);
}

/* header */
header[data-testid="stHeader"]{
  background: rgba(6,8,18,0.85) !important;
  border-bottom: 1px solid rgba(255,255,255,0.06) !important;
}
div[data-testid="stToolbar"]{
  background: transparent !important;
}
div[data-testid="stToolbar"] *{
  color: var(--text) !important;
  fill: var(--text) !important;
}

/* typography */
h1, h2, h3, h4, h5, h6,
p, li, label, span, div[data-testid="stMarkdownContainer"] * {
  color: var(--text) !important;
}
[data-testid="stCaption"], .stCaption, [data-testid="stCaption"] * {
  color: var(--muted) !important;
}

/* sidebar */
section[data-testid="stSidebar"]{
  background: rgba(8,10,22,0.96) !important;
  border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] *{
  color: var(--text) !important;
}

/* inputs */
div[data-baseweb="base-input"],
div[data-baseweb="input"],
div[data-baseweb="textarea"] {
  background: var(--panel) !important;
}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stNumberInput"] input,
input[type="text"], input[type="number"], textarea {
  color: var(--text) !important;
  background: var(--panel) !important;
  border: 1px solid var(--line) !important;
  border-radius: 10px !important;
}
textarea::placeholder, input::placeholder{
  color: rgba(245,245,255,0.50) !important;
}

/* file uploader */
div[data-testid="stFileUploader"],
div[data-testid="stFileUploader"] > div {
  background: var(--panel) !important;
  border: 1px solid var(--line) !important;
  border-radius: 14px !important;
}
div[data-testid="stFileUploader"] *{
  color: var(--text) !important;
}

/* radio */
div[data-testid="stRadio"] > div {
  gap: 0.35rem;
}
div[data-testid="stRadio"] label {
  color: var(--text) !important;
}
[data-baseweb="radio"] * {
  color: var(--text) !important;
}

/* sliders */
div[data-testid="stSlider"] {
  padding-top: 0.15rem;
  padding-bottom: 0.45rem;
}
div[data-testid="stSlider"] label,
div[data-testid="stSlider"] span,
div[data-testid="stSlider"] p {
  color: var(--text) !important;
}
div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {
  background: rgba(255,255,255,0.18) !important;
}
div[data-testid="stSlider"] [role="slider"] {
  background: var(--accent2) !important;
  border: 2px solid #ffd6d6 !important;
  box-shadow: 0 0 0 2px rgba(255,123,127,0.20) !important;
  width: 18px !important;
  height: 18px !important;
}
div[data-testid="stSlider"] div[data-testid="stThumbValue"] {
  color: var(--accent2) !important;
  font-weight: 700 !important;
}

/* buttons */
.stButton > button {
  border-radius: 12px !important;
  background: linear-gradient(90deg, #3b5ea8, #5d7fd0) !important;
  color: white !important;
  border: 1px solid rgba(255,255,255,0.16) !important;
}
.stButton > button:hover {
  filter: brightness(1.08);
}

/* alerts */
div[data-testid="stAlert"],
div[data-baseweb="notification"] {
  background: var(--panel2) !important;
  border: 1px solid var(--line) !important;
  color: var(--text) !important;
}

/* expander */
div[data-testid="stExpander"] > details,
div[data-testid="stExpander"] > div {
  background: var(--panel) !important;
  border: 1px solid var(--line) !important;
  border-radius: 10px !important;
}
div[data-testid="stExpander"] * {
  color: var(--text) !important;
}

/* dataframe/table */
div[data-testid="stDataFrame"],
div[data-testid="stDataFrame"] > div {
  background: var(--panel) !important;
  border-radius: 12px !important;
  border: 1px solid var(--line) !important;
}
div[data-testid="stDataFrame"] * {
  color: var(--text) !important;
}
table, thead, tbody, tr, td, th {
  color: var(--text) !important;
}

/* plotly wrapper */
.js-plotly-plot, .plotly, .plot-container {
  background: transparent !important;
}
/* ============================================================
   File uploader fix : 白枠・白背景・薄い文字を黒UIへ寄せる
   ============================================================ */

/* 外枠 */
div[data-testid="stFileUploader"]{
  background: var(--panel) !important;
  border: 1px solid var(--line) !important;
  border-radius: 14px !important;
  padding: 10px !important;
}

/* 内部ラッパ */
div[data-testid="stFileUploader"] > div,
div[data-testid="stFileUploader"] > div > div,
div[data-testid="stFileUploader"] section,
div[data-testid="stFileUploader"] section > div,
div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"]{
  background: var(--panel) !important;
  border: 1px dashed rgba(255,255,255,0.22) !important;
  border-radius: 12px !important;
}

/* Drag and drop file here の面 */
div[data-testid="stFileUploader"] [data-baseweb="file-uploader"],
div[data-testid="stFileUploader"] [data-baseweb="file-uploader"] > div,
div[data-testid="stFileUploader"] [data-baseweb="file-uploader"] > div > div,
div[data-testid="stFileUploader"] [role="button"]{
  background: var(--panel) !important;
  color: var(--text) !important;
}

/* 文字色 */
div[data-testid="stFileUploader"] *,
div[data-testid="stFileUploader"] label,
div[data-testid="stFileUploader"] small,
div[data-testid="stFileUploader"] span,
div[data-testid="stFileUploader"] p{
  color: var(--text) !important;
}

/* Drag and drop file here / Limit 200MB... */
div[data-testid="stFileUploader"] p,
div[data-testid="stFileUploader"] small,
div[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] *{
  color: var(--muted) !important;
}

/* Browse files ボタン */
div[data-testid="stFileUploader"] button{
  background: var(--panel2) !important;
  color: var(--text) !important;
  border: 1px solid var(--line) !important;
  border-radius: 10px !important;
}
div[data-testid="stFileUploader"] button:hover{
  filter: brightness(1.08);
}

/* アップロード済みファイル表示 */
div[data-testid="stFileUploader"] [data-baseweb="tag"],
div[data-testid="stFileUploader"] [data-baseweb="tag"] *{
  background: rgba(14,18,32,0.96) !important;
  color: var(--text) !important;
  border-color: var(--line) !important;
}

/* 白背景のインライン指定を上書き */
div[data-testid="stFileUploader"] [style*="background-color: rgb(255"],
div[data-testid="stFileUploader"] [style*="background-color:rgb(255"],
div[data-testid="stFileUploader"] [style*="background: rgb(255"],
div[data-testid="stFileUploader"] [style*="background:rgb(255"],
div[data-testid="stFileUploader"] [style*="#fff"],
div[data-testid="stFileUploader"] [style*="#FFF"],
div[data-testid="stFileUploader"] [style*="#ffffff"],
div[data-testid="stFileUploader"] [style*="#FFFFFF"]{
  background: var(--panel) !important;
  background-color: var(--panel) !important;
  color: var(--text) !important;
}
</style>
"""
st.markdown(SPACE_CSS, unsafe_allow_html=True)

# ============================================================
# Constants
# ============================================================
S_INNEN = "十二因縁と12誓願の統合"
S_CHAR3 = "12神の本質・性格・3軸ベクトルとその説明"
S_MAT_DIST = "神と誓願の因果律マトリクス（距離ベース） "
S_MAT_MEAN = "神と誓願の因果律マトリクス（意味ベース）  "

STOP_TOKENS = {
    "した","たい","いる","こと","それ","これ","ため","よう","ので","から",
    "です","ます","ある","ない","そして","でも","しかし","また",
    "自分","私","あなた","もの","感じ","気持ち","今日",
    "に","を","が","は","と","も","で","へ","や","の",
}

GLOBAL_WORDS_DATABASE = [
    "世界平和","貢献","成長","学び","挑戦","夢","希望","未来",
    "感謝","愛","幸せ","喜び","安心","充実","満足","平和",
    "努力","継続","忍耐","誠実","正直","優しさ","思いやり","共感",
    "調和","バランス","自然","美","真実","自由","正義","道",
    "絆","つながり","家族","友人","仲間","信頼","尊敬","協力",
    "今","瞬間","過程","変化","進化","発展","循環","流れ",
    "静けさ","集中","覚悟","決意","勇気","強さ","柔軟性","寛容",
]

CATEGORIES = {
    "願い": ["世界平和","貢献","成長","夢","希望","未来"],
    "感情": ["感謝","愛","幸せ","喜び","安心","満足","平和"],
    "行動": ["努力","継続","忍耐","誠実","正直","挑戦","学び"],
    "哲学": ["調和","バランス","自然","美","道","真実","自由","正義"],
    "関係": ["絆","つながり","家族","友人","仲間","信頼","尊敬","協力"],
    "内的": ["静けさ","集中","覚悟","決意","勇気","強さ","柔軟性","寛容"],
    "時間": ["今","瞬間","過程","変化","進化","発展","循環","流れ"],
}

# ============================================================
# Basic helpers
# ============================================================
def norm_col(s: str) -> str:
    s = str(s or "").replace("\n", " ").replace("\r", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def to_num(x, default=np.nan):
    try:
        if x is None or (isinstance(x, float) and np.isnan(x)):
            return default
        if isinstance(x, str):
            x = x.strip()
            if x == "":
                return default
            x = x.replace("＋", "+").replace("−", "-").replace("ー", "-")
            x = x.replace(",", "")
        return float(x)
    except Exception:
        return default

def safe_str(x) -> str:
    if x is None:
        return ""
    if isinstance(x, float) and np.isnan(x):
        return ""
    return str(x).strip()

def minmax01(arr):
    arr = np.asarray(arr, dtype=float)
    if np.allclose(arr.max(), arr.min()):
        return np.zeros_like(arr)
    return (arr - arr.min()) / (arr.max() - arr.min())

def zscore01(arr):
    arr = np.asarray(arr, dtype=float)
    if np.allclose(arr.std(), 0):
        return np.zeros_like(arr)
    z = (arr - arr.mean()) / (arr.std() + 1e-9)
    return minmax01(z)

def cosine_similarity(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return float(np.dot(a, b) / (na * nb))

def make_seed(s: str) -> int:
    s = str(s or "")
    return int(hashlib.md5(s.encode("utf-8")).hexdigest()[:8], 16)

def normalize_filename_token(s: str) -> str:
    s = safe_str(s)
    s = re.sub(r"[^\w\-]+", "_", s, flags=re.UNICODE)
    return s.strip("_")

# ============================================================
# QR share helpers
# ============================================================
def encode_oracle_payload(payload: dict) -> str:
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    comp = zlib.compress(raw, level=9)
    b64 = base64.urlsafe_b64encode(comp).decode("ascii").rstrip("=")
    return b64

def decode_oracle_payload(token: str) -> dict:
    token = str(token or "").strip()
    if not token:
        return {}
    pad = "=" * (-len(token) % 4)
    comp = base64.urlsafe_b64decode(token + pad)
    raw = zlib.decompress(comp)
    return json.loads(raw.decode("utf-8"))

def build_share_url(base_url: str, payload: dict) -> str:
    token = encode_oracle_payload(payload)
    base_url = (base_url or "").strip()
    if not base_url:
        base_url = "http://localhost:8501"
    sep = "&" if "?" in base_url else "?"
    return f"{base_url}{sep}oracle={quote(token)}"

def make_qr_image(url: str):
    if qrcode is None:
        return None
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

# ============================================================
# HTML helpers
# ============================================================
def render_glass_message(text: str) -> str:
    text = escape(text).replace("\n", "<br>")
    return f"""
    <div style="
        background: linear-gradient(180deg, rgba(20,28,48,0.92), rgba(10,14,26,0.92));
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
        border-radius: 18px;
        padding: 18px 20px;
        color: rgba(245,245,255,0.96);
        line-height: 1.8;
        font-size: 1.02rem;
        white-space: normal;
    ">{text}</div>
    """

def render_dataframe_as_html_table(df: pd.DataFrame) -> str:
    if df is None or len(df) == 0:
        return "<p style='color:#ddd;'>（データなし）</p>"

    cols = list(df.columns)
    thead = "".join([
        f"<th style='padding:10px 12px;border-bottom:1px solid rgba(255,255,255,0.16);text-align:left;'>{escape(str(c))}</th>"
        for c in cols
    ])
    rows_html = []
    for _, row in df.iterrows():
        tds = []
        for c in cols:
            val = row[c]
            if isinstance(val, float):
                sval = f"{val:.4f}" if abs(val) < 100 else f"{val:.2f}"
            else:
                sval = str(val)
            tds.append(
                f"<td style='padding:10px 12px;border-bottom:1px solid rgba(255,255,255,0.08);vertical-align:top;'>{escape(sval)}</td>"
            )
        rows_html.append("<tr>" + "".join(tds) + "</tr>")

    return f"""
    <div style="overflow-x:auto; background:rgba(12,16,30,0.92); border:1px solid rgba(255,255,255,0.12); border-radius:16px; padding:6px;">
      <table style="width:100%; border-collapse:collapse; color:rgba(245,245,255,0.96); font-size:0.95rem;">
        <thead><tr>{thead}</tr></thead>
        <tbody>{''.join(rows_html)}</tbody>
      </table>
    </div>
    """

# ============================================================
# Excel loaders
# ============================================================
def locate_sheet(xls: pd.ExcelFile, target_name: str) -> str:
    target = safe_str(target_name)
    names = list(xls.sheet_names)
    if target in names:
        return target

    target_n = re.sub(r"\s+", "", target)
    candidates = [n for n in names if re.sub(r"\s+", "", safe_str(n)) == target_n]
    if candidates:
        return candidates[0]

    for n in names:
        if target_n in re.sub(r"\s+", "", safe_str(n)):
            return n

    raise KeyError(f"シートが見つかりません: {target_name} / available={names}")

@st.cache_data(show_spinner=False)
def read_excel_all(file_bytes: bytes) -> Dict[str, pd.DataFrame]:
    bio = io.BytesIO(file_bytes)
    xls = pd.ExcelFile(bio, engine="openpyxl")

    s_innen = locate_sheet(xls, S_INNEN)
    s_char3 = locate_sheet(xls, S_CHAR3)
    s_md = locate_sheet(xls, S_MAT_DIST)
    s_mm = locate_sheet(xls, S_MAT_MEAN)

    dfs = {
        "innen": pd.read_excel(io.BytesIO(file_bytes), sheet_name=s_innen, engine="openpyxl"),
        "char3": pd.read_excel(io.BytesIO(file_bytes), sheet_name=s_char3, engine="openpyxl"),
        "mat_dist": pd.read_excel(io.BytesIO(file_bytes), sheet_name=s_md, engine="openpyxl"),
        "mat_mean": pd.read_excel(io.BytesIO(file_bytes), sheet_name=s_mm, engine="openpyxl"),
    }

    try:
        qsheet = locate_sheet(xls, "QUOTES")
        dfs["quotes"] = pd.read_excel(io.BytesIO(file_bytes), sheet_name=qsheet, engine="openpyxl")
    except Exception:
        dfs["quotes"] = pd.DataFrame(columns=["QUOTE", "SOURCE", "LANG"])

    return dfs

# ============================================================
# Column detection / parsing
# ============================================================
def parse_vow_columns(df_innen: pd.DataFrame):
    cols = list(df_innen.columns)
    ncols = [norm_col(c).upper() for c in cols]

    vow_map = {}
    for c, nc in zip(cols, ncols):
        m = re.search(r"VOW[_\-\s]?(\d{1,2})", nc)
        if m:
            vid = f"VOW_{int(m.group(1)):02d}"
            vow_map[vid] = c

    if len(vow_map) < 12:
        for c, nc in zip(cols, ncols):
            nums = re.findall(r"\b(\d{1,2})\b", nc)
            if nums:
                n = int(nums[0])
                if 1 <= n <= 12:
                    vow_map.setdefault(f"VOW_{n:02d}", c)

    vow_ids = [f"VOW_{i:02d}" for i in range(1, 13)]
    missing = [v for v in vow_ids if v not in vow_map]
    if missing:
        raise ValueError(
            "VOW列が見つかりません。Excel側に VOW_01..VOW_12 の列名、または "
            "それに準ずる番号付き列を用意してください。missing=" + str(missing)
        )

    title_col = None
    subtitle_col = None
    for c, nc in zip(cols, ncols):
        if ("誓願" in safe_str(c) and "タイトル" in safe_str(c)) or ("VOW" in nc and "TITLE" in nc):
            title_col = c
        if ("サブ" in safe_str(c)) or ("SUBTITLE" in nc):
            subtitle_col = c

    col_innen = next((c for c in cols if "因縁" in safe_str(c)), cols[0])
    col_modern = next((c for c in cols if "現代" in safe_str(c) or "起きがち" in safe_str(c)), cols[min(1, len(cols)-1)])
    col_intervene = next((c for c in cols if "介入" in safe_str(c) or "介入点" in safe_str(c)), cols[min(2, len(cols)-1)])

    return vow_ids, vow_map, title_col, subtitle_col, col_innen, col_modern, col_intervene

def parse_char3(df_char3: pd.DataFrame):
    cols = list(df_char3.columns)
    ncols = [norm_col(c).upper() for c in cols]

    col_name = next((c for c, nc in zip(cols, ncols) if "NAME" in nc or "神名" in safe_str(c) or nc == "神"), cols[0])
    col_id = next((c for c, nc in zip(cols, ncols) if nc == "ID" or "CHAR_ID" in nc or "神ID" in safe_str(c)), None)
    col_tip = next((c for c, nc in zip(cols, ncols) if "性格" in safe_str(c) or "説明" in safe_str(c) or "TIP" in nc or "DESC" in nc), None)

    axis_candidates = {}
    for c, nc in zip(cols, ncols):
        s = safe_str(c)
        if ("顕" in s and "密" in s) or "X" == nc:
            axis_candidates["x"] = c
        elif ("智" in s and "悲" in s) or "Y" == nc:
            axis_candidates["y"] = c
        elif ("和" in s and "荒" in s) or "Z" == nc:
            axis_candidates["z"] = c

    if len(axis_candidates) < 3:
        num_cols = []
        for c in cols:
            vals = pd.to_numeric(df_char3[c], errors="coerce")
            if vals.notna().sum() >= max(3, len(df_char3) // 2):
                num_cols.append(c)
        if len(num_cols) >= 3:
            axis_candidates.setdefault("x", num_cols[0])
            axis_candidates.setdefault("y", num_cols[1])
            axis_candidates.setdefault("z", num_cols[2])

    if len(axis_candidates) < 3:
        raise ValueError("3軸列（顕↔密 / 智↔悲 / 和↔荒）が見つかりません。")

    char_names = df_char3[col_name].astype(str).tolist()
    char_ids = (
        df_char3[col_id].astype(str).tolist()
        if col_id is not None else
        [f"P{i:02d}" for i in range(1, len(df_char3)+1)]
    )

    axes = []
    for _, r in df_char3.iterrows():
        axes.append([
            to_num(r[axis_candidates["x"]], 0.0),
            to_num(r[axis_candidates["y"]], 0.0),
            to_num(r[axis_candidates["z"]], 0.0),
        ])
    axes = np.asarray(axes, dtype=float)

    tips = (
        df_char3[col_tip].fillna("").astype(str).tolist()
        if col_tip is not None else
        ["" for _ in range(len(df_char3))]
    )

    return char_ids, char_names, axes, tips

def parse_matrix(df_mat: pd.DataFrame, vow_ids: List[str], expected_rows: int):
    cols = list(df_mat.columns)
    ncols = [norm_col(c).upper() for c in cols]

    row_id_col = next((c for c, nc in zip(cols, ncols) if nc in {"ID", "CHAR_ID"} or "神ID" in safe_str(c)), None)
    row_name_col = next((c for c, nc in zip(cols, ncols) if "NAME" in nc or "神名" in safe_str(c) or nc == "神"), None)

    vow_cols = {}
    for c, nc in zip(cols, ncols):
        m = re.search(r"VOW[_\-\s]?(\d{1,2})", nc)
        if m:
            vow_cols[f"VOW_{int(m.group(1)):02d}"] = c

    if len(vow_cols) < 12:
        num_cols = []
        for c in cols:
            vals = pd.to_numeric(df_mat[c], errors="coerce")
            if vals.notna().sum() >= max(2, len(df_mat)//2):
                num_cols.append(c)
        non_id = [c for c in num_cols if c not in {row_id_col, row_name_col}]
        for i, vid in enumerate(vow_ids):
            if vid not in vow_cols and i < len(non_id):
                vow_cols[vid] = non_id[i]

    missing = [v for v in vow_ids if v not in vow_cols]
    if missing:
        raise ValueError("因果律マトリクスで VOW 列が不足しています: " + str(missing))

    if len(df_mat) < expected_rows:
        raise ValueError(f"因果律マトリクスの行数が不足しています。expected_rows={expected_rows}, got={len(df_mat)}")

    W = []
    row_ids = []
    row_names = []
    for i in range(expected_rows):
        r = df_mat.iloc[i]
        row_ids.append(safe_str(r[row_id_col]) if row_id_col else f"P{i+1:02d}")
        row_names.append(safe_str(r[row_name_col]) if row_name_col else f"神{i+1:02d}")
        W.append([to_num(r[vow_cols[vid]], 0.0) for vid in vow_ids])

    return np.asarray(W, dtype=float), row_ids, row_names

def parse_quotes(df_quotes: pd.DataFrame) -> pd.DataFrame:
    if df_quotes is None or len(df_quotes) == 0:
        return pd.DataFrame(columns=["QUOTE", "SOURCE", "LANG"])

    cols = list(df_quotes.columns)
    ncols = [norm_col(c).upper() for c in cols]

    q_col = next((c for c, nc in zip(cols, ncols) if "QUOTE" in nc or "格言" in safe_str(c) or "言葉" in safe_str(c)), None)
    s_col = next((c for c, nc in zip(cols, ncols) if "SOURCE" in nc or "出典" in safe_str(c) or "作者" in safe_str(c)), None)
    l_col = next((c for c, nc in zip(cols, ncols) if "LANG" in nc or "言語" in safe_str(c)), None)

    if q_col is None:
        return pd.DataFrame(columns=["QUOTE", "SOURCE", "LANG"])

    out = pd.DataFrame({
        "QUOTE": df_quotes[q_col].fillna("").astype(str),
        "SOURCE": df_quotes[s_col].fillna("").astype(str) if s_col else "",
        "LANG": df_quotes[l_col].fillna("ja").astype(str) if l_col else "ja",
    })
    out = out[out["QUOTE"].str.strip() != ""].reset_index(drop=True)
    return out

# ============================================================
# Simple keyword extraction
# ============================================================
def extract_keywords(text: str, top_n: int = 6) -> List[str]:
    text = safe_str(text)
    if not text:
        return []

    words = re.findall(r"[一-龥ぁ-んァ-ヶA-Za-z0-9_]+", text)
    words = [w for w in words if len(w) >= 2 and w not in STOP_TOKENS]

    scores = {}
    for w in words:
        scores[w] = scores.get(w, 0) + 1.0
        for cat, vocab in CATEGORIES.items():
            if w in vocab:
                scores[w] += 1.2

    if not scores:
        return []

    ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    return [w for w, _ in ranked[:top_n]]

# ============================================================
# 3D word sphere
# ============================================================
def random_points_on_sphere(n, radius=1.0, seed=0):
    rng = np.random.default_rng(seed)
    phi = rng.uniform(0, 2*np.pi, n)
    costheta = rng.uniform(-1, 1, n)
    theta = np.arccos(costheta)
    x = radius * np.sin(theta) * np.cos(phi)
    y = radius * np.sin(theta) * np.sin(phi)
    z = radius * np.cos(theta)
    return np.vstack([x, y, z]).T

def plot_word_sphere(center_words, user_keywords, seed=0, star_count=700):
    rng = np.random.default_rng(seed)

    base_words = list(dict.fromkeys(center_words))
    user_keywords = list(dict.fromkeys([w for w in user_keywords if w and w not in base_words]))
    all_words = base_words + user_keywords

    pts = random_points_on_sphere(len(all_words), radius=1.0, seed=seed)
    pts += rng.normal(0, 0.03, size=pts.shape)

    xs, ys, zs = pts[:, 0], pts[:, 1], pts[:, 2]

    star_xyz = rng.uniform(-2.6, 2.6, size=(star_count, 3))
    star_size = rng.uniform(1.0, 3.3, size=star_count)

    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
        x=star_xyz[:, 0], y=star_xyz[:, 1], z=star_xyz[:, 2],
        mode="markers",
        marker=dict(size=star_size, opacity=0.65),
        hoverinfo="skip",
        showlegend=False
    ))

    x_line, y_line, z_line = [], [], []
    for uk in user_keywords:
        uidx = all_words.index(uk)
        for bw in base_words[: min(18, len(base_words))]:
            bidx = all_words.index(bw)
            if rng.random() < 0.14:
                x_line += [xs[uidx], xs[bidx], None]
                y_line += [ys[uidx], ys[bidx], None]
                z_line += [zs[uidx], zs[bidx], None]

    if len(x_line) > 0:
        fig.add_trace(go.Scatter3d(
            x=x_line, y=y_line, z=z_line,
            mode="lines",
            line=dict(width=2),
            hoverinfo="skip",
            showlegend=False
        ))

    fig.add_trace(go.Scatter3d(
        x=xs[:len(base_words)], y=ys[:len(base_words)], z=zs[:len(base_words)],
        mode="markers+text",
        text=base_words,
        textposition="top center",
        marker=dict(size=7, opacity=0.9),
        hovertemplate="%{text}<extra></extra>",
        showlegend=False
    ))

    if user_keywords:
        fig.add_trace(go.Scatter3d(
            x=xs[len(base_words):], y=ys[len(base_words):], z=zs[len(base_words):],
            mode="markers+text",
            text=user_keywords,
            textposition="top center",
            marker=dict(size=10, opacity=1.0),
            hovertemplate="%{text}<extra></extra>",
            showlegend=False
        ))

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            camera=dict(eye=dict(x=1.45, y=1.25, z=1.25)),
            aspectmode="cube",
        ),
        height=700,
    )
    return fig

# ============================================================
# Oracle / QUOTES
# ============================================================
def pick_quotes_by_temperature(df_quotes: pd.DataFrame, lang: str = "ja", k: int = 3, tau: float = 1.0, seed: int = 0):
    if df_quotes is None or len(df_quotes) == 0:
        return pd.DataFrame(columns=["QUOTE", "SOURCE", "LANG"])

    sub = df_quotes.copy()
    if "LANG" in sub.columns and lang:
        lang_mask = sub["LANG"].fillna("").astype(str).str.lower().eq(lang.lower())
        if lang_mask.any():
            sub = sub[lang_mask].copy()

    if len(sub) == 0:
        return pd.DataFrame(columns=["QUOTE", "SOURCE", "LANG"])

    rng = np.random.default_rng(seed)
    base = np.arange(len(sub), dtype=float)

    quote_len = sub["QUOTE"].fillna("").astype(str).apply(len).to_numpy(dtype=float)
    source_bonus = sub["SOURCE"].fillna("").astype(str).apply(lambda s: 0.3 if s.strip() else 0.0).to_numpy(dtype=float)
    len_pref = -np.abs(quote_len - 18.0) / 18.0
    noise = rng.normal(0, 0.18, size=len(sub))

    score = 0.55 * zscore01(base) + 0.35 * zscore01(len_pref) + 0.10 * source_bonus + noise
    score = score - np.max(score)

    tau = max(0.05, float(tau))
    p = np.exp(score / tau)
    p = p / p.sum()

    take = min(k, len(sub))
    idx = rng.choice(np.arange(len(sub)), size=take, replace=False, p=p)
    return sub.iloc[idx].reset_index(drop=True)

# ============================================================
# QUBO helpers
# ============================================================
def build_qubo_onehot(linear_E: np.ndarray, P: float) -> np.ndarray:
    linear_E = np.asarray(linear_E, dtype=float)
    n = len(linear_E)
    Q = np.zeros((n, n), dtype=float)

    for i in range(n):
        Q[i, i] += linear_E[i]

    # P*(sum x - 1)^2 = P*(sum x + 2 sum_{i<j} xixj - 2 sum x + 1)
    #                = P*(-sum x + 2 sum_{i<j} xixj + 1)
    for i in range(n):
        Q[i, i] += -P
    for i in range(n):
        for j in range(i + 1, n):
            Q[i, j] += 2.0 * P

    return Q

def energy(Q: np.ndarray, x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    return float(x @ Q @ x)

def onehot_index(x) -> Optional[int]:
    idx = np.where(np.asarray(x) > 0.5)[0]
    if len(idx) == 1:
        return int(idx[0])
    return None

def sa_sample(Q: np.ndarray, num_reads: int = 50, sweeps: int = 500, seed: int = 0):
    rng = np.random.default_rng(seed)
    n = Q.shape[0]
    samples = []
    Es = []

    # temperature schedule
    t0, t1 = 3.0, 0.02
    temps = np.geomspace(t0, t1, sweeps)

    for _ in range(num_reads):
        x = rng.integers(0, 2, size=n).astype(int)
        e = energy(Q, x)

        for T in temps:
            i = int(rng.integers(0, n))
            x_new = x.copy()
            x_new[i] = 1 - x_new[i]
            e_new = energy(Q, x_new)
            de = e_new - e
            if de <= 0 or rng.random() < math.exp(-de / max(T, 1e-9)):
                x, e = x_new, e_new

        samples.append(x.copy())
        Es.append(e)

    return samples, np.asarray(Es, dtype=float)

# ============================================================
# Main input area / shared result mode
# ============================================================
uploaded = st.file_uploader(
    "統合Excelファイルをアップロードしてください",
    type=["xlsx", "xlsm", "xls"],
    help="シート名の例：『十二因縁と12誓願の統合』『12神の本質・性格・3軸ベクトルとその説明』など"
)

params = st.query_params
oracle_token = params.get("oracle", "")

# 共有表示モード
if oracle_token:
    try:
        shared = decode_oracle_payload(oracle_token)
        st.title("🔮 共有された神託")
        st.caption("QRコードから開かれた神託結果です。")

        c1, c2 = st.columns([1, 2], gap="large")
        with c1:
            god_name = safe_str(shared.get("god_name"))
            image_file = safe_str(shared.get("image_file"))
            st.subheader(god_name if god_name else "観測された神")
            if image_file:
                img_path = Path("assets/images/characters") / image_file
                if img_path.exists():
                    try:
                        st.image(Image.open(img_path), width=260)
                    except Exception:
                        st.info(f"画像はありますが読み込めませんでした: {img_path}")
                else:
                    st.info(f"画像ファイルが見つかりませんでした: {img_path}")

        with c2:
            vow_title_shared = safe_str(shared.get("vow_title"))
            oracle_message_shared = safe_str(shared.get("oracle_message"))
            quote_text_shared = safe_str(shared.get("quote_text"))
            quote_source_shared = safe_str(shared.get("quote_source"))
            mode_label_shared = safe_str(shared.get("mode_label"))
            ts_shared = safe_str(shared.get("timestamp"))

            if mode_label_shared:
                st.caption(f"方式: {mode_label_shared}")
            if ts_shared:
                st.caption(f"生成時刻: {ts_shared}")

            if vow_title_shared:
                st.markdown(f"### 🧩 誓願: {escape(vow_title_shared)}", unsafe_allow_html=True)

            if oracle_message_shared:
                st.markdown(render_glass_message(oracle_message_shared), unsafe_allow_html=True)

            if quote_text_shared:
                qd = f"「{quote_text_shared}」"
                if quote_source_shared:
                    qd += f"\n\n— {quote_source_shared}"
                st.markdown("### 📜 格言")
                st.markdown(render_glass_message(qd), unsafe_allow_html=True)

        st.info("この神託は保存を伴わない共有URLから復元しています。履歴は保持していません。")
        st.stop()

    except Exception as e:
        st.error(f"共有URLの神託を復元できませんでした: {e}")
        st.stop()

st.title("Q-Quest-QUBO｜量子神託")
st.caption("3軸 → 誓願推定 → one-hot QUBOで12神を観測し、神託として返します。")

if uploaded is None:
    st.info("まず統合Excelファイルをアップロードしてください。")
    st.stop()

# ============================================================
# Load Excel
# ============================================================
try:
    file_bytes = uploaded.read()
    dfs = read_excel_all(file_bytes)
except Exception as e:
    st.error(f"Excel読み込みに失敗しました: {e}")
    st.stop()

df_innen = dfs["innen"].copy()
df_char3 = dfs["char3"].copy()
df_mat_dist = dfs["mat_dist"].copy()
df_mat_mean = dfs["mat_mean"].copy()
df_quotes = parse_quotes(dfs["quotes"])

try:
    vow_ids, vow_map, title_col, subtitle_col, col_innen, col_modern, col_intervene = parse_vow_columns(df_innen)
except Exception as e:
    st.error(f"十二因縁 / 誓願シートの解析に失敗しました: {e}")
    st.stop()

try:
    char_ids, char_names, char_axes, char_tips = parse_char3(df_char3)
except Exception as e:
    st.error(f"12神シートの解析に失敗しました: {e}")
    st.stop()

try:
    W_dist, row_ids_dist, row_names_dist = parse_matrix(df_mat_dist, vow_ids, expected_rows=len(char_names))
    W_mean, row_ids_mean, row_names_mean = parse_matrix(df_mat_mean, vow_ids, expected_rows=len(char_names))
except Exception as e:
    st.error(f"因果律マトリクスの解析に失敗しました: {e}")
    st.stop()

# aligned image file names
img_files = []
for cid, cname in zip(char_ids, char_names):
    token = normalize_filename_token(cid)
    guesses = [
        f"{token}.png", f"{token}.jpg", f"{token}.jpeg", f"{token}.webp",
        f"{normalize_filename_token(cname)}.png",
        f"{normalize_filename_token(cname)}.jpg",
        f"{normalize_filename_token(cname)}.jpeg",
        f"{normalize_filename_token(cname)}.webp",
    ]
    picked = None
    for g in guesses:
        if (Path("assets/images/characters") / g).exists():
            picked = g
            break
    if picked is None:
        picked = guesses[0]
    img_files.append(picked)

# vow title / subtitle map
vow_title = {}
vow_subtitle = {}
for i, vid in enumerate(vow_ids):
    vow_title[vid] = vid
    vow_subtitle[vid] = ""

if title_col:
    tdf = df_innen[[vow_map[vow_ids[0]], title_col]].copy() if vow_ids and title_col else pd.DataFrame()
    for vid in vow_ids:
        col = vow_map[vid]
        rows = df_innen[[col] + ([title_col] if title_col else []) + ([subtitle_col] if subtitle_col else [])].copy()
        for _, rr in rows.iterrows():
            title_text = safe_str(rr[title_col]) if title_col else ""
            sub_text = safe_str(rr[subtitle_col]) if subtitle_col else ""
            if title_text:
                vow_title[vid] = title_text
                vow_subtitle[vid] = sub_text
                break

# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    st.header("⚙ 設定")
    mat_mode = st.radio(
        "🧭 方式選択\n神×誓願 相性表",
        ["距離ベース（3軸の近さ）", "意味ベース（ロア共鳴）"],
        index=0,
    )

    if mat_mode.startswith("距離"):
        st.success("現在の選択: 距離ベース（3軸の近さ）")
        st.caption("距離ベースを選択中")
    else:
        st.success("現在の選択: 意味ベース（ロア共鳴）")
        st.caption("意味ベースを選択中")

    W = W_dist if mat_mode.startswith("距離") else W_mean

    st.markdown("---")
    st.markdown("### 3軸入力")
    x = st.slider("存在（顕↔密）", -3.0, 3.0, 0.2, 0.1)
    y = st.slider("作用（智↔悲）", -3.0, 3.0, 0.1, 0.1)
    z = st.slider("魂（和↔荒）", -3.0, 3.0, 0.0, 0.1)

    st.markdown("---")
    st.markdown("### 自由入力（願い・悩み・問い）")
    user_text = st.text_area(
        "言葉で書いてください",
        value="",
        height=140,
        placeholder="例：今の自分の進むべき方向が分からず、不安と期待が交差しています。"
    )

    st.markdown("---")
    st.markdown("### SA / QUBO パラメータ")
    num_reads = st.slider("num_reads", 20, 200, 60, 10)
    sweeps = st.slider("sweeps", 100, 2000, 700, 100)
    P_user = st.slider("one-hot制約ペナルティ P", 1.0, 40.0, 10.0, 0.5)
    seed = st.number_input("seed", value=42, step=1)

    st.markdown("---")
    st.markdown("### QR共有")
    share_base_url = st.text_input(
        "共有ベースURL",
        value=st.session_state.get("share_base_url", "http://localhost:8501"),
        help="ローカル検証時は http://192.168.x.x:8501 のようにPCのIPを入れると、同じネットワーク上のスマホで開けます。"
    )
    st.session_state["share_base_url"] = share_base_url

    st.markdown("---")
    run = st.button("🧪 QUBOで観測", use_container_width=True)

# ============================================================
# Step1: user vector
# ============================================================
st.subheader("① 現在地（3軸ベクトル）")
v_user = np.array([x, y, z], dtype=float)

df_user_vec = pd.DataFrame({
    "軸": ["存在（顕↔密）", "作用（智↔悲）", "魂（和↔荒）"],
    "値": v_user
})
st.markdown(render_dataframe_as_html_table(df_user_vec), unsafe_allow_html=True)

# ============================================================
# Step2: vow prediction (from 3-axis)
# ============================================================
st.subheader("② 今、必要になりやすい誓願（12候補）")

vow_table = []
for vid in vow_ids:
    r = df_innen[[vow_map[vid], col_innen, col_modern, col_intervene]].copy()
    colv = vow_map[vid]
    vals = pd.to_numeric(df_innen[colv], errors="coerce").fillna(0.0).to_numpy(dtype=float)

    need = float(minmax01(np.array([vals.mean()]))[0]) if len(vals) > 0 else 0.0
    need = float(min(1.0, max(0.0, 0.5 + 0.12 * (abs(x) + abs(y) + abs(z)) / 3.0 + random.Random(make_seed(vid)).uniform(-0.08, 0.08))))
    vow_table.append({
        "VOW_ID": vid,
        "TITLE": vow_title.get(vid, vid),
        "SUBTITLE": vow_subtitle.get(vid, ""),
        "need(0-1)": need,
    })
df_vpred = pd.DataFrame(vow_table).sort_values("need(0-1)", ascending=False)

html_table_vpred = render_dataframe_as_html_table(df_vpred[["VOW_ID", "TITLE", "SUBTITLE", "need(0-1)"]])
st.markdown(html_table_vpred, unsafe_allow_html=True)

st.caption("※「誓願＝介入メニュー」。3軸の現在地から、今必要になりやすい誓願を推定しています。")

# ============================================================
# Step2.5: keyword sphere
# ============================================================
if user_text:
    st.subheader("🔍 キーワード抽出と球体アート")

    kw = extract_keywords(user_text, top_n=6)
    colA, colB = st.columns([1.0, 1.6], gap="large")

    with colA:
        st.markdown("### 抽出キーワード")
        if kw:
            st.markdown("**" + " / ".join(kw) + "**")
            st.caption("※簡易抽出です（形態素解析なし）。")
        else:
            st.info("入力が短い/空のため、キーワードが抽出できません。")

    with colB:
        st.markdown("### 🌐 単語の球体（誓願→キーワード→縁のネットワーク）")
        if kw:
            seed_sphere = make_seed(user_text + "|sphere")
            fig = plot_word_sphere(
                center_words=GLOBAL_WORDS_DATABASE,
                user_keywords=kw,
                seed=seed_sphere,
                star_count=850
            )
            st.plotly_chart(
                fig,
                width="stretch",
                config={
                    "displayModeBar": True,
                    "scrollZoom": True,
                    "displaylogo": False,
                    "doubleClick": "reset",
                }
            )
        else:
            st.info("キーワードが抽出できませんでした。")

# ============================================================
# Step3: vows -> god by QUBO
# ============================================================
st.subheader("③ 12神をQUBOで観測（one-hot）")

score = W @ v_user
linear_E = -score

P_min = float(np.max(np.abs(linear_E)) * 3.0 + 1.0)
P = max(float(P_user), P_min)
Q = build_qubo_onehot(linear_E, P)

st.caption(f"ペナルティPの自動下限 P_min={P_min:.2f} を考慮し、採用値は P={P:.2f} です。")

if run:
    samples, Es = sa_sample(Q, num_reads=num_reads, sweeps=sweeps, seed=int(seed))
    idxs = [onehot_index(x) for x in samples]
    idxs = [k for k in idxs if k is not None]

    counts = np.zeros(len(char_names), int)
    for k in idxs:
        counts[k] += 1

    valid = [(energy(Q, x), onehot_index(x)) for x in samples if onehot_index(x) is not None]
    if not valid:
        st.error("one-hot 解が見つかりませんでした。Pを上げて再実行してください。")
    else:
        best_k = min(valid, key=lambda t: t[0])[1]
        st.session_state["counts"] = counts
        st.session_state["best_k"] = int(best_k)
        st.session_state["P"] = float(P)
        st.session_state["v_user"] = v_user
        st.session_state["score"] = score

# ============================================================
# Result
# ============================================================
if "best_k" in st.session_state:
    k = int(st.session_state["best_k"])
    selected_quote_text = ""
    selected_quote_source = ""
    mode_label = "距離ベース（3軸の近さ）" if mat_mode.startswith("距離") else "意味ベース（ロア共鳴）"

    st.markdown("---")
    st.subheader("🌟 観測された神（QUBO解）")

    col_char, col_oracle = st.columns([1, 2])

    with col_char:
        st.write(f"**{char_names[k]}**")
        img_path = Path("assets/images/characters") / img_files[k]
        if img_path.exists():
            try:
                st.image(Image.open(img_path), width=250)
            except Exception:
                st.info(f"画像はありますが読み込めませんでした: {img_path}")
        else:
            st.info(f"画像ファイルが見つかりませんでした: {img_path}")

        ax = char_axes[k]
        st.write("**3軸（神の性格）**")
        st.write(
            f"- 存在（顕↔密）: {ax[0]:+.1f}\n"
            f"- 作用（智↔悲）: {ax[1]:+.1f}\n"
            f"- 魂（和↔荒）: {ax[2]:+.1f}"
        )
        if char_tips[k]:
            st.write("**性格・口調ヒント**")
            st.write(char_tips[k])

    with col_oracle:
        st.subheader("💬 神託（観測された神からのメッセージ）")
        v_user = st.session_state["v_user"]
        score = st.session_state["score"]
        contrib = W[k, :] * v_user
        order = np.argsort(contrib)[::-1]
        top_vid = vow_ids[order[0]]
        top_vow_title = vow_title.get(top_vid, top_vid)

        oracle_text = f"{char_names[k]}が語る：\n\n"
        oracle_text += f"「{top_vow_title}」という誓願が、今のあなたに響いています。\n\n"

        r = df_innen[df_innen["VOW_ID_N"].astype(str) == str(top_vid)]
        if len(r) >= 1:
            r0 = r.iloc[0]
            oracle_text += f"十二因縁の「{str(r0[col_innen])}」の段にいます。\n"
            oracle_text += f"この段で起きがちなこと：{str(r0[col_modern])}\n\n"
            oracle_text += f"介入点：{str(r0[col_intervene])}"

        st.markdown(render_glass_message(oracle_text), unsafe_allow_html=True)

    st.subheader("📊 観測分布（サンプリング）")
    
    hist = pd.DataFrame({
        "神": char_names,
        "count": st.session_state["counts"]
    }).sort_values("count", ascending=False)
    
    fig_bar = go.Figure()
    
    fig_bar.add_trace(go.Bar(
        x=hist["神"],
        y=hist["count"],
        marker=dict(
            color="rgba(120,170,255,0.85)",
            line=dict(color="rgba(255,255,255,0.4)", width=1)
        )
    ))
    
    fig_bar.update_layout(
        paper_bgcolor="rgba(6,8,18,1)",
        plot_bgcolor="rgba(10,12,26,0.95)",
        font=dict(color="rgba(245,245,255,0.95)"),
        xaxis=dict(
            tickangle=90,
            gridcolor="rgba(255,255,255,0.05)"
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.08)"
        ),
        margin=dict(l=20, r=20, t=20, b=120),
        height=420
    )
    
    st.plotly_chart(
        fig_bar,
        width="stretch",
        config={
            "displayModeBar": False
        }
    )

    st.subheader("🧩 この神託が指している誓願（上位）")
    v_user = st.session_state["v_user"]
    contrib = W[k, :] * v_user
    order = np.argsort(contrib)[::-1]

    rows = []
    for idx in order[:4]:
        vid = vow_ids[idx]
        rows.append({
            "VOW_ID": vid,
            "TITLE": vow_title.get(vid, vid),
            "need": float(v_user[idx]),
            "compat": float(W[k, idx]),
            "contrib": float(contrib[idx]),
        })
    df_top_vows = pd.DataFrame(rows)
    st.markdown(render_dataframe_as_html_table(df_top_vows), unsafe_allow_html=True)

    if len(df_quotes) > 0:
        st.subheader("📜 QUOTES神託（温度付きで選択）")
        quote_tau = st.slider("格言温度（高→ランダム / 低→上位固定）", 0.2, 2.5, 1.2, 0.1, key="quote_tau")

        if "last_quote_tau" not in st.session_state:
            st.session_state["last_quote_tau"] = quote_tau
            st.session_state["quote_seed_offset"] = 0

        if abs(st.session_state.get("last_quote_tau", quote_tau) - quote_tau) > 0.05:
            st.session_state["quote_seed_offset"] = st.session_state.get("quote_seed_offset", 0) + 1
            st.session_state["last_quote_tau"] = quote_tau

        quote_seed_base = (
            (user_text or "")
            + f"|quotes_temp|{quote_tau:.3f}|{seed}|offset_{st.session_state.get('quote_seed_offset', 0)}"
        )
        quote_seed = make_seed(quote_seed_base)

        qpick_temp = pick_quotes_by_temperature(
            df_quotes, lang="ja", k=3, tau=quote_tau, seed=quote_seed
        )

        if len(qpick_temp) > 0:
            for q_idx, (_, row) in enumerate(qpick_temp.iterrows()):
                quote_text = str(row.get("QUOTE", "")).strip()
                source_text = str(row.get("SOURCE", "")).strip()
                if q_idx == 0:
                    selected_quote_text = quote_text
                    selected_quote_source = source_text if source_text != "nan" else ""
                if quote_text:
                    quote_display = f"「{quote_text}」"
                    if source_text and source_text != "nan":
                        quote_display += f"\n\n— {source_text}"
                    st.markdown(render_glass_message(quote_display), unsafe_allow_html=True)
        else:
            st.info("QUOTES神託が見つかりませんでした。")

    st.subheader("📜 十二因縁（診断）→ 誓願（介入）→ 神（語り手）")
    if len(r) >= 1:
        r0 = r.iloc[0]
        st.write(f"**今、強く出ている誓願**：{top_vow_title}")
        st.write(f"**対応する十二因縁**：{str(r0[col_innen])}")
        st.write(f"**現代語（起きがちなこと）**：{str(r0[col_modern])}")
        st.write(f"**介入点（つながりの理由）**：{str(r0[col_intervene])}")
    else:
        st.info("十二因縁シートに、上位誓願の対応行が見つかりませんでした。")

    st.subheader("🧠 QUBO 証拠（one-hot）")
    x = [1 if i == k else 0 for i in range(len(char_names))]
    st.code(
        f"E(x)=ΣE_i x_i + P(Σx-1)^2\n"
        f"P={st.session_state['P']:.2f}\n"
        f"linear_E(=-score)={np.round((-score), 3).tolist()}\n"
        f"x={x}",
        language="text",
    )

    st.subheader("📱 神託をQRで共有")
    shared_oracle_payload = {
        "god_name": str(char_names[k]),
        "image_file": str(img_files[k]),
        "vow_id": str(top_vid),
        "vow_title": str(top_vow_title),
        "oracle_message": oracle_text,
        "quote_text": selected_quote_text,
        "quote_source": selected_quote_source,
        "mode_label": mode_label,
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    share_url = build_share_url(st.session_state.get("share_base_url", "http://localhost:8501"), shared_oracle_payload)
    qr_img = make_qr_image(share_url)

    st.caption("※ローカル検証では、共有ベースURLに PC のIPアドレス（例: http://192.168.1.10:8501）を設定すると、同じネットワーク上のスマホで読み取れます。")
    st.text_input("共有URL", value=share_url, key="share_url_display")
    c_qr1, c_qr2 = st.columns([1, 1.4])
    with c_qr1:
        if qr_img is not None:
            st.image(qr_img, caption="このQRをスマホで読み取ると神託結果を表示します。", width=260)
        else:
            st.warning("QR画像を表示するには `pip install qrcode[pil]` を実行してください。")
    with c_qr2:
        st.markdown(render_glass_message(
            f"共有内容\n"
            f"- 神: {char_names[k]}\n"
            f"- 誓願: {top_vow_title}\n"
            f"- 格言: {selected_quote_text or '（なし）'}"
        ), unsafe_allow_html=True)

else:
    st.info("左サイドバーで設定して、**🧪 QUBOで観測** を押してください。")
