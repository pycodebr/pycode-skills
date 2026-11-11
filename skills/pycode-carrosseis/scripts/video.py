"""pycode carousel video: grava um slide animado em MP4 (H.264, yuv420p, BT.709, faststart).

A página expõe window.setT(t); o script chama setT quadro a quadro, captura cada quadro no Chromium e
manda os pixels para o ffmpeg do imageio-ffmpeg. O mesmo t gera sempre o mesmo quadro, então o vídeo
sai igual em qualquer máquina. O quadro 0 vira o pôster (out/slide-NN-poster.jpg).
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

import carousel_lib as L
from pycode_tools import paths


def normalize_gain(audio, seconds, target=-16.0):
    """Ganho para levar a trilha a ~-16 LUFS, medido no trecho que entra no vídeo (loudnorm erra em clipes curtos)."""
    import re
    out = subprocess.run([L.ffmpeg_exe(), "-hide_banner", "-nostats", "-i", str(audio), "-af",
                          f"apad,atrim=0:{seconds},ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"I:\s+(-?[\d.]+) LUFS", out[out.rfind("Summary"):])
    return round(target - float(m.group(1)), 2) if m else 0.0


def encode_cmd(out, fps, seconds, audio, normalize, gain):
    cmd = [L.ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{L.W}x{L.H}", "-r", str(fps), "-i", "-"]
    if audio:
        cmd += ["-i", str(audio)]
    cmd += ["-map", "0:v"]
    # rgb24 -> yuv420p com matriz BT.709 (sem isso o swscale usa BT.601 e as cores da marca deslocam)
    cmd += ["-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,"
            "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv",
            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-profile:v", "high", "-pix_fmt", "yuv420p",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
            "-r", str(fps)]
    if audio:
        if normalize:
            gain += normalize_gain(audio, seconds)
        # limitador em -1,5 dBFS: o AAC ainda soma ~1 dB de pico, e o alvo final é ficar abaixo de -1
        chain = [f"volume={gain}dB", "alimiter=limit=0.84:attack=1:release=40:level=disabled", "apad",
                 f"atrim=0:{seconds}"]
        cmd += ["-map", "1:a", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-af", ",".join(chain)]
    cmd += ["-t", f"{seconds}", "-movflags", "+faststart", str(out)]
    return cmd


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode carousel video",
                                 description="Grava um slide animado (Carousel.animate) em MP4 1080x1350.")
    ap.add_argument("pasta", nargs="?", default=".", help="pasta do carrossel (padrão: a atual)")
    ap.add_argument("--slide", type=int, required=True, help="número do slide animado")
    ap.add_argument("--seconds", type=float, help="duração (padrão: video.seconds do slides.json ou a da animação)")
    ap.add_argument("--fps", type=int, default=30, help="quadros por segundo (padrão 30)")
    ap.add_argument("--audio", help="trilha (wav/mp3/m4a) com licença guardada em licencas/")
    ap.add_argument("--normalize", action="store_true", help="leva a trilha a ~-16 LUFS (medido) com limitador em -1,5 dBFS")
    ap.add_argument("--gain", type=float, default=0.0, help="ganho em dB aplicado antes de tudo (ex.: -3)")
    args = ap.parse_args(argv)

    import io

    from PIL import Image
    root = L.project_dir(args.pasta)
    data = L.load_slides(root)
    L.write_mirror(root, data)
    n = args.slide
    if not 1 <= n <= len(data["slides"]):
        paths.die(f"slide {n} não existe (o carrossel tem {len(data['slides'])})")
    audio = Path(args.audio).expanduser().resolve() if args.audio else None
    if audio and not audio.is_file():
        paths.die(f"áudio não encontrado: {audio}")
    if audio and not any((root / "licencas").glob("*")):
        paths.say("aviso: guarde a licença do som em licencas/ (o pack inclui a pasta)")
    out = root / "out" / f"slide-{n:02d}.mp4"
    poster = root / "out" / f"slide-{n:02d}-poster.jpg"
    out.parent.mkdir(exist_ok=True)

    with L.session(root) as (base, browser):
        page = L.open_slide(browser, base, n, scale=1)
        anims = L.animated(page)
        if n not in anims:
            paths.die(f"o slide {n} não tem animação. Registre em js/scene.js: "
                      f"Carousel.animate({n}, (t, slide) => {{...}}, {{duration: 5}})")
        declared = (data["slides"][n - 1].get("video") or {}).get("seconds")
        seconds = args.seconds or declared or anims[n] or 5
        if not 3 <= seconds <= 60:
            paths.die("o slide em vídeo do Instagram precisa ter de 3 a 60 s (o ideal para carrossel: 4 a 6 s)")
        frames = int(round(seconds * args.fps))
        proc = subprocess.Popen(encode_cmd(out, args.fps, seconds, audio, args.normalize, args.gain),
                                stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        started = time.time()
        try:
            for k in range(frames):
                L.set_time(page, k / args.fps)
                png = page.screenshot(type="jpeg", quality=100)
                im = Image.open(io.BytesIO(png)).convert("RGB")
                if im.size != (L.W, L.H):
                    im = im.resize((L.W, L.H), Image.LANCZOS)
                if k == 0:
                    im.save(poster, "JPEG", quality=92, subsampling=0)
                proc.stdin.write(im.tobytes())
                if k and k % (args.fps * 2) == 0:
                    print(f"  {k}/{frames} quadros ({time.time() - started:.0f} s)", flush=True)
            proc.stdin.close()
        except BrokenPipeError:
            pass
        err = proc.stderr.read().decode(errors="ignore")
        if proc.wait() != 0:
            paths.die(f"o ffmpeg falhou: {err.strip()[-800:]}")
        console = list(page.pycode_console)
        page.context.close()

    info = L.probe(out)
    problems = []
    if (info.get("width"), info.get("height")) != (L.W, L.H):
        problems.append(f"tamanho {info.get('width')}x{info.get('height')}")
    if info.get("pix_fmt") != "yuv420p" or "bt709" not in info.get("color", ""):
        problems.append(f"cor {info.get('pix_fmt')} {info.get('color')}")
    if abs(info.get("duration", 0) - seconds) > 0.1:
        problems.append(f"duração {info.get('duration')} s (esperado {seconds})")
    if not info["faststart"]:
        problems.append("sem faststart")
    if console:
        problems.append(f"erro no console: {console[:2]}")
    print(out)
    print(poster)
    print(f"  {L.W}x{L.H} · {info.get('codec')} {info.get('pix_fmt')} ({info.get('color')}) · "
          f"{info.get('duration')} s · {frames} quadros a {args.fps} fps · áudio: {'sim' if info['audio'] else 'não'}"
          f" · faststart: {'sim' if info['faststart'] else 'não'}")
    if audio:
        lufs, peak = L.loudness(out)
        print(f"  loudness {lufs} LUFS · pico {peak} dBFS")
        if peak is not None and peak > -1.0:
            problems.append(f"pico de áudio {peak} dBFS acima de -1 (use --gain -2 ou --normalize)")
        if lufs is not None and not -20 <= lufs <= -12:
            paths.say(f"aviso: {lufs} LUFS fora da faixa usual de -20 a -12 (trilha só de cliques fica perto de -18)")
    if problems:
        for p in problems:
            print(f"[pycode] problema: {p}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
