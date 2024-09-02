import streamlit as st
import json
import requests
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# Funzione per generare il video
def create_video(json_data):
    data = json.loads(json_data)

    # Scarica il video di sfondo
    video_url = data["video"]["background"]["url"]
    video_response = requests.get(video_url)
    with open('background_video.mp4', 'wb') as f:
        f.write(video_response.content)

    clip = VideoFileClip('background_video.mp4')

    # Crea clip dei testi
    text_clips = []
    for overlay in data["video"]["overlayTexts"]:
        txt_clip = (TextClip(overlay["text"], fontsize=overlay["size"], color=overlay["color"])
                     .set_position((overlay["position"]["x"], overlay["position"]["y"]))
                     .set_duration(clip.duration))
        
        if overlay["background"]:
            bg_clip = (TextClip(overlay["text"], fontsize=overlay["size"], color=overlay["background"]["color"],
                                bg_color=overlay["background"]["color"], size=txt_clip.size)
                        .set_opacity(overlay["background"]["opacity"])
                        .set_position((overlay["position"]["x"], overlay["position"]["y"]))
                        .set_duration(clip.duration))
            text_clips.append(CompositeVideoClip([bg_clip, txt_clip]))

    final_clip = CompositeVideoClip([clip] + text_clips)
    final_clip.write_videofile("output_video.mp4", codec="libx264")

# Interfaccia Streamlit
st.title('Generatore di Video con Testo Sovrapposto')

# Input JSON
json_input = st.text_area("Inserisci il JSON per il video", height=300)

if st.button("Crea Video"):
    if json_input:
        try:
            create_video(json_input)
            st.success("Video creato con successo!")
            st.video("output_video.mp4")
        
        except Exception as e:
            st.error(f"Si è verificato un errore: {e}")
    else:
        st.warning("Per favore, inserisci un JSON valido.")
