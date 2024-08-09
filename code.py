import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
import time
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk
nltk.download('punkt')

# Mapping ngôn ngữ với mã ngôn ngữ
language_map = {
    "English": "en",
    "Chinese (Mandarin)": "zh-Hans",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "Arabic (Standard)": "ar",
    "Bengali": "bn",
    "Russian": "ru",
    "Portuguese": "pt",
    "Indonesian": "id",
    "Vietnamese": "vi"
}

# Hàm lấy id của video từ link YouTube
def get_video_id(url):
    yt = YouTube(url)
    return yt.video_id

# Hàm lấy transcript của video YouTube
def get_transcript(video_id, language_code):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript([language_code])
        transcript_data = transcript.fetch()
        
        # Định dạng transcript với thời gian và dấu phẩy
        transcript_formatted = ""
        for entry in transcript_data:
            text = entry['text'].replace("\n", ", ")  # Thay xuống dòng bằng dấu phẩy
            time_format = f"{int(entry['start']//3600):02}:{int((entry['start']%3600)//60):02}:{int(entry['start']%60):02}"  # Chuyển đổi thời gian thành định dạng giờ:phút:giây
            transcript_formatted += f"{time_format} - {text},\n\n"  # Thêm dòng trống để mỗi timestamp nằm trên dòng riêng
        
        return transcript_formatted
    except Exception as e:
        return f"Unable to retrieve transcript: {str(e)}"

# Hàm tóm tắt transcript
def summarize_transcript(transcript_text):
    parser = PlaintextParser.from_string(transcript_text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 5)  # Số câu tóm tắt (có thể điều chỉnh)
    summary_text = "\n\n".join([str(sentence) for sentence in summary])
    return summary_text

# Giao diện Streamlit
st.set_page_config(page_title="YouTube Transcript Extractor", layout="wide")

# Lựa chọn page
page = st.sidebar.selectbox("Choose a page:", ["Extract Transcript", "Summarize Transcript"])

if page == "Extract Transcript":
    st.markdown("<h1 style='text-align: center; color: #4B8BBE;'>YouTube Video Transcript Extractor</h1>", unsafe_allow_html=True)

    # Nhập link YouTube
    st.markdown("<p style='text-align: center; font-size: 18px;'>Enter the YouTube video link:</p>", unsafe_allow_html=True)
    video_url = st.text_input("", key="video_url_input")

    # Lựa chọn ngôn ngữ
    st.markdown("<p style='text-align: center; font-size: 18px;'>Select the language for the transcript:</p>", unsafe_allow_html=True)
    language = st.selectbox("", list(language_map.keys()), key="language_select")

    # Hiển thị transcript khi người dùng nhấn nút
    if st.button("Get Transcript", key="get_transcript_button"):
        if video_url:
            video_id = get_video_id(video_url)
            language_code = language_map[language]
            
            # Bắt đầu đo thời gian
            start_time = time.time()
            
            # Hiển thị thanh tiến trình
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Giả lập quá trình tải với các bước
            for percent_complete in range(100):
                time.sleep(0.01)  # Giả lập thời gian chờ
                progress_bar.progress(percent_complete + 1)
                status_text.text(f"Loading... {percent_complete + 1}%")
            
            # Lấy transcript sau khi quá trình tải hoàn thành
            transcript = get_transcript(video_id, language_code)
            
            # Lưu transcript vào session state
            st.session_state['transcript'] = transcript
            
            # Hiển thị transcript với định dạng đẹp
            st.markdown("<div style='font-size: 16px; line-height: 1.6;'>", unsafe_allow_html=True)
            st.write(transcript)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Tính toán và hiển thị thời gian hoàn thành
            end_time = time.time()
            total_time = end_time - start_time
            st.success(f"Transcript loaded successfully in {total_time:.2f} seconds.")
            
        else:
            st.error("Please enter a valid YouTube video link.")

    # Tùy chỉnh thêm cho trang web chuyên nghiệp
    st.markdown("""
        <style>
        .stProgress > div > div > div > div {
            background-color: #4B8BBE;
        }
        .stButton button {
            background-color: #4B8BBE;
            color: white;
            font-size: 16px;
            border-radius: 8px;
        }
        .stButton button:hover {
            background-color: #306998;
        }
        </style>
        """, unsafe_allow_html=True)

elif page == "Summarize Transcript":
    st.markdown("<h1 style='text-align: center; color: #4B8BBE;'>Transcript Summary</h1>", unsafe_allow_html=True)
    
    if 'transcript' in st.session_state:
        transcript = st.session_state['transcript']
        summary = summarize_transcript(transcript)
        
        # Hiển thị tóm tắt
        st.markdown("<div style='font-size: 16px; line-height: 1.6;'>", unsafe_allow_html=True)
        st.write(summary)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("No transcript found. Please extract a transcript first.")
