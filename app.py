import streamlit as st
from google import genai

# Sayfa Yapılandırması
st.set_page_config(page_title="Tıbbi Vaka Tahmin & Eğitim Asistanı", page_icon="🩺", layout="centered")

# Tasarım ve Renkler (Özel CSS)
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(135deg, #3b82f6 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        text-align: center;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #2563eb 0%, #db2777 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        width: 100%;
        box-shadow: 0 4px 14px 0 rgba(59, 130, 246, 0.3);
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #be185d 100%);
        transform: translateY(-2px);
    }
    .stTextArea textarea, .stSelectbox select, .stTextInput input {
        background-color: #1e293b;
        color: #f8fafc;
        border: 1px solid #334155;
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# Başlık Kısmı
st.markdown('<div class="main-title">🩺 Tıbbi Vaka Tahmin & Eğitim Asistanı</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Klinik bulguları analiz edin, vakayı çözün ve hastalıkların hücresel mekanizmalarını keşfedin.</div>', unsafe_allow_html=True)

# API Anahtarı Kontrolü
api_key = st.secrets.get("GEMINI_API_KEY")

# Oturum Durumu (Session State) Tanımlamaları
if "case_text" not in st.session_state:
    st.session_state.case_text = ""
if "target_disease" not in st.session_state:
    st.session_state.target_disease = ""

# Kullanıcı Seçimleri
difficulty = st.selectbox("Zorluk Seviyesi Seçin", ["Kolay (Tipik Semptomlar)", "Orta (Kombine Bulgular)", "Uzman (Nadir Vaka / Kompleks)"])

if st.button("🎲 Yeni Klinik Vaka Üret"):
    if not api_key:
        st.error("Sistemde API anahtarı bulunamadı. Streamlit Secrets ayarlarına GEMINI_API_KEY ekleyin.")
    else:
        with st.spinner("🔍 Hastalık vakası kurgulanıyor ve laboratuvar verileri hazırlanıyor..."):
            try:
                client = genai.Client(api_key=api_key)
                prompt = f"""
                Sen uzman bir tıp profesörüsün. Zorluk seviyesi '{difficulty}' olan eğitsel bir tıbbi vaka senaryosu oluştur.
                Lütfen yanıtını kesinlikle şu iki bölümde ver:
                
                BÖLÜM 1 (VAKA SUNUMU): Hastanın yaşı, cinsiyeti, temel yakınması, öyküsü, fizik muayene ve laboratuvar bulgularını içeren detaylı bir klinik tablo yaz. Asla hastalık adını buraya yazma.
                
                BÖLÜM 2 (GİZLİ TEŞHİS): Metnin en altına tam olarak şu formatta yaz: [GİZLİ_HASTALIK: Hastalğın Adı]
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                
                if response and response.text:
                    full_response = response.text
                    if "[GİZLİ_HASTALIK:" in full_response:
                        parts = full_response.split("[GİZLİ_HASTALIK:")
                        st.session_state.case_text = parts[0].strip()
                        st.session_state.target_disease = parts[1].replace("]", "").strip()
                    else:
                        st.session_state.case_text = full_response
                        st.session_state.target_disease = "Bilinmeyen Vaka"
                else:
                    st.error("Vaka üretilemedi, lütfen tekrar deneyin.")
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")

# Vaka Oluştuysa Ekranı Göster
if st.session_state.case_text:
    st.markdown("### 📋 Vaka Dosyası")
    st.info(st.session_state.case_text)
    
    user_guess = st.text_input("💡 Sizce Bu Hastalık Nedir? (Tahmininizi yazın)")
    
    if st.button("Tahmini Kontrol Et & Eğitsel Analiz Al"):
        if not user_guess.strip():
            st.warning("Lütfen bir tahmin yazın.")
        else:
            with st.spinner("🧬 Teşhis değerlendiriliyor ve biyolojik mekanizma analiz ediliyor..."):
                try:
                    client = genai.Client(api_key=api_key)
                    eval_prompt = f"""
                    Gerçek Doğru Teşhis: {st.session_state.target_disease}
                    Kullanıcının Tahmini: {user_guess.strip()}
                    
                    Görevin:
                    1. Kullanıcının tahmininin doğru olup olmadığını yapıcı ve motive edici bir dille değerlendir.
                    2. Doğru hastalığın ne olduğunu açıkla.
                    3. Bu hastalığın vücuttaki hücresel, anatomik ve fizyolojik mekanizmalarını (neden bu semptomların ortaya çıktığını) derinlemesine ama lise/üniversite seviyesinde anlaşılır bir biyoloji dersi gibi açıkla.
                    """
                    
                    eval_response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=eval_prompt,
                    )
                    
                    if eval_response and eval_response.text:
                        st.markdown("### 📊 Sonuç ve Bilimsel Açıklama")
                        st.markdown(eval_response.text)
                except Exception as e:
                    st.error(f"Analiz sırasında hata oluştu: {e}")