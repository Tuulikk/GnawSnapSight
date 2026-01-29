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
    parser.add_argument("--expect-title", help="Verifiera att fönstret har denna titel (eller del av titel)")

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

    def take_snap_and_verify(current_output, expected_title, retry=0):
        # Ta screenshot
        cmd = ["spectacle", "-b", "-n", "-o", current_output]
        if args.active_only:
            cmd.append("-a")
        
        print(f"[*] Tar screenshot (försök {retry + 1}): {current_output}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[!] Fel vid körning av spectacle: {e}")
            return False, None

        if not os.path.exists(current_output):
            print(f"[!] Kunde inte hitta utdatafilen {current_output}")
            return False, None

        if not expected_title:
            return True, None

        # Verifiera titel med vision
        verify_prompt = f"Does this window have the title or contain the text '{expected_title}'? Answer with 'YES' or 'NO' followed by the actual window title you see."
        result = describe_image(current_output, args.model, args.ollama_url, verify_prompt)
        
        if "YES" in result.upper():
            print(f"[+] Verifiering lyckades: Modellen hittade '{expected_title}'")
            return True, result
        else:
            print(f"[!] Verifiering misslyckades: Modellen såg: {result.strip()}")
            return False, result

    # 2. Kör huvudlogiken (med eventuell retry om titel förväntas)
    success, last_result = take_snap_and_verify(args.output, args.expect_title)
    
    if not success and args.expect_title and args.launch:
        print("[*] Provar igen om 3 sekunder (fönstret kanske inte hade fokus än)...")
        time.sleep(3)
        success, last_result = take_snap_and_verify(args.output, args.expect_title, retry=1)

    # 3. Slutgiltig Vision-beskrivning/analys
    if (args.describe or args.prompt) and success:
        # Om vi redan fick en beskrivning under verifiering och det var en enkel prompt, 
        # kanske vi vill ha den fulla analysen nu.
        if args.prompt:
            final_prompt = args.prompt
        else:
            final_prompt = "Analyze this application window screenshot. Identify the application name, its main purpose, visible text, buttons, and the current state of any displayed data."
        
        description = describe_image(args.output, args.model, args.ollama_url, final_prompt)
        print("\n=== Vision Beskrivning ===")
        print(description)
        print("==========================\n")
        
        desc_file = os.path.splitext(args.output)[0] + ".txt"
        with open(desc_file, "w") as f:
            f.write(description)
        print(f"[+] Beskrivning sparad till: {desc_file}")
    elif not success and args.expect_title:
        print(f"[!] Avbryter: Kunde inte bekräfta att rätt fönster ({args.expect_title}) var aktivt.")
        sys.exit(1)


if __name__ == "__main__":
    main()
