"""Gera só as falas novas do final, com a mesma voz e o mesmo jeito do tts.py (N tentativas por frase).

  ~/.venvs/omnivoice/bin/python tts_final.py      # tentativas em TAKES_F/<nome>_<k>.wav

A escolha da melhor tentativa é feita depois (whisper + tts.nota), fora deste processo, para caber no teto de memória.
"""
import os, sys
import soundfile as sf
import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../VoiceStudio"))
from omnivoice.models.omnivoice import OmniVoice  # noqa: E402
from omnivoice.utils.dtype import tts_dtype_name  # noqa: E402

REF = "../teste-voz/vozes/terror_grave_lento.wav"
REF_TXT = ("Era uma noite comum, até que o telefone tocou. Do outro lado, ninguém falava. "
           "Só havia uma respiração... lenta, pesada. A polícia nunca explicou o que aconteceu naquela casa. "
           "Mas os arquivos revelam algo que ninguém queria que você soubesse.")
SPEED, N = 0.85, 6
TAKES_F = "takes_final"
FRASES = {
    "tempo": "Você ouviu essa voz esse tempo todo e, provavelmente, confiou nela.",
    "falha1": "Você deve ter percebido as falhas na minha voz.",
    "falha2": "Mas será que isso é um problema do meu modelo... ou a sua simulação está falhando?",
    "riso": "Rá, rá, rá, rá, rá!",
}

if __name__ == "__main__":
    os.makedirs(TAKES_F, exist_ok=True)
    m = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cuda", dtype=getattr(torch, tts_dtype_name("cuda")))
    for nome, f in FRASES.items():
        for k in range(N):
            p = f"{TAKES_F}/{nome}_{k}.wav"
            if not os.path.exists(p):
                torch.manual_seed(9100 + 37 * k)
                a = m.generate(text=f, language="Portuguese", ref_audio=REF, ref_text=REF_TXT, speed=SPEED)[0].squeeze().float().cpu().numpy()
                sf.write(p, a, m.sampling_rate)
            print(p, flush=True)
