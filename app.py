import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import base64

# ==========================================
# 1. 页面与全局美化配置 (Dark Tech / Bento Style)
# ==========================================
st.set_page_config(page_title="纯净听写记录仪 Pro", page_icon="🎙️", layout="centered")

# 注入自定义 CSS
st.markdown("""
    <style>
    /* 全局字体和背景微调 */
    .stApp {
        background-color: #0d1117;
    }
    /* 美化主标题 */
    h1 {
        text-align: center;
        font-weight: 700;
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0rem;
    }
    .subtitle {
        text-align: center;
        color: #8b949e;
        font-size: 14px;
        margin-bottom: 2rem;
    }
    /* 美化音频播放器 */
    audio {
        width: 100%;
        border-radius: 8px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    /* 卡片式容器模拟 (给区块增加间距) */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 3rem !important;
    }
    /* 表单边框淡化 */
    [data-testid="stForm"] {
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 24px;
        background-color: #161b22;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 状态初始化
# ==========================================
if 'vocab_list' not in st.session_state:
    st.session_state.vocab_list = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'records' not in st.session_state:
    st.session_state.records = []
if 'setup_done' not in st.session_state:
    st.session_state.setup_done = False

# ==========================================
# 3. 核心功能函数
# ==========================================
def parse_markdown_table(md_text):
    """解析 Markdown 表格为字典列表"""
    parsed_data = []
    lines = md_text.strip().split('\n')
    for line in lines:
        if not line.strip() or '---' in line or '单词' in line:
            continue
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if len(parts) >= 2:
            parsed_data.append({"word": parts[0], "meaning": parts[1]})
    return parsed_data

def get_autoplay_audio_html(text):
    """生成带 autoplay 属性的 base64 音频 HTML"""
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    b64 = base64.b64encode(fp.getvalue()).decode()
    
    # 使用 HTML5 audio 标签，注入 base64 音频并开启 autoplay 与 controls
    audio_html = f'''
        <audio controls autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            您的浏览器不支持音频播放。
        </audio>
    '''
    return audio_html

def generate_markdown_report():
    """生成 Markdown 报告"""
    md_content = "# 📅 每日单词听写记录\n\n"
    md_content += "| 标准拼写 | 标准释义 | 我的拼写 | 我的释义 |\n"
    md_content += "|---|---|---|---|\n"
    for record in st.session_state.records:
        md_content += f"| **{record['std_word']}** | {record['std_meaning']} | {record['user_word']} | {record['user_meaning']} |\n"
    return md_content

def reset_session():
    st.session_state.vocab_list = []
    st.session_state.current_index = 0
    st.session_state.records = []
    st.session_state.setup_done = False
    st.rerun()

# ==========================================
# 4. 页面 UI 构建
# ==========================================
st.markdown("<h1>🎙️ 纯净听写记录仪</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>专注输入 • 自动播放 • Markdown 原生支持</div>", unsafe_allow_html=True)

# ----------------- 视图 1：数据导入 -----------------
if not st.session_state.setup_done:
    st.markdown("### 📥 导入听写词库")
    
    # 使用 Tabs 优化界面，支持文件上传和纯文本粘贴
    tab1, tab2 = st.tabs(["📁 上传 .md 文件", "✍️ 粘贴 Markdown 表格"])
    
    parsed_data = None
    
    with tab1:
        st.info("💡 请直接上传由 OpenClaw 或 Obsidian 导出的 .md 单词表文件。")
        uploaded_file = st.file_uploader("选择一个 Markdown 文件", type=['md'])
        if st.button("🚀 从文件开始听写", type="primary", use_container_width=True, key="btn_file"):
            if uploaded_file is not None:
                content = uploaded_file.read().decode("utf-8")
                parsed_data = parse_markdown_table(content)
            else:
                st.warning("请先上传文件！")
                
    with tab2:
        md_input = st.text_area("将 Markdown 表格粘贴在此处：", height=150, 
                                placeholder="| 单词 | 中文释义 |\n|---|---|\n| extraction | 提取 |")
        if st.button("🚀 从文本开始听写", type="primary", use_container_width=True, key="btn_text"):
            if md_input:
                parsed_data = parse_markdown_table(md_input)
            else:
                st.warning("请先粘贴数据！")

    # 处理解析结果
    if parsed_data is not None:
        if parsed_data:
            st.session_state.vocab_list = parsed_data
            st.session_state.setup_done = True
            st.rerun()
        else:
            st.error("解析失败！请检查文件或内容中是否包含标准的 Markdown 表格（由 `|` 分隔）。")

# ----------------- 视图 2：听写进行中 -----------------
elif st.session_state.current_index < len(st.session_state.vocab_list):
    total = len(st.session_state.vocab_list)
    curr = st.session_state.current_index
    current_word_data = st.session_state.vocab_list[curr]
    
    # 顶部状态栏：进度指示器与防中断导出
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress((curr) / total, text=f"当前进度: {curr + 1} / {total}")
    with col2:
        temp_md = generate_markdown_report()
        st.download_button("💾 暂存当前进度", temp_md, file_name="听写暂存记录.md", use_container_width=True)

    st.divider()

    # 音频播放区 (自动播放)
    st.markdown("#### 🎧 正在听写...")
    # 调用含有 autoplay 的 HTML 组件
    audio_html = get_autoplay_audio_html(current_word_data["word"])
    st.components.v1.html(audio_html, height=60)
    
    # 盲打输入表单
    with st.form(key=f"dictation_form_{curr}", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            user_w = st.text_input("📝 拼写记录 (Word)", autocomplete="off", placeholder="记录你听到的英文")
        with c2:
            user_m = st.text_input("💡 释义记录 (Meaning)", autocomplete="off", placeholder="记录该词的中文意思")
        
        st.markdown("<br>", unsafe_allow_html=True) # 增加一点空隙
        submit_btn = st.form_submit_button("记录并进入下一个 ⏭️", use_container_width=True)
        
        if submit_btn:
            st.session_state.records.append({
                "std_word": current_word_data["word"],
                "std_meaning": current_word_data["meaning"],
                "user_word": user_w.strip() if user_w.strip() else "—",
                "user_meaning": user_m.strip() if user_m.strip() else "—"
            })
            st.session_state.current_index += 1
            st.rerun()

# ----------------- 视图 3：听写完成与导出 -----------------
else:
    st.balloons()
    
    st.success("🎉 今日听写记录完成！你的专注力很棒。")
    
    # 结果数据看板
    col_a, col_b = st.columns(2)
    col_a.metric("完成词汇量", f"{len(st.session_state.records)} 个")
    col_b.metric("听写状态", "已全部记录")

    st.markdown("### 📊 本次记录对比对照表")
    df = pd.DataFrame(st.session_state.records)
    df.columns = ["标准拼写", "标准释义", "我的拼写", "我的释义"]
    st.dataframe(df, use_container_width=True)
    
    st.divider()
    
    # 导出与重新开始按钮组
    final_md = generate_markdown_report()
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            label="⬇️ 导出完整 Markdown 文件 (.md)",
            data=final_md,
            file_name="今日听写对照记录.md",
            mime="text/markdown",
            use_container_width=True,
            type="primary"
        )
    with c2:
        if st.button("🔄 开启新一轮听写", use_container_width=True):
            reset_session()
