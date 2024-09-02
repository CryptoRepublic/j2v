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
    
    # Salva il video di sfondo localmente
    with open('background_video.mp4', 'wb') as f:
        f.write(video_response.content)
    
    # Carica il video di sfondo
    clip = VideoFileClip('background_video.mp4').resize(width=640)  # Riduci la risoluzione per evitare problemi
    
    text_clips = []
    for overlay in data["video"]["overlayTexts"]:
        # Crea un clip di testo
        txt_clip = (
            TextClip(overlay["text"], fontsize=overlay["size"], color=overlay["color"], font='Arial')  # Usa Arial se disponibile
            .set_position((
                lambda x: int(clip.w * float(x.strip('%')) / 100) if '%' in x else x, 
                lambda y: int(clip.h * float(y.strip('%')) / 100) if '%' in y else y
            )(overlay["position"]["x"]),
            (overlay["position"]["y"]))
            .set_duration(clip.duration)
        )
        
        # Se c'è uno sfondo colorato, aggiungi un'immagine di sfondo semi-trasparente
        if overlay.get("background"):
            bg_color = overlay["background"]["color"]
            bg_opacity = overlay["background"].get("opacity", 0.6)
            bg_clip = (
                TextClip(overlay["text"], fontsize=overlay["size"], color=bg_color, font='Arial', size=(clip.w, clip.h))
                .set_opacity(bg_opacity)
                .set_position((
                    lambda x: int(clip.w * float(x.strip('%')) / 100) if '%' in x else x, 
                    lambda y: int(clip.h * float(y.strip('%')) / 100) if '%' in y else y
                )(overlay["position"]["x"]),
                (overlay["position"]["y"]))
                .set_duration(clip.duration)
            )
            text_clips.append(CompositeVideoClip([bg_clip, txt_clip]))
        else:
            text_clips.append(txt_clip)
    
    # Combina il video di sfondo con i testi
    final_clip = CompositeVideoClip([clip] + text_clips)
    final_clip.write_videofile("output_video.mp4", codec="libx264", fps=24)

# Interfaccia Streamlit
st.title('Generatore di Video con Testo Sovrapposto')

json_input = st.text_area("Inserisci il JSON per il video", height=300, value='''
{
    "video": {
        "background": {
            "type": "video",
            "url": "https://videos.pexels.com/video-files/1034068/1034068-hd_1920_1080_25fps.mp4"
        },
        "overlayTexts": [
            {
                "text": "Testo Sovrapposto 1",
                "position": {
                    "x": "50%",
                    "y": "20%"
                },
                "font": "Arial",
                "size": 30,
                "color": "#FFFFFF",
                "background": {
                    "color": "#000000",
                    "opacity": 0.6
                }
            },
            {
                "text": "Testo Sovrapposto 2",
                "position": {
                    "x": "50%",
                    "y": "80%"
                },
                "font": "Arial",
                "size": 25,
                "color": "#FFFFFF",
                "background": {
                    "color": "#000000",
                    "opacity": 0.6
                }
            }
        ]
    }
}
''')

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
