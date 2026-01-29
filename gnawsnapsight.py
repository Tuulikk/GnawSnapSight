#!/usr/bin/env python3
import argparse
import subprocess
import time
import os
import sys
import base64
import json
import requests

def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def describe_image(image_path, model, url, prompt):
    print(f"[*] Anropar Ollama ({model}) för att beskriva bilden...")
    try:
        base64_image = get_base64_image(image_path)
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "images": [base64_image]
        }
        response = requests.post(f"{url}/api/generate", json=payload)
        response.raise_for_status()
        return response.json().get("response", "Ingen beskrivning genererades.")
    except Exception as e:
        return f"Fel vid anrop till Ollama: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="GnawSnapSight: Screenshot-verktyg med Vision-stöd för agenter.")
    parser.add_argument("--launch", help="Kommando för att starta programmet")
    parser.add_argument("--delay", type=float, default=2.0, help="Fördröjning i sekunder (default: 2.0)")
    parser.add_argument("--output", default="snap.png", help="Utdatafil (default: snap.png)")
    parser.add_argument("--describe", action="store_true", help="Använd Ollama för att beskriva bilden")
    parser.add_argument("--model", default="llama3.2-vision:11b", help="Ollama-modell för vision (default: llama3.2-vision:11b)")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="Ollama API URL")
    parser.add_argument("--active-only", action="store_true", default=True, help="Fånga endast aktivt fönster (default: True)")
    parser.add_argument("--prompt", help="Specifik fråga till vision-modellen (ersätter standardanalys)")

    args = parser.parse_args()

    # 1. Starta programmet om det anges
    if args.launch:
        print(f"[*] Startar program: {args.launch}")
        # Vi kör i bakgrunden
        subprocess.Popen(args.launch, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Extra väntan för att låta fönstret dyka upp
        time.sleep(args.delay)
    else:
        # Om vi inte startar något, vänta bara på delay innan snap
        if args.delay > 0:
            print(f"[*] Väntar {args.delay} sekunder innan screenshot...")
            time.sleep(args.delay)

    # 2. Ta screenshot
    # Spectacle flaggor: -b (background), -n (nonotify), -o (output), -a (active window)
    cmd = ["spectacle", "-b", "-n", "-o", args.output]
    if args.active_only:
        cmd.append("-a")
    
    print(f"[*] Tar screenshot av aktivt fönster: {args.output}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Fel vid körning av spectacle: {e}")
        sys.exit(1)

    if not os.path.exists(args.output):
        print(f"[!] Kunde inte hitta utdatafilen {args.output}")
        sys.exit(1)

    print(f"[+] Screenshot sparad: {args.output}")

    # 3. Vision-beskrivning
    if args.describe or args.prompt:
        # Välj prompt: Användarens specifika fråga eller standardanalys
        if args.prompt:
            final_prompt = args.prompt
        else:
            final_prompt = "Analyze this application window screenshot. Identify the application name, its main purpose, visible text, buttons, and the current state of any displayed data."
        
        description = describe_image(args.output, args.model, args.ollama_url, final_prompt)
        print("\n=== Vision Beskrivning ===")
        print(description)
        print("==========================\n")
        
        # Spara även beskrivningen till en textfil om önskat? 
        # Vi sparar den som [filnamn].txt
        desc_file = os.path.splitext(args.output)[0] + ".txt"
        with open(desc_file, "w") as f:
            f.write(description)
        print(f"[+] Beskrivning sparad till: {desc_file}")

if __name__ == "__main__":
    main()
