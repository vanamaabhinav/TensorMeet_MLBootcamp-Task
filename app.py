import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

from src.pipeline.stt import WhisperTranscriber
from src.pipeline.refiner import TranscriptRefiner
from src.pipeline.minutes_generator import MeetingDocumentationGenerator

st.set_page_config(page_title="TensorMeet", page_icon="T", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        max-width: 1200px;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif !important;
        color: #1D1D1F !important;
    }
    
    .stTextInput>div>div>input {
        border: 1px solid #E5E5EA !important;
        border-radius: 8px !important;
        background-color: #F5F5F7 !important;
        color: #1D1D1F !important;
    }
    
    .stFileUploader>div>div {
        border: 1px dashed #E5E5EA !important;
        border-radius: 12px !important;
        background-color: #F5F5F7 !important;
    }
    
    .stButton>button {
        border: none !important;
        border-radius: 8px !important;
        background-color: #0071E3 !important;
        color: white !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        box-shadow: none !important;
        transition: opacity 0.2s ease;
    }
    .stButton>button:hover {
        opacity: 0.8 !important;
        color: white !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #E5E5EA;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 12px;
        padding-bottom: 12px;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 2px solid #0071E3 !important;
        color: #0071E3 !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin-bottom: 2rem; display: flex; justify-content: flex-start;">
    <div style="display: flex; flex-direction: column; align-items: flex-end;">
        <div style="display: flex; align-items: baseline;">
            <span style="font-size: 3.5rem; font-weight: 800; color: #1D1D1F; line-height: 1;">T</span>
            <span style="font-size: 1.6rem; font-weight: 700; color: #1D1D1F; letter-spacing: -0.5px; margin-left: -2px;">ensorMeet</span>
        </div>
        <div style="font-size: 0.75rem; font-weight: 600; color: #86868B; letter-spacing: 1.5px; text-transform: uppercase; margin-top: -4px;"> by EnsembleStrike</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### Configuration")
api_key_input = st.text_input("Gemini API Key", type="password", help="Enter your own key, or leave blank to use the server's default key.")
actual_api_key = api_key_input if api_key_input else os.environ.get("GEMINI_API_KEY", "")

st.markdown("---")
st.markdown("### Supported formats\n`.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`")

uploaded_file = st.file_uploader("Upload Meeting Recording", type=['mp3', 'wav', 'm4a', 'ogg', 'flac'])

if uploaded_file is not None:
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    if file_ext not in ['.mp3', '.wav', '.m4a', '.ogg', '.flac']:
        st.error("Invalid file type uploaded. Please upload a valid audio file.")
    else:
        st.audio(uploaded_file)
        
        if st.button("Process Meeting Recording"):
            if not actual_api_key:
                st.error("Please enter a Gemini API Key to proceed, or configure it on the server.")
            else:
                with st.status("Processing Meeting...", expanded=True) as status:
                    st.write("Saving audio file...")
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_audio_path = tmp_file.name

                    try:
                        st.write("Stage 1: Transcribing with Whisper (this might take a minute)...")
                        transcriber = WhisperTranscriber()
                        raw_transcript = transcriber.transcribe(tmp_audio_path)
                        
                        st.write("Stage 2: Refining Transcript with Gemini...")
                        refiner = TranscriptRefiner(api_key=actual_api_key)
                        refined_transcript = refiner.refine(raw_transcript)
                        
                        st.write("Stage 3: Generating Minutes & Actions...")
                        generator = MeetingDocumentationGenerator(api_key=actual_api_key)
                        record = generator.generate(refined_transcript)
                        
                        status.update(label="Processing Complete!", state="complete", expanded=False)
                        
                        st.session_state['raw'] = raw_transcript
                        st.session_state['refined'] = refined_transcript
                        st.session_state['record'] = record
                        
                    except Exception as e:
                        status.update(label="Processing Failed", state="error")
                        st.error(f"Error: {str(e)}")
                    finally:
                        os.unlink(tmp_audio_path)

        if 'record' in st.session_state:
            st.success("Meeting processing completed successfully!")
            
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "Transcripts", 
                "Summary & Minutes", 
                "Decisions", 
                "Action Items", 
                "Export"
            ])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Raw Transcript")
                    st.write(st.session_state['raw'])
                with col2:
                    st.subheader("Refined Transcript")
                    st.write(st.session_state['refined'])
            
            with tab2:
                st.subheader("Executive Summary")
                st.write(st.session_state['record'].summary)
                
                st.subheader("Meeting Minutes")
                for min_pt in st.session_state['record'].minutes:
                    st.markdown(f"- {min_pt}")
                    
            with tab3:
                st.subheader("Key Decisions")
                if st.session_state['record'].decisions:
                    for dec in st.session_state['record'].decisions:
                        st.markdown(f"- {dec}")
                else:
                    st.info("No formal decisions were reached.")
                    
            with tab4:
                st.subheader("Action Items")
                if st.session_state['record'].action_items:
                    for item in st.session_state['record'].action_items:
                        st.markdown(f"**Task:** {item.description}")
                        st.markdown(f"**Owner:** {item.owner} | **Deadline:** {item.deadline}")
                        st.markdown("---")
                else:
                    st.info("No action items were assigned.")
                    
            with tab5:
                json_str = st.session_state['record'].model_dump_json(indent=2)
                st.download_button("Download JSON", json_str, file_name="meeting_record.json", mime="application/json")
                
                md_str = f"# Meeting Record\n\n## Summary\n{st.session_state['record'].summary}\n\n## Minutes\n"
                for m in st.session_state['record'].minutes:
                    md_str += f"- {m}\n"
                md_str += "\n## Decisions\n"
                if st.session_state['record'].decisions:
                    for d in st.session_state['record'].decisions:
                        md_str += f"- {d}\n"
                else:
                    md_str += "None\n"
                md_str += "\n## Action Items\n"
                if st.session_state['record'].action_items:
                    for a in st.session_state['record'].action_items:
                        md_str += f"- {a.description} (Owner: {a.owner}, Deadline: {a.deadline})\n"
                else:
                    md_str += "None\n"
                    
                st.download_button("Download Markdown", md_str, file_name="meeting_record.md", mime="text/markdown")
else:
    st.markdown("""
    <div style="background-color: #F5F5F7; padding: 2.5rem; border-radius: 12px; margin-top: 1rem; border: 1px solid #E5E5EA;">
        <h2 style="margin-top: 0; color: #1D1D1F; font-size: 1.8rem; font-weight: 600;">Streamline Your Meetings</h2>
        <p style="color: #48484A; font-size: 1.1rem; line-height: 1.6; margin-bottom: 0;">
            Upload your meeting audio to automatically generate highly accurate transcripts, intelligent executive summaries, 
            key decisions, and assignable action items. Powered by Whisper and Gemini.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="padding: 1.5rem; border: 1px solid #E5E5EA; border-radius: 12px; height: 100%; background-color: #FFFFFF;">
            <div style="color: #0071E3; font-weight: 700; font-size: 1.2rem; margin-bottom: 0.5rem;">1. Upload</div>
            <p style="color: #86868B; margin: 0; font-size: 0.95rem;">Provide your meeting audio in any standard format (MP3, WAV, M4A).</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="padding: 1.5rem; border: 1px solid #E5E5EA; border-radius: 12px; height: 100%; background-color: #FFFFFF;">
            <div style="color: #0071E3; font-weight: 700; font-size: 1.2rem; margin-bottom: 0.5rem;">2. Process</div>
            <p style="color: #86868B; margin: 0; font-size: 0.95rem;">Our AI pipeline transcribes and refines the audio to extract insights.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="padding: 1.5rem; border: 1px solid #E5E5EA; border-radius: 12px; height: 100%; background-color: #FFFFFF;">
            <div style="color: #0071E3; font-weight: 700; font-size: 1.2rem; margin-bottom: 0.5rem;">3. Export</div>
            <p style="color: #86868B; margin: 0; font-size: 0.95rem;">Review and download your ready-to-share JSON or Markdown records.</p>
        </div>
        """, unsafe_allow_html=True)
