# 导入所需的库：Streamlit用于Web界面，os用于文件操作，shutil用于目录操作，datetime用于时间处理，time用于延时
import streamlit as st
import os
import shutil
from datetime import datetime
import time

# 配置Streamlit页面，设置标题为"临时网盘"，布局为居中
st.set_page_config(page_title="临时网盘", layout="centered")

# 定义上传文件的保存目录为'uploaded_files'
UPLOAD_DIR = 'uploaded_files'
# 设置文件过期时间为7200秒（2小时）
EXPIRE_TIME = 7200

def init_app():
    # 创建上传文件目录，如果目录已存在则不会报错
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # 显示应用标题和说明
    st.markdown("# 临时网盘")

def get_file_info(user_dir):
    # 检查用户目录是否存在且不为空
    if not (os.path.exists(user_dir) and os.listdir(user_dir)):
        return None, None, None
    # 获取目录中的第一个文件名
    file_name = os.listdir(user_dir)[0]
    # 构建完整的文件路径
    file_path = os.path.join(user_dir, file_name)
    # 获取文件的最后修改时间
    file_time = os.path.getmtime(file_path)
    return file_name, file_path, file_time

def check_file_expiry(user_dir, file_time):
    # 计算文件是否超过过期时间
    if datetime.now().timestamp() - file_time > EXPIRE_TIME:
        # 如果过期，删除整个用户目录
        shutil.rmtree(user_dir)
        # 显示过期警告
        st.warning('⚠️ 文件已过期，请重新上传')
        # 刷新页面
        st.rerun()

def save_content(user_dir, content, is_file=True):
    # 确保用户目录存在
    os.makedirs(user_dir, exist_ok=True)
    if is_file:
        # 如果是文件，构建文件保存路径
        file_path = os.path.join(user_dir, content.name)
        # 以二进制方式写入文件内容
        with open(file_path, 'wb') as f:
            f.write(content.getbuffer())
        # 显示上传成功提示
        st.success('✅ 文件上传成功！')
    else:
        # 如果是文本，保存为content.txt
        file_path = os.path.join(user_dir, 'content.txt')
        # 以UTF-8编码写入文本内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        # 显示保存成功提示
        st.success('✅ 文本保存成功！')
    # 刷新页面
    st.rerun()

def display_content(file_name, file_path):
    # 显示当前内容的标题
    st.markdown(f"### 📄 当前内容：{file_name}")
    if file_name == 'content.txt':
        try:
            # 使用 with 语句确保文件正确关闭
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            # 将文本内容存储在会话状态中
            st.session_state.text_content = text_content
            # 使用会话状态中的内容显示，而不是直接读取文件
            st.code(st.session_state.text_content, language="markdown")
        except Exception as e:
            st.error(f'读取文件时出错：{str(e)}')
    else:
        try:
            # 读取文件内容到内存
            with open(file_path, 'rb') as f:
                file_content = f.read()
            # 使用内存中的内容创建下载按钮
            st.download_button('⬇️ 下载文件', file_content, file_name=file_name, use_container_width=True)
        except Exception as e:
            st.error(f'读取文件时出错：{str(e)}')

def handle_deletion(user_dir):
    # 创建删除按钮
    if st.button('🗑️ 删除', use_container_width=True):
        try:
            # 清除会话状态中的内容
            if 'text_content' in st.session_state:
                del st.session_state.text_content
            # 添加短暂延时，确保文件句柄已释放
            time.sleep(0.1)
            # 删除用户目录
            shutil.rmtree(user_dir)
            # 显示删除成功提示
            st.success('✅ 已删除')
            # 等待2秒后刷新页面
            time.sleep(1)
            # 刷新页面
            st.rerun()
        except Exception as e:
            st.error(f'删除文件时出错：{str(e)}')
            # 如果删除失败，等待较长时间后重试
            time.sleep(1)
            st.rerun()
            try:
                shutil.rmtree(user_dir)
                st.success('✅ 已删除')
                time.sleep(1)
                # 刷新页面
                st.rerun()
            except Exception as e2:
                st.error('删除失败，请稍后重试')
                time.sleep(1)
                st.rerun()

def display_countdown(file_time):
    # 计算剩余时间
    remaining = datetime.fromtimestamp(file_time + EXPIRE_TIME) - datetime.now()
    remaining_seconds = remaining.total_seconds()
    # 显示剩余时间警告
    st.warning(f'⏳ 将在 {int(remaining_seconds/60)} 分 {int(remaining_seconds%60)} 秒后自动删除')
    # 显示进度条
    st.progress(1 - remaining_seconds/EXPIRE_TIME)
    # 等待1秒
    time.sleep(1)
    # 刷新页面更新倒计时
    st.rerun()

def handle_upload(user_dir):
    # 创建单选按钮，选择上传类型
    upload_type = st.radio(
        "选择上传类型",
        ["文件上传", "文本上传"],
        horizontal=True,
        help="支持各种格式文件或文本内容"
    )

    if upload_type == "文件上传":
        # 如果选择文件上传，显示文件上传组件
        uploaded_file = st.file_uploader('选择要上传的文件', help='文件将在2小时后自动删除')
        if uploaded_file:
            # 如果有文件上传，保存文件
            save_content(user_dir, uploaded_file, is_file=True)
    else:
        # 如果选择文本上传，显示文本输入框
        text_content = st.text_area('输入要保存的文本', height=150, help='文本将在2小时后自动删除')
        # 创建保存按钮
        if st.button('保存文本', use_container_width=True) and text_content:
            # 如果点击保存且有文本内容，保存文本
            save_content(user_dir, text_content, is_file=False)

def main():
    # 初始化应用
    init_app()
    # 创建密码输入框
    
    passcode = st.text_input(label="请输入口令")
    # 如果没有输入密码，直接返回
    if not passcode:
        return

    # 构建用户目录路径
    user_dir = os.path.join(UPLOAD_DIR, passcode)
    # 获取文件信息
    file_name, file_path, file_time = get_file_info(user_dir)

    if file_name:
        # 如果存在文件，检查是否过期
        check_file_expiry(user_dir, file_time)
        # 显示文件内容
        display_content(file_name, file_path)
        # 显示删除按钮
        handle_deletion(user_dir)
        # 显示倒计时
        display_countdown(file_time)
    else:
        # 如果不存在文件，显示上传界面
        handle_upload(user_dir)

# 程序入口点
if __name__ == '__main__':
    # 运行主函数
    main()
    # 添加空行
    st.write('')