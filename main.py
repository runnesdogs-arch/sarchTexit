import streamlit as st
import os
import google.generativeai as genai

# --- 1. ページ初期設定 ---
st.set_page_config(
    page_title="多職種視点型・文献＆症例事例検索システム",
    layout="wide",
    page_icon="🔍"
)

# --- 2. アクセス制御（簡易パスワード機能） ---
PASSWORD = st.secrets.get("APP_PASSWORD", "ot_pass_2026")

st.sidebar.title("🔒 アクセス制御")
input_pass = st.sidebar.text_input("アクセスパスワードを入力してください", type="password")

if input_pass != PASSWORD:
    st.title("多職種視点型・文献＆症例事例検索システム")
    st.info("サイドバーから正しいパスワードを入力してログインしてください。")
    st.stop()

# --- 3. Gemini API設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("GEMINI_API_KEY が Secrets に設定されていません。")
    st.stop()

genai.configure(api_key=api_key)
# 最新の gemini-3.6-flash に設定
model = genai.GenerativeModel("gemini-3.6-flash")

# --- 4. メイン画面ヘッダー ---
st.title("多職種視点型・文献＆症例事例検索システム")
st.caption("作業療法士・多職種連携のための思考・アセスメント補完アシスタント")

# --- 5. タブ構成（3つのアプローチ） ---
tab1, tab2, tab3 = st.tabs([
    "💡 困りごと・症例から逆算検索", 
    "🔍 キーワード・文献指定検索", 
    "🔄 多職種視点変換・通訳"
])

# ==========================================
# タブ1：困りごと・症例から逆算検索
# ==========================================
with tab1:
    st.subheader("目の前の困りごと・現象からの多角分析")
    st.write("臨床や現場で起きている具象的な状況を入力すると、多職種レンズを通して原因仮説とアプローチ案を提示します。")

    trouble_text = st.text_area(
        "目の前の困りごと・行動（自由記述）",
        placeholder="例：小1男児。授業中に教室を飛び出してしまう。声かけを聞き入れてくれない。"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        target_age = st.text_input("対象（年齢・学年・診断など）", placeholder="例：7歳（小1）、ASD傾向")
    with col2:
        focus_roles = st.multiselect(
            "特に重視したい視点（複数選択可）",
            ["OT（作業療法士）", "PT（理学療法士）", "医師・医学", "看護師", "保育士・児童指導員", "特別支援教育"],
            default=["OT（作業療法士）", "保育士・児童指導員"]
        )

    if st.button("多角分析＆アプローチ案を生成", type="primary"):
        if not trouble_text:
            st.warning("困りごとの内容を入力してください。")
        else:
            with st.spinner("Geminiが多職種レンズで分析中..."):
                prompt = f"""
あなたは作業療法士をはじめとする多職種チームの優秀な臨床アシスタントです。
以下の困りごとについて、多角的な視点から原因仮説と解決への示唆を提示してください。

【対象情報】
{target_age}

【目の前の困りごと】
{trouble_text}

【重視する視点】
{", ".join(focus_roles)}

以下の構成で出力してください：
1. **背景にある多角的な原因・仮説（OT/医学/保育・指導員などの各レンズより）**
2. **推奨される検索キーワード例（J-STAGEやCiNiiで深く調べる際の検索語）**
3. **現場で明日から試せる具体的アプローチ案**
4. **配慮・関連する疾患特性・薬・制度に関するメモ（該当する場合）**
"""
                response = model.generate_content(prompt)
                st.markdown(response.text)

# ==========================================
# タブ2：キーワード・文献指定検索
# ==========================================
with tab2:
    st.subheader("キーワードによるダイレクト文献・知見検索")
    
    search_keyword = st.text_input("検索キーワード", placeholder="例：感覚過敏 偏食 食育")
    search_domain = st.selectbox(
        "対象領域・ジャンル",
        ["ノージャンル（全般網羅）", "リハビリ・コメディカル全般", "医学・医療・看護", "保育・幼児教育", "児童福祉・特別支援教育"]
    )
    
    if st.button("検索＆要約実行"):
        if not search_keyword:
            st.warning("キーワードを入力してください。")
        else:
            with st.spinner("関連知見を検索・要約中..."):
                prompt = f"""
以下のキーワードと領域に基づいて、臨床で役立つ文献・症例の傾向と具体的知見をまとめてください。

【検索キーワード】: {search_keyword}
【指定領域】: {search_domain}

以下の構成で回答してください：
1. **概要・このテーマにおける臨床的ポイント**
2. **各職種（OT/PT/医師/保育・指導員）の着眼点の違い**
3. **関連する文献・症例報告でよく見られるアプローチ例**
"""
                response = model.generate_content(prompt)
                st.markdown(response.text)

# ==========================================
# タブ3：多職種視点変換・通訳
# ==========================================
with tab3:
    st.subheader("多職種への説明・チーム共有用の視点変換")
    st.write("自身の評価見解やメモを、他職種に伝わりやすい言葉・着眼点に自動翻訳します。")

    my_assessment = st.text_area(
        "自分の見解・伝えたい内容（OT視点のメモなど）",
        placeholder="例：前庭感覚の低登録があり、姿勢保持が困難で離席につながっている。座面の調整と適度な固有感覚入力が必要。"
    )
    
    target_role = st.selectbox(
        "伝えたい相手（翻訳先の職種・立場）",
        ["医師（要点・医学的根拠重視）", "看護師（生活リズム・ケア重視）", "保育士・児童指導員（現場での対応具体策重視）", "保護者（わかりやすい言葉と安心感重視）"]
    )

    if st.button("相手に合わせた表現に変換"):
        if not my_assessment:
            st.warning("内容を入力してください。")
        else:
            with st.spinner("視点を変換中..."):
                prompt = f"""
以下の作業療法士（または専門職）による見解を、【{target_role}】に対して最も伝わりやすく、現場で共有しやすい表現に変換・要約してください。

【元の見解・メモ】
{my_assessment}

専門用語を適切にかみ砕きつつ、相手の職種が求める着眼点（治療、生活、集団指導、家庭での対応など）に焦点を当てた文章を出力してください。
"""
                response = model.generate_content(prompt)
                st.markdown(response.text)
