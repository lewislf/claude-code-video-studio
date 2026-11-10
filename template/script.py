"""Script as data: the single source for the voice (tts.py), the scenes (scenes/<group>/build_<group>.py) and the assembly (assemble.py).

SCENES = [(scene id, title, [segments])]. Segment = (spoken text, pause after in s, visual).
The visual is free-form: it names the subject ("a") and whatever the scene build needs. Each segment becomes one clip in the assembly.
Write numbers as words in the spoken text ("two thousand thirteen"); PRONUNCIATION swaps words only in the audio.
"""

LANG = "en"  # ISO code for OmniVoice and whisper; any language OmniVoice supports ("pt", "es", ...)
PRONUNCIATION = {}  # word in the text -> how the voice should say it, e.g. {"GIF": "jif"}
# VOICE = "en_deep_uk_a"  # optional: a name from studio/voices/, or {"ref": wav, "ref_txt": exact transcript, "speed": 0.9}
# MUSIC = ["MusicGen prompt 1", "prompt 2"]                                                   # optional

P, G = 1.4, 0.5  # long pause and short breath

SCENES = [
  ("sky", "The sky", [
    ("Look up on a clear day. The sky is blue.", G, {"a": "sky"}),
    ("But sunlight is white. It has every color mixed together.", P, {"a": "prism"}),
  ]),
  ("rayleigh", "Rayleigh", [
    ("Air scatters blue light more than red light. This is called Rayleigh scattering.", G, {"a": "scatter"}),
    ("So wherever you look, blue reaches you.", P, {"a": "title", "text": "BLUE REACHES YOU"}),
  ]),
]

if __name__ == "__main__":
    n = sum(len(t.split()) for _, _, s in SCENES for t, _, _ in s)
    print(n, "words, ~", round(n / 140 * 60), "s")
