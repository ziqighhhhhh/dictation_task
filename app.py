import streamlit as st
import pandas as pd
import re
from gtts import gTTS
import io

# ==========================================
# 页面配置 (暗黑实验室风格)
# ==========================================
st.set_page_config(page_title="自主听写记录仪", page_icon="🎙️", layout="centered")

# ==========================================
# 状态初始化 (防止中断丢失数据)
# ==========================================
if 'vocab_list' not in st.session_state:
    st.session_state.vocab_list = []      # 待听写的单词列表
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0    # 当前听写到第几个
if 'records' not in st.session_state:
    st.session_state.records = []         # 记录用户的输入
if 'setup_done' not in st.session_state:
    st.session_state.setup_done = False   # 是否已导入数据

# ==========================================
# 核心功能函数
# ==========================================
def parse_markdown_table(md_text):
    """解析 Markdown 表格为字典列表"""
    parsed_data = []
    lines = md_text.strip().split('\n')
    for line in lines:
        # 跳过空行、表头分隔线(---|---)和纯表头文本
        if not line.strip() or '---' in line or '单词' in line:
            continue
        # 提取 | xxx | yyy | 格式
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if len(parts) >= 2:
            parsed_data.append({"word": parts[0], "meaning": parts[1]})
    return parsed_data

def generate_audio(text):
    """生成 TTS 语音流"""
    tts = gTTS(text=text, lang='en')
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    return audio_fp

def generate_markdown_report():
    """生成最终/中断时的 Markdown 报告"""
    md_content = "# 📅 每日单词听写记录\n\n"
    md_content += "| 标准拼写 | 标准释义 | 我的拼写 | 我的释义 |\n"
    md_content += "|---|---|---|---|\n"
    
    for record in st.session_state.records:
        md_content += f"| **{record['std_word']}** | {record['std_meaning']} | {record['user_word']} | {record['user_meaning']} |\n"
    
    return md_content

def reset_session():
    """重置所有状态"""
    st.session_state.vocab_list = []
    st.session_state.current_index = 0
    st.session_state.records = []
    st.session_state.setup_done = False
    st.rerun()

# ==========================================
# UI 渲染逻辑
# ==========================================
st.title("🎙️ 纯净听写记录仪")

# 视图 1：数据导入
if not st.session_state.setup_done:
    st.markdown("### 📥 导入今日数据")
    md_input = st.text_area("将 OpenClaw 输出的 Markdown 表格粘贴在此处：", height=200, 
                            placeholder="| 单词 | 中文释义 |\n|---|---|\n| apple | 苹果 |")
    
    if st.button("🚀 开始解析并听写", type="primary", use_container_width=True):
        if md_input:
            parsed = parse_markdown_table(md_input)
            if parsed:
                st.session_state.vocab_list = parsed
                st.session_state.setup_done = True
                st.rerun()
            else:
                st.error("无法解析数据，请检查 Markdown 表格格式是否正确。")
        else:
            st.warning("请先粘贴数据！")

# 视图 2：听写进行中
elif st.session_state.current_index < len(st.session_state.vocab_list):
    total = len(st.session_state.vocab_list)
    curr = st.session_state.current_index
    current_word_data = st.session_state.vocab_list[curr]
    
    # 顶部状态栏：进度与中断保护
    col_prog, col_interrupt = st.columns([3, 1])
    with col_prog:
        st.progress((curr) / total, text=f"当前进度: {curr + 1} / {total}")
    with col_interrupt:
        # 提供中途导出的选项，防止有突发事件需要退出
        temp_md = generate_markdown_report()
        st.download_button("💾 暂存当前进度", temp_md, file_name="听写暂存记录.md", key="temp_save")

    st.divider()

    # 语音播放区
    st.markdown("#### 🎧 点击播放音频")
    audio_file = generate_audio(current_word_data["word"])
    st.audio(audio_file, format='audio/mp3')
    
    # 盲打输入区 (使用 form 避免每次输入字符都刷新页面)
    with st.form(key=f"dictation_form_{curr}", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            user_w = st.text_input("拼写记录 (Word)", autocomplete="off")
        with c2:
            user_m = st.text_input("释义记录 (Meaning)", autocomplete="off")
        
        submit_btn = st.form_submit_button("记录并进入下一个 ⏭️", use_container_width=True)
        
        if submit_btn:
            # 记录当前答案
            st.session_state.records.append({
                "std_word": current_word_data["word"],
                "std_meaning": current_word_data["meaning"],
                "user_word": user_w if user_w else "—",
                "user_meaning": user_m if user_m else "—"
            })
            st.session_state.current_index += 1
            st.rerun()

# 视图 3：听写完成与导出
else:
    st.balloons()
    st.success("🎉 今日听写记录完成！")
    
    # 预览表格
    df = pd.DataFrame(st.session_state.records)
    df.columns = ["标准拼写", "标准释义", "我的拼写", "我的释义"]
    st.dataframe(df, use_container_width=True)
    
    # 导出按钮
    final_md = generate_markdown_report()
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            label="📄 导出 Markdown 文件 (.md)",
            data=final_md,
            file_name="今日听写记录.md",
            mime="text/markdown",
            use_container_width=True
        )
    with c2:
        if st.button("🔄 开启新一轮听写", use_container_width=True):
            reset_session()