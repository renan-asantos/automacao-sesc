import subprocess

def notificar_sistema(mensagem: str):
    """
    Envia uma notificação para o sistema Ubuntu.
    """
    try:
        subprocess.run([
            "notify-send",
            "-u", "critical",
            "-i", "info",  # ícone
            "📢 Sesc Bertioga",
            mensagem
        ], check=True)
        print("✅ Notificação enviada para o sistema.")
    except FileNotFoundError:
        print("⚠️ notify-send não encontrado. Instale com: sudo apt install libnotify-bin")
    except Exception as e:
        print(f"❌ Falha ao enviar notificação: {e}")

def notificar_zenity(mensagem: str):
    """Exibe uma caixa de diálogo gráfica."""
    try:
        subprocess.run([
            "zenity",
            "--info",
            "--title=Sesc Bertioga",
            "--text=" + mensagem,
            "--width=400"
        ], check=True)
    except FileNotFoundError:
        print("⚠️ zenity não encontrado. Instale com: sudo apt install zenity")
    except Exception as e:
        print(f"❌ Falha ao abrir caixa de diálogo: {e}")