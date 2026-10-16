import streamlit as st
from google import genai

# Sayfa Yapılandırması
st.set_page_config(page_title="Tıbbi Vaka Tahmin & Eğitim Asistanı", page_icon="🩺", layout="centered")

# Tasarladığımız Sevimli Çizgi Film Hastane Arka Planı (Base64 Entegreli)
# Bu yöntem sayesinde harici bir dosya indirme hatası yaşanmaz.
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(255,255,255,0.65), rgba(255,255,255,0.65)), 
                    url('https://images.unsplash.com/photo-1538108149393-fbbd81895907?q=80&w=1000&auto=format&fit=crop') no-repeat center center fixed;
        background-size: cover;
    }
    
    /* Ana Başlık ve Alt Başlık Font Renkleri (Pembe Konsept) */
    .main-title {
        font-size: 2.1rem;
        font-weight: 900;
        color: #ff1493;
        text-shadow: 2px 2px 6px rgba(255,255,255,0.9);
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .highlight-pink {
        color: #ff007f;
        text-shadow: 0 0 12px rgba(255,0,127,0.5);
    }
    .sub-title {
        color: #db2777;
        font-size: 0.95rem;
        font-weight: 700;
        text-shadow: 1px 1px 4px rgba(255,255,255,0.9);
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    /* İçerik Okunabilirliği İçin Şeffaf Kutular */
    .stMarkdown, .stSelectbox, .stTextInput {
        background-color: rgba(255, 255, 255, 0.94);
        border-radius: 15px;
        color: #1e293b;
    }
    
    /* Pembe Buton Tasarımı */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #ff1493 0%, #ff69b4 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.75rem 1.5rem;
        font-size: 1.05rem;
        font-weight: bold;
        width: 100%;
        box-shadow: 0 4px 15px rgba(255, 20, 147, 0.4);
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #db2777 0%, #be185d 100%);
    }
    </style>
""", unsafe_allow_html=True)

# Başlık Alanı
st.markdown('<div class="main-title">🩺 Tıbbi Vaka Tahmin & <span class="highlight-pink">Eğitim</span> Asistanı</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Klinik bulguları analiz edin, vakayı çözün ve hastalıkların hücresel mekanizmalarını keşfedin.</div>', unsafe_allow_html=True)

# API Anahtarı Kontrolü
api_key = st.secrets.get("GEMINI_API_KEY")

# Oturum Durumları
if "case_text" not in st.session_state:
    st.session_state.case_text = ""
if "target_disease" not in st.session_state:
    st.session_state.target_disease = ""

difficulty = st.selectbox("Zorluk Seviyesi Seçin", ["Kolay (Tipik Semptomlar)", "Orta (Kombine Bulgular)", "Uzman (Nadir Vaka / Kompleks)"])

if st.button("🎲 Yeni Klinik Vaka Üret"):
    if not api_key:
        st.error("Sistemde API anahtarı bulunamadı. Lütfen Streamlit Secrets ayarlarına GEMINI_API_KEY ekleyin.")
    else:
        with st.spinner("🔍 Hastalık vakası kurgulanıyor..."):
            try:
                client = genai.Client(api_key=api_key)
                prompt = f"""
                Sen uzman bir tıp profesörüsün. Zorluk seviyesi '{difficulty}' olan eğitsel bir tıbbi vaka senaryosu oluştur.
                Lütfen yanıtını kesinlikle şu iki bölümde ver:
                
                BÖLÜM 1 (VAKA SUNUMU): Hastanın yaşı, cinsiyeti, temel yakınması, öyküsü, fizik muayene ve laboratuvar bulgularını içeren detaylı bir klinik tablo yaz. Asla hastalık adını buraya yazma.
                
                BÖLÜM 2 (GİZLİ TEŞHİS): Metnin en altına tam olarak şu formatta yaz: [GİZLİ_HASTALIK: Hastalığın Adı]
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
                    3. Bu hastalığın vücuttaki hücresel, anatomik ve fizyolojik mekanizmalarını derinlemesine ama lise/üniversite seviyesinde anlaşılır bir biyoloji dersi gibi açıkla.
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
