import streamlit as st
import json
import requests
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip

# Funzione per generare il video
def create_video(json_data):
    data = json.loads(json_data)

    # Scarica il video di sfondo
    video_url = data["video"]["background"]["url"]
    video_response = requests.get(video_url)
    
    # Salva il video di sfondo localmente
    with open('background_video.mp4', 'wb') as f:
        f.write(video_response.content)

    # Carica il video di sfondo
    clip = VideoFileClip('background_video.mp4')

    # Crea clip dei testi
    text_clips = []
    for overlay in data["video"]["overlayTexts"]:
        # Crea un'area di sfondo per il testo
        if overlay.get("background"):
            bg_color = overlay["background"]["color"]
            bg_opacity = overlay["background"].get("opacity", 0.6)
            # Crea un clip di colore per lo sfondo del testo
            background_clip = ColorClip(clip.size, color=bg_color)
            background_clip = background_clip.set_opacity(bg_opacity).set_duration(clip.duration).set_position((overlay["position"]["x"], overlay["position"]["y"]))
            text_clips.append(background_clip)

        # Crea il clip di testo
        txt_clip = (TextClip(overlay["text"], fontsize=overlay["size"], color=overlay["color"], method="label")
                     .set_position((overlay["position"]["x"], overlay["position"]["y"]))
                     .set_duration(clip.duration))
        text_clips.append(txt_clip)

    # Combina il video di sfondo con i testi
    final_clip = CompositeVideoClip([clip] + text_clips)
    final_clip.write_videofile("output_video.mp4", codec="libx264", fps=24)

# Interfaccia Streamlit
st.title('Generatore di Video con Testo Sovrapposto')

# Input JSON
json_input = st.text_area("Inserisci il JSON per il video", height=300)

if st.button("Crea Video"):
    if json_input:
        try:
            create_video(json_input)
            st.success("Video creato con successo!")
            st.video("output_video.mp4")  # Mostra il video generato
            
        except Exception as e:
            st.error(f"Si è verificato un errore: {e}")
    else:
        st.warning("Per favore, inserisci un JSON valido.")
